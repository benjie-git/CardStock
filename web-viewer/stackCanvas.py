from browser import window, document, worker, bind, timer, ajax
import sys

stackWorker = worker.Worker("stackWorker")

MAX_CANVAS_WIDTH = 800
MAX_CANVAS_HEIGHT = 800


"""
This StackCanvas class, which runs on the main thread, works tightly with the StackWorker class, which runs in a
web worker/background thread.  The StackCanvas is the only code that runs in the main thread of the browser tab.
The StackWorker hosts the StackManager which itself runs the cardstock stack and code.
This class is just a thin layer that:
  - senses events
  - sends event messages to the worker thread that's actually running all of the cardstock code
  - receives messages back from the worker thread about what to show,
  - and updates the canvas, to draw to the screen.
  
The web worker API doesn't allow sharing our model objects between threads.  It allows passing messages, and very simple
shared memory, that we just use for synchronization. 
"""


class StackCanvas(object):
    def __init__(self):
        self.waitSAB = window.SharedArrayBuffer.new(4)
        self.waitSA32 = window.Int32Array.new(self.waitSAB)
        self.countsSAB = window.SharedArrayBuffer.new(4)
        self.countsSA32 = window.Int32Array.new(self.countsSAB)
        self.dataSAB = window.SharedArrayBuffer.new(32768)
        self.dataSA16 = window.Int16Array.new(self.dataSAB)

        self.canvas = document.getElementById('canvas')

        # if self.IsMobileBrowser() and window.navigator.hasOwnProperty("virtualKeyboard"):
        #     window.navigator.virtualKeyboard.overlaysContent = True

        self.fabCanvas = window.fabric.Canvas.new('canvas')
        self.fabCanvas.preserveObjectStacking = True
        self.fabCanvas.selection = False
        self.fabCanvas.renderOnAddRemove = False
        self.fabCanvas.on('mouse:down', self.OnMouseDown)
        self.fabCanvas.on('mouse:move', self.OnMouseMove)
        self.fabCanvas.on('mouse:up', self.OnMouseUp)
        # self.fabCanvas.on('touchstart', self.OnTouchStart)
        # self.fabCanvas.on('touchmove', self.OnTouchMove)
        # self.fabCanvas.on('touchend', self.OnTouchEnd)
        # self.fabCanvas.on('touchcancel', self.OnTouchEnd)
        self.fabCanvas.on('text:changed', self.OnTextChanged)
        document.onkeydown = self.OnKeyDown
        document.onkeyup = self.OnKeyUp
        window.onresize = self.OnWindowResize

        self.fabObjs = {0: self.fabCanvas}
        self.canvasSize = (0, 0)
        self.imgCache = {}
        self.lastMousePos = (0,0)
        self.writeBuffer = ""
        self.resourceMap = {}
        self.canResize = False
        self.didRenderOnce = False

        stackWorker.bind("message", self.OnMessageM)

        # Send over references to the shared memory chunks to get the worker set up.
        stackWorker.send(('setup', self.waitSAB, self.countsSAB, self.dataSAB))

        # Load up the embedded stack
        if 'resourceMap' in window:
            self.resourceMap = window.resourceMap.to_dict()
        stackWorker.send(('load', window.stackJSON))

        # Pre-load all sounds in the resourceMap
        self.soundCache = {}
        for key,path in self.resourceMap.items():
            snd = window.Howl.new({'src': [path]})
            self.soundCache[key] = snd

        self.OnWindowResize(None, force=True)

    def LoadFromStr(self, s):
        stackWorker.send(('loadStr', s))

    # Redraw, only if we're done loading a page (to avoid briefly showing objects that get hidden or moved on startup)
    # We also try to minimize UI updates, and only display changes once per frame (~60Hz), and then only if something
    # actually changed.
    def Render(self):
        self.fabCanvas.renderAll()

    def OnMessageM(self, evt):
        """Handles the messages sent by the worker, which are sent as lists of messages."""
        for msg in evt.data:
            self.HandleOneMessage(msg)

    def HandleOneMessage(self, message):
        msg = message[0]
        args = message[1:]

        # if msg != "write": print("Main", msg, args)

        if msg == "canvasSetSize":  # x, y, canResize
            document.getElementById("loadingDiv").style.display = "none"
            self.canvasSize = (args[0], args[1])
            self.canResize = args[2]
            self.fabCanvas.setWidth(self.canvasSize[0])
            self.fabCanvas.setHeight(self.canvasSize[1]+2)
            self.canvas.style.border = "1px solid black"

        elif msg == "fabNew":  # uid, type, [other args,] options
            # Add a new object to the canvas
            uid = args[0]
            fabClass = window.fabric[args[1]]
            options = {'csid': uid,
                       'isType': args[1],
                       'selectable': False,
                       'hoverCursor': "arrow"}
            options.update(args[-1].to_dict())
            fabObj = fabClass.new(*(args[2:-1]), options)
            fabObj.set()
            self.fabObjs[uid] = fabObj
            self.fabCanvas.add(fabObj)

        elif msg == "imgNew":  # uid, filePath
            # Add a new Image object to the canvas
            # this requires loading the image, telling the Worker its size, and then possibly cropping it and resizing,
            # which happens later in an "imgRefit" message
            uid = args[0]
            filePath = args[1]

            # Set up placeholder rect
            fabObj = window.fabric.Rect.new(
                {'csid': uid,
                 'isType': "Rect",
                 'strokeWidth': 0,
                 'selectable': False,
                 'hoverCursor': "arrow",
                 'filePath': filePath})
            self.fabObjs[uid] = fabObj
            self.fabCanvas.add(fabObj)

            def didLoad(img, failed):
                if not failed:
                    if filePath not in self.imgCache:
                        self.imgCache[filePath] = img
                    s = self.imgCache[filePath].getOriginalSize()
                    stackWorker.send(("imgSize", uid, s.width, s.height))

            if filePath in self.imgCache:
                s = self.imgCache[filePath].getOriginalSize()
                stackWorker.send(("imgSize", uid, s.width, s.height))
            else:
                if filePath in self.resourceMap:
                    window.fabric.Image.fromURL(self.resourceMap[filePath], didLoad)
                else:
                    window.fabric.Image.fromURL("Resources/"+filePath, didLoad)

        elif msg == "imgReplace":  # uid, filePath
            # download a new image to use to replace the current one.  used when user code sets an image.file
            uid = args[0]
            filePath = args[1]
            oldObj = self.fabObjs[uid]
            oldObj['filePath'] = filePath
            index = [o.csid for o in self.fabCanvas.getObjects()].index(oldObj.csid)

            def didLoad(img, failed):
                if not failed:
                    if filePath not in self.imgCache:
                        self.imgCache[filePath] = img
                    s = self.imgCache[filePath].getOriginalSize()
                    stackWorker.send(("imgSize", uid, s.width, s.height))

            if filePath in self.imgCache:
                s = self.imgCache[filePath].getOriginalSize()
                stackWorker.send(("imgSize", uid, s.width, s.height))
            else:
                if filePath in self.resourceMap:
                    window.fabric.Image.fromURL(self.resourceMap[filePath], didLoad)
                else:
                    window.fabric.Image.fromURL("Resources/"+filePath, didLoad)

        elif msg == "imgRefit":  # uid, options
            # crop and resize as needed
            uid = args[0]
            options = args[1]
            oldObj = self.fabObjs[uid]
            origImage = self.imgCache[oldObj.filePath]
            index = [o.csid for o in self.fabCanvas.getObjects()].index(oldObj.csid)
            self.fabCanvas.remove(oldObj)

            def setImg(img):
                img.set({'csid': uid,
                         'isType': "Image",
                         'scaleX': options['scaleX'], 'scaleY': options['scaleY'],
                         'angle': options['angle'],
                         'selectable': False,
                         'hoverCursor': "arrow",
                         'filePath': oldObj.filePath,
                         'left': int(options['left']), 'top': int(options['top']),
                         'visible': options['visible']
                         })
                self.fabObjs[uid] = img
                img.setCoords()
                self.fabCanvas.insertAt(img, index, False)
                if self.didRenderOnce:
                    self.Render()

            origImage.cloneAsImage(setImg, {'left': int(options['clipLeft']), 'top': int(options['clipTop']),
                                            'width': int(options['clipWidth']), 'height': int(options['clipHeight'])})

        elif msg == "fieldNew":  # uid, text, options
            # Add a new TextField object to the canvas
            uid = args[0]
            text = args[1]
            fabObj = window.fabric.Textbox.new(text, args[2])

            fabObj.set({'csid': uid,
                        'isType': 'TextField',
                        'hasControls': False,
                        'lockMovementX': True,
                        'lockMovementY': True,
                        'hoverCursor': "text"})
            self.fabObjs[uid] = fabObj

            self.fabCanvas.add(fabObj)
            fabObj.on('selected', self.OnTextFieldSelected)
            fabObj.on('deselected', self.OnTextFieldDeselected)
            fabObj.oldOnKeyDown = fabObj.onKeyDown
            fabObj.onKeyDown = self.OnTextFieldKeyDown

        elif msg == "fabReplace":  # uid, type, options
            # replace a fabric object with this one (used when user code sets line.points)
            uid = args[0]

            oldObj = self.fabObjs[uid]
            index = [o.csid for o in self.fabCanvas.getObjects()].index(oldObj.csid)
            self.fabCanvas.remove(oldObj)

            fabClass = window.fabric[args[1]]
            fabObj = fabClass.new(*args[2:])
            fabObj.set({'csid':uid,
                        'isType': args[1],
                        'selectable': False,
                        'hoverCursor': "arrow"})
            self.fabObjs[uid] = fabObj
            self.fabCanvas.insertAt(fabObj, index, False)

        elif msg == "fabDel":  # uid, [more uids...]
            # delete objects from the canvas
            for uid in args:
                if uid in self.fabObjs:
                    fabObj = self.fabObjs[uid]
                    del self.fabObjs[uid]
                    if fabObj.isType == 'TextField':
                        fabObj.off('selected', self.OnTextFieldSelected)
                        fabObj.off('deselected', self.OnTextFieldDeselected)
                    self.fabCanvas.remove(fabObj)
                else:
                    print("Delete: no object with uid", uid)

        elif msg == "fabFunc":  # uid, funcName, [args...]
            # call a fabric function on an object by name
            uid = args[0]
            fabObj = self.fabObjs[uid]
            fabFunc = fabObj[args[1]]
            fabFunc(*args[2:])
            # if uid == 0 and args[1] == "setBackgroundColor":
            #     document.body.style.backgroundColor = args[2]

        elif msg == "fabSet":  # uid, options
            # update a fabric object's options
            uid = args[0]
            options = args[1]
            fabObj = self.fabObjs[uid]
            fabObj.set(options)
            options = options.to_dict()
            if 'left' in options or 'width' in options:
                fabObj.setCoords()

        elif msg == "fabReorder":  # uid, index
            # change an object's z-order
            uid = args[0]
            index = args[1]
            fabObj = self.fabObjs[uid]
            self.fabCanvas.moveTo(fabObj, index)

        elif msg == "render":  # No args
            self.Render()
            self.didRenderOnce = True

        elif msg == "fabLabelAutoSize":
            uid = args[0]
            fabObj = self.fabObjs[uid]
            self.UpdateTextSize(fabObj)

        elif msg == "focus":  # uid
            # focus a textfield
            uid = args[0]
            if not self.fabCanvas.getActiveObject() or self.fabCanvas.getActiveObject().csid != uid:
                field = self.fabObjs[uid]
                self.fabCanvas.setActiveObject(field)
                field.enterEditing()
                length = len(field.text)
                field.setSelectionStart(length)
                field.setSelectionEnd(length)
                if self.IsMobileBrowser() and window.navigator.hasOwnProperty("virtualKeyboard"):
                    print("Show!")
                    window.navigator.virtualKeyboard.show()

        elif msg == "alert":  # text
            # open an alert (Just an OK button).  first make sure our render is up to date, by requesting a render
            # and waiting for the next frame.  then actually open the alert.  The Worker will wait until the user
            # closes the alert, so we need to update waitSA32[0] and notify that it has been updated,since this is
            # what the Worker is waiting on.
            self.fabCanvas.requestRenderAll()
            timer.set_timeout(self.HandleOneMessage, 20, ("alertInternal", *args))
        elif msg == "alertInternal":
            text = args[0]
            window.alert(text)
            self.dataSA16[0] = 0
            self.waitSA32[0] = 1
            window.Atomics.notify(self.waitSA32, 0)

        elif msg == "confirm":  # text
            # open a confirmation alert (OK/Cancel buttons).  But first make sure our render is up to date, by
            # requesting a render and waiting for the next frame.  then actually open the alert.  The Worker will
            # wait until the user closes the alert, so we need to update waitSA32[0] and notify that it has been
            # updated,since this is what the Worker is waiting on.  And we also update dataSA16[0] to send back the
            # result: Ok vs. Cancel.
            self.fabCanvas.requestRenderAll()
            timer.set_timeout(self.HandleOneMessage, 20, ("confirmInternal", *args))
        elif msg == "confirmInternal":
            text = args[0]
            result = window.confirm(text)
            self.dataSA16[0] = result
            self.waitSA32[0] = 1
            window.Atomics.notify(self.waitSA32, 0)

        elif msg == "prompt":  # text, [defaultResponseText]
            # open a prompt alert (Text field and OK/Cancel buttons).  But first make sure our render is up to date, by
            # requesting a render and waiting for the next frame.  then actually open the alert.  The Worker will
            # wait until the user closes the alert, so we need to update waitSA32[0] and notify that it has been
            # updated,since this is what the Worker is waiting on.  And we also update dataSA16 to send back the
            # result: dataSA16[0] holds the length, and then the following int16 values hold the data as unicode values.
            self.fabCanvas.requestRenderAll()
            timer.set_timeout(self.HandleOneMessage, 20, ("promptInternal", *args))
        elif msg == "promptInternal":
            text = args[0]
            default = "" if len(args) < 2 else args[1]
            result = window.prompt(text, default)
            if result is not None:
                self.dataSA16[0] = len(result)
                for i in range(len(result)):
                    self.dataSA16[i+1] = ord(result[i])
            else:
                self.dataSA16[0] = -1  # Flag to return None
            self.waitSA32[0] = 1
            window.Atomics.notify(self.waitSA32, 0)

        elif msg == "playAudio":  # filePath
            # play an audio file
            file = args[0]
            self.soundCache[file].play()
            if file in self.resourceMap:
                path = self.resourceMap[file]
                snd = window.Howl.new({'src': [path]})
                snd.play()

        elif msg == "stopAudio":  # No args
            # stop all audio
            window.Howler.stop()

        elif msg == "write":  # text
            # Allows printing from the worker thread
            print(args[0], end='')

        elif msg == "echo":  # args
            # pop the first arg ("echo") and send back the rest.
            # This is used from the worker to queue up a message in its own message queue
            stackWorker.send(args)

        else:
            print("StackCanvas received bad msg:", msg)

    def IsMobileBrowser(self):
        toMatch = ["Android", "webOS", "iPhone", "iPad", "iPod", "Windows Phone"]
        ua = window.navigator.userAgent
        for m in toMatch:
            if m in ua:
                return True
        return False

    def SendBuffer(self):
        # print out any buffered writes from the worker thread's print() calls
        if len(self.writeBuffer):
            print(window.stackCanvas.writeBuffer, end='')
            self.writeBuffer = ""

    def ConvPoint(self, x, y):
        rect = self.canvas.getBoundingClientRect()
        # Flip coords vertically to match cardstock: (0,0) = Bottom Left
        return (x-rect.left, self.canvasSize[1] - y + rect.top)

    def OnMouseDown(self, options):
        uid = 0
        if options.target:
            uid = options.target.csid
            if options.target.isType == "TextField":
                self.OnTextFieldMouseDown(options.target, options.e)
        if "touch" in options.e.type:
            isTouch = True
            pos = (options.e.touches[0].clientX, options.e.touches[0].clientY)
        else:
            isTouch = False
            pos = (options.e.clientX, options.e.clientY)
        self.DoMouseDown(uid, pos[0], pos[1], isTouch)

    def DoMouseDown(self, uid, x, y, isTouch):
        # Flip points vertically and send to the worker.  Also fix TextField selection on click.
        pos = self.ConvPoint(x, y)
        self.lastMousePos = pos
        stackWorker.send(("mouseDown", uid, pos, isTouch))

    def OnMouseMove(self, options):
        uid = 0
        if options.target:
            uid = options.target.csid
        if options.e.type.startswith("touch"):
            isTouch = True
            pos = (options.e.touches[0].clientX, options.e.touches[0].clientY)
        else:
            isTouch = False
            pos = (options.e.clientX, options.e.clientY)
        self.DoMouseMove(uid, pos[0], pos[1], isTouch)

    def DoMouseMove(self, uid, x, y, isTouch):
        # Flip points vertically and send to the worker.
        pos = self.ConvPoint(x, y)
        if pos[0] != self.lastMousePos[0] or pos[1] != self.lastMousePos[1]:
            self.lastMousePos = pos
            # keep track of how many OnMouseMove calls are pending, so the worker doesn't get bogged down
            # if it's slow to process these
            window.Atomics.add(self.countsSA32, 0, 1)
            stackWorker.send(("mouseMove", uid, pos, isTouch))

    def OnMouseUp(self, options):
        uid = 0
        if options.target:
            uid = options.target.csid
        if options.e.type.startswith("touch"):
            isTouch = True
            pos = self.lastMousePos
        else:
            isTouch = False
            pos = (options.e.clientX, options.e.clientY)
        self.DoMouseUp(uid, pos[0], pos[1], isTouch)

    def DoMouseUp(self, uid, x, y, isTouch):
        # Flip points vertically and send to the worker.
        pos = self.ConvPoint(x, y)
        self.lastMousePos = pos
        stackWorker.send(("mouseUp", uid, pos, isTouch))

    def OnKeyDown(self, e):
        # Don't tab focus out of the canvas
        # forward these events on to the worker
        if e.key == "Tab":
            e.preventDefault()
        if not e.repeat:
            stackWorker.send(("keyDown", e.key))

    def OnKeyUp(self, e):
        # forward these events on to the worker
        stackWorker.send(("keyUp", e.key))

    def UpdateTextSize(self, fab):
        if fab.autoShrink:
            s = fab.origFontSize
            fab.set({'fontSize': s})
            if fab.autoShrink:
                while s > 4 and fab.calcTextHeight() > fab.height:
                    s -= 1
                    fab.set({'fontSize': s})

    def OnTextFieldMouseDown(self, field, e):
        # Start text selection on a mouse down in a text field
        self.fabCanvas.setActiveObject(field)
        field.enterEditing()
        field.setCursorByClick(e)

    def OnTextFieldKeyDown(self, e):
        # Forward arrow keys to the card, and catch Enter/Return so we can run "OnEnter"
        # Also avoid adding newlines to non-multiline text fields
        fabObj = self.fabCanvas.getActiveObject()
        if fabObj and fabObj.isType == 'TextField':
            fabObj.oldOnKeyDown(e)
            if not e.repeat:
                if "Arrow" in e.key:
                    self.OnKeyDown(e)
                if e.key in ("Enter", "Return"):
                    if not fabObj.isMultiline:
                        e.preventDefault()
                    stackWorker.send(("textEnter", fabObj.csid))

    def OnTextFieldSelected(self, options):
        # tell the worker that the field got focused
        fabObj = options.target
        stackWorker.send(("objectFocus", fabObj.csid))

    def OnTextChanged(self, options):
        # Tell the worker that the field's text changed
        uid = options.target.csid
        textbox = self.fabObjs[uid]
        stackWorker.send(("textChanged", uid, textbox.text))

    def OnTextFieldDeselected(self, options):
        # tell the worker that the field got un-focused
        fabObj = options.target
        fabObj.exitEditing()
        fabObj = self.fabCanvas.getActiveObject()
        if not fabObj:
            stackWorker.send(("objectFocus", 0))

    def OnWindowResize(self, _e, force=False):
        # tell the worker that the window resized
        if self.canResize or force:
            self.canvas.style.border = "1px solid transparent"
            self.fabCanvas.setWidth(0)
            self.fabCanvas.setHeight(0)
            canvasDiv = document.getElementById('canvasContainer')
            stackWorker.send(("windowSized", min(MAX_CANVAS_WIDTH, canvasDiv.scrollWidth),
                                             min(MAX_CANVAS_HEIGHT, canvasDiv.scrollHeight)))


class ConsoleOutput:
    """
    Show output in the console TextArea on the page, if it exists
    """
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



if __name__ == "__main__":

    window.stackCanvas = StackCanvas()

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
