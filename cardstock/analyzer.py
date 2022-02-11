import wx
import ast
import helpData
import threading
import re
import types

ANALYSIS_TIMEOUT = 1000  # in ms


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

        self.varNames = set()
        self.funcNames = set()
        self.globalVars = helpData.HelpDataGlobals.variables.keys()
        self.globalFuncs = helpData.HelpDataGlobals.functions.keys()
        self.cardNames = []
        self.objNames = {}
        self.objProps = {}
        self.objMethods = {}
        self.syntaxErrors = {}
        self.lastHandlerObj = None
        self.lastHandlerName = None
        self.notifyList = []

        # Create list of known properties and methods for each object type
        for cls in helpData.helpClasses:
            types = ["any"]
            types.extend(cls.types)
            for t in types:
                self.objProps[t] = []
                self.objMethods[t] = []
        for cls in helpData.helpClasses:
            c = cls
            types = ["any", "object"]
            types.extend(cls.types)
            while c:
                for t in types:
                    self.objProps[t] += c.properties.keys()
                    self.objMethods[t] += c.methods.keys()
                c = c.parent

        for t in ["bool", "int", "float", "string", "list", "dictionary", "point", "size"]: self.objProps[t] = []
        for t in ["bool", "int", "float", "string", "list", "dictionary", "point", "size"]: self.objMethods[t] = []

        self.objProps["point"] += ["x", "y"]
        self.objProps["size"] += ["width", "height"]
        self.objProps["any"] += ["x", "y", "width", "height"]

        strMethods = ["capitalize", "casefold", "center", "count", "encode", "endswith", "expandtabs",
                      "find", "format", "format_map", "index", "isalnum", "isalpha", "isascii",
                      "isdecimal", "isdigit", "isidentifier", "islower", "isnumeric", "isprintable",
                      "isspace", "istitle", "isupper", "join", "ljust", "lower", "lstrip", "maketrans",
                      "partition", "replace", "rfind", "rindex", "rjust", "rpartition", "rsplit",
                      "rstrip", "split", "splitlines", "startswith", "strip", "swapcase", "title",
                      "translate", "upper", "zfill"]
        listMethods = ["append", "clear", "copy", "count", "extend", "index", "insert", "pop", "remove", "reverse", "sort"]
        self.objMethods["string"] += strMethods
        self.objMethods["list"] += listMethods
        self.objMethods["any"] += strMethods
        self.objMethods["any"] += listMethods

        self.objProps = {key:list(set(l)) for (key, l) in self.objProps.items()}  # unique the items
        self.objMethods = {key:list(set(l)) for (key, l) in self.objMethods.items()}  # unique the items

        self.built_in = ["False", "True", "None"]
        self.built_in.extend("else import pass break except in raise finally is return and continue for lambda try "
                             "as def from while del global not with elif if or yield".split(" "))
        self.built_in.extend(["abs()", "str()", "bool()", "list()", "int()", "float()", "dict()", "tuple()",
                              "len()", "min()", "max()", "print()", "range()", "sorted()", "filter()", "format()",
                              "hex()", "oct()", "map()", "ord()", "open()", "pow()", "reversed()", "round()", "sum()",
                              "zip()"])

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

    def GetTypeFromLeadingString(self, handlerObj, handlerName, leadingStr):
        cleaned = re.sub(r'\([^)]*\)', '', leadingStr)
        for c in ' ()[]{}':
            cleaned = cleaned.split(c)[-1]
        parts = cleaned.split('.')

        # else loop through parts, finding type and object along the way, and return (type, obj)
        # else fall back to the below
        thisCard = self.stackManager.uiCard.model

        def traverseParts(objType, obj, parts_):
            p = parts_[0]
            retVals = (None, None)
            if objType == None:
                cardChild = thisCard.GetChildModelByName(p)
                if cardChild:
                    retVals = (cardChild.type, cardChild)
                elif p == "self" and handlerObj:
                    retVals = (handlerObj.type, handlerObj)
                elif p == "card":
                    retVals = ("card", thisCard)
                elif p == "stack":
                    retVals = ("stack", self.stackManager.stackModel)
                elif p in self.globalVars:
                    retVals = (helpData.HelpDataGlobals.variables[p]["type"], None)
                elif p in self.globalFuncs:
                    retVals = (helpData.HelpDataGlobals.functions[p]["return"], None)
                elif p in self.varNames or p in self.funcNames:
                    # Later, track the actual type of each user variable
                    retVals = ("any", None)
                elif p == "mousePos":
                    retVals = ("point", None)
                elif p == "elapsedTime":
                    retVals = ("float", None)
                elif p in ["message", "keyName"]:
                    retVals = ("string", None)
                elif len(parts[0]) and parts[0][-1] in ('"', "'"):  # string literal
                    retVals = ("string", None)
                elif len(parts[0]) and parts[0][-1] == "]":  # list literal
                    retVals = ("list", None)
                elif len(parts[0]) and parts[0][-1] == "}":  # dict literal
                    retVals = ("dict", None)
                elif parts[0] == '':  # nothing
                    retVals = (None, None)
                else:
                    retVals = ("any", None)
            else:
                if p in self.objProps["any"]:
                    retVals = (helpData.HelpData.GetTypeForProp(p), None)
                elif p in self.objMethods["any"]:
                    retVals = (helpData.HelpData.GetTypeForMethod(p), None)
                elif p in self.built_in:
                    retVals = (None, None)
                if obj:
                    objChild = obj.GetChildModelByName(p)
                    if objChild:
                        retVals = (objChild.type, objChild)

            if retVals is not None and len(parts_) > 1:
                return traverseParts(*retVals, parts_[1:])
            else:
                return retVals

        retVals = traverseParts(None, None, parts)
        return retVals

    def GetACList(self, handlerObj, handlerName, leadingStr, prefix):
        if len(leadingStr) == 0 or leadingStr[-1] != '.':
            if len(prefix) < 1:
                return []
            names = []
            names.extend(self.built_in)
            names.extend(self.globalVars)
            names.extend([s+"()" for s in self.globalFuncs])
            names.extend(self.varNames)
            names.extend([s+"()" for s in self.funcNames])
            names.extend(self.objNames.keys())
            if handlerName:
                if "Mouse" in handlerName: names.append("mousePos")
                if "Key" in handlerName: names.append("keyName")
                if "Periodic" in handlerName: names.append("elapsedTime")
                if "KeyHold" in handlerName: names.append("elapsedTime")
                if "Message" in handlerName: names.append("message")
                if "Bounce" in handlerName: names.extend(["otherObject", "edge"])
                if "CardStockLink" in handlerName: names.append("message")
                if "DoneLoading" in handlerName: names.extend(["URL", "didLoad"])
            names = [n for n in list(set(names)) if prefix.lower() in n.lower()]
            names.sort(key=str.casefold)
            return names
        else:
            (t, o) = self.GetTypeFromLeadingString(handlerObj, handlerName, leadingStr[:-1])
            if t is None:
                return []
            if t == "any" and len(prefix) < 1:
                return []
            attributes = []
            attributes.extend(self.objProps[t])
            attributes.extend([s+"()" for s in self.objMethods[t]])
            if t in ["stack", None]:
                attributes.extend(self.cardNames)
            if t in ["card", "group", None]:
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
        self.syntaxErrors = {}

        for path,code in codeDict.items():
            self.ParseWithFallback(code, path)

        wx.CallAfter(self.ScanFinished)

    def ScanFinished(self):
        for func in self.notifyList:
            func()
        self.analysisPending = False
        self.analysisRunning = False

    def ParseWithFallback(self, code, path):
        try:
            root = ast.parse(code, path)

            for node in ast.walk(root):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    self.varNames.add(node.id)
                elif isinstance(node, ast.FunctionDef):
                    self.funcNames.add(node.name)
                    for arg in node.args.args:
                        self.varNames.add(arg.arg)
                elif isinstance(node, ast.Import):
                    for name in node.names:
                        self.varNames.add(name.name)
                elif isinstance(node, ast.ImportFrom):
                    for name in node.names:
                        self.funcNames.add(name.name)

        except SyntaxError as e:
            lineStr = e.args[1][3]
            lineNum = e.args[1][1]
            linePos = e.args[1][2]
            self.syntaxErrors[path] = (e.args[0], lineStr, lineNum, linePos)

            # Syntax error?  Try again with all code in this handler, up to right before the bad line,
            # to make sure we find any variables we can, that appear before the bad line
            lines = code.split('\n')
            firstPart = "\n".join(lines[:lineNum-1])
            if len(firstPart):
                self.ParseWithFallback(firstPart, path)
