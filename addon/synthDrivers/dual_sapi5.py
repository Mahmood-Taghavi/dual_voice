# -*- coding: UTF-8 -*-
# A part of Dual Voice for NVDA
# Copyright (C) 2015-2021 Seyed Mahmood Taghavi Shahri
# https://mahmood-taghavi.github.io/dual_voice/
# This file is developed based on the NVDA "sapi5.py" driver (obtained on 2021-06-19) (NVDA: "release-2021.1beta3").
# https://github.com/nvaccess/nvda/blob/master/source/synthDrivers/sapi5.py
# This file is covered by the GNU General Public License version 3.
# See the file COPYING for more details.

import locale
from collections import OrderedDict
import threading
import time
import os
from ctypes import *
import comtypes.client
from comtypes import COMError
import winreg
import audioDucking
import NVDAHelper
import globalVars
import speech
from synthDriverHandler import SynthDriver, VoiceInfo, synthIndexReached, synthDoneSpeaking
import config
import nvwave
from logHandler import log
import weakref
from . import _dual_sapi5
from synthDrivers import _realtime


from speech.commands import (
	IndexCommand,
	CharacterModeCommand,
	LangChangeCommand,
	BreakCommand,
	PitchCommand,
	RateCommand,
	VolumeCommand,
	PhonemeCommand,
	SpeechCommand,
)

# SPAudioState enumeration
SPAS_CLOSED=0
SPAS_STOP=1
SPAS_PAUSE=2
SPAS_RUN=3

class FunctionHooker(object):

	def __init__(
		self,
		targetDll: str,
		importDll: str,
		funcName: str,
		newFunction # result of ctypes.WINFUNCTYPE
	):
		# dllImportTableHooks_hookSingle expects byte strings.
		try:
			self._hook=NVDAHelper.localLib.dllImportTableHooks_hookSingle(
				targetDll.encode("mbcs"),
				importDll.encode("mbcs"),
				funcName.encode("mbcs"),
				newFunction
			)
		except UnicodeEncodeError:
			log.error("Error encoding FunctionHooker input parameters", exc_info=True)
			self._hook = None
		if self._hook:
			log.debug(f"Hooked {funcName}")
		else:
			log.error(f"Could not hook {funcName}")
			raise RuntimeError(f"Could not hook {funcName}")

	def __del__(self):
		if self._hook:
			NVDAHelper.localLib.dllImportTableHooks_unhookSingle(self._hook)

_duckersByHandle={}

@WINFUNCTYPE(windll.winmm.waveOutOpen.restype,*windll.winmm.waveOutOpen.argtypes,use_errno=False,use_last_error=False)
def waveOutOpen(pWaveOutHandle,deviceID,wfx,callback,callbackInstance,flags):
	try:
		res=windll.winmm.waveOutOpen(pWaveOutHandle,deviceID,wfx,callback,callbackInstance,flags) or 0
	except WindowsError as e:
		res=e.winerror
	if res==0 and pWaveOutHandle:
		h=pWaveOutHandle.contents.value
		d=audioDucking.AudioDucker()
		d.enable()
		_duckersByHandle[h]=d
	return res

@WINFUNCTYPE(c_long,c_long)
def waveOutClose(waveOutHandle):
	try:
		res=windll.winmm.waveOutClose(waveOutHandle) or 0
	except WindowsError as e:
		res=e.winerror
	if res==0 and waveOutHandle:
		_duckersByHandle.pop(waveOutHandle,None)
	return res

_waveOutHooks=[]
def ensureWaveOutHooks():
	if not _waveOutHooks and audioDucking.isAudioDuckingSupported():
		sapiPath=os.path.join(os.path.expandvars("$SYSTEMROOT"),"system32","speech","common","sapi.dll")
		_waveOutHooks.append(FunctionHooker(sapiPath,"WINMM.dll","waveOutOpen",waveOutOpen))
		_waveOutHooks.append(FunctionHooker(sapiPath,"WINMM.dll","waveOutClose",waveOutClose))

class constants:
	SVSFlagsAsync = 1
	SVSFPurgeBeforeSpeak = 2
	SVSFIsXML = 8
	# From the SpeechVoiceEvents enum: https://msdn.microsoft.com/en-us/library/ms720886(v=vs.85).aspx
	SVEEndInputStream = 4
	SVEBookmark = 16

class SapiSink(object):
	"""Handles SAPI event notifications.
	See https://msdn.microsoft.com/en-us/library/ms723587(v=vs.85).aspx
	"""

	def __init__(self, synthRef: weakref.ReferenceType):
		self.synthRef = synthRef

	def Bookmark(self, streamNum, pos, bookmark, bookmarkId):
		synth = self.synthRef()
		if synth is None:
			log.debugWarning("Called Bookmark method on SapiSink while driver is dead")
			return
		synthIndexReached.notify(synth=synth, index=bookmarkId)

	def EndStream(self, streamNum, pos):
		synth = self.synthRef()
		if synth is None:
			log.debugWarning("Called Bookmark method on EndStream while driver is dead")
			return
		synthDoneSpeaking.notify(synth=synth)

class SynthDriver(SynthDriver):
	supportedSettings=(SynthDriver.VoiceSetting(),SynthDriver.RateSetting(),SynthDriver.PitchSetting(),SynthDriver.VolumeSetting())
	supportedCommands = {
		IndexCommand,
		CharacterModeCommand,
		LangChangeCommand,
		BreakCommand,
		PitchCommand,
		RateCommand,
		VolumeCommand,
		PhonemeCommand,
	}
	supportedNotifications = {synthIndexReached, synthDoneSpeaking}

	COM_CLASS = "SAPI.SPVoice"

	name="dual_sapi5"
	description="Dual voice using Speech API version 5"

	@classmethod
	def check(cls):
		try:
			r=winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,cls.COM_CLASS)
			r.Close()
			return True
		except:
			return False

	ttsAudioStream=None #: Holds the ISPAudio interface for the current voice, to aid in stopping and pausing audio

	def __init__(self,_defaultVoiceToken=None):
		"""
		@param _defaultVoiceToken: an optional sapi voice token which should be used as the default voice (only useful for subclasses)
		@type _defaultVoiceToken: ISpeechObjectToken
		"""
		ensureWaveOutHooks()
		self._pitch=50
		self._initTts(_defaultVoiceToken)
		confspec = {
			"sapi5SecondVoice": "string(default='')",
			"sapi5SecondRate": "integer(default=50)",
			"sapi5SecondPitch": "integer(default=50)",
			"sapi5SecondVolume": "integer(default=100)",
			"sapi5SecondIsLatin": "boolean(default=False)",
			"sapi5NonLatinPriority": "boolean(default=False)",
			"sapi5ConsiderContext": "boolean(default=False)",
		}
		config.conf.spec["dual_voice"] = confspec

		_realtime.sapi5SecondVoice = config.conf["dual_voice"]["sapi5SecondVoice"]
		_realtime.sapi5SecondRate = config.conf["dual_voice"]["sapi5SecondRate"]
		_realtime.sapi5SecondPitch = config.conf["dual_voice"]["sapi5SecondPitch"]
		_realtime.sapi5SecondVolume = config.conf["dual_voice"]["sapi5SecondVolume"]
		_realtime.sapi5SecondIsLatin = config.conf["dual_voice"]["sapi5SecondIsLatin"]
		_realtime.sapi5NonLatinPriority = config.conf["dual_voice"]["sapi5NonLatinPriority"]
		_realtime.sapi5ConsiderContext = config.conf["dual_voice"]["sapi5ConsiderContext"]
		_realtime.primaryVoiceID = _defaultVoiceToken
		_realtime.problemisticPrimaryVoiceID = ''

	def terminate(self):
		self._eventsConnection = None
		self.tts = None

	def _getAvailableVoices(self):
		voices=OrderedDict()
		v=self._getVoiceTokens()
		# #2629: Iterating uses IEnumVARIANT and GetBestInterface doesn't work on tokens returned by some token enumerators.
		# Therefore, fetch the items by index, as that method explicitly returns the correct interface.
		for i in range(len(v)):
			try:
				ID=v[i].Id
				name=v[i].GetDescription()
				try:
					language=locale.windows_locale[int(v[i].getattribute('language').split(';')[0],16)]
				except KeyError:
					language=None
				# Extract the name Attribute of each voice which could be used in SAPI5 XML for voice selection.
				voiceAttribName = v[i].getattribute('name')
			except COMError:
				log.warning("Could not get the voice info. Skipping...")
			voices[ID]=VoiceInfo(ID,name,language)
			if voiceAttribName in _realtime.list_VoiceAttribName:
				pass
			else:
				_realtime.list_VoiceAttribName.append(voiceAttribName)
				_realtime.list_VoiceID.append(ID)
				_realtime.list_VoiceName.append(name)
				_realtime.list_VoiceLang.append(language)
		return voices

	def _getVoiceTokens(self):
		"""Provides a collection of sapi5 voice tokens. Can be overridden by subclasses if tokens should be looked for in some other registry location."""
		return self.tts.getVoices()

	def _get_rate(self):
		return (self.tts.rate*5)+50

	def _get_pitch(self):
		return self._pitch

	def _get_volume(self):
		# return self.tts.volume
		return _realtime.sapi5FirstVolume

	def _get_voice(self):
		return self.tts.voice.Id
 
	def _get_lastIndex(self):
		bookmark=self.tts.status.LastBookmark
		if bookmark!="" and bookmark is not None:
			return int(bookmark)
		else:
			return None

	def _percentToRate(self, percent):
		return (percent - 50) // 5

	def _set_rate(self,rate):
		self.tts.Rate = self._percentToRate(rate)

	def _set_pitch(self,value):
		#pitch is really controled with xml around speak commands
		self._pitch=value

	def _set_volume(self,value):
		# self.tts.Volume = value
		_realtime.sapi5FirstVolume = value

	def _initTts(self, voice=None):
		self.tts=comtypes.client.CreateObject(self.COM_CLASS)
		if voice:
			# #749: It seems that SAPI 5 doesn't reset the audio parameters when the voice is changed,
			# but only when the audio output is changed.
			# Therefore, set the voice before setting the audio output.
			# Otherwise, we will get poor speech quality in some cases.
			self.tts.voice = voice
		outputDeviceID=nvwave.outputDeviceNameToID(config.conf["speech"]["outputDevice"], True)
		if outputDeviceID>=0:
			self.tts.audioOutput=self.tts.getAudioOutputs()[outputDeviceID]
		self._eventsConnection = comtypes.client.GetEvents(self.tts, SapiSink(weakref.ref(self)))
		self.tts.EventInterests = constants.SVEBookmark | constants.SVEEndInputStream
		from comInterfaces.SpeechLib import ISpAudio
		try:
			self.ttsAudioStream=self.tts.audioOutputStream.QueryInterface(ISpAudio)
		except COMError:
			log.debugWarning("SAPI5 voice does not support ISPAudio") 
			self.ttsAudioStream=None

	def _set_voice(self,value):
		tokens = self._getVoiceTokens()
		# #2629: Iterating uses IEnumVARIANT and GetBestInterface doesn't work on tokens returned by some token enumerators.
		# Therefore, fetch the items by index, as that method explicitly returns the correct interface.
		for i in range(len(tokens)):
			voice=tokens[i]
			if value==voice.Id:
				break
		else:
			# Voice not found.
			return
		self._initTts(voice=voice)
		_realtime.primaryVoiceID = voice.Id
		_realtime.problemisticPrimaryVoiceID = ''

	def _percentToPitch(self, percent):
		return percent // 2 - 25

	IPA_TO_SAPI = {
		u"θ": u"th",
		u"s": u"s",
	}
	def _convertPhoneme(self, ipa):
		# We only know about US English phonemes.
		# Rather than just ignoring unknown phonemes, SAPI throws an exception.
		# Therefore, don't bother with any other language.
		if self.tts.voice.GetAttribute("language") != "409":
			raise LookupError("No data for this language")
		out = []
		outAfter = None
		for ipaChar in ipa:
			if ipaChar == u"ˈ":
				outAfter = u"1"
				continue
			out.append(self.IPA_TO_SAPI[ipaChar])
			if outAfter:
				out.append(outAfter)
				outAfter = None
		if outAfter:
			out.append(outAfter)
		return u" ".join(out)

	# def speak(self, speechSequence):
	def _speak(self, speechSequence):
		textList = []

		# NVDA SpeechCommands are linear, but XML is hierarchical.
		# Therefore, we track values for non-empty tags.
		# When a tag changes, we close all previously opened tags and open new ones.
		tags = {}
		# We have to use something mutable here because it needs to be changed by the inner function.
		tagsChanged = [True]
		openedTags = []
		def outputTags():
			if not tagsChanged[0]:
				return
			for tag in reversed(openedTags):
				textList.append("</%s>" % tag)
			del openedTags[:]
			for tag, attrs in tags.items():
				textList.append("<%s" % tag)
				for attr, val in attrs.items():
					textList.append(' %s="%s"' % (attr, val))
				textList.append(">")
				openedTags.append(tag)
			tagsChanged[0] = False

		pitch = self._pitch
		# Pitch must always be specified in the markup.
		tags["pitch"] = {"absmiddle": self._percentToPitch(pitch)}
		rate = self.rate
		# volume = self.volume
		volume = _realtime.sapi5FirstVolume

		for item in speechSequence:
			if isinstance(item, str):
				outputTags()
				# textList.append(item.replace("<", "&lt;"))
				item = item.replace("<", "&lt;")
				item = _dual_sapi5.nlp(text=item)
				textList.append(item)
			elif isinstance(item, IndexCommand):
				textList.append('<Bookmark Mark="%d" />' % item.index)
			elif isinstance(item, CharacterModeCommand):
				if item.state:
					tags["spell"] = {}
				else:
					try:
						del tags["spell"]
					except KeyError:
						pass
				tagsChanged[0] = True
			elif isinstance(item, BreakCommand):
				textList.append('<silence msec="%d" />' % item.time)
			elif isinstance(item, PitchCommand):
				tags["pitch"] = {"absmiddle": self._percentToPitch(int(pitch * item.multiplier))}
				tagsChanged[0] = True
			elif isinstance(item, VolumeCommand):
				if item.multiplier == 1:
					try:
						del tags["volume"]
					except KeyError:
						pass
				else:
					tags["volume"] = {"level": int(volume * item.multiplier)}
				tagsChanged[0] = True
			elif isinstance(item, RateCommand):
				if item.multiplier == 1:
					try:
						del tags["rate"]
					except KeyError:
						pass
				else:
					tags["rate"] = {"absspeed": self._percentToRate(int(rate * item.multiplier))}
				tagsChanged[0] = True
			elif isinstance(item, PhonemeCommand):
				try:
					textList.append(u'<pron sym="%s">%s</pron>'
						% (self._convertPhoneme(item.ipa), item.text or u""))
				except LookupError:
					log.debugWarning("Couldn't convert character in IPA string: %s" % item.ipa)
					if item.text:
						textList.append(item.text)
			elif isinstance(item, SpeechCommand):
				log.debugWarning("Unsupported speech command: %s" % item)
			else:
				log.error("Unknown speech: %s" % item)
		# Close any tags that are still open.
		tags.clear()
		tagsChanged[0] = True
		outputTags()

		text = "".join(textList)
		flags = constants.SVSFIsXML | constants.SVSFlagsAsync
		self.tts.Speak(text, flags)

	def speak(self, speechSequence):
		try:
			self._speak(speechSequence)
		except:
			if (_realtime.problemisticPrimaryVoiceID == _realtime.primaryVoiceID) and (_realtime.problemisticSapi5SecondVoice == _realtime.sapi5SecondVoice):
				log.error('Dual Voice add-on: Fatal error! It seems the selected voices and the computer default voice have problems. So at least select another voice as the computer default voice!')
				speech.setSynth('espeak')
			else:
				_realtime.problemisticSapi5SecondVoice = _realtime.sapi5SecondVoice
				_realtime.problemisticPrimaryVoiceID = _realtime.primaryVoiceID
				try:
					# Possible solution 1: find the primary voice and use it also as the secondary voice.
					index = _realtime.list_VoiceID.index(_realtime.primaryVoiceID)
					voiceAttribName = _realtime.list_VoiceAttribName[index]
					log.warning('Dual Voice add-on: Error in at least one of the selected SAPI 5 voices has been occured! The primary voice was ('+voiceAttribName+') and the secondary voice was ('+_realtime.sapi5SecondVoice+')')
					log.warning('Dual Voice add-on: Try possible solution 1! Use the primary voice ('+voiceAttribName+') in place of the possible problematic secondary voice ('+_realtime.sapi5SecondVoice+').')
					_realtime.tempStringVar = _realtime.sapi5SecondVoice
					_realtime.sapi5SecondVoice = voiceAttribName
					#config.conf["dual_voice"]["sapi5SecondVoice"] = _realtime.sapi5SecondVoice
					self._speak(speechSequence)
				except:
					# Possible solution 2: find the default voice and use it as the primary voice.
					_realtime.sapi5SecondVoice = _realtime.tempStringVar
					#config.conf["dual_voice"]["sapi5SecondVoice"] = _realtime.sapi5SecondVoice
					log.warning('Dual Voice add-on: The possible solution 1 was failed! Hence the selected secondary voice was restored.')
					log.warning('Dual Voice add-on: Try possible solution 2! Use the computer default voice ('+_realtime.list_VoiceAttribName[0]+') in place of the possible problematic primary voice ('+voiceAttribName+').')
					tokens = self._getVoiceTokens()
					voice = tokens[0]
					self._initTts(voice=voice)
					_realtime.primaryVoiceID = voice.Id
					self._speak(speechSequence)

	def cancel(self):
		# SAPI5's default means of stopping speech can sometimes lag at end of speech, especially with Win8 / Win 10 Microsoft Voices.
		# Therefore  instruct the underlying audio interface to stop first, before interupting and purging any remaining speech.
		if self.ttsAudioStream:
			self.ttsAudioStream.setState(SPAS_STOP,0)
		self.tts.Speak(None, 1|constants.SVSFPurgeBeforeSpeak)

	def pause(self,switch):
		# SAPI5's default means of pausing in most cases is either extrmemely slow (e.g. takes more than half a second) or does not work at all.
		# Therefore instruct the underlying audio interface to pause instead.
		if self.ttsAudioStream:
			self.ttsAudioStream.setState(SPAS_PAUSE if switch else SPAS_RUN,0)
