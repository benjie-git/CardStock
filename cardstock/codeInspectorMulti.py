import wx
import pythonEditor
import wx.stc
import helpData
import appCommands
from uiView import UiView


class CodeInspector(wx.ScrolledWindow):
    def __init__(self, cPanel, stackManager):
        super().__init__(cPanel, style=wx.BORDER_SUNKEN)
        self.SetBackgroundColour("#EEEEEE")
        self.AlwaysShowScrollbars(False, True)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self.Bind(wx.EVT_SIZE, self.OnResize)

        self.handlerPicker = None

        self.cPanel = cPanel
        self.stackManager = stackManager
        self.updateHelpTextFunc = None

        self.currentUiView = None
        self.codeEditors = {}
        self.editorCache = []

        self.SetScrollbars(1, 1, 1, 1)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetupEditorsForUiView(None)
        self.SetSizer(self.sizer)

    def ClearViews(self):
        self.sizer.Clear()

        for editorBlock in self.codeEditors.values():
            self.editorCache.append(editorBlock)
            editorBlock.Hide()
        self.codeEditors = {}

    def SetupEditorsForUiView(self, uiView):
        if uiView == self.currentUiView:
            return

        self.ClearViews()
        self.currentUiView = uiView

        if uiView:
            self.sizer.AddSpacer(5)
            for (handlerName, code) in uiView.model.handlers.items():
                editorBlock = self.GetEditorBlock()
                editorBlock.SetupForHandler(uiView, handlerName)
                self.codeEditors[handlerName] = editorBlock
                self.sizer.Add(editorBlock, 0, wx.EXPAND | wx.ALL, 0)
            self.UpdateEditorVisibility()

        if uiView:
            for (handlerName, code) in uiView.model.handlers.items():
                if len(code.strip()):
                    editorBlock = self.codeEditors[handlerName]
                    editorBlock.codeEditor.SetFocus()
                    break

    def UpdateEditorVisibility(self):
        if not self.currentUiView:
            return

        firstBlock = None
        lastBlock = None
        numShown = 0
        for (handlerName, code) in self.currentUiView.model.handlers.items():
            editorBlock = self.codeEditors[handlerName]
            isPopulated = len(code.strip()) > 0
            shouldShow = isPopulated or handlerName in self.currentUiView.model.additionalVisibleHandlers
            if shouldShow:
                if not firstBlock:
                    firstBlock = editorBlock
                editorBlock.ShowAddButton(False)
                editorBlock.ShowCloseButton(not isPopulated)
                editorBlock.line.Show()
                lastBlock = editorBlock
                numShown += 1

            editorBlock.Show(shouldShow)

        if numShown == 0:
            initial = self.currentUiView.model.initialEditHandler
            self.currentUiView.model.additionalVisibleHandlers.append(initial)
            firstBlock = lastBlock = self.codeEditors[initial]
            lastBlock.Show()
            numShown += 1

        disableAddButton = (numShown == len(self.currentUiView.model.handlers))
        firstBlock.ShowAddButton(True, disableAddButton)
        if numShown == 1:
            lastBlock.ShowCloseButton(False)
        lastBlock.line.Hide()  # Hide last botom-line

        for handlerName, block in self.codeEditors.items():
            if block.IsShown():
                block.UpdateLabelState(handlerName)
        self.Relayout()

    def GetAnalyzer(self):
        return self.stackManager.analyzer

    def GetEditorBlock(self):
        if len(self.editorCache):
            editorBlock = self.editorCache.pop()
            editorBlock.Show()
            return editorBlock
        else:
            editorBlock = EditorBlock(self, self.stackManager, self.cPanel)
            return editorBlock

    def Relayout(self):
        self.sizer.FitInside(self)

    def ShowEditorBlock(self, handlerName, show):
        editorBlock = self.codeEditors[handlerName]
        if not show:
            if editorBlock.codeEditor.HasFocus():
                self.stackManager.view.SetFocus()
            editorBlock.Hide()
        else:
            editorBlock.Show()
            editorBlock.codeEditor.SetFocus()
        editorBlock.UpdateLabelState(handlerName)
        editorBlock.UpdateEditorSize()
        self.Relayout()

    def GetCurrentHandler(self):
        if self.currentUiView:
            for (handlerName, editorBlock) in self.codeEditors.items():
                if editorBlock.codeEditor.HasFocus():
                    return handlerName
            for (handlerName, editorBlock) in self.codeEditors.items():
                if editorBlock.IsShown():
                    return handlerName
            return self.currentUiView.model.handlers[0]
        return None

    def UpdateHandlerForUiView(self, uiView, handlerName, selection=None):
        self.SetupEditorsForUiView(uiView)

        if uiView:
            if handlerName:
                editorBlock = self.codeEditors[handlerName]
                editorBlock.codeEditor.SetFocus()
                if selection and uiView:
                    firstLine = editorBlock.codeEditor.GetFirstVisibleLine()
                    editorBlock.codeEditor.AutoCompCancel()

                editorBlock.lastCursorSel = editorBlock.codeEditor.GetSelection()
                editorBlock.SetupForHandler(uiView, handlerName)
                self.ShowEditorBlock(handlerName, True)

                if selection:
                    editorBlock.codeEditor.SetSelection(*selection)
                    editorBlock.codeEditor.ScrollToLine(firstLine)
                    editorBlock.codeEditor.ScrollRange(*selection)
                    editorBlock.codeEditor.SetFocus()

                self.stackManager.analyzer.RunAnalysis()

    def SelectAndScrollTo(self, handlerName, selStart, selEnd):
        editorBlock = self.codeEditors[handlerName]
        self.ShowEditorBlock(handlerName, True)
        editorBlock.codeEditor.SetSelection(selStart, selEnd)
        editorBlock.codeEditor.ScrollRange(selStart, selEnd)
        editorBlock.codeEditor.SetFocus()

    def SelectAndScrollToLine(self, handlerName, selLine):
        editorBlock = self.codeEditors[handlerName]
        self.ShowEditorBlock(handlerName, True)
        editorBlock.codeEditor.GotoLine(selLine)
        lineEnd = editorBlock.codeEditor.GetLineEndPosition(selLine)
        lineLen = editorBlock.codeEditor.GetLineLength(selLine)
        editorBlock.codeEditor.SetSelectionStart(lineEnd-lineLen)
        editorBlock.codeEditor.SetSelectionEnd(lineEnd)
        editorBlock.codeEditor.SetFocus()

    def SelectInCodeForHandlerName(self, handlerName, selectStart, selectEnd):
        editorBlock = self.codeEditors[handlerName]
        self.ShowEditorBlock(handlerName, True)
        editorBlock.codeEditor.SetSelection(selectStart, selectEnd)
        editorBlock.codeEditor.ScrollRange(selectStart, selectEnd)
        editorBlock.codeEditor.SetFocus()

    def GetCodeEditorSelection(self, handlerName):
        editorBlock = self.codeEditors[handlerName]
        start, end = editorBlock.codeEditor.GetSelection()
        text = editorBlock.codeEditor.GetSelectedText()
        return (start, end, text)

    def OnMouseWheel(self, event):
        if event.GetWheelAxis() == wx.MOUSE_WHEEL_VERTICAL:
            pos = self.GetViewStart()
            dy = event.GetWheelRotation()
            if event.IsWheelInverted():
                dy = -dy
            self.Scroll(pos[0], pos[1]+dy)
        else:
            event.Skip()

    def OnPlusClicked(self, event):
        displayNames = []
        for k in self.currentUiView.model.GetHandlers().keys():
            displayNames.append(UiView.handlerDisplayNames[k])

        self.handlerPicker = wx.ListBox(self, choices=displayNames, style=wx.LB_SINGLE | wx.WANTS_CHARS)
        self.handlerPicker.Bind(wx.EVT_LEFT_UP, self.OnPickerMouseSelect)
        self.handlerPicker.Bind(wx.EVT_LISTBOX, self.OnPickerSelect)
        self.handlerPicker.Bind(wx.EVT_KEY_DOWN, self.OnPickerKey)
        self.handlerPicker.Bind(wx.EVT_MOTION, self.OnPickerMouseMove)
        self.handlerPicker.Bind(wx.EVT_NAVIGATION_KEY, self.OnPickerKey)
        self.handlerPicker.Bind(wx.EVT_KILL_FOCUS, self.OnPickerLostFocus)
        self.SetHandlerRect()

    def OnResize(self, event):
        if self.handlerPicker:
            self.SetHandlerRect()
        event.Skip()

    def SetHandlerRect(self):
        handlers = self.currentUiView.model.GetHandlers().keys()
        cs = self.GetClientSize()
        width = 300
        height = (4+len(handlers)*20) if wx.Platform == "__WXMAC__" else (4+len(handlers)*18)
        height = min (height, cs[1])
        self.handlerPicker.SetPosition((cs[0]-width,0))
        self.handlerPicker.SetSize(width, height)
        self.handlerPicker.SetFocus()

    def OnPickerMouseMove(self, event):
        index = self.handlerPicker.HitTest(event.GetPosition())
        if index != wx.NOT_FOUND:
            self.handlerPicker.SetSelection(index)
        handlerName = self.GetPickerSelectedHandler()
        self.updateHelpTextFunc(helpData.HelpData.GetHandlerHelp(self.currentUiView, handlerName))

    def OnPickerMouseSelect(self, event):
        self.AddHandler()
        event.Skip()

    def OnPickerKey(self, event):
        if event.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.AddHandler()
        elif event.GetKeyCode() in (wx.WXK_ESCAPE, wx.WXK_BACK, wx.WXK_DELETE):
            self.handlerPicker.DestroyLater()
            self.handlerPicker = None
        else:
            event.Skip()

    def OnPickerLostFocus(self, event):
        self.handlerPicker.DestroyLater()
        self.handlerPicker = None
        event.Skip()

    def GetPickerSelectedHandler(self):
        displayName = self.handlerPicker.GetString(self.handlerPicker.GetSelection())
        displayName = displayName.strip().replace("def ", "")
        keys = list(UiView.handlerDisplayNames.keys())
        vals = list(UiView.handlerDisplayNames.values())
        return keys[vals.index(displayName)]

    def OnPickerSelect(self, event):
        handlerName = self.GetPickerSelectedHandler()
        self.updateHelpTextFunc(helpData.HelpData.GetHandlerHelp(self.currentUiView, handlerName))
        event.Skip()

    def AddHandler(self):
        handlerName = self.GetPickerSelectedHandler()
        self.currentUiView.model.additionalVisibleHandlers.append(handlerName)
        self.UpdateEditorVisibility()
        self.handlerPicker.DestroyLater()
        self.handlerPicker = None
        self.codeEditors[handlerName].codeEditor.SetFocus()

    def OnBlockClick(self, event):
        editorBlock = event.GetEventObject()
        editorBlock.codeEditor.SetFocus()

    def CloseBlock(self, handlerName):
        if handlerName in self.currentUiView.model.additionalVisibleHandlers:
            self.currentUiView.model.additionalVisibleHandlers.remove(handlerName)
        self.UpdateEditorVisibility()

    def OnSetFocus(self, event):
        self.stackManager.view.SetFocus()

    def CodeEditorFocused(self, event):
        if self.currentUiView:
            codeEditor = event.GetEventObject()
            handlerName = codeEditor.currentHandler
            self.updateHelpTextFunc(helpData.HelpData.GetHandlerHelp(self.currentUiView, handlerName))
        event.Skip()


class EditorBlock(wx.Window):
    plusBmp = None
    minusBmp = None
    closeBmp = None

    def __init__(self, parent, stackManager, cPanel):
        super().__init__(parent)
        self.Bind(wx.EVT_LEFT_DOWN, parent.OnBlockClick)
        self.stackManager = stackManager
        self.parent = parent
        self.cPanel = cPanel
        self.uiView = None
        self.canShowClose = False

        if not EditorBlock.plusBmp:
            EditorBlock.plusBmp = wx.ArtProvider.GetBitmap(wx.ART_PLUS, size=wx.Size(20,20))
        if not EditorBlock.minusBmp:
            EditorBlock.minusBmp = wx.ArtProvider.GetBitmap(wx.ART_MINUS, size=wx.Size(20,20))
        if not EditorBlock.closeBmp:
            EditorBlock.closeBmp = wx.ArtProvider.GetBitmap(wx.ART_CLOSE, size=wx.Size(10,10))

        self.label = wx.StaticText(self)
        self.addButton = wx.StaticBitmap(self)
        self.addButton.SetToolTip("Add Event")
        self.addButton.Bind(wx.EVT_LEFT_DOWN, self.parent.OnPlusClicked)
        self.addButton.Bind(wx.EVT_LEFT_DCLICK, self.parent.OnPlusClicked)
        self.closeButton = wx.StaticBitmap(self, bitmap=EditorBlock.closeBmp)
        self.closeButton.SetToolTip("Close")
        self.closeButton.Bind(wx.EVT_LEFT_DOWN, self.OnBlockClose)
        self.closeButton.Bind(wx.EVT_LEFT_DCLICK, self.OnBlockClose)

        self.headerSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.headerSizer.Add(self.label, 1, wx.EXPAND | wx.ALL, 4)
        self.headerSizer.Add(self.addButton, 0, wx.EXPAND | wx.ALL, 1)
        self.headerSizer.AddSpacer(8)
        self.headerSizer.Add(self.closeButton, 0, wx.EXPAND | wx.ALL, 1)
        self.headerSizer.AddSpacer(4)

        self.codeEditor = pythonEditor.PythonEditor(self, cPanel, self.stackManager, style=wx.BORDER_NONE)
        self.codeEditor.SetUseVerticalScrollBar(False)
        self.codeEditor.SetUseHorizontalScrollBar(True)
        self.codeEditor.Bind(wx.EVT_IDLE, self.CodeEditorOnIdle)
        self.codeEditor.Bind(wx.EVT_SET_FOCUS, parent.CodeEditorFocused)
        self.codeEditor.Bind(wx.EVT_MOUSEWHEEL, parent.OnMouseWheel)
        self.lastCursorSel = None

        self.line = wx.Window(self, size=wx.Size(100, 1))
        self.line.SetBackgroundColour("#AAAAAA")

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.headerSizer, 0, wx.EXPAND|wx.ALL, 0)
        self.sizer.Add(self.codeEditor, 0, wx.EXPAND|wx.ALL, 0)
        self.sizer.AddSpacer(8)
        self.sizer.Add(self.line, 0, wx.EXPAND|wx.ALL, 0)
        self.sizer.AddSpacer(8)
        self.SetSizer(self.sizer)

    def SetupForHandler(self, uiView, handlerName):
        self.uiView = uiView
        code = uiView.model.handlers[handlerName]
        self.codeEditor.currentModel = self.uiView.model
        self.codeEditor.currentHandler = handlerName
        self.codeEditor.SetupWithText(code)
        self.codeEditor.EmptyUndoBuffer()
        self.codeEditor.Fit()
        self.line.Show()
        self.addButton.Hide()
        self.UpdateLabelState(handlerName)
        wx.CallAfter(self.UpdateEditorSize)

    def ShowAddButton(self, show, disable=False):
        self.addButton.Show(show)
        self.addButton.Enable(not disable)

    def ShowCloseButton(self, show):
        self.canShowClose = show

    def OnBlockClose(self, event):
        self.parent.CloseBlock(self.codeEditor.currentHandler)

    def UpdateLabelState(self, handlerName):
        color = "black"
        code = self.uiView.model.handlers[handlerName]
        if len(code.strip()) == 0:
            color = "#555555"
        font = wx.Font(wx.FontInfo(wx.Size(0, 14)).Family(wx.FONTFAMILY_TELETYPE))
        self.label.SetFont(font)
        self.label.SetForegroundColour(wx.Colour(color))
        self.label.SetLabel("def " + UiView.handlerDisplayNames[handlerName])

        isPopulated = len(code.strip()) > 0
        self.closeButton.Show(self.canShowClose and not isPopulated)

        self.addButton.SetBitmap(EditorBlock.plusBmp)
        self.headerSizer.Layout()

    def UpdateEditorSize(self):
        height = (self.codeEditor.GetLineCount()+1) * self.codeEditor.TextHeight(0)+1
        self.codeEditor.SetMinClientSize((100, height))
        self.codeEditor.SetMaxClientSize((100000, height))
        self.Fit()
        self.parent.Relayout()

    def SaveHandler(self, handlerName):
        if self.uiView:
                if self.codeEditor.HasFocus():
                    oldVal = self.uiView.model.GetHandler(handlerName)
                    newVal = self.codeEditor.GetText()
                    newCursorSel = self.codeEditor.GetSelection()

                    if newVal != oldVal:
                        command = appCommands.SetHandlerCommand(True, "Set Handler", self.cPanel,
                                                                self.stackManager.cardIndex, self.uiView.model,
                                                                handlerName, newVal,
                                                                self.lastCursorSel, newCursorSel)
                        self.stackManager.command_processor.Submit(command)
                        self.UpdateEditorSize()
                    if (len(newVal.strip())==0) != (len(oldVal.strip())==0):
                        self.UpdateLabelState(handlerName)
                    self.lastCursorSel = newCursorSel

    def CodeEditorOnIdle(self, event):
        codeEditor = event.GetEventObject()
        handlerName = codeEditor.currentHandler
        self.SaveHandler(handlerName)
        event.Skip()

