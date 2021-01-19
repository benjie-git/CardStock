from wx.lib.docview import Command

class MoveUiViewCommand(Command):
    uiView = None

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.cardIndex = args[3]
        self.viewModel = args[4]
        self.delta = args[5]

    def Do(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        pos = self.viewModel.GetProperty("position")
        self.viewModel.SetProperty("position", (pos[0]+self.delta[0], pos[1]+self.delta[1]))
        return True

    def Undo(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        pos = self.viewModel.GetProperty("position")
        self.viewModel.SetProperty("position", (pos[0]-self.delta[0], pos[1]-self.delta[1]))
        return True


class ResizeUiViewCommand(Command):
    uiView = None

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.cardIndex = args[3]
        self.viewModel = args[4]
        self.delta = args[5]

    def Do(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        viewSize = self.viewModel.GetProperty("size")
        self.viewModel.SetProperty("size", (viewSize[0]+self.delta[0], viewSize[1]+self.delta[1]))
        return True

    def Undo(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        viewSize = self.viewModel.GetProperty("size")
        self.viewModel.SetProperty("size", (viewSize[0]-self.delta[0], viewSize[1]-self.delta[1]))
        return True


class AddUiViewCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.cardIndex = args[3]
        self.viewType = args[4]
        self.viewModel = args[5] if len(args)>5 else None

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


class RemoveUiViewCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.cardIndex = args[3]
        self.viewModel = args[4]

    def Do(self):
        if self.viewModel.type == "card":
            self.stackView.LoadCardAtIndex(None)
            self.stackView.stackModel.RemoveCardModel(self.viewModel)
            index = self.cardIndex
            if index >= len(self.stackView.stackModel.cardModels)-1: index = len(self.stackView.stackModel.cardModels)-1
            self.stackView.LoadCardAtIndex(index)
        else:
            self.stackView.LoadCardAtIndex(self.cardIndex)
            self.stackView.RemoveUiViewByModel(self.viewModel)
        return True

    def Undo(self):
        if self.viewModel.type == "card":
            self.stackView.LoadCardAtIndex(None)
            self.stackView.stackModel.InsertCardModel(self.cardIndex, self.viewModel)
            self.stackView.LoadCardAtIndex(self.cardIndex)
        else:
            self.stackView.LoadCardAtIndex(self.cardIndex)
            self.stackView.AddUiViewInternal(self.viewModel.type, self.viewModel)
        return True


class ReorderUiViewCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.cardIndex = args[3]
        self.viewModel = args[4]
        self.newIndex = args[5]
        if self.viewModel.type != "card":
            self.oldIndex = self.stackView.stackModel.cardModels[self.cardIndex].childModels.index(self.viewModel)

    def Do(self):
        if self.viewModel.type == "card":
            cardList = self.stackView.stackModel.cardModels
            cardList.insert(self.newIndex, cardList.pop(self.cardIndex))
            self.stackView.LoadCardAtIndex(self.newIndex)
        else:
            viewList = self.stackView.stackModel.cardModels[self.cardIndex].childModels
            viewList.insert(self.newIndex, viewList.pop(self.oldIndex))
            self.stackView.LoadCardAtIndex(self.cardIndex, reload=True)
            self.stackView.SelectUiView(self.stackView.GetUiViewByModel(self.viewModel))
        return True

    def Undo(self):
        if self.viewModel.type == "card":
            cardList = self.stackView.stackModel.cardModels
            cardList.insert(self.cardIndex, cardList.pop(self.newIndex))
            self.stackView.LoadCardAtIndex(self.cardIndex)
        else:
            viewList = self.stackView.stackModel.cardModels[self.cardIndex].childModels
            viewList.insert(self.oldIndex, viewList.pop(self.newIndex))
            self.stackView.LoadCardAtIndex(self.cardIndex, reload=True)
            self.stackView.SelectUiView(self.stackView.GetUiViewByModel(self.viewModel))
        return True
