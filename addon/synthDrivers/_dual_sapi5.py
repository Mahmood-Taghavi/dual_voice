# -*- coding: UTF-8 -*-
#A part of Dual Voice for NVDA
#Copyright (C) 2015-2020 Seyed Mahmood Taghavi Shahri
#https://mahmood-taghavi.github.io/dual_voice/
#This file is covered by the GNU General Public License version 3.
#See the file COPYING for more details.

#import config
from synthDrivers import _realtime
from . import _dualvoice

def nlp(text):
	SecondVoice = _realtime.sapi5SecondVoice
	if SecondVoice=="":
		index = _realtime.list_VoiceID.index(_realtime.primaryVoiceID)
		voiceAttribName = _realtime.list_VoiceAttribName[index]
		SecondVoice = voiceAttribName # use the name attribute value of the primary voice as the secondary voice name.
	SecondVolume = str(_realtime.sapi5SecondVolume)
	SecondRate = str(round((_realtime.sapi5SecondRate-50)/5))
	SecondPitch = str(round((_realtime.sapi5SecondPitch-50)/5))
	latinPriority = (_realtime.sapi5NonLatinPriority==False)
	considerContext = _realtime.sapi5ConsiderContext
	nonLatinStartTag = ' <voice required="Name=' + SecondVoice + '"> <volume level="' + SecondVolume + '"> <rate absspeed="' + SecondRate + '"> <pitch absmiddle="' + SecondPitch + '"> '
	nonLatinEndTag = ' </pitch> </rate> </volume> </voice> '
	FirstVolume = str(_realtime.sapi5FirstVolume)
	LatinStartTag = '<volume level="' + FirstVolume + '">'
	LatinEndTag = '</volume>'
	if _realtime.sapi5SecondIsLatin == False:
		return _dualvoice.nlp(text,latinPriority,considerContext,nonLatinStartTag,nonLatinEndTag,LatinStartTag,LatinEndTag)
	else:
		return _dualvoice.nlp(text,latinPriority,considerContext,LatinStartTag,LatinEndTag,nonLatinStartTag,nonLatinEndTag)
