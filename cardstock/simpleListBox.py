# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
LINE_HEIGHT = 20


class SimpleListBox(wx.Control):
    def __init__(self, parent, shouldCapture, **kwargs):
        super().__init__(parent, style=wx.WANTS_CHARS, **kwargs)
        fSize = 18
        if wx.Platform == "__WXGTK__": fSize = 18
        if wx.Platform == "__WXMSW__": fSize = 16
        fSize = self.FromDIP(fSize)
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
        self.shouldCapture = shouldCapture
        self.items = []
        self.matchCharIndex = 0
        self.selection = None
        self.selectFunc = None
        self.doneFunc = None

    def SetupWithItems(self, items, matchCharIndex, selectedStr=None):
        self.items = items
        self.matchCharIndex = matchCharIndex
        self.selection = None
        if selectedStr:
            i = self.items.index(selectedStr)
            self.selection = i
        width = 100  # min width
        for i in self.items:
            w,h = self.GetTextExtent(i)
            if w > width:
                width = w
        self.SetSize(self.FromDIP(wx.Size(self.ToDIP(width)+20, LINE_HEIGHT*len(self.items)+3)))
        if self.shouldCapture and not self.HasCapture():
            self.CaptureMouse()

    def SetSelection(self, sel):
        self.selection = sel
        self.Refresh(True)

    def SetStringSelection(self, s):
        if s:
            self.selection = self.items.index(s)
        self.Refresh(True)

    def DoClose(self, success):
        if self.shouldCapture and self.HasCapture():
            self.ReleaseMouse()
        if not success and self.doneFunc:
            self.selection = None
        self.ChooseCurrentItem()
        self.Hide()

    def OnMouseMove(self, event):
        pos = event.GetPosition()
        s = self.GetSize()
        if 0 <= pos.x <= s.Width and 0 <= pos.y <= s.Height:
            lheight = self.FromDIP(LINE_HEIGHT)
            i = min(pos.y//lheight, len(self.items)-1)
            if 0 <= i < len(self.items) and i != self.selection:
                self.UpdateSelection(i)
        else:
            if self.selection is not None:
                self.UpdateSelection(None)

        event.Skip()

    def OnMouseUp(self, event):
        self.OnMouseMove(event)
        self.DoClose(True)
        event.Skip()

    def ChooseCurrentItem(self):
        if self.doneFunc:
            if self.selection is not None:
                self.doneFunc(self.selection, self.items[self.selection])
            else:
                self.doneFunc(None, None)
            self.doneFunc = None

    def OnKeyDown(self, event):
        if event.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_SPACE):
            self.DoClose(True)
        elif event.GetKeyCode() == wx.WXK_UP:
            if self.selection is None:
                self.UpdateSelection(len(self.items)-1)
            elif self.selection > 0:
                self.UpdateSelection(self.selection-1)
        elif event.GetKeyCode() == wx.WXK_DOWN:
            if self.selection is None:
                self.UpdateSelection(0)
            elif self.selection < len(self.items)-1:
                self.UpdateSelection(self.selection+1)
        elif event.GetKeyCode() == wx.WXK_ESCAPE:
            self.selection = None
            self.DoClose(False)
        else:
            c = event.GetKeyCode()
            if ord('A') <= c <= ord('Z') or ord('0') <= c <= ord('9') or c in (ord(c) for c in "-_+=/?., "):
                newSel = None

                if self.selection is not None and self.selection < len(self.items)+1 and\
                        self.items[self.selection][self.matchCharIndex].lower() == chr(c).lower():
                    for i in self.items[self.selection+1:]:
                        if len(i) > self.matchCharIndex:
                            if i[self.matchCharIndex].lower() == chr(c).lower():
                                newSel = self.items.index(i)
                                break

                if newSel is None:
                    for i in self.items:
                        if len(i) > self.matchCharIndex:
                            if i[self.matchCharIndex].lower() == chr(c).lower():
                                newSel = self.items.index(i)
                                break
                if newSel is not None:
                    self.UpdateSelection(newSel)
                    return

    def UpdateSelection(self, i):
        self.selection = i
        self.Refresh(True)
        if self.selectFunc:
            if self.selection is not None:
                self.selectFunc(self.selection, self.items[self.selection])
            else:
                self.selectFunc(self.selection, None)

    def OnLostFocus(self, event):
        self.DoClose(False)

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

        if self.selection is not None:
            dc.SetBrush(wx.Brush('blue'))
            dc.DrawRectangle(self.FromDIP(1), self.FromDIP(self.selection*LINE_HEIGHT), self.FromDIP(width-4), self.FromDIP(LINE_HEIGHT))

        font = self.GetFont()
        dc.SetFont(font)
        dc.SetTextForeground("#222222")

        lineNum = 0
        for line in self.items:
            if lineNum == self.selection:
                dc.SetTextForeground("#EEEEEE")
            dc.DrawText(line, self.FromDIP(wx.Point(4, lineNum*LINE_HEIGHT+2)))
            if lineNum == self.selection:
                dc.SetTextForeground("#222222")
            lineNum += 1

        event.Skip()
