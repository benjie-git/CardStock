# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
This module contains the StackManager class which manages painting, editing, and
interacting with the stack.
This class is very central to CardStock, and right now, probably contains a bit more than it should.  :)
"""


import wx
from wx.lib.docview import CommandProcessor
from time import time
import json
from tools import *
from appCommands import *
import generator
import findEngineDesigner
import resourcePathManager
import analyzer
from stackModel import StackModel
from uiCard import UiCard, UiView, CardModel
from uiButton import UiButton
from uiTextField import UiTextField
from uiTextLabel import UiTextLabel
from uiImage import UiImage, ImageModel
from uiWebView import UiWebView
from uiShape import UiShape
from uiGroup import UiGroup, GroupModel
from codeRunnerThread import RunOnMainSync, RunOnMainAsync
import mediaSearchDialogs
import flippedGCDC

# ----------------------------------------------------------------------

class DeferredRefreshWindow(wx.Window):
    """
    This wx.Window subclass allows deferring Refresh() calls.  When this feature is enabled, it flags
    when a Refresh() has been requested, but doesn't call wx.Window.Refresh() until receiving a
    RefreshIfNeeded() call.
    This class also helps with flipping the vertical coordinate axis of the stack, by using bottom-left corner as the
    origin, and making upwards==positive, on all calls to ScreenToClient(), which is used to wrap all
    event.GetPosition() calls throughout the code.
    """
    def __init__(self, stackManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stackManager = stackManager
        self.needsRefresh = False
        self.deferredRefresh = False
        self.didResize = False

    def UseDeferredRefresh(self, deferred):
        self.deferredRefresh = deferred

    def Refresh(self, eraseBackground=True, rect=None):
        if not self.deferredRefresh:
            super().Refresh(eraseBackground)
        else:
            self.needsRefresh = True

    def Update(self):
        if not self.deferredRefresh:
            super().Update()

    @RunOnMainAsync
    def RefreshIfNeeded(self):
        if self.didResize:
            self.stackManager.RepositionViews()
            self.didResize = False
        if self.needsRefresh:
            self.needsRefresh = False
            super().Refresh(True, None)
            super().Update()

    def ScreenToClient(self, *args, **kwargs):
        """
        Vertically flip the mouse position / input to the stack view, so the origin is the bottom-left corner.
        """
        return self.stackManager.ConvPoint(super().ScreenToClient(*args, **kwargs), conv_ToDIP=True)


class StackManager(object):
    def __init__(self, parentView, isEditing):
        super().__init__()
        self.view = DeferredRefreshWindow(self, parentView, style=wx.WANTS_CHARS)
        self.listeners = []
        self.designer = None
        self.isEditing = isEditing
        self.command_processor = CommandProcessor()
        self.timer = None
        self.timerCount = 0
        self.tool = None
        self.globalCursor = None
        self.lastMousePos = wx.Point(0,0)
        self.lastFocusedTextField = None
        self.lastMouseMovedUiView = None
        self.isDoubleClick = False
        self.inlineEditingView = None
        self.runner = None
        self.filename = None
        self.resPathMan = resourcePathManager.ResourcePathManager(self)
        self.lastOnPeriodicTime = None
        self.lastMouseDownView = None

        self.analyzer = analyzer.CodeAnalyzer(self)
        self.stackModel = StackModel(self)
        self.stackModel.AppendCardModel(CardModel(self))

        self.lastVarUpdateTime = 0
        self.varUpdateTimer = wx.Timer()
        self.varUpdateTimer.Bind(wx.EVT_TIMER, self.OnUpdateVarsTimer)

        self.selectedViews = []
        self.modelToViewMap = {}
        self.cardIndex = None

        # This is the only UiCard in the designer or viewer.  It gets re-set-up with each card model, one at a time.
        self.uiCard = None
        self.uiCard = UiCard(None, self, self.stackModel.childModels[0])
        self.uiStack = UiView(None, self, self.stackModel, None)

        self.uiCard.model.SetDirty(False)
        self.command_processor.ClearCommands()

        if wx.Platform != '__WXMAC__':
            # Skip double-buffering on Mac, as it's much faster without it, and looks great
            self.buffer = None

        if not self.isEditing:
            self.timer = wx.Timer(self.view)
            self.view.Bind(wx.EVT_TIMER, self.OnPeriodicTimer, self.timer)
            self.timer.Start(15 if wx.Platform != "__WXMSW__" else 11)

        self.view.Bind(wx.EVT_SIZE, self.OnResize)
        self.view.Bind(wx.EVT_PAINT, self.OnPaint)
        self.view.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.view.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseExit)
        self.view.Bind(wx.EVT_KILL_FOCUS, self.OnLoseFocus)

    def SetDown(self):
        self.view.Unbind(wx.EVT_SIZE, handler=self.OnResize)
        self.view.Unbind(wx.EVT_PAINT, handler=self.OnPaint)
        self.view.Unbind(wx.EVT_ERASE_BACKGROUND, handler=self.OnEraseBackground)
        self.view.Unbind(wx.EVT_LEAVE_WINDOW, handler=self.OnMouseExit)

        if self.timer:
            self.timer.Stop()
        self.timer = None

        if self.runner:
            self.runner.CleanupFromRun()

        self.uiCard.SetDown()
        self.uiCard = None
        self.stackModel.SetDown()
        self.stackModel.DismantleChildTree()
        self.stackModel = None
        self.listeners = None
        self.designer = None
        self.command_processor.ClearCommands()
        self.command_processor = None
        self.tool = None
        self.lastFocusedTextField = None
        self.lastMouseMovedUiView = None
        self.lastMouseDownView = None
        self.inlineEditingView = None
        self.runner = None
        self.resPathMan = None
        self.lastOnPeriodicTime = None
        self.varUpdateTimer.Stop()
        self.analyzer.SetDown()
        self.analyzer = None
        self.selectedViews = None
        self.modelToViewMap = None
        self.view.stackManager = None
        self.view = None

    def UpdateCursor(self):
        if self.tool:
            self.globalCursor = self.tool.GetCursor()
        else:
            self.globalCursor = None

        allUiViews = self.uiCard.GetAllUiViews()
        if self.globalCursor:
            cur = wx.Cursor(self.globalCursor)
            self.view.SetCursor(cur)
            for uiView in allUiViews:
                if uiView.view:
                    uiView.view.SetCursor(cur)
        else:
            cursor = wx.CURSOR_ARROW
            self.view.SetCursor(wx.Cursor(cursor))
            for uiView in allUiViews:
                viewCursor = uiView.GetCursor()
                if uiView.view:
                    uiView.view.SetCursor(wx.Cursor(viewCursor if viewCursor else cursor))

    def OnPeriodicTimer(self, event):
        if not self.runner.stopRunnerThread:
            didRun = False
            self.timerCount += 1
            # Determine elapsed time since last round of on_periodic calls
            now = time()
            if not self.lastOnPeriodicTime:
                self.lastOnPeriodicTime = self.runner.stackStartTime
            elapsed_time = now - self.lastOnPeriodicTime

            # Run animations at 60 Hz / FPS
            allUi = self.uiCard.GetAllUiViews()
            onFinishedCalls = []
            if self.uiCard.RunAnimations(onFinishedCalls, elapsed_time):
                didRun = True
            for ui in allUi:
                if ui.RunAnimations(onFinishedCalls, elapsed_time):
                    didRun = True
            # Let all animations process, before running their on_finished handlers,
            # which could start new animations.
            for c in onFinishedCalls:
                c()
            self.lastOnPeriodicTime = now

            # Check for all collisions
            collisions = {}
            for ui in allUi:
                ui.FindCollisions(collisions)

            # Perform any bounces
            for (k,v) in collisions.items():
                v[0].PerformBounce(v, elapsed_time)
                didRun = True

            # Run on_periodic at 30 Hz
            if self.timerCount % 2 == 0 and self.runner.numOnPeriodicsQueued == 0:
                if self.uiCard.OnPeriodic(event):
                    didRun = True

            if didRun:
                self.runner.EnqueueRefresh()
                if self.runner.shouldUpdateVars:
                    self.UpdateVars()
            else:
                self.view.RefreshIfNeeded()

    def SetTool(self, tool):
        if self.tool:
            self.tool.Deactivate()
        self.tool = tool
        if self.tool:
            self.tool.Activate()
        self.view.Refresh()
        self.UpdateCursor()

    def OnLoseFocus(self, event):
        if self.runner:
            self.runner.ClearPressedKeys()

    def ClearAllViews(self):
        self.SelectUiView(None)

        def DelFromMap(ui):
            if ui.model.type != "card":
                del self.modelToViewMap[ui.model]
            if ui.model.type in ["card", "group"]:
                for childUi in ui.uiViews:
                    DelFromMap(childUi)
        DelFromMap(self.uiCard)

        self.uiCard.RemoveUiViews()

    def CreateViews(self, cardModel):
        self.uiCard.SetModel(cardModel)
        self.AddUiViewsFromModels(cardModel.childModels, canUndo=False)  # Don't allow undoing card loads

    def SetStackModel(self, model, skipSetDown=False):
        if model == self.stackModel:
            return
        self.ClearAllViews()
        if not skipSetDown:
            self.stackModel.SetDown()
        model.SetStackManager(self)
        self.stackModel = model
        self.uiStack = UiView(None, self, self.stackModel, None)
        self.cardIndex = None
        if self.isEditing:
            wx.CallAfter(self.analyzer.RunAnalysis)
            self.uiCard.ResizeCardView(self.uiCard.model.GetProperty("size"))
        if not skipSetDown:
            self.command_processor.ClearCommands()
            self.stackModel.SetDirty(False)
        self.UpdateCursor()

    @RunOnMainSync
    def LoadCardAtIndex(self, index, reload=False):
        if index != self.cardIndex or reload == True:
            if not self.isEditing and self.cardIndex is not None and not reload:
                oldCardModel = self.stackModel.childModels[self.cardIndex]
                if not self.isEditing:
                    self.runner.RunHandler(oldCardModel, "on_hide_card", None)
            self.cardIndex = index
            if self.designer:
                self.designer.Freeze()
            self.ClearAllViews()
            self.lastFocusedTextField = None
            self.lastMouseMovedUiView = None
            if index is not None:
                cardModel = self.stackModel.GetCardModel(index)
                self.CreateViews(cardModel)
                self.SelectUiView(self.uiCard)
                if self.designer:
                    self.designer.UpdateCardList()
                if self.runner:
                    self.runner.SetupForCard(cardModel)
                    if not self.isEditing and not reload:
                        if self.uiCard.model.GetHandler("on_show_card"):
                            self.runner.RunHandler(self.uiCard.model, "on_show_card", None)
                        if self.uiCard.model.GetProperty("can_resize"):
                            self.runner.RunHandler(self.uiCard.model, "on_resize", None, True)
                if self.designer:
                    self.designer.SetFrameSizeFromModel()
                else:
                    self.runner.viewer.SetupViewerSize()
                self.view.Refresh()
            if self.designer:
                self.designer.Thaw()

    def SetDesigner(self, designer):
        self.designer = designer

    def CopyModels(self, models):
        clipData = wx.CustomDataObject("org.cardstock.models")
        list = [model.GetData() for model in models]
        data = bytes(json.dumps(list).encode('utf8'))
        clipData.SetData(data)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipData)
        wx.TheClipboard.Close()

    def Copy(self):
        # Re-order self.selectedViews to be lowest z-order first, so when pasted, they will end up in the right order
        models = [ui.model for ui in self.uiCard.GetAllUiViews() if ui in self.selectedViews]
        if len(self.selectedViews) == 1 and self.selectedViews[0].model.type == "card":
            models = [self.uiCard.model]
        self.CopyModels(models)

    def SelectAll(self):
        self.SelectUiView(None)
        for ui in self.uiCard.uiViews:
            self.SelectUiView(ui, True)

    def DeleteModels(self, models, canUndo=True):
        if len(models) == 1 and models[0].type == "card":
            self.RemoveCard()
        elif len(models) > 0:
            models = [ui.model for ui in self.uiCard.GetAllUiViews() if ui.model in models]
            deleteModels = [m for m in models if m.parent.type != "group"]
            command = RemoveUiViewsCommand(True, "Cut", self, self.cardIndex, deleteModels)
            self.command_processor.Submit(command, storeIt=canUndo)

    def CutModels(self, models, canUndo=True):
        self.CopyModels(models)
        self.DeleteModels(models, canUndo)

    def Cut(self, canUndo=True):
        # Re-order self.selectedViews to be lowest z-order first, so when pasted, they will end up in the right order
        models = [ui.model for ui in self.uiCard.GetAllUiViews() if ui in self.selectedViews]
        if len(self.selectedViews) == 1 and self.selectedViews[0].model.type == "card":
            models = [self.uiCard.model]
        self.CutModels(models, canUndo)

    def Delete(self, canUndo=True):
        models = [ui.model for ui in self.selectedViews]
        if len(self.selectedViews) == 1 and self.selectedViews[0].model.type == "card":
            models = [self.uiCard.model]
        if len(models):
            self.DeleteModels(models, canUndo)

    def Paste(self, canUndo=True):
        models = []
        if not wx.TheClipboard.IsOpened():  # may crash, otherwise
            if wx.TheClipboard.Open():
                if wx.TheClipboard.IsSupported(wx.DataFormat("org.cardstock.models")):
                    clipData = wx.CustomDataObject("org.cardstock.models")
                    if wx.TheClipboard.GetData(clipData):
                        rawData = clipData.GetData()
                        wx.TheClipboard.Close()
                        s = rawData.tobytes().decode('utf8')
                        list = json.loads(s)
                        models = [generator.StackGenerator.ModelFromData(self, dict) for dict in list]
                        if len(models) == 1 and models[0].type == "card":
                            models[0].SetProperty("name", models[0].DeduplicateName(models[0].GetProperty("name"),
                                                                                    [m.GetProperty("name") for m in
                                                                                     self.stackModel.childModels]))
                            command = AddNewUiViewCommand(True, "Paste Card", self, self.cardIndex + 1, "card", models[0])
                            self.command_processor.Submit(command, storeIt=canUndo)
                        else:
                            self.uiCard.model.DeduplicateNamesForModels(models)
                            command = AddUiViewsCommand(True, 'Add Views', self, self.cardIndex, models)
                            self.command_processor.Submit(command, storeIt=canUndo)
                elif wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_BITMAP)):
                    clipData = wx.CustomDataObject(wx.DataFormat(wx.DF_BITMAP))
                    if wx.TheClipboard.GetData(clipData):
                        rawData = clipData.GetData()
                        wx.TheClipboard.Close()
                        if rawData:
                            if not self.filename:
                                r = wx.MessageDialog(self.designer,
                                                     "You need to save this stack before pasting an Image.",
                                                     "Save now?", wx.OK | wx.CANCEL).ShowModal()
                                if r == wx.ID_CANCEL:
                                    return []
                                elif r == wx.ID_OK:
                                    self.designer.OnMenuSave(None)
                                    if not self.filename:
                                        return []
                            path = mediaSearchDialogs.ImageSearchDialog.SaveImageData(self.designer,
                                                                                      self.designer.GetCurDir(),
                                                                                      "image", rawData)
                            if path:
                                self.AddImageFromPath(path)
                else:
                    wx.TheClipboard.Close()
        return models

    def GroupSelectedViews(self):
        models = []
        for ui in self.uiCard.uiViews:
            if ui.isSelected:
                models.append(ui.model)
        if len(models) >= 2:
            command = GroupUiViewsCommand(True, 'Group Views', self, self.cardIndex, models)
            self.command_processor.Submit(command)

    def UngroupSelectedViews(self):
        models = []
        for ui in self.uiCard.uiViews:
            if ui.isSelected and ui.model.type == "group":
                models.append(ui.model)
        if len(models) >= 1:
            command = UngroupUiViewsCommand(True, 'Ungroup Views', self, self.cardIndex, models)
            self.command_processor.Submit(command)

    def AlignOrDistributeSelectedViews(self, doAlign, dirStr):
        if len(self.selectedViews) < 2:
            return
        for ui in self.selectedViews:
            if ui == self.uiCard or ui.model.parent.type == "group":
                return

        def getAlignPos(model, dir):
            if dir == "Left": return model.GetAbsoluteFrame().Left
            if dir == "HCenter": return model.GetCenter()[0]
            if dir == "Right": return model.GetAbsoluteFrame().Right
            if dir == "Top": return model.GetAbsoluteFrame().Bottom  # Bottom and Top are switched since we use positive y axis pointing up
            if dir == "VCenter": return model.GetCenter()[1]
            if dir == "Bottom": return model.GetAbsoluteFrame().Top  # Bottom and Top are switched since we use positive y axis pointing up

        def setAlignPos(model, val, dir):
            rect = model.GetAbsoluteFrame()
            pos = wx.Point(tuple(int(x) for x in model.GetProperty("position")))
            if dir == "Left": pos.x += int(val - rect.Left)
            if dir == "HCenter": pos.x += int(val - (rect.Left + (rect.Right - rect.Left)/2))
            if dir == "Right": pos.x += int(val - rect.Right)
            # Bottom and Top are switched since we use positive y axis pointing up
            if dir == "Top": pos.y += int(val - rect.Bottom)
            if dir == "VCenter": pos.y += int(val - (rect.Top + (rect.Bottom - rect.Top)/2))
            if dir == "Bottom": pos.y += int(val - rect.Top)
            return SetPropertyCommand(True, "Set Property", self.designer.cPanel, self.cardIndex,
                                      model, "position", pos)

        models = [ui.model for ui in self.selectedViews]

        if doAlign:
            posList = [getAlignPos(m, dirStr) for m in models]
            sharedPos = round(sum(posList)/len(posList))
            commands = []
            for m in models:
                commands.append(setAlignPos(m, sharedPos, dirStr))
            cmdGroup = CommandGroup(True, "Align", self, commands, models)
            self.command_processor.Submit(cmdGroup)
        elif "Spacing" not in dirStr:
            # Distribute objects
            ordered = sorted([(getAlignPos(m, dirStr), m) for m in models], key=lambda l: l[0])
            first = ordered[0][0]
            last = ordered[-1][0]
            num = len(ordered)
            offset = 0
            commands = []
            for (pos, model) in ordered[1:-1]:  # No need to distribute the first and last
                offset += (last - first) / (num - 1)
                commands.append(setAlignPos(model, int(first + offset), dirStr))
            if len(commands):
                cmdGroup = CommandGroup(True, "Distribute", self, commands, models)
                self.command_processor.Submit(cmdGroup)
        else:
            # Distribute object spacing
            d = "HCenter" if dirStr=="HSpacing" else "VCenter"
            ordered = sorted([(getAlignPos(m, d), m) for m in models], key=lambda l: l[0])
            ordered = [pair[1] for pair in ordered]
            if dirStr == "HSpacing":
                start = ordered[0].GetAbsoluteFrame().Right
                end = ordered[-1].GetAbsoluteFrame().Left
            else:
                start = ordered[0].GetAbsoluteFrame().Bottom
                end = ordered[-1].GetAbsoluteFrame().Top
            total = end-start
            for model in ordered[1:-1]:  # No need to distribute the first and last
                s = model.GetProperty("size")
                total -= s.Width if dirStr=="HSpacing" else s.Height
            spacing = total/(len(models)-1)
            last = start
            commands = []
            d = "Left" if dirStr=="HSpacing" else "Bottom"
            for model in ordered[1:-1]:  # No need to distribute the first and last
                commands.append(setAlignPos(model, int(last + spacing), d))
                if dirStr == "HSpacing":
                    last += spacing + model.GetProperty("size").Width
                else:
                    last += spacing + model.GetProperty("size").Height
            if len(commands):
                cmdGroup = CommandGroup(True, "Distribute", self, commands, models)
                self.command_processor.Submit(cmdGroup)

    def FlipSelection(self, flipHorizontal):
        commands = []
        for ui in self.selectedViews:
            commands.append(FlipShapeCommand(True, 'Flip object', self, self.cardIndex,
                                                   ui.model, flipHorizontal, not flipHorizontal))
        if len(commands) >= 1:
            command = CommandGroup(True, 'Flip Objects', self, commands, [ui.model for ui in self.selectedViews])
            self.command_processor.Submit(command)

    def GroupModelsInternal(self, models, group=None, name=None):
        """ Groups both the models and uiView objects, so while running, call this within a @RunOnMainSync. """
        if len(models) > 1:
            card = models[0].GetCard()
            if not group:
                group = GroupModel(self)
                if not name:
                    name = "group"
                group.SetProperty("name", card.GetNextAvailableNameInCard(name), notify=False)
            else:
                group.SetBackUp(self)
            validModels = []
            proxies = {}
            for m in models:
                if m.GetCard() == card:
                    validModels.append(m)
                    if m.proxy:
                        proxies[m] = m.proxy
                    self.RemoveUiViewByModel(m)
                    m.SetBackUp(self)
            group.AddChildModels(validModels)
            if card == self.uiCard.model:
                self.AddUiViewsFromModels([group], False)
            else:
                card.AddChild(group)
            for m, p in proxies.items():
                p._model = m
                m.proxy = p
        return group

    def UngroupModelsInternal(self, groups):
        """ Ungroups both the models and uiView objects, so while running, call this within a @RunOnMainSync. """
        modelSets = []
        if len(groups) > 0:
            self.SelectUiView(None)
            for group in groups:
                childModels = []
                modelSets.append(childModels)
                proxies = {}
                for child in group.childModels.copy():
                    childModels.append(child)
                    if child.proxy:
                        proxies[child] = child.proxy
                    group.RemoveChild(child)
                    child.SetBackUp(self)
                if group.GetCard() == self.uiCard.model:
                    self.RemoveUiViewByModel(group)
                    self.AddUiViewsFromModels(childModels, False)
                else:
                    p = group.parent
                    p.RemoveChild(group)
                    for child in childModels:
                        p.AddChild(child)
                for m,p in proxies.items():
                    p._model = m
                    m.proxy = p

        return modelSets

    def AddUiViewInternal(self, model):
        """ Only used while editing / in the designer. """
        uiView = None
        objType = model.type

        if objType == "button":
            uiView = UiButton(self.uiCard, self, model)
        elif objType == "textfield" or objType == "field":
            uiView = UiTextField(self.uiCard, self, model)
        elif objType == "textlabel" or objType == "label":
            uiView = UiTextLabel(self.uiCard, self, model)
        elif objType == "image":
            uiView = UiImage(self.uiCard, self, model)
        elif objType == "webview":
            uiView = UiWebView(self.uiCard, self, model)
        elif objType == "group":
            uiView = UiGroup(self.uiCard, self, model)
        elif objType in ["pen", "line", "oval", "rect", "polygon", "roundrect"]:
            uiView = UiShape(self.uiCard, self, model)

        if not model.GetCard():
            uiView.model.SetProperty("name", self.uiCard.model.DeduplicateNameInCard(
                uiView.model.GetProperty("name"), exclude=[]), notify=False)

        def AddToMap(ui):
            self.modelToViewMap[ui.model] = ui
            if ui.model.type == "group":
                for childUi in ui.uiViews:
                    AddToMap(childUi)
        AddToMap(uiView)

        if uiView:
            self.uiCard.uiViews.append(uiView)

            if uiView.model not in self.uiCard.model.childModels:
                self.uiCard.model.AddChild(uiView.model)

            if self.globalCursor:
                if uiView.view:
                    uiView.view.SetCursor(wx.Cursor(self.globalCursor))
            self.view.Refresh()
        return uiView

    def AddUiViewsFromModels(self, models, canUndo=True):
        """
        Adds views for the given models, and adds the models as children of the current card model
        if they're not already somewhere in the stack's model tree.  To split model changes from view changes,
        just add the model to the stack before calling this, and then this method will only make changes to the views.
        """
        models = [m for m in models if not m.didSetDown]
        self.uiCard.model.DeduplicateNamesForModels(models)
        command = AddUiViewsCommand(True, 'Add Views', self, self.cardIndex, models)

        if canUndo:
            self.command_processor.Submit(command)
        else:
            # Don't mess with the Undo queue when we're just building a pgae
            command.Do()

        uiViews = self.uiCard.uiViews[-len(models):]

        if self.globalCursor:
            for uiView in uiViews:
                if uiView.view:
                    uiView.view.SetCursor(wx.Cursor(self.globalCursor))

        return uiViews

    def AddImageFromPath(self, path):
        im = ImageModel(self)
        im.SetProperty("file", path)
        im.SetProperty("size", (200,200))
        im.SetProperty("center", self.uiCard.model.GetProperty("center"))
        self.AddUiViewsFromModels([im], True)

    def GetSelectedUiViews(self):
        return self.selectedViews.copy()

    def SelectUiView(self, uiView, extend=False):
        if self.isEditing:
            selectStack = False
            if uiView == self.uiStack:
                selectStack = True
                uiView = None

            if extend and uiView and uiView.parent and uiView.parent.model.type == "group":
                extend = False
            if extend and len(self.selectedViews) and self.selectedViews[0].parent and self.selectedViews[0].parent.model.type == "group":
                extend = False
            if extend and uiView and ((uiView.model.type == "card") != (len(self.selectedViews) and self.selectedViews[0].model.type == "card")):
                extend = False
            if len(self.selectedViews) and not extend:
                for ui in self.selectedViews:
                    ui.SetSelected(False)
                self.selectedViews = []
            if uiView:
                if extend and uiView in self.selectedViews:
                    uiView.SetSelected(False)
                    self.selectedViews.remove(uiView)
                else:
                    uiView.SetSelected(True)
                    self.selectedViews.append(uiView)
            if self.designer:
                self.designer.SetSelectedUiViews(self.selectedViews)

            if selectStack:
                self.designer.cPanel.UpdateForUiViews([self.uiStack])

    @RunOnMainAsync
    def OnPropertyChanged(self, model, key):
        uiView = self.GetUiViewByModel(model)
        if model.type == "card" and key == "size":
            s = model.GetProperty(key)
            if self.designer:
                self.uiCard.ResizeCardView(s)
            else:
                self.view.GetTopLevelParent().SetClientSize(self.view.FromDIP(s))
        if uiView:
            uiView.OnPropertyChanged(model, key)
        if uiView and self.designer:
            self.designer.cPanel.UpdatedProperty(uiView, key)

    def GetUiViewByModel(self, model):
        if not self.uiCard:
            return None
        if model == self.stackModel:
            return self.uiStack
        if model == self.uiCard.model:
            return self.uiCard
        if model in self.modelToViewMap:
            return self.modelToViewMap[model]
        return None

    def GetUiViewByName(self, name):
        if self.uiCard.model.properties["name"] == name:
            return self.uiCard
        for ui in self.uiCard.GetAllUiViews():
            if ui.model.properties["name"] == name:
                return ui
        return None

    def RemoveUiViewByModel(self, viewModel):
        """
        Removes views for the given models, and removes the models from the stack if they're still in the stack tree.
        To split model changes from view changes, just remove the model from the stack before calling this, and then
        this method will only make changes to the views.
        """
        ui = self.GetUiViewByModel(viewModel)
        if ui:
            if ui in self.selectedViews:
                self.SelectUiView(ui, True)

            def DelFromMap(ui):
                del self.modelToViewMap[ui.model]
                if ui.model.type == "group":
                    for childUi in ui.uiViews:
                        DelFromMap(childUi)
            DelFromMap(ui)

            self.uiCard.uiViews.remove(ui)
            if ui.model.parent:
                self.uiCard.model.RemoveChild(ui.model)
            ui.SetDown()
            self.view.Refresh()
        else:
            if viewModel.parent:
                viewModel.parent.RemoveChild(viewModel)

    def ReorderSelectedViews(self, direction):
        oldIndexes = []
        for ui in self.selectedViews:
            if ui == self.uiCard or ui.model.parent.type == "group":
                return
            oldIndexes.append(self.uiCard.model.childModels.index(ui.model))
        oldIndexes.sort()

        if len(oldIndexes):
            firstIndex = oldIndexes[0]
            newIndexes = []
            for i in range(0, len(oldIndexes)):
                newIndex = 0
                if direction == "end":
                    newIndex = 0 + i
                elif direction == "fwd":
                    newIndex = firstIndex + 1 + i
                elif direction == "back":
                    newIndex = firstIndex - 1 + i
                elif direction == "front":
                    newIndex = len(self.uiCard.model.childModels) - len(oldIndexes) + i
                if newIndex < 0 or newIndex >= len(self.uiCard.model.childModels):
                    return
                newIndexes.append(newIndex)

            command = ReorderUiViewsCommand(True, "Reorder Views", self, self.cardIndex, oldIndexes, newIndexes)
            self.command_processor.Submit(command)

    def ReorderCurrentCard(self, direction):
        currentIndex = self.cardIndex
        newIndex = None
        if direction == "fwd": newIndex = currentIndex + 1
        elif direction == "back": newIndex = currentIndex - 1

        if newIndex < 0: newIndex = 0
        if newIndex >= len(self.stackModel.childModels): newIndex = len(self.stackModel.childModels) - 1

        if newIndex != currentIndex:
            command = ReorderCardCommand(True, "Reorder Card", self, self.cardIndex, newIndex)
            self.command_processor.Submit(command)

    def AddCard(self):
        newCard = CardModel(self)
        newCard.SetProperty("name", newCard.DeduplicateName("card_1",
                                                            [m.GetProperty("name") for m in self.stackModel.childModels]))
        newCard.SetProperty("size", self.uiCard.model.GetProperty("size"))
        newCard.SetProperty("can_resize", self.uiCard.model.GetProperty("can_resize"))
        command = AddNewUiViewCommand(True, "Add Card", self, self.cardIndex+1, "card", newCard)
        self.command_processor.Submit(command)

    def DuplicateCard(self, card=None):
        newCard = CardModel(self)
        if not card:
            card = self.stackModel.childModels[self.cardIndex]
        newCard.SetData(card.GetData())
        newCard.SetProperty("name", newCard.DeduplicateName(newCard.GetProperty("name"),
                                                            [m.GetProperty("name") for m in self.stackModel.childModels]))
        command = AddNewUiViewCommand(True, "Duplicate Card", self, self.cardIndex+1, "card", newCard)
        self.command_processor.Submit(command)
        return newCard

    def RemoveCard(self):
        index = self.cardIndex
        if len(self.stackModel.childModels) > 1:
            command = RemoveUiViewsCommand(True, "Remove Card", self, index, [self.stackModel.childModels[index]])
            self.command_processor.Submit(command)

    def RemoveCardRaw(self, cardModel):
        index = self.stackModel.childModels.index(cardModel)
        self.stackModel.RemoveCardModel(cardModel)
        if index == self.cardIndex:
            if index == len(self.stackModel.childModels):
                index = len(self.stackModel.childModels) - 1
            self.LoadCardAtIndex(None, reload=True)
            if index >= 0:
                self.LoadCardAtIndex(index)

    def OnRightDown(self, uiView, event):
        if self.isEditing:
            pos = self.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
            uiView = self.HitTest(pos)
            if uiView.parent and uiView.parent.isSelected:
                uiView = uiView.parent
            if not uiView.isSelected:
                self.SelectUiView(uiView)
            menu = self.designer.MakeContextMenu(self.selectedViews)
            self.designer.PopupMenu(menu, self.designer.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition())))

    def OnMouseDown(self, uiView, event):
        if self.view.HasCapture() and event.LeftDClick():
            # Make sure we don't double-capture the mouse on GTK/Linux
            event.Skip()
            if uiView and uiView.model.type.startswith("text") and event.LeftDClick():
                # Flag this is a double-click  On mouseUp, we'll start the inline editor.
                self.isDoubleClick = True
            if self.tool.name != "polygon" or wx.Platform == "__WXGTK__":
                return

        pos = self.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
        if self.isEditing:
            if uiView == self.uiCard and (pos.y < 0 or pos.x > self.uiCard.model.GetProperty("size").width):
                # Don't select card when a click starts outside of the card.
                self.SelectUiView(None)
                uiViews = []
            else:
                uiView = self.HitTest(pos, not event.ShiftDown())
                uiViews = [uiView] if uiView else None
        else:
            uiViews = self.HitTestAll(pos)

        if self.inlineEditingView:
            if uiViews and uiViews[0] == self.inlineEditingView:
                # Let the inline editor handle clicks while it's enabled
                event.Skip()
                return
            else:
                self.inlineEditingView.StopInlineEditing()

        if self.isEditing:
            if uiViews and uiViews[0].model.type.startswith("text") and event.LeftDClick():
                # Flag this is a double-click  On mouseUp, we'll start the inline editor.
                self.isDoubleClick = True
            else:
                # We need to pass in a view, even when click starts outside the card
                self.tool.OnMouseDown(uiViews[0] if uiViews else self.uiCard, event)
        else:
            self.lastMouseDownView = uiViews[0]
            self.runner.ResetStopHandlingMouseEvent()
            for uiView in uiViews:
                uiView.OnMouseDown(event)
            event.Skip()

    def OnMouseMove(self, uiView, event):
        if not event.GetEventObject().GetTopLevelParent():
            # In case the uiView went away already
            return

        pos = self.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
        if pos == self.lastMousePos:
            event.Skip()
            return

        if self.isEditing:
            uiView = self.HitTest(pos, not wx.KeyboardState().ShiftDown())
            uiViews = [uiView] if uiView else None
            self.designer.UpdateStatusBar(uiView, pos)
        else:
            uiViews = self.HitTestAll(pos)

        if uiViews and uiViews[0] != self.lastMouseMovedUiView:
            if not self.globalCursor:
                if uiViews and uiViews[0].GetCursor():
                    self.view.SetCursor(wx.Cursor(uiViews[0].GetCursor()))
                else:
                    self.view.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

        if self.inlineEditingView:
            # Let the inline editor handle clicks while it's enabled
            event.Skip()
            return

        if self.isEditing:
            if self.tool:
                self.tool.OnMouseMove(uiViews[0], event)
        else:
            if uiViews[0] != self.lastMouseMovedUiView:
                if self.lastMouseMovedUiView:
                    self.lastMouseMovedUiView.OnMouseExit(event)
                if uiViews[0]:
                    uiViews[0].OnMouseEnter(event)
            self.runner.ResetStopHandlingMouseEvent()
            for uiView in uiViews:
                uiView.OnMouseMove(event)
            event.Skip()
        self.lastMouseMovedUiView = uiViews[0]
        self.lastMousePos = pos

    def OnMouseUp(self, uiView, event):
        if not event.GetEventObject().GetTopLevelParent():
            # In case the uiView went away already
            return

        pos = self.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
        if self.isEditing:
            uiView = self.HitTest(pos, not event.ShiftDown())
            uiViews = [uiView] if uiView else None
        else:
            uiViews = self.HitTestAll(pos)

        if self.inlineEditingView:
            # Let the inline editor handle clicks while it's enabled
            event.Skip()
            return

        if self.tool and self.isEditing:
            self.tool.OnMouseUp(uiViews[0], event)
            if uiViews and uiViews[0].model and uiViews[0].model.type.startswith("text") and self.isDoubleClick:
                # Fire it up!
                uiViews[0].StartInlineEditing()
                event.Skip()
        else:
            if self.lastMouseDownView:
                if self.lastMouseDownView != uiViews[0]:
                    self.lastMouseDownView.OnMouseUpOutside(event)
                self.lastMouseDownView = None
            self.runner.ResetStopHandlingMouseEvent()
            for uiView in uiViews:
                uiView.OnMouseUp(event)
            event.Skip()
        self.isDoubleClick = False

    def OnMouseExit(self, event):
        if self.lastMouseMovedUiView:
            self.lastMouseMovedUiView.OnMouseExit(event)
        self.lastMouseMovedUiView = None
        if self.isEditing:
            self.designer.UpdateStatusBar(None, None)

    def RepositionViews(self):
        for uiView in self.uiCard.GetAllUiViews():
            if uiView.view:
                # Make sure native subview positions get adjusted based on the new origin
                uiView.OnPropertyChanged(uiView.model, "position")

    def OnResize(self, event):
        if self.uiCard.model not in self.stackModel.childModels:
            return
        if not self.uiCard.model.parent:
            return # Not fully set up yet
        self.UpdateBuffer()
        event.Skip()

    def ConvPoint(self, pt, conv_ToDIP=False):
        """
        Vertically flip the stack view, so the origin is the bottom-left corner.
        """
        height = self.view.GetSize().Height

        if wx.Platform == '__WXMSW__':
            if conv_ToDIP:
                return self.view.ToDIP(wx.Point(int(pt[0]), int(height - pt[1])))
            else:
                return self.view.FromDIP(wx.Point(int(pt[0]), int(self.view.ToDIP(height) - pt[1])))
        else:
            return wx.Point(int(pt[0]), int(height - pt[1]))

    def ConvRect(self, rect):
        """
        Vertically flip the stack view, so the origin is the bottom-left corner.
        """
        if rect:
            height = self.view.GetSize().Height
            bl = rect.BottomLeft
            if wx.Platform == '__WXMSW__':
                return wx.Rect(self.view.FromDIP(wx.Point(bl[0], self.view.ToDIP(height) - bl[1])), self.view.FromDIP(rect.Size))
            else:
                return wx.Rect(wx.Point(bl[0], height - bl[1]), rect.Size)
        return None

    def UpdateBuffer(self):
        if wx.Platform != '__WXMAC__':
            self.buffer = wx.Bitmap.FromRGBA(self.view.GetSize().Width, self.view.GetSize().Height)

    def OnEraseBackground(self, event):
        # No thank you!
        # This event was causing bad flickering on Windows.  Much better now!
        pass

    def OnPaint(self, event):
        if wx.Platform == '__WXMAC__':
            # Skip double-buffering on Mac, as it's much faster without it, and looks great
            dc = wx.PaintDC(self.view)
        else:
            if not self.buffer:
                self.UpdateBuffer()
            dc = wx.MemoryDC(self.buffer)

        gc = flippedGCDC.FlippedGCDC(dc, self)
        gc.cachedGC = gc.GetGraphicsContext()

        self.uiCard.DoPaint(gc)
        if self.isEditing:
            self.uiCard.DoPaintSelectionBoxes(gc)
            if self.tool:
                self.tool.Paint(gc)

        if wx.Platform != '__WXMAC__':
            wx.BufferedPaintDC(self.view, self.buffer)
        del gc.cachedGC

    def HitTest(self, pt, selectedFirst=True):
        # First find selected objects, so you can move a selected object from under another
        # But only if allowed by selectedFirst.
        # We disable selectedFirst searching if the Shift key is down, or if the user does a click
        # as opposed to a drag or resize.
        if selectedFirst:
            for uiView in self.selectedViews:
                if uiView.model.type != "card":
                    hit = uiView.HitTest(pt)
                    if hit and (hit == uiView or hit.HasGroupAncestor(uiView)):
                        return hit
        # Native views first
        for uiView in reversed(self.uiCard.uiViews):
            if uiView.model.IsVisible() and uiView.view:
                hit = uiView.HitTest(pt)
                if hit:
                    return hit
        # Then virtual views
        for uiView in reversed(self.uiCard.uiViews):
            if uiView.model.IsVisible() and not uiView.view:
                hit = uiView.HitTest(pt)
                if hit:
                    return hit
        return self.uiCard

    def HitTestAll(self, pt):
        # Return a list of all views that the given point would touch, all the way down to the card.  Top views first.
        views = []
        allViews = list(reversed(self.uiCard.GetAllUiViews()))
        for uiView in allViews:
            if uiView.model.IsVisible() and uiView.view:
                hit = uiView.HitTest(pt)
                if hit:
                    views.append(uiView)
        # Then virtual views
        for uiView in allViews:
            if uiView.model.IsVisible() and not uiView.view:
                hit = uiView.HitTest(pt)
                if hit:
                    views.append(uiView)
        views.append(self.uiCard)
        return views

    def OnKeyDown(self, uiView, event):
        code = event.GetKeyCode()
        if self.tool and self.isEditing:
            ms = wx.GetMouseState()
            if not ms.LeftIsDown() and not self.inlineEditingView and not event.ControlDown() \
                    and not event.AltDown() and self.view.FindFocus() != self.designer.cPanel.inspector:
                if code == ord('H') or code == wx.WXK_ESCAPE:
                    self.designer.cPanel.SetToolByName("hand")
                elif code == ord('B'):
                    self.designer.cPanel.SetToolByName("button")
                elif code == ord('F'):
                    self.designer.cPanel.SetToolByName("field")
                elif code == ord('T'):
                    self.designer.cPanel.SetToolByName("label")
                elif code == ord('I'):
                    self.designer.cPanel.SetToolByName("image")
                elif code == ord('W'):
                    self.designer.cPanel.SetToolByName("webview")
                elif code == ord('P'):
                    self.designer.cPanel.SetToolByName("pen")
                elif code == ord('O'):
                    self.designer.cPanel.SetToolByName("oval")
                elif code == ord('R'):
                    self.designer.cPanel.SetToolByName("rect")
                elif code == ord('G'):
                    self.designer.cPanel.SetToolByName("polygon")
                elif code == ord('D'):
                    self.designer.cPanel.SetToolByName("roundrect")
                elif code == ord('L'):
                    self.designer.cPanel.SetToolByName("line")
                elif code in [wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER] and event.ShiftDown():
                    selected = self.GetSelectedUiViews()
                    if len(selected) == 1 and selected[0].model.type.startswith("text"):
                        selected[0].StartInlineEditing()
                    else:
                        event.Skip()
                else:
                    event.Skip()
            else:
                event.Skip()

            self.tool.OnKeyDown(uiView, event)
        elif not self.isEditing:
            isNonAutoRepeatKeyDown = self.runner.OnKeyDown(event)
            if isNonAutoRepeatKeyDown:
                self.uiCard.OnKeyDown(event)
            if code == wx.WXK_TAB:
                # Cycle through focusable objects
                views = [ui for ui in self.uiCard.GetAllUiViews() if ui.view]
                if len(views):
                    offset = -1 if event.ShiftDown() else 1  # Backward / Fwd
                    nextView = views[0]
                    if uiView in views:
                        i = views.index(uiView)
                        nextView = views[(i+offset)%len(views)]
                    nextView.view.SetFocus()
            elif uiView.model.type in ["textfield", "button"]:
                event.Skip()

    def OnKeyUp(self, uiView, event):
        if self.tool and self.isEditing:
            self.tool.OnKeyUp(uiView, event)
        else:
            self.runner.OnKeyUp(event)
            self.uiCard.OnKeyUp(event)
            if uiView.model.type == "textfield":
                event.Skip()

    def Undo(self):
        self.command_processor.Undo()
        if not self.command_processor.CanUndo():
            self.stackModel.SetDirty(False)
        self.view.Refresh()

    def Redo(self):
        self.command_processor.Redo()
        self.view.Refresh()

    @RunOnMainAsync
    def UpdateVars(self):
        now = time()
        if now > self.lastVarUpdateTime + 1.0:
            self.OnUpdateVarsTimer()
        else:
            ms = (self.lastVarUpdateTime+1.0 - now)*1000
            if ms < 10: ms = 10
            if self.varUpdateTimer:
                self.varUpdateTimer.StartOnce(int(ms))

    def OnUpdateVarsTimer(self, event=None):
        if self.runner and not self.isEditing:
            self.runner.viewer.UpdateVars()
        self.lastVarUpdateTime = time()

    def ShowStackInfo(self):
        if self.runner and self.runner.viewer:
            self.runner.viewer.OnMenuInfo()

    def GetDesignerFindPath(self):
        cPanel = self.designer.cPanel
        cardModel = self.uiCard.model
        cardIndex = self.stackModel.childModels.index(cardModel)
        uiView = None
        if len(cPanel.lastSelectedUiViews) == 1:
            uiView = cPanel.lastSelectedUiViews[0]
        model = uiView.model if uiView else None

        start, end, text = self.designer.cPanel.GetInspectorSelection()
        if text:
            propName = uiView.model.PropertyKeys()[cPanel.inspector.GetGridCursorRow()]
            return (str(cardIndex) + "." + model.GetProperty("name") + ".property." + propName, (start, end, text))

        if uiView:
            handlerName = cPanel.codeInspector.GetCurrentHandler()
            start, end, text = self.designer.cPanel.codeInspector.GetCodeEditorSelection(handlerName)
            if model and handlerName:
                return (str(cardIndex) + "." + model.GetProperty("name") + ".handler." + handlerName, (start, end, text))

        if not model:
            model = self.uiCard.model
        return (str(cardIndex) + "." + model.GetProperty("name") + ".property." + model.PropertyKeys()[0], (0, 0, ""))

    def ShowDesignerFindPath(self, findPath, selectStart, selectEnd):
        if findPath:
            parts = findPath.split(".")
            # cardIndex, objectName, property|handler, key
            self.designer.cPanel.inspector.EnableCellEditControl(False)
            self.LoadCardAtIndex(int(parts[0]))
            self.SelectUiView(self.GetUiViewByName(parts[1]))
            if parts[2] == "property":
                wx.CallAfter(self.designer.cPanel.SelectInInspectorForPropertyName, parts[3], selectStart, selectEnd)
            elif parts[2] == "handler":
                wx.CallAfter(self.designer.cPanel.codeInspector.SelectAndScrollTo, parts[3], selectStart, selectEnd)

    def GetViewerFindPath(self):
        cardModel = self.uiCard.model
        cardIndex = self.stackModel.childModels.index(cardModel)
        uiViews = self.uiCard.GetAllUiViews()
        uiView = None
        if self.lastFocusedTextField in uiViews:
            uiView = self.lastFocusedTextField
        if not uiView:
            for ui in uiViews:
                if ui.model.type == "textfield" and ui.view.HasFocus():
                    uiView = ui
                    break
        if not uiView:
            for ui in uiViews:
                if ui.model.type == "textfield":
                    uiView = ui
                    break

        if uiView:
            start, end = uiView.view.GetSelection()
            text = uiView.view.GetStringSelection()
            return (str(cardIndex) + "." + uiView.model.GetProperty("name") + ".property.text", (start, end, text))
        return None

    def ShowViewerFindPath(self, findPath, selectStart, selectEnd):
        if findPath:
            cardIndex, objectName, pathType, key = findPath.split(".")
            self.LoadCardAtIndex(int(cardIndex))
            uiView = self.GetUiViewByName(objectName)
            if uiView and uiView.view:
                uiView.view.SetFocus()
                uiView.view.SetSelection(selectStart, selectEnd)
