# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import requests
import wx
import os
import sys
import re
import random
import json
import shutil

try:
    import PyInstaller.__main__
    PY_INSTALLER_AVAILABLE = True
except ModuleNotFoundError:
    PY_INSTALLER_AVAILABLE = False

# Settings for Uploading stack to CardStock.run
CSWEB_DISPLAY_NAME = "CardStock.run"
CSHOST = "https://cardstock.run"  # "http://127.0.0.1:8000"
CSWEB_SIGNUP_URL = f"{CSHOST}/l/signup"
CSWEB_GET_TOKEN_URL = f"{CSHOST}/v/1/api-token-auth/"
CSWEB_UPLOAD_URL = f"{CSHOST}/v/1/upload-stack"

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
        self.moduleList = None
        self.exportDlg = None
        self.stackManager = stackManager

    def StartExport(self, doSave):
        # Check that the user has saved the stack
        if self.stackManager.stackModel.GetDirty():
            r = wx.MessageDialog(self.stackManager.designer,
                                 "There are unsaved changes. You will need to Save before Exporting.",
                                 "Save before Exporting?", wx.OK | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            if r == wx.ID_OK:
                doSave()

        subStackList = self.GatherSubStacks()
        if len(subStackList) > 0:
            wx.MessageDialog(self.stackManager.designer,
                             "CardStock is not currently able to export a stack that includes any run_stack() calls.",
                             "Unable to Export", wx.OK).ShowModal()
            return

        self.GatherResources()
        self.GatherModules()
        self.ConfirmResources()

    def GatherResources(self):
        self.resList = set()

        # Add paths to resources used during stack runtime
        paths = self.stackManager.resPathMan.GetRequestedPaths()
        for path in paths:
            self.resList.add(path)

        # Add paths found by simple static analysis:
        # Look for any image objects with a file property
        # Look in all handlers for play_sound("<path>"), *.file = "<path>"
        patterns = [[re.compile(r"\s*play_sound\('([^']+)'\)", re.MULTILINE)],
                    [re.compile(r'\s*play_sound\("([^"]+)"\)', re.MULTILINE)],
                    [re.compile(r"\w\.file\s*=\s*'([^']+)'", re.MULTILINE)],
                    [re.compile(r'\w\.file\s*=\s*"([^"]+)"', re.MULTILINE)]]
        self.ScanObjTree(self.stackManager.stackModel, [["image", "file"]], patterns, self.resList)

    def GatherModules(self):
        self.moduleList = set()

        # Add modules found by simple static analysis:
        # Look in all handlers for imports
        patterns = [[re.compile(r"^\s*import\s+([^\s,]+(?:[^\S\r\n,]*,[^\S\r\n,]*[^\s,]+)*)", re.MULTILINE),
                     re.compile(r"[\s,]*([^\s,]+)[\s,]*")],
                    [re.compile(r"^[^\S\r\n]*from[^\S\r\n]+([^\s,]+)[^\S\r\n]+import\s", re.MULTILINE)]]
        self.ScanObjTree(self.stackManager.stackModel, [], patterns, self.moduleList)

    def GatherSubStacks(self):
        stackList = set()

        # Find all uses of run_stack()
        patterns = [[re.compile(r'\s*run_stack\("([^"]+)"\)', re.MULTILINE)]]
        self.ScanObjTree(self.stackManager.stackModel, [], patterns, stackList)
        return stackList

    def ScanObjTree(self, obj, props, patterns, outputSet):
        for pList in props:
            (t, p) = pList
            if obj.type == t:
                path = obj.GetProperty(p)
                if path:
                    outputSet.add(path)

        def runPatterns(l, s):
            if len(l) == 0 or len(s) == 0:
                return
            for match in l[0].findall(s):
                if len(l) > 1:
                    runPatterns(l[1:], match)
                else:
                    outputSet.add(match)

        for (k, v) in obj.handlers.items():
            for pList in patterns:
                runPatterns(pList, v)

        for child in obj.childModels:
            self.ScanObjTree(child, props, patterns, outputSet)

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

            initialDir = os.path.dirname(self.stackManager.filename)
            dlg = wx.FileDialog(self.stackManager.designer, "Export CardStock application to...", initialDir,
                                plainFileName,
                                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                                wildcard="CardStock Application (*)|*")
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
            dlg.Hide()
            dlg.Destroy()
            wx.YieldIfNeeded()
        return path

    def ExportApp(self):
        # Check that we even have pyinstaller available
        if not PY_INSTALLER_AVAILABLE and not getattr(sys, 'frozen', False):
            wx.MessageDialog(self.stackManager.designer,
                             "To export a stack as a stand-alone program, "
                             "you need to first install the pyinstaller python package.",
                             "Unable to Export", wx.OK).ShowModal()
            return

        filepath = self.GetOutputPath()
        if getattr(sys, 'frozen', False) and hasattr(sys, "_MEIPASS"):
            # We're running in a bundle
            self.ExportFromBundle(filepath)
        else:
            self.ExportUsingPyInstaller(filepath)

    def ExportUsingPyInstaller(self, filepath):
        if filepath:
            filename = os.path.basename(filepath)

            can_save = self.stackManager.stackModel.GetProperty("can_save")

            # Prep temp dir
            tmp = "/tmp/CardStock" if wx.Platform != "__WXMSW__" else "C:\Windows\Temp\CardStock"
            sep = ":" if wx.Platform != "__WXMSW__" else ";"
            tmp += "-"+str(random.randint(1000000, 9999999))
            os.mkdir(tmp)

            # Copy stack
            tmpStack = os.path.join(tmp, 'stack.cds')
            shutil.copyfile(self.stackManager.filename, tmpStack)

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
                if can_save:
                    os.mkdir(filepath)
                    resPath = os.path.join(filepath, "Resources")
                    os.mkdir(resPath)
                    shutil.copyfile(tmpStack, os.path.join(resPath, "stack.cds"))
                    distpath = filepath
                else:
                    distpath = os.path.dirname(filepath)

                args.extend([
                    '--onefile',
                    '--distpath', distpath])
                if not can_save:
                    args.extend(["--add-data", f"{tmpStack}{sep}."])
            else:
                if can_save:
                    os.mkdir(filepath)
                    resPath = os.path.join(filepath, "Resources")
                    os.mkdir(resPath)
                    shutil.copyfile(tmpStack, os.path.join(resPath, "stack.cds"))
                    distpath = filepath
                else:
                    distpath = os.path.dirname(filepath)

                args.extend([
                    '--onefile',
                    # '-s',  # slightly smaller, but slower to build.  Maybe make optional?
                    '--distpath', distpath])
                if not can_save:
                    args.extend(["--add-data", f"{tmpStack}{sep}."])

            args.extend(["--add-data", f"{mapFile}{sep}."])
            stackDir = os.path.dirname(self.stackManager.filename)
            for (origPath, newPath) in self.resMap.items():
                absPath = os.path.join(stackDir, origPath)
                tmpPath = os.path.join(tmp, newPath)
                shutil.copyfile(absPath, tmpPath)
                args.extend(["--add-data", f"{tmpPath}{sep}."])

            for mod in self.moduleList:
                args.extend(["--hidden-import", mod])

            print("Run: pyinstaller " + " ".join(args))
            PyInstaller.__main__.run(args)

            if wx.Platform == "__WXMAC__":
                try:
                    os.remove(filepath) # remove the actual chosen path, keep the .app
                except (IsADirectoryError, PermissionError) as e:
                    shutil.rmtree(filepath)

            shutil.rmtree(tmp)
            print("Export finished.")

    def ExportFromBundle(self, filepath):
        bundle_dir = sys._MEIPASS
        if wx.Platform == "__WXMAC__":
            standaloneDir = os.path.join(bundle_dir, "../Resources")
            standalonePath = os.path.join(standaloneDir, "standalone.app")
            appPath = filepath + ".app"
            shutil.copytree(standalonePath, appPath)
            resDir = appPath + "/Contents/MacOS"
            shutil.copyfile(self.stackManager.filename, os.path.join(resDir, "stack.cds"))
        elif wx.Platform == "__WXMSW__":
            standalonePath = os.path.join(bundle_dir, "standalone.exe")
            exeName = os.path.basename(filepath) + ".exe"
            appPath = os.path.join(filepath, exeName)
            os.mkdir(filepath)
            shutil.copyfile(standalonePath, appPath)
            resDir = os.path.join(filepath, "Resources")
            os.mkdir(resDir)
            shutil.copyfile(self.stackManager.filename, os.path.join(resDir, "stack.cds"))
        else:
            standalonePath = os.path.join(bundle_dir, "standalone")
            exeName = os.path.basename(filepath)
            appPath = os.path.join(filepath, exeName)
            os.mkdir(filepath)
            shutil.copyfile(standalonePath, appPath)
            os.chmod(appPath, 0o775)
            resDir = os.path.join(filepath, "Resources")
            os.mkdir(resDir)
            shutil.copyfile(self.stackManager.filename, os.path.join(resDir, "stack.cds"))

        # Create ResourceMap.json
        self.BuildResMap()
        jsonData = json.dumps(self.resMap)
        mapFile = os.path.join(resDir, 'ResourceMap.json')
        with open(mapFile, 'w') as f:
            f.write(jsonData)

        stackDir = os.path.dirname(self.stackManager.filename)
        for (origPath, newPath) in self.resMap.items():
            absPath = os.path.join(stackDir, origPath)
            shutil.copyfile(absPath, os.path.join(resDir, newPath))

        print("Export finished.")

    def ExportWeb(self):
        stackName = os.path.basename(self.stackManager.filename)
        if stackName.endswith(".cds"):
            stackName = stackName[:-4]
        resMap = {}
        i=1
        stackDir = os.path.dirname(self.stackManager.filename)
        for path in self.resList:
            resMap[path] = "r-"+str(i)
            i += 1

        token = self.stackManager.designer.configInfo["upload_token"]
        headers = {"Authorization": f"Token {token}"}

        params = {
            "name": stackName,
            "is_public": True,
            "resource_map": json.dumps(resMap),
        }

        tmp = "/tmp/" if wx.Platform != "__WXMSW__" else "C:\\Windows\\Temp\\"
        tmpPath = tmp + "CardStock_" + str(random.randint(1000000, 9999999)) + ".png"
        self.stackManager.designer.thumbnail.SaveFile(tmpPath, wx.BITMAP_TYPE_PNG)

        files = {"stack_data": open(self.stackManager.filename, 'rb'),
                 "thumbnail": open(tmpPath, 'rb')}
        for k,v in resMap.items():
            absPath = os.path.join(stackDir, k)
            files[v] = open(absPath, 'rb')

        try:
            response = requests.post(CSWEB_UPLOAD_URL, headers=headers, data=params, files=files)
            responseJson = response.json()
            if 'url' in responseJson:
                msg = f"Upload done.  This stack is available at\n\n{responseJson['url']}"
                dialog = wx.MessageDialog(None, msg, 'Upload Succeeded', wx.YES_NO | wx.CANCEL | wx.CANCEL_DEFAULT)
                dialog.SetYesNoCancelLabels('Open URL', 'Copy URL', 'Done')
                answer = dialog.ShowModal()
                dialog.Destroy()
                if answer == wx.ID_NO:
                    # Copy URL
                    if wx.TheClipboard.Open():
                        wx.TheClipboard.SetData(wx.TextDataObject(responseJson['url']))
                        wx.TheClipboard.Close()
                elif answer == wx.ID_YES:
                    # Open URL
                    wx.LaunchDefaultBrowser(responseJson['url'])
                return responseJson['url']
            msg = f"Upload failed. \n\n {responseJson.get('error')}"
        except Exception as e:
            msg = f"Upload failed.\n\n{e}"

        try:
            os.remove(tmpPath)
        except:
            pass

        wx.MessageDialog(None, msg, "", wx.OK).ShowModal()
        return None


class ExportDialog(wx.Dialog):
    def __init__(self, parent, exporter):
        super().__init__(parent, title="Export Stack", size=(parent.FromDIP(500), parent.FromDIP(400)))
        self.exporter = exporter

        self.panel = wx.Panel(self)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        spacing = self.FromDIP(5)

        self.items = list(self.exporter.resList)

        addBtn = wx.Button(self.panel, label = "Add", size=(self.FromDIP(50), self.FromDIP(20)))
        addBtn.Bind(wx.EVT_BUTTON, self.OnAdd)

        rmBtn = wx.Button(self.panel, label = "Remove", size=(self.FromDIP(50), self.FromDIP(20)))
        rmBtn.Bind(wx.EVT_BUTTON, self.OnRemove)

        exportAppBtn = wx.Button(self.panel, label = "Export as App", size=(self.FromDIP(50), self.FromDIP(20)))
        exportAppBtn.Bind(wx.EVT_BUTTON, self.OnExportApp)

        exportWebBtn = wx.Button(self.panel, label = "Upload to Web", size=(self.FromDIP(50), self.FromDIP(20)))
        exportWebBtn.Bind(wx.EVT_BUTTON, self.OnExportWeb)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(addBtn, 1, wx.EXPAND|wx.ALL, spacing)
        buttonSizer.Add(rmBtn, 1, wx.EXPAND|wx.ALL, spacing)
        buttonSizer.Add(exportAppBtn, 1, wx.EXPAND|wx.ALL, spacing)
        buttonSizer.Add(exportWebBtn, 1, wx.EXPAND|wx.ALL, spacing)

        isLoggedIn = False
        username = self.exporter.stackManager.designer.configInfo["upload_username"]
        if username:
            isLoggedIn = True
            self.logoutBtn = wx.Button(self.panel, label=f"[Logout '{username}']", style=wx.BORDER_NONE)
            self.logoutBtn.Bind(wx.EVT_BUTTON, self.OnLogOut)

        if len(self.exporter.resList) > 0:
            labelStr = "These are the image and sound files that this stack seems to need.  " \
                       "If you think other files are needed, try running the stack again and make sure to use " \
                       "all of the images and sounds that this stack can.  Or you can add or remove files here by using the " \
                       "buttons below, and when the list is complete, " \
                       "click an \"Export\" button to Export these files along with this stack."
        else:
            labelStr = "No image or sound files seem to be used by this stack.  That's fine, but " \
                       "if you think other files are needed, try running the stack again and make sure to use " \
                       "all of the images and sounds that this stack can.  Or you can add or remove files here by using the " \
                       "buttons below, and when the list is complete, " \
                       "click an \"Export\" button to Export these files along with this stack."

        if len(exporter.moduleList) > 0:
            labelStr += "\n\nFound imports for python modules: " + ", ".join(exporter.moduleList)

        label = wx.StaticText(self.panel, label=labelStr)

        self.listBox = wx.ListBox(self.panel, choices=self.items)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 0, wx.EXPAND|wx.ALL, spacing)
        sizer.Add(self.listBox, 1, wx.EXPAND|wx.ALL, spacing)
        if isLoggedIn:
            sizer.Add(self.logoutBtn, 0, wx.ALL|wx.ALIGN_RIGHT, spacing)
            exportWebBtn.SetDefault()
        else:
            exportAppBtn.SetDefault()
        sizer.Add(buttonSizer, 0, wx.EXPAND|wx.ALL, spacing)
        self.panel.SetSizerAndFit(sizer)
        sizer.Layout()

        label.Wrap(self.GetClientSize().width-spacing*2)
        sizes = wx.MemoryDC().GetFullMultiLineTextExtent(label.GetLabelText(), label.GetFont())
        label.SetSize(wx.Size(label.GetSize().Width, sizes[1]))
        sizer.Layout()
        self.listBox.SetFocus()

    def OnKeyDown(self, event):
        code = event.GetKeyCode()
        if code == wx.WXK_ESCAPE or (code == ord("W") and event.ControlDown()):
            self.Close()
        event.Skip()

    def OnLogOut(self, event):
        self.exporter.stackManager.designer.configInfo["upload_username"] = None
        self.exporter.stackManager.designer.configInfo["upload_token"] = None
        self.exporter.stackManager.designer.WriteConfig()
        self.logoutBtn.Hide()

    def OnAdd(self, event):
        initialDir = os.path.dirname(self.exporter.stackManager.filename)
        dlg = wx.FileDialog(self.exporter.stackManager.designer, "Add Resource File(s)", initialDir,
                            "",
                            style=wx.FD_OPEN | wx.FD_MULTIPLE,
                            wildcard="Any File (*)|*")
        if dlg.ShowModal() == wx.ID_OK:
            for filepath in dlg.GetPaths():
                path = filepath
                try:
                    path = os.path.relpath(path, os.path.dirname(self.exporter.stackManager.filename))
                except:
                    pass
                self.items.append(path)
            self.listBox.SetItems(self.items)
        dlg.Destroy()

    def OnRemove(self, event):
        i = self.listBox.GetSelection()
        if i != wx.NOT_FOUND:
            del self.items[i]
            self.listBox.SetItems(self.items)
            self.listBox.SetSelection(min(i, len(self.items)-1))

    def OnExportApp(self, event):
        self.SetTitle("Exporting Stack...")
        self.panel.Enable(False)
        wx.YieldIfNeeded()
        self.exporter.resList = set(self.items)
        self.exporter.ExportApp()
        self.exporter = None
        self.Close()

    def OnExportWeb(self, event):
        # Generate Thumbnail
        self.exporter.stackManager.designer.runnerFinishedCallback = self.OnExportWeb_Part2
        self.panel.Enable(False)
        self.exporter.stackManager.designer.RunFromCard(0, generateThumbnail=True)
        self.stillExporting = True
        def ExportTimeout():
            if self.exporter and self.stillExporting:
                self.exporter.stackManager.designer.viewer.MakeThumbnail()
        wx.CallLater(1000, ExportTimeout)

    def OnExportWeb_Part2(self):
        self.stillExporting = False
        self.exporter.stackManager.designer.runnerFinishedCallback = None
        username = self.exporter.stackManager.designer.configInfo["upload_username"]
        if username:
            self.SetTitle("Uploading Stack...")
            self.panel.Enable(False)
            wx.YieldIfNeeded()
            self.exporter.resList = set(self.items)
            url = self.exporter.ExportWeb()
            if url:
                self.exporter = None
                self.items = None
                self.Close()
            else:
                self.panel.Enable(True)
        else:
            dlg = LoginDialog(self.GetParent(), self.exporter, self.items)
            self.exporter = None
            self.Close()
            dlg.ShowModal()


class LoginDialog(wx.Dialog):
    def __init__(self, parent, exporter, items):
        super().__init__(parent, title="Login for Upload")

        self.exporter = exporter
        self.items = items

        self.panel = wx.Panel(self)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        spacing = 5
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        cancelBtn = wx.Button(self.panel, label = "Cancel")
        cancelBtn.Bind(wx.EVT_BUTTON, self.OnCancel)
        buttonSizer.AddStretchSpacer()
        buttonSizer.Add(cancelBtn, 1, wx.EXPAND | wx.ALL, spacing)

        labelStr = f"You are not yet logged in to {CSWEB_DISPLAY_NAME}.  Please Log In if you already have an account.  " \
                   f"Otherwise please Sign Up, and then Log In once you have an account."

        user_sizer = wx.BoxSizer(wx.HORIZONTAL)
        user_lbl = wx.StaticText(self.panel, label="Username:")
        user_sizer.Add(user_lbl, 0, wx.ALL | wx.CENTER, spacing)
        self.userField = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
        self.userField.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)
        user_sizer.Add(self.userField, 1, wx.EXPAND | wx.ALL, spacing)

        pass_sizer = wx.BoxSizer(wx.HORIZONTAL)
        p_lbl = wx.StaticText(self.panel, label="Password:")
        pass_sizer.Add(p_lbl, 0, wx.ALL | wx.CENTER, spacing)
        self.passField = wx.TextCtrl(self.panel, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        self.passField.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)
        pass_sizer.Add(self.passField, 1, wx.EXPAND | wx.ALL, spacing)

        signupBtn = wx.Button(self.panel, label="Sign Up")
        signupBtn.Bind(wx.EVT_BUTTON, self.OnSignUp)
        buttonSizer.Add(signupBtn, 1, wx.EXPAND | wx.ALL, spacing)

        loginBtn = wx.Button(self.panel, label="Log In")
        loginBtn.Bind(wx.EVT_BUTTON, self.OnLogIn)
        loginBtn.SetDefault()
        buttonSizer.Add(loginBtn, 1, wx.EXPAND | wx.ALL, spacing)

        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self.panel, label=labelStr)
        sizer.Add(label, 1, wx.EXPAND | wx.ALL, spacing*2)
        sizer.Add(user_sizer, 0, wx.EXPAND | wx.ALL, spacing)
        sizer.Add(pass_sizer, 0, wx.EXPAND | wx.ALL, spacing)
        sizer.Add(buttonSizer, 0, wx.EXPAND | wx.ALL, spacing)
        self.panel.SetSizerAndFit(sizer)
        sizer.Layout()
        self.Fit()

        label.Wrap(self.GetClientSize().width-spacing*2)
        sizes = wx.MemoryDC().GetFullMultiLineTextExtent(label.GetLabelText(), label.GetFont())
        label.SetSize(wx.Size(label.GetSize().Width, sizes[1]))

        self.userField.SetFocus()

    def OnKeyDown(self, event):
        code = event.GetKeyCode()
        if code == wx.WXK_ESCAPE or (code == ord("W") and event.ControlDown()):
            self.Close()
        event.Skip()

    def OnTextEnter(self, event):
        username = self.userField.GetValue()
        password = self.passField.GetValue()
        if not len(username):
            self.userField.SetFocus()
        elif len(username) and not len(password):
            self.passField.SetFocus()
        else:
            self.OnLogIn(event)

    def OnSignUp(self, event):
        wx.LaunchDefaultBrowser(CSWEB_SIGNUP_URL)

    def OnLogIn(self, event):
        username = self.userField.GetValue()
        password = self.passField.GetValue()
        params = {"username": username, "password": password}
        response = requests.post(CSWEB_GET_TOKEN_URL, data=params)
        responseJson = response.json()
        if "token" in responseJson:
            self.exporter.stackManager.designer.configInfo["upload_username"] = username
            self.exporter.stackManager.designer.configInfo["upload_token"] = responseJson["token"]
            self.exporter.stackManager.designer.WriteConfig()

            self.exporter.resList = set(self.items)
            url = self.exporter.ExportWeb()
            if url:
                self.exporter = None
                self.items = None
                self.Close()
                return
        wx.MessageDialog(self, "Couldn't Log In").ShowModal()

    def OnCancel(self, event):
        self.exporter = None
        self.items = None
        self.Close()

