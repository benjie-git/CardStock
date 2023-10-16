# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import sys

# CardStock-specific Point, Size, RealPoint subclasses
# These notify their model when their components are changed, so that, for example:
# button.center.x = 100  will notify the button's model that the center changed.


class CDSPoint(wx.Point):
    def __init__(self, *args, **kwargs):
        model = kwargs.pop("model")
        role = kwargs.pop("role")
        super().__init__(*args, **kwargs)
        self.model = model
        self.role = role

    def __setitem__(self, key, val):
        if not isinstance(val, (int, float)):
            raise TypeError("value must be a number")
        super().__setitem__(key, val)

    @property
    def x(self):
        return super().x
    @x.setter
    def x(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("x must be a number")
        self += [val-self[0], 0]
        self.model.FramePartChanged(self)

    @property
    def y(self):
        return super().y
    @y.setter
    def y(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("y must be a number")
        self += [0, val-self[1]]
        self.model.FramePartChanged(self)

    def __iadd__(self, other):
        super().__iadd__(tuple((int(x) for x in other)))
        return self

    def __add__(self, other):
        return super().__add__(tuple((int(x) for x in other)))

    def __isub__(self, other):
        super().__isub__(tuple((int(x) for x in other)))
        return self

    def __sub__(self, other):
        return super().__sub__(tuple((int(x) for x in other)))


class CDSRealPoint(wx.RealPoint):
    def __init__(self, *args, **kwargs):
        model = kwargs.pop("model")
        role = kwargs.pop("role")
        super().__init__(*args, **kwargs)
        self.model = model
        self.role = role

    def __setitem__(self, key, val):
        if not isinstance(val, (int, float)):
            raise TypeError("value must be a number")
        super().__setitem__(key, val)

    @property
    def x(self):
        return super().x
    @x.setter
    def x(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("x must be a number")
        self += (val-self[0], 0)
        self.model.FramePartChanged(self)

    @property
    def y(self):
        return super().y
    @y.setter
    def y(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("y must be a number")
        self += (0, val-self[1])
        self.model.FramePartChanged(self)

    def __add__(self, other):
        if sys.version_info.major == 3 and sys.version_info.minor >= 10:
            return super().__add__(tuple((int(x) for x in other)))
        else:
            return super().__add__(other)

    def __iadd__(self, other):
        if sys.version_info.major == 3 and sys.version_info.minor >= 10:
            super().__iadd__(tuple((int(x) for x in other)))
        else:
            super().__iadd__(other)
        return self

    def __sub__(self, other):
        if sys.version_info.major == 3 and sys.version_info.minor >= 10:
            return super().__sub__(tuple((int(x) for x in other)))
        else:
            return super().__sub__(other)

    def __isub__(self, other):
        if sys.version_info.major == 3 and sys.version_info.minor >= 10:
            super().__isub__(tuple((int(x) for x in other)))
        else:
            super().__isub__(other)
        return self


class CDSSize(wx.Size):
    def __init__(self, *args, **kwargs):
        model = kwargs.pop("model")
        role = kwargs.pop("role")
        super().__init__(*args, **kwargs)
        self.model = model
        self.role = role

    def __setitem__(self, key, val):
        if not isinstance(val, (int, float)):
            raise TypeError("size must be a number")
        super().__setitem__(key, val)

    @property
    def x(self):
        raise TypeError("size has no property 'x'")
    @x.setter
    def x(self, val):
        raise TypeError("size has no property 'x'")

    @property
    def y(self):
        raise TypeError("size has no property 'y'")
    @y.setter
    def y(self, val):
        raise TypeError("size has no property 'y'")

    @property
    def width(self):
        return super().width
    @width.setter
    def width(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("width must be a number")
        self += [val-self[0], 0]
        self.model.FramePartChanged(self)

    @property
    def height(self):
        return super().height
    @height.setter
    def height(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("height must be a number")
        self += [0, val-self[1]]
        self.model.FramePartChanged(self)

    def __iadd__(self, other):
        super().__iadd__(tuple((int(x) for x in other)))
        return self

    def __add__(self, other):
        return super().__add__(tuple((int(x) for x in other)))
