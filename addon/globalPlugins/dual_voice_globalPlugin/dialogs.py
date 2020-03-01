# https://github.com/Mahmood-Taghavi

#from collections import defaultdict
import wx
import gui
#import addonHandler
#addonHandler.initTranslation()
import config

#import languageHandler
from logHandler import log
import speech
from synthDriverHandler import SynthDriver
from synthDrivers import _realtime

class DualVoiceLanguageSettingsDialog(gui.SettingsDialog):
	title = _('The "Dual Voice" settings')
	def __init__(self, parent):
		super(DualVoiceLanguageSettingsDialog, self).__init__(parent)
		#_realtime.typingArea = "Alaki"
		if ("dual_sapi5" in speech.getSynth().name):
			config.conf["dual_voice"]["tempSecondVoice"] = config.conf["dual_voice"]["sapi5SecondVoice"]
			config.conf["dual_voice"]["tempSecondRate"] = config.conf["dual_voice"]["sapi5SecondRate"]
			config.conf["dual_voice"]["tempSecondPitch"] = config.conf["dual_voice"]["sapi5SecondPitch"]
			config.conf["dual_voice"]["tempSecondVolume"] = config.conf["dual_voice"]["sapi5SecondVolume"]
			config.conf["dual_voice"]["tempSecondIsLatin"] = config.conf["dual_voice"]["sapi5SecondIsLatin"]
			config.conf["dual_voice"]["tempNonLatinPriority"] = config.conf["dual_voice"]["sapi5NonLatinPriority"]
			config.conf["dual_voice"]["tempConsiderContext"] = config.conf["dual_voice"]["sapi5ConsiderContext"]		

	def makeSettings(self, sizer):
		synthInfo = _('Your current speech synthesizer is the %. Please select the Dual Voice as the speech synthesizer in the NVDA speech settings.')
		synthName = speech.getSynth().description
		synthInfo = synthInfo.replace('%', synthName)
		if ("dual_sapi5" not in speech.getSynth().name):
			infoLabel = wx.StaticText(self, label = synthInfo)
		else:
			## find the primary voice and show it in a label      
			try:
				primaryVoiceID = config.conf["speech"]["dual_sapi5"]["voice"]
				index = _realtime.list_VoiceID.index(primaryVoiceID)
				voiceName = _realtime.list_VoiceName[index]
			except:
				config.conf["speech"]["dual_sapi5"]["voice"] = _realtime.list_VoiceID[0]
				primaryVoiceID = config.conf["speech"]["dual_sapi5"]["voice"]
				index = _realtime.list_VoiceID.index(primaryVoiceID)
				voiceName = _realtime.list_VoiceName[index]
			voiceInfo = _('You have selected % as the primary voice.')
			voiceInfo = voiceInfo.replace('%', voiceName)
			infoLabel = wx.StaticText(self, label = voiceInfo)
		infoLabel.Wrap(self.GetSize()[0])
		sizer.Add(infoLabel)
		###
		if ("dual_sapi5" in speech.getSynth().name):
			sVoicesLabel = wx.StaticText(self, label=_("Secondary &voice:"))		
			sizer.Add(sVoicesLabel)	
			self._sVoicesChoice = wx.Choice(self, choices = _realtime.list_VoiceName)
			if ("dual_sapi5" in speech.getSynth().name):
				check = config.conf["dual_voice"]["sapi5SecondVoice"] in _realtime.list_VoiceAttribName
				if check:
					index = _realtime.list_VoiceAttribName.index(config.conf["dual_voice"]["sapi5SecondVoice"])
					self._sVoicesChoice.SetSelection(index)
				else:
					#self._sVoicesChoice.SetSelection(0)
					check = config.conf["speech"]["dual_sapi5"]["voice"] in _realtime.list_VoiceID
					if check:
						index = _realtime.list_VoiceID.index(config.conf["speech"]["dual_sapi5"]["voice"])
						self._sVoicesChoice.SetSelection(index)
					else:
						self._sVoicesChoice.SetSelection(0)
			self._sVoicesChoice.Bind(wx.EVT_CHOICE, self.onSVoiceChange)
			sizer.Add(self._sVoicesChoice)
			##
			self._secondIsLatinCheckBox = wx.CheckBox(self, label = _("&Use the secondary voice for reading Latin text instead of non-Latin."))
			if ("dual_sapi5" in speech.getSynth().name):
				self._secondIsLatinCheckBox.SetValue(config.conf["dual_voice"]["sapi5SecondIsLatin"])
			self._secondIsLatinCheckBox.Bind(wx.EVT_CHECKBOX, self.onSIsLatinCheck)
			sizer.Add(self._secondIsLatinCheckBox)					
			##
			sRateLabel = wx.StaticText(self, label=_("&Rate:"))
			sizer.Add(sRateLabel)
			self._sRateSlider = wx.Slider(self, value = 50, minValue = 0, maxValue = 100, style = wx.SL_HORIZONTAL)	
			self._sRateSlider.Bind(wx.EVT_SLIDER, self.OnSRateSliderScroll)
			if ("dual_sapi5" in speech.getSynth().name):
				self._sRateSlider.SetValue(config.conf["dual_voice"]["sapi5SecondRate"])
			sizer.Add(self._sRateSlider)
			##
			sPitchLabel = wx.StaticText(self, label=_("&Pitch:"))
			sizer.Add(sPitchLabel)
			self._sPitchSlider = wx.Slider(self, value = 50, minValue = 0, maxValue = 100, style = wx.SL_HORIZONTAL)
			self._sPitchSlider.Bind(wx.EVT_SLIDER, self.OnSPitchSliderScroll)
			if ("dual_sapi5" in speech.getSynth().name):
				self._sPitchSlider.SetValue(config.conf["dual_voice"]["sapi5SecondPitch"])
			sizer.Add(self._sPitchSlider)
			##
			sVolumeLabel = wx.StaticText(self, label=_("V&olume:"))
			sizer.Add(sVolumeLabel)
			self._sVolumeSlider = wx.Slider(self, value = 100, minValue = 0, maxValue = 100, style = wx.SL_HORIZONTAL)				
			self._sVolumeSlider.Bind(wx.EVT_SLIDER, self.OnSVolumeSliderScroll)
			if ("dual_sapi5" in speech.getSynth().name):
				self._sVolumeSlider.SetValue(config.conf["dual_voice"]["sapi5SecondVolume"])			
			sizer.Add(self._sVolumeSlider)
			##
			self._nonLatinPriorityCheckBox = wx.CheckBox(self, label = _("&Prioritize non-Latin text over Latin text."))
			if ("dual_sapi5" in speech.getSynth().name):
				self._nonLatinPriorityCheckBox.SetValue(config.conf["dual_voice"]["sapi5NonLatinPriority"])
			self._nonLatinPriorityCheckBox.Bind(wx.EVT_CHECKBOX, self.nonLatinPriorityCheck)
			sizer.Add(self._nonLatinPriorityCheckBox)
			self._considerContextCheckBox = wx.CheckBox(self, label = _("Read &numbers and punctuations based on context."))	
			if ("dual_sapi5" in speech.getSynth().name):
				self._considerContextCheckBox.SetValue(config.conf["dual_voice"]["sapi5ConsiderContext"])							
			self._considerContextCheckBox.Bind(wx.EVT_CHECKBOX, self.considerContextCheck)
			sizer.Add(self._considerContextCheckBox)			
			##
			typingAreaLabel = wx.StaticText(self, label=_("&Typing area:"))		
			sizer.Add(typingAreaLabel)
			self._typingAreaTextCtrl = wx.TextCtrl(self)
			#self._typingAreaTextCtrl.SetValue(_("You can type here to check the voices"))
			#self._typingAreaTextCtrl.SetValue(_realtime.list_VoiceName[0])
			self._typingAreaTextCtrl.SetValue(_realtime.typingArea)
			sizer.Add(self._typingAreaTextCtrl)
			if ("dual_sapi5" not in speech.getSynth().name):
				sVoicesLabel.Disable()
				self._sVoicesChoice.Disable()
				sRateLabel.Disable()
				self._sRateSlider.Disable()
				sPitchLabel.Disable()
				self._sPitchSlider.Disable()
				sVolumeLabel.Disable()
				self._sVolumeSlider.Disable()
				self._secondIsLatinCheckBox.Disable()
				self._nonLatinPriorityCheckBox.Disable()
				self._considerContextCheckBox.Disable()
				typingAreaLabel.Disable()
				self._typingAreaTextCtrl.Disable()
				
			

	def onOk(self, event):
		# Update Configurations
		if ("dual_sapi5" in speech.getSynth().name):				
			_realtime.typingArea = self._typingAreaTextCtrl.GetValue()
		return super(DualVoiceLanguageSettingsDialog, self).onOk(event)
		
	def onCancel(self, event):
		# Restore Configurations
		if ("dual_sapi5" in speech.getSynth().name):
			config.conf["dual_voice"]["sapi5SecondVoice"] = config.conf["dual_voice"]["tempSecondVoice"]
			config.conf["dual_voice"]["sapi5SecondRate"] = config.conf["dual_voice"]["tempSecondRate"]
			config.conf["dual_voice"]["sapi5SecondPitch"] = config.conf["dual_voice"]["tempSecondPitch"]
			config.conf["dual_voice"]["sapi5SecondVolume"] = config.conf["dual_voice"]["tempSecondVolume"]
			config.conf["dual_voice"]["sapi5SecondIsLatin"] = config.conf["dual_voice"]["tempSecondIsLatin"]
			config.conf["dual_voice"]["sapi5NonLatinPriority"] = config.conf["dual_voice"]["tempNonLatinPriority"]
			config.conf["dual_voice"]["sapi5ConsiderContext"] = config.conf["dual_voice"]["tempConsiderContext"]
		return super(DualVoiceLanguageSettingsDialog, self).onCancel(event)
		

	def onSVoiceChange(self, event):
		if ("dual_sapi5" in speech.getSynth().name):
			config.conf["dual_voice"]["sapi5SecondVoice"] = _realtime.list_VoiceAttribName[self._sVoicesChoice.GetSelection()]

	def OnSRateSliderScroll(self, event):
		if ("dual_sapi5" in speech.getSynth().name):
			config.conf["dual_voice"]["sapi5SecondRate"] = self._sRateSlider.GetValue()
		
	def OnSPitchSliderScroll(self, event):
		if ("dual_sapi5" in speech.getSynth().name):
			config.conf["dual_voice"]["sapi5SecondPitch"] = self._sPitchSlider.GetValue()
	
	def OnSVolumeSliderScroll(self, event):
		if ("dual_sapi5" in speech.getSynth().name):
			config.conf["dual_voice"]["sapi5SecondVolume"] = self._sVolumeSlider.GetValue()
	
	def onSIsLatinCheck(self, event):
		if ("dual_sapi5" in speech.getSynth().name):
			config.conf["dual_voice"]["sapi5SecondIsLatin"] = self._secondIsLatinCheckBox.GetValue()

	def nonLatinPriorityCheck(self, event):
		if ("dual_sapi5" in speech.getSynth().name):
			config.conf["dual_voice"]["sapi5NonLatinPriority"] = self._nonLatinPriorityCheckBox.GetValue()	
	
	def considerContextCheck(self, event):
		if ("dual_sapi5" in speech.getSynth().name):
			config.conf["dual_voice"]["sapi5ConsiderContext"] = self._considerContextCheckBox.GetValue()
