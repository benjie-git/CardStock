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
        container = wx.Window(parent=stackManager.view)
        super().__init__(parent, stackManager, model, container)
        self.CreateWebView(container)

    def GetCursor(self):
        return None

    def CreateWebView(self, container):
        s = self.model.GetProperty("size")

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

            pos = wx.Point(0,0)-list(self.model.GetProperty("position"))
            f = self.model.GetFrame()
            f.Inflate(2)
            f.Offset(pos)
            gc.DrawRectangle(f)

    def OnWillLoad(self, event):
        allowedHosts = self.model.GetProperty("allowedHosts")
        url = event.GetURL()
        parts = urlparse(url)
        if len(allowedHosts):
            if "http" in parts.scheme:
                allowed = False
                for h in allowedHosts:
                    if parts.hostname.endswith(h):
                        allowed = True
                        break
                if not allowed:
                    event.Veto()
                    self.OnDidError(event)
                    return
        if parts.scheme == "cardstock":
            event.Veto()
            if self.stackManager.runner and self.model and self.model.GetHandler("OnCardStockLink"):
                wx.CallAfter(self.stackManager.runner.RunHandler, self.model, "OnCardStockLink", event,
                             url[10:])

    def OnDidLoad(self, event):
        if not self.stackManager.isEditing:
            url = event.GetURL()
            if url not in ("file:///", "about:blank"):
                self.model.SetProperty("URL", url, notify=False)
                if self.stackManager.runner and self.model and self.model.GetHandler("OnDoneLoading"):
                    wx.CallAfter(self.stackManager.runner.RunHandler, self.model, "OnDoneLoading", event, (url, True))
        event.Skip()

    def OnDidError(self, event):
        if not self.stackManager.isEditing:
            url = event.GetURL()
            if url != "file:///" and not url.startswith("cardstock:"):
                if self.stackManager.runner and self.model and self.model.GetHandler("OnDoneLoading"):
                    wx.CallAfter(self.stackManager.runner.RunHandler, self.model, "OnDoneLoading", event, (url, False))
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
        handlers = {"OnSetup": "", "OnDoneLoading": "", "OnCardStockLink": ""}
        for k,v in self.handlers.items():
            if "Mouse" not in k:
                handlers[k] = v
        self.handlers = handlers
        self.initialEditHandler = "OnDoneLoading"

        self.properties["name"] = "webview_1"
        self.properties["URL"] = ""
        self.properties["HTML"] = ""
        self.properties["allowedHosts"] = []
        self.propertyTypes["URL"] = "string"
        self.propertyTypes["HTML"] = "string"
        self.propertyTypes["allowedHosts"] = "list"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "URL", "allowedHosts", "position", "size"]

    def SetProperty(self, key, value, notify=True):
        if key == "URL":
            if len(value):
                parts = urlparse(value)
                if not parts.scheme:
                    value = "https://" + value
        elif key == "allowedHosts":
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
    def allowedHosts(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("allowedHosts")
    @allowedHosts.setter
    def allowedHosts(self, val):
        if not isinstance(val, (list, tuple)):
            raise TypeError("allowedHosts must be set to a list value")
        model = self._model
        if not model: return
        model.SetProperty("allowedHosts", val)

    @property
    @RunOnMainSync
    def canGoBack(self):
        ui = self._model.stackManager.GetUiViewByModel(self._model)
        if ui:
            return ui.webView.CanGoBack()
        return False

    @property
    @RunOnMainSync
    def canGoForward(self):
        ui = self._model.stackManager.GetUiViewByModel(self._model)
        if ui:
            return ui.webView.CanGoForward()
        return False

    @RunOnMainSync
    def GoBack(self):
        ui = self._model.stackManager.GetUiViewByModel(self._model)
        if ui:
            ui.webView.GoBack()

    @RunOnMainSync
    def GoForward(self):
        ui = self._model.stackManager.GetUiViewByModel(self._model)
        if ui:
            ui.webView.GoForward()

    def RunJavaScript(self, code):
        ui = self._model.stackManager.GetUiViewByModel(self._model)
        if ui:
            return ui.RunJavaScript(code)
        return None
