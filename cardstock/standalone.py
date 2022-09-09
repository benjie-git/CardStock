#!/usr/bin/python3

# standalone.py
"""
This is the root of the CardStock exported stack application.
It loads the embedded stack and ResourceMap, and runs the viewer.
"""

import os
import sys
import json
import wx
import wx.html
from viewer import ViewerFrame
from stackModel import StackModel
from wx.lib.mixins.inspection import InspectionMixin

ID_MENU_FIND = wx.NewIdRef()
ID_MENU_FIND_SEL = wx.NewIdRef()
ID_MENU_FIND_NEXT = wx.NewIdRef()
ID_MENU_FIND_PREV = wx.NewIdRef()
ID_MENU_REPLACE = wx.NewIdRef()

# ----------------------------------------------------------------------


class StandaloneApp(wx.App, InspectionMixin):
    def OnInit(self):
        self.Init(self)  # for InspectionMixin
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        self.SetAppDisplayName('CardStock')

        if getattr(sys, 'frozen', False) and hasattr(sys, "_MEIPASS"):
            if wx.Platform != "__WXMAC__":
                bundle_dir = sys._MEIPASS
            else:
                bundle_dir = os.path.join(os.path.dirname(sys.executable), "Resources")
        else:
            bundle_dir = os.path.dirname(os.path.realpath(__file__))
        stackPath = os.path.join(bundle_dir, "stack.cds")

        if not os.path.exists(stackPath):
            if wx.Platform != "__WXMAC__":
                bundle_dir = os.path.join(os.path.dirname(sys.executable), "Resources")
            else:
                bundle_dir = os.path.dirname(sys.executable)
            stackPath = os.path.join(bundle_dir, "stack.cds")

        if not os.path.exists(stackPath):
            return False

        mapPath = os.path.join(bundle_dir, "ResourceMap.json")
        resMap = None
        if os.path.exists(mapPath):
            with open(mapPath, 'r') as f:
                resMap = json.load(f)

        with open(stackPath, 'r') as f:
            data = json.load(f)
        if data:
            stackModel = StackModel(None)
            stackModel.SetData(data)
            self.frame = ViewerFrame(None, True, resMap)
            self.frame.PushStack(stackModel, stackPath, 0)
            self.SetTopWindow(self.frame)
            self.frame.Show(True)

        return True

    def MacReopenApp(self):
        """
        Restore the main frame (if it's minimized) when the Dock icon is
        clicked on OSX.
        """
        top = self.GetTopWindow()
        if top and top.IsIconized():
            top.Iconize(False)
        if top:
            top.Raise()


# ----------------------------------------------------------------------


if __name__ == '__main__':
    if wx.Platform == "__WXMSW__":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(True)
        except:
            pass

    app = StandaloneApp(redirect=False)
    app.MainLoop()
