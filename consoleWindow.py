import wx
import wx.stc as stc
from io import StringIO
import sys


class ConsoleWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="Output", style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_TOOL_WINDOW)
        self.SetMinClientSize(wx.Size(300,100))
        self.SetClientSize(wx.Size(500,200))

        self.textBox = stc.StyledTextCtrl(parent=self, style=wx.BORDER_SIMPLE | stc.STC_WRAP_WORD)
        self.textBox.SetUseHorizontalScrollBar(False)
        self.textBox.SetWrapMode(stc.STC_WRAP_WORD)
        self.textBox.SetMarginWidth(1, 0)
        self.textBox.EmptyUndoBuffer()
        self.textBox.SetCaretStyle(stc.STC_CARETSTYLE_INVISIBLE)
        self.textBox.StyleSetSpec(2, "fore:#aa0000")
        self.textBox.SetEditable(False)

        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.timer = None
        self.stdoutIO = None
        self.stderrIO = None
        self.stdoutPos = 0
        self.stderrPos = 0
        self.old_stdout = None
        self.old_stderr = None
        self.hasShown = False
        self.Hide()
        self.SetStreamsUp()

    def Show(self, shown=True):
        super().Show(shown)
        self.SetSize((self.GetParent().GetSize().Width, 100))
        self.SetPosition(self.GetParent().GetPosition() + (0, self.GetParent().GetSize().Height))

    def Destroy(self):
        self.SetStreamsDown()
        return super().Destroy()

    def OnResize(self, event):
        self.textBox.SetSize(self.GetClientSize())

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
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        self.old_stdout = None
        self.old_stderr = None
        self.stdoutIO = None
        self.stderrIO = None

    def OnTimer(self, event):
        def readStream(stream, pos, oldStream):
            stream.seek(pos)
            s = stream.read()
            if len(s):
                scrollPos = self.textBox.GetScrollPos(wx.VERTICAL) + self.textBox.LinesOnScreen()
                scrollRange = self.textBox.GetScrollRange(wx.VERTICAL)

                self.textBox.SetEditable(True)
                start = self.textBox.GetLastPosition()
                self.textBox.AppendText(s)
                end = self.textBox.GetLastPosition()
                if stream == self.stderrIO:
                    self.textBox.StartStyling(start)
                    self.textBox.SetStyling(end-start, 2)
                self.textBox.SetEditable(False)
                oldStream.write(s)

                if scrollPos > scrollRange - 4:
                    self.textBox.ScrollToEnd()

                if not self.hasShown and stream == self.stdoutIO:
                    self.Show()
                    self.hasShown = True
            return pos + len(s)

        self.stdoutPos = readStream(self.stdoutIO, self.stdoutPos, self.old_stdout)
        self.stderrPos = readStream(self.stderrIO, self.stderrPos, self.old_stderr)
