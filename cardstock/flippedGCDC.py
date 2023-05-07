# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx

class FlippedGCDC(wx.GCDC):
    """
    Vertically flip the output to the stack view, so the origin is the bottom-left corner.
    """
    def __init__(self, dc, stackManager, **kwargs):
        super().__init__(dc, **kwargs)
        self.stackManager = stackManager

    def DrawRectangle(self, rect):
        super().DrawRectangle(self.stackManager.ConvRect(rect))

    def DrawCircle(self, pt, radius):
        super().DrawCircle(self.stackManager.ConvPoint(pt), self.stackManager.view.FromDIP(radius))

    def DrawEllipse(self, rect):
        super().DrawEllipse(self.stackManager.ConvRect(rect))

    def DrawRoundedRectangle(self, rect, radius):
        super().DrawRoundedRectangle(self.stackManager.ConvRect(rect), self.stackManager.view.FromDIP(radius))

    def DrawLine(self, pointA, pointB):
        super().DrawLine(self.stackManager.ConvPoint(pointA), self.stackManager.ConvPoint(pointB))

    def DrawLines(self, points, xoffset=0, yoffset=0):
        points = [self.stackManager.ConvPoint((p[0]+xoffset, p[1]+yoffset)) for p in points]
        super().DrawLines(points)

    def DrawPolygon(self, points, xoffset=0, yoffset=0, fill_style=wx.ODDEVEN_RULE):
        points = [self.stackManager.ConvPoint((p[0]+xoffset, p[1]+yoffset)) for p in points]
        super().DrawPolygon(points, fill_style=fill_style)

    def DrawBitmap(self, bitmap, x, y, useMask=False):
        pt = self.stackManager.ConvPoint((x, y))
        super().DrawBitmap(bitmap, pt.x, pt.y, useMask)

    def DrawText(self, text, pt):
        pt = self.stackManager.ConvPoint(pt)
        super().DrawText(text, pt)
