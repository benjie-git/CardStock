#!/usr/bin/python

from uiPage import PageModel


class StackModel(object):
    def __init__(self):
        super().__init__()
        self.cardModels = []

    def AddPageModel(self, pageModel):
        self.cardModels.append(pageModel)

    def RemovePageModel(self, pageModel):
        self.cardModels.remove(pageModel)

    def GetPageModel(self, i):
        return self.cardModels[i]

    def GetDirty(self):
        for page in self.cardModels:
            if page.GetDirty():
                return True
        return False

    def SetDirty(self, dirty):
        for page in self.cardModels:
            page.SetDirty(dirty)

    def SetRunner(self, runner):
        for pageModel in self.cardModels:
            pageModel.runner = runner
            for model in pageModel.childModels:
                model.runner = runner

    def GetData(self):
        return {"pages":[m.GetData() for m in self.cardModels]}

    def SetData(self, stackData):
        self.cardModels = []
        for data in stackData["pages"]:
            m = PageModel()
            m.SetData(data)
            self.AddPageModel(m)
