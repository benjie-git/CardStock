#!/usr/bin/python

from uiPage import PageModel


class StackModel(object):
    def __init__(self):
        super().__init__()
        self.pageModels = []

    def AddPageModel(self, pageModel):
        self.pageModels.append(pageModel)

    def RemovePageModel(self, pageModel):
        self.pageModels.remove(pageModel)

    def GetPageModel(self, i):
        return self.pageModels[i]

    def GetData(self):
        return {"pages":[m.GetData() for m in self.pageModels]}

    def SetData(self, stackData):
        self.pageModels = []
        for data in stackData["pages"]:
            m = PageModel()
            m.SetData(data)
            self.AddPageModel(m)
