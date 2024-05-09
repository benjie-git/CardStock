# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import ast
import helpDataGen
import threading
import re
import types

ANALYSIS_TIMEOUT = 1000  # in ms
NAME_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"

class CodeAnalyzer(object):
    """
    Get object, function, and variable names from the stack, for use in Autocomplete,
    and find and report any syntax errors along the way.
    """
    def __init__(self, stackManager):
        super().__init__()
        self.stackManager = stackManager

        self.analysisTimer = wx.Timer()
        self.analysisTimer.Bind(wx.EVT_TIMER, self.OnAnalysisTimer)
        self.analysisPending = False
        self.analysisRunning = False
        self.disableAC = False

        self.varNames = set()
        self.funcNames = set()
        self.globalVars = helpDataGen.HelpDataGlobals.variables.keys()
        self.globalFuncs = helpDataGen.HelpDataGlobals.functions.keys()
        self.builtinFuncs = helpDataGen.HelpDataBuiltins.functions.keys()
        self.cardNames = []
        self.objNames = {}
        self.objProps = {}
        self.objMethods = {}
        self.handlerVars = {}
        self.syntaxErrors = {}
        self.lastHandlerObj = None
        self.lastHandlerName = None
        self.notifyList = []

        for t in ["bool", "int", "float", "string", "list", "dictionary", "point", "size", "other"]: self.objProps[t] = []
        for t in ["bool", "int", "float", "string", "list", "dictionary", "point", "size", "other"]: self.objMethods[t] = []

        # Create list of known properties and methods for each object type
        for cls in helpDataGen.helpClasses:
            types = ["any"]
            types.extend(cls.types)
            for t in types:
                self.objProps[t] = []
                self.objMethods[t] = []
        for cls in helpDataGen.helpClasses:
            c = cls
            types = ["any", "object"]
            types.extend(cls.types)
            while c:
                for t in types:
                    self.objProps[t] += c.properties.keys()
                    self.objMethods[t] += c.methods.keys()
                c = c.parent

        self.objProps["point"] += ["x", "y"]
        self.objProps["size"] += ["width", "height"]
        self.objProps["any"] += ["x", "y", "width", "height"]

        for t in ["file", "bytes"]:
            self.objProps[t] = []
            self.objMethods[t] = []

        self.objProps = {key:list(set(l)) for (key, l) in self.objProps.items()}  # unique the items
        self.objMethods = {key:list(set(l)) for (key, l) in self.objMethods.items()}  # unique the items

        self.built_in = ["False", "True", "None"]
        self.built_in.extend("else import pass break except in raise finally is return and continue for lambda try "
                             "as def from while del global not with elif if or yield input()".split(" "))

    def SetDown(self):
        self.syntaxErrors = None
        self.notifyList = None
        self.analysisTimer.Stop()
        self.analysisTimer = None

    def AddScanCompleteNotification(self, func):
        self.notifyList.append(func)

    def RemoveScanCompleteNotification(self, func):
        self.notifyList.remove(func)

    def RunDeferredAnalysis(self):
        self.analysisPending = True
        self.analysisTimer.StartOnce(ANALYSIS_TIMEOUT)

    def OnAnalysisTimer(self, event):
        self.RunAnalysis()

    def RunAnalysis(self):
        if self.stackManager.isEditing:
            self.analysisTimer.Stop()
            if not self.analysisRunning:
                self.analysisPending = True
                self.ScanCode()

    def GetTypeFromLeadingString(self, handlerObj, leadingStr):
        """ Return the parent type, parent obj, type, and object of the last token in leadingStr """
        cleaned = re.sub(r'\([^)]*\)', '', leadingStr)
        for c in ' ()[{/+-*%:<>,':
            cleaned = cleaned.split(c)[-1]
        parts = cleaned.split('.')

        # else loop through parts, finding type and object along the way, and return (type, obj)
        # else fall back to the below
        thisCard = self.stackManager.uiCard.model

        def traverseParts(objType, obj, parts_):
            p = parts_[0]
            retVals = (objType, p, None, None)
            if objType == "global":
                cardChild = thisCard.GetChildModelByName(p)
                if cardChild:
                    retVals = (objType, p, cardChild.type, cardChild)
                elif p == "self" and handlerObj:
                    retVals = (objType, p, handlerObj.type, handlerObj)
                elif p == "card":
                    retVals = (objType, p, "card", thisCard)
                elif p == "stack":
                    retVals = (objType, p, "stack", self.stackManager.stackModel)
                elif p in self.globalVars:
                    retVals = (objType, p, helpDataGen.HelpDataGlobals.variables[p]["type"], None)
                elif p in self.globalFuncs:
                    retVals = (objType, p, helpDataGen.HelpDataGlobals.functions[p]["return"], None)
                elif p in self.builtinFuncs:
                    retVals = (objType, p, helpDataGen.HelpDataBuiltins.functions[p]["return"], None)
                elif p in self.varNames or p in self.funcNames:
                    # Later, track the actual type of each user variable
                    retVals = (objType, p, "any", None)
                elif p == "mouse_pos":
                    retVals = (objType, p, "bool", None)
                elif p == "elapsed_time":
                    retVals = (objType, p, "float", None)
                elif p in ["message", "key_name"]:
                    retVals = (objType, p, "string", None)
                elif len(parts[0]) and parts[0][-1] in ('"', "'"):  # string literal
                    retVals = (objType, p, "string", None)
                elif len(parts[0]) and parts[0][-1] == "]":
                    openPos = leadingStr.rfind('[')
                    if openPos > 0 and leadingStr[openPos-1] in NAME_CHARS:
                        retVals = (objType, p, "any", None)  # list index
                    else:
                        retVals = (objType, p, "list", None)  # list literal
                elif len(parts[0]) and parts[0][-1] == "}":  # dict literal
                    retVals = (objType, p, "dictionary", None)
                elif parts[0] == '':  # nothing
                    retVals = (objType, p, None, None)
                else:
                    retVals = (objType, p, "any", None)
            else:
                if objType and p in self.objProps[objType]:
                    retVals = (objType, p, helpDataGen.HelpData.GetTypeForProp(p, objType), None)
                elif objType and p in self.objMethods[objType]:
                    retVals = (objType, p, helpDataGen.HelpData.GetTypeForMethod(p, objType), None)
                elif p in self.objProps["any"]:
                    retVals = (objType, p, helpDataGen.HelpData.GetTypeForProp(p), None)
                elif p in self.objMethods["any"]:
                    retVals = (objType, p, helpDataGen.HelpData.GetTypeForMethod(p), None)
                elif p in self.built_in:
                    retVals = (objType, p, None, None)
                if obj:
                    objChild = obj.GetChildModelByName(p)
                    if objChild:
                        retVals = (objType, p, objChild.type, objChild)

            if retVals is not None and len(parts_) > 1:
                return traverseParts(*retVals[2:], parts_[1:])
            else:
                return retVals

        retVals = traverseParts("global", None, parts)
        return retVals

    def GetACList(self, handlerObj, handlerName, leadingStr, prefix):
        if self.disableAC:
            return []

        if len(leadingStr) == 0 or leadingStr[-1] != '.':
            if len(prefix) < 1:
                return []
            names = []
            names.extend(self.built_in)
            names.extend(self.globalVars)
            names.extend([s+"()" for s in self.globalFuncs])
            names.extend([s+"()" for s in self.builtinFuncs])
            names.extend(self.varNames)
            names.extend([s+"()" for s in self.funcNames])
            names.extend(self.objNames.keys())
            if handlerName:
                if "_mouse" in handlerName: names.append("mouse_pos")
                if "_key" in handlerName: names.append("key_name")
                if "_periodic" in handlerName: names.append("elapsed_time")
                if "_key_hold" in handlerName: names.append("elapsed_time")
                if "_message" in handlerName: names.append("message")
                if "_bounce" in handlerName: names.extend(["other_object", "edge"])
                if "_cardstock_link" in handlerName: names.append("message")
                if "_selection_changed" in handlerName: names.append("is_selected")
                if "_resize" in handlerName: names.append("is_initial")
                if "_done_loading" in handlerName: names.extend(["URL", "did_load"])

                path = handlerObj.GetPath() + "." + handlerName
                if path in self.handlerVars:
                    names.extend(list(self.handlerVars[path]))

            names = [n for n in list(set(names)) if prefix.lower() in n.lower()]
            names.sort(key=str.casefold)
            return names
        else:
            (pt, pn, t, o) = self.GetTypeFromLeadingString(handlerObj, leadingStr[:-1])
            if t is None:
                return []
            if t == "any" and len(prefix) < 1:
                return []
            attributes = []
            attributes.extend(self.objProps[t])
            attributes.extend([s+"()" for s in self.objMethods[t]])
            if t in ["stack", "any"]:
                attributes.extend(self.cardNames)
            if t in ["card", "group", "global", "any"]:
                if o:
                    attributes.extend([c.GetProperty("name") for c in o.childModels])
                else:
                    attributes.extend(self.objNames.keys())
            attributes = [n for n in list(set(attributes)) if prefix.lower() in n.lower()]
            attributes.sort(key=str.casefold)
            return attributes

    def SetRuntimeVarNames(self, varDict):
        # Used for autocomplete from the Console window
        self.objNames = {}
        self.cardNames = []
        self.varNames = set()
        self.funcNames = set()
        self.handlerVars = {}
        self.CollectObjs(self.stackManager.stackModel, [])
        for k,v in varDict.items():
            if isinstance(v, (types.FunctionType, types.BuiltinFunctionType, types.MethodType,
                              types.BuiltinMethodType)):
                self.funcNames.add(k)
            else:
                self.varNames.add(k)

    def CollectObjs(self, model, path):
        if model.type == "card":
            self.cardNames.append(model.GetProperty("name"))  # also collect all card names
        else:
            self.objNames[model.GetProperty("name")] = model.type  # and other object names, with their types
        if model.type != "stack":
            path.append(model.GetProperty("name"))
        for child in model.childModels:
            self.CollectObjs(child, path)
        if model.type != "stack":
            path.pop()

    def CollectCode(self, model, path, codeDict):
        if model.type != "stack":
            path.append(model.GetProperty("name"))

        for k,v in model.handlers.items():
            if len(v):
                codeDict[".".join(path)+"."+k] = v
        for child in model.childModels:
            self.CollectCode(child, path, codeDict)
        if model.type != "stack":
            path.pop()

    def ScanCode(self):
        self.analysisRunning = True
        thread = threading.Thread(target=self.ScanCodeInternal)
        thread.start()

    def ScanCodeInternal(self):
        self.objNames = {}
        self.cardNames = []
        codeDict = {}
        self.CollectObjs(self.stackManager.stackModel, [])
        self.CollectCode(self.stackManager.stackModel, [], codeDict)

        self.varNames = set()
        self.funcNames = set()
        self.handlerVars = {}
        self.syntaxErrors = {}

        for path,code in codeDict.items():
            self.ParseWithFallback(code, path)

        wx.CallAfter(self.ScanFinished)

    def ScanFinished(self):
        for func in self.notifyList:
            func()
        self.analysisPending = False
        self.analysisRunning = False

    def ParseWithFallback(self, code, path, doFallback=True):
        try:
            root = ast.parse(code, path)

            for node in ast.walk(root):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    self.varNames.add(node.id)
                elif isinstance(node, ast.FunctionDef):
                    self.funcNames.add(node.name)
                    for arg in node.args.args:
                        if path not in self.handlerVars:
                            self.handlerVars[path] = set()
                        self.handlerVars[path].add(arg.arg)
                elif isinstance(node, ast.Import):
                    for name in node.names:
                        self.varNames.add(name.name)
                elif isinstance(node, ast.ImportFrom):
                    for name in node.names:
                        self.funcNames.add(name.name)
            return True

        except SyntaxError as e:
            lineStr = e.args[1][3]
            lineNum = e.args[1][1]
            linePos = e.args[1][2]
            self.syntaxErrors[path] = (e.args[0], lineStr, lineNum, linePos)

            # Syntax error?  Try again with all code in this handler, up to right before the bad line,
            # to make sure we find any variables we can, that appear before the bad line
            if doFallback:
                lines = code.split('\n')
                firstPart = "\n".join(lines[:lineNum])
                lastLine = ""
                while len(lastLine.strip()) == 0:
                    lineNum -= 1
                    lastLine = lines[lineNum]
                    if lineNum == 0: break
                indent = self.getIndentation(lastLine)
                lastLine = lastLine.strip()
                if len(lastLine) and lastLine[-1] == ":":
                    firstPart += "\n" + " "*(indent+1)+"pass"
                    if self.ParseWithFallback(firstPart, path, doFallback=False):
                        return True

                lines = code.split('\n')
                firstPart = "\n".join(lines[:lineNum-1])
                if len(firstPart):
                    if self.ParseWithFallback(firstPart, path, doFallback=False):
                        return True
            return False

    @staticmethod
    def getIndentation(s, tabsize=3):
        sx = s.expandtabs(tabsize)
        return 0 if sx.isspace() else len(sx) - len(sx.lstrip())
