# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

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

ID_MENU_FIND = wx.NewIdRef()
ID_MENU_FIND_SEL = wx.NewIdRef()
ID_MENU_FIND_NEXT = wx.NewIdRef()
ID_MENU_FIND_PREV = wx.NewIdRef()
ID_MENU_REPLACE = wx.NewIdRef()

# ----------------------------------------------------------------------


class StandaloneApp(wx.App):
    def OnInit(self):
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        self.SetAppDisplayName('CardStock')

        if getattr(sys, 'frozen', False) and hasattr(sys, "_MEIPASS"):
            if wx.Platform != "__WXMAC__":
                bundle_dir = sys._MEIPASS
            else:
                dirPath = os.path.dirname(sys.executable)
                bundle_dir = os.path.join(dirPath, "Resources")
                if not os.path.exists(os.path.join(bundle_dir, "stack.cds")):
                    dirPath = os.path.dirname(os.path.dirname(sys.executable))
                    bundle_dir = os.path.join(dirPath, "Resources")
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
