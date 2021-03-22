import wx
import os
import re
import random
import json

try:
    import PyInstaller.__main__
    from shutil import copyfile, rmtree
    PY_INSTALLER_AVAILABLE = True
except ModuleNotFoundError:
    PY_INSTALLER_AVAILABLE = False

HERE = os.path.dirname(os.path.realpath(__file__))


class StackExporter(object):
    """
    Export a stack as a standalone application.  Uses pyinstaller, and pulls in all of the resources used by the stack,
    as seen by the ResourcePathManager.
    """
    def __init__(self, stackManager):
        super().__init__()
        self.resList = None
        self.resMap = None
        self.exportDlg = None
        self.stackManager = stackManager

    def StartExport(self, doSave):
        # Check that we even have pyinstaller available
        if not PY_INSTALLER_AVAILABLE:
            wx.MessageDialog(self.stackManager.designer,
                             "To export a stack as a stand-alone program, "
                             "you need to first install the pyinstaller python package.",
                             "Unable to Export", wx.OK).ShowModal()
            return

        # Check that the user has saved the stack
        if self.stackManager.stackModel.GetDirty():
            r = wx.MessageDialog(self.stackManager.designer,
                                 "There are unsaved changes. You will need to Save before Exporting.",
                                 "Save before Exporting?", wx.OK | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            if r == wx.ID_OK:
                doSave()

        self.GatherResources()
        self.ConfirmResources()

    def GatherResources(self):
        self.resList = set()

        # Add paths to resources used during stack runtime
        paths = self.stackManager.resPathMan.GetRequestedPaths()
        for path in paths:
            self.resList.add(path)

        # Add paths found by simple static analysis
        # Look for any image objects with a file property
        # Look in all handlers for PlaySound("<path>"), *.file = "<path>"
        patterns = [re.compile(r"\bPlaySound\('([^']+)'\)"),
                    re.compile(r'\bPlaySound\("([^"]+)"\)'),
                    re.compile(r"\w\.file\s*=\s*'([^']+)'"),
                    re.compile(r'\w\.file\s*=\s*"([^"]+)"')]
        self.ScanObjTree(self.stackManager.stackModel, patterns)

    def ScanObjTree(self, obj, patterns):
        if obj.type == "image":
            path = obj.GetProperty("file")
            if path:
                self.resList.add(path)

        for (k, v) in obj.handlers.items():
            for p in patterns:
                for match in p.findall(v):
                    self.resList.add(match)

        for child in obj.childModels:
            self.ScanObjTree(child, patterns)

    def ConfirmResources(self):
        self.exportDlg = ExportDialog(self.stackManager.designer, self)
        self.exportDlg.ShowModal()

    def BuildResMap(self):
        self.resMap = {}
        i = 1
        for path in self.resList:
            self.resMap[path] = "resource-" + str(i)
            i += 1

    def GetOutputPath(self):
        path = None
        if self.stackManager.filename:
            plainFileName = os.path.basename(self.stackManager.filename)
            if plainFileName.endswith(".cds"):
                plainFileName = plainFileName[:-4]

            dlg = wx.FileDialog(self.stackManager.designer, "Export CardStock application to...", os.getcwd(),
                                plainFileName,
                                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                                wildcard="CardStock Application (*)|*")
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
            dlg.Hide()
            dlg.Destroy()
            wx.Yield()
        return path

    def Export(self):
        filepath = self.GetOutputPath()
        if filepath:
            filename = os.path.basename(filepath)

            canSave = self.stackManager.stackModel.GetProperty("canSave")

            # Prep temp dir
            tmp = "/tmp/CardStock" if wx.Platform != "__WXMSW__" else "C:\Windows\Temp\CardStock"
            sep = ":" if wx.Platform != "__WXMSW__" else ";"
            tmp += "-"+str(random.randint(1000000, 9999999))
            os.mkdir(tmp)

            # Copy stack
            tmpStack = os.path.join(tmp, 'stack.cds')
            copyfile(self.stackManager.filename, tmpStack)

            # Create ResourceMap.json
            self.BuildResMap()
            mapFile = os.path.join(tmp, 'ResourceMap.json')
            jsonData = json.dumps(self.resMap)
            with open(mapFile, 'w') as f:
                f.write(jsonData)

            # Set up pyinstaller args
            args = [
                '--windowed',
                '--workpath',
                tmp,
                '--specpath',
                tmp,
                '--clean',
                '--name',
                filename,
                '-y',
                f'{HERE}/standalone.py']

            if wx.Platform == "__WXMAC__":
                args.extend([
                    '--onedir',
                    # '-s',  # slightly smaller, but slower to build.  Maybe make optional?
                    "--add-data",
                    f"{tmpStack}{sep}.",
                    '--distpath',
                    os.path.dirname(filepath)
                ])
            elif wx.Platform == "__WXMSW__":
                if canSave:
                    os.mkdir(filepath)
                    copyfile(tmpStack, os.path.join(filepath, "stack.cds"))
                    distpath = filepath
                else:
                    distpath = os.path.dirname(filepath)

                args.extend([
                    '--onefile',
                    '--distpath', distpath])
                if not canSave:
                    args.extend(["--add-data", f"{tmpStack}{sep}."])
            else:
                if canSave:
                    os.mkdir(filepath)
                    copyfile(tmpStack, os.path.join(filepath, "stack.cds"))
                    distpath = filepath
                else:
                    distpath = os.path.dirname(filepath)

                args.extend([
                    '--onefile',
                    # '-s',  # slightly smaller, but slower to build.  Maybe make optional?
                    '--distpath', distpath])
                if not canSave:
                    args.extend(["--add-data", f"{tmpStack}{sep}."])

            args.extend(["--add-data", f"{mapFile}{sep}."])
            stackDir = os.path.dirname(self.stackManager.filename)
            for (origPath, newPath) in self.resMap.items():
                absPath = os.path.join(stackDir, origPath)
                tmpPath = os.path.join(tmp, newPath)
                copyfile(absPath, tmpPath)
                args.extend(["--add-data", f"{tmpPath}{sep}."])

            print("Run: pyinstaller " + " ".join(args))
            PyInstaller.__main__.run(args)

            if wx.Platform == "__WXMAC__":
                try:
                    os.remove(filepath) # remove the actual chosen path, keep the .app
                except (IsADirectoryError, PermissionError) as e:
                    rmtree(filepath)

            rmtree(tmp)
            print("Export finished.")


class ExportDialog(wx.Dialog):
    def __init__(self, parent, exporter):
        super().__init__(parent, title="Export Stack", size=(500, 400))
        self.exporter = exporter

        self.panel = wx.Panel(self)
        spacing = 5

        self.items = list(self.exporter.resList)

        addBtn = wx.Button(self.panel, label = "Add", size=(50, 20))
        addBtn.Bind(wx.EVT_BUTTON, self.OnAdd)

        rmBtn = wx.Button(self.panel, label = "Remove", size=(50, 20))
        rmBtn.Bind(wx.EVT_BUTTON, self.OnRemove)

        exportBtn = wx.Button(self.panel, label = "Export", size=(50, 20))
        exportBtn.Bind(wx.EVT_BUTTON, self.OnExport)
        exportBtn.SetDefault()

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(addBtn, 1, wx.EXPAND|wx.ALL, spacing)
        buttonSizer.Add(rmBtn, 1, wx.EXPAND|wx.ALL, spacing)
        buttonSizer.Add(exportBtn, 1, wx.EXPAND|wx.ALL, spacing)

        if len(self.exporter.resList) > 0:
            labelStr = "These are the image and sound files that this stack seems to need.  " \
                       "If you think other files are needed, try running the stack again and make sure to use " \
                       "all of the images and sounds that it can.  Or you can add or remove files here by using the " \
                       "buttons below, and when the list is complete, " \
                       "click the \"Export\" button to Export these files along with this stack."
        else:
            labelStr = "No image or sound files seem to be used by this stack.  That's fine, but " \
                       "if you think other files are needed, try running the stack again and make sure to use " \
                       "all of the images and sounds that it can.  Or you can add or remove files here by using the " \
                       "buttons below, and when the list is complete, " \
                       "click the \"Export\" button to Export these files along with this stack."

        label = AutoWrapStaticText(self.panel, label=labelStr)

        self.listBox = wx.ListBox(self.panel, choices=self.items)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 0, wx.EXPAND|wx.ALL, spacing)
        sizer.Add(self.listBox, 1, wx.EXPAND|wx.ALL, spacing)
        sizer.Add(buttonSizer, 0, wx.EXPAND|wx.ALL, spacing)
        self.panel.SetSizerAndFit(sizer)

    def OnAdd(self, event):
        dlg = wx.FileDialog(self.exporter.stackManager.designer, "Add Resource File(s)", os.getcwd(),
                            "",
                            style=wx.FD_OPEN | wx.FD_MULTIPLE,
                            wildcard="Any File (*)|*")
        if dlg.ShowModal() == wx.ID_OK:
            for filepath in dlg.GetPaths():
                relPath = os.path.relpath(filepath, os.path.dirname(self.exporter.stackManager.filename))
                self.items.append(relPath)
            self.listBox.SetItems(self.items)
        dlg.Destroy()

    def OnRemove(self, event):
        i = self.listBox.GetSelection()
        if i != wx.NOT_FOUND:
            del self.items[i]
            self.listBox.SetItems(self.items)
            self.listBox.SetSelection(min(i, len(self.items)-1))

    def OnExport(self, event):
        self.SetTitle("Exporting Stack...")
        self.panel.Enable(False)
        wx.Yield()
        self.exporter.resList = set(self.items)
        self.exporter.Export()
        self.exporter = None
        self.Close()


class AutoWrapStaticText(wx.Control):
    def __init__(self, parent, id=-1, label="",
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0):
        super().__init__(parent=parent, id=id, pos=pos, size=size, style=wx.NO_BORDER)
        self.st = wx.StaticText(self, label=label, style=style)
        self._label = label  # save the unwrapped text
        self._Rewrap()
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def SetLabel(self, label):
        self._label = label
        self._Rewrap()

    def GetLabel(self):
        return self._label

    def SetFont(self, font):
        self.st.SetFont(font)
        self._Rewrap()

    def GetFont(self):
        return self.st.GetFont()

    def OnSize(self, evt):
        self.st.SetSize(self.GetSize())
        self._Rewrap()

    def _Rewrap(self):
        self.st.Freeze()
        self.st.SetLabel(self._label)
        self.st.Wrap(self.GetSize().width)
        self.st.Thaw()

    def DoGetBestSize(self):
        # this should return something meaningful for what the best
        # size of the widget is, but what that size should be while we
        # still don't know the actual width is still an open
        # question...  Just return a dummy value for now.
        return wx.Size(100, 100)
