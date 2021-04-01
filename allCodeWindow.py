import wx
import PythonEditor
import wx.stc as stc
from uiView import UiView


class AllCodeWindow(wx.Frame):
    def __init__(self, designer):
        super().__init__(designer, title="All Code", style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_TOOL_WINDOW)
        self.SetMinClientSize(wx.Size(300,50))
        self.SetClientSize(wx.Size(500,500))

        self.designer = designer
        self.text = ""
        self.numLines = 0
        self.lastLineNum = 0
        self.methodStartLines = []
        self.textBox = PythonEditor.PythonEditor(self, self.designer.stackManager, style=wx.BORDER_SUNKEN)
        self.textBox.SetCaretStyle(stc.STC_CARETSTYLE_INVISIBLE)
        self.textBox.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUi)
        self.Bind(wx.EVT_SIZE, self.OnResize)

    def Clear(self):
        self.text = ""
        self.numLines = 0
        self.methodStartLines = []
        self.textBox.SetEditable(True)
        self.textBox.ChangeValue("")
        self.textBox.SetEditable(False)

    def Update(self):
        self.text = ""
        self.numLines = 0
        self.methodStartLines = []
        stack = self.designer.stackManager.stackModel
        self.AppendOnSetupCode(stack)
        self.AppendNonSetupCode(stack)
        self.lastLineNum = 0
        self.textBox.SetEditable(True)
        self.textBox.ChangeValue(self.text)
        self.textBox.SetEditable(False)

    def AppendOnSetupCode(self, obj):
        if obj.type != "stack":
            if obj.type == "card":
                name = obj.GetProperty("name")
                card = obj
            else:
                card = obj.GetCard()
                name = card.GetProperty("name") + "." + obj.GetProperty("name")

            handlerName = "OnSetup"
            displayName = UiView.handlerDisplayNames[handlerName]
            handlerCode = obj.GetHandler(handlerName)
            if handlerCode:
                self.text += f"# {name}\n"
                self.numLines += 1

                self.methodStartLines.append((self.numLines, card, obj, handlerName))
                code = f"def {displayName}\n"
                lines = handlerCode.splitlines(False)
                code += "\n".join(["\t"+line for line in lines])
                self.text += code + "\n\n"
                self.numLines += 1 + len(lines) + 1
        for child in obj.childModels:
            self.AppendOnSetupCode(child)

    def AppendNonSetupCode(self, obj):
        if obj.type != "stack":
            if obj.type == "card":
                name = obj.GetProperty("name")
                card = obj
            else:
                card = obj.GetCard()
                name = card.GetProperty("name") + "." + obj.GetProperty("name")

            didAddComment = False
            for handlerName in obj.handlers:
                if handlerName == "OnSetup": continue

                displayName = UiView.handlerDisplayNames[handlerName]
                handlerCode = obj.GetHandler(handlerName)
                if handlerCode:
                    if not didAddComment:
                        self.text += f"# {name}\n"
                        didAddComment = True
                        self.numLines += 1

                    self.methodStartLines.append((self.numLines, card, obj, handlerName))
                    code = f"def {displayName}\n"
                    lines = handlerCode.splitlines(False)
                    code += "\n".join(["\t"+line for line in lines])
                    self.text += code + "\n\n"
                    self.numLines += 1 + len(lines) + 1
        for child in obj.childModels:
            self.AppendNonSetupCode(child)

    def OnResize(self, event):
        self.textBox.SetSize(self.GetClientSize())

    def OnUpdateUi(self, event):
        line = self.textBox.GetCurrentLine()
        if line != self.lastLineNum:
            self.lastLineNum = line
            for l in reversed(self.methodStartLines):
                if line >= l[0]-1:
                    self.JumpToCode(l[1], l[2], l[3], line-l[0])
                    break

    def JumpToCode(self, card, obj, handlerName, lineNum):
        self.designer.stackManager.LoadCardAtIndex(card.parent.childModels.index(card))
        uiView = self.designer.stackManager.GetUiViewByModel(obj)
        self.designer.stackManager.SelectUiView(uiView)
        self.designer.cPanel.UpdateHandlerForUiViews([uiView], handlerName)
        ed = self.designer.cPanel.codeEditor
        ed.GotoLine(lineNum-1)
        ed.SetSelectionStart(ed.GetLineEndPosition(lineNum-1) - ed.GetLineLength(lineNum-1))
        ed.SetSelectionEnd(ed.GetLineEndPosition(lineNum-1))
