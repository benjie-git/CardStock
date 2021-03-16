import wx
import os

try:
    import PyInstaller.__main__
    from shutil import copyfile, rmtree
    PY_INSTALLER_AVAILABLE = True
except ModuleNotFoundError:
    PY_INSTALLER_AVAILABLE = False

HERE = os.path.dirname(os.path.realpath(__file__))


class StackExporter(object):
    def __init__(self, stackManager):
        super().__init__()
        self.stackManager = stackManager

    def StartExport(self, doSave):
        if not PY_INSTALLER_AVAILABLE:
            wx.MessageDialog(None, "To export a stack as a stand-alone program, "
                                   "you need to first install the pyinstaller python package.",
                             "Unable to Export", wx.OK).ShowModal()
            return
        if self.stackManager.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. You will need to Save before Exporting.",
                                 "Save before Exporting?", wx.OK | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            if r == wx.ID_OK:
                doSave()

        if self.stackManager.filename:
            plainFileName = os.path.basename(self.stackManager.filename)
            if plainFileName.endswith(".cds"):
                plainFileName =  plainFileName[:-4]

            dlg = wx.FileDialog(self.stackManager.designer, "Export CaardStock application to...", os.getcwd(),
                                plainFileName,
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                               wildcard = "CardStock Application (*)|*")
            if dlg.ShowModal() == wx.ID_OK:
                filepath = dlg.GetPath()
                filename = os.path.basename(filepath)

                canSave = self.stackManager.stackModel.GetProperty("canSave")

                tmp = "/tmp" if wx.Platform != "__WXMSW__" else "C:\Windows\Temp"
                tmpStack = os.path.join(tmp, 'stack.cds')
                copyfile(self.stackManager.filename, tmpStack)

                if wx.Platform == "__WXMAC__":
                    args = [
                        '--onedir',
                        '--windowed',
                        # '-s',  # slightly smaller, but slower to build.  Maybe make optional?
                        '--workpath',
                        tmp,
                        '--specpath',
                        tmp,
                        '--clean',
                        "--add-data",
                        f"{tmpStack}:.",
                        '--distpath',
                        os.path.dirname(filepath),
                        '--name',
                        filename,
                        '-y',
                        f'{HERE}/standalone.py'
                    ]
                elif wx.Platform == "__WXMSW__":
                    if canSave:
                        os.mkdir(filepath)
                        copyfile(tmpStack, os.path.join(filepath, "stack.cds"))
                        distpath = filepath
                    else:
                        distpath = os.path.dirname(filepath)

                    args = [
                        '--onefile',
                        '--windowed',
                        '--workpath',
                        tmp,
                        '--specpath',
                        tmp,
                        '--clean',
                        '--distpath',
                        distpath,
                        '--name',
                        filename,
                        '-y',
                        f'{HERE}/standalone.py'
                    ]
                    if not canSave:
                        args.extend(["--add-data", f"{tmpStack};."])
                else:
                    if canSave:
                        os.mkdir(filepath)
                        copyfile(tmpStack, os.path.join(filepath, "stack.cds"))
                        distpath = filepath
                    else:
                        distpath = os.path.dirname(filepath)

                    args = [
                        '--onefile',
                        '--windowed',
                        # '-s',  # slightly smaller, but slower to build.  Maybe make optional?
                        '--workpath',
                        tmp,
                        '--specpath',
                        tmp,
                        '--clean',
                        '--distpath',
                        distpath,
                        '--name',
                        filename,
                        '-y',
                        f'{HERE}/standalone.py'
                    ]
                    if not canSave:
                        args.extend(["--add-data", f"{tmpStack}:."])

                # waitDlg = wx.MessageDialog(None, "Exporting this stack...", "", wx.OK|wx.ICON_INFORMATION)
                # waitDlg.Show() # Show does nothing, showModal waits.  Maybe don't use a dialog...
                # wx.Yield()

                print("Run: pyinstaller " + " ".join(args))
                PyInstaller.__main__.run(args)

                os.remove(tmpStack)

                if wx.Platform == "__WXMAC__":
                    try:
                        os.remove(filepath) # remove the actual chosen path, keep the .app
                    except (IsADirectoryError, PermissionError) as e:
                        rmtree(filepath)

                # waitDlg.Hide()
                # waitDlg.Destroy()
                print("Export finished.")

            dlg.Hide()
            dlg.Destroy()
