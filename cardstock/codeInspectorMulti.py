import wx
import pythonEditor
import wx.stc
import helpData
import appCommands
from uiView import UiView


class CodeInspector(wx.ScrolledWindow):
    def __init__(self, parent, stackManager):
        super().__init__(parent, style=wx.BORDER_SUNKEN)
        self.SetBackgroundColour("white")
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)

        self.parent = parent
        self.stackManager = stackManager
        self.updateHelpTextFunc = None

        self.currentUiView = None
        self.codeLabels = {}
        self.codeEditors = {}
        self.codeLines = {}
        self.lastCursorSels = {}

        self.editorCache = []
        self.labelCache = []
        self.lineCache = []
        self.lastLine = None

        self.container = self
        self.container.SetScrollbars(1, 1, 1, 1)

        self.editBox = wx.BoxSizer(wx.VERTICAL)
        self.SetupEditorForUiView(None)
        self.container.SetSizer(self.editBox)
        self.container.SetAutoLayout(True)

    def SetupEditorForUiView(self, uiView):
        if uiView == self.currentUiView:
            return

        self.ClearViews()
        self.currentUiView = uiView

        self.editBox.AddSpacer(5)
        if uiView:
            for (handlerName, code) in uiView.model.handlers.items():
                self.AddViewsForEvent(handlerName, code)
            self.lastLine.Hide()
        self.Relayout()

        if uiView:
            for (handlerName, code) in uiView.model.handlers.items():
                if len(code.strip()):
                    codeEditor = self.codeEditors[handlerName]
                    codeEditor.SetFocus()
                    break

    def GetAnalyzer(self):
        return self.stackManager.analyzer

    def GetCurrentHandler(self):
        if self.currentUiView:
            for (handlerName, editor) in self.codeEditors.items():
                if editor.HasFocus():
                    return handlerName
            return self.currentUiView.model.handlers[0]
        return None

    def SelectAndScrollTo(self, handlerName, selStart, selEnd):
        codeEditor = self.codeEditors[handlerName]
        self.ShowEditor(handlerName, True)
        codeEditor.SetSelection(selStart, selEnd)
        codeEditor.ScrollRange(selStart, selEnd)
        codeEditor.SetFocus()

    def SelectAndScrollToLine(self, handlerName, selLine):
        codeEditor = self.codeEditors[handlerName]
        self.ShowEditor(handlerName, True)
        codeEditor.GotoLine(selLine)
        lineEnd = codeEditor.GetLineEndPosition(selLine)
        lineLen = codeEditor.GetLineLength(selLine)
        codeEditor.SetSelectionStart(lineEnd-lineLen)
        codeEditor.SetSelectionEnd(lineEnd)
        codeEditor.SetFocus()

    def UpdateHandlerForUiView(self, uiView, handlerName, selection=None):
        self.SetupEditorForUiView(uiView)

        if uiView:
            if handlerName:
                codeEditor = self.codeEditors[handlerName]
                codeEditor.SetFocus()
                if selection and uiView:
                    firstLine = codeEditor.GetFirstVisibleLine()
                    codeEditor.AutoCompCancel()

                self.lastCursorSels[handlerName] = codeEditor.GetSelection()

                codeEditor.SetupWithText(uiView.model.GetHandler(handlerName))
                self.ShowEditor(handlerName, True)
                codeEditor.EmptyUndoBuffer()
                codeEditor.currentModel = uiView.model
                codeEditor.currentHandler = handlerName

                if selection:
                    codeEditor.SetSelection(*selection)
                    codeEditor.ScrollToLine(firstLine)
                    codeEditor.ScrollRange(*selection)
                    codeEditor.SetFocus()

                self.stackManager.analyzer.RunAnalysis()

    def SelectInCodeForHandlerName(self, handlerName, selectStart, selectEnd):
        codeEditor = self.codeEditors[handlerName]
        self.ShowEditor(handlerName, True)
        codeEditor.SetSelection(selectStart, selectEnd)
        codeEditor.ScrollRange(selectStart, selectEnd)
        codeEditor.SetFocus()

    def GetCodeEditorSelection(self, handlerName):
        codeEditor = self.codeEditors[handlerName]
        start, end = codeEditor.GetSelection()
        text = codeEditor.GetSelectedText()
        return (start, end, text)

    # Internal

    def ClearViews(self):
        self.editBox.Clear()

        for label in self.codeLabels.values():
            self.labelCache.append(label)
            label.Hide()
        self.codeLabels = {}

        for editor in self.codeEditors.values():
            self.editorCache.append(editor)
            editor.Hide()
        self.codeEditors = {}

        for line in self.codeLines.values():
            self.lineCache.append(line)
            line.Hide()
        self.codeLines = {}

        self.lastCursorSels = {}

    def GetCodeLabel(self):
        if len(self.labelCache):
            label = self.labelCache.pop()
            label.Show()
            return label
        else:
            label = wx.StaticText(self.container)
            # label.SetBackgroundColour("white")
            indicator = wx.StaticText(label)
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.AddStretchSpacer()
            sizer.Add(indicator, 0, wx.EXPAND|wx.ALL, 0)
            label.SetSizer(sizer)
            label._CDS_indicator = indicator
            label.Bind(wx.EVT_LEFT_DOWN, self.OnLabelClicked)
            label.Bind(wx.EVT_LEFT_DCLICK, self.OnLabelClicked)
            return label

    def GetCodeEditor(self):
        if len(self.editorCache):
            codeEditor = self.editorCache.pop()
            codeEditor.Show()
            return codeEditor
        else:
            codeEditor = pythonEditor.PythonEditor(self.container, self.parent, self.stackManager, style=wx.BORDER_NONE)
            codeEditor.SetUseVerticalScrollBar(False)
            codeEditor.Bind(wx.EVT_IDLE, self.CodeEditorOnIdle)
            codeEditor.Bind(wx.EVT_SET_FOCUS, self.CodeEditorFocused)
            codeEditor.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
            return codeEditor

    def GetCodeLine(self):
        if len(self.lineCache):
            line = self.lineCache.pop()
            line.Show()
            return line
        else:
            line = wx.Window(self, size=wx.Size(100, 1))
            line.SetBackgroundColour("#808080")
            return line

    def AddViewsForEvent(self, handlerName, code):
        isCodeEmpty = (len(code.strip()) == 0)

        label = self.GetCodeLabel()
        self.codeLabels[handlerName] = label

        codeEditor = self.GetCodeEditor()
        codeEditor.currentModel = self.currentUiView.model
        codeEditor.currentHandler = handlerName
        codeEditor.SetupWithText(code)
        codeEditor.EmptyUndoBuffer()
        self.codeEditors[handlerName] = codeEditor
        self.lastCursorSels[handlerName] = None

        line = self.GetCodeLine()
        self.codeLines[handlerName] = line
        self.lastLine = line

        self.editBox.Add(label, 0, wx.EXPAND|wx.ALL, 0)
        self.editBox.AddSpacer(2)
        self.editBox.Add(codeEditor, 1, wx.EXPAND|wx.ALL, 0)
        self.editBox.AddSpacer(8)
        self.editBox.Add(line, 0, wx.EXPAND|wx.ALL, 0)
        self.editBox.AddSpacer(8)

        self.UpdateEditorSize(handlerName)
        codeEditor.Show(not isCodeEmpty)
        self.UpdateLabelState(handlerName)

    def UpdateLabelState(self, handlerName):
        color = "black"
        code = self.currentUiView.model.handlers[handlerName]
        editor = self.codeEditors[handlerName]
        if len(code.strip()) == 0:
            color = "#777777"
        label = self.codeLabels[handlerName]
        font = wx.Font(wx.FontInfo(wx.Size(0, 14)).Family(wx.FONTFAMILY_TELETYPE))
        label.SetFont(font)
        label.SetForegroundColour(wx.Colour(color))
        label._CDS_indicator.SetLabel("(X)" if editor.IsShown() else "(+)")
        label._CDS_indicator.SetFont(font)
        label.SetLabel("def " + UiView.handlerDisplayNames[handlerName])

    def UpdateEditorSize(self, handlerName):
        editor = self.codeEditors[handlerName]
        height = (editor.GetLineCount()+1) * editor.TextHeight(0)+1
        editor.SetMinSize((100, height))
        editor.SetMaxSize((10000, height))
        self.Relayout()

    def Relayout(self):
        self.editBox.FitInside(self)
        self.editBox.Layout()
        self.Layout()

    def OnMouseWheel(self, event):
        if event.GetWheelAxis() == wx.MOUSE_WHEEL_VERTICAL:
            pos = self.GetViewStart()
            dy = event.GetWheelRotation()
            if event.IsWheelInverted():
                dy = -dy
            self.Scroll(pos[0], pos[1]+dy)
        else:
            event.Skip()

    def ShowEditor(self, handlerName, show):
        editor = self.codeEditors[handlerName]
        if not show:
            self.stackManager.view.SetFocus()
            editor.Hide()
        else:
            editor.Show()
            editor.SetFocus()
        self.UpdateLabelState(handlerName)
        self.Relayout()

    def OnSetFocus(self, event):
        self.stackManager.view.SetFocus()

    def OnLabelClicked(self, event):
        clickedLabel = event.GetEventObject()
        handlerName = None
        for key, label in self.codeLabels.items():
            if label == clickedLabel:
                handlerName = key
                break
        if handlerName:
            editor = self.codeEditors[handlerName]
            self.ShowEditor(handlerName, not editor.IsShown())

    def CodeEditorFocused(self, event):
        if self.currentUiView:
            codeEditor = event.GetEventObject()
            handlerName = codeEditor.currentHandler
            self.updateHelpTextFunc(helpData.HelpData.GetHandlerHelp(self.currentUiView, handlerName))
        event.Skip()

    def CodeEditorOnIdle(self, event):
        codeEditor = event.GetEventObject()
        handlerName = codeEditor.currentHandler
        self.SaveHandler(handlerName)
        event.Skip()

    def SaveHandler(self, handlerName):
        if self.currentUiView:
            if handlerName in self.codeEditors:
                codeEditor = self.codeEditors[handlerName]
                if codeEditor.HasFocus():
                    oldVal = self.currentUiView.model.GetHandler(handlerName)
                    newVal = codeEditor.GetText()
                    newCursorSel = codeEditor.GetSelection()

                    if newVal != oldVal:
                        command = appCommands.SetHandlerCommand(True, "Set Handler", self.parent,
                                                                self.stackManager.cardIndex, self.currentUiView.model,
                                                                handlerName, newVal,
                                                                self.lastCursorSels[handlerName], newCursorSel)
                        self.stackManager.command_processor.Submit(command)
                        self.UpdateLabelState(handlerName)
                        self.UpdateEditorSize(handlerName)
                    self.lastCursorSels[handlerName] = newCursorSel
