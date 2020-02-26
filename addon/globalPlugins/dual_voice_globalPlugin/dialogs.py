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
import winreg
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
			config.conf["dual_voice"]["tempNonLatinStartTag"] = config.conf["dual_voice"]["sapi5NonLatinStartTag"]
			config.conf["dual_voice"]["tempNonLatinEndTag"] = config.conf["dual_voice"]["sapi5NonLatinEndTag"]
			config.conf["dual_voice"]["tempLatinStartTag"] = config.conf["dual_voice"]["sapi5LatinStartTag"]
			config.conf["dual_voice"]["tempLatinEndTag"] = config.conf["dual_voice"]["sapi5LatinEndTag"]
		elif ("dual_mssp" in speech.getSynth().name):
			config.conf["dual_voice"]["tempSecondVoice"] = config.conf["dual_voice"]["msspSecondVoice"]
			config.conf["dual_voice"]["tempSecondRate"] = config.conf["dual_voice"]["msspSecondRate"]
			config.conf["dual_voice"]["tempSecondPitch"] = config.conf["dual_voice"]["msspSecondPitch"]
			config.conf["dual_voice"]["tempSecondVolume"] = config.conf["dual_voice"]["msspSecondVolume"]
			config.conf["dual_voice"]["tempSecondIsLatin"] = config.conf["dual_voice"]["msspSecondIsLatin"]
			config.conf["dual_voice"]["tempNonLatinPriority"] = config.conf["dual_voice"]["msspNonLatinPriority"]
			config.conf["dual_voice"]["tempConsiderContext"] = config.conf["dual_voice"]["msspConsiderContext"]
			config.conf["dual_voice"]["tempNonLatinStartTag"] = config.conf["dual_voice"]["msspNonLatinStartTag"]
			config.conf["dual_voice"]["tempNonLatinEndTag"] = config.conf["dual_voice"]["msspNonLatinEndTag"]
			config.conf["dual_voice"]["tempLatinStartTag"] = config.conf["dual_voice"]["msspLatinStartTag"]
			config.conf["dual_voice"]["tempLatinEndTag"] = config.conf["dual_voice"]["msspLatinEndTag"]
		elif ("dual_eSpeak" in speech.getSynth().name):
			config.conf["dual_voice"]["tempSecondVoice"] = config.conf["dual_voice"]["eSpeakSecondVoice"]
			config.conf["dual_voice"]["tempSecondRate"] = config.conf["dual_voice"]["eSpeakSecondRate"]
			config.conf["dual_voice"]["tempSecondPitch"] = config.conf["dual_voice"]["eSpeakSecondPitch"]
			config.conf["dual_voice"]["tempSecondVolume"] = config.conf["dual_voice"]["eSpeakSecondVolume"]
			config.conf["dual_voice"]["tempSecondIsLatin"] = config.conf["dual_voice"]["eSpeakSecondIsLatin"]
			config.conf["dual_voice"]["tempNonLatinPriority"] = config.conf["dual_voice"]["eSpeakNonLatinPriority"]
			config.conf["dual_voice"]["tempConsiderContext"] = config.conf["dual_voice"]["eSpeakConsiderContext"]
			config.conf["dual_voice"]["tempNonLatinStartTag"] = config.conf["dual_voice"]["eSpeakNonLatinStartTag"]
			config.conf["dual_voice"]["tempNonLatinEndTag"] = config.conf["dual_voice"]["eSpeakNonLatinEndTag"]
			config.conf["dual_voice"]["tempLatinStartTag"] = config.conf["dual_voice"]["eSpeakLatinStartTag"]
			config.conf["dual_voice"]["tempLatinEndTag"] = config.conf["dual_voice"]["eSpeakLatinEndTag"]
		

	def makeSettings(self, sizer):
		synthLabel = _("Your current speech synthesizer is the")
		synthLabeladded = _(".")
		if ("dual_sapi5" not in speech.getSynth().name and "dual_mssp" not in speech.getSynth().name and "dual_eSpeak" not in speech.getSynth().name):
			synthLabeladded = _(". Please select Dual Voice  as the speech synthesizer in the NVDA speech setting.")
		synthLabel = wx.StaticText(self, label = synthLabel + " " + speech.getSynth().description + "" + synthLabeladded)
		synthLabel.Wrap(self.GetSize()[0])
		sizer.Add(synthLabel)
		###
		if ("dual_sapi5" in speech.getSynth().name or "dual_mssp" in speech.getSynth().name or "dual_eSpeak" in speech.getSynth().name):
			## find the primary voice and show it in a label          
			primaryVoiceID = config.conf["speech"]["dual_sapi5"]["voice"]
			primaryVoiceToken = primaryVoiceID.split("\\")
			voiceToken = primaryVoiceToken[-1]
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
			primaryVoiceLabel = wx.StaticText(self, label=_('You have selected ') + voiceAttribName[0] + ' as the primary voice.')		
			sizer.Add(primaryVoiceLabel)			
			##        
			VoiceOrderedDict = SynthDriver._get_availableVoices(speech.getSynth()) # it's an OrderedDict
			list_VoiceInfo = [ VoiceInfo for VoiceInfo in VoiceOrderedDict.values() ] # it's a list of NVDA VoiceInfo objects
			# extract ID, name, and language field of each VoiceInfo object and save them in corresponding lists
			self.list_VoiceID = []
			list_VoiceName = []
			list_VoiceLang = []
			self.list_VoiceAttribName = []
			for index in range(0,len(list_VoiceInfo)):
				self.list_VoiceID.append(list_VoiceInfo[index].id)
				list_VoiceName.append(list_VoiceInfo[index].displayName)
				list_VoiceLang.append(list_VoiceInfo[index].language)
				voiceAttribName = 'Unknown'
				voiceID = list_VoiceInfo[index].id
				if ("dual_sapi5" in speech.getSynth().name):
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
					self.list_VoiceAttribName.append(voiceAttribName[0]) # index 0 is the value of the registry item returned by winreg.QueryValueEx
				elif ("dual_mssp" in speech.getSynth().name):
					listVoiceToken = voiceID.split("\\")
					voiceToken = listVoiceToken[-1]
					#self.list_VoiceAttribName.append(voiceToken)				
					try:
						voiceRegPath = 'SOFTWARE\\Microsoft\\Speech Server\\v11.0\\Voices\\Tokens\\' + voiceToken + '\\Attributes'
						key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, voiceRegPath)
						voiceAttribName = winreg.QueryValueEx(key, 'Name')
						key.Close()
					except:
						voiceRegPath = 'SOFTWARE\\Wow6432Node\\Microsoft\\Speech Server\\v11.0\\Voices\\Tokens\\' + voiceToken + '\\Attributes'
						key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, voiceRegPath)
						voiceAttribName = winreg.QueryValueEx(key, 'Name')
						key.Close()
					self.list_VoiceAttribName.append(voiceAttribName[0]) # index 0 is the value of the registry item returned by winreg.QueryValueEx
				else:
					self.list_VoiceAttribName.append('unsupported')
			sVoicesLabel = wx.StaticText(self, label=_("Secondary &voice:"))		
			sizer.Add(sVoicesLabel)	
			self._sVoicesChoice = wx.Choice(self, choices = list_VoiceName)
			_sameVoice = False
			if ("dual_sapi5" in speech.getSynth().name):
				check = config.conf["dual_voice"]["sapi5SecondVoice"] in self.list_VoiceAttribName
				if check:
					index = self.list_VoiceAttribName.index(config.conf["dual_voice"]["sapi5SecondVoice"])
					self._sVoicesChoice.SetSelection(index)
				else:
					#self._sVoicesChoice.SetSelection(0)
					check = config.conf["speech"]["dual_sapi5"]["voice"] in self.list_VoiceID
					if check:
						index = self.list_VoiceID.index(config.conf["speech"]["dual_sapi5"]["voice"])
						self._sVoicesChoice.SetSelection(index)
						_sameVoice = True
					else:
						self._sVoicesChoice.SetSelection(0)
			elif ("dual_mssp" in speech.getSynth().name):
				check = config.conf["dual_voice"]["msspSecondVoice"] in self.list_VoiceAttribName
				if check:
					index = self.list_VoiceAttribName.index(config.conf["dual_voice"]["msspSecondVoice"])
					self._sVoicesChoice.SetSelection(index)
				else:
					#self._sVoicesChoice.SetSelection(0)
					check = config.conf["speech"]["dual_mssp"]["voice"] in self.list_VoiceID
					if check:
						index = self.list_VoiceID.index(config.conf["speech"]["dual_mssp"]["voice"])
						self._sVoicesChoice.SetSelection(index)
						_sameVoice = True
					else:
						self._sVoicesChoice.SetSelection(0)
			elif ("dual_eSpeak" in speech.getSynth().name):
				check = config.conf["dual_voice"]["eSpeakSecondVoice"] in self.list_VoiceID
				if check:
					index = self.list_VoiceID.index(config.conf["dual_voice"]["eSpeakSecondVoice"])
					self._sVoicesChoice.SetSelection(index)
				else:
					#self._sVoicesChoice.SetSelection(0)
					check = config.conf["speech"]["dual_eSpeak"]["voice"] in self.list_VoiceID
					if check:
						index = self.list_VoiceID.index(config.conf["speech"]["dual_eSpeak"]["voice"])
						self._sVoicesChoice.SetSelection(index)
						_sameVoice = True
					else:
						self._sVoicesChoice.SetSelection(0)					
			self._sVoicesChoice.Bind(wx.EVT_CHOICE, self.onSVoiceChange)
			sizer.Add(self._sVoicesChoice)
			##
			self._secondIsLatinCheckBox = wx.CheckBox(self, label = _("&Use the secondary voice for reading Latin text instead of non-Latin."))
			if ("dual_sapi5" in speech.getSynth().name):
				self._secondIsLatinCheckBox.SetValue(config.conf["dual_voice"]["sapi5SecondIsLatin"])
			elif ("dual_mssp" in speech.getSynth().name):
				self._secondIsLatinCheckBox.SetValue(config.conf["dual_voice"]["msspSecondIsLatin"])
			elif ("dual_eSpeak" in speech.getSynth().name):
				self._secondIsLatinCheckBox.SetValue(config.conf["dual_voice"]["eSpeakSecondIsLatin"])	
			self._secondIsLatinCheckBox.Bind(wx.EVT_CHECKBOX, self.onSIsLatinCheck)
			sizer.Add(self._secondIsLatinCheckBox)					
			##
			sRateLabel = wx.StaticText(self, label=_("&Rate:"))
			sizer.Add(sRateLabel)
			self._sRateSlider = wx.Slider(self, value = 50, minValue = 0, maxValue = 100, style = wx.SL_HORIZONTAL)	
			self._sRateSlider.Bind(wx.EVT_SLIDER, self.OnSRateSliderScroll)
			if ("dual_sapi5" in speech.getSynth().name):
				self._sRateSlider.SetValue(config.conf["dual_voice"]["sapi5SecondRate"])
			elif ("dual_mssp" in speech.getSynth().name):
				self._sRateSlider.SetValue(config.conf["dual_voice"]["msspSecondRate"])
			elif ("dual_eSpeak" in speech.getSynth().name):
				self._sRateSlider.SetValue(config.conf["dual_voice"]["eSpeakSecondRate"])
			sizer.Add(self._sRateSlider)
			##
			sPitchLabel = wx.StaticText(self, label=_("&Pitch:"))
			sizer.Add(sPitchLabel)
			self._sPitchSlider = wx.Slider(self, value = 50, minValue = 0, maxValue = 100, style = wx.SL_HORIZONTAL)
			self._sPitchSlider.Bind(wx.EVT_SLIDER, self.OnSPitchSliderScroll)
			if ("dual_sapi5" in speech.getSynth().name):
				self._sPitchSlider.SetValue(config.conf["dual_voice"]["sapi5SecondPitch"])
			elif ("dual_mssp" in speech.getSynth().name):
				self._sPitchSlider.SetValue(config.conf["dual_voice"]["msspSecondPitch"])
			elif ("dual_eSpeak" in speech.getSynth().name):
				self._sPitchSlider.SetValue(config.conf["dual_voice"]["eSpeakSecondPitch"])		
			sizer.Add(self._sPitchSlider)
			##
			sVolumeLabel = wx.StaticText(self, label=_("V&olume:"))
			sizer.Add(sVolumeLabel)
			self._sVolumeSlider = wx.Slider(self, value = 100, minValue = 0, maxValue = 100, style = wx.SL_HORIZONTAL)				
			self._sVolumeSlider.Bind(wx.EVT_SLIDER, self.OnSVolumeSliderScroll)
			if ("dual_sapi5" in speech.getSynth().name):
				self._sVolumeSlider.SetValue(config.conf["dual_voice"]["sapi5SecondVolume"])
			elif ("dual_mssp" in speech.getSynth().name):
				self._sVolumeSlider.SetValue(config.conf["dual_voice"]["msspSecondVolume"])
			elif ("dual_eSpeak" in speech.getSynth().name):
				self._sVolumeSlider.SetValue(config.conf["dual_voice"]["eSpeakSecondVolume"])				
			sizer.Add(self._sVolumeSlider)
			##
			self._nonLatinPriorityCheckBox = wx.CheckBox(self, label = _("&Prioritize non-Latin text over Latin text."))
			if ("dual_sapi5" in speech.getSynth().name):
				self._nonLatinPriorityCheckBox.SetValue(config.conf["dual_voice"]["sapi5NonLatinPriority"])
			elif ("dual_mssp" in speech.getSynth().name):
				self._nonLatinPriorityCheckBox.SetValue(config.conf["dual_voice"]["msspNonLatinPriority"])
			elif ("dual_eSpeak" in speech.getSynth().name):
				self._nonLatinPriorityCheckBox.SetValue(config.conf["dual_voice"]["eSpeakNonLatinPriority"])					
			self._nonLatinPriorityCheckBox.Bind(wx.EVT_CHECKBOX, self.nonLatinPriorityCheck)
			sizer.Add(self._nonLatinPriorityCheckBox)
			self._considerContextCheckBox = wx.CheckBox(self, label = _("Read &numbers and punctuations based on context."))	
			if ("dual_sapi5" in speech.getSynth().name):
				self._considerContextCheckBox.SetValue(config.conf["dual_voice"]["sapi5ConsiderContext"])
			elif ("dual_mssp" in speech.getSynth().name):
				self._considerContextCheckBox.SetValue(config.conf["dual_voice"]["msspConsiderContext"])
			elif ("dual_eSpeak" in speech.getSynth().name):
				self._considerContextCheckBox.SetValue(config.conf["dual_voice"]["eSpeakConsiderContext"])							
			self._considerContextCheckBox.Bind(wx.EVT_CHECKBOX, self.considerContextCheck)
			sizer.Add(self._considerContextCheckBox)			
			##
			typingAreaLabel = wx.StaticText(self, label=_("&Typing area:"))		
			sizer.Add(typingAreaLabel)
			self._typingAreaTextCtrl = wx.TextCtrl(self)
			#self._typingAreaTextCtrl.SetValue(_("You can type here to check the voices"))
			#self._typingAreaTextCtrl.SetValue(list_VoiceName[0])
			self._typingAreaTextCtrl.SetValue(_realtime.typingArea)
			sizer.Add(self._typingAreaTextCtrl)
			if ("dual_sapi5" not in speech.getSynth().name and "dual_mssp" not in speech.getSynth().name and "dual_eSpeak" not in speech.getSynth().name):
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
		if ("dual_sapi5" in speech.getSynth().name or "dual_mssp" in speech.getSynth().name or "dual_eSpeak" in speech.getSynth().name):				
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
			config.conf["dual_voice"]["sapi5NonLatinStartTag"] = config.conf["dual_voice"]["tempNonLatinStartTag"]
			config.conf["dual_voice"]["sapi5NonLatinEndTag"] = config.conf["dual_voice"]["tempNonLatinEndTag"]
			config.conf["dual_voice"]["sapi5LatinStartTag"] = config.conf["dual_voice"]["tempLatinStartTag"]
			config.conf["dual_voice"]["sapi5LatinEndTag"] = config.conf["dual_voice"]["tempLatinEndTag"]
		elif ("dual_mssp" in speech.getSynth().name):
			config.conf["dual_voice"]["msspSecondVoice"] = config.conf["dual_voice"]["tempSecondVoice"]
			config.conf["dual_voice"]["msspSecondRate"] = config.conf["dual_voice"]["tempSecondRate"]
			config.conf["dual_voice"]["msspSecondPitch"] = config.conf["dual_voice"]["tempSecondPitch"]
			config.conf["dual_voice"]["msspSecondVolume"] = config.conf["dual_voice"]["tempSecondVolume"]
			config.conf["dual_voice"]["msspSecondIsLatin"] = config.conf["dual_voice"]["tempSecondIsLatin"]
			config.conf["dual_voice"]["msspNonLatinPriority"] = config.conf["dual_voice"]["tempNonLatinPriority"]
			config.conf["dual_voice"]["msspConsiderContext"] = config.conf["dual_voice"]["tempConsiderContext"]
			config.conf["dual_voice"]["msspNonLatinStartTag"] = config.conf["dual_voice"]["tempNonLatinStartTag"]
			config.conf["dual_voice"]["msspNonLatinEndTag"] = config.conf["dual_voice"]["tempNonLatinEndTag"]
			config.conf["dual_voice"]["msspLatinStartTag"] = config.conf["dual_voice"]["tempLatinStartTag"]
			config.conf["dual_voice"]["msspLatinEndTag"] = config.conf["dual_voice"]["tempLatinEndTag"]
		elif ("dual_eSpeak" in speech.getSynth().name):
			config.conf["dual_voice"]["eSpeakSecondVoice"] = config.conf["dual_voice"]["tempSecondVoice"]
			config.conf["dual_voice"]["eSpeakSecondRate"] = config.conf["dual_voice"]["tempSecondRate"]
			config.conf["dual_voice"]["eSpeakSecondPitch"] = config.conf["dual_voice"]["tempSecondPitch"]
			config.conf["dual_voice"]["eSpeakSecondVolume"] = config.conf["dual_voice"]["tempSecondVolume"]
			config.conf["dual_voice"]["eSpeakSecondIsLatin"] = config.conf["dual_voice"]["tempSecondIsLatin"]
			config.conf["dual_voice"]["eSpeakNonLatinPriority"] = config.conf["dual_voice"]["tempNonLatinPriority"]
			config.conf["dual_voice"]["eSpeakConsiderContext"] = config.conf["dual_voice"]["tempConsiderContext"]
			config.conf["dual_voice"]["eSpeakNonLatinStartTag"] = config.conf["dual_voice"]["tempNonLatinStartTag"]
			config.conf["dual_voice"]["eSpeakNonLatinEndTag"] = config.conf["dual_voice"]["tempNonLatinEndTag"]
			config.conf["dual_voice"]["eSpeakLatinStartTag"] = config.conf["dual_voice"]["tempLatinStartTag"]
			config.conf["dual_voice"]["eSpeakLatinEndTag"] = config.conf["dual_voice"]["tempLatinEndTag"]		
		return super(DualVoiceLanguageSettingsDialog, self).onCancel(event)
		

	def onSVoiceChange(self, event):
		if ("dual_sapi5" in speech.getSynth().name):
			config.conf["dual_voice"]["sapi5SecondVoice"] = self.list_VoiceAttribName[self._sVoicesChoice.GetSelection()]
		elif ("dual_mssp" in speech.getSynth().name):
			config.conf["dual_voice"]["msspSecondVoice"] = self.list_VoiceAttribName[self._sVoicesChoice.GetSelection()]
		elif ("dual_eSpeak" in speech.getSynth().name):
			config.conf["dual_voice"]["eSpeakSecondVoice"] = self.list_VoiceAttribName[self._sVoicesChoice.GetSelection()]

	def OnSRateSliderScroll(self, event):
		if ("dual_sapi5" in speech.getSynth().name):
			config.conf["dual_voice"]["sapi5SecondRate"] = self._sRateSlider.GetValue()
		elif ("dual_mssp" in speech.getSynth().name):
			config.conf["dual_voice"]["msspSecondRate"] = self._sRateSlider.GetValue()
		elif ("dual_eSpeak" in speech.getSynth().name):
			config.conf["dual_voice"]["eSpeakSecondRate"] = self._sRateSlider.GetValue()

		
	def OnSPitchSliderScroll(self, event):
		if ("dual_sapi5" in speech.getSynth().name):
			config.conf["dual_voice"]["sapi5SecondPitch"] = self._sPitchSlider.GetValue()
		elif ("dual_mssp" in speech.getSynth().name):
			config.conf["dual_voice"]["msspSecondPitch"] = self._sPitchSlider.GetValue()
		elif ("dual_eSpeak" in speech.getSynth().name):
			config.conf["dual_voice"]["eSpeakSecondPitch"] = self._sPitchSlider.GetValue()

	
	def OnSVolumeSliderScroll(self, event):
		if ("dual_sapi5" in speech.getSynth().name):
			config.conf["dual_voice"]["sapi5SecondVolume"] = self._sVolumeSlider.GetValue()
		elif ("dual_mssp" in speech.getSynth().name):
			config.conf["dual_voice"]["msspSecondVolume"] = self._sVolumeSlider.GetValue()
		elif ("dual_eSpeak" in speech.getSynth().name):
			config.conf["dual_voice"]["eSpeakSecondVolume"] = self._sVolumeSlider.GetValue()
	
	def onSIsLatinCheck(self, event):
		if ("dual_sapi5" in speech.getSynth().name):
			config.conf["dual_voice"]["sapi5SecondIsLatin"] = self._secondIsLatinCheckBox.GetValue()
		elif ("dual_mssp" in speech.getSynth().name):
			config.conf["dual_voice"]["msspSecondIsLatin"] = self._secondIsLatinCheckBox.GetValue()
		elif ("dual_eSpeak" in speech.getSynth().name):
			config.conf["dual_voice"]["eSpeakSecondIsLatin"] = self._secondIsLatinCheckBox.GetValue()
		
	
	def nonLatinPriorityCheck(self, event):
		if ("dual_sapi5" in speech.getSynth().name):
			config.conf["dual_voice"]["sapi5NonLatinPriority"] = self._nonLatinPriorityCheckBox.GetValue()
		elif ("dual_mssp" in speech.getSynth().name):
			config.conf["dual_voice"]["msspNonLatinPriority"] = self._nonLatinPriorityCheckBox.GetValue()
		elif ("dual_eSpeak" in speech.getSynth().name):
			config.conf["dual_voice"]["eSpeakNonLatinPriority"] = self._nonLatinPriorityCheckBox.GetValue()
		
	
	def considerContextCheck(self, event):
		if ("dual_sapi5" in speech.getSynth().name):
			config.conf["dual_voice"]["sapi5ConsiderContext"] = self._considerContextCheckBox.GetValue()
		elif ("dual_mssp" in speech.getSynth().name):
			config.conf["dual_voice"]["msspConsiderContext"] = self._considerContextCheckBox.GetValue()
		elif ("dual_eSpeak" in speech.getSynth().name):
			config.conf["dual_voice"]["eSpeakConsiderContext"] = self._considerContextCheckBox.GetValue()


