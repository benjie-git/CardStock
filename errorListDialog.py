import wx


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


class ErrorListDialog(wx.Frame):
    def __init__(self, designer, errorList):
        super().__init__(designer, title="Errors")
        self.designer = designer
        self.errors = errorList
        self.ConvertViewerToDesignerModels()
        self.CreateStatusBar()
        box = wx.BoxSizer(wx.VERTICAL)
        self.listBox = wx.ListBox(self, size=(500, 60), style=wx.LB_SINGLE,
                                  choices=[e.msg if e.count==1 else f"{e.msg} ({e.count} times)" for e in self.errors])
        box.Add(self.listBox, 0, wx.EXPAND)
        self.SetSizerAndFit(box)
        self.Centre()
        self.listBox.Bind(wx.EVT_LISTBOX, self.OnListBox)

    def OnListBox(self, event):
        self.JumpToError(self.errors[event.GetSelection()])
        self.listBox.SetSelection(wx.NOT_FOUND)

    def ConvertViewerToDesignerModels(self):
        # convert error objects from viewer's models, to designer's models
        for e in self.errors:
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
            self.designer.stackManager.LoadCardAtIndex(error.card.parent.childModels.index(error.card))
            if error.obj:
                uiView = self.designer.stackManager.GetUiViewByModel(error.obj)
                self.designer.stackManager.SelectUiView(uiView)
                self.designer.cPanel.UpdateHandlerForUiViews([uiView], error.handlerName)
                ed = self.designer.cPanel.codeEditor
                ed.GotoLine(error.lineNum-1)
                ed.SetSelectionStart(ed.GetLineEndPosition(error.lineNum-1) - ed.GetLineLength(error.lineNum-1))
                ed.SetSelectionEnd(ed.GetLineEndPosition(error.lineNum-1))
