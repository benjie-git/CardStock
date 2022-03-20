import wx_compat as wx

FontMap = {'Default': 'Arial', 'Mono': 'monospace', 'Serif': 'serif', 'Sans-Serif': 'Arial'}


class UiView(object):
    def __init__(self, parent, stackManager, model):
        self.parent = parent
        self.stackManager = stackManager
        self.model = model
        self.fabObjs = []
        self.uiViews = {}

    def LoadChildren(self):
        for m in self.model.childModels:
            ui = self.stackManager.UiViewFromModel(self.model, self.stackManager, m)
            self.uiViews[m] = ui
            ui.LoadChildren()

    def OnPropertyChanged(self, key):
        print(self, key)
        pass


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

    def Load(self, model):
        self.UnLoad()
        self.model = model
        self.stackManager.canvas.setBackgroundColor(self.model.GetProperty("fillColor"))
        self.LoadChildren()
        self.AddChildren()

    def OnPropertyChanged(self, key):
        if key == "fillColor":
            self.stackManager.canvas.setBackgroundColor(self.model.GetProperty("fillColor"))


class UiButton(UiView):
    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model)
        fabric = stackManager.fabric
        rect = stackManager.ConvRect(model.GetFrame())
        hasBorder = model.properties['hasBorder']

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

        group = fabric.Group.new([self.rrBg, self.titleLabel])
        group.hasControls = False
        group.lockMovementX = True
        group.lockMovementY = True
        group.hoverCursor = "pointer"
        self.fabObjs = [group]

    def OnPropertyChanged(self, key):
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
                                           'angle': model.properties['rotation'],
                                           'centeredRotation': True,
                                           'textAlign': model.properties['alignment'],
                                           'fill': model.properties['textColor'],
                                           'fontFamily': FontMap[model.properties['font']],
                                           'fontSize': model.properties['fontSize'] * 1.2})
        self.textbox.selectable = False
        self.textbox.hoverCursor = "arrow"
        self.fabObjs = [self.textbox]

    def OnPropertyChanged(self, key):
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
                                       'strokeWidth': 1})
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
                                           'fontSize': model.properties['fontSize']*1.2})
        self.textbox.hasControls = False
        self.textbox.lockMovementX = True
        self.textbox.lockMovementY = True
        self.textbox.hoverCursor = "text"

        self.fabObjs = [self.textBg, self.textbox]

    def OnPropertyChanged(self, key):
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
                                           'flipY': True
                                           })
        elif model.type in ["line", "pen"]:
            self.shape = fabric.Polyline.new([{"x":p[0], "y":p[1]} for p in self.model.GetScaledPoints()],
                                          {'left': rect.x,
                                           'top': rect.y,
                                           'fill': None,
                                           'stroke': model.properties['penColor'],
                                           'strokeWidth': model.properties['penThickness'],
                                           'flipY': True
                                         })

        self.shape.rotate(model.properties['rotation'])
        self.shape.selectable = False
        self.shape.hoverCursor = "arrow"
        self.fabObjs = [self.shape]

    def OnPropertyChanged(self, key):
        if key == "fillColor":
            self.shape.set({'fill': self.model.GetProperty(key)})
        elif key == "penColor":
            self.shape.set({'stroke': self.model.GetProperty(key)})
        elif key == "penThickness":
            self.shape.set({'strokeWidth': self.model.GetProperty(key)})


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
                                'angle': model.properties['rotation'],
                                'centeredRotation': True,
                                'scaleX': scale, 'scaleY': scale})
                self.image.selectable = False
                self.image.hoverCursor = "arrow"
                self.fabObjs = [self.image]
            self.stackManager.uiCard.pendingLoads -= 1
            self.stackManager.uiCard.AddChildren()

        self.stackManager.uiCard.pendingLoads += 1
        fabric.Image.fromURL(file, imgLoaded)

    def OnPropertyChanged(self, key):
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
                                             'subTargetCheck': True})
        self.group.rotate(self.model.properties['rotation'])
        self.group.selectable = False
        self.group.hoverCursor = "arrow"
        self.fabObjs = [self.group]


class UiWebView(UiView):
    pass
