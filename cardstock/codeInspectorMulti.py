import wx
import pythonEditor
import wx.stc
import helpData
import appCommands
from uiView import UiView


class CodeInspectorContainer(wx.Window):
    def __init__(self, cPanel, stackManager):
        super().__init__(cPanel)
        self.codeInspector = CodeInspector(self, cPanel, stackManager)
        self.Bind(wx.EVT_SIZE, self.OnResize)

        self.addButton = wx.Button(self, label="Add Event")
        self.addButton.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_PLUS, size=wx.Size(19,19)))
        self.addButton.Bind(wx.EVT_LEFT_DOWN, self.codeInspector.OnPlusClicked)
        self.addButton.Bind(wx.EVT_LEFT_DCLICK, self.codeInspector.OnPlusClicked)
        self.addButton.Fit()

    def OnResize(self, event):
        self.codeInspector.SetRect(wx.Rect((0,0), event.GetSize()))
        self.addButton.SetPosition((self.codeInspector.ClientSize.Width - self.addButton.Size.Width-18, 2))
        event.Skip()


class CodeInspector(wx.ScrolledWindow):
    def __init__(self, parent, cPanel, stackManager):
        super().__init__(parent, style=wx.BORDER_SUNKEN)
        self.SetBackgroundColour('white')
        self.AlwaysShowScrollbars(False, True)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self.Bind(wx.EVT_SIZE, self.OnResize)

        self.handlerPicker = None

        self.container = parent
        self.cPanel = cPanel
        self.stackManager = stackManager
        self.updateHelpTextFunc = None

        self.currentUiView = None
        self.blocks = {}
        self.visibleBlocks = []

        self.blockCache = []

        self.SetScrollbars(1, 1, 1, 1)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetupEditorsForUiView(None)
        self.SetSizer(self.sizer)

    def ShouldScrollToChildOnFocus(self, child):
        return False

    def ClearViews(self):
        self.sizer.Clear()

        for editorBlock in self.blocks.values():
            self.blockCache.append(editorBlock)
            editorBlock.Hide()
        self.blocks = {}

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
                self.blocks[handlerName] = editorBlock
                self.sizer.Add(editorBlock, 0, wx.EXPAND | wx.ALL, 0)

            self.UpdateEditorVisibility()

            for (handlerName, code) in uiView.model.handlers.items():
                if len(code.strip()):
                    editorBlock = self.blocks[handlerName]
                    editorBlock.codeEditor.SetFocus()
                    break

    def UpdateEditorVisibility(self):
        if not self.currentUiView:
            return

        firstBlock = None
        lastBlock = None
        numShown = 0
        for (handlerName, code) in self.currentUiView.model.handlers.items():
            editorBlock = self.blocks[handlerName]
            isPopulated = len(code.strip()) > 0
            if isPopulated:
                self.currentUiView.model.visibleHandlers.append(handlerName)
            if handlerName in self.currentUiView.model.visibleHandlers:
                if not firstBlock:
                    firstBlock = editorBlock
                editorBlock.SetCanShowCloseButton(True)
                editorBlock.line.Show()
                lastBlock = editorBlock
                numShown += 1
                editorBlock.Show()
            else:
                editorBlock.Hide()

        if numShown == 0:
            initial = self.currentUiView.model.initialEditHandler
            self.currentUiView.model.visibleHandlers.append(initial)
            firstBlock = lastBlock = self.blocks[initial]
            lastBlock.SetCanShowCloseButton(False)
            lastBlock.Show()
            numShown += 1

        if numShown == 1:
            lastBlock.SetCanShowCloseButton(False)
        lastBlock.line.Hide()  # Hide last botom-line

        self.visibleBlocks = []
        for handlerName, block in self.blocks.items():
            if block.IsShown():
                self.visibleBlocks.append(block)
                block.UpdateLabelState(handlerName)
                block.UpdateEditorSize()
        self.Relayout()

    def GetAnalyzer(self):
        return self.stackManager.analyzer

    def GetEditorBlock(self):
        if len(self.blockCache):
            editorBlock = self.blockCache.pop()
            editorBlock.Show()
            return editorBlock
        else:
            editorBlock = EditorBlock(self, self.stackManager, self.cPanel)
            return editorBlock

    def Relayout(self):
        self.sizer.FitInside(self)

    def ShowEditorBlock(self, handlerName, show):
        editorBlock = self.blocks[handlerName]
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
            for (handlerName, editorBlock) in self.blocks.items():
                if editorBlock.codeEditor.HasFocus():
                    return handlerName
            for (handlerName, editorBlock) in self.blocks.items():
                if editorBlock.IsShown():
                    return handlerName
            return self.currentUiView.model.handlers[0]
        return None

    def UpdateHandlerForUiView(self, uiView, handlerName, selection=None):
        self.SetupEditorsForUiView(uiView)

        if uiView:
            if handlerName:
                editorBlock = self.blocks[handlerName]
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
        editorBlock = self.blocks[handlerName]
        self.ShowEditorBlock(handlerName, True)
        editorBlock.codeEditor.SetSelection(selStart, selEnd)
        editorBlock.codeEditor.ScrollRange(selStart, selEnd)
        editorBlock.codeEditor.SetFocus()

    def SelectAndScrollToLine(self, handlerName, selLine):
        editorBlock = self.blocks[handlerName]
        self.ShowEditorBlock(handlerName, True)
        editorBlock.codeEditor.GotoLine(selLine)
        lineEnd = editorBlock.codeEditor.GetLineEndPosition(selLine)
        lineLen = editorBlock.codeEditor.GetLineLength(selLine)
        editorBlock.codeEditor.SetSelectionStart(lineEnd-lineLen)
        editorBlock.codeEditor.SetSelectionEnd(lineEnd)
        editorBlock.codeEditor.SetFocus()

    def SelectInCodeForHandlerName(self, handlerName, selectStart, selectEnd):
        editorBlock = self.blocks[handlerName]
        self.ShowEditorBlock(handlerName, True)
        editorBlock.codeEditor.SetSelection(selectStart, selectEnd)
        editorBlock.codeEditor.ScrollRange(selectStart, selectEnd)
        editorBlock.codeEditor.SetFocus()

    def GetCodeEditorSelection(self, handlerName):
        editorBlock = self.blocks[handlerName]
        start, end = editorBlock.codeEditor.GetSelection()
        text = editorBlock.codeEditor.GetSelectedText()
        return (start, end, text)

    def OnMouseWheel(self, event):
        if event.GetWheelAxis() == wx.MOUSE_WHEEL_VERTICAL:
            pos = self.GetViewStart()
            dy = event.GetWheelRotation()
            # if event.IsWheelInverted():
            #     dy = -dy
            self.Scroll(pos[0], pos[1]-dy)
        else:
            event.Skip()

    def OnPlusClicked(self, event):
        self.container.addButton.Hide()
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
            self.container.addButton.Show()
        else:
            event.Skip()

    def OnPickerLostFocus(self, event):
        self.handlerPicker.DestroyLater()
        self.handlerPicker = None
        self.container.addButton.Show()
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
        self.currentUiView.model.visibleHandlers.append(handlerName)
        self.UpdateEditorVisibility()
        self.handlerPicker.DestroyLater()
        self.handlerPicker = None
        self.container.addButton.Show()
        self.blocks[handlerName].codeEditor.SetFocus()

    def OnMouseDown(self, event):
        lastBlock = None
        for block in self.blocks.values():
            if block.codeEditor.currentHandler in self.currentUiView.model.visibleHandlers:
                lastBlock = block
        if lastBlock:
            mousePos = event.GetPosition()
            if mousePos.y > lastBlock.GetPosition().y:
                lastBlock.codeEditor.SetFocus()
                end = lastBlock.codeEditor.GetLastPosition()
                lastBlock.codeEditor.SetSelection(end, end)
        event.Skip()

    def OnBlockClick(self, event):
        mousePos = event.GetPosition()
        editorBlock = event.GetEventObject()
        editorBlock.codeEditor.SetFocus()
        if mousePos.y < editorBlock.codeEditor.GetPosition().y:
            editorBlock.codeEditor.SetSelection(0, 0)
        else:
            end = editorBlock.codeEditor.GetLastPosition()
            editorBlock.codeEditor.SetSelection(end, end)

        editorBlock.codeEditor.SetFocus()

    def CloseBlock(self, handlerName):
        if handlerName in self.currentUiView.model.visibleHandlers:
            self.currentUiView.model.visibleHandlers.remove(handlerName)
        self.UpdateEditorVisibility()

    def OnSetFocus(self, event):
        self.stackManager.view.SetFocus()

    def CodeEditorFocused(self, event):
        if self.currentUiView:
            codeEditor = event.GetEventObject()
            handlerName = codeEditor.currentHandler
            self.blocks[handlerName].ScrollParentIfNeeded()
            self.updateHelpTextFunc(helpData.HelpData.GetHandlerHelp(self.currentUiView, handlerName))
        event.Skip()


class EditorBlock(wx.Window):
    closeBmp = None

    def __init__(self, parent, stackManager, cPanel):
        super().__init__(parent)
        self.Bind(wx.EVT_LEFT_DOWN, parent.OnBlockClick)
        self.SetBackgroundColour('white')
        self.stackManager = stackManager
        self.parent = parent
        self.cPanel = cPanel
        self.uiView = None
        self.canShowClose = False

        if not EditorBlock.closeBmp:
            EditorBlock.closeBmp = wx.ArtProvider.GetBitmap(wx.ART_CLOSE, size=wx.Size(12,12))

        self.label = wx.StaticText(self)
        self.label.SetBackgroundColour('white')
        self.closeButton = wx.StaticBitmap(self, bitmap=EditorBlock.closeBmp)
        self.closeButton.SetToolTip("Close")
        self.closeButton.Bind(wx.EVT_LEFT_DOWN, self.OnBlockClose)
        self.closeButton.Bind(wx.EVT_LEFT_DCLICK, self.OnBlockClose)

        self.headerSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.headerSizer.Add(self.label, 1, wx.EXPAND | wx.ALL, 4)
        self.headerSizer.AddSpacer(8)
        self.headerSizer.Add(self.closeButton, 0, wx.EXPAND | wx.ALL, 1)
        self.headerSizer.AddSpacer(4)

        self.codeEditor = pythonEditor.PythonEditor(self, cPanel, self.stackManager, style=wx.BORDER_NONE)
        self.codeEditor.SetUseVerticalScrollBar(False)
        self.codeEditor.SetUseHorizontalScrollBar(True)
        self.codeEditor.Bind(wx.EVT_IDLE, self.CodeEditorOnIdle)
        self.codeEditor.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.codeEditor.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.codeEditor.Bind(wx.stc.EVT_STC_UPDATEUI, self.OnUpdateUi)
        self.codeEditor.Bind(wx.EVT_SET_FOCUS, parent.CodeEditorFocused)
        self.codeEditor.Bind(wx.EVT_KILL_FOCUS, self.OnEditorLostFocus)
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
        self.UpdateLabelState(handlerName)
        self.UpdateEditorSize()

    def SetCanShowCloseButton(self, show):
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

    def OnUpdateUi(self, event):
        if event.GetUpdated() == wx.stc.STC_UPDATE_SELECTION:
            self.ScrollParentIfNeeded()
        event.Skip()

    def OnKeyDown(self, event):
        line = self.codeEditor.GetCurrentLine()
        if event.GetKeyCode() in (wx.WXK_UP, wx.WXK_NUMPAD_UP) and line == 0:
            index = self.parent.visibleBlocks.index(self)
            if index > 0:
                ed = self.parent.visibleBlocks[index-1].codeEditor
                ed.SetSelection(ed.GetLastPosition(), ed.GetLastPosition())
                ed.SetFocus()
        elif event.GetKeyCode() in (wx.WXK_DOWN, wx.WXK_NUMPAD_DOWN) and line == self.codeEditor.GetNumberOfLines()-1:
            index = self.parent.visibleBlocks.index(self)
            if index < len(self.parent.visibleBlocks)-1:
                ed = self.parent.visibleBlocks[index+1].codeEditor
                ed.SetSelection(0,0)
                ed.SetFocus()
        event.Skip()

    def OnKeyUp(self, event):
        self.ScrollParentIfNeeded()
        event.Skip()

    def ScrollParentIfNeeded(self):
        line = self.codeEditor.GetCurrentLine()
        if line == 0: line = -1
        y = line * self.codeEditor.TextHeight(0)
        y += self.codeEditor.GetPosition().y
        pos = self.GetPosition()
        usp = self.parent.CalcUnscrolledPosition(pos).y
        y += usp
        vs = self.parent.GetViewStart()[1]
        s = self.parent.GetSize()[1]
        if y < vs:
            wx.CallAfter(self.parent.Scroll, 0, y-20)
        elif y+20 > vs + s:
            wx.CallAfter(self.parent.Scroll, 0, y-s+40)

    def OnEditorLostFocus(self, event):
        (_from, _to) = self.codeEditor.GetSelection()
        self.codeEditor.SetSelection(_to, _to)
        event.Skip()

    def CodeEditorOnIdle(self, event):
        codeEditor = event.GetEventObject()
        handlerName = codeEditor.currentHandler
        self.SaveHandler(handlerName)
        event.Skip()

