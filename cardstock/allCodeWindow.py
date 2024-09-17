# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import pythonEditor
import wx.stc as stc
from uiView import UiView


class AllCodeWindow(wx.Frame):
    def __init__(self, designer):
        super().__init__(designer, title="All Code", style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_TOOL_WINDOW)
        self.SetMinClientSize(self.FromDIP(wx.Size(300,50)))
        self.SetClientSize(self.FromDIP(wx.Size(500,500)))

        self.designer = designer
        self.analyzer = self.designer.stackManager.analyzer
        self.analyzer.AddScanCompleteNotification(self.MarkAllSyntaxErrors)

        self.text = ""
        self.numLines = 0
        self.lastLineNum = 0
        self.methodStartLines = []
        self.textBox = pythonEditor.PythonEditor(self, None, self.designer.stackManager, style=wx.BORDER_SUNKEN)
        self.textBox.SetCaretStyle(stc.STC_CARETSTYLE_INVISIBLE)
        self.textBox.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUi)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.textBox.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)

    def OnKeyDown(self, event):
        code = event.GetKeyCode()
        if code == wx.WXK_ESCAPE or (code == ord("W") and event.ControlDown()):
            self.Close()
        event.Skip()

    def OnDestroy(self, event):
        self.analyzer.RemoveScanCompleteNotification(self.MarkAllSyntaxErrors)
        event.Skip()

    def Clear(self):
        self.text = ""
        self.numLines = 0
        self.methodStartLines = []
        self.textBox.SetEditable(True)
        self.textBox.ChangeValue("")
        self.textBox.SetEditable(False)

    def UpdateCode(self):
        self.text = ""
        self.numLines = 0
        self.methodStartLines = []
        stack = self.designer.stackManager.stackModel
        self.AppendOnSetupCode(stack)
        self.AppendNonSetupCode(stack)
        self.lastLineNum = 0
        self.textBox.SetEditable(True)
        self.textBox.SetupWithText(self.text)
        self.MarkAllSyntaxErrors()
        self.textBox.SetEditable(False)

    def AppendOnSetupCode(self, obj):
        if obj.type == "stack":
            name = "stack"
            card = None
        elif obj.type == "card":
            name = obj.GetProperty("name")
            card = obj
        else:
            card = obj.GetCard()
            name = card.GetProperty("name") + "." + obj.GetProperty("name")

        handlerName = "on_setup"
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
        if obj.type == "stack":
            name = "stack"
            card = None
        elif obj.type == "card":
            name = obj.GetProperty("name")
            card = obj
        else:
            card = obj.GetCard()
            name = card.GetProperty("name") + "." + obj.GetProperty("name")

        didAddComment = False
        for handlerName in obj.handlers:
            if handlerName == "on_setup": continue

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

    def MarkAllSyntaxErrors(self):
        if not self.IsShown():
            return
        self.textBox.ClearSyntaxErrorMarks()
        for path, e in self.analyzer.syntaxErrors.items():
            for info in self.methodStartLines:
                if info[2]:
                    infoPath = info[2].GetPath() + "." + info[3]
                else:
                    infoPath = info[3]
                if infoPath == path:
                    lineNum = e[2] + info[0]
                    linePos = e[3] - 1
                    lineStartPos = self.textBox.GetLineEndPosition(lineNum) - self.textBox.GetLineLength(lineNum)
                    self.textBox.MarkSyntaxError(lineStartPos + linePos, 2)

    def OnResize(self, event):
        self.textBox.SetSize(self.GetClientSize())

    def OnUpdateUi(self, event):
        line = self.textBox.GetCurrentLine()
        pos = self.textBox.GetLineEndPosition(line)-self.textBox.GetLineLength(line)
        self.textBox.SetSelection(pos, pos)
        if line != self.lastLineNum:
            self.lastLineNum = line
            for l in reversed(self.methodStartLines):
                if line >= l[0]-1:
                    self.JumpToCode(l[1], l[2], l[3], line-l[0])
                    break
        event.Skip()

    def JumpToCode(self, card, obj, handlerName, lineNum):
        if card:
            self.designer.stackManager.LoadCardAtIndex(card.parent.childModels.index(card))
        else:
            self.designer.stackManager.SelectUiView(self.designer.stackManager.uiStack)
        uiView = self.designer.stackManager.GetUiViewByModel(obj)
        self.designer.stackManager.SelectUiView(uiView)
        self.designer.cPanel.UpdateHandlerForUiViews([uiView], None)
        self.designer.cPanel.codeInspector.SelectAndScrollToLine(handlerName, lineNum-1)
