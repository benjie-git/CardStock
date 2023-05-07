# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import uiView

# These Sanitize* functions make sure that the "data" property only includes json-serializable data


def SanitizeKey(val, seen):
    if type(val) == dict:
        value = None
    else:
        value = SanitizeValue(val, seen)
    return value


def SanitizeValue(val, seen):
    if type(val) in [bool, int, float, str] or val is None:
        value = val
    elif isinstance(val, (wx.Point, wx.RealPoint, wx.Size, uiView.CDSPoint, uiView.CDSRealPoint, uiView.CDSSize)):
        value = SanitizeList(list(val), seen)
    elif type(val) == dict:
        if val not in seen:
            value = SanitizeDict(val, seen)
        else:
            value = None
    elif type(val) in [list, set, tuple]:
        if val not in seen:
            value = SanitizeList(list(val), seen)
        else:
            value = None
    else:
        try:
            value = str(val)
        except (ValueError, TypeError) as e:
            value = None
    return value


def SanitizeDict(inDict, seen):
    seen.append(inDict)
    outDict = {}
    for k,v in inDict.items():
        key = SanitizeKey(k, seen)
        value = SanitizeValue(v, seen)
        if key is not None and value is not None:
            outDict[key] = value
    return outDict


def SanitizeList(inList, seen):
    seen.append(inList)
    outList = []
    for v in inList:
        value = SanitizeValue(v, seen)
        if value is not None:
            outList.append(value)
    return outList
