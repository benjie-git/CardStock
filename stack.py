from page import PageWindow

class StackModel():
    def __init__(self):
        self.pagesData = []

    def GetPageData(self, i):
        return self.pagesData[i]

    def GetPages(self):
        return self.pagesData

    def AppendPage(self, page):
        self.pagesData.append(page.GetData())

    def GetStackData(self):
        return {"pages":self.pagesData}

    def SetStackData(self, data):
        self.pagesData = data["pages"]
