class Size(object):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            self.width = args[0][0]
            self.height = args[0][1]
        elif len(args) == 1 and isinstance(args[0], Size):
            self.width = args[0].width
            self.height = args[0].height
        elif len(args) == 2 and isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            self.width = args[0]
            self.height = args[1]
        else:
            raise TypeError("Size() requires 2 numbers or a Size")

    def __str__(self):
        return f"({self.width}, {self.height})"

    def __getitem__(self, key):
        if key == 0:
            return self.width
        elif key == 1:
            return self.height
        else:
            raise KeyError("Size has 2 elements")

    def __setitem__(self, key, val):
        if key == 0:
            self.width = val
        elif key == 1:
            self.height = val
        else:
            raise KeyError("Size has 2 elements")

    def __iter__(self):
        return (self.__getitem__(k) for k in (0, 1))


class Point(object):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            self.x = args[0][0]
            self.y = args[0][1]
        elif len(args) == 1 and isinstance(args[0], (Point, RealPoint)):
            self.x = args[0].x
            self.y = args[0].y
        elif len(args) == 2 and isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            self.x = args[0]
            self.y = args[1]
        else:
            raise TypeError("Point() requires 2 numbers or a Point")

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise KeyError("Point has 2 elements")

    def __setitem__(self, key, val):
        if key == 0:
            self.x = val
        elif key == 1:
            self.y = val
        else:
            raise KeyError("Point has 2 elements")

    def __iter__(self):
        return (self.__getitem__(k) for k in (0, 1))


class RealPoint(Point):
    pass


class Rect(object):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.x = x
        self.y = y
        self.width = w
        self.height = h

class Colour(object):
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

class AffineMatrix2D(object):
    def __init__(self, a,b,c,d,e,f):
        super().__init__()
        pass

    def Translate(self, a,b,c):
        pass

    def Rotate(self, a,b,c):
        pass

    def TransformPoint(self, x, y):
        return (x, y)


# CardStock-specific Point, Size, RealPoint subclasses
# These notify their model when their components are changed, so that, for example:
# button.center.x = 100  will notify the button's model that the center changed.


class CDSPoint(Point):
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


class CDSRealPoint(RealPoint):
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


class CDSSize(Size):
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
