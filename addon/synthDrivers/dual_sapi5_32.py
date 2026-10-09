# -*- coding: utf-8 -*-
"""Dual Voice SAPI5 (32-bit), NVDA 2026.2 experimental proxy.

Copyright (C) 2026 Seyed Mahmood Taghavi Shahri / contributors.
GPL-3.0-or-later (as used by Dual Voice).

Runs in NVDA's main 64-bit process. It creates a 32-bit NVDA synth host
and synchronizes the Dual Voice UI settings through an internal speech
control message. The control message is removed by the remote worker and
is NEVER passed to SAPI or spoken.
"""

import json
import os
import winreg

import config
from _bridge.clients.synthDriverHost32.synthDriver import SynthDriverProxy32
from synthDrivers import _realtime
from logHandler import log

# Keep this value *identical* in _dual_sapi5_32_worker.py.
_SETTINGS_PREFIX = "\x00DUAL_VOICE_32_SETTINGS_V1:"

_DUAL_VOICE_SPEC = {
    "sapi5SecondVoice": "string(default='')",
    "sapi5SecondRate": "integer(default=50)",
    "sapi5SecondPitch": "integer(default=50)",
    "sapi5SecondVolume": "integer(default=100)",
    "sapi5SecondIsLatin": "boolean(default=False)",
    "sapi5NonLatinPriority": "boolean(default=False)",
    "sapi5ConsiderContext": "boolean(default=False)",
}


class SynthDriver(SynthDriverProxy32):
    name = "dual_sapi5_32"
    description = "Dual Voice using SAPI5 (32-bit voices)"
    # The host inserts this directory into synthDrivers.__path__ before import.
    synthDriver32Path = os.path.dirname(os.path.abspath(__file__))
    # Leading underscore prevents this internal module from appearing in NVDA's
    # synthesizer-selection list in the main process.
    synthDriver32Name = "_dual_sapi5_32_worker"

    @classmethod
    def check(cls):
        if not super().check():
            return False
        try:
            with winreg.OpenKey(
                winreg.HKEY_CLASSES_ROOT,
                r"SAPI.SpVoice",
                0,
                winreg.KEY_READ | winreg.KEY_WOW64_32KEY,
            ):
                return True
        except OSError:
            return False

    def __init__(self):
        # This registry is in the 64-bit NVDA process. The remote worker is
        # deliberately not asked to read config.conf['dual_voice'].
        config.conf.spec["dual_voice"] = _DUAL_VOICE_SPEC
        conf = config.conf["dual_voice"]
        _realtime.sapi5SecondVoice = conf["sapi5SecondVoice"]
        _realtime.sapi5SecondRate = conf["sapi5SecondRate"]
        _realtime.sapi5SecondPitch = conf["sapi5SecondPitch"]
        _realtime.sapi5SecondVolume = conf["sapi5SecondVolume"]
        _realtime.sapi5SecondIsLatin = conf["sapi5SecondIsLatin"]
        _realtime.sapi5NonLatinPriority = conf["sapi5NonLatinPriority"]
        _realtime.sapi5ConsiderContext = conf["sapi5ConsiderContext"]
        _realtime.problemisticPrimaryVoiceID = ""
        _realtime.problemisticSapi5SecondVoice = ""
        super().__init__()
        # Populate voice labels AND SAPI XML 'Name' attributes for dialogs.py.
        self._getAvailableVoices()
        _realtime.primaryVoiceID = self.voice
        log.info("Dual Voice 32-bit host initialized; primary voice: %s", self.voice)

    def _getAvailableVoices(self):
        voices = super()._getAvailableVoices()
        # The worker exposes SAPI's raw 'Name' attributes via the existing
        # getAvailableVariants RPC only as metadata (not a real variant setting).
        rawNameByID = dict(self._remoteService.getAvailableVariants())
        _realtime.list_VoiceID[:] = []
        _realtime.list_VoiceName[:] = []
        _realtime.list_VoiceLang[:] = []
        _realtime.list_VoiceAttribName[:] = []
        for voiceID, info in voices.items():
            _realtime.list_VoiceID.append(voiceID)
            _realtime.list_VoiceName.append(info.displayName)
            _realtime.list_VoiceLang.append(info.language)
            _realtime.list_VoiceAttribName.append(rawNameByID.get(voiceID, info.displayName))
        return voices

    def _set_voice(self, value):
        super()._set_voice(value)
        # Update the primary voice shown in the existing Dual Voice dialog.
        _realtime.primaryVoiceID = self.voice
        _realtime.problemisticPrimaryVoiceID = ""

    def _get_volume(self):
        # Historically Dual Voice controls primary volume by SAPI XML tags.
        return int(_realtime.sapi5FirstVolume)

    def _set_volume(self, value):
        # Keep remote SAPI volume at its default of 100; primary volume
        # is applied in the XML for each utterance.
        _realtime.sapi5FirstVolume = max(0, min(100, int(value)))

    def speak(self, speechSequence):
        prefs = {
            "secondVoice": _realtime.sapi5SecondVoice,
            "secondRate": int(_realtime.sapi5SecondRate),
            "secondPitch": int(_realtime.sapi5SecondPitch),
            "secondVolume": int(_realtime.sapi5SecondVolume),
            "secondIsLatin": bool(_realtime.sapi5SecondIsLatin),
            "nonLatinPriority": bool(_realtime.sapi5NonLatinPriority),
            "considerContext": bool(_realtime.sapi5ConsiderContext),
            "firstVolume": int(_realtime.sapi5FirstVolume),
        }
        marker = _SETTINGS_PREFIX + json.dumps(prefs, ensure_ascii=False, separators=(",", ":"))
        # SynthDriverProxy serializes strings + NVDA speech commands, and the
        # remote worker removes this FIRST metadata-only string before speech.
        return super().speak([marker, *speechSequence])
