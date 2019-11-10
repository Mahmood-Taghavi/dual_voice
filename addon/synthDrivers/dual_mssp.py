# -*- coding: utf-8 -*-
# Dual voice Add-on for NVDA.
# Copyright (C) 2015-2019 Seyed Mahmood Taghavi-Shahri.
# This file is covered by the GNU General Public License.
# This code is heavily based on the NVDA mssp driver.
# Release: 2015-01-31	Version: 3.0
# Project homepage: https://github.com/Mahmood-Taghavi/dual_voice


from dual_sapi5 import SynthDriver

class SynthDriver(SynthDriver):
	COM_CLASS = "speech.SPVoice"

	name="dual_mssp"
	description="Dual voice (Speech Platform)"
