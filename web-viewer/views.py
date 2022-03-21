from browser import document
import wx_compat as wx

FontMap = {'Default': 'Arial', 'Mono': 'monospace', 'Serif': 'serif', 'Sans-Serif': 'Arial'}


class UiView(object):
    def __init__(self, parent, stackManager, model):
        self.parent = parent
        self.stackManager = stackManager
        self.model = model
        self.fabObjs = []
        self.uiViews = {}

    _NextId = 1
    @classmethod
    def NextId(cls):
        id = cls._NextId
        cls._NextId += 1
        return id

    def LoadChildren(self):
        for m in self.model.childModels:
            ui = self.stackManager.UiViewFromModel(self.model, self.stackManager, m)
            self.uiViews[m] = ui
            ui.LoadChildren()

    def OnMouseDown(self, e):
        self.stackManager.runner.RunHandler(self.model, "OnMouseDown", e)

    def OnMouseMove(self, e):
        self.stackManager.runner.RunHandler(self.model, "OnMouseMove", e)

    def OnMouseUp(self, e):
        self.stackManager.runner.RunHandler(self.model, "OnMouseUp", e)

    def OnPropertyChanged(self, key):
        if key in ("position", "center"):
            rect = self.stackManager.ConvRect(self.model.GetFrame())
            for fab in self.fabObjs:
                fab.set({'left': rect.x, 'top': rect.y})
                fab.setCoords()
        elif key == "size":
            s = self.model.GetProperty("size")
            for fab in self.fabObjs:
                fab.set({'width': s.width, 'height': s.height})
                fab.setCoords()


class UiCard(UiView):
    def __init__(self, parent, stackManager, model):
        self.pendingLoads = 0
        super().__init__(parent, stackManager, model)

    def UnLoad(self):
        if self.model:
            for model, ui in self.uiViews.items():
                for o in ui.fabObjs:
                    self.stackManager.canvas.remove(o)
            self.uiViews = {}

    def AddChildren(self):
        if self.pendingLoads == 0:
            for model, ui in self.uiViews.items():
                for o in ui.fabObjs:
                    self.stackManager.canvas.add(o)
            self.stackManager.canvas.requestRenderAll()

    def FindTargetUi(self, fabObj):
        for ui in self.uiViews.values():
            for f in ui.fabObjs:
                if f.id == fabObj.id:
                    return ui
        return None

    def OnFabricMouseDown(self, options):
        target_ui = None
        if options.target:
            target_ui = self.FindTargetUi(options.target)
        if not target_ui:
            target_ui = self
        target_ui.OnMouseDown(options.e)

    def OnFabricMouseMove(self, options):
        target_ui = None
        if options.target:
            target_ui = self.FindTargetUi(options.target)
        if not target_ui:
            target_ui = self
        target_ui.OnMouseMove(options.e)

    def OnFabricMouseUp(self, options):
        target_ui = None
        if options.target:
            target_ui = self.FindTargetUi(options.target)
        if not target_ui:
            target_ui = self
        target_ui.OnMouseUp(options.e)

    def OnKeyDown(self, e):
        if not e.repeat:
            self.stackManager.runner.RunHandler(self.model, "OnKeyDown", e)

    def OnKeyUp(self, e):
        self.stackManager.runner.RunHandler(self.model, "OnKeyUp", e)

    def Load(self, model):
        self.UnLoad()
        self.model = model
        self.stackManager.canvas.setBackgroundColor(self.model.GetProperty("fillColor"))
        self.LoadChildren()
        self.AddChildren()

        self.stackManager.canvas.on('mouse:down', self.OnFabricMouseDown)
        self.stackManager.canvas.on('mouse:move', self.OnFabricMouseMove)
        self.stackManager.canvas.on('mouse:up', self.OnFabricMouseUp)
        document.onkeydown = self.OnKeyDown
        document.onkeyup = self.OnKeyUp

    def OnPropertyChanged(self, key):
        super().OnPropertyChanged(key)
        if key == "fillColor":
            self.stackManager.canvas.setBackgroundColor(self.model.GetProperty("fillColor"))


class UiButton(UiView):
    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model)
        fabric = stackManager.fabric
        rect = stackManager.ConvRect(model.GetFrame())
        hasBorder = model.properties['hasBorder']
        self.isHilighted = False
        self.isMouseDown = False

        if hasBorder:
            self.rrBg = fabric.Rect.new({'left': rect.x,
                                         'top': rect.y,
                                         'width': model.properties['size'].width,
                                         'height': model.properties['size'].height,
                                         'rx': 6, 'ry': 6,
                                         'fill': 'white',
                                         'stroke': 'grey',
                                         'strokeWidth':1})
        else:
            self.rrBg = fabric.Rect.new({'left': rect.x,
                                         'top': rect.y,
                                         'width': model.properties['size'].width,
                                         'height': model.properties['size'].height,
                                         'fill': None,
                                         'strokeWidth':0})

        self.titleLabel = fabric.Textbox.new(model.properties['title'],
                                             {'left': rect.x,
                                              'top': rect.y + (rect.height-18)/2,
                                              'width': rect.width,
                                              'height': rect.height,
                                              'textAlign': 'center',
                                              'fill': "black",
                                              'fontFamily': 'Arial',
                                              'fontSize': 14})

        self.group = fabric.Group.new([self.rrBg, self.titleLabel], {'id': UiView.NextId()})
        self.group.hasControls = False
        self.group.lockMovementX = True
        self.group.lockMovementY = True
        self.group.hoverCursor = "pointer"
        self.fabObjs = [self.group]

    def Highlight(self, on):
        if on:
            self.rrBg.set({'fill': "blue"})
            self.titleLabel.set({'fill': "white"})
        else:
            self.rrBg.set({'fill': "white" if self.model.properties['hasBorder'] else None})
            self.titleLabel.set({'fill': "black"})
        self.isHilighted = on
        self.stackManager.canvas.requestRenderAll()

    def OnMouseDown(self, e):
        super().OnMouseDown(e)
        self.isMouseDown = True
        self.Highlight(True)

    def OnMouseMove(self, e):
        if self.isMouseDown:
            contains = self.group.containsPoint({'x':e.pageX, 'y':e.pageY})
            if not self.isHilighted and contains:
                self.Highlight(True)
            elif self.isHilighted and not contains:
                self.Highlight(False)

    def OnMouseUp(self, e):
        self.isMouseDown = False
        if self.isHilighted:
            self.Highlight(False)
            self.stackManager.runner.RunHandler(self.model, "OnClick", e)
        super().OnMouseUp(e)

    def OnPropertyChanged(self, key):
        super().OnPropertyChanged(key)
        if key == "title":
            self.titleLabel.set({'text':self.model.GetProperty("title")})


class UiTextLabel(UiView):
    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model)
        fabric = stackManager.fabric
        rect = stackManager.ConvRect(model.GetFrame())
        self.textbox = fabric.Textbox.new(model.properties['text'],
                                          {'left': rect.x,
                                           'top': rect.y,
                                           'width': rect.width,
                                           'height': rect.height,
                                           'textAlign': model.properties['alignment'],
                                           'fill': model.properties['textColor'],
                                           'fontFamily': FontMap[model.properties['font']],
                                           'fontSize': model.properties['fontSize'] * 1.2,
                                           'id': UiView.NextId()})
        self.textbox.rotate(model.properties['rotation'])
        self.textbox.selectable = False
        self.textbox.hoverCursor = "arrow"
        self.fabObjs = [self.textbox]

    def OnPropertyChanged(self, key):
        super().OnPropertyChanged(key)
        if key == "text":
            self.textbox.set({'text': self.model.GetProperty(key)})


class UiTextField(UiView):
    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model)
        fabric = stackManager.fabric
        rect = stackManager.ConvRect(model.GetFrame())

        self.textBg = fabric.Rect.new({'left': rect.x,
                                       'top': rect.y,
                                       'width': model.properties['size'].width,
                                       'height': model.properties['size'].height,
                                       'rx': 2, 'ry': 2,
                                       'fill': 'white',
                                       'stroke': 'grey',
                                       'strokeWidth': 1,
                                       'id': UiView.NextId()})
        self.textBg.selectable = False
        self.textBg.hoverCursor = "arrow"

        self.textbox = fabric.Textbox.new(model.properties['text'],
                                          {'left': rect.x,
                                           'top': rect.y,
                                           'width': rect.width,
                                           'height': rect.height,
                                           'textAlign': model.properties['alignment'],
                                           'fill': model.properties['textColor'],
                                           'fontFamily': FontMap[model.properties['font']],
                                           'fontSize': model.properties['fontSize']*1.2,
                                           'id': UiView.NextId()})
        self.textbox.hasControls = False
        self.textbox.lockMovementX = True
        self.textbox.lockMovementY = True
        self.textbox.hoverCursor = "text"

        self.textbox.on('selected', self.OnSelected)
        self.textbox.on('selection:cleared', self.OnDeselected)

        self.fabObjs = [self.textBg, self.textbox]

    def OnMouseDown(self, e):
        super().OnMouseDown(e)
        self.stackManager.canvas.setActiveObject(self.textbox)

    def OnSelected(self, options):
        self.textbox.enterEditing()
        end = len(self.textbox.text)
        self.textbox.setSelectionStart(end)
        self.textbox.setSelectionEnd(end)

    def OnDeselected(self, options):
        self.textbox.exitEditing()

    def OnPropertyChanged(self, key):
        super().OnPropertyChanged(key)
        if key == "text":
            self.textbox.set({'text': self.model.GetProperty(key)})


class UiShape(UiView):
    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model)
        fabric = stackManager.fabric
        rect = stackManager.ConvRect(model.GetFrame())
        if model.type == "oval":
            self.shape = fabric.Ellipse.new({'left': rect.x,
                                             'top': rect.y,
                                             'rx': model.properties['size'].width/2,
                                             'ry': model.properties['size'].height/2,
                                             'fill': model.properties['fillColor'],
                                             'stroke': model.properties['penColor'],
                                             'strokeWidth': model.properties['penThickness']
                                            })
        elif model.type == "rect":
            self.shape = fabric.Rect.new({'left': rect.x,
                                          'top': rect.y,
                                          'width': model.properties['size'].width,
                                          'height': model.properties['size'].height,
                                          'fill': model.properties['fillColor'],
                                          'stroke': model.properties['penColor'],
                                          'strokeWidth': model.properties['penThickness']
                                         })
        elif model.type == "roundrect":
            self.shape = fabric.Rect.new({'left': rect.x,
                                          'top': rect.y,
                                          'width': model.properties['size'].width,
                                          'height': model.properties['size'].height,
                                          'rx': model.properties['cornerRadius'],
                                          'ry': model.properties['cornerRadius'],
                                          'fill': model.properties['fillColor'],
                                          'stroke': model.properties['penColor'],
                                          'strokeWidth': model.properties['penThickness']
                                         })
        elif model.type == "polygon":
            self.shape = fabric.Polygon.new([{"x":p[0], "y":p[1]} for p in self.model.GetScaledPoints()],
                                          {'left': rect.x,
                                           'top': rect.y,
                                           'fill': model.properties['fillColor'],
                                           'stroke': model.properties['penColor'],
                                           'strokeWidth': model.properties['penThickness'],
                                           'strokeLineJoin': 'round',
                                           'flipY': True
                                           })
        elif model.type in ["line", "pen"]:
            self.shape = fabric.Polyline.new([{"x":p[0], "y":p[1]} for p in self.model.GetScaledPoints()],
                                          {'left': rect.x,
                                           'top': rect.y,
                                           'fill': None,
                                           'stroke': model.properties['penColor'],
                                           'strokeWidth': model.properties['penThickness'],
                                           'strokeLineCap': 'round',
                                           'strokeLineJoin': 'round',
                                           'flipY': True
                                         })

        self.shape.rotate(model.properties['rotation'])
        self.shape.set({'id': UiView.NextId()})
        self.shape.selectable = False
        self.shape.hoverCursor = "arrow"
        self.fabObjs = [self.shape]

    def OnPropertyChanged(self, key):
        super().OnPropertyChanged(key)
        if key == "fillColor":
            self.shape.set({'fill': self.model.GetProperty(key)})
        elif key == "penColor":
            self.shape.set({'stroke': self.model.GetProperty(key)})
        elif key == "penThickness":
            self.shape.set({'strokeWidth': self.model.GetProperty(key)})
        elif self.model.type == "oval" and key == "size":
            s = self.model.GetProperty("size")
            self.shape.set({'rx': s.width/2, 'ry': s.height/2})
            self.shape.setCoords()


class UiImage(UiView):
    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model)
        fabric = stackManager.fabric
        rect = stackManager.ConvRect(model.GetFrame())
        self.image = None
        file = "Resources/" + model.properties['file']

        def imgLoaded(img, err):
            if not err:
                self.image = img
                imgSize = img.getOriginalSize()
                scale = min(rect.width/imgSize['width'], rect.height/imgSize['height'])
                self.image.set({'left': rect.x, 'top': rect.y,
                                'scaleX': scale, 'scaleY': scale})
                self.image.rotate(model.properties['rotation'])
                self.image.set({'id': UiView.NextId()})
                self.image.selectable = False
                self.image.hoverCursor = "arrow"
                self.fabObjs = [self.image]
            self.stackManager.uiCard.pendingLoads -= 1
            self.stackManager.uiCard.AddChildren()

        self.stackManager.uiCard.pendingLoads += 1
        fabric.Image.fromURL(file, imgLoaded)

    def OnPropertyChanged(self, key):
        super().OnPropertyChanged(key)
        if key == "file":
            self.image.setSrc(self.model.GetProperty(key))


class UiGroup(UiView):
    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model)

    def LoadChildren(self):
        super().LoadChildren()

        fabric = self.stackManager.fabric
        rect = self.stackManager.ConvRect(self.model.GetFrame())
        objs = []

        for model,ui in self.uiViews.items():
            objs.extend(ui.fabObjs)

        self.group = fabric.Group.new(objs, {'left': rect.x, 'top': rect.y,
                                             'subTargetCheck': True,
                                             'id': UiView.NextId()})
        self.group.rotate(self.model.properties['rotation'])
        self.group.selectable = False
        self.group.hoverCursor = "arrow"
        self.fabObjs = [self.group]


class UiWebView(UiView):
    pass
