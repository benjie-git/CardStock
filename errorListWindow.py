import wx
import wx.html


class CardStockError(object):
    def __init__(self, card, obj, handlerName, lineNum, msg):
        self.card = card
        self.obj = obj
        self.handlerName = handlerName
        self.lineNum = lineNum
        self.msg = msg
        self.count = 0

    def __repr__(self):
        return f"<CardStockError: {self.msg} (count={self.count})>"


class ErrorListWindow(wx.Frame):
    def __init__(self, designer):
        super().__init__(designer, title="Error List", style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_TOOL_WINDOW|wx.FRAME_FLOAT_ON_PARENT)
        self.SetMinClientSize(wx.Size(300,20))
        self.SetClientSize(wx.Size(500,50))
        self.designer = designer
        self.errors = []
        self.listBox = wx.html.SimpleHtmlListBox(self, choices=[""], style=wx.html.HLB_DEFAULT_STYLE)
        self.listBox.SetBackgroundColour('#EE3333')
        self.listBox.Bind(wx.EVT_LISTBOX, self.OnListBox)
        self.listBox.Bind(wx.EVT_SIZE, self.OnListBoxResize)
        self.listBox.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)

    def SetErrorList(self, errorList):
        self.errors = errorList
        self.ConvertViewerToDesignerModels()
        self.listBox.Set([e.msg if e.count<=1 else f"{e.msg} ({e.count} times)" for e in self.errors])

    def OnListBoxResize(self, event):
        self.listBox.SetSize(self.GetClientSize())
        event.Skip(True)

    def OnListBox(self, event):
        self.JumpToError(self.errors[event.GetSelection()])
        self.listBox.SetSelection(wx.NOT_FOUND)

    def OnMouseDown(self, event):
        # Pre-Focus the listBox, so that even if this was not the top window, this click will still select a row
        self.Raise()
        self.listBox.SetFocus()
        event.Skip(True)

    def ConvertViewerToDesignerModels(self):
        # convert error objects from viewer's models, to designer's models
        for e in self.errors:
            if not e.card:
                continue
            cardName = e.card.GetProperty("name")
            for card in self.designer.stackManager.stackModel.childModels:
                if card.GetProperty("name") == cardName:
                    e.card = card
                    break
            else:
                e.card = None
                e.obj = None

            if e.card:
                objName = e.obj.GetProperty("name")
                if e.obj.type == "card":
                    e.obj = e.card
                else:
                    for obj in e.card.childModels:
                        if obj.GetProperty("name") == objName:
                            e.obj = obj
                            break
                    else:
                        e.card = None

    def JumpToError(self, error):
        if error.card:
            self.designer.cPanel.SetToolByName("hand")
            self.designer.stackManager.LoadCardAtIndex(error.card.parent.childModels.index(error.card))
            if error.obj:
                uiView = self.designer.stackManager.GetUiViewByModel(error.obj)
                self.designer.stackManager.SelectUiView(uiView)
                self.designer.cPanel.UpdateHandlerForUiViews([uiView], error.handlerName)
                ed = self.designer.cPanel.codeEditor
                if error.lineNum is not None:
                    ed.GotoLine(error.lineNum-1)
                    ed.SetSelectionStart(ed.GetLineEndPosition(error.lineNum-1) - ed.GetLineLength(error.lineNum-1))
                    ed.SetSelectionEnd(ed.GetLineEndPosition(error.lineNum-1))
                ed.SetFocus()
                self.designer.Raise()
