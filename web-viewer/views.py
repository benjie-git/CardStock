from browser import self as worker
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
        self.fabIds = []
        self.offsets = []
        self.sizeOffsets = []
        self.uiViews = []
        self.CreateFabObjs()

    def CreateFabObjs(self):
        pass

    def SetDown(self):
        for ui in self.uiViews:
            ui.SetDown()
        self.stackManager = None
        self.parent = None
        self.uiViews = None
        self.model = None

    def LoadChildren(self):
        for m in self.model.childModels:
            ui = self.stackManager.UiViewFromModel(self, self.stackManager, m)
            self.stackManager.AddUiViewToMap(ui)
            self.uiViews.append(ui)
            ui.LoadChildren()

    def OnMouseDown(self, pos, isTouch):
        self.stackManager.runner.RunHandler(self.model, "on_mouse_press", pos, isTouch)

    def OnMouseMove(self, pos, isTouch):
        self.stackManager.runner.RunHandler(self.model, "on_mouse_move", pos, isTouch)

    def OnMouseUp(self, pos, isTouch):
        self.stackManager.runner.RunHandler(self.model, "on_mouse_release", pos, isTouch)

    def OnPeriodic(self):
        self.stackManager.runner.RunHandler(self.model, "on_periodic", None)
        for ui in self.uiViews.copy():
            ui.OnPeriodic()

    def OnPropertyChanged(self, key):
        if key == "size":
            s = self.model.GetProperty("size")
            data = []
            i = 0
            for uid in self.fabIds:
                sizeOffset = (0, 0)
                if len(self.sizeOffsets) > i:
                    sizeOffset = self.sizeOffsets[i]
                data.append(("fabSet", uid, {'width': int(s.width+sizeOffset[0]), 'height': int(s.height+sizeOffset[1])}))
                i += 1
            worker.stackWorker.SendAsync(*data)
        if key in ("position", "center", "size", "rotation"):
            self.UpdateFabObjCoords()
        elif key == "is_visible":
            visible = self.model.GetProperty("is_visible")
            data = []
            for i in self.fabIds:
                data.append(("fabSet", i, {'visible': visible}))
            worker.stackWorker.SendAsync(*data)

    def GetFabObjCoords(self):
        size = self.model.properties["size"]
        if self.model.parent and self.model.parent.type != "card":
            rot = self.model.GetAbsoluteRotation()
        else:
            rot = self.model.properties["rotation"] if "rotation" in self.model.properties else 0
        num = max(len(self.offsets), 1)
        results = []
        for i in range(num):
            pos = self.model.properties["position"] + (0, size.height)
            objOffset = (0,0)
            if i < len(self.offsets):
                objOffset = self.offsets[i]
                pos += (objOffset[0], objOffset[1])

            if self.model.type in ["oval", "rect", "roundrect", "polygon", "line", "pen"]:
                thick = self.model.GetProperty('pen_thickness')
                pos = wx.Point(pos[0] - thick / 2, pos[1] + thick / 2)
            if rot:
                s = size + (-2*objOffset[0], 2*objOffset[1])
                aff = wx.AffineMatrix2D()
                aff.Rotate(math.radians(-rot))
                offset = aff.TransformPoint(s[0] / 2, -s[1] / 2)
                pos += (s[0] / 2 - offset[0], -s[1] / 2 - offset[1])
            if self.model.type in ["line", "pen"]:
                if size.height == 2: pos[1] -= 2

            if self.model.parent and (self.model.parent.type != "card" or rot):
                aff = self.model.parent.GetAffineTransform()
                pos = aff.TransformPoint(pos[0], pos[1])
            self.stackManager.ConvPointInPlace(pos)
            results.append((pos[0], pos[1], rot))
        return results

    def UpdateFabObjCoords(self):
        results = self.GetFabObjCoords()
        msgs = []
        for i in range(min(len(results), len(self.fabIds))):
            uid = self.fabIds[i]
            vals = results[i]
            msgs.append(("fabSet", uid, {'left': vals[0], 'top': vals[1], 'angle':vals[2]}))
        worker.stackWorker.SendAsync(*msgs)

    def RunAnimations(self, onFinishedCalls, elapsed_time):
        # Move the object by speed.x and speed.y pixels per second
        updateList = []
        finishList = []
        didRun = False
        if self.model.type not in ["stack", "card"]:
            speed = self.model.properties["speed"]
            if (speed.x != 0 or speed.y != 0) and "position" not in self.model.animations:
                pos = self.model.properties["position"]
                self.model.SetProperty("position", [pos.x + speed.x*elapsed_time, pos.y + speed.y*elapsed_time])
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
        if not self.model.didSetDown and self.model.GetProperty("is_visible") and tuple(self.model.GetProperty("speed")) != (0, 0):
            for k,v in self.model.bounceObjs.items():
                other_ui = self.stackManager.GetUiViewByModel(k)
                (mode, last_dist) = v

                if not other_ui.model.GetProperty("is_visible"):
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
                    self.model.bounceObjs[k][0] = "In" if other_ui.model.GetProxy().is_touching_point(self.model.GetCenter()) else "Out"
                    self.model.bounceObjs[k][1] = new_dist
                    continue

                edges = self.model.GetProxy().is_touching_edge(other_ui.model.GetProxy(), mode == "In")
                if mode == "In" and not edges:
                    if not other_ui.model.GetProxy().is_touching_point(self.model.GetCenter()):
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

    def PerformBounce(self, info, elapsed_time):
        # Perform this bounce for this object, and the other object
        (this_ui, other_ui, selfAxes, otherAxes, edges, mode) = info
        ss = self.model.GetProxy().speed
        os = other_ui.model.GetProxy().speed

        # Flags
        selfBounce = other_ui.model in self.model.bounceObjs
        selfBounceInside = False if not selfBounce else self.model.bounceObjs[other_ui.model][0] == "In"
        otherBounce = self.model in other_ui.model.bounceObjs

        # Back up to avoid overlap
        self.model.SetProperty("position", self.model.GetProperty("position") - tuple(ss*(elapsed_time/2)))

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
                if self.stackManager.runner and self.model.GetHandler("on_bounce"):
                    self.stackManager.runner.RunHandler(self.model, "on_bounce", None,
                                                        [other_ui.model.GetProxy(), edge])

        if self.model in other_ui.model.bounceObjs:
            # Use this opposites dict to show the right edge names in the other object's on_bounce calls
            opposites = {"Top": "Bottom", "Bottom": "Top", "Left": "Right", "Right": "Left"}
            for edge in edges:
                otherEdge = edge if selfBounceInside else opposites[edge] # Don't flip names for inside bounces
                if self.stackManager.runner and other_ui.model.GetHandler("on_bounce"):
                    self.stackManager.runner.RunHandler(other_ui.model, "on_bounce", None,
                                                        [self.model.GetProxy(), otherEdge])


class UiCard(UiView):
    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model)
        self.lastMouseOverObj = None
        self.mouseCaptureObj = None

    def Load(self, model):
        self.Unload()
        self.lastMouseOverObj = None
        self.model = model
        worker.stackWorker.SendAsync(("fabFunc", 0, "setBackgroundColor", self.model.GetProperty("fill_color")))
        self.LoadChildren()
        self.stackManager.RunSetupIfNeeded()
        self.stackManager.runner.SetupForCard(self.model)
        self.stackManager.runner.RunHandler(self.model, "on_show_card", None)

    def Unload(self):
        if self.model:
            self.stackManager.runner.RunHandler(self.model, "on_hide_card", None)
            self.stackManager.RemoveFabObjs(self)
            self.stackManager.delayedSetDowns.extend(self.uiViews)
            self.uiViews = []

    def GetAllUiViews(self):
        allUiViews = []
        for uiView in self.uiViews:
            allUiViews.append(uiView)
            if uiView.model.type == "group":
                uiView.GetAllUiViews(allUiViews)
        return allUiViews

    def FindTargetUi(self, uid):
        if uid == 0:
            return self
        for ui in self.GetAllUiViews():
            if uid in ui.fabIds:
                return ui
        return None

    def GetFirstFabIndexForUiView(self, uiView):
        uiViews = self.GetAllUiViews()
        n = 0
        for ui in uiViews:
            if ui == uiView:
                return n
            n += len(ui.fabIds)
        return None

    def OnFabricMouseDown(self, uid, pos, isTouch):
        target_ui = self.FindTargetUi(uid)
        pos = wx.Point(pos[0], pos[1])
        self.stackManager.runner.lastMousePos = pos
        self.stackManager.runner.ResetStopHandlingMouseEvent()
        if self.mouseCaptureObj:
            target_ui = self.mouseCaptureObj
        if target_ui:
            while target_ui.model.type != "card":
                target_ui.OnMouseDown(pos, isTouch)
                if self.stackManager.runner.DidStopHandlingMouseEvent():
                    return
                target_ui = target_ui.parent
        self.OnMouseDown(pos, isTouch)

    def OnFabricMouseMove(self, uid, pos, isTouch):
        target_ui = self.FindTargetUi(uid)
        pos = wx.Point(pos[0], pos[1])
        self.stackManager.runner.lastMousePos = pos

        if self.lastMouseOverObj and not self.lastMouseOverObj.model:
            self.lastMouseOverObj = None

        if target_ui != self.lastMouseOverObj:
            if self.lastMouseOverObj:
                self.stackManager.runner.RunHandler(self.lastMouseOverObj.model, "on_mouse_exit", pos)
            self.lastMouseOverObj = target_ui
            if self.lastMouseOverObj:
                self.stackManager.runner.RunHandler(self.lastMouseOverObj.model, "on_mouse_enter", pos)

        self.stackManager.runner.ResetStopHandlingMouseEvent()
        if self.mouseCaptureObj:
            target_ui = self.mouseCaptureObj
        if target_ui:
            while target_ui.model.type != "card":
                target_ui.OnMouseMove(pos, isTouch)
                if self.stackManager.runner.DidStopHandlingMouseEvent():
                    return
                target_ui = target_ui.parent
        self.OnMouseMove(pos, isTouch)

    def OnFabricMouseUp(self, uid, pos, isTouch):
        target_ui = self.FindTargetUi(uid)
        pos = wx.Point(pos[0], pos[1])
        self.stackManager.runner.ResetStopHandlingMouseEvent()
        if self.mouseCaptureObj:
            target_ui = self.mouseCaptureObj
        if target_ui:
            while target_ui.model.type != "card":
                target_ui.OnMouseUp(pos, isTouch)
                if self.stackManager.runner.DidStopHandlingMouseEvent():
                    return
                target_ui = target_ui.parent
        self.OnMouseUp(pos, isTouch)

    def OnKeyDown(self, code):
        self.stackManager.runner.OnKeyDown(code)
        self.stackManager.runner.RunHandler(self.model, "on_key_press", code)

    def OnKeyHold(self):
        for key_name in self.stackManager.runner.pressedKeys:
            self.stackManager.runner.RunHandler(self.model, "on_key_hold", None, key_name)

    def OnKeyUp(self, code):
        self.stackManager.runner.OnKeyUp(code)
        self.stackManager.runner.RunHandler(self.model, "on_key_release", code)

    def OnTextChanged(self, uid, text):
        target_ui = self.FindTargetUi(uid)
        if target_ui:
            target_ui.on_text_changed(text)

    def OnTextEnter(self, uid):
        target_ui = self.FindTargetUi(uid)
        if target_ui:
            target_ui.OnEnter()

    def OnPropertyChanged(self, key):
        super().OnPropertyChanged(key)
        if key == "fill_color":
            worker.stackWorker.SendAsync(("fabFunc", 0, "setBackgroundColor", self.model.GetProperty("fill_color")))


class UiButton(UiView):
    def __init__(self, parent, stackManager, model):
        self.isHilighted = False
        self.isMouseDown = False
        self.rrBg = None
        self.icon = None
        super().__init__(parent, stackManager, model)

    def CreateFabObjs(self, shouldReplace=False):
        model = self.model
        style = model.properties['style']
        rect = self.model.GetFrame()

        if style in ("Border", "Borderless"):
            self.offsets = ((0, 0), (0, -(rect.Height - 16) / 2))
            coords = self.GetFabObjCoords()
        else:
            self.offsets = ((0,0), (23, -(rect.Height - 16) / 2), (2, -(rect.Height - 16) / 2 - 1))
            coords = self.GetFabObjCoords()

        if style == "Border":
            self.rrBg = worker.stackWorker.CreateFab("Rect",
                                                     {'width': rect.Width,
                                                      'height': rect.Height,
                                                      'left': coords[0][0],
                                                      'top': coords[0][1],
                                                      'angle': coords[0][2],
                                                      'rx': 6, 'ry': 6,
                                                      'fill': 'white',
                                                      'stroke': 'grey',
                                                      'strokeWidth': 1,
                                                      'hoverCursor': "pointer"},
                                                     replace=self.rrBg if shouldReplace else None)
        else:
            self.rrBg = worker.stackWorker.CreateFab("Rect",
                                                     {'width': rect.Width,
                                                      'height': rect.Height,
                                                      'left': coords[0][0],
                                                      'top': coords[0][1],
                                                      'angle': coords[0][2],
                                                      'fill': None,
                                                      'strokeWidth': 0,
                                                      'hoverCursor': "pointer"},
                                                     replace=self.rrBg if shouldReplace else None)

        if style in ("Border", "Borderless"):
            self.titleLabel = worker.stackWorker.CreateFab("Textbox", model.GetProperty("title"),
                                                           {'width': rect.Width,
                                                            'height': rect.Height,
                                                            'left': coords[1][0],
                                                            'top': coords[1][1],
                                                            'angle': coords[1][2],
                                                            'textAlign': 'center',
                                                            'fill': "black",
                                                            'fontFamily': 'Arial',
                                                            'fontSize': 14,
                                                            'hoverCursor': "pointer"},
                                                           replace=self.titleLabel if shouldReplace else None)
            self.fabIds = [self.rrBg, self.titleLabel]

        else:
            self.titleLabel = worker.stackWorker.CreateFab("Textbox", model.GetProperty("title"),
                                                           {'width': rect.Width,
                                                            'height': rect.Height,
                                                            'left': coords[1][0],
                                                            'top': coords[1][1],
                                                            'angle': coords[1][2],
                                                            'textAlign': 'left',
                                                            'fill': "black",
                                                            'fontFamily': 'Arial',
                                                            'fontSize': 14,
                                                            'hoverCursor': "pointer"},
                                                           replace=self.titleLabel if shouldReplace else None)
            self.icon = worker.stackWorker.CreateImageStatic(self.MakeIconPath(model),
                                                             {'left': coords[2][0],
                                                              'top': coords[2][1],
                                                              'angle': coords[2][2],
                                                              'scaleX': 0.5,
                                                              'scaleY': 0.5,
                                                              'visible': True},
                                                             replace=self.icon if shouldReplace else None)
            self.fabIds = [self.rrBg, self.titleLabel, self.icon]

    def MakeIconPath(self, model):
        style = model.properties['style']
        is_sel = model.GetProperty("is_selected")
        return f"/s/icons/{'checkbox' if style == 'Checkbox' else 'radio'}-{'on' if is_sel else 'off'}.png"

    def Highlight(self, on):
        style = self.model.properties['style']
        if style == "Border":
            worker.stackWorker.SendAsync(('fabSet', self.rrBg, {'fill': "#CCCCCC" if on else "white"}),
                                         ("render",))
        elif style == "Borderless":
            worker.stackWorker.SendAsync(('fabSet', self.titleLabel, {'fill': "#888888"  if on else "black"}),
                                         ("render",))
        self.isHilighted = on

    def OnMouseDown(self, pos, isTouch):
        self.stackManager.uiCard.mouseCaptureObj = self
        super().OnMouseDown(pos, isTouch)
        self.isMouseDown = True
        self.Highlight(True)
        style = self.model.properties['style']
        if style == "Radio":
            self.model.SetProperty("is_selected", True)
        elif style == "Checkbox":
            self.model.SetProperty("is_selected", not self.model.GetProperty("is_selected"))

    def OnMouseMove(self, pos, isTouch):
        if self.isMouseDown:
            contains = self.model.GetProxy().is_touching_point(pos)
            if not self.isHilighted and contains:
                self.Highlight(True)
            elif self.isHilighted and not contains:
                self.Highlight(False)

    def OnMouseUp(self, pos, isTouch):
        self.stackManager.uiCard.mouseCaptureObj = None
        self.isMouseDown = False
        if self.isHilighted:
            self.Highlight(False)
            self.stackManager.runner.RunHandler(self.model, "on_click", pos)
        super().OnMouseUp(pos, isTouch)

    def OnPropertyChanged(self, key):
        if key == "size":
            s = self.model.properties['size']
            self.offsets = ((0,0), (0, -(s.height - 16) / 2))
        if key == "title":
            worker.stackWorker.SendAsync(('fabSet', self.titleLabel, {'text':self.model.GetProperty("title")}))
        elif key in ("style", "is_selected"):
            self.CreateFabObjs(shouldReplace=True)
        super().OnPropertyChanged(key)


class UiTextLabel(UiView):
    def __init__(self, parent, stackManager, model):
        self.textbox = None
        super().__init__(parent, stackManager, model)

    def CreateFabObjs(self):
        model = self.model
        rect = self.stackManager.ConvRect(model.GetAbsoluteFrame())
        coords = self.GetFabObjCoords()
        self.textbox = worker.stackWorker.CreateFab("Textbox",
                                                    model.properties['text'],
                                                    {'width': rect.Width,
                                                     'height': rect.Height,
                                                     'left': coords[0][0],
                                                     'top': coords[0][1],
                                                     'angle': coords[0][2],
                                                     'textAlign': model.properties['alignment'].lower(),
                                                     'fill': model.properties['text_color'],
                                                     'fontFamily': FontMap[model.properties['font']],
                                                     'fontSize': model.properties['font_size'] * 1.1,
                                                     'origFontSize': model.properties['font_size'] * 1.1,
                                                     'fontWeight': "bold" if model.properties['is_bold'] else "normal",
                                                     'fontStyle': "italic" if model.properties['is_italic'] else "normal",
                                                     'underline': model.properties['is_underlined'],
                                                     'autoShrink': model.properties['can_auto_shrink'],
                                                     'visible': model.properties['is_visible']})
        if model.properties['can_auto_shrink']:
            worker.stackWorker.SendAsync(('fabLabelAutoSize', self.textbox))
        self.fabIds = [self.textbox]


    def OnPropertyChanged(self, key):
        super().OnPropertyChanged(key)
        if key == "text":
            worker.stackWorker.SendAsync(("fabSet", self.textbox, {'text': self.model.GetProperty(key)}),
                                         ('fabLabelAutoSize', self.textbox))
        elif key == "text_color":
            worker.stackWorker.SendAsync(("fabSet", self.textbox, {'fill': self.model.GetProperty(key)}))
        elif key == "alignment":
            worker.stackWorker.SendAsync(("fabSet", self.textbox, {'textAlign': self.model.properties['alignment'].lower()}))
        elif key == "font":
            worker.stackWorker.SendAsync(("fabSet", self.textbox, {'fontFamily': FontMap[self.model.properties['font']]}),
                                         ('fabLabelAutoSize', self.textbox))
        elif key == "font_size":
            worker.stackWorker.SendAsync(("fabSet", self.textbox,
                                          {'fontSize': self.model.properties['font_size'] * 1.1,
                                           'origFontSize': self.model.properties['font_size'] * 1.1}),
                                         ('fabLabelAutoSize', self.textbox))
        elif key == "is_bold":
            worker.stackWorker.SendAsync(("fabSet", self.textbox, {'fontWeight': "bold" if self.model.properties['is_bold'] else "normal"}),
                                         ('fabLabelAutoSize', self.textbox))
        elif key == "is_italic":
            worker.stackWorker.SendAsync(("fabSet", self.textbox, {'fontStyle': "italic" if self.model.properties['is_italic'] else "normal"}),
                                         ('fabLabelAutoSize', self.textbox))
        elif key == "is_underlined":
            worker.stackWorker.SendAsync(("fabSet", self.textbox, {'underline': self.model.properties['is_underlined']}),
                                         ('fabLabelAutoSize', self.textbox))
        elif key in ("size", "can_auto_shrink"):
            worker.stackWorker.SendAsync(('fabLabelAutoSize', self.textbox))

class UiTextField(UiView):
    def __init__(self, parent, stackManager, model):
        self.textBg = None
        self.textbox = None
        super().__init__(parent, stackManager, model)

    def CreateFabObjs(self):
        model = self.model
        rect = model.GetAbsoluteFrame()
        self.offsets = ((0,0), (2, -2))
        self.sizeOffsets = ((0,0), (-4, -2))
        coords = self.GetFabObjCoords()

        self.textBg = worker.stackWorker.CreateFab("Rect",
                                                   {'width': model.properties['size'].width,
                                                    'height': model.properties['size'].height,
                                                    'left': coords[0][0],
                                                    'top': coords[0][1],
                                                    'angle': coords[0][2],
                                                    'rx': 2, 'ry': 2,
                                                    'fill': 'white',
                                                    'stroke': 'grey',
                                                    'strokeWidth': 1,
                                                    'visible': model.properties['is_visible']})

        self.textbox = worker.stackWorker.CreateTextField(model.properties['text'],
                                                          {'width': rect.Width - 4,
                                                           'height': rect.Height - 2,
                                                           'left': coords[0][0] + 2,
                                                           'top': coords[0][1] + 2,
                                                           'angle': coords[0][2],
                                                           'autoShrink': False,
                                                           'textAlign': model.properties['alignment'].lower(),
                                                           'fill': model.properties['text_color'],
                                                           'fontFamily': FontMap[model.properties['font']],
                                                           'fontSize': model.properties['font_size']*1.1,
                                                           'fontWeight': "bold" if model.properties['is_bold'] else "normal",
                                                           'fontStyle': "italic" if model.properties['is_italic'] else "normal",
                                                           'editable': model.properties['is_editable'],
                                                           'isMultiline': model.properties['is_multiline'],
                                                           'visible': model.properties['is_visible']})
        self.fabIds = [self.textBg, self.textbox]

    def OnEnter(self):
        self.model.stackManager.runner.RunHandler(self.model, "on_text_enter", None)

    def on_text_changed(self, text):
        self.model.SetProperty('text', text)
        self.stackManager.runner.RunHandler(self.model, "on_text_changed", None)

    def OnPropertyChanged(self, key):
        super().OnPropertyChanged(key)
        if key == "text":
            worker.stackWorker.SendAsync(("fabSet", self.textbox, {'text': self.model.GetProperty(key)}))
        elif key == "text_color":
            worker.stackWorker.SendAsync(("fabSet", self.textbox, {'fill': self.model.GetProperty(key)}))
        elif key == "alignment":
            worker.stackWorker.SendAsync(("fabSet", self.textbox, {'textAlign': self.model.properties['alignment'].lower()}))
        elif key == "font":
            worker.stackWorker.SendAsync(("fabSet", self.textbox, {'fontFamily': FontMap[self.model.properties['font']]}))
        elif key == "font_size":
            worker.stackWorker.SendAsync(("fabSet", self.textbox, {'fontSize': self.model.properties['font_size'] * 1.1}))
        elif key == "is_bold":
            worker.stackWorker.SendAsync(("fabSet", self.textbox, {'fontWeight': "bold" if self.model.properties['is_bold'] else "normal"}),
                                         ('fabLabelAutoSize', self.textbox))
        elif key == "is_italic":
            worker.stackWorker.SendAsync(("fabSet", self.textbox, {'fontStyle': "italic" if self.model.properties['is_italic'] else "normal"}),
                                         ('fabLabelAutoSize', self.textbox))
        elif key == "is_editable":
            worker.stackWorker.SendAsync(("fabSet", self.textbox, {'editable': self.model.properties['is_editable']}))
        elif key == "selectAll":
            worker.stackWorker.SendAsync(("fabFunc", self.textbox, "selectAll"))


class UiShape(UiView):
    def __init__(self, parent, stackManager, model):
        self.shape = None
        super().__init__(parent, stackManager, model)

    def CreateFabObjs(self):
        model = self.model
        thickness = model.properties['pen_thickness']
        shape = None
        coords = self.GetFabObjCoords()
        if model.type == "oval":
            shape = worker.stackWorker.CreateFab("Ellipse",
                                                 {'rx': model.properties['size'].width / 2,
                                                  'ry': model.properties['size'].height / 2,
                                                  'left': coords[0][0],
                                                  'top': coords[0][1],
                                                  'angle': coords[0][2],
                                                  'fill': model.properties['fill_color'],
                                                  'stroke': model.properties['pen_color'],
                                                  'strokeWidth': thickness,
                                                  'visible': model.properties['is_visible']}, replace=self.shape)
        elif model.type == "rect":
            shape = worker.stackWorker.CreateFab("Rect",
                                                 {'width': model.properties['size'].width,
                                                  'height': model.properties['size'].height,
                                                  'left': coords[0][0],
                                                  'top': coords[0][1],
                                                  'angle': coords[0][2],
                                                  'fill': model.properties['fill_color'],
                                                  'stroke': model.properties['pen_color'],
                                                  'strokeWidth': thickness,
                                                  'visible': model.properties['is_visible']}, replace=self.shape)
        elif model.type == "roundrect":
            shape = worker.stackWorker.CreateFab("Rect",
                                                 {'width': model.properties['size'].width,
                                                  'height': model.properties['size'].height,
                                                  'left': coords[0][0],
                                                  'top': coords[0][1],
                                                  'angle': coords[0][2],
                                                  'rx': model.properties['corner_radius'],
                                                  'ry': model.properties['corner_radius'],
                                                  'fill': model.properties['fill_color'],
                                                  'stroke': model.properties['pen_color'],
                                                  'strokeWidth': thickness,
                                                  'visible': model.properties['is_visible']}, replace=self.shape)
        elif model.type == "polygon":
            shape = worker.stackWorker.CreateFab("Polygon",
                                                 [{"x": p[0], "y": p[1]} for p in self.model.GetScaledPoints()],
                                                 {'left': coords[0][0],
                                                  'top': coords[0][1],
                                                  'angle': coords[0][2],
                                                  'fill': model.properties['fill_color'],
                                                  'stroke': model.properties['pen_color'],
                                                  'strokeWidth': thickness,
                                                  'strokeLineJoin': 'round',
                                                  'flipY': True,
                                                  'visible': model.properties['is_visible']}, replace=self.shape)
        elif model.type in ["line", "pen"]:
            shape = worker.stackWorker.CreateFab("Polyline",
                                                 [{"x": p[0], "y": p[1]} for p in self.model.GetScaledPoints()],
                                                 {'left': coords[0][0],
                                                  'top': coords[0][1],
                                                  'angle': coords[0][2],
                                                  'fill': None,
                                                  'stroke': model.properties['pen_color'],
                                                  'strokeWidth': thickness,
                                                  'strokeLineCap': 'round',
                                                  'strokeLineJoin': 'round',
                                                  'flipY': True,
                                                  'visible': model.properties['is_visible']}, replace=self.shape)
        self.shape = shape
        self.fabIds = [self.shape]

    def OnPropertyChanged(self, key):
        if key == "fill_color":
            worker.stackWorker.SendAsync(("fabSet", self.shape, {'fill': self.model.GetProperty(key)}))
        elif key == "pen_color":
            worker.stackWorker.SendAsync(("fabSet", self.shape, {'stroke': self.model.GetProperty(key)}))
        elif key == "pen_thickness":
            worker.stackWorker.SendAsync(("fabSet", self.shape, {'strokeWidth': self.model.GetProperty(key)}))
        elif self.model.type == "oval" and key == "size":
            s = self.model.GetProperty("size")
            worker.stackWorker.SendAsync(("fabSet", self.shape, {'rx': int(s.width/2), 'ry': int(s.height/2)}))
        elif key == "shape" or (key == "size" and self.model.type in ("line", "pen", "polygon")):
            self.CreateFabObjs()
        else:
            super().OnPropertyChanged(key)


class UiImage(UiView):
    def __init__(self, parent, stackManager, model):
        self.origImageSize = wx.Size(1, 1)
        self.image = None
        self.imgOffset = (0, 0)
        super().__init__(parent, stackManager, model)

    def SetImageSize(self, w, h):
        self.origImageSize = wx.Size(w, h)
        self.FitImage()

    def CreateFabObjs(self):
        model = self.model
        file = model.properties['file']
        self.image = worker.stackWorker.CreateImage(file)
        self.fabIds = [self.image]

    def FitImage(self):
        s = self.model.GetProperty('size')
        imgSize = self.origImageSize
        fit = self.model.GetProperty('fit')

        if fit == "Stretch":
            self.offsets = ((0, 0),)
            results = self.GetFabObjCoords()[0]
            options = {'fit': "Stretch", 'left': results[0], 'top': results[1],
                       'clipLeft': 0, 'clipTop': 0, 'clipWidth': imgSize.width, 'clipHeight': imgSize.height,
                       'scaleX': s.width / imgSize.width, 'scaleY': s.height / imgSize.height, 'angle': results[2],
                       'visible': self.model.properties['is_visible']}

        elif fit == "Fill":
            scale = max(s.width / imgSize.width, s.height / imgSize.height)
            dx = (imgSize.width*scale - s.width) / 2
            dy = (imgSize.height*scale - s.height) / 2
            self.offsets = ((-min(dx,0)/scale, -min(dy,0)/scale),)
            results = self.GetFabObjCoords()[0]
            options = {'fit': "Fill", 'left': results[0], 'top': results[1],
                       'clipLeft': max(dx, 0) / scale, 'clipTop': max(dy, 0) / scale,
                       'clipWidth': int(s.width / scale), 'clipHeight': int(s.height / scale),
                       'scaleX': scale, 'scaleY': scale, 'angle': results[2], 'visible': self.model.properties['is_visible']}

        elif fit == "Center":
            dx = (imgSize.width - s.width) / 2
            dy = (imgSize.height - s.height) / 2
            self.offsets = ((max(-dx, 0), min(dy,0)),)
            results = self.GetFabObjCoords()[0]
            options = {'fit': "Center", 'left': results[0], 'top': results[1],
                       'clipLeft': max(dx, 0), 'clipTop': max(dy, 0),
                       'clipWidth': min(s.width, imgSize.width), 'clipHeight': min(s.height, imgSize.height),
                       'scaleX': 1, 'scaleY': 1, 'angle': results[2], 'visible': self.model.properties['is_visible']}

        else:  # "Contain"
            scale = min(s.width / imgSize.width, s.height / imgSize.height)
            dx = (imgSize.width*scale - s.width) / 2
            dy = (imgSize.height*scale - s.height) / 2
            self.offsets = ((max(-dx,0), min(dy,0)),)
            results = self.GetFabObjCoords()[0]
            options = {'fit': "Contain", 'left': results[0], 'top': results[1],
                       'clipLeft': 0, 'clipTop': 0, 'clipWidth': imgSize.width, 'clipHeight': imgSize.height,
                       'scaleX': scale, 'scaleY': scale, 'angle': results[2], 'visible': self.model.properties['is_visible']}

        worker.stackWorker.SendAsync(("imgRefit", self.image, options))

    def OnPropertyChanged(self, key):
        if key != "size":
            super().OnPropertyChanged(key)
        if key in ("size", "fit"):
            self.FitImage()
        elif key == "file":
            file = self.model.properties['file']
            worker.stackWorker.CreateImage(file, replace=self.image)


class UiGroup(UiView):
    # def __init__(self, parent, stackManager, model):
    #     super().__init__(parent, stackManager, model)

    def LoadChildren(self):
        super().LoadChildren()
        super().CreateFabObjs()

    def GetAllUiViews(self, allUiViews):
        for uiView in self.uiViews:
            allUiViews.append(uiView)
            if uiView.model.type == "group":
                uiView.GetAllUiViews(allUiViews)

    def OnPropertyChanged(self, key):
        super().OnPropertyChanged(key)
        if key in ("size", "position", "center", "rotation"):
            for ui in self.uiViews:
                ui.OnPropertyChanged(key)


class UiWebView(UiView):
    def __init__(self, parent, stackManager, model):
        self.textBg = None
        self.textbox = None
        super().__init__(parent, stackManager, model)

    def CreateFabObjs(self):
        model = self.model
        rect = model.GetAbsoluteFrame()
        self.offsets = ((0, 0), (2, -2))
        coords = self.GetFabObjCoords()

        self.textBg = worker.stackWorker.CreateFab("Rect",
                                                   {'width': model.properties['size'].width,
                                                    'height': model.properties['size'].height,
                                                    'left': coords[0][0],
                                                    'top': coords[0][1],
                                                    'fill': 'grey',
                                                    'stroke': 'black',
                                                    'strokeWidth': 1,
                                                    'hoverCursor': "arrow",
                                                    'visible': model.properties['is_visible']})

        self.textbox = worker.stackWorker.CreateFab("Textbox", model.properties['URL'],
                                                        {'width': rect.Width - 2,
                                                         'left': coords[0][0],
                                                         'top': coords[0][1],
                                                         'angle': coords[0][2],
                                                         'textAlign': "center",
                                                         'fill': 'black',
                                                         'fontFamily': 'Arial',
                                                         'fontSize': 14,
                                                         'hoverCursor': "arrow",
                                                         'editable': False,
                                                         'visible': model.properties['is_visible']})
        self.fabIds = [self.textBg, self.textbox]
