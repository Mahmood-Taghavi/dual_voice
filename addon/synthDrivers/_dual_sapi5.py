# -*- coding: utf-8 -*-
# Dual voice Add-on for NVDA.
# Copyright (C) 2015 Seyed Mahmood Taghavi-Shahri.
# This file is covered by the GNU General Public License.
# This code initially developed for Persian (Farsi) language.
# Release: 2015-01-31	Version: 3.0
# Project homepage: http://dualvoice.sf.net
# This file contain functions for natural language processing.
import config
from synthDrivers import _realtime
from . import _dualvoice

def nlp(text):
	SecondVoice = config.conf["dual_voice"]["sapi5SecondVoice"]
	if SecondVoice=="":
		primaryVoiceID = config.conf["speech"]["dual_sapi5"]["voice"]
		index = _realtime.list_VoiceID.index(primaryVoiceID)
		voiceAttribName = _realtime.list_VoiceAttribName[index]
		SecondVoice = voiceAttribName # use the name attribute value of the primary voice as the secondary voice name.
	SecondVolume = str(config.conf["dual_voice"]["sapi5SecondVolume"])
	SecondRate = str(round((config.conf["dual_voice"]["sapi5SecondRate"]-50)/5))
	SecondPitch = str(round((config.conf["dual_voice"]["sapi5SecondPitch"]-50)/5))
	latinPriority = (config.conf["dual_voice"]["sapi5NonLatinPriority"]==False)
	considerContext = config.conf["dual_voice"]["sapi5ConsiderContext"]
	nonLatinStartTag = ' <voice required="Name=' + SecondVoice + '"> <volume level="' + SecondVolume + '"> <rate absspeed="' + SecondRate + '"> <pitch absmiddle="' + SecondPitch + '"> '
	nonLatinEndTag = ' </pitch> </rate> </volume> </voice> '
	FirstVolume = str(_realtime.sapi5FirstVolume)
	LatinStartTag = '<volume level="' + FirstVolume + '">'
	LatinEndTag = '</volume>'
	if config.conf["dual_voice"]["sapi5SecondIsLatin"] == False:
		return _dualvoice.nlp(text,latinPriority,considerContext,nonLatinStartTag,nonLatinEndTag,LatinStartTag,LatinEndTag)
	else:
		return _dualvoice.nlp(text,latinPriority,considerContext,LatinStartTag,LatinEndTag,nonLatinStartTag,nonLatinEndTag)
