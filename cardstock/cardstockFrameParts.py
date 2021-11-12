import wx

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
        self += [val-self.x, 0]
        self.model.FramePartChanged(self)

    @property
    def y(self):
        return super().y
    @y.setter
    def y(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("y must be a number")
        self += [0, val-self.y]
        self.model.FramePartChanged(self)


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
        self += [val-self.x, 0]
        self.model.FramePartChanged(self)

    @property
    def y(self):
        return super().y
    @y.setter
    def y(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("y must be a number")
        self += [0, val-self.y]
        self.model.FramePartChanged(self)


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
    def width(self):
        return super().width
    @width.setter
    def width(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("width must be a number")
        self += [val-self.width, 0]
        self.model.FramePartChanged(self)

    @property
    def height(self):
        return super().height
    @height.setter
    def height(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("height must be a number")
        self += [0, val-self.height]
        self.model.FramePartChanged(self)
