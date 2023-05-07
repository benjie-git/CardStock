# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import stackManager
from uiView import ViewModel
from appCommands import SetPropertyCommand, CommandGroup
import re

"""
Find and Replace logic.
The search order is:
- Current card only
  - Recursively find cardModel's childModels (obj1, obj2, obj2.child1, obj2.child2, obj3, etc.)
    - Only search TextField.text properties
    - For replace, only replace if TextField.editable

Create a dict of searchable item paths and values on every Find. Paths are of the form:
  - cardIndex.objectName.property.text
Determine our currently selected findPath, and selection inside it, and start searching there.
Search each item in order, and call stackManager.ShowViewerFindPath(findpath, selectionStart, selectionEnd) to show matches.

Only allow Replacing once per Find, to avoid duplicated replaceText.
"""

class FindEngine(object):
    def __init__(self, stackManager):
        super().__init__()
        self.stackManager = stackManager
        self.findData = wx.FindReplaceData(1)   # initializes and holds search parameters
        self.didReplace = False

    def AddDictItemsForModel(self, searchDict, i, model):
        if model.type == "textfield":
            path = ".".join([str(i), model.GetProperty("name"), "property", "text"])
            searchDict[path] = model.GetProperty("text")
        for m in model.childModels:
            self.AddDictItemsForModel(searchDict, i, m)

    def GenerateSearchDict(self):
        searchDict = {}
        cardModel = self.stackManager.uiCard.model
        self.AddDictItemsForModel(searchDict, self.stackManager.stackModel.childModels.index(cardModel), cardModel)
        return searchDict

    def UpdateFindTextFromSelection(self):
        result = self.stackManager.GetViewerFindPath()
        if result:
            _, textSel = result
            start, end, findStr = textSel
            if findStr and len(findStr):
                self.findData.SetFindString(findStr)

    def Find(self):
        findStr = self.findData.GetFindString()
        if len(findStr):
            searchDict = self.GenerateSearchDict()
            result = self.stackManager.GetViewerFindPath()
            if result:
                startPath, textSel = result
                path, start, end = self.DoFindNext(searchDict, startPath, textSel)
                if path:
                    self.didReplace = False
                    self.stackManager.ShowViewerFindPath(path, start, end)

    def Replace(self):
        if not self.didReplace:
            replaceStr = self.findData.GetReplaceString()
            result = self.stackManager.GetViewerFindPath()
            if result:
                findPath, textSel = result
                self.DoReplaceAtPath(findPath, [textSel], replaceStr)
                self.didReplace = True

    def DoFindNext(self, searchDict, startPath, textSel):
        flags = self.findData.GetFlags()
        findStr = self.findData.GetFindString()
        findBackwards = not (flags & 1)
        findWholeWord = flags & 2
        findMatchCase = flags & 4

        keyList = list(searchDict.keys())
        index = keyList.index(startPath)

        slicedKeys = keyList[index:]
        slicedKeys.extend(keyList[:index])
        slicedKeys.append(slicedKeys[0])
        if findBackwards:
            slicedKeys.reverse()

        for key in slicedKeys:
            text = searchDict[key]
            if len(text) == 0:
                textSel = None
                continue

            offset = 0
            if textSel and not findBackwards:
                text = text[textSel[1]:]
                offset = textSel[1]
            elif textSel:
                text = text[:textSel[0]]
            textSel = None

            flags = (re.MULTILINE) if (findMatchCase) else (re.IGNORECASE | re.MULTILINE)
            if findWholeWord:
                p = re.compile(r'\b{searchStr}\b'.format(searchStr=findStr), flags)
            else:
                p = re.compile(r'{searchStr}'.format(searchStr=findStr), flags)

            start = -1
            end = -1
            matches = [m for m in p.finditer(text)]
            if len(matches):
                if not findBackwards:
                    start = matches[0].start()
                    end = matches[0].end()
                else:
                    start = matches[-1].start()
                    end = matches[-1].end()

            if start != -1:
                return (key, start+offset, end+offset)
        return (None, None, None)

    def DoReplaceAtPath(self, findPath, textSels, replaceStr):
        parts = findPath.split(".")
        # cardIndex, objectName, property|handler, key
        cardIndex = int(parts[0])
        card = self.stackManager.stackModel.childModels[cardIndex]
        model = card.GetChildModelByName(parts[1])
        key = parts[3]
        if model.GetProperty("editable"):
            val = str(model.GetProperty(key))
            for textSel in reversed(textSels):
                val = val[:textSel[0]] + replaceStr + val[textSel[1]:]
            model.SetProperty(key, val)

    def ReplaceAll(self):
        searchDict = self.GenerateSearchDict()
        findStr = self.findData.GetFindString()
        replaceStr = self.findData.GetReplaceString()
        flags = self.findData.GetFlags()
        findWholeWord = flags & 2
        findMatchCase = flags & 4

        for path, text in searchDict.items():
            if len(text) == 0:
                continue

            flags = (re.MULTILINE) if (findMatchCase) else (re.IGNORECASE | re.MULTILINE)
            if findWholeWord:
                p = re.compile(r'\b{searchStr}\b'.format(searchStr=findStr), flags)
            else:
                p = re.compile(r'{searchStr}'.format(searchStr=findStr), flags)

            matches = [m for m in p.finditer(text)]
            for match in reversed(matches):
                self.DoReplaceAtPath(path, [(match.start(), match.end())], replaceStr)
