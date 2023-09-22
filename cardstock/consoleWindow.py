# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import wx.stc as stc
from io import StringIO
import pythonEditor
from wx.lib.docview import CommandProcessor, Command
from codeRunnerThread import RunOnMainSync
import sys

INPUT_STYLE = stc.STC_STYLE_DEFAULT
OUTPUT_STYLE = 28
ERR_STYLE = 29

cmdHistory = []


class ConsoleWindow(wx.Frame):
    def __init__(self, parent, allowInput):
        super().__init__(parent, title="Console", style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_TOOL_WINDOW)
        self.SetMinClientSize(self.FromDIP(wx.Size(300,75)))
        self.SetClientSize(self.FromDIP(wx.Size(500,200)))

        self.textBox = pythonEditor.PythonEditor(self, None, parent.stackManager, skipLexer=True, style=wx.BORDER_SIMPLE | stc.STC_WRAP_WORD)
        self.textBox.returnHandler = self.OnReturn
        self.textBox.SetUseHorizontalScrollBar(False)
        self.textBox.SetWrapMode(stc.STC_WRAP_WORD)
        self.textBox.SetMarginType(1, wx.stc.STC_MARGIN_BACK)
        self.textBox.SetMarginWidth(1, 3)
        #self.textBox.SetCaretStyle(stc.STC_CARETSTYLE_INVISIBLE)
        self.textBox.StyleSetSpec(INPUT_STYLE, "fore:#000000,size:14")
        self.textBox.StyleSetSpec(ERR_STYLE, "fore:#aa0000,size:14")
        self.textBox.StyleSetSpec(OUTPUT_STYLE, "fore:#555555,size:14")

        self.funcBeforeCode = None
        self.funcAfterCode = None

        self.allowInput = allowInput
        self.timer = None
        self.stdoutIO = None
        self.stderrIO = None
        self.stdoutPos = 0
        self.stderrPos = 0
        self.old_stdout = None
        self.old_stderr = None
        self.hasShown = False
        if self.allowInput:
            self.textBox.ChangeValue("> ")
            self.lastOutputPos = 2
        else:
            self.textBox.ChangeValue("")
            self.lastOutputPos = 0
            self.textBox.SetEditable(False)
        self.oldCmdText = ""
        self.oldCmdSelection = (0,0)
        self.needsNewPrompt = False
        self.historyPos = None  # None means we're on live input, not history
        self.stackUndoCount = 0
        self.command_processor = CommandProcessor()
        self.skipChanges = False
        self.workingCommand = None
        self.Hide()
        self.SetStreamsUp()
        self.runner = None
        self.didSetDown = False
        self.inputFunc = None

        self.textBox.Bind(stc.EVT_STC_ZOOM, self.OnZoom)
        self.textBox.Bind(stc.EVT_STC_CHARADDED, self.OnChar)
        self.textBox.Bind(stc.EVT_STC_CHANGE, self.OnTextChange)
        self.textBox.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.textBox.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.textBox.Bind(stc.EVT_STC_UPDATEUI, self.UpdateEditable)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def Show(self, doShow=True):
        super().Show(doShow)
        if doShow and not self.hasShown:
            self.SetClientSize((self.GetParent().GetSize().Width, self.FromDIP(100)))
            self.SetPosition(self.GetParent().GetPosition() + (0, self.GetParent().GetSize().Height))
            self.textBox.SetSelection(self.lastOutputPos, self.lastOutputPos)
            self.Raise()
            self.UpdateAC()
            self.hasShown = True
            self.GetParent().Raise()

    def Focus(self):
        self.Raise()
        self.textBox.SetFocus()

    def Destroy(self):
        self.SetStreamsDown()
        return super().Destroy()

    def OnResize(self, event):
        self.textBox.SetSize(self.GetClientSize())
        event.Skip()

    def OnZoom(self, event):
        z = event.GetEventObject().GetZoom()
        if z != 0:
            event.GetEventObject().SetZoom(0)

    def DoUndo(self, event=None):
        if self.command_processor.CanUndo():
            self.skipChanges = True
            self.command_processor.Undo()
            self.oldCmdText = self.GetCommandText()
            self.skipChanges = False
        else:
            if self.runner.stackManager.command_processor.CanUndo():
                self.runner.stackManager.command_processor.Undo()
                self.stackUndoCount += 1

    def DoRedo(self, event=None):
        if self.stackUndoCount:
            if self.runner.stackManager.command_processor.CanRedo():
                self.runner.stackManager.command_processor.Redo()
                self.stackUndoCount -= 1
        elif self.command_processor.CanRedo():
            self.skipChanges = True
            self.command_processor.Redo()
            self.oldCmdText = self.GetCommandText()
            self.skipChanges = False
        elif self.runner.stackManager.command_processor.CanRedo():
                self.runner.stackManager.command_processor.Redo()
                self.stackUndoCount -= 1

    def ClearUndoHistory(self):
        self.command_processor.ClearCommands()
        self.oldCmdText = self.GetCommandText()
        self.oldCmdSelection = (0,0)

    def OnTextChange(self, event):
        if not self.skipChanges:
            newText = self.GetCommandText()
            if newText != self.oldCmdText:
                newSel = self.oldCmdSelection[0] + len(newText) - len(self.oldCmdText)
                newSel = (newSel, newSel)
                command = TextEditCommand(True, "Change Text", self, self.oldCmdText, newText, self.oldCmdSelection, newSel)
                self.command_processor.Submit(command)
                self.oldCmdText = newText
                self.oldCmdSelection = newSel
                self.stackUndoCount = 0
        event.Skip()

    def OnChar(self, event):
        if self.textBox.GetLastPosition() - self.lastOutputPos == 1:
            # On first char added to the line, update AutoComplete data
            self.UpdateAC()
        event.Skip()

    def UpdateAC(self):
        # Update the analyzer for autocomplete
        vars = self.runner.GetClientVars()
        if self.runner.stackManager:
            self.runner.stackManager.analyzer.SetRuntimeVarNames(vars)

    def GetCommandText(self):
        return self.textBox.GetTextRange(self.lastOutputPos, self.textBox.GetLastPosition())

    def SetCommandText(self, text):
        if len(text) and text[-1] == "\n":
            text = text[:-1]
        self.textBox.Replace(self.lastOutputPos, self.textBox.GetLastPosition(), text)
        self.textBox.SetSelection(self.textBox.GetLastPosition(), self.textBox.GetLastPosition())
        self.textBox.ScrollToEnd()
        if not self.skipChanges:
            self.ClearUndoHistory()

    def OnKeyDown(self, event):
        # Handle Up/Down arrow keys
        if self.textBox.IsEditable() and not self.textBox.AutoCompActive():
            key = event.GetKeyCode()
            if key in [wx.WXK_UP, wx.WXK_NUMPAD_UP]:
                if self.inputFunc: return
                if self.historyPos is None:
                    if len(cmdHistory):
                        self.workingCommand = self.GetCommandText()
                        self.historyPos = len(cmdHistory) - 1
                        self.SetCommandText(cmdHistory[self.historyPos])
                elif self.historyPos > 0:
                    self.historyPos -= 1
                    self.SetCommandText(cmdHistory[self.historyPos])
                return
            elif key in [wx.WXK_DOWN, wx.WXK_NUMPAD_DOWN] and len(cmdHistory):
                if self.inputFunc: return
                if self.historyPos is not None and self.historyPos < len(cmdHistory)-1:
                    self.historyPos += 1
                    self.SetCommandText(cmdHistory[self.historyPos])
                    return
                elif self.historyPos == len(cmdHistory)-1:
                    self.historyPos = None
                    self.SetCommandText(self.workingCommand)
                    return
        elif chr(event.GetUnicodeKey()).isalnum() and self.allowInput and not self.textBox.IsEditable():
            last = self.textBox.GetLastPosition()
            self.textBox.SetSelection(last, last)
            self.UpdateEditable()

        event.Skip()

    def OnClose(self, event):
        event.Veto()
        self.Hide()

    def SetStreamsUp(self):
        self.stdoutIO = StringIO()
        self.stderrIO = StringIO()
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        sys.stdout = self.stdoutIO
        sys.stderr = self.stderrIO
        self.timer = wx.Timer()
        self.timer.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer.Start(100)

    def SetStreamsDown(self):
        if self.timer:
            self.timer.Stop()
            self.timer = None

        # Make sure not to lose any last bytes from the steams
        self.didSetDown = True
        self.stdoutIO.flush()
        self.stderrIO.flush()
        self.OnTimer(None)

        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        self.old_stdout = None
        self.old_stderr = None
        self.stdoutIO = None
        self.stderrIO = None

    def UpdateEditable(self, event=None):
        # Only make the text editable when the cursor is in the current command
        if self.allowInput:
            start = self.textBox.GetSelectionStart()
            end = self.textBox.GetSelectionEnd()
            if not wx.GetMouseState().LeftIsDown() and start == end and start < self.lastOutputPos and start >= self.lastOutputPos - 2:
                start = self.lastOutputPos
                end = start
                self.textBox.SetSelection(start, end)
            editable = (start >= self.lastOutputPos and end >= self.lastOutputPos)
            self.textBox.SetEditable(editable)
        else:
            self.textBox.SetEditable(False)

    def OnMouseUp(self, event):
        if self.allowInput:
            wx.CallAfter(self.UpdateEditable)
        event.Skip()

    def Clear(self):
        if self.allowInput:
            self.textBox.SetEditable(True)
            self.textBox.ChangeValue("> ")
            self.lastOutputPos = 2
            self.UpdateEditable()
            self.textBox.SetSelection(self.lastOutputPos, self.lastOutputPos)
        else:
            self.textBox.ChangeValue("  ")

    def RemovePrompt(self):
        self.SetCommandText("")
        last = self.textBox.GetLastPosition()
        self.textBox.Replace(last-2, last, "  ")
        # self.lastOutputPos -= 2

    def OnReturn(self):
        # Return key was pressed, and not for autocompletion, nor in the middle of a multiline command entry
        if self.inputFunc:
            last = self.textBox.GetLastPosition()
            self.textBox.SetSelection(last, last)
            self.UpdateEditable()
            text = self.GetCommandText()
            self.textBox.AppendText('\n')
            self.lastOutputPos = self.textBox.GetLastPosition()
            self.textBox.SetSelection(self.lastOutputPos, self.lastOutputPos)
            self.AppendText('> ', INPUT_STYLE, False)
            self.inputFunc(text)
            self.inputFunc = None
            return

        if self.allowInput:
            last = self.textBox.GetLastPosition()
            self.textBox.SetSelection(last, last)
            self.UpdateEditable()
            code = self.GetCommandText()
            self.textBox.AppendText('\n')
            self.lastOutputPos = self.textBox.GetLastPosition()
            self.textBox.SetSelection(self.lastOutputPos, self.lastOutputPos)
            if len(code.strip()) > 0:
                cmdHistory.append(code)
                self.historyPos = None
                if self.funcBeforeCode:
                    self.funcBeforeCode()
                self.runner.EnqueueCode(code)
                if self.funcAfterCode:
                    self.runner.EnqueueFunction(self.funcAfterCode)
            self.ClearUndoHistory()
            @RunOnMainSync
            def on_done():
                self.AppendText('> ', INPUT_STYLE, False)
                self.ClearUndoHistory()
            self.runner.EnqueueFunction(on_done)

    def AppendText(self, text, style, beforeInput):
        scrollPos = self.textBox.GetScrollPos(wx.VERTICAL) + self.textBox.LinesOnScreen()
        scrollRange = self.textBox.GetScrollRange(wx.VERTICAL)
        selPos = self.textBox.GetSelection()

        self.textBox.SetEditable(True)

        self.skipChanges = True
        start = self.textBox.GetLastPosition()
        if self.allowInput:
            insertPos = (self.lastOutputPos-2) if beforeInput else start
        else:
            insertPos = self.lastOutputPos
        self.textBox.InsertText(insertPos, text)
        end = self.textBox.GetLastPosition()
        insertedLen = end-start

        self.textBox.StartStyling(insertPos)
        self.textBox.SetStyling(insertedLen, style)
        self.lastOutputPos += insertedLen
        self.textBox.SetSelection(selPos[0]+insertedLen, selPos[1]+insertedLen)
        self.UpdateEditable()
        self.skipChanges = False

        if scrollPos > scrollRange - 4:
            self.textBox.ScrollToEnd()

    def OnTimer(self, event):
        def readStream(stream, pos, oldStream):
            stream.seek(pos)
            s = stream.read()
            if len(s):
                oldStream.write(s)
                if not self.didSetDown:
                    self.AppendText(s, ERR_STYLE if stream == self.stderrIO else OUTPUT_STYLE, True)
                    if not self.hasShown:
                        self.Show()
            return pos + len(s)

        self.stdoutPos = readStream(self.stdoutIO, self.stdoutPos, self.old_stdout)
        self.stderrPos = readStream(self.stderrIO, self.stderrPos, self.old_stderr)
        if not self.didSetDown:
            if self.textBox.GetLastPosition() < self.lastOutputPos:
                # The user backspaced into non-editable text!
                self.lastOutputPos -= 1
                self.AppendText(' ', INPUT_STYLE, False)


class TextEditCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.console = args[2]
        self.oldText = args[3]
        self.newText = args[4]
        self.oldSel = args[5]
        self.newSel = args[6]
        self.didRun = False

    def Do(self):
        if self.didRun:
            self.console.SetCommandText(self.newText)
            s = [max(0,n+self.console.lastOutputPos) for n in self.newSel]
            self.console.textBox.SetSelection(*s)
        self.didRun = True
        return True

    def Undo(self):
        self.console.SetCommandText(self.oldText)
        s = [max(0,n+self.console.lastOutputPos) for n in self.oldSel]
        self.console.textBox.SetSelection(*s)
        return True

