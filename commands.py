from wx.lib.docview import Command

class MoveUiViewsCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.cardIndex = args[3]
        self.viewModels = args[4]
        self.delta = args[5]

    def Do(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        self.stackView.SelectUiView(None)
        for m in self.viewModels:
            pos = m.GetProperty("position")
            m.SetProperty("position", (pos[0]+self.delta[0], pos[1]+self.delta[1]))
            self.stackView.SelectUiView(self.stackView.GetUiViewByModel(m), True)
        return True

    def Undo(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        self.stackView.SelectUiView(None)
        for m in self.viewModels:
            pos = m.GetProperty("position")
            m.SetProperty("position", (pos[0]-self.delta[0], pos[1]-self.delta[1]))
            self.stackView.SelectUiView(self.stackView.GetUiViewByModel(m), True)
        return True


class ResizeUiViewCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.cardIndex = args[3]
        self.viewModel = args[4]
        self.delta = args[5]

    def Do(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        sizeModel = self.stackView.stackModel if self.viewModel.type == "card" else self.viewModel
        viewSize = sizeModel.GetProperty("size")
        sizeModel.SetProperty("size", (viewSize[0]+self.delta[0], viewSize[1]+self.delta[1]))
        self.stackView.SelectUiView(self.stackView.GetUiViewByModel(self.viewModel))
        return True

    def Undo(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        sizeModel = self.stackView.stackModel if self.viewModel.type == "card" else self.viewModel
        viewSize = sizeModel.GetProperty("size")
        sizeModel.SetProperty("size", (viewSize[0]-self.delta[0], viewSize[1]-self.delta[1]))
        self.stackView.SelectUiView(self.stackView.GetUiViewByModel(self.viewModel))
        return True


class AddNewUiViewCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.cardIndex = args[3]
        self.viewType = args[4]
        self.viewModel = args[5] if len(args) > 5 else None

    def Do(self):
        if self.viewType == "card":
            self.stackView.LoadCardAtIndex(None)
            self.stackView.stackModel.InsertCardModel(self.cardIndex, self.viewModel)
            self.stackView.LoadCardAtIndex(self.cardIndex)
        else:
            self.stackView.LoadCardAtIndex(self.cardIndex)
            uiView = self.stackView.AddUiViewInternal(self.viewType, self.viewModel)
            if not self.viewModel:
                self.viewModel = uiView.model
            self.stackView.SelectUiView(self.stackView.GetUiViewByModel(self.viewModel))
        return True

    def Undo(self):
        if self.viewType == "card":
            self.stackView.LoadCardAtIndex(None)
            self.stackView.stackModel.RemoveCardModel(self.viewModel)
            index = self.cardIndex-1
            if index < 0: index = 0
            self.stackView.LoadCardAtIndex(index)
        else:
            self.stackView.LoadCardAtIndex(self.cardIndex)
            self.stackView.RemoveUiViewByModel(self.viewModel)
        return True


class AddUiViewsCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.cardIndex = args[3]
        self.viewModels = args[4]

    def Do(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        self.stackView.SelectUiView(None)
        for m in self.viewModels:
            self.stackView.AddUiViewInternal(m.type, m)
            self.stackView.SelectUiView(self.stackView.GetUiViewByModel(m), True)
        return True

    def Undo(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        for m in self.viewModels:
            self.stackView.RemoveUiViewByModel(m)
        return True


class RemoveUiViewsCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.cardIndex = args[3]
        self.viewModels = args[4]
        self.modelIndexes = []

    def Do(self):
        if len(self.viewModels) == 1 and self.viewModels[0].type == "card":
            self.stackView.LoadCardAtIndex(None)
            self.stackView.stackModel.RemoveCardModel(self.viewModels[0])
            index = self.cardIndex
            if index >= len(self.stackView.stackModel.childModels)-1: index = len(self.stackView.stackModel.childModels) - 1
            self.stackView.LoadCardAtIndex(index)
        else:
            self.stackView.LoadCardAtIndex(self.cardIndex)
            self.modelIndexes = []
            for m in self.viewModels.copy():
                self.modelIndexes.append(self.stackView.uiCard.model.childModels.index(m))
                self.stackView.RemoveUiViewByModel(m)
        return True

    def Undo(self):
        if len(self.viewModels) == 1 and self.viewModels[0].type == "card":
            self.stackView.LoadCardAtIndex(None)
            self.stackView.stackModel.InsertCardModel(self.cardIndex, self.viewModels[0])
            self.stackView.LoadCardAtIndex(self.cardIndex)
        else:
            self.stackView.LoadCardAtIndex(self.cardIndex)
            i = len(self.modelIndexes)-1
            models = self.viewModels.copy()
            models.reverse()
            for m in models:
                self.stackView.uiCard.model.childModels.insert(i, m)
                i -= 1
            self.stackView.LoadCardAtIndex(self.cardIndex, True)
            self.stackView.SelectUiView(None)
            for m in models:
                self.stackView.SelectUiView(self.stackView.GetUiViewByModel(m), True)
        return True


class ReorderCardCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.cardIndex = args[3]
        self.newIndex = args[4]

    def Do(self):
        cardList = self.stackView.stackModel.childModels
        cardList.insert(self.newIndex, cardList.pop(self.cardIndex))
        self.stackView.LoadCardAtIndex(self.newIndex)
        return True

    def Undo(self):
        cardList = self.stackView.stackModel.childModels
        cardList.insert(self.cardIndex, cardList.pop(self.newIndex))
        self.stackView.LoadCardAtIndex(self.cardIndex)
        return True


class ReorderUiViewsCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.cardIndex = args[3]
        self.oldIndexes = args[4]
        self.newIndexes = args[5]

    def Do(self):
        models = []
        viewList = self.stackView.stackModel.childModels[self.cardIndex].childModels
        for i in reversed(self.oldIndexes):
            models.append(viewList.pop(i))
        for i in self.newIndexes:
            viewList.insert(i, models.pop())
        selected = self.stackView.GetSelectedUiViews()
        self.stackView.LoadCardAtIndex(self.cardIndex, reload=True)
        self.stackView.SelectUiView(None)
        for ui in selected:
            self.stackView.SelectUiView(ui, True)
        return True

    def Undo(self):
        models = []
        viewList = self.stackView.stackModel.childModels[self.cardIndex].childModels
        for i in reversed(self.newIndexes):
            models.append(viewList.pop(i))
        for i in self.oldIndexes:
            viewList.insert(i, models.pop())
        selected = self.stackView.GetSelectedUiViews()
        self.stackView.LoadCardAtIndex(self.cardIndex, reload=True)
        self.stackView.SelectUiView(None)
        for ui in selected:
            self.stackView.SelectUiView(ui, True)
        return True


class SetPropertyCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.cPanel = args[2]
        self.cardIndex = args[3]
        self.model = args[4]
        self.key = args[5]
        self.newVal = args[6]
        self.interactive = args[7] if len(args) >= 8 else True
        self.oldVal = self.model.GetProperty(self.key)
        self.hasRun = False

    def Do(self):
        if self.interactive:
            self.cPanel.stackView.LoadCardAtIndex(self.cardIndex)
            if self.hasRun:
                uiView = self.cPanel.stackView.GetUiViewByModel(self.model)
                self.cPanel.stackView.SelectUiView(uiView)

        self.model.SetProperty(self.key, self.newVal)
        self.hasRun = True
        return True

    def Undo(self):
        if self.interactive:
            self.cPanel.stackView.LoadCardAtIndex(self.cardIndex)
            if self.hasRun:
                uiView = self.cPanel.stackView.GetUiViewByModel(self.model)
                self.cPanel.stackView.SelectUiView(uiView)

        self.model.SetProperty(self.key, self.oldVal)
        return True


class SetHandlerCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.cPanel = args[2]
        self.cardIndex = args[3]
        self.model = args[4]
        self.key = args[5]
        self.newVal = args[6]
        self.oldSel = args[7]
        self.newSel = args[8]
        self.interactive = args[9] if len(args) >= 10 else True
        self.oldVal = self.model.GetHandler(self.key)
        self.hasRun = False

    def Do(self):
        uiView = self.cPanel.stackView.GetUiViewByModel(self.model)
        if self.interactive:
            self.cPanel.stackView.LoadCardAtIndex(self.cardIndex)
            if self.hasRun:
                self.cPanel.stackView.SelectUiView(uiView)

        self.model.SetHandler(self.key, self.newVal)

        if self.hasRun and uiView:
            self.cPanel.UpdateHandlerForUiViews([uiView], self.key)
        if self.interactive:
            if self.newSel:
                self.cPanel.codeEditor.SetSelection(*self.newSel)

        self.hasRun = True
        return True

    def Undo(self):
        uiView = self.cPanel.stackView.GetUiViewByModel(self.model)
        if self.interactive:
            self.cPanel.stackView.LoadCardAtIndex(self.cardIndex)
            self.cPanel.stackView.SelectUiView(uiView)

        self.model.SetHandler(self.key, self.oldVal)

        if uiView:
            self.cPanel.UpdateHandlerForUiViews([uiView], self.key)
        if self.interactive:
            if self.oldSel:
                self.cPanel.codeEditor.SetSelection(*self.oldSel)
        return True


class GroupUiViewsCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.cardIndex = args[3]
        self.models = args[4]
        self.group = None

    def Do(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        self.group = self.stackView.GroupModelsInternal(self.models, self.group)
        return True

    def Undo(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        self.stackView.UngroupModelsInternal([self.group])
        return True


class UngroupUiViewsCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.cardIndex = args[3]
        self.groups = args[4]

    def Do(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        self.modelSets = self.stackView.UngroupModelsInternal(self.groups)
        return True

    def Undo(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        i = 0
        for subviews in self.modelSets:
            self.stackView.GroupModelsInternal(subviews, self.groups[i])
            i += 1
        self.modelSets = None
        return True


class CommandGroup(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.commands = args[2]

    def Do(self):
        for c in self.commands:
            c.Do()
        return True

    def Undo(self):
        for c in reversed(self.commands):
            c.Undo()
        return True
