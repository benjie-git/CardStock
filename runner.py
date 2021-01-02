import traceback
import sys

class Runner():
    def __init__(self, page, sb):
        self.locals = {}
        self.globals = {}
        self.globals["page"] = page
        self.statusBar = sb
        for ui in page.uiViews:
            self.globals[ui.properties["name"]] = ui.view

    def RunHandler(self, uiView, handlerName):
        self.locals["self"] = uiView.view

        handlerStr = uiView.handlers[handlerName]

        error_class = None
        line_number = None
        detail = None

        try:
            exec(handlerStr, self.globals, self.locals)
        except SyntaxError as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            line_number = err.lineno
        except Exception as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            cl, exc, tb = sys.exc_info()
            line_number = traceback.extract_tb(tb)[-1][1]

        if error_class:
            msg = f"{error_class} in {uiView.GetProperty('name')}.{handlerName}(), line {line_number}: {detail}"
            print(msg)
            self.statusBar.SetStatusText(msg)
