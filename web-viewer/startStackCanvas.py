from browser import window, document, timer
import sys
import stackCanvas

window.stackCanvas = stackCanvas.StackCanvas()


class ConsoleOutput:
    # Show output in the console TextArea on the page, if it exists

    def __init__(self, console, consoleLabel):
        self.console = console
        self.consoleLabel = consoleLabel
        self.text = ""
        self.dirty = False
        self.isShown = False

    def write(self, text):
        self.text += text
        self.dirty = True

    def update(self, force=False):
        window.stackCanvas.SendBuffer()
        if console and console.style.display == "block" and (force or self.dirty):
            self.console.text = self.text
            self.console.scrollTop = self.console.scrollHeight
            self.dirty = False

    def toggleConsole(self):
        self.isShown = not self.isShown
        console.style.display = "block" if (self.isShown) else "none"
        if self.isShown:
            self.consoleLabel.text = " (-) Hide Output"
            window.console.update(force=True)
        else:
            self.consoleLabel.text = " (+) Show Output"


if "console" in document and "consoleLabel" in document:
    console = document['console']
    consoleLabel = document['consoleLabel']
    cOutput = ConsoleOutput(console, consoleLabel)
    sys.stdout = cOutput
    sys.stderr = cOutput
    timer.set_interval(cOutput.update, 1000)
    window.console = cOutput
    window.toggleConsole = cOutput.toggleConsole
else:
    timer.set_interval(window.stackCanvas.SendBuffer, 1000)
