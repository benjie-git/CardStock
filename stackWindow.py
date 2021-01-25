#!/usr/bin/python
# stackWindow.py

"""
This module contains the StackWindow class which is a window that you
can do simple drawings upon. and add Buttons and TextFields to.
"""


import wx
from wx.lib.docview import CommandProcessor
import json
from tools import *
from commands import *
import generator
from stackModel import StackModel
from uiCard import UiCard, CardModel
from uiButton import UiButton
from uiTextField import UiTextField
from uiTextLabel import UiTextLabel
from uiImage import UiImage
from uiShape import UiShape
from uiGroup import UiGroup, GroupModel


# ----------------------------------------------------------------------

class StackWindow(wx.Window):
    def __init__(self, parent, ID, stackModel):
        wx.Window.__init__(self, parent, ID, style=wx.WANTS_CHARS)
        self.listeners = []
        self.designer = None
        self.isEditing = False  # Is in Editing mode (running from the designer), as opposed to just the viewer
        self.command_processor = CommandProcessor()
        self.noIdling = False
        self.timer = None
        self.tool = None
        self.cacheView = wx.Window(self, size=(0,0))  # just an offscreen holder for cached uiView.views
        self.cacheView.Hide()
        self.uiViewCache = {}
        self.globalCursor = None
        self.lastMousePos = wx.Point(0,0)
        self.runner = None

        if not stackModel:
            stackModel = StackModel(self)
            stackModel.AppendCardModel(CardModel(self))

        self.stackModel = stackModel
        self.selectedViews = []
        self.uiViews = []
        self.cardIndex = None
        self.uiCard = UiCard(None, self, stackModel.cardModels[0])
        self.LoadCardAtIndex(0)

        self.uiCard.model.SetDirty(False)
        self.command_processor.ClearCommands()

        # When the window is destroyed, clean up resources.
        self.Bind(wx.EVT_WINDOW_DESTROY, self.Cleanup)

    def Cleanup(self, evt):
        if evt.GetEventObject() == self:
            if hasattr(self, "menu"):
                self.menu.Destroy()
                del self.menu
            if self.timer:
                self.timer.Stop()

    def RefreshNow(self):
        self.Refresh()
        self.Update()
        self.noIdling = True
        wx.GetApp().Yield()
        self.noIdling = False

    def SetEditing(self, editing):
        self.isEditing = editing
        if not editing:
            self.SelectUiView(None)
            self.timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.OnIdleTimer, self.timer)
            self.timer.Start(33)
        else:
            if self.timer:
                self.timer.Stop()

    def UpdateCursor(self):
        if self.tool:
            self.globalCursor = self.tool.GetCursor()
        else:
            self.globalCursor = None

        allUiViews = self.GetAllUiViews()
        if self.globalCursor:
            self.SetCursor(wx.Cursor(self.globalCursor))
            for uiView in allUiViews:
                uiView.view.SetCursor(wx.Cursor(self.globalCursor))
        else:
            cursor = wx.CURSOR_ARROW
            self.SetCursor(wx.Cursor(cursor))
            for uiView in allUiViews:
                viewCursor = uiView.GetCursor()
                uiView.view.SetCursor(wx.Cursor(viewCursor if viewCursor else cursor))

    def OnIdleTimer(self, event):
        if not self.isEditing and not self.noIdling:
            self.uiCard.OnIdle(event)

    def SetTool(self, tool):
        self.tool = tool
        self.UpdateCursor()

    def ClearAllViews(self):
        self.SelectUiView(None)
        for ui in self.uiViews.copy():
            if ui.model.type != "card":
                self.uiViews.remove(ui)
                ui.view.Reparent(self.cacheView)
                self.uiViewCache[ui.model] = ui

    def CreateViews(self, cardModel):
        self.uiCard.SetModel(cardModel)
        self.uiViews = []
        self.AddUiViewsFromModels(cardModel.childModels, canUndo=False)  # Don't allow undoing card loads

    def GetAllUiViews(self):
        allUiViews = []
        for uiView in self.uiViews:
            allUiViews.append(uiView)
            if uiView.model.type == "group":
                allUiViews.extend(uiView.GetAllUiViews())
        return allUiViews

    def SetStackModel(self, model):
        self.ClearAllViews()
        self.stackModel = model
        self.cardIndex = None
        self.LoadCardAtIndex(0)
        self.SetSize(self.stackModel.GetProperty("size"))
        self.command_processor.ClearCommands()
        self.stackModel.SetDirty(False)
        self.UpdateCursor()

    def LoadCardAtIndex(self, index, reload=False):
        if index != self.cardIndex or reload == True:
            if not self.isEditing and self.cardIndex is not None and not reload:
                oldCardModel = self.stackModel.cardModels[self.cardIndex]
                if self.runner:
                    self.runner.RunHandler(oldCardModel, "OnHideCard", None)
            self.cardIndex = index
            self.ClearAllViews()
            if index is not None:
                cardModel = self.stackModel.GetCardModel(index)
                self.CreateViews(cardModel)
                self.SelectUiView(self.uiCard)
                self.Refresh()
                self.Update()
                if self.designer:
                    self.designer.UpdateCardList()
                if not self.isEditing and self.runner:
                    self.runner.SetupForCurrentCard()
                    self.runner.RunHandler(self.uiCard.model, "OnShowCard", None)
                self.noIdling = True
                wx.GetApp().Yield()
                self.noIdling = False

    def SetDesigner(self, designer):
        self.designer = designer

    def CopyView(self):
        clipData = wx.CustomDataObject("org.cardstock.models")
        list = [ui.model.GetData() for ui in self.selectedViews]
        data = bytes(json.dumps(list).encode('utf8'))
        clipData.SetData(data)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipData)
        wx.TheClipboard.Close()

    def SelectAll(self):
        self.SelectUiView(None)
        for ui in self.uiViews:
            self.SelectUiView(ui, True)

    def CutView(self):
        self.CopyView()
        if len(self.selectedViews) == 1 and self.selectedViews[0].model.type == "card":
            self.RemoveCard()
        elif len(self.selectedViews) > 0:
            deleteViews = [ui for ui in self.selectedViews if ui.model.parent.type != "group"]
            command = RemoveUiViewsCommand(True, "Cut", self, self.cardIndex, [ui.model for ui in deleteViews])
            self.command_processor.Submit(command)

    def PasteView(self):
        if not wx.TheClipboard.IsOpened():  # may crash, otherwise
            if wx.TheClipboard.Open():
                if wx.TheClipboard.IsSupported(wx.DataFormat("org.cardstock.models")):
                    clipData = wx.CustomDataObject("org.cardstock.models")
                    if wx.TheClipboard.GetData(clipData):
                        rawdata = clipData.GetData()
                        list = json.loads(rawdata.tobytes().decode('utf8'))
                        self.SelectUiView(None)
                        models = [generator.StackGenerator.ModelFromData(self.stackView, dict) for dict in list]
                        if len(models) == 1 and models[0].type == "card":
                            models[0].SetProperty("name", models[0].DeduplicateName(models[0].GetProperty("name"),
                                                                            [m.GetProperty("name") for m in
                                                                             self.stackModel.cardModels]))
                            command = AddNewUiViewCommand(True, "Paste Card", self, self.cardIndex + 1, "card", models[0])
                            self.command_processor.Submit(command)
                        else:
                            for model in models:
                                model.SetProperty("name",
                                                  self.uiCard.model.DeduplicateNameInCard(model.GetProperty("name")))
                            command = AddUiViewsCommand(True, 'Add Views', self, self.cardIndex, models)
                            self.command_processor.Submit(command)
                            for ui in self.uiViews[-len(models):]:
                                self.SelectUiView(ui, True)
                wx.TheClipboard.Close()

    def GroupSelectedViews(self):
        models = []
        for ui in self.uiViews:
            if ui.isSelected:
                models.append(ui.model)
        if len(models) >= 2:
            command = GroupUiViewsCommand(True, 'Group Views', self, self.cardIndex, models)
            self.command_processor.Submit(command)

    def UngroupSelectedViews(self):
        models = []
        for ui in self.uiViews:
            if ui.isSelected and ui.model.type == "group":
                models.append(ui.model)
        if len(models) >= 1:
            command = UngroupUiViewsCommand(True, 'Ungroup Views', self, self.cardIndex, models)
            self.command_processor.Submit(command)

    def GroupModelsInternal(self, models, group=None):
        if len(models) > 1:
            for m in models:
                self.RemoveUiViewByModel(m)

            if not group:
                group = GroupModel(self)
            group.AddChildModels(models)
            self.AddUiViewsFromModels([group], False)
            self.SelectUiView(self.GetUiViewByModel(group))
        return group

    def UngroupModelsInternal(self, groups):
        modelSets = []
        if len(groups) > 0:
            self.SelectUiView(None)
            for group in groups:
                childModels = []
                modelSets.append(childModels)
                for child in group.childModels.copy():
                    ui = self.GetUiViewByModel(child)
                    group.RemoveChild(child)
                    childModels.append(child)
                self.RemoveUiViewByModel(group)
                self.AddUiViewsFromModels(childModels, False)
                for child in childModels:
                    self.SelectUiView(self.GetUiViewByModel(child), True)
        return modelSets

    def AddUiViewInternal(self, type, model=None):
        uiView = None

        if model and model in self.uiViewCache:
            uiView = self.uiViewCache.pop(model)
            uiView.view.Reparent(self)
        else:
            if type == "button":
                uiView = UiButton(self.uiCard, self, model)
            elif type == "textfield" or type == "field":
                uiView = UiTextField(self.uiCard, self, model)
            elif type == "textlabel" or type == "label":
                uiView = UiTextLabel(self.uiCard, self, model)
            elif type == "image":
                uiView = UiImage(self.uiCard, self, model)
            elif type == "group":
                uiView = UiGroup(self.uiCard, self, model)
            elif type in ["pen", "line", "oval", "rect", "round_rect"]:
                uiView = UiShape(self.uiCard, self, type, model)

        if uiView:
            if not model:
                uiView.view.Center()
                uiView.model.SetProperty("position", uiView.view.GetPosition())
                uiView.model.SetProperty("size", uiView.view.GetSize())
            self.uiViews.append(uiView)
            uiView.model.parent = self.uiCard.model

            if uiView.model not in self.uiCard.model.childModels:
                self.uiCard.model.AddChild(uiView.model)

            if self.globalCursor:
                uiView.view.SetCursor(wx.Cursor(self.globalCursor))
        return uiView

    def AddUiViewsFromModels(self, models, canUndo=True):
        for model in models:
            if not model in self.uiCard.model.childModels:
                model.SetProperty("name", self.uiCard.model.DeduplicateNameInCard(model.GetProperty("name")))

        command = AddUiViewsCommand(True, 'Add Views', self, self.cardIndex, models)

        if canUndo:
            self.command_processor.Submit(command)
        else:
            # Don't mess with the Undo queue when we're just building a pgae
            command.Do()

        uiViews = self.uiViews[-len(models):]

        if self.globalCursor:
            for uiView in uiViews:
                uiView.view.SetCursor(wx.Cursor(self.globalCursor))

        return uiViews

    def GetSelectedUiViews(self):
        return self.selectedViews

    def SelectUiView(self, view, extend=False):
        if self.isEditing:
            if view and view.parent != self.uiCard:
                extend = False
            if len(self.selectedViews) and not extend:
                for ui in self.selectedViews:
                    ui.SetSelected(False)
                self.selectedViews = []
            if view:
                if not extend or view not in self.selectedViews:
                    view.SetSelected(True)
                    self.selectedViews.append(view)
                else:
                    view.SetSelected(False)
                    self.selectedViews.remove(view)
            if self.designer:
                self.designer.SetSelectedUiViews(self.selectedViews)

    def OnPropertyChanged(self, model, key):
        if model == self.stackModel:
            uiView = self.uiCard
            if key == "size":
                self.SetSize(model.GetProperty(key))
        else:
            uiView = self.GetUiViewByModel(model)
        modelView = self.GetUiViewByModel(model)
        if modelView:
            modelView.OnPropertyChanged(model, key)
        if self.designer:
            self.designer.cPanel.UpdatedProperty(uiView, key)

    def UpdateSelectedUiView(self):
        if self.designer:
            self.designer.UpdateSelectedUiView()

    def GetUiViewByModel(self, model):
        if model == self.uiCard.model:
            return self.uiCard
        for ui in self.GetAllUiViews():
            if ui.model == model:
                return ui
        return None

    def RemoveUiViewByModel(self, viewModel):
        for ui in self.uiViews.copy():
            if ui.model == viewModel:
                if ui in self.selectedViews:
                    self.SelectUiView(ui, True)
                ui.model.parent = None
                if ui.model.type == "group":
                    ui.RemoveChildViews()
                self.uiViews.remove(ui)
                self.uiCard.model.RemoveChild(ui.model)
                ui.DestroyView()
                return

    def ReorderSelectedViews(self, direction):
        oldIndexes = []
        for ui in self.selectedViews:
            if ui.model.parent.type == "group":
                return
            if ui != self.uiCard:
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
        if newIndex >= len(self.stackModel.cardModels): newIndex = len(self.stackModel.cardModels) - 1

        if newIndex != currentIndex:
            command = ReorderCardCommand(True, "Reorder Card", self, self.cardIndex, newIndex)
            self.command_processor.Submit(command)

    def AddCard(self):
        newCard = CardModel(self.stackView)
        newCard.SetProperty("name", newCard.DeduplicateName("card_1",
                                                            [m.GetProperty("name") for m in self.stackModel.cardModels]))
        command = AddNewUiViewCommand(True, "Add Card", self, self.cardIndex+1, "card", newCard)
        self.command_processor.Submit(command)

    def DuplicateCard(self):
        newCard = CardModel(self.stackView)
        newCard.SetData(self.stackModel.cardModels[self.cardIndex].GetData())
        newCard.SetProperty("name", newCard.DeduplicateName(newCard.GetProperty("name"),
                                                            [m.GetProperty("name") for m in self.stackModel.cardModels]))
        command = AddNewUiViewCommand(True, "Duplicate Card", self, self.cardIndex+1, "card", newCard)
        self.command_processor.Submit(command)

    def RemoveCard(self):
        index = self.cardIndex
        if len(self.stackModel.cardModels) > 1:
            command = RemoveUiViewsCommand(True, "Remove Card", self, index, [self.stackModel.cardModels[index]])
            self.command_processor.Submit(command)

    def OnMouseDown(self, uiView, event):
        if self.tool and self.isEditing:
            self.tool.OnMouseDown(uiView, event)
        else:
            uiView.OnMouseDown(event)

    def OnMouseMove(self, uiView, event):
        pos = self.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
        if pos == self.lastMousePos: return

        if self.tool and self.isEditing:
            self.tool.OnMouseMove(uiView, event)
        else:
            uiView.OnMouseMove(event)
            parent = uiView.parent
            while parent:
                parent.OnMouseMove(event)
                parent = parent.parent
        self.lastMousePos = pos

    def OnMouseUp(self, uiView, event):
        if self.tool and self.isEditing:
            self.tool.OnMouseUp(uiView, event)
        else:
            uiView.OnMouseUp(event)

    def OnMouseEnter(self, uiView, event):
        if not self.isEditing:
            uiView.OnMouseEnter(event)

    def OnMouseExit(self, uiView, event):
        if not self.isEditing:
            uiView.OnMouseExit(event)

    def OnKeyDown(self, uiView, event):
        if self.tool and self.isEditing:
            ms = wx.GetMouseState()
            if event.GetKeyCode() == wx.WXK_ESCAPE and not ms.LeftIsDown():
                self.designer.cPanel.SetToolByName("hand")
            self.tool.OnKeyDown(uiView, event)
        else:
            self.uiCard.OnKeyDown(event)
            event.Skip()

    def OnKeyUp(self, uiView, event):
        if self.tool and self.isEditing:
            self.tool.OnKeyUp(uiView, event)
        else:
            self.uiCard.OnKeyUp(event)
            event.Skip()

    def Undo(self):
        self.command_processor.Undo()
        if not self.command_processor.CanUndo():
            self.stackModel.SetDirty(False)
        self.Refresh()

    def Redo(self):
        self.command_processor.Redo()
        self.Refresh()
