# -*- coding: UTF-8 -*-
#A part of Dual Voice for NVDA
#Copyright (C) 2015-2020 Seyed Mahmood Taghavi Shahri
#https://mahmood-taghavi.github.io/dual_voice/
#This file is covered by the GNU General Public License version 3.
#See the file COPYING for more details.

def charactertype(character):
    character.encode('utf-8')
    code = ord(character)
    if (code ==32):
        charType = 'space'
    elif (code >= 880):
        charType = 'nonLatin'
    elif (code ==33 or code ==34) or (code >= 39 and code <= 41) or (code >= 44 and code <= 46) or (code ==58 or code ==59) or (code ==63 or code ==96 or code ==171 or code ==187 or code ==8230):
        charType = 'complex'
    elif (code < 65) or (code > 90 and code < 97) or (code > 122 and code < 161) or (code > 161 and code < 191) or (code ==215 or code ==247):
        charType = 'symbol'     # common punctuation or number
    else:
        charType = 'Latin'
    return charType


def nlp(text,latinPriority,considerContext,nonLatinStartTag,nonLatinEndTag,LatinStartTag,LatinEndTag):
    text.encode('utf-8')
    output = ""
    output.encode('utf-8')
    subtext = ""
    subtext.encode('utf-8')
    beforeIsLatin = False
    if latinPriority:
        beforeIsLatin = True
    length = len(text)
    if length == 1:
        letter = text[0]
        if beforeIsLatin:
            if charactertype(letter) == 'nonLatin':
                output = nonLatinStartTag + letter + nonLatinEndTag
                beforeIsLatin = False
            else:
                output = LatinStartTag + letter + LatinEndTag
        else:
            if charactertype(letter) == 'Latin':
                output = LatinStartTag + letter + LatinEndTag
                beforeIsLatin = True
            else:
                output = nonLatinStartTag + letter + nonLatinEndTag
    else:
        for i in range(length):
            letter = text[i]
            charType = charactertype(letter)
            if (charType == 'complex'):
                charType = 'space'
            elif (charType == 'symbol'):
                if considerContext:
                    if beforeIsLatin:
                        charType = 'Latin'
                    else:
                        charType = 'nonLatin'
                else:
                    if latinPriority:
                        charType = 'Latin'
                    else:
                        charType = 'nonLatin'
            if (charType == 'space'):
                    subtext = subtext + letter
            elif (charType == 'Latin'):
                if beforeIsLatin:
                    subtext = subtext + letter
                else:
                    if subtext != '':
                        output = output + nonLatinStartTag + subtext + nonLatinEndTag
                    subtext = letter
                    beforeIsLatin = True
            if (charType == 'nonLatin'):
                if beforeIsLatin:
                    if subtext != '':
                        output = output + LatinStartTag + subtext + LatinEndTag
                    subtext = letter
                    beforeIsLatin = False
                else:
                    subtext = subtext + letter
        if beforeIsLatin:
            output = output + LatinStartTag + subtext + LatinEndTag
        else:
            output = output + nonLatinStartTag + subtext + nonLatinEndTag
    return output

def alaki(text):
	outtext = text.replace("1", "Yek")# just a dummy function as a test.
	return outtext

