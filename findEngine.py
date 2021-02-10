import wx
import stackWindow
from uiView import ViewModel
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
        self.currentPath = None
        self.searchDict = None

    def AddDictItemsForModel(self, i, model):
        for key in model.PropertyKeys():
            if key in SEARCHABLE_PROPERTIES:
                path = ".".join([str(i), model.GetProperty("name"), "property", key])
                self.searchDict[path] = model.GetProperty(key)
        for key, code in model.handlers.items():
            if len(code) > 0:
                path = ".".join([str(i), model.GetProperty("name"), "handler", key])
                self.searchDict[path] = model.handlers[key]
        for m in model.childModels:
            self.AddDictItemsForModel(i, m)

    def GenerateSearchDict(self):
        self.searchDict = {}
        i = 0
        for card in self.stackView.stackModel.childModels:
            self.AddDictItemsForModel(i, card)
            i += 1

    def Find(self, findData):
        flags = findData.GetFlags()
        findStr = findData.GetFindString()
        self.startPath, textSel = self.stackView.GetFindPath()
        self.GenerateSearchDict()
        path, start, end = self.DoFindNext(findStr, textSel, flags)
        self.stackView.ShowFindPath(path, start, end)

    def Replace(self, findData):
        flags = findData.GetFlags()
        findStr = findData.GetFindString()
        self.replaceStr = findData.GetReplaceString()
        self.startPath, self.textSel = self.stackView.GetFindPath()
        self.GenerateSearchDict()

    def ReplaceAll(self, findData):
        flags = findData.GetFlags()
        findStr = findData.GetFindString()
        self.replaceStr = findData.GetReplaceString()
        self.GenerateSearchDict()

    def DoFindNext(self, findStr, textSel, flags):
        findBackwards = not (flags & 1)
        findWholeWord = flags & 2
        findMatchCase = flags & 4

        keyList = list(self.searchDict.keys())
        index = keyList.index(self.startPath)

        slicedKeys = keyList[index:]
        slicedKeys.extend(keyList[:index])
        slicedKeys.append(slicedKeys[0])
        if findBackwards:
            slicedKeys.reverse()

        if not findMatchCase and not findWholeWord:
            findStr = findStr.lower()

        for key in slicedKeys:
            text = self.searchDict[key]

            offset = 0
            if textSel and not findBackwards:
                text = text[textSel[1]:]
                offset = textSel[1]
            elif textSel:
                text = text[:textSel[0]]
            textSel = None

            start = -1
            if not findWholeWord:
                if not findMatchCase:
                    text = text.lower()

                if not findBackwards:
                    start = text.find(findStr)
                else:
                    start = text.rfind(findStr)
            else:
                flags = (re.MULTILINE) if (findMatchCase) else (re.IGNORECASE | re.MULTILINE)
                p = re.compile(r'\b{searchStr}\b'.format(searchStr=findStr), flags)
                matches = [m for m in p.finditer(text)]
                if len(matches):
                    if not findBackwards:
                        start = matches[0].start()
                    else:
                        start = matches[-1].start()

            if start != -1:
                return (key, start+offset, start+offset+len(findStr))
        return (None, None, None)
