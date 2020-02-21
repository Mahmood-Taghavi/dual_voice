# -*- coding: utf-8 -*-
# Dual voice Add-on for NVDA.
# Copyright (C) 2015 Seyed Mahmood Taghavi-Shahri.
# This file is covered by the GNU General Public License.
# This code initially developed for Persian (Farsi) language.
# Release: 2015-01-31	Version: 3.0
# Project homepage: http://dualvoice.sf.net
# This file contain functions for natural language processing.
import config
import winreg
from . import _dualvoice

def nlp(text):
	SecondVoice = config.conf["dual_voice"]["sapi5SecondVoice"]
	if SecondVoice=="":
		voiceID = config.conf["speech"]["dual_sapi5"]["voice"]
		listVoiceToken = voiceID.split("\\")
		voiceToken = listVoiceToken[-1]
		#self.list_VoiceAttribName.append(voiceToken)				
		try:
			voiceRegPath = 'SOFTWARE\\Wow6432Node\\Microsoft\\Speech\\Voices\\Tokens\\' + voiceToken + '\\Attributes'
			key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, voiceRegPath)
			voiceAttribName = winreg.QueryValueEx(key, 'Name')
			key.Close()
		except:
			voiceRegPath = 'SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\' + voiceToken + '\\Attributes'
			key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, voiceRegPath)
			voiceAttribName = winreg.QueryValueEx(key, 'Name')
			key.Close()
		SecondVoice = voiceAttribName[0] # index 0 is the value of the registry item returned by winreg.QueryValueEx
	SecondVolume = str(config.conf["dual_voice"]["sapi5SecondVolume"])
	SecondRate = str(round((config.conf["dual_voice"]["sapi5SecondRate"]-50)/5))
	SecondPitch = str(round((config.conf["dual_voice"]["sapi5SecondPitch"]-50)/5))
	latinPriority = (config.conf["dual_voice"]["sapi5NonLatinPriority"]==False)
	considerContext = config.conf["dual_voice"]["sapi5ConsiderContext"]
	nonLatinStartTag = ' <voice required="Name=' + SecondVoice + '"> <volume level="' + SecondVolume + '"> <rate absspeed="' + SecondRate + '"> <pitch absmiddle="' + SecondPitch + '"> '
	nonLatinEndTag = ' </pitch> </rate> </volume> </voice> '
	LatinStartTag = ''
	LatinEndTag = ''
	if config.conf["dual_voice"]["sapi5SecondIsLatin"] == False:
		return _dualvoice.nlp(text,latinPriority,considerContext,nonLatinStartTag,nonLatinEndTag,LatinStartTag,LatinEndTag)
	else:
		return _dualvoice.nlp(text,latinPriority,considerContext,LatinStartTag,LatinEndTag,nonLatinStartTag,nonLatinEndTag)
