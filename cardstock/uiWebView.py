# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
from uiView import *
from urllib.parse import urlparse
import wx.html2


class UiWebView(UiView):
    """
    This class is a controller that coordinates management of a WebView, based on data from a WebViewModel.
    """

    def __init__(self, parent, stackManager, model):
        self.stackManager = stackManager
        self.model = None
        self.cover = None
        self.webView = None
        stackManager.view.Freeze()
        container = wx.Window(parent=stackManager.view)
        super().__init__(parent, stackManager, model, container)
        self.CreateWebView(container)
        stackManager.view.Thaw()

    def GetCursor(self):
        return None

    def CreateWebView(self, container):
        s = self.view.FromDIP(self.model.GetProperty("size"))
        self.webView = wx.html2.WebView.New(container, size=s)
        self.webView.RegisterHandler(wx.html2.WebViewFSHandler('cardstock'))
        self.webView.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.OnWillLoad)
        self.webView.Bind(wx.html2.EVT_WEBVIEW_NAVIGATED, self.OnDidLoad)
        self.webView.Bind(wx.html2.EVT_WEBVIEW_ERROR, self.OnDidError)
        if self.stackManager.isEditing:
            self.webView.Disable()
            self.cover = wx.Window(parent=container, size=s)
            self.BindEvents(self.cover)

        url = self.model.GetProperty("URL")
        if url and len(url):
            self.webView.LoadURL(url)

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "URL":
            if self.webView:
                url = str(self.model.GetProperty(key))
                if len(url):
                    self.webView.LoadURL(url)
                else:
                    self.webView.SetPage("", "")
        elif key == "HTML":
            if self.webView:
                html = str(self.model.GetProperty(key))
                self.webView.SetPage(html, "")
        elif key == "size":
            s = self.view.GetSize()
            if self.webView:
                self.webView.SetSize(s)
            if self.cover:
                self.cover.SetSize(s)

    def PaintBoundingBox(self, gc, color='Gray'):
        if self.stackManager.isEditing:
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.SetPen(wx.Pen(color, 1, wx.PENSTYLE_DOT))

            pos = wx.Point(0,0)-tuple(int(x) for x in self.model.GetProperty("position"))
            f = self.model.GetFrame()
            f.Inflate(2)
            f.Offset(pos)
            gc.DrawRectangle(f)

    def OnWillLoad(self, event):
        allowed_hosts = self.model.GetProperty("allowed_hosts")
        url = event.GetURL()
        parts = urlparse(url)
        if len(allowed_hosts):
            if "http" in parts.scheme:
                allowed = False
                for h in allowed_hosts:
                    if parts.hostname.endswith(h):
                        allowed = True
                        break
                if not allowed:
                    event.Veto()
                    self.OnDidError(event)
                    return
        if parts.scheme == "cardstock":
            event.Veto()
            if not self.stackManager.isEditing and self.stackManager.runner and self.model and self.model.GetHandler("on_card_stock_link"):
                wx.CallAfter(self.stackManager.runner.RunHandler, self.model, "on_card_stock_link", event,
                             url[10:])

    def OnDidLoad(self, event):
        if not self.stackManager.isEditing:
            url = event.GetURL()
            if url not in ("file:///", "about:blank"):
                self.model.SetProperty("URL", url, notify=False)
                if self.stackManager.runner and self.model and self.model.GetHandler("on_done_loading"):
                    wx.CallAfter(self.stackManager.runner.RunHandler, self.model, "on_done_loading", event, (url, True))
        event.Skip()

    def OnDidError(self, event):
        if not self.stackManager.isEditing:
            url = event.GetURL()
            if url != "file:///" and not url.startswith("cardstock:"):
                if self.stackManager.runner and self.model and self.model.GetHandler("on_done_loading"):
                    wx.CallAfter(self.stackManager.runner.RunHandler, self.model, "on_done_loading", event, (url, False))
        event.Skip()

    @RunOnMainSync
    def RunJavaScript(self, code):
        success, result = self.webView.RunScript(code)
        if success:
            return result
        return None


class WebViewModel(ViewModel):
    """
    This is the model for a WebView object.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "webview"
        self.proxyClass = WebView

        # Add custom handlers to the top of the list
        handlers = {"on_setup": "", "on_done_loading": "", "on_card_stock_link": ""}
        for k,v in self.handlers.items():
            if "Mouse" not in k:
                handlers[k] = v
        self.handlers = handlers
        self.initialEditHandler = "on_done_loading"

        self.properties["name"] = "webview_1"
        self.properties["URL"] = ""
        self.properties["HTML"] = ""
        self.properties["allowed_hosts"] = []
        self.propertyTypes["URL"] = "string"
        self.propertyTypes["HTML"] = "string"
        self.propertyTypes["allowed_hosts"] = "list"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "URL", "allowed_hosts", "position", "size"]

    def SetProperty(self, key, value, notify=True):
        if key == "URL":
            if len(value):
                parts = urlparse(value)
                if not parts.scheme:
                    value = "https://" + value
        elif key == "allowed_hosts":
            if isinstance(value, (list, tuple)):
                value = [str(i) for i in value]
        super().SetProperty(key, value, notify)


class WebView(ViewProxy):
    """
    WebView proxy objects are the user-accessible objects exposed to event handler code for WebView objects.
    """

    @property
    def URL(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("URL")
    @URL.setter
    def URL(self, val):
        if not isinstance(val, str):
            raise TypeError("URL must be set to a string value")
        model = self._model
        if not model: return
        model.SetProperty("HTML", "", notify=False)
        model.SetProperty("URL", str(val))

    @property
    def HTML(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("HTML")
    @HTML.setter
    def HTML(self, val):
        if not isinstance(val, str):
            raise TypeError("HTML must be set to a string value")
        model = self._model
        if not model: return
        model.SetProperty("URL", "", notify=False)
        model.SetProperty("HTML", str(val))

    @property
    def allowed_hosts(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("allowed_hosts")
    @allowed_hosts.setter
    def allowed_hosts(self, val):
        if not isinstance(val, (list, tuple)):
            raise TypeError("allowed_hosts must be set to a list value")
        model = self._model
        if not model: return
        model.SetProperty("allowed_hosts", val)

    @property
    @RunOnMainSync
    def can_go_back(self):
        ui = self._model.stackManager.GetUiViewByModel(self._model)
        if ui:
            return ui.webView.CanGoBack()
        return False

    @property
    @RunOnMainSync
    def can_go_forward(self):
        ui = self._model.stackManager.GetUiViewByModel(self._model)
        if ui:
            return ui.webView.CanGoForward()
        return False

    @RunOnMainSync
    def go_back(self):
        ui = self._model.stackManager.GetUiViewByModel(self._model)
        if ui:
            ui.webView.GoBack()

    @RunOnMainSync
    def go_forward(self):
        ui = self._model.stackManager.GetUiViewByModel(self._model)
        if ui:
            ui.webView.GoForward()

    def run_java_script(self, code):
        ui = self._model.stackManager.GetUiViewByModel(self._model)
        if ui:
            return ui.RunJavaScript(code)
        return None
