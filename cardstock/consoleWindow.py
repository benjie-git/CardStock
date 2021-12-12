import wx
import wx.stc as stc
from io import StringIO
import pythonEditor
from wx.lib.docview import CommandProcessor, Command
import sys

INPUT_STYLE = stc.STC_STYLE_DEFAULT
OUTPUT_STYLE = 28
ERR_STYLE = 29

cmdHistory = []


class ConsoleWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="Console", style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_TOOL_WINDOW)
        self.SetMinClientSize(wx.Size(300,100))
        self.SetClientSize(wx.Size(500,200))

        self.textBox = pythonEditor.PythonEditor(self, None, parent.stackManager, skipLexer=True, style=wx.BORDER_SIMPLE | stc.STC_WRAP_WORD)
        self.textBox.returnHandler = self.OnReturn
        self.textBox.SetUseHorizontalScrollBar(False)
        self.textBox.SetWrapMode(stc.STC_WRAP_WORD)
        self.textBox.SetMarginType(1, wx.stc.STC_MARGIN_BACK)
        self.textBox.SetMarginWidth(1, 3)
        #self.textBox.SetCaretStyle(stc.STC_CARETSTYLE_INVISIBLE)
        self.textBox.StyleSetSpec(INPUT_STYLE, "fore:#000000")
        self.textBox.StyleSetSpec(ERR_STYLE, "fore:#aa0000")
        self.textBox.StyleSetSpec(OUTPUT_STYLE, "fore:#555555")

        self.timer = None
        self.stdoutIO = None
        self.stderrIO = None
        self.stdoutPos = 0
        self.stderrPos = 0
        self.old_stdout = None
        self.old_stderr = None
        self.hasShown = False
        self.textBox.ChangeValue("> ")
        self.lastOutputPos = 2
        self.oldCmdText = ""
        self.oldCmdSelection = (0,0)
        self.textBox.SetSelection(2, 2)
        self.needsNewPrompt = False
        self.historyPos = None  # None means we're on live input, not history
        self.command_processor = CommandProcessor()
        self.skipChanges = False
        self.workingCommand = None
        self.Hide()
        self.SetStreamsUp()
        self.SetMenuBar(parent.GetMenuBar())
        self.runner = None

        self.textBox.Bind(stc.EVT_STC_ZOOM, self.OnZoom)
        self.textBox.Bind(stc.EVT_STC_CHARADDED, self.OnChar)
        self.textBox.Bind(stc.EVT_STC_CHANGE, self.OnTextChange)
        self.textBox.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.textBox.Bind(stc.EVT_STC_UPDATEUI, self.UpdateEditable)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def Show(self, shown=True):
        super().Show(shown)
        self.SetSize((self.GetParent().GetSize().Width, 100))
        self.SetPosition(self.GetParent().GetPosition() + (0, self.GetParent().GetSize().Height))
        self.UpdateAC()

    def Destroy(self):
        self.SetStreamsDown()
        return super().Destroy()

    def OnResize(self, event):
        self.textBox.SetSize(self.GetClientSize())

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

    def DoRedo(self, event=None):
        if self.command_processor.CanRedo():
            self.skipChanges = True
            self.command_processor.Redo()
            self.oldCmdText = self.GetCommandText()
            self.skipChanges = False

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
        event.Skip()

    def OnChar(self, event):
        if self.lastOutputPos == self.textBox.GetLastPosition():
            # On first char added to the line, update AutoComplete data
            self.UpdateAC()
        event.Skip()

    def UpdateAC(self):
        # Update the analyzer for autocomplete
        vars = self.runner.clientVars.copy()
        for v in self.runner.initialClientVars:
            vars.pop(v)
        if '__builtins__' in vars:
            vars.pop('__builtins__')
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
                if self.historyPos is not None and self.historyPos < len(cmdHistory)-1:
                    self.historyPos += 1
                    self.SetCommandText(cmdHistory[self.historyPos])
                    return
                elif self.historyPos == len(cmdHistory)-1:
                    self.historyPos = None
                    self.SetCommandText(self.workingCommand)
                    return
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
        start = self.textBox.GetSelectionStart()
        end = self.textBox.GetSelectionEnd()
        editable = (start >= self.lastOutputPos and end >= self.lastOutputPos)
        self.textBox.SetEditable(editable)

    def Clear(self):
        self.textBox.SetEditable(True)
        self.textBox.ChangeValue("> ")
        self.lastOutputPos = 2
        self.UpdateEditable()

    def OnReturn(self):
        # Return key was pressed, and not for autocompletion, nor in the middle of a multiline command entry
        code = self.GetCommandText()
        self.textBox.AppendText('\n')
        self.lastOutputPos = self.textBox.GetLastPosition()
        self.textBox.SetSelection(self.lastOutputPos, self.lastOutputPos)
        if len(code.strip()) > 0:
            cmdHistory.append(code)
            self.historyPos = None
            self.runner.EnqueueCode(code)
        self.AppendText('> ', INPUT_STYLE, False)
        self.ClearUndoHistory()

    def AppendText(self, text, style, beforeInput):
        scrollPos = self.textBox.GetScrollPos(wx.VERTICAL) + self.textBox.LinesOnScreen()
        scrollRange = self.textBox.GetScrollRange(wx.VERTICAL)
        selPos = self.textBox.GetSelection()

        self.textBox.SetEditable(True)

        self.skipChanges = True
        start = self.textBox.GetLastPosition()
        insertPos = (self.lastOutputPos-2) if beforeInput else start
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
                self.AppendText(s, ERR_STYLE if stream == self.stderrIO else OUTPUT_STYLE, True)
                oldStream.write(s)

                if not self.hasShown:
                    self.Show()
                    self.hasShown = True
            return pos + len(s)

        self.stdoutPos = readStream(self.stdoutIO, self.stdoutPos, self.old_stdout)
        self.stderrPos = readStream(self.stderrIO, self.stderrPos, self.old_stderr)
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

