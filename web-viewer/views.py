from browser import document
import wx_compat as wx
from time import time
import math

FontMap = {'Default': 'Arial', 'Mono': 'monospace', 'Serif': 'serif', 'Sans-Serif': 'Arial'}


class UiView(object):
    def __init__(self, parent, stackManager, model):
        super().__init__()
        self.parent = parent
        self.stackManager = stackManager
        self.model = model
        self.fabObjs = []
        self.offsets = {}
        self.uiViews = {}
        self.CreateFabObjs()

    def CreateFabObjs(self):
        self.OnPropertyChanged('isVisible')

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
            ui = self.stackManager.UiViewFromModel(self, self.stackManager, m)
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
        for ui in self.uiViews.copy().values():
            ui.OnPeriodic()

    def OnPropertyChanged(self, key):
        if key == "size":
            s = self.model.GetProperty("size")
            for fab in self.fabObjs:
                fab.set({'width': s.width, 'height': s.height})
                fab.setCoords()
        if key in ("position", "center", "size"):
            for fab in self.fabObjs:
                self.SetFabObjCoords(fab)
        elif key == "rotation":
            rot = self.model.GetAbsoluteRotation()
            for fab in self.fabObjs:
                fab.rotate(rot)
                self.SetFabObjCoords(fab)
        elif key == "isVisible":
            visible = self.model.GetProperty("isVisible")
            for fab in self.fabObjs:
                fab.set({'visible': visible})

    def SetFabObjCoords(self, fab):
        rect = self.model.GetFrame()
        rot = self.model.GetAbsoluteRotation()

        pos = rect.BottomLeft
        if fab in self.offsets:
            pos += self.offsets[fab]

        if self.model.type in ["oval", "rect", "roundrect", "polygon", "line", "pen"]:
            thick = self.model.GetProperty('penThickness')
            pos = wx.Point(pos[0] - thick / 2, pos[1] + thick / 2)
        if rot and self.model.type in ["image", "line"]:
            s = (fab.width, -fab.height)
            aff = wx.AffineMatrix2D()
            aff.Rotate(math.radians(-rot))
            offset = aff.TransformPoint(s[0] / 2, s[1] / 2)
            pos += (s[0] / 2 - offset[0], s[1] / 2 - offset[1])
        if self.model.type in ["line", "pen"]:
            if rect.Height == 2: pos[1] -= 2

        aff = self.model.parent.GetAffineTransform()
        pos = aff.TransformPoint(*pos)
        pos = self.stackManager.ConvPoint(pos)
        fab.rotate(rot)
        fab.set({'left': pos[0], 'top': pos[1]})
        fab.setCoords()

    def RunAnimations(self, onFinishedCalls, elapsedTime):
        # Move the object by speed.x and speed.y pixels per second
        updateList = []
        finishList = []
        didRun = False
        if self.model.type not in ["stack", "card"]:
            speed = self.model.properties["speed"]
            if (speed.x != 0 or speed.y != 0) and "position" not in self.model.animations:
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

    def FindCollisions(self, collisions):
        # Find collisions between this object and others in its bounceObjs list
        # and add them to the collisions list, to be handled after all are found.
        removeFromBounceObjs = []
        if not self.model.didSetDown and self.model.GetProperty("isVisible") and tuple(self.model.GetProperty("speed")) != (0, 0):
            for k,v in self.model.bounceObjs.items():
                other_ui = self.stackManager.GetUiViewByModel(k)
                (mode, last_dist) = v

                if not other_ui.model.GetProperty("isVisible"):
                    continue

                if other_ui.model.didSetDown:
                    # remove deleted objects from the bounceObjs list, after this loop is done
                    removeFromBounceObjs.append(k)
                    continue

                sc = self.model.GetProxy().center       # sc = self center
                oc = other_ui.model.GetProxy().center   # oc = other center
                new_dist = (abs(sc[0]-oc[0]), abs(sc[1]-oc[1]))

                if not mode:
                    # Determine whether we're inside or outside of this object
                    self.model.bounceObjs[k][0] = "In" if other_ui.model.GetProxy().IsTouchingPoint(self.model.GetCenter()) else "Out"
                    self.model.bounceObjs[k][1] = new_dist
                    continue

                edges = self.model.GetProxy().IsTouchingEdge(other_ui.model.GetProxy(), mode == "In")
                if mode == "In" and not edges:
                    if not other_ui.model.GetProxy().IsTouchingPoint(self.model.GetCenter()):
                        edges = []
                        sc = self.model.GetCenter()
                        oc = other_ui.model.GetCenter()
                        if sc[0] < oc[0]: edges.append("Left")
                        if sc[0] > oc[0]: edges.append("Right")
                        if sc[1] < oc[1]: edges.append("Bottom")
                        if sc[1] > oc[1]: edges.append("Top")
                if edges:
                    selfBounceAxes = ""
                    otherBounceAxes = ""
                    ss = self.model.GetProxy().speed
                    os = other_ui.model.GetProxy().speed
                    if mode == "In":
                        # Bounce if hitting an edge of the enclosing object, and only if moving toward the other object's edge
                        if ("Left" in edges or "Right" in edges) and new_dist[0] > last_dist[0]:
                            if (ss[0] > 0 and oc[0] < sc[0]) or (ss[0] < 0 and oc[0] > sc[0]):
                                selfBounceAxes += "H"
                            if (os[0] > 0 and sc[0] < oc[0]) or (os[0] < 0 and sc[0] > oc[0]):
                                otherBounceAxes += "H"
                        if ("Top" in edges or "Bottom" in edges) and new_dist[1] > last_dist[1]:
                            if (ss[1] > 0 and oc[1] < sc[1]) or (ss[1] < 0 and oc[1] > sc[1]):
                                selfBounceAxes += "V"
                            if (os[1] > 0 and sc[1] < oc[1]) or (os[1] < 0 and sc[1] > oc[1]):
                                otherBounceAxes += "V"
                    elif mode == "Out":
                        # Bounce if hitting an edge of the other object, and only if moving toward the other object
                        if ("Left" in edges or "Right" in edges) and new_dist[0] < last_dist[0]:
                            if (ss[0] > 0 and oc[0] > sc[0]) or (ss[0] < 0 and oc[0] < sc[0]):
                                selfBounceAxes += "H"
                            if (os[0] > 0 and sc[0] > oc[0]) or (os[0] < 0 and sc[0] < oc[0]):
                                otherBounceAxes += "H"
                        if ("Top" in edges or "Bottom" in edges) and new_dist[1] < last_dist[1]:
                            if (ss[1] > 0 and oc[1] > sc[1]) or (ss[1] < 0 and oc[1] < sc[1]):
                                selfBounceAxes += "V"
                            if (os[1] > 0 and sc[1] > oc[1]) or (os[1] < 0 and sc[1] < oc[1]):
                                otherBounceAxes += "V"

                    if len(selfBounceAxes) or len(otherBounceAxes):
                        sn = self.model.GetProperty("name")
                        on = other_ui.model.GetProperty("name")
                        key = (self, other_ui) if sn < on else (other_ui, self)
                        if key not in collisions:
                            # Add this collision to the list, indexed by normalized object pair to avoid duplicates
                            edgeList = []
                            for eStr in ("Top", "Bottom", "Left", "Right"):
                                if eStr in edges: edgeList.append(eStr)
                            collisions[key] = (self, other_ui, selfBounceAxes, otherBounceAxes, tuple(edgeList), mode)

                self.model.bounceObjs[k][1] = new_dist

            for k in removeFromBounceObjs:
                del self.model.bounceObjs[k]

    def PerformBounce(self, info, elapsedTime):
        # Perform this bounce for this object, and the other object
        (this_ui, other_ui, selfAxes, otherAxes, edges, mode) = info
        ss = self.model.GetProxy().speed
        os = other_ui.model.GetProxy().speed

        # Flags
        selfBounce = other_ui.model in self.model.bounceObjs
        selfBounceInside = False if not selfBounce else self.model.bounceObjs[other_ui.model][0] == "In"
        otherBounce = self.model in other_ui.model.bounceObjs

        # Back up to avoid overlap
        self.model.SetProperty("position", self.model.GetProperty("position") - tuple(ss*(elapsedTime/2)))

        # Finally perform the actual bounces
        if selfBounce and "H" in selfAxes:
            ss.x = -ss.x
        if otherBounce and "H" in otherAxes:
            os.x = -os.x
        if selfBounce and "V" in selfAxes:
            ss.y = -ss.y
        if otherBounce and "V" in otherAxes:
            os.y = -os.y

        # Call the bounce handlers.  It's possible to bounce off of 2 edges at once (a corner), in which
        # case we call this handler once per edge it bounced off of.
        if other_ui.model in self.model.bounceObjs:
            for edge in edges:
                if self.stackManager.runner and self.model.GetHandler("OnBounce"):
                    self.stackManager.runner.RunHandler(self.model, "OnBounce", None,
                                                        [other_ui.model.GetProxy(), edge])

        if self.model in other_ui.model.bounceObjs:
            # Use this opposites dict to show the right edge names in the other object's OnBounce calls
            opposites = {"Top": "Bottom", "Bottom": "Top", "Left": "Right", "Right": "Left"}
            for edge in edges:
                otherEdge = edge if selfBounceInside else opposites[edge] # Don't flip names for inside bounces
                if self.stackManager.runner and other_ui.model.GetHandler("OnBounce"):
                    self.stackManager.runner.RunHandler(other_ui.model, "OnBounce", None,
                                                        [self.model.GetProxy(), otherEdge])


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
        self.fabObjs = []

    def CreateFabObjs(self):
        pass

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

    def FinishedLoad(self):
        self.stackManager.canvas.requestRenderAll()
        self.stackManager.RunSetupIfNeeded()
        self.stackManager.runner.SetupForCard(self.model)
        self.stackManager.runner.RunHandler(self.model, "OnShowCard", None)

    def UnLoad(self):
        if self.model:
            self.stackManager.runner.RunHandler(self.model, "OnHideCard", None)
            self.UnloadFabObjs()

    def AddChildren(self):
        if self.pendingLoads == 0:
            for ui in self.GetAllUiViews():
                for o in ui.fabObjs:
                    self.stackManager.canvas.add(o)
            self.FinishedLoad()

    def FindTargetUi(self, fabObj):
        for ui in self.GetAllUiViews():
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
        self.isHilighted = False
        self.isMouseDown = False
        super().__init__(parent, stackManager, model)

    def CreateFabObjs(self):
        fabric = self.stackManager.fabric
        model = self.model
        rect = self.model.GetFrame()
        hasBorder = model.properties['hasBorder']
        if hasBorder:
            self.rrBg = fabric.Rect.new({'width': rect.Width,
                                         'height': rect.Height,
                                         'rx': 6, 'ry': 6,
                                         'fill': 'white',
                                         'stroke': 'grey',
                                         'strokeWidth':1})
        else:
            self.rrBg = fabric.Rect.new({'width': rect.Width,
                                         'height': rect.Height,
                                         'fill': None,
                                         'strokeWidth':0})

        self.titleLabel = fabric.Textbox.new(model.properties['title'],
                                             {'left': 0,
                                              'top': (rect.Height-18)/2,
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
        self.group.centeredRotation = True
        self.group.hoverCursor = "pointer"
        self.SetFabObjCoords(self.group)
        self.fabObjs = [self.group]
        super().CreateFabObjs()

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

    def CreateFabObjs(self):
        fabric = self.stackManager.fabric
        model = self.model
        rect = self.stackManager.ConvRect(model.GetAbsoluteFrame())
        self.textbox = fabric.Textbox.new(model.properties['text'],
                                          {'width': rect.Width,
                                           'height': rect.Height,
                                           'textAlign': model.properties['alignment'].lower(),
                                           'fill': model.properties['textColor'],
                                           'fontFamily': FontMap[model.properties['font']],
                                           'fontSize': model.properties['fontSize'] * 1.2,
                                           'id': UiView.NextId()})
        self.textbox.centeredRotation = True
        self.textbox.selectable = False
        self.textbox.hoverCursor = "arrow"
        self.SetFabObjCoords(self.textbox)
        self.fabObjs = [self.textbox]
        super().CreateFabObjs()

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

    def SetDown(self):
        self.textbox.off('selected', self.OnSelected)
        self.textbox.off('selection:cleared', self.OnDeselected)
        self.stackManager.canvas.off('text:changed', self.OnTextChanged)
        self.oldOnKeyDown = None
        super().SetDown()

    def CreateFabObjs(self):
        fabric = self.stackManager.fabric
        model = self.model
        rect = model.GetAbsoluteFrame()

        self.textBg = fabric.Rect.new({'width': model.properties['size'].width,
                                       'height': model.properties['size'].height,
                                       'rx': 2, 'ry': 2,
                                       'fill': 'white',
                                       'stroke': 'grey',
                                       'strokeWidth': 1,
                                       'id': UiView.NextId()})
        self.textBg.selectable = False
        self.textBg.centeredRotation = True
        self.textBg.hoverCursor = "arrow"

        self.textbox = fabric.Textbox.new(model.properties['text'],
                                          {'width': rect.Width-2,
                                           'height': rect.Height-2,
                                           'textAlign': model.properties['alignment'].lower(),
                                           'fill': model.properties['textColor'],
                                           'fontFamily': FontMap[model.properties['font']],
                                           'fontSize': model.properties['fontSize']*1.2,
                                           'editable': model.properties['isEditable'],
                                           'id': UiView.NextId()})
        self.offsets = {self.textbox: (2, -2)}
        self.textbox.hasControls = False
        self.textbox.lockMovementX = True
        self.textbox.lockMovementY = True
        self.textbox.centeredRotation = True
        self.textbox.hoverCursor = "text"
        self.SetFabObjCoords(self.textBg)
        self.SetFabObjCoords(self.textbox)

        self.textbox.on('selected', self.OnSelected)
        self.textbox.on('selection:cleared', self.OnDeselected)
        self.stackManager.canvas.on('text:changed', self.OnTextChanged)
        self.oldOnKeyDown = self.textbox.onKeyDown
        self.textbox.onKeyDown = self.OnKeyDown

        self.fabObjs = [self.textBg, self.textbox]
        super().CreateFabObjs()

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
        self.shape = None
        super().__init__(parent, stackManager, model)

    def CreateFabObjs(self):
        model = self.model
        fabric = self.stackManager.fabric
        thickness = model.properties['penThickness']
        shape = None
        if model.type == "oval":
            shape = fabric.Ellipse.new({'rx': model.properties['size'].width/2,
                                        'ry': model.properties['size'].height/2,
                                        'fill': model.properties['fillColor'],
                                        'stroke': model.properties['penColor'],
                                        'strokeWidth': thickness
                                        })
        elif model.type == "rect":
            shape = fabric.Rect.new({'width': model.properties['size'].width,
                                     'height': model.properties['size'].height,
                                     'fill': model.properties['fillColor'],
                                     'stroke': model.properties['penColor'],
                                     'strokeWidth': thickness
                                     })
        elif model.type == "roundrect":
            shape = fabric.Rect.new({'width': model.properties['size'].width,
                                     'height': model.properties['size'].height,
                                     'rx': model.properties['cornerRadius'],
                                     'ry': model.properties['cornerRadius'],
                                     'fill': model.properties['fillColor'],
                                     'stroke': model.properties['penColor'],
                                     'strokeWidth': thickness
                                     })
        elif model.type == "polygon":
            shape = fabric.Polygon.new([{"x":p[0], "y":p[1]} for p in self.model.GetScaledPoints()],
                                          {'fill': model.properties['fillColor'],
                                           'stroke': model.properties['penColor'],
                                           'strokeWidth': thickness,
                                           'strokeLineJoin': 'round',
                                           'flipY': True
                                           })
        elif model.type in ["line", "pen"]:
            shape = fabric.Polyline.new([{"x":p[0], "y":p[1]} for p in self.model.GetScaledPoints()],
                                          {'fill': None,
                                           'stroke': model.properties['penColor'],
                                           'strokeWidth': thickness,
                                           'strokeLineCap': 'round',
                                           'strokeLineJoin': 'round',
                                           'flipY': True
                                         })

        shape.set({'id': UiView.NextId()})
        shape.selectable = False
        shape.centeredRotation = True
        shape.hoverCursor = "arrow"
        shape.rotate(model.GetAbsoluteRotation())
        self.SetFabObjCoords(shape)
        self.shape = shape
        self.fabObjs = [self.shape]
        super().CreateFabObjs()

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
        elif key == "shape" or (key == "size" and self.model.type in ("line", "pen", "polygon")):
            index = self.stackManager.canvas.getObjects().index(self.shape)
            self.stackManager.canvas.remove(self.shape)
            self.CreateFabObjs()
            self.stackManager.canvas.add(self.shape)
            self.shape.moveTo(index)

class UiImage(UiView):
    def __init__(self, parent, stackManager, model):
        self.origImage = None
        self.image = None
        self.imgOffset = (0, 0)
        super().__init__(parent, stackManager, model)

    def CreateFabObjs(self):
        fabric = self.stackManager.fabric
        model = self.model
        file = "Resources/" + model.properties['file']
        superCreateFabObjs = super().CreateFabObjs

        def imgLoaded(img, err):
            if not err:
                self.origImage = img
                self.FitImage()
                self.image.set({'id': UiView.NextId()})
                self.image.selectable = False
                self.image.centeredRotation = True
                self.image.hoverCursor = "arrow"
                self.SetFabObjCoords(self.image)
                superCreateFabObjs()
            self.stackManager.uiCard.pendingLoads -= 1
            self.stackManager.uiCard.AddChildren()

        self.stackManager.uiCard.pendingLoads += 1
        fabric.Image.fromURL(file, imgLoaded)

    def FitImage(self):
        rect = self.model.GetFrame()
        imgSize = self.origImage.getOriginalSize()
        fit = self.model.GetProperty('fit')

        def setImg(img):
            self.image = img

        if fit == "Stretch":
            scaleX,scaleY = (rect.Width / imgSize['width'], rect.Height / imgSize['height'])
            self.origImage.cloneAsImage(setImg)
            self.image.set({'scaleX': scaleX, 'scaleY': scaleY})
            self.offsets = {}
        elif fit == "Fill":
            scale = max(rect.Width / imgSize['width'], rect.Height / imgSize['height'])
            dx = (imgSize.width*scale - rect.Width) / 2
            dy = (imgSize.height*scale - rect.Height) / 2
            self.origImage.cloneAsImage(setImg,
                                        {'left': max(dx, 0) / scale, 'top': max(dy, 0) / scale,
                                         'width': rect.Width / scale,
                                         'height': rect.Height / scale})
            self.image.set({'scaleX': scale, 'scaleY': scale})
            self.offsets = {self.image: (-max(dx,0)/scale, -max(dy,0)/scale)}
        elif fit == "Center":
            dx = (imgSize.width - rect.Width) / 2
            dy = (imgSize.height - rect.Height) / 2
            self.origImage.cloneAsImage(setImg,
                                        {'left': max(dx, 0), 'top': max(dy, 0),
                                         'width': min(rect.Width, imgSize.width), 'height': min(rect.Height, imgSize.height)})
            self.offsets = {self.image: (-dx, -dy)}
        else:  # "Contain"
            scale = min(rect.Width / imgSize['width'], rect.Height / imgSize['height'])
            dx = (imgSize.width*scale - rect.Width) / 2
            dy = (imgSize.height*scale - rect.Height) / 2
            self.origImage.cloneAsImage(setImg)
            self.image.set({'scaleX': scale, 'scaleY': scale,
                            'left': rect.Left - min(dx,0), 'top': rect.Top - min(dy,0)})
            self.offsets = {self.image: (-min(dx,0), -min(dy,0))}
        self.fabObjs = [self.image]

    def OnPropertyChanged(self, key):
        if key not in ("size", "position", "center"):
            super().OnPropertyChanged(key)
        if key == "size":
            s = self.model.GetProperty("size")
            self.image.set({'width': s.width, 'height': s.height})
            self.image.setCoords()
        if key in ("position", "center", "size"):
            self.SetFabObjCoords(self.image)
        elif key == "file":
            file = "Resources/" + self.model.properties['file']
            self.image.setSrc(file)
        elif key == "fit":
            index = self.stackManager.canvas.getObjects().index(self.image)
            self.stackManager.canvas.remove(self.image)
            self.FitImage()
            self.stackManager.canvas.add(self.image)
            self.image.moveTo(index)


class UiGroup(UiView):
    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model)

    def LoadChildren(self):
        super().LoadChildren()
        super().CreateFabObjs()

    def GetAllUiViews(self, allUiViews):
        for uiView in self.uiViews.values():
            allUiViews.append(uiView)
            if uiView.model.type == "group":
                uiView.GetAllUiViews(allUiViews)

    def OnPropertyChanged(self, key):
        super().OnPropertyChanged(key)
        if key in ("size", "position", "center", "rotation"):
            for ui in self.uiViews.values():
                ui.OnPropertyChanged(key)


class UiWebView(UiView):
    pass
