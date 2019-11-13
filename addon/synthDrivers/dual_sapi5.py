# -*- coding: utf-8 -*-
# Dual voice Add-on for NVDA.
# Copyright (C) 2015-2019 Seyed Mahmood Taghavi-Shahri.
# This file is covered by the GNU General Public License.
# This code is heavily based on the NVDA sapi5 driver.
# Release: 2015-01-31	Version: 3.0
# Project homepage: https://github.com/Mahmood-Taghavi/dual_voice


from . import _dualvoice
import addonHandler
import locale
from collections import OrderedDict
import time
import os
import comtypes.client
from comtypes import COMError
import _winreg
import globalVars
import speech
from synthDriverHandler import SynthDriver,VoiceInfo,BooleanSynthSetting, NumericSynthSetting
import config
import nvwave
from logHandler import log


# Initialize translation support
addonHandler.initTranslation()


class constants:
	SVSFlagsAsync = 1
	SVSFPurgeBeforeSpeak = 2
	SVSFIsXML = 8

	
class SynthDriver(SynthDriver):
	supportedSettings=(SynthDriver.VoiceSetting(), 
	SynthDriver.VariantSetting(), 
	# Translators: Label for a setting in voice settings dialog.
	BooleanSynthSetting('variantIsLatin',_('&Use first voice for non-Latin and second voice for Latin language')), 
	SynthDriver.RateSetting(), 
	# Translators: Label for a setting in voice settings dialog.
	NumericSynthSetting("variantRate",_("Second voice ra&te"),normalStep=1), 
	SynthDriver.PitchSetting(), 
	# Translators: Label for a setting in voice settings dialog.
	NumericSynthSetting("variantPitch",_("Second voice p&itch"),normalStep=1), 
	SynthDriver.VolumeSetting(), 
	# Translators: Label for a setting in voice settings dialog.
	NumericSynthSetting("variantVolume",_("Second voice volu&me"),normalStep=1), 
	# Translators: Label for a setting in voice settings dialog.
	BooleanSynthSetting('considerContext',_('Read &numbers and punctuations based on context')),
	# Translators: Label for a setting in voice settings dialog.
	BooleanSynthSetting("latinPriority",_('&Give priority to Latin instead of non-Latin language')))

	
	COM_CLASS = "SAPI.SPVoice"

	name="dual_sapi5"
	description="Dual voice (Speech API version 5)"

	@classmethod
	
	
	def check(cls):
		try:
			r=_winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT,cls.COM_CLASS)
			r.Close()
			return True
		except:
			return False
	

	_variantName = ""
	_variantRate = 50
	_variantPitch = 50
	_variantVolume = 100
	_variantTag = ''
	_endTag = '</volume></rate></pitch></voice>'
	_voiceVolume = 100
	_voiceTag = ''
	_voiceEndTag = ''
	_currentVariant = ""


	def _get_variantRate(self):
		return self._variantRate

	def _set_variantRate(self, value):
		self._variantRate = value
		self._variantTag = '<voice required="Name=' + self._variantName + '"><pitch absmiddle="' + str((self._variantPitch-50)/5) + '"><rate absspeed="' + str((self._variantRate-50)/5) + '"><volume level="' + str(self._variantVolume) + '">'
		
		
	def _get_variantPitch(self):
		return self._variantPitch

	def _set_variantPitch(self, value):
		self._variantPitch = value
		self._variantTag = '<voice required="Name=' + self._variantName + '"><pitch absmiddle="' + str((self._variantPitch-50)/5) + '"><rate absspeed="' + str((self._variantRate-50)/5) + '"><volume level="' + str(self._variantVolume) + '">'

		
	def _get_variantVolume(self):
		return self._variantVolume

	def _set_variantVolume(self, value):
		self._variantVolume = value
		self._variantTag = '<voice required="Name=' + self._variantName + '"><pitch absmiddle="' + str((self._variantPitch-50)/5) + '"><rate absspeed="' + str((self._variantRate-50)/5) + '"><volume level="' + str(self._variantVolume) + '">'

		
	_variantIsLatin = False
	
	def _get_variantIsLatin(self):
		return self._variantIsLatin

	def _set_variantIsLatin(self, enable):
		self._variantIsLatin = enable	

		
	_latinPriority = False

	def _get_latinPriority(self):
		return self._latinPriority

	def _set_latinPriority(self, enable):
		self._latinPriority = enable

	_considerContext = False

	def _get_considerContext(self):
		return self._considerContext

	def _set_considerContext(self, enable):
		self._considerContext = enable


	def __init__(self,_defaultVoiceToken=None):
		"""
		@param _defaultVoiceToken: an optional sapi voice token which should be used as the default voice (only useful for subclasses)
		@type _defaultVoiceToken: ISpeechObjectToken
		"""
		self._pitch=50
		self._initTts(_defaultVoiceToken)
		## Second voice by default assumed as Latin
		self._set_variantIsLatin(True)	
		## Second voice default volume
		self._set_variantVolume(100)
		## set computer default voice for second voice:
		self._set_variant("")


	def terminate(self):
		del self.tts
	
	def _getAvailableVoices(self):
		voices=OrderedDict()
		v=self._getVoiceTokens()
		# #2629: Iterating uses IEnumVARIANT and GetBestInterface doesn't work on tokens returned by some token enumerators.
		# Therefore, fetch the items by index, as that method explicitly returns the correct interface.
		for i in xrange(len(v)):
			try:
				ID=v[i].Id
				name=v[i].GetDescription()
				try:
					language=locale.windows_locale[int(v[i].getattribute('language').split(';')[0],16)]
				except KeyError:
					language=None
			except COMError:
				log.warning("Could not get the voice info. Skipping...")
			voices[ID]=VoiceInfo(ID,name,language)
		return voices

	def _getAvailableVariants(self):
		voices=OrderedDict()
		v=self._getVoiceTokens()
		# #2629: Iterating uses IEnumVARIANT and GetBestInterface doesn't work on tokens returned by some token enumerators.
		# Therefore, fetch the items by index, as that method explicitly returns the correct interface.
		for i in xrange(len(v)):
			try:
				ID=v[i].Id
				name=v[i].GetDescription()
				try:
					language=locale.windows_locale[int(v[i].getattribute('language').split(';')[0],16)]
				except KeyError:
					language=None
			except COMError:
				log.warning("Could not get the voice info. Skipping...")
			voices[ID]=VoiceInfo(ID,name,language)
		return voices

	def _getVoiceTokens(self):
		"""Provides a collection of sapi5 voice tokens. Can be overridden by subclasses if tokens should be looked for in some other registry location."""
		return self.tts.getVoices()

	def _get_rate(self):
		return (self.tts.rate*5)+50

	def _get_pitch(self):
		return self._pitch

	def _get_volume(self):
		return self._voiceVolume

	def _get_voice(self):
		return self.tts.voice.Id

	def _get_variant(self): 
		return self._currentVariant
 
	def _get_lastIndex(self):
		bookmark=self.tts.status.LastBookmark
		if bookmark!="" and bookmark is not None:
			return int(bookmark)
		else:
			return None

	def _set_rate(self,rate):
		self.tts.Rate = (rate-50)/5

	def _set_pitch(self,value):
		#pitch is really controled with xml around speak commands
		self._pitch=value
		
	def _set_volume(self,value):
		self._voiceVolume = value
		if  value == 100:
			self._voiceTag = ''
			self._voiceEndTag = ''
		else:
			self._voiceTag = '<volume level="' + str(self._voiceVolume) + '">'
			self._voiceEndTag = '</volume>'

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

	def _set_voice(self,value):
		tokens = self._getVoiceTokens()
		# #2629: Iterating uses IEnumVARIANT and GetBestInterface doesn't work on tokens returned by some token enumerators.
		# Therefore, fetch the items by index, as that method explicitly returns the correct interface.
		for i in xrange(len(tokens)):
			voice=tokens[i]
			if value==voice.Id:
				break
		else:
			# Voice not found.
			return
		self._initTts(voice=voice)


	def _set_variant(self, value):
		self._currentVariant = value
		## check for errors in variant initialization
		resetVariant = False
		try:
			if self._currentVariant.find('HKEY_LOCAL_MACHINE') == 0:
				variantAddress = self._currentVariant[19:] + '\Attributes'
				key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, variantAddress)
			else:
				variantAddress = self._currentVariant[18:] + '\Attributes'
				key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, variantAddress)
			key.Close()
		except:
			resetVariant = True
		if (self._variantName == "" or resetVariant):
			tokens = self._getVoiceTokens()
			self._currentVariant = tokens[0].Id		
		## now set self._variantName:
		if self._currentVariant.find('HKEY_LOCAL_MACHINE') == 0:
			variantAddress = self._currentVariant[19:] + '\Attributes'
			key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, variantAddress)
		else:
			variantAddress = self._currentVariant[18:] + '\Attributes'
			key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, variantAddress)
		nameValue = _winreg.QueryValueEx(key, 'Name')
		key.Close()
		self._variantName = nameValue[0]
		self._variantTag = '<voice required="Name=' + self._variantName + '"><pitch absmiddle="' + str((self._variantPitch-50)/5) + '"><rate absspeed="' + str((self._variantRate-50)/5) + '"><volume level="' + str(self._variantVolume) + '">'


	def speak(self,speechSequence):
		textList=[]
		for item in speechSequence:
			if isinstance(item,basestring):
				itemtext = item.replace("<","&lt;")
				## Start NLP section:
				if self._variantIsLatin == False:
					itemtext = _dualvoice.nlp(text=itemtext,latinPriority=self._latinPriority,considerContext=self._considerContext,nonLatinStartTag=self._variantTag,nonLatinEndTag=self._endTag,LatinStartTag=self._voiceTag,LatinEndTag=self._voiceEndTag)				
				else:
					itemtext = _dualvoice.nlp(text=itemtext,latinPriority=self._latinPriority,considerContext=self._considerContext,nonLatinStartTag=self._voiceTag,nonLatinEndTag=self._voiceEndTag,LatinStartTag=self._variantTag,LatinEndTag=self._endTag)
				## End NLP section;
				textList.append(itemtext)
			elif isinstance(item,speech.IndexCommand):
				textList.append("<Bookmark Mark=\"%d\" />"%item.index)
			elif isinstance(item,speech.CharacterModeCommand):
				textList.append("<spell>" if item.state else "</spell>")
			elif isinstance(item,speech.SpeechCommand):
				log.debugWarning("Unsupported speech command: %s"%item)
			else:
				log.error("Unknown speech: %s"%item)
		text="".join(textList)
		#Pitch must always be hardcoded
		pitch=(self._pitch/2)-25
		text="<pitch absmiddle=\"%s\">%s</pitch>"%(pitch,text)
		flags=constants.SVSFIsXML|constants.SVSFlagsAsync
		self.tts.Speak(text,flags)

	def cancel(self):
		#if self.tts.Status.RunningState == 2:
		self.tts.Speak(None, 1|constants.SVSFPurgeBeforeSpeak)

	def pause(self,switch):
		if switch:
			self.cancel()
