import wx
import wx.grid
import uiView


class VariablesWindow(wx.Frame):
    def __init__(self, parent, stackManager):
        super().__init__(parent, title="Variables", style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_TOOL_WINDOW)
        self.SetMinClientSize(wx.Size(300,100))
        self.SetClientSize(wx.Size(300,500))

        self.stackManager = stackManager
        self.path = []
        self.keys = None
        self.vars = None
        self.hasShown = False

        self.pathLabel = wx.StaticText(self)
        self.pathLabel.Bind(wx.EVT_LEFT_DOWN, self.OnPathClick)

        self.grid = wx.grid.Grid(self, -1)
        self.grid.CreateGrid(2, 2)
        self.grid.SetRowSize(0, 25)
        self.grid.SetColSize(0, 100)
        self.grid.SetColLabelSize(20)
        self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelValue(0, "Name")
        self.grid.SetColLabelValue(1, "Value")
        self.grid.DisableDragRowSize()
        # self.grid.DisableDragColSize()
        self.grid.SetSelectionMode(wx.grid.Grid.GridSelectNone)

        self.grid.Bind(wx.EVT_SIZE, self.OnResize)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnGridDClick)
        # self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnInspectorValueChanged)
        # self.grid.Bind(wx.EVT_KEY_DOWN, self.OnGridEnter)
        # self.grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnGridCellSelected)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.pathLabel, 0, wx.EXPAND|wx.ALL, 3)
        sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 3)
        self.SetSizerAndFit(sizer)
        sizer.Layout()

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.Hide()
        self.didSetDown = False

    def Show(self, doShow=True):
        super().Show(doShow)
        if doShow and not self.hasShown:
            self.SetSize((300, self.GetParent().GetSize().Height))
            self.SetPosition(self.GetParent().GetPosition() + (self.GetParent().GetSize().Width, 0))
            self.hasShown = True
        self.path = []
        self.UpdateVars()

    def OnClose(self, event):
        self.keys = None
        self.vars = None
        event.Veto()
        self.Hide()

    def OnResize(self, event):
        (width, height) = self.grid.GetClientSize()
        width = width - self.grid.GetColSize(0) - 1
        if width < 0: width = 0
        self.grid.SetColSize(1, width)
        event.Skip()

    def UpdateVars(self):
        if not self.IsShown() or self.grid.IsCellEditControlShown():
            return

        clientVars = self.stackManager.runner.GetClientVars()
        obj = clientVars
        for p in self.path:
            if isinstance(p, int) and isinstance(obj, (tuple, list)):
                if p >= 0 and p < len(obj):
                    obj = obj[p]
            elif p in obj:
                obj = obj[p]
            else:
                self.path.pop()
                self.UpdateVars()
                return
            if isinstance(obj, uiView.ViewProxy):
                obj = obj._model
            if isinstance(obj, uiView.ViewModel):
                props = obj.properties.copy()
                if obj.type in ("card", "stack", "group"):
                    props["children"] = obj.childModels.copy()
                if obj.type in ("pen", "line", "poly"):
                    props["points"] = obj.points
                if "originalSize" in props:
                    del props["originalSize"]
                obj = props

        self.vars = obj

        dispPath = [f".{p}" if isinstance(p, str) else f"[{p}]" for p in self.path]
        self.pathLabel.SetLabelText("All" + ''.join(dispPath))

        if isinstance(self.vars, (tuple, list)):
            self.keys = range(len(self.vars))
        else:
            self.keys = sorted(self.vars.keys(), key=str.casefold)

        oldNum = self.grid.GetNumberRows()
        newNum = len(self.keys)

        noUpdates = wx.grid.GridUpdateLocker(self.grid)
        if newNum < oldNum:
            self.grid.DeleteRows(0, oldNum-newNum)
        elif newNum > oldNum:
            self.grid.InsertRows(0, newNum - oldNum)

        row = 0
        for k in self.keys:
            val = self.vars[k]
            if isinstance(val, uiView.ViewProxy):
                val = val._model
            val = str(val)

            self.grid.SetCellValue(row, 0, str(k))
            self.grid.SetReadOnly(row, 0)
            self.grid.SetCellValue(row, 1, val)
            self.grid.SetReadOnly(row, 1)
            row += 1
        self.grid.Refresh(True)

    def OnPathClick(self, event):
        if len(self.path):
            self.path.pop()
            self.UpdateVars()

    def OnGridDClick(self, event):
        (r,c) = (event.Row, event.Col)
        k = self.keys[r]
        v = self.vars[k]
        if isinstance(v, (dict, list, tuple, uiView.ViewProxy, uiView.ViewModel)):
            self.path.append(k)
            self.UpdateVars()
