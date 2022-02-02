import wx
LINE_HEIGHT = 20


class SimpleListBox(wx.Control):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, style=wx.WANTS_CHARS, **kwargs)
        fSize = 14
        if wx.Platform == "__WXGTK__": fSize = 18
        if wx.Platform == "__WXMSW__": fSize = 16
        self.SetFont(wx.Font(wx.FontInfo(wx.Size(0, fSize)).Family(wx.FONTFAMILY_MODERN)))

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_NAVIGATION_KEY, self.OnKeyDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseMove)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnLostFocus)

        self.parent = parent
        self.items = []
        self.matchCharIndex = 0
        self.selection = 0
        self.selectFunc = None
        self.doneFunc = None

    def SetupWithItems(self, items, matchCharIndex, selectedStr=None):
        self.items = items
        self.matchCharIndex = matchCharIndex
        self.selection = 0
        if selectedStr:
            i = self.items.index(selectedStr)
            self.selection = i
        width = 100  # min width
        for i in self.items:
            w,h = self.GetTextExtent(i)
            if w > width:
                width = w
        self.SetSize((width+20, LINE_HEIGHT*len(self.items)+3))

    def SetSelection(self, sel):
        self.selection = sel
        self.Refresh(True)

    def SetStringSelection(self, s):
        if s:
            self.selection = self.items.index(s)
        self.Refresh(True)

    def DoClose(self):
        self.Hide()

    def OnMouseMove(self, event):
        pos = event.GetPosition()
        i = min(pos.y//LINE_HEIGHT, len(self.items)-1)
        if i != self.selection:
            self.UpdateSelection(i)
        event.Skip()

    def OnMouseUp(self, event):
        self.OnMouseMove(event)
        self.DoClose()
        event.Skip()

    def ChooseCurrentItem(self):
        if wx.Platform != "__WXGTK__" and wx.GetKeyState(wx.WXK_ESCAPE):
                self.selection = None
        if self.doneFunc:
            if self.selection is not None:
                self.doneFunc(self.selection, self.items[self.selection])
            else:
                self.doneFunc(None, None)
            self.doneFunc = None

    def OnKeyDown(self, event):
        if event.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_SPACE):
            self.DoClose()
        elif event.GetKeyCode() == wx.WXK_UP:
            if self.selection > 0:
                self.UpdateSelection(self.selection-1)
        elif event.GetKeyCode() == wx.WXK_DOWN:
            if self.selection < len(self.items)-1:
                self.UpdateSelection(self.selection+1)
        elif event.GetKeyCode() == wx.WXK_ESCAPE:
            self.selection = None
            self.DoClose()
        else:
            c = event.GetKeyCode()
            if ord('A') <= c <= ord('Z') or ord('0') <= c <= ord('9') or c in (ord(c) for c in "-_+=/?., "):
                newSel = None

                if self.selection is not None and self.selection < len(self.items)+1 and\
                        self.items[self.selection][self.matchCharIndex] == chr(c):
                    for i in self.items[self.selection+1:]:
                        if len(i) > self.matchCharIndex:
                            if i[self.matchCharIndex] == chr(c):
                                newSel = self.items.index(i)
                                break

                if newSel is None:
                    for i in self.items:
                        if len(i) > self.matchCharIndex:
                            if i[self.matchCharIndex] == chr(c):
                                newSel = self.items.index(i)
                                break
                if newSel is not None:
                    self.UpdateSelection(newSel)
                    return

    def UpdateSelection(self, i):
        self.selection = i
        self.Refresh(True)
        if self.selectFunc:
            self.selectFunc(self.selection, self.items[self.selection])

    def OnLostFocus(self, event):
        self.ChooseCurrentItem()
        self.DoClose()

    def OnEraseBackground(self, event):
        # No thank you!
        # This event was causing bad flickering on Windows.  Much better now!
        pass

    def OnPaint(self, event):
        (width, height) = self.GetSize()
        dc = wx.PaintDC(self)

        dc.SetPen(wx.Pen('gray', 1))
        dc.SetBrush(wx.Brush('#F8F8F8'))
        dc.DrawRectangle(wx.Rect(1,1,width-3,height-3))

        dc.SetBrush(wx.Brush('blue'))
        dc.DrawRectangle(1, self.selection*LINE_HEIGHT, width-4, LINE_HEIGHT)

        font = self.GetFont()
        dc.SetFont(font)
        dc.SetTextForeground("#222222")

        lineNum = 0
        for line in self.items:
            if lineNum == self.selection:
                dc.SetTextForeground("#EEEEEE")
            dc.DrawText(line, wx.Point(4, lineNum*LINE_HEIGHT+2))
            if lineNum == self.selection:
                dc.SetTextForeground("#222222")
            lineNum += 1

        event.Skip()
