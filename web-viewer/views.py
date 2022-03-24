from browser import document
import wx_compat as wx
from time import time

FontMap = {'Default': 'Arial', 'Mono': 'monospace', 'Serif': 'serif', 'Sans-Serif': 'Arial'}


class UiView(object):
    def __init__(self, parent, stackManager, model):
        self.parent = parent
        self.stackManager = stackManager
        self.model = model
        self.fabObjs = []
        self.uiViews = {}

    def SetDown(self):
        for ui in self.uiViews:
            ui.SetDown()
        self.stackManager = None
        self.parent = None
        self.uiViews = None
        self.model = None
        self.hitRegion = None

    _NextId = 1
    @classmethod
    def NextId(cls):
        id = cls._NextId
        cls._NextId += 1
        return id

    def UnloadFabObjs(self):
        for o in self.fabObjs:
            self.stackManager.canvas.remove(o)
        self.fabObjs = []
        for ui in self.uiViews.values():
            ui.UnloadFabObjs()

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

    def OnPeriodic(self):
        self.stackManager.runner.RunHandler(self.model, "OnPeriodic", None)
        for ui in self.uiViews.values():
            ui.OnPeriodic()

    def OnPropertyChanged(self, key):
        if key in ("position", "center"):
            rect = self.stackManager.ConvRect(self.model.GetFrame())
            for fab in self.fabObjs:
                fab.set({'left': rect.Left, 'top': rect.Top})
                fab.setCoords()
        elif key == "size":
            s = self.model.GetProperty("size")
            for fab in self.fabObjs:
                fab.set({'width': s.width, 'height': s.height})
                fab.setCoords()
        elif key == "rotation":
            rot = self.model.GetProperty("rotation")
            for fab in self.fabObjs:
                fab.rotate(rot)
                fab.setCoords()
        elif key == "isVisible":
            visible = self.model.GetProperty("isVisible")
            for fab in self.fabObjs:
                fab.set({'visible': visible})

    def RunAnimations(self, onFinishedCalls, elapsedTime):
        # Move the object by speed.x and speed.y pixels per second
        updateList = []
        finishList = []
        didRun = False
        if self.model.type not in ["stack", "card"]:
            speed = self.model.properties["speed"]
            if speed != (0,0) and "position" not in self.model.animations:
                pos = self.model.properties["position"]
                self.model.SetProperty("position", [pos.x + speed.x*elapsedTime, pos.y + speed.y*elapsedTime])
                didRun = True

        # Run any in-progress animations
        now = time()
        for (key, animList) in self.model.animations.items():
            animDict = animList[0]
            if "startTime" in animDict:
                progress = (now - animDict["startTime"]) / animDict["duration"]
                if progress < 1.0:
                    if animDict["onUpdate"]:
                        updateList.append([animDict, progress])
                else:
                    if animDict["onUpdate"]:
                        updateList.append([animDict, 1.0])
                    finishList.append(key)
        for (d,p) in updateList:
            d["onUpdate"](p, d)
            didRun = True
        for key in finishList:
            def deferFinish(key):
                def f(): self.model.FinishAnimation(key)
                return f
            onFinishedCalls.append(deferFinish(key))
        return didRun


class UiCard(UiView):
    def __init__(self, parent, stackManager, model):
        self.pendingLoads = 0
        super().__init__(parent, stackManager, model)
        self.stackManager.canvas.on('mouse:down', self.OnFabricMouseDown)
        self.stackManager.canvas.on('mouse:move', self.OnFabricMouseMove)
        self.stackManager.canvas.on('mouse:up', self.OnFabricMouseUp)
        document.onkeydown = self.OnKeyDown
        document.onkeyup = self.OnKeyUp
        self.lastMouseOverObj = None
        self.fabObjs = [stackManager.canvas]

    def SetDown(self):
        self.stackManager.canvas.off('mouse:down', self.OnFabricMouseDown)
        self.stackManager.canvas.off('mouse:move', self.OnFabricMouseMove)
        self.stackManager.canvas.off('mouse:up', self.OnFabricMouseUp)
        document.onkeydown = None
        document.onkeyup = None

    def Load(self, model):
        self.UnLoad()
        self.model = model
        self.stackManager.canvas.setBackgroundColor(self.model.GetProperty("fillColor"))
        self.LoadChildren()
        self.AddChildren()
        self.stackManager.runner.RunHandler(self.model, "OnShowCard", None)

    def UnLoad(self):
        if self.model:
            self.stackManager.runner.RunHandler(self.model, "OnHideCard", None)
            self.UnloadFabObjs()
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

    def GetAllUiViews(self):
        allUiViews = []
        for uiView in self.uiViews.values():
            allUiViews.append(uiView)
            if uiView.model.type == "group":
                uiView.GetAllUiViews(allUiViews)
        return allUiViews

    def OnFabricMouseDown(self, options):
        target_ui = None
        if options.target:
            target_ui = self.FindTargetUi(options.target)
        self.stackManager.runner.ResetStopHandlingMouseEvent()
        if target_ui:
            target_ui.OnMouseDown(options.e)
            if self.stackManager.runner.DidStopHandlingMouseEvent():
                return
        self.OnMouseDown(options.e)

    def OnFabricMouseMove(self, options):
        self.stackManager.runner.lastMousePos = self.stackManager.ConvPoint(wx.Point(options.e.pageX, options.e.pageY))
        target_ui = None
        if options.target:
            target_ui = self.FindTargetUi(options.target)

        if target_ui != self.lastMouseOverObj:
            if self.lastMouseOverObj:
                self.stackManager.runner.RunHandler(self.lastMouseOverObj.model, "OnMouseExit", options.e)
            self.lastMouseOverObj = target_ui
            if self.lastMouseOverObj:
                self.stackManager.runner.RunHandler(self.lastMouseOverObj.model, "OnMouseEnter", options.e)

        self.stackManager.runner.ResetStopHandlingMouseEvent()
        if target_ui:
            target_ui.OnMouseMove(options.e)
            if self.stackManager.runner.DidStopHandlingMouseEvent():
                return
        self.OnMouseMove(options.e)

    def OnFabricMouseUp(self, options):
        target_ui = None
        if options.target:
            target_ui = self.FindTargetUi(options.target)
        self.stackManager.runner.ResetStopHandlingMouseEvent()
        if target_ui:
            target_ui.OnMouseUp(options.e)
            if self.stackManager.runner.DidStopHandlingMouseEvent():
                return
        self.OnMouseUp(options.e)

    def OnKeyDown(self, e):
        if e.key == "Tab":
            e.preventDefault()
        if not e.repeat:
            self.stackManager.runner.OnKeyDown(e)
            self.stackManager.runner.RunHandler(self.model, "OnKeyDown", e)

    def OnKeyHold(self):
        for keyName in self.stackManager.runner.pressedKeys:
            self.stackManager.runner.RunHandler(self.model, "OnKeyHold", None, keyName)

    def OnKeyUp(self, e):
        self.stackManager.runner.OnKeyUp(e)
        self.stackManager.runner.RunHandler(self.model, "OnKeyUp", e)

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
            self.rrBg = fabric.Rect.new({'left': rect.Left,
                                         'top': rect.Top,
                                         'width': model.properties['size'].width,
                                         'height': model.properties['size'].height,
                                         'rx': 6, 'ry': 6,
                                         'fill': 'white',
                                         'stroke': 'grey',
                                         'strokeWidth':1})
        else:
            self.rrBg = fabric.Rect.new({'left': rect.Left,
                                         'top': rect.Top,
                                         'width': model.properties['size'].width,
                                         'height': model.properties['size'].height,
                                         'fill': None,
                                         'strokeWidth':0})

        self.titleLabel = fabric.Textbox.new(model.properties['title'],
                                             {'left': rect.Left,
                                              'top': rect.Top + (rect.Height-18)/2,
                                              'width': rect.Width,
                                              'height': rect.Height,
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
        elif key == "hasBorder":
            hasBorder = self.model.properties['hasBorder']
            if hasBorder:
                self.rrBg.set({'rx': 6, 'ry': 6, 'fill': 'white', 'stroke': 'grey', 'strokeWidth': 1})
            else:
                self.rrBg.set({'rx': 0, 'ry': 0, 'fill': None, 'stroke': None, 'strokeWidth': 0})
            self.rrBg.setCoords()


class UiTextLabel(UiView):
    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model)
        fabric = stackManager.fabric
        rect = stackManager.ConvRect(model.GetFrame())
        self.textbox = fabric.Textbox.new(model.properties['text'],
                                          {'left': rect.Left,
                                           'top': rect.Top,
                                           'width': rect.Width,
                                           'height': rect.Height,
                                           'textAlign': model.properties['alignment'].lower(),
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
        elif key == "textColor":
            self.textbox.set({'fill': self.model.GetProperty(key)})
        elif key == "alignment":
            self.textbox.set({'textAlign': self.model.properties['alignment'].lower()})
        elif key == "font":
            self.textbox.set({'fontFamily': FontMap[self.model.properties['font']]})
        elif key == "fontSize":
            self.textbox.set({'fontSize': self.model.properties['fontSize'] * 1.2})


class UiTextField(UiView):
    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model)
        fabric = stackManager.fabric
        rect = stackManager.ConvRect(model.GetFrame())

        self.textBg = fabric.Rect.new({'left': rect.Left,
                                       'top': rect.Top,
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
                                          {'left': rect.Left+2,
                                           'top': rect.Top+2,
                                           'width': rect.Width-2,
                                           'height': rect.Height-2,
                                           'textAlign': model.properties['alignment'].lower(),
                                           'fill': model.properties['textColor'],
                                           'fontFamily': FontMap[model.properties['font']],
                                           'fontSize': model.properties['fontSize']*1.2,
                                           'editable': model.properties['isEditable'],
                                           'id': UiView.NextId()})
        self.textbox.hasControls = False
        self.textbox.lockMovementX = True
        self.textbox.lockMovementY = True
        self.textbox.hoverCursor = "text"

        self.textbox.on('selected', self.OnSelected)
        self.textbox.on('selection:cleared', self.OnDeselected)
        self.stackManager.canvas.on('text:changed', self.OnTextChanged)
        self.oldOnKeyDown = self.textbox.onKeyDown
        self.textbox.onKeyDown = self.OnKeyDown

        self.fabObjs = [self.textBg, self.textbox]

    def OnKeyDown(self, e):
        self.oldOnKeyDown(e)
        if "Arrow" in e.key:
            self.stackManager.uiCard.OnKeyDown(e)
        if e.key in ("Enter", "Return"):
            self.OnEnter()
            if not self.model.GetProperty("isMultiline"):
                e.preventDefault()

    def OnEnter(self):
        self.model.stackManager.runner.RunHandler(self.model, "OnTextEnter", None)

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

    def OnTextChanged(self, options):
        if options.target.id == self.textbox.id:
            self.model.SetProperty('text', self.textbox.text)
            self.stackManager.runner.RunHandler(self.model, "OnTextChanged", None)

    def OnPropertyChanged(self, key):
        super().OnPropertyChanged(key)
        if key == "text":
            self.textbox.set({'text': self.model.GetProperty(key)})
        elif key == "textColor":
            self.textbox.set({'fill': self.model.GetProperty(key)})
        elif key == "alignment":
            self.textbox.set({'textAlign': self.model.properties['alignment'].lower()})
        elif key == "font":
            self.textbox.set({'fontFamily': FontMap[self.model.properties['font']]})
        elif key == "fontSize":
            self.textbox.set({'fontSize': self.model.properties['fontSize'] * 1.2})
        elif key == "isEditable":
            self.textbox.set({'editable': self.model.properties['isEditable']})
        elif key == "selectAll":
            self.textbox.selectAll()


class UiShape(UiView):
    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model)
        self.shape = self.CreateShape()
        self.fabObjs = [self.shape]

    def CreateShape(self):
        model = self.model
        fabric = self.stackManager.fabric
        rect = self.stackManager.ConvRect(model.GetFrame())
        shape = None
        if model.type == "oval":
            shape = fabric.Ellipse.new({'left': rect.Left,
                                             'top': rect.Top,
                                             'rx': model.properties['size'].width/2,
                                             'ry': model.properties['size'].height/2,
                                             'fill': model.properties['fillColor'],
                                             'stroke': model.properties['penColor'],
                                             'strokeWidth': model.properties['penThickness']
                                            })
        elif model.type == "rect":
            shape = fabric.Rect.new({'left': rect.Left,
                                          'top': rect.Top,
                                          'width': model.properties['size'].width,
                                          'height': model.properties['size'].height,
                                          'fill': model.properties['fillColor'],
                                          'stroke': model.properties['penColor'],
                                          'strokeWidth': model.properties['penThickness']
                                         })
        elif model.type == "roundrect":
            shape = fabric.Rect.new({'left': rect.Left,
                                          'top': rect.Top,
                                          'width': model.properties['size'].width,
                                          'height': model.properties['size'].height,
                                          'rx': model.properties['cornerRadius'],
                                          'ry': model.properties['cornerRadius'],
                                          'fill': model.properties['fillColor'],
                                          'stroke': model.properties['penColor'],
                                          'strokeWidth': model.properties['penThickness']
                                         })
        elif model.type == "polygon":
            shape = fabric.Polygon.new([{"x":p[0], "y":p[1]} for p in self.model.GetScaledPoints()],
                                          {'left': rect.Left,
                                           'top': rect.Top,
                                           'fill': model.properties['fillColor'],
                                           'stroke': model.properties['penColor'],
                                           'strokeWidth': model.properties['penThickness'],
                                           'strokeLineJoin': 'round',
                                           'flipY': True
                                           })
        elif model.type in ["line", "pen"]:
            shape = fabric.Polyline.new([{"x":p[0], "y":p[1]} for p in self.model.GetScaledPoints()],
                                          {'left': rect.Left,
                                           'top': rect.Top,
                                           'fill': None,
                                           'stroke': model.properties['penColor'],
                                           'strokeWidth': model.properties['penThickness'],
                                           'strokeLineCap': 'round',
                                           'strokeLineJoin': 'round',
                                           'flipY': True
                                         })

        shape.rotate(model.properties['rotation'])
        shape.set({'id': UiView.NextId()})
        shape.selectable = False
        shape.hoverCursor = "arrow"
        return shape

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
        elif key == "shape":
            self.stackManager.canvas.remove(self.shape)
            self.shape = self.CreateShape()
            self.fabObjs = [self.shape]
            self.stackManager.canvas.add(self.shape)


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
                scale = min(rect.Width/imgSize['width'], rect.Height/imgSize['height'])
                self.image.set({'left': rect.Left, 'top': rect.Top,
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

        self.group = fabric.Group.new(objs, {'left': rect.Left, 'top': rect.Top,
                                             'subTargetCheck': True,
                                             'id': UiView.NextId()})
        self.group.rotate(self.model.properties['rotation'])
        self.group.selectable = False
        self.group.hoverCursor = "arrow"
        self.fabObjs = [self.group]

    def GetAllUiViews(self, allUiViews):
        for uiView in self.uiViews.values():
            allUiViews.append(uiView)
            if uiView.model.type == "group":
                uiView.GetAllUiViews(allUiViews)


class UiWebView(UiView):
    pass
