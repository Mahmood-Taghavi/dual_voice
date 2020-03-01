# https://github.com/Mahmood-Taghavi

import globalPluginHandler, wx, gui
from .dialogs import *
import webbrowser
import config

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

class GlobalPlugin (globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		self.createMenu()

	def createMenu(self):
		self.submenu_dualvoice = wx.Menu()
		item = self.submenu_dualvoice.Append(wx.ID_ANY, _("&Settings of the Dual voice..."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU , lambda e : gui.mainFrame._popupSettingsDialog(DualVoiceLanguageSettingsDialog), item)
		item = self.submenu_dualvoice.Append(wx.ID_ANY, _("&Check the Dual Voice website!"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onCheckUpdate, item)
		item = self.submenu_dualvoice.Append(wx.ID_ANY, _("&About the Dual voice for NVDA"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onAbout, item)
		self.submenu_item = gui.mainFrame.sysTrayIcon.menu.InsertMenu(2, wx.ID_ANY, _("Dual &voice"), self.submenu_dualvoice)

	def onAbout(self, event):
		gui.messageBox("Version 4.5 by Seyed Mahmood Taghavi-Shahri", _("About the Dual voice add-on for NVDA"), wx.OK)
		
		
	def onCheckUpdate(self, event):
		webbrowser.open("https://mahmood-taghavi.github.io/dual_voice/")
