import wx
import ast
import helpData
import threading


class CodeAnalyzer(object):
    """
    Get object, function, and variable names from the stack, for use in Autocomplete,
    and find and report any syntax errors along the way.
    """
    def __init__(self):
        super().__init__()
        self.varNames = None
        self.funcNames = None
        self.globalVars = helpData.HelpDataGlobals.variables.keys()
        self.globalFuncs = helpData.HelpDataGlobals.functions.keys()
        self.cardNames = []
        self.objNames = []
        self.objProps = []
        self.objMethods = []
        self.syntaxErrors = {}
        for cls in helpData.helpClasses:
            self.objProps += cls.properties.keys()
            self.objMethods += cls.methods.keys()
        self.ACNames = []
        self.ACAttributes = []

        self.built_in = ["False", "True", "None"]
        self.built_in.extend("else import pass break except in raise finally is return and continue for lambda try "
                             "as def from while del global not with elif if or yield".split(" "))
        self.built_in.extend(["abs()", "str()", "bool()", "list()", "int()", "float()", "dict()", "tuple()",
                              "len()", "min()", "max()", "print()", "range()"])

    def BuildACLists(self, handlerName):
        names = []
        names.extend(self.varNames)
        names.extend([s+"()" for s in self.funcNames])
        names.extend(self.globalVars)
        names.extend([s+"()" for s in self.globalFuncs])
        names.extend(self.objNames)
        names.extend(self.built_in)
        if "Mouse" in handlerName: names.append("mousePos")
        if "Key" in handlerName: names.append("keyName")
        if "Idle" in handlerName: names.append("elapsedTime")
        if "Message" in handlerName: names.append("message")
        names = list(set(names))
        names.sort(key=str.casefold)
        self.ACNames = names

        attributes = []
        attributes.extend(self.objProps)
        attributes.extend([s+"()" for s in self.objMethods])
        attributes.extend(self.cardNames)
        attributes.extend(self.objNames)
        attributes.extend(["x", "y", "width", "height"])
        attributes = list(set(attributes))
        attributes.sort(key=str.casefold)
        self.ACAttributes = attributes

    def CollectCode(self, model, path, codeDict):
        if model.type == "card":
            self.cardNames.append(model.GetProperty("name"))  # also collect all card names
        else:
            self.objNames.append(model.GetProperty("name"))  # and other object names

        if model.type != "stack":
            path.append(model.GetProperty("name"))
        for k,v in model.handlers.items():
            if len(v):
                codeDict[".".join(path)+"."+k] = v
        for child in model.childModels:
            self.CollectCode(child, path, codeDict)
        if model.type != "stack":
            path.pop()

    def ScanCode(self, model, handlerName, completionHandler):
        self.objNames = []
        self.cardNames = []
        codeDict = {}
        self.CollectCode(model, [], codeDict)
        thread = threading.Thread(target=self.ScanCodeInternal, args=(codeDict, handlerName, completionHandler))
        thread.start()

    def ScanCodeInternal(self, codeDict, handlerName, completionHandler):
        self.varNames = set()
        self.funcNames = set()
        self.syntaxErrors = {}

        for path,code in codeDict.items():
            self.ParseWithFallback(code, path)

        self.BuildACLists(handlerName)

        if completionHandler:
            wx.CallAfter(completionHandler)

    def ParseWithFallback(self, code, path):
        try:
            root = ast.parse(code, path)

            for node in ast.walk(root):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    self.varNames.add(node.id)
                elif isinstance(node, ast.FunctionDef):
                    self.funcNames.add(node.name)
        except SyntaxError as e:
            lineStr = e.args[1][3]
            lineNum = e.args[1][1]
            linePos = e.args[1][2]
            self.syntaxErrors[path] = (e.args[0], lineStr, lineNum, linePos)

            # Syntax error?  Try again will all code in this handler, up to right before the bad line,
            # to make sure we find any variables we can, that appear before the bad line
            lines = code.split('\n')
            firstPart = "\n".join(lines[:lineNum-1])
            if len(firstPart):
                self.ParseWithFallback(firstPart, path)
