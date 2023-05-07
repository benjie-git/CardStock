# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import wx.html2
import requests
import os
import uiImage

'''
The MediaSearchDialogs allow the user to search for images or sounds hosted on openclipart.com, and freesound.com, and
to easily download these and add them into the stack.  Currently this is done using a web browser and intercepting 
certain page loads to automatically download media.  But both sites have proper APIs, so we should switch to those,
and build out a custom searching and browsing UI.
'''


class MediaSearchDialog(wx.Dialog):
    def __init__(self, parent, title, url, cur_dir, callback):
        super().__init__(parent, -1, title,
                          size=(parent.FromDIP(600), parent.FromDIP(600)), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

        self.browser = wx.html2.WebView.New(self)
        self.browser.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.OnLoad)
        self.browser.LoadURL(url)

        self.cur_dir = cur_dir
        self.callback = callback
        self.fileLocation = None

        self.label = wx.StaticText(parent=self, style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.label.SetFont(wx.Font(wx.FontInfo(16).Weight(wx.FONTWEIGHT_BOLD).Family(wx.FONTFAMILY_DEFAULT)))

        # Set up the layout with a Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label, wx.SizerFlags(0).Expand().Border(wx.ALL, 5))
        sizer.Add(self.browser, wx.SizerFlags(1).Expand().Border(wx.ALL, 5))
        self.SetSizer(sizer)
        self.Layout()

    def Close(self, force=False):
        if self.callback:
            self.callback(None)
            self.callback = None
        super().Close(force)

    def RunModal(self):
        self.ShowModal()
        return self.fileLocation

    def OnLoad(self, event):
        pass


class ImageSearchDialog(MediaSearchDialog):
    def __init__(self, parent, cur_dir, callback):
        super().__init__(parent, "Image Search", "https://openclipart.org/", cur_dir, callback)
        self.label.SetLabel("Search for clip art here, and click an image to download and use it.")

    def OnLoad(self, event):
        url = event.GetURL()

        # Keep users on this one site
        if not url.startswith("https://openclipart.org/"):
            event.Veto()
            return

        if "/detail/" in url:
            event.Veto()
            parts = url.split("/")
            image_id = parts[4]
            name = parts[5]
            self.SaveUrl(f"https://openclipart.org/image/400px/{image_id}", name)

    def SaveUrl(self, url, name):
        r = requests.get(url)
        data = r.content
        filename = self.SaveImageData(self, self.cur_dir, name, data)
        if filename:
            self.fileLocation = filename

            if self.callback:
                wx.CallAfter(self.callback, filename)
                self.callback = None

            wx.CallAfter(self.Close)

    @staticmethod
    def SaveImageData(parent, cur_dir, name, data):
        skipWrite = False
        initialDir = os.path.expanduser('~')
        if cur_dir:
            initialDir = cur_dir

        filename = os.path.join(initialDir, name+'.png')
        name, extension = os.path.splitext(filename)
        counter = 1
        while os.path.exists(filename):
            f = open(filename, "rb")
            old_data = f.read()
            f.close()
            if old_data == data:
                skipWrite = True
                break
            filename = name + "_" + str(counter) + extension
            counter += 1

        if not skipWrite:
            f = open(filename, "wb")
            f.write(data)
            f.close()

        uiImage.UiImage.ClearCache(filename)

        if cur_dir:
            try:
                filename = os.path.relpath(filename, cur_dir)
            except:
                pass

        return filename

    # @staticmethod
    # def SaveImageData(parent, cur_dir, name, data):
    #     filename = None
    #     initialDir = os.getcwd()
    #     if cur_dir:
    #         initialDir = cur_dir
    #     wildcard = "PNG files (*.png)|*.png"
    #     dlg = wx.FileDialog(parent, "Save Image as...", initialDir, name + ".png",
    #                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
    #                        wildcard = wildcard)
    #     if dlg.ShowModal() == wx.ID_OK:
    #         filename = dlg.GetPath()
    #         if not os.path.splitext(filename)[1]:
    #             filename = filename + '.png'
    #
    #         f = open(filename, "wb")
    #         f.write(data)
    #         f.close()
    #
    #         uiImage.UiImage.ClearCache(filename)
    #
    #         if cur_dir:
    #             try:
    #                 filename = os.path.relpath(filename, cur_dir)
    #             except:
    #                 pass
    #
    #     dlg.Destroy()
    #     return filename


class AudioSearchDialog(MediaSearchDialog):
    """
    Not currently used, and not complete (downloading doesn't work yet).
    But no rush, since I feel the quality/usefulness of the audio clips at freesound is too low.
    It may make more sense to curate our own small library of audio files to access here.
    """

    def __init__(self, parent, lastOpenFile, callback):
        super().__init__(parent, "Sound Search", "https://freesound.org/", lastOpenFile, callback)
        self.label.SetLabel("Search for sounds here, and click \"Download\" to download and use it.")
        self.referrer = None

    def OnLoad(self, event):
        url = event.GetURL()

        if url.endswith(".wav"):
            event.Veto()
            parts = url.split("/")
            name = parts[-1]
            self.SaveUrl(url, name)
        elif "/sounds/" in url:
            self.referrer = url

    def SaveUrl(self, url, name):
        initialDir = os.path.expanduser('~')
        if self.cur_dir:
            initialDir = self.cur_dir
        wildcard = "WAV files (*.wav)|*.wav"
        dlg = wx.FileDialog(self, "Save Sound as...", initialDir, name,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                           wildcard = wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not os.path.splitext(filename)[1]:
                filename = filename + '.wav'

            # FIXME: Attempt to grab all cookies.  But the sessionId cookie is htmlOnly, so no dice.
            success, cookie_data = self.browser.RunScript("document.cookie")
            cookie_parts = cookie_data.split(';')
            cookies = {}
            for cookie in cookie_parts:
                parts = cookie.split('=')
                if len(parts) == 2:
                    cookies[parts[0]] = parts[1]
            r = requests.get(url, headers={'referer': self.referrer}, cookies=cookies)
            data = r.content

            f = open(filename, "wb")
            f.write(data)
            f.close()

            if self.cur_dir:
                try:
                    filename = os.path.relpath(filename, self.cur_dir)
                except:
                    pass

            self.fileLocation = filename

            if self.callback:
                wx.CallAfter(self.callback, filename)
                self.callback = None

            wx.CallAfter(self.Close)

        dlg.Destroy()
