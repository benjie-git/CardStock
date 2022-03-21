class Size(object):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            self._width = args[0][0]
            self._height = args[0][1]
        elif len(args) == 1 and isinstance(args[0], Size):
            self._width = args[0]._width
            self._height = args[0]._height
        elif len(args) == 2 and isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            self._width = args[0]
            self._height = args[1]
        else:
            raise TypeError("Size() requires 2 numbers or a Size")

    @property
    def width(self):
        return self._width
    @width.setter
    def width(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("width must be a number")
        self._width = val

    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("height must be a number")
        self._height = val

    def __str__(self):
        return f"({self._width}, {self._height})"

    def __getitem__(self, key):
        if key == 0:
            return self._width
        elif key == 1:
            return self._height
        else:
            raise KeyError("Size has 2 elements")

    def __setitem__(self, key, val):
        if key == 0:
            self.width = val
        elif key == 1:
            self.height = val
        else:
            raise KeyError("Size has 2 elements")

    def __iadd__(self, other):
        if isinstance(other, (tuple, list)):
            self._width += other[0]
            self._height += other[1]
        elif isinstance(other, Size):
            self._width += other._width
            self._height += other._height
        else:
            raise TypeError()
        return self

    def __iter__(self):
        return (self.__getitem__(k) for k in (0, 1))


class Point(object):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            self._x = args[0][0]
            self._y = args[0][1]
        elif len(args) == 1 and isinstance(args[0], (Point, RealPoint)):
            self._x = args[0]._x
            self._y = args[0]._y
        elif len(args) == 2 and isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            self._x = args[0]
            self._y = args[1]
        else:
            raise TypeError("Point() requires 2 numbers or a Point")

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("x must be a number")
        self._x = val

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("y must be a number")
        self._y = val

    def __str__(self):
        return f"({self._x}, {self._y})"

    def __getitem__(self, key):
        if key == 0:
            return self._x
        elif key == 1:
            return self._y
        else:
            raise KeyError("Point has 2 elements")

    def __setitem__(self, key, val):
        if key == 0:
            self._x = val
        elif key == 1:
            self._y = val
        else:
            raise KeyError("Point has 2 elements")

    def __iadd__(self, other):
        if isinstance(other, (tuple, list)):
            self._x += other[0]
            self._y += other[1]
        elif isinstance(other, Point):
            self._x += other._x
            self._y += other._y
        else:
            raise TypeError()
        return self

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
        return self._x
    @x.setter
    def x(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("x must be a number")
        self._x = val
        self.model.FramePartChanged(self)

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("y must be a number")
        self._y = val
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
        return self._x
    @x.setter
    def x(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("x must be a number")
        self._x = val
        self.model.FramePartChanged(self)

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("y must be a number")
        self._y = val
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
        return self._width
    @width.setter
    def width(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("width must be a number")
        self._width = val
        self.model.FramePartChanged(self)

    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("height must be a number")
        self._height = val
        self.model.FramePartChanged(self)


def RunOnMainSync(func):
    def wrapper_run_on_main(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper_run_on_main

def RunOnMainAsync(func):
    def wrapper_run_on_main(*args, **kwargs):
        func(*args, **kwargs)
    return wrapper_run_on_main
