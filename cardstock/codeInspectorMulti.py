# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import pythonEditor
import wx.stc
import helpDataGen
import appCommands
from uiView import UiView
from simpleListBox import SimpleListBox

HEADER_HEIGHT = 30

class CodeInspectorContainer(wx.Window):
    """ Contains the codeInspector, and the fixed-position 'Add Event' button """
    def __init__(self, cPanel, stackManager):
        super().__init__(cPanel)
        self.cPanel = cPanel
        self.codeInspector = CodeInspector(self, cPanel, stackManager)
        self.Bind(wx.EVT_SIZE, self.OnResize)

        self.addButton = wx.Button(self, label="Add Event")
        self.addButton.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_PLUS, size=wx.Size(19,19)))
        self.addButton.Bind(wx.EVT_BUTTON, self.codeInspector.OnPlusClicked)
        self.addButton.Fit()

    def OnResize(self, event):
        if wx.Platform == "__WXMSW__":
            self.codeInspector.SetRect(wx.Rect((0,self.FromDIP(24)), event.GetSize()-(0,self.FromDIP(24))))
            self.addButton.SetPosition((self.codeInspector.Size.Width - self.addButton.Size.Width, 0))
        elif wx.Platform == "__WXGTK__":
            self.codeInspector.SetRect(wx.Rect((0, 12), event.GetSize()-(0,12)))
            self.addButton.SetPosition((self.codeInspector.Size.Width - self.addButton.Size.Width - 26, 0))
        else:
            self.codeInspector.SetRect(wx.Rect((0, 0), event.GetSize()))
            self.addButton.SetPosition((self.codeInspector.ClientSize.Width - self.addButton.Size.Width - 20, 2))
        event.Skip()


class CodeInspector(wx.ScrolledWindow):
    """
    Contains a block for each available handler for the selected object.
    Manages their visibility and scrolling.
    """
    def __init__(self, parent, cPanel, stackManager):
        super().__init__(parent, style=wx.BORDER_SUNKEN)
        self.SetBackgroundColour('white')
        self.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        self.EnableScrolling(False, True)

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
        self.lastFocusedHandler = None

        self.blockCache = []

        self.SetScrollbars(1, 1, 1, 1)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetupEditorsForUiView(None)
        self.SetSizer(self.sizer)

    def ShouldScrollToChildOnFocus(self, child):
        return False

    def ClearViews(self):
        """ Remove all blocks in preparation for setting up or a new view. """
        self.sizer.Clear()

        for editorBlock in self.blocks.values():
            self.blockCache.append(editorBlock)
            editorBlock.Hide()
        self.blocks = {}
        self.lastFocusedHandler = None

    def SetupEditorsForUiView(self, uiView):
        if uiView == self.currentUiView:
            return

        self.ClearViews()
        self.currentUiView = uiView

        self.container.addButton.Show(uiView is not None)

        if uiView:
            if wx.Platform == "__WXMSW__":
                self.sizer.AddSpacer(5)
            else:
                bar = wx.Window(self, size=wx.Size(10, HEADER_HEIGHT))
                bar.SetBackgroundColour(wx.Colour('#EEEEEE'))
                self.sizer.Add(bar, 0, wx.EXPAND | wx.ALL, 0)

            for (handlerName, code) in uiView.model.handlers.items():
                editorBlock = self.GetEditorBlock()
                editorBlock.SetupForHandler(uiView, handlerName)
                self.blocks[handlerName] = editorBlock
                self.sizer.Add(editorBlock, 0, wx.EXPAND | wx.ALL, 0)
            # self.sizer.AddSpacer(100)

            self.UpdateEditorVisibility()
            if wx.Platform != "__WXMSW__":
                self.Scroll(0, HEADER_HEIGHT)

            # for (handlerName, code) in uiView.model.handlers.items():
            #     if len(code.strip()):
            #         editorBlock = self.blocks[handlerName]
            #         break

    def UpdateEditorVisibility(self):
        if not self.currentUiView:
            return

        lastBlock = None
        numShown = 0
        for (handlerName, code) in self.currentUiView.model.handlers.items():
            editorBlock = self.blocks[handlerName]
            isPopulated = len(code.strip()) > 0
            if isPopulated:
                self.currentUiView.model.visibleHandlers.add(handlerName)
            if handlerName in self.currentUiView.model.visibleHandlers:
                editorBlock.SetCanShowCloseButton(True)
                editorBlock.line.Show()
                lastBlock = editorBlock
                numShown += 1
                editorBlock.Show()
            else:
                editorBlock.Hide()

        if numShown == 0 and len(self.blocks):
            initial = self.currentUiView.model.initialEditHandler
            self.currentUiView.model.visibleHandlers.add(initial)
            lastBlock = self.blocks[initial]
            lastBlock.SetCanShowCloseButton(False)
            lastBlock.Show()
            numShown += 1

        if numShown == 1:
            lastBlock.SetCanShowCloseButton(False)
        if numShown > 0:
            lastBlock.line.Hide()  # Hide last block's bottom-line

        self.visibleBlocks = []
        for handlerName, block in self.blocks.items():
            if block.IsShown():
                self.visibleBlocks.append(block)
                block.UpdateLabelState(handlerName)
                block.UpdateEditorSize()
        self.Relayout()

    def GetEditorBlock(self):
        """ Get an editor block from the cache, or create a new one if we've run out. """
        if len(self.blockCache):
            editorBlock = self.blockCache.pop()
            editorBlock.Show()
            return editorBlock
        else:
            editorBlock = EditorBlock(self, self.stackManager, self.cPanel)
            return editorBlock

    def Relayout(self):
        """ Layout the blocks, e.g. after changing block visibility. """
        self.sizer.FitInside(self)

    def GetCurrentHandler(self):
        """ Determine the handler currently being edited.  """
        if self.currentUiView:
            if self.lastFocusedHandler:
                return self.lastFocusedHandler
            for (handlerName, editorBlock) in self.blocks.items():
                if editorBlock.codeEditor.HasFocus():
                    return handlerName
            for (handlerName, editorBlock) in self.blocks.items():
                if editorBlock.IsShown():
                    return handlerName
            return self.currentUiView.model.handlers[0]
        return None

    def UpdateHandlerForUiView(self, uiView, handlerName=None, selection=None):
        """
        Set up the codeInspector for the specified view, focus any given handler, and select any given selection.
        """
        self.SetupEditorsForUiView(uiView)

        if uiView and handlerName:
            editorBlock = self.blocks[handlerName]
            if not editorBlock.IsShown():
                self.currentUiView.model.visibleHandlers.add(handlerName)
                self.UpdateEditorVisibility()

            if selection and uiView:
                firstLine = editorBlock.codeEditor.GetFirstVisibleLine()
                editorBlock.codeEditor.AutoCompCancel()

            editorBlock.lastCursorSel = editorBlock.codeEditor.GetSelection()
            editorBlock.SetupForHandler(uiView, handlerName)
            editorBlock.UpdateLabelState(handlerName)

            if selection:
                self.SelectAndScrollTo(handlerName, *selection)
            else:
                self.SelectAndScrollTo(handlerName, *selection)

            self.stackManager.analyzer.RunAnalysis()

    def SelectAndScrollTo(self, handlerName, selStart, selEnd):
        editorBlock = self.blocks[handlerName]
        if not editorBlock.IsShown():
            self.currentUiView.model.visibleHandlers.add(handlerName)
            self.UpdateEditorVisibility()
        editorBlock.codeEditor.SetFocus()
        editorBlock.codeEditor.SetSelection(selStart, selEnd)
        editorBlock.codeEditor.ScrollRange(selStart, selEnd)
        editorBlock.ScrollParentIfNeeded()

    def SelectAndScrollToLine(self, handlerName, selLine):
        editorBlock = self.blocks[handlerName]
        if not editorBlock.IsShown():
            self.currentUiView.model.visibleHandlers.add(handlerName)
            self.UpdateEditorVisibility()
        lineEnd = editorBlock.codeEditor.GetLineEndPosition(selLine)
        lineLen = editorBlock.codeEditor.GetLineLength(selLine)
        editorBlock.codeEditor.SetFocus()
        editorBlock.codeEditor.SetSelectionStart(lineEnd-lineLen)
        editorBlock.codeEditor.SetSelectionEnd(lineEnd)
        editorBlock.ScrollParentIfNeeded()

    def GetCodeEditorSelection(self, handlerName):
        editorBlock = self.blocks[handlerName]
        start, end = editorBlock.codeEditor.GetSelection()
        text = editorBlock.codeEditor.GetSelectedText()
        return (start, end, text)

    def OnMouseWheel(self, event):
        """
        Make sure vertical scrolling works smoothly across all blocks, labels, etc.
        """
        if event.GetWheelAxis() == wx.MOUSE_WHEEL_VERTICAL:
            pos = self.GetViewStart()
            dy = event.GetWheelRotation()
            # if event.IsWheelInverted():
            #     dy = -dy
            self.Scroll(pos[0], pos[1]-dy)
        else:
            event.Skip()

    def OnPlusClicked(self, event):
        """
        Create and open the Add Event handlerPicker.
        """
        self.container.addButton.Hide()
        if wx.Platform == "__WXMSW__":
            self.container.Disable()
        displayNames = []
        for k in self.currentUiView.model.GetHandlers().keys():
            displayNames.append(k+'()')

        self.handlerPicker = SimpleListBox(self.cPanel, True)
        self.handlerPicker.SetupWithItems(displayNames, 3, 0)
        self.handlerPicker.doneFunc = self.OnHandlerPickerDone
        self.handlerPicker.selectFunc = self.OnHandlerPickerSelectionChanged
        self.SetHandlerPickerPos()
        self.handlerPicker.SetFocus()
        event.Skip()

    def SetHandlerPickerPos(self):
        cs = self.GetClientSize()
        hpSize = self.handlerPicker.GetSize()
        cPanelHeight = self.cPanel.GetSize().Height
        cPos = self.container.GetPosition()
        offset = -15
        if (cPos.y+hpSize.Height > cPanelHeight+15):
            offset = cPanelHeight - hpSize.Height - cPos.y
        self.handlerPicker.SetPosition(cPos + (cs[0]-hpSize.Width, offset))

    def OnResize(self, event):
        if self.handlerPicker:
            self.SetHandlerPickerPos()
        event.Skip()

    def DisplayNameToRawName(self, displayName):
        name = displayName.strip().replace("()", "")
        return name

    def OnHandlerPickerDone(self, index, text):
        if self.handlerPicker:
            hp = self.handlerPicker
            self.handlerPicker = None
            if text:
                handlerName = self.DisplayNameToRawName(text)
                if handlerName not in self.currentUiView.model.visibleHandlers:
                    self.currentUiView.model.visibleHandlers.add(handlerName)
                    self.UpdateEditorVisibility()
                self.blocks[handlerName].UpdateEditorSize()
                self.stackManager.view.SetFocus()
                def f():
                    self.blocks[handlerName].codeEditor.SetFocus()
                    pos = self.blocks[handlerName].GetPosition()
                    self.Scroll(pos)
                wx.CallAfter(f)

            self.container.addButton.Show()
            if wx.Platform == "__WXMSW__":
                self.container.Enable()
            hp.DestroyLater()
            self.Refresh(True)

    def OnHandlerPickerSelectionChanged(self, index, text):
        if index is not None and self.currentUiView:
            handlerName = self.DisplayNameToRawName(text)
            self.updateHelpTextFunc(helpDataGen.HelpData.GetHandlerHelp(self.currentUiView.model, handlerName))

    def OnMouseDown(self, event):
        """
        Clicked in the codeInspector, outside of any block, so focus the first or last block's editor and select the
        first or last position, if the user clicked either above or below the editor blocks.
        """
        firstBlock = lastBlock = None
        for block in self.blocks.values():
            if block.codeEditor.currentHandler in self.currentUiView.model.visibleHandlers:
                if not firstBlock: firstBlock = block
                lastBlock = block
        if firstBlock:
            mouse_pos = event.GetPosition()
            if mouse_pos.y <= firstBlock.codeEditor.GetPosition().y:
                firstBlock.codeEditor.SetFocus()
                firstBlock.codeEditor.SetSelection(0, 0)
            elif mouse_pos.y > lastBlock.GetPosition().y:
                lastBlock.codeEditor.SetFocus()
                end = lastBlock.codeEditor.GetLastPosition()
                lastBlock.codeEditor.SetSelection(end, end)
        event.Skip()

    def OnBlockClick(self, event):
        """
        Clicked in a block, outside of the editor, so focus this block's editor and select the
        first or last position depending on whether the user clicked above or below the editor.
        """
        mouse_pos = event.GetPosition()
        editorBlock = event.GetEventObject()
        if isinstance(editorBlock, wx.StaticText):
            editorBlock = editorBlock.GetParent()
        editorBlock.codeEditor.SetFocus()
        if mouse_pos.y < editorBlock.codeEditor.GetPosition().y:
            editorBlock.codeEditor.SetSelection(0, 0)
            if self.currentUiView:
                self.updateHelpTextFunc(helpDataGen.HelpData.GetHandlerHelp(self.currentUiView.model,
                                                                         editorBlock.codeEditor.currentHandler))
        else:
            end = editorBlock.codeEditor.GetLastPosition()
            editorBlock.codeEditor.SetSelection(end, end)

        editorBlock.codeEditor.SetFocus()

    def CloseBlock(self, handlerName):
        """ User clicked a block's Close button. """
        if handlerName in self.currentUiView.model.visibleHandlers:
            self.currentUiView.model.visibleHandlers.remove(handlerName)
        self.UpdateEditorVisibility()

    def OnSetFocus(self, event):
        """ When focusing the codeInspector (not a codeEditor) give up focus to the stack manager.  """
        self.stackManager.view.SetFocus()

    def CodeEditorFocused(self, event):
        """ When focusing a codeEditor, scroll it into view. """
        if self.currentUiView:
            codeEditor = event.GetEventObject()
            handlerName = codeEditor.currentHandler
            if handlerName in self.blocks and self.blocks[handlerName].IsShown():
                wx.CallAfter(self.blocks[handlerName].ScrollParentIfNeeded)
                self.updateHelpTextFunc(helpDataGen.HelpData.GetHandlerHelp(self.currentUiView.model, handlerName))
                self.lastFocusedHandler = handlerName
        event.Skip()


class EditorBlock(wx.Window):
    """ One block of handlerName label and code editor. """
    closeBmp = None

    def __init__(self, parent, stackManager, cPanel):
        super().__init__(parent)
        self.Bind(wx.EVT_LEFT_DOWN, parent.OnBlockClick)
        self.Bind(wx.EVT_SET_FOCUS, parent.OnSetFocus)
        self.SetBackgroundColour('white')
        self.stackManager = stackManager
        self.parent = parent
        self.cPanel = cPanel
        self.uiView = None
        self.canShowClose = False

        if not EditorBlock.closeBmp:
            s = self.FromDIP(16 if (wx.Platform == "__WXGTK__") else 12)
            EditorBlock.closeBmp = wx.ArtProvider.GetBitmap(wx.ART_MINUS, size=wx.Size(s,s))

        self.label = wx.StaticText(self)
        self.label.Bind(wx.EVT_LEFT_DOWN, parent.OnBlockClick)
        self.label.SetBackgroundColour('white')

        self.closeButton = wx.StaticBitmap(self, wx.ID_ANY, bitmap=EditorBlock.closeBmp)
        self.closeButton.SetBackgroundColour("white")
        self.closeButton.SetToolTip("Hide Event")
        self.closeButton.Bind(wx.EVT_LEFT_DOWN, self.OnBlockClose)
        self.closeButton.Bind(wx.EVT_LEFT_DCLICK, self.OnBlockClose)

        self.headerSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.headerSizer.Add(self.label, 1, wx.EXPAND | wx.ALL, 4)
        self.headerSizer.AddSpacer(self.FromDIP(8))
        self.headerSizer.Add(self.closeButton, 0, wx.EXPAND | wx.ALL, 1)
        self.headerSizer.AddSpacer(self.FromDIP(4))

        self.codeEditor = pythonEditor.PythonEditor(self, cPanel, self.stackManager, style=wx.BORDER_NONE)
        self.codeEditor.SetUseVerticalScrollBar(False)
        self.codeEditor.SetUseHorizontalScrollBar(True)
        self.codeEditor.Bind(wx.EVT_IDLE, self.CodeEditorOnIdle)
        self.codeEditor.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
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
        self.sizer.AddSpacer(self.FromDIP(8))
        self.sizer.Add(self.line, 0, wx.EXPAND|wx.ALL, 0)
        self.sizer.AddSpacer(self.FromDIP(8))
        self.SetSizer(self.sizer)

    def SetupForHandler(self, uiView, handlerName):
        self.uiView = uiView
        code = uiView.model.handlers[handlerName]
        self.codeEditor.currentModel = self.uiView.model
        self.codeEditor.currentHandler = handlerName
        self.codeEditor.SetupWithText(code)
        self.UpdateEditorSize()
        self.codeEditor.EmptyUndoBuffer()

    def SetCanShowCloseButton(self, show):
        """ Can't show close button if this is the only visible block. """
        self.canShowClose = show

    def OnBlockClose(self, event):
        self.parent.CloseBlock(self.codeEditor.currentHandler)

    def UpdateLabelState(self, handlerName):
        """ Set up label color, text, close button visibility. """
        code = self.uiView.model.handlers[handlerName]

        color = "black"
        fsize = self.FromDIP(17 if wx.Platform != "__WXMSW__" else 15)
        fontInfo = wx.FontInfo(wx.Size(0, fsize)).Family(wx.FONTFAMILY_MODERN).Weight(wx.FONTWEIGHT_BOLD)
        if len(code.strip()) == 0:
            color = "#555555"
            fontInfo.Weight(wx.FONTWEIGHT_NORMAL)

        self.label.SetFont(wx.Font(fontInfo))
        self.label.SetForegroundColour(wx.Colour(color))
        self.label.SetLabel("def " + UiView.handlerDisplayNames[handlerName])

        isPopulated = len(code.strip()) > 0
        self.closeButton.Show(self.canShowClose and not isPopulated)

        self.headerSizer.Layout()

    def UpdateEditorSize(self):
        """ Keep the editor sized vertically to fit it's content. """
        height = (self.codeEditor.GetLineCount()+1) * self.codeEditor.TextHeight(0)+1
        if height != self.codeEditor.GetMaxClientSize().Height:
            self.parent.Freeze()
            self.codeEditor.SetMinClientSize((100, height))
            self.codeEditor.SetMaxClientSize((100000, height))
            self.Fit()
            self.parent.Relayout()
            self.parent.Thaw()

    def SaveHandler(self, handlerName):
        """ Save the event handler code after the user makes changes. """
        if self.uiView and self.uiView.model:
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
                    self.ScrollParentIfNeeded()
                if (len(newVal.strip())==0) != (len(oldVal.strip())==0):
                    self.UpdateLabelState(handlerName)
                self.lastCursorSel = newCursorSel

    def OnUpdateUi(self, event):
        if event.GetUpdated() == wx.stc.STC_UPDATE_SELECTION:
            self.codeEditor.AutoCompCancel()
            if self.codeEditor.HasFocus():
                wx.CallAfter(self.ScrollParentIfNeeded)
        event.Skip()

    def OnKeyDown(self, event):
        line = self.codeEditor.GetCurrentLine()
        if not self.codeEditor.AutoCompActive() and not event.ShiftDown() and self in self.parent.visibleBlocks:
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
            else:
                if event.GetKeyCode() not in (wx.WXK_SHIFT, wx.WXK_ALT, wx.WXK_CONTROL, wx.WXK_COMMAND):
                    wx.CallAfter(self.ScrollParentIfNeeded)
        event.Skip()

    def ScrollParentIfNeeded(self):
        """ Scroll the codeInspector to make the current line visible, if it wasn't. """
        line = self.codeEditor.GetCurrentLine()
        y = line * self.codeEditor.TextHeight(0)
        y += self.codeEditor.GetPosition().y
        pos = self.GetPosition()
        usp = self.parent.CalcUnscrolledPosition(pos).y
        y += usp
        vs = self.parent.GetViewStart()[1]
        s = self.parent.GetSize()[1]
        if y < vs:
            if line==0: y -= 20
            wx.CallAfter(self.parent.Scroll, 0, y)
        elif y+20 > vs + s:
            wx.CallAfter(self.parent.Scroll, 0, y-s+40)

    def OnEditorLostFocus(self, event):
        """ Remove selection, so non-focused editors don't show selections.  This was too confusing. """
        (_from, _to) = self.codeEditor.GetSelection()
        self.codeEditor.SetSelection(_to, _to)
        event.Skip()

    def CodeEditorOnIdle(self, event):
        """ Save on Idle, so we're not necessarily saving after every single keystroke. """
        codeEditor = event.GetEventObject()
        handlerName = codeEditor.currentHandler
        self.SaveHandler(handlerName)
        event.Skip()

