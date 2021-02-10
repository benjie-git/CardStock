import wx
import stackWindow
from uiView import ViewModel
from commands import SetPropertyCommand, SetHandlerCommand, CommandGroup
import re

SEARCHABLE_PROPERTIES = ["name", "text", "title", "file",
                         "bgColor", "textColor", "penColor", "fillColor",
                         "fit", "alignment"]

"""
Find and Replace logic.
The search order is:
- Cards, first to last
  - Recursively find cardModel's childModels (obj1, obj2, obj2.child1, obj2.child2, obj3, etc.)
    - Property text, in model.PropertyKeys() order (this is display order in the inspector)
    - Handlers in model.handlers order (this is display order in the handlerPicker)
      - handler text, start to end

Create a searchable dict of item paths on every search if we don't have one, or if models are Dirty?
  (cardIndex.objectName.property.propertyName or cardIndex.objectName.handler.handlerName)
Determine our currently selected findPath, and start searching there
search each item in order, and add stackView.SelectFindPath(findpath, selectionStart, selectionEnd) to show matches


"""

class FindEngine(object):
    def __init__(self, stackView):
        super().__init__()
        self.stackView = stackView
        self.findData = wx.FindReplaceData(1)   # initializes and holds search parameters
        self.didReplace = False

    def AddDictItemsForModel(self, searchDict, i, model):
        for key in model.PropertyKeys():
            if key in SEARCHABLE_PROPERTIES:
                path = ".".join([str(i), model.GetProperty("name"), "property", key])
                searchDict[path] = model.GetProperty(key)
        for key, code in model.handlers.items():
            path = ".".join([str(i), model.GetProperty("name"), "handler", key])
            searchDict[path] = model.handlers[key]
        for m in model.childModels:
            self.AddDictItemsForModel(searchDict, i, m)

    def GenerateSearchDict(self):
        searchDict = {}
        i = 0
        for card in self.stackView.stackModel.childModels:
            self.AddDictItemsForModel(searchDict, i, card)
            i += 1
        return searchDict

    def UpdateFindTextFromSelection(self):
        findStr = self.stackView.GetSelectedText()
        self.findData.SetFindString(findStr)

    def Find(self):
        findStr = self.findData.GetFindString()
        if len(findStr):
            searchDict = self.GenerateSearchDict()
            startPath, textSel = self.stackView.GetFindPath()
            path, start, end = self.DoFindNext(searchDict, startPath, textSel)
            if path:
                self.didReplace = False
                self.stackView.ShowFindPath(path, start, end)

    def Replace(self):
        if not self.didReplace:
            replaceStr = self.findData.GetReplaceString()
            findPath, textSel = self.stackView.GetFindPath()
            command = self.DoReplaceAtPath(findPath, textSel, replaceStr)
            if command:
                self.stackView.command_processor.Submit(command)
            parts = findPath.split(".")
            key = parts[3]
            if parts[2] == "handler":
                self.stackView.designer.cPanel.UpdateHandlerForUiViews([self.stackView.designer.cPanel.lastSelectedUiView], key)
                pos = textSel[0] + len(replaceStr)
                self.stackView.designer.cPanel.codeEditor.SetSelection(pos, pos)
                self.stackView.designer.cPanel.codeEditor.ScrollRange(pos, pos)
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

    def DoReplaceAtPath(self, findPath, textSel, replaceStr):
        parts = findPath.split(".")
        # cardIndex, objectName, property|handler, key
        cardIndex = int(parts[0])
        card = self.stackView.stackModel.childModels[cardIndex]
        model = card.GetChildModelByName(parts[1])
        key = parts[3]
        command = None
        if parts[2] == "property":
            val = str(model.GetProperty(key))
            val = val[:textSel[0]] + replaceStr + val[textSel[1]:]
            command = SetPropertyCommand(True, "Set Property", self.stackView.designer.cPanel,
                                         cardIndex, model, key, val, False)
        elif parts[2] == "handler":
            val = model.handlers[key]
            val = val[:textSel[0]] + replaceStr + val[textSel[1]:]
            command = SetHandlerCommand(True, "Set Handler", self.stackView.designer.cPanel,
                                        cardIndex, model, key, val, None, None, False)
        return command

    def ReplaceAll(self):
        selectedUiViews = self.stackView.GetSelectedUiViews()
        self.stackView.SelectUiView(None)

        searchDict = self.GenerateSearchDict()
        findStr = self.findData.GetFindString()
        replaceStr = self.findData.GetReplaceString()
        flags = self.findData.GetFlags()
        findWholeWord = flags & 2
        findMatchCase = flags & 4

        commands = []

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
                command = self.DoReplaceAtPath(path, (match.start(), match.end()), replaceStr)
                if command:
                    commands.append(command)

        if len(commands):
            command = CommandGroup(True, "Replace All", commands)
            self.stackView.command_processor.Submit(command)

        for ui in selectedUiViews:
            self.stackView.SelectUiView(ui, selectedUiViews.index(ui)>0)
