# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import wx.grid
import propertyInspector
import uiView


class VariablesWindow(wx.Frame):
    def __init__(self, parent, stackManager):
        super().__init__(parent, title="Variables", style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_TOOL_WINDOW)
        self.SetMinClientSize(wx.Size(self.FromDIP(300),self.FromDIP(100)))
        self.SetClientSize(wx.Size(self.FromDIP(300),self.FromDIP(500)))

        self.stackManager = stackManager
        self.path = []
        self.keys = None
        self.vars = None
        self.hasShown = False

        self.backButton = wx.Button(self, label="Back")
        self.backButton.Bind(wx.EVT_LEFT_DOWN, self.OnBackClick)
        self.pathLabel = wx.StaticText(self)

        self.grid = propertyInspector.PropertyInspector(self, self.stackManager)
        self.grid.valueChangedFunc = self.InspectorValChanged
        self.grid.objClickedFunc = self.InspectorObjClicked
        self.grid.Bind(wx.grid.EVT_GRID_EDITOR_SHOWN, self.OnGridEditorShow)
        self.grid.Bind(wx.grid.EVT_GRID_EDITOR_HIDDEN, self.OnGridEditorHide)
        self.grid.Bind(wx.EVT_KEY_DOWN, self.OnGridKeyDown)

        headSizer = wx.BoxSizer(wx.HORIZONTAL)
        headSizer.Add(self.backButton, 0, wx.EXPAND|wx.ALL, 3)
        headSizer.Add(self.pathLabel, 1, wx.EXPAND|wx.ALL, 3)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(headSizer, 0, wx.EXPAND|wx.ALL, 3)
        sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 3)
        self.SetSizerAndFit(sizer)
        sizer.Layout()

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.Hide()
        self.didSetDown = False

    def Show(self, doShow=True):
        super().Show(doShow)
        self.stackManager.runner.EnableUpdateVars(True)
        if doShow and not self.hasShown:
            self.SetSize((self.FromDIP(300), self.GetParent().GetSize().Height))
            self.SetPosition(self.GetParent().GetPosition() + (self.GetParent().GetSize().Width, 0))
            self.grid.SetGridCursor(0, 1)
            self.hasShown = True
        self.path = []
        self.UpdateVars()

    def OnClose(self, event):
        self.stackManager.runner.EnableUpdateVars(False)
        self.keys = None
        self.vars = None
        event.Veto()
        self.Hide()

    def OnGridEditorShow(self, event):
        self.stackManager.runner.EnableUpdateVars(False)
        event.Skip()

    def OnGridEditorHide(self, event):
        self.stackManager.runner.EnableUpdateVars(True)
        event.Skip()

    def OnBackClick(self, event):
        if not self.grid.IsEnabled() or not self.grid.IsCellEditControlShown():
            self.ZoomOut()
        event.Skip()

    def OnGridKeyDown(self, event):
        if not self.grid.IsCellEditControlShown() and event.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            if self.grid.GetGridCursorCol() == 1:
                key = self.keys[self.grid.GetGridCursorRow()]
                if self.grid.GetTypeForKey(key) in ("obj", "static_list"):
                    self.ZoomInto(key)
                    return
        elif not self.grid.IsCellEditControlShown() and event.GetKeyCode() in (wx.WXK_ESCAPE, wx.WXK_BACK, wx.WXK_DELETE):
            self.ZoomOut()
        event.Skip()

    def InspectorObjClicked(self, row):
        key = self.keys[row]
        self.ZoomInto(key)

    def ZoomInto(self, key):
        if self.grid.GetTypeForKey(key) in ("obj", "list", "static_list", "dict", "set"):
            v = self.vars[key]
            obj = self.ObjFromPath()
            if isinstance(obj, (dict, list, tuple)):
                self.path.append(('sub', key))
                self.grid.SetGridCursor(0, 1)
                self.UpdateVars()
            elif isinstance(obj, (uiView.ViewProxy, uiView.ViewModel)):
                self.path.append(('attr', key))
                self.grid.SetGridCursor(0, 1)
                self.UpdateVars()
            return True
        return False

    def ZoomOut(self):
        if len(self.path):
            self.path.pop()
            self.grid.SetGridCursor(0, 1)
            self.UpdateVars()
            return True
        return False

    def ObjFromPath(self):
        clientVars = self.stackManager.runner.GetClientVars()
        obj = clientVars
        for (t, p) in self.path:
            if isinstance(obj, uiView.ViewProxy):
                obj = obj._model
            if isinstance(obj, (tuple, list)) and isinstance(p, int):
                if 0 <= p < len(obj):
                    obj = obj[p]
                else:
                    return None
            elif isinstance(obj, uiView.ViewModel):
                if p == "children":
                    obj = obj.childModels
                elif p == "points":
                    obj = obj.points
                else:
                    obj = obj.properties[p]
            elif p in obj:
                obj = obj[p]
            else:
                return None
        return obj

    def GetVars(self):
        vars = self.stackManager.runner.GetClientVars()
        obj = None
        for (t, p) in self.path:
            obj = None
            if t == 'sub':
                if isinstance(p, int):
                    if 0 <= p < len(vars):
                        vars = vars[p]
                elif p in vars:
                    vars = vars[p]
                else:
                    self.path.pop()
                    self.grid.SetGridCursor(0,1)
                    return self.GetVars()
            elif t == "attr" and p in vars:
                vars = vars[p]
            else:
                self.path.pop()
                self.grid.SetGridCursor(0, 1)
                return self.GetVars()

            if isinstance(vars, uiView.ViewProxy):
                vars = vars._model
            if isinstance(vars, uiView.ViewModel):
                obj = vars
                props = vars.properties.copy()
                if vars.type == "stack":
                    props["children"] = vars.childModels.copy()
                    del props["position"]
                    del props["size"]
                    del props["speed"]
                    del props["is_visible"]
                elif vars.type == "card":
                    props["children"] = vars.childModels.copy()
                    props["size"] = vars.parent.properties["size"]
                    del props["position"]
                    del props["speed"]
                    del props["is_visible"]
                elif vars.type == "group":
                    props["children"] = vars.childModels.copy()
                elif vars.type in ("pen", "line", "polygon"):
                    props["points"] = vars.points

                if "originalSize" in props:
                    del props["originalSize"]
                vars = props
        return (obj, vars)

    def UpdatePath(self):
        if len(self.path):
            dispPath = str(self.path[0][1])
            if len(self.path)>1:
                dispParts = [f".{p}" if t == "attr" else f"[{p}]" for (t, p) in self.path[1:]]
                dispPath += ''.join(dispParts)
            self.pathLabel.SetLabelText(dispPath)
            self.backButton.Enable()
        else:
            self.pathLabel.SetLabelText("All")
            self.backButton.Disable()

    def UpdateVars(self):
        if not self.IsShown() or self.grid.IsCellEditControlShown():
            return

        (obj, self.vars) = self.GetVars()
        self.UpdatePath()

        if isinstance(self.vars, set):
            self.vars = list(self.vars)

        if isinstance(self.vars, (tuple, list)):
            self.keys = range(len(self.vars))
        else:

            self.keys = sorted(self.vars.keys(), key=lambda x: str.casefold(x) if isinstance(x, str) else x)
        d = {}
        types = {}
        for k in self.keys:
            d[k] = self.vars[k]
            if isinstance(obj, uiView.ViewModel):
                if k == "name":
                    types[k] = "static"
                elif k == "children":
                    types[k] = "static_list"
                else:
                    types[k] = obj.GetPropertyType(k)
            elif isinstance(self.vars, tuple):
                types[k] = "static"

        self.vars = d

        oldNum = self.grid.GetNumberRows()
        newNum = len(self.keys)

        noUpdates = wx.grid.GridUpdateLocker(self.grid)
        if newNum < oldNum:
            self.grid.DeleteRows(0, oldNum-newNum)
        elif newNum > oldNum:
            self.grid.InsertRows(0, newNum - oldNum)

        self.grid.SetData("Variables", self.vars, types)

    def InspectorValChanged(self, key, val):
        clientVars = self.stackManager.runner.GetClientVars()
        obj = clientVars
        changedPoints = None
        for (t, p) in self.path:
            if isinstance(obj, uiView.ViewProxy):
                obj = obj._model
            if isinstance(obj, (tuple, list)) and isinstance(p, int):
                if 0 <= p < len(obj):
                    obj = obj[p]
                else:
                    return
            elif isinstance(obj, uiView.ViewModel):
                if p == "children":
                    obj = obj.childModels
                elif p == "points":
                    changedPoints = obj
                    obj = obj.points
                else:
                    obj = obj.properties[p]
            elif p in obj:
                obj = obj[p]
            else:
                return

        if isinstance(obj, uiView.ViewProxy):
            obj = obj._model
        if obj == clientVars:
            self.stackManager.runner.UpdateClientVar(key, val)
        elif isinstance(obj, (dict, tuple, list)):
            obj[key] = val
        elif isinstance(obj, uiView.ViewModel):
            obj.SetProperty(key, val)

        if changedPoints:
            changedPoints.DidUpdateShape()
