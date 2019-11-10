# Dual Voice for NVDA #

Dual Voice for NVDA, is an open source speech driver for NVDA screen reader. This let use two separate voices for reading non-Latin and Latin languages. 
This add-on is compatible with SAPI5 (Speech API version 5) and MSSP (Speech Platform). 

For updates please see the [Dual Voice for NVDA project homepage](https://github.com/Mahmood-Taghavi/dual_voice).

Copyright 2015-2019 Seyed Mahmood Taghavi-Shahri.

This package is distributed under the terms of the GNU General Public License, version 3. Please see the file "LICENSE.txt" for further details.

## Features

This NVDA add-on provides the following features: 

*	Select first and second voices for use with the NVDA.
*	Determining ordering of two selected voices.
*	Setting for rate of reading, pitch and volume of first voice.
*	Setting for rate of reading, pitch and volume of second voice.
*	Determining priority of voices for reading numbers and common punctuations.
*	Have an option to read numbers and common punctuations based on context.

## Requirements

This add-on need one non-Latin and one Latin voices with common interface. Both non-Latin and Latin voices must have Speech API version 5 interface or Speech Platform interface.

*	Non-Latin Languages such as Persian, Arabic, Belarusian, Bulgarian, Chinese, Greek, Hebrew, Japanese, Korean, Russian, and Ukrainian. 
*	Latin Languages such as English, Czech, Croatian, Finnish, French, German, Italian, Polish, Portuguese, Slovenian, Spanish, and Turkish. 


### To activate this speech driver add-on and use it: ###

- After installing of this addon in NVDA screen reader:
- Go to NVDA settings dialog using "Preferences" sub-menu, and "Settings...".
- Use the down arrow key to select the speech category.
- Twice press the tab button to reach the change button after the current synthesizer and activate it.
- Use down or up arrows to select "Dual voice (Speech API version 5)" or "Dual voice (Speech Platform)" as the synthesizer.
- Select first voice in the voice combo-box.
- Select second voice in the variant combo-box.
- If your first voice is Latin, unselect the following option that say "Use first voice for non-Latin and second voice for Latin language".
- Set rate, pitch, volume for both first and second voices. Note: Rate slider act as general rate in this add-on. So if you want change relative rate of two voices, do it with "Second voice rate" slider.
- If you want program read numbers and common punctuations based on surrounding text, check the option that say "Read numbers and punctuations based on context".
- If you want numbers and common punctuations read use non-Latin voice, check the option that say "Give priority to Latin instead of non-Latin language".

### Common problems and solutions: ###
- When "Automatic language switching" is activated, NVDA automatically replace symbols with equivalent text of first voice language. So select first voice in your preferred language or unselect automatic language switching.
- When "Use spelling functionality if supported" is activated, some text to speech engines cannot read individual characters. So if you confront this problem, first unselect "Use spelling functionality if supported" option.

## Change log ##

### Changes for version 3.1 ###

* The official website of this addon transferred from Sourceforge to GitHub because Sourceforge has blocked Iranian visually impaired users!
* Compatibility with the latest version of NVDA (2019.2.1) is checked which successfully passed and refelected in "lastTestedNVDAVersion" filed of "manifest.ini" file.

### Changes for version 3.0 ###

* The add-on is redesigned to support all speech features.
* The guide has been prepared for English and Persian Languages. 
* Translation for Persian language added.

### Changes for version 2.0 ###

* Bug fixed. Prevent NVDA crash after uninstall used SAPI5 voices.

### Changes for version 1.0 ###

* First official release.
