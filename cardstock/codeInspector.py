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


class CodeInspectorContainer(wx.Window):
    def __init__(self, cPanel, stackManager):
        super().__init__(cPanel)
        self.codeInspector = CodeInspector(self, cPanel, stackManager)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.codeInspector, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(sizer)



class CodeInspector(wx.Window):
    def __init__(self, parent, cPanel, stackManager):
        super().__init__(parent)

        self.parent = parent
        self.cPanel = cPanel
        self.stackManager = stackManager
        self.updateHelpTextFunc = None

        self.currentUiView = None
        self.currentHandler = None
        self.lastCursorSel = None

        self.handlerPicker = wx.Choice(parent=self)
        self.handlerPicker.Enable(False)
        self.handlerPicker.Bind(wx.EVT_CHOICE, self.OnHandlerChoice)

        self.codeEditor = pythonEditor.PythonEditor(self, cPanel, self.stackManager, style=wx.BORDER_SUNKEN)
        self.codeEditor.Bind(wx.EVT_IDLE, self.CodeEditorOnIdle)
        self.codeEditor.Bind(wx.EVT_SET_FOCUS, self.CodeEditorFocused)

        spacing = 6
        self.editBox = wx.BoxSizer(wx.VERTICAL)
        self.editBox.Add(self.handlerPicker, 0, wx.EXPAND|wx.ALL, spacing)
        self.editBox.Add(self.codeEditor, 1, wx.EXPAND|wx.ALL, spacing)
        self.editBox.SetSizeHints(self)
        self.SetSizer(self.editBox)

    def GetAnalyzer(self):
        return self.codeEditor.analyzer

    def GetCurrentHandler(self):
        return self.currentHandler

    def SelectAndScrollTo(self, handlerName, selStart, selEnd):
        if self.currentHandler == handlerName:
            self.codeEditor.SetSelection(selStart, selEnd)
            self.codeEditor.ScrollRange(selStart, selEnd)
            self.codeEditor.SetFocus()

    def SelectAndScrollToLine(self, handlerName, selLine):
        if self.currentHandler == handlerName:
            self.codeEditor.GotoLine(selLine)
            lineEnd = self.codeEditor.GetLineEndPosition(selLine)
            lineLen = self.codeEditor.GetLineLength(selLine)
            self.codeEditor.SetSelectionStart(lineEnd-lineLen)
            self.codeEditor.SetSelectionEnd(lineEnd)
            self.codeEditor.SetFocus()

    def UpdateHandlerForUiView(self, uiView, handlerName, selection=None):
        if not uiView:
            self.codeEditor.SetupWithText("")
            self.codeEditor.Enable(False)
            self.handlerPicker.Enable(False)
            self.codeEditor.currentModel = None
            self.codeEditor.currentHandler = None
            return

        self.codeEditor.Enable(True)
        self.handlerPicker.Enable(True)
        self.currentUiView = uiView

        if handlerName is None:
            handlerName = uiView.lastEditedHandler
        if not handlerName:
            for k in uiView.model.GetHandlers().keys():
                if uiView.model.GetHandler(k):
                    handlerName = k
                    break
            else:
                handlerName = uiView.model.initialEditHandler
        if handlerName:
            self.currentHandler = handlerName

        displayNames = []
        for k in uiView.model.GetHandlers().keys():
            decorator = "def " if uiView.model.GetHandler(k) else "       "
            displayNames.append(decorator + UiView.handlerDisplayNames[k])
        self.handlerPicker.SetItems(displayNames)
        self.handlerPicker.SetSelection(list(uiView.model.GetHandlers().keys()).index(self.currentHandler))

        if selection and self.currentUiView == uiView and self.currentHandler == handlerName:
            firstLine = self.codeEditor.GetFirstVisibleLine()
            self.codeEditor.AutoCompCancel()

        self.codeEditor.SetupWithText(uiView.model.GetHandler(self.currentHandler))

        self.lastCursorSel = self.codeEditor.GetSelection()
        self.codeEditor.EmptyUndoBuffer()
        self.handlerPicker.Enable(True)
        self.codeEditor.Enable(True)

        if selection:
            self.codeEditor.SetSelection(*selection)
            self.codeEditor.ScrollToLine(firstLine)
            self.codeEditor.ScrollRange(*selection)
            self.codeEditor.SetFocus()

        self.codeEditor.currentModel = uiView.model
        self.codeEditor.currentHandler = self.currentHandler
        self.stackManager.analyzer.RunAnalysis()
        uiView.lastEditedHandler = self.currentHandler

    def GetCodeEditorSelection(self, handlerName):
        start, end = self.codeEditor.GetSelection()
        text = self.codeEditor.GetSelectedText()
        return (start, end, text)

    def OnHandlerChoice(self, event):
        displayName = self.handlerPicker.GetItems()[self.handlerPicker.GetSelection()]
        displayName = displayName.strip().replace("def ", "")
        keys = list(UiView.handlerDisplayNames.keys())
        vals = list(UiView.handlerDisplayNames.values())
        self.SaveCurrentHandler()
        self.UpdateHandlerForUiView(self.stackManager.GetSelectedUiViews()[0], keys[vals.index(displayName)])
        self.codeEditor.SetFocus()
        if self.currentUiView:
            self.updateHelpTextFunc(helpDataGen.HelpData.GetHandlerHelp(self.currentUiView.model, self.currentHandler))


    # Internal

    def CodeEditorFocused(self, event):
        helpText = None
        if self.currentUiView:
            self.updateHelpTextFunc(helpDataGen.HelpData.GetHandlerHelp(self.currentUiView.model, self.currentHandler))
        event.Skip()

    def CodeEditorOnIdle(self, event):
        if self.currentHandler:
            self.SaveCurrentHandler()
        event.Skip()

    def SaveCurrentHandler(self):
        if self.codeEditor.HasFocus():
            uiView = self.stackManager.GetSelectedUiViews()[0]
            if uiView:
                oldVal = uiView.model.GetHandler(self.currentHandler)
                newVal = self.codeEditor.GetText()
                newCursorSel = self.codeEditor.GetSelection()

                if newVal != oldVal:
                    command = appCommands.SetHandlerCommand(True, "Set Handler", self.cPanel, self.stackManager.cardIndex, uiView.model,
                                                self.currentHandler, newVal, self.lastCursorSel, newCursorSel)
                    self.stackManager.command_processor.Submit(command)
                self.lastCursorSel = newCursorSel
