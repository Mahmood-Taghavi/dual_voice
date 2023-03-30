# -*- coding: UTF-8 -*-
# A part of Dual Voice for NVDA
# Copyright (C) 2015-2021 Seyed Mahmood Taghavi Shahri
# https://mahmood-taghavi.github.io/dual_voice/
# This file is covered by the GNU General Public License version 3.
# See the file COPYING for more details.

import globalPluginHandler, wx, gui
from .dialogs import *
import webbrowser
import addonHandler
addonHandler.initTranslation()
import config
from synthDrivers import _realtime

class GlobalPlugin (globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		self.createMenu()
		_realtime.typingArea = _('You can type here to check the voices')

	def createMenu(self):
		self.submenu_dualvoice = wx.Menu()
		item = self.submenu_dualvoice.Append(wx.ID_ANY, _('&Settings of the Dual voice...'))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU , lambda e : gui.mainFrame._popupSettingsDialog(DualVoiceLanguageSettingsDialog), item)
		item = self.submenu_dualvoice.Append(wx.ID_ANY, _('Visit the SAPI &Unifier website!'))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onSAPI_Unifier, item)
		item = self.submenu_dualvoice.Append(wx.ID_ANY, _('Visit the &Dual Voice website!'))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onCheckUpdate, item)
		item = self.submenu_dualvoice.Append(wx.ID_ANY, _('&About the Dual voice for NVDA'))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onAbout, item)
		self.submenu_item = gui.mainFrame.sysTrayIcon.menu.InsertMenu(2, wx.ID_ANY, _('Dual &voice'), self.submenu_dualvoice)

	def onAbout(self, event):
		gui.messageBox('Version 5.2 by Seyed Mahmood Taghavi-Shahri, Iran', _('About the Dual voice add-on for NVDA'), wx.OK)
		
	def onCheckUpdate(self, event):
		webbrowser.open("https://mahmood-taghavi.github.io/dual_voice/")

	def onSAPI_Unifier(self, event):
		webbrowser.open("https://mahmood-taghavi.github.io/SAPI_Unifier/")
