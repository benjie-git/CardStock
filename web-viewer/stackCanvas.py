# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

from browser import window as context
from browser import document, worker, timer, ajax


MAX_CANVAS_WIDTH = 1000
MAX_CANVAS_HEIGHT = 1000


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
        self.stackWorker = None
        worker.create_worker("stackWorker", onready=self.OnReady, onmessage=self.OnMessageM, onerror=None)

        self.waitSAB = context.SharedArrayBuffer.new(4)
        self.waitSA32 = context.Int32Array.new(self.waitSAB)
        self.countsSAB = context.SharedArrayBuffer.new(4)
        self.countsSA32 = context.Int32Array.new(self.countsSAB)
        self.dataSAB = context.SharedArrayBuffer.new(32768)
        self.dataSA16 = context.Int16Array.new(self.dataSAB)

        self.canvas = document.getElementById('canvas')

        self.fabCanvas = context.fabric.Canvas.new('canvas')
        self.fabCanvas.preserveObjectStacking = True
        self.fabCanvas.selection = False
        self.fabCanvas.renderOnAddRemove = False

        self.fabObjs = {0: self.fabCanvas}
        self.canvasSize = (0, 0)
        self.imgCache = {}
        self.lastMousePos = (0,0)
        self.writeBuffer = ""
        self.resourceMap = {}
        self.canResize = False
        self.isDoneLoading = False
        self.isUsingTouch = False
        self.isMouseDown = False
        self.activeAlert = None
        self.needsResize = False

    def OnReady(self, w):
        self.stackWorker = w

        self.fabCanvas.on('mouse:down', self.OnMouseDown)
        self.fabCanvas.on('mouse:move', self.OnMouseMove)
        self.fabCanvas.on('mouse:up', self.OnMouseUp)
        self.fabCanvas.on('text:changed', self.OnTextChanged)
        document.onkeydown = self.OnKeyDown
        document.onkeyup = self.OnKeyUp
        document.bind("visibilitychange", self.OnTabVisibilityChanged)
        context.bind("blur", self.OnTabFocusLost)
        context.bind("focus", self.OnTabFocused)
        document.addEventListener("touchcancel", self.OnMouseCancel)
        document.bind("mouseup", self.OnMouseDocUp)
        context.onresize = self.OnWindowResize

        # Send over references to the shared memory chunks to get the worker set up,
        # along with the channel name for communicating runtime errors back to the editor tab,
        # if we're running the stack live from the editor.
        channelName = context.channelName if "channelName" in context else ""
        self.stackWorker.send(('setup', self.waitSAB, self.countsSAB, self.dataSAB, channelName))

        # Set up initial window size
        self.OnWindowResize(None, force=True)

        # Load up the embedded stack
        if 'resourceMap' in context:
            self.resourceMap = context.resourceMap.to_dict()
        self.stackWorker.send(('load', context.stackJSON, context.initialCardNumber))

        # Pre-load all sounds in the resourceMap
        self.soundCache = {}
        for key,path in self.resourceMap.items():
            snd = context.Howl.new({'src': [path]})
            self.soundCache[key] = snd

    def LoadFromStr(self, s):
        self.stackWorker.send(('loadStr', s, context.initialCardNumber))

    # Redraw, only if we're done loading a page (to avoid briefly showing objects that get hidden or moved on startup)
    # We also try to minimize UI updates, and only display changes once per frame (~60Hz), and then only if something
    # actually changed.
    def Render(self):
        if self.isDoneLoading:
            self.fabCanvas.renderAll()

    def OnMessageM(self, evt):
        """Handles the messages sent by the worker, which are sent as lists of messages."""
        for msg in evt.data:
            self.HandleOneMessage(msg)

    def HandleOneMessage(self, message):
        msg = message[0]
        args = message[1:]

        # if msg != "write":
        #     pyArgs = args.copy()
        #     for i in range(len(args)):
        #         try:
        #             pyArgs[i] = args[i].to_dict()
        #         except:
        #             pass
        #     print("Main", msg, pyArgs)

        if msg == "canvasSetSize":  # x, y, canResize
            document.getElementById("loading").style.display = "none"
            self.canvasSize = (args[0], args[1])
            self.canResize = args[2]
            self.fabCanvas.setWidth(self.canvasSize[0])
            self.fabCanvas.setHeight(self.canvasSize[1]+2)
            self.canvas.style.border = "1px solid black"

        elif msg == "fabNew":  # uid, type, [other args,] options
            # Add a new object to the canvas
            uid = args[0]
            fabClass = context.fabric[args[1]]
            options = {'csid': uid,
                       'isType': args[1],
                       'selectable': False,
                       'hasControls': False,
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
            fabObj = context.fabric.Rect.new(
                {'csid': uid,
                 'isType': "Rect",
                 'strokeWidth': 0,
                 'selectable': False,
                 'hasControls': False,
                 'hoverCursor': "arrow",
                 'filePath': filePath})
            self.fabObjs[uid] = fabObj
            self.fabCanvas.add(fabObj)

            def didLoad(img, failed):
                if not failed:
                    if filePath not in self.imgCache:
                        self.imgCache[filePath] = img
                    s = self.imgCache[filePath].getOriginalSize()
                    self.stackWorker.send(("imgSize", uid, s.width, s.height))

            if filePath in self.imgCache:
                s = self.imgCache[filePath].getOriginalSize()
                self.stackWorker.send(("imgSize", uid, s.width, s.height))
            else:
                if filePath in self.resourceMap:
                    context.fabric.Image.fromURL(self.resourceMap[filePath], didLoad)
                # else:
                #     context.fabric.Image.fromURL("Resources/"+filePath, didLoad)

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
                    self.stackWorker.send(("imgSize", uid, s.width, s.height))

            if filePath in self.imgCache:
                s = self.imgCache[filePath].getOriginalSize()
                self.stackWorker.send(("imgSize", uid, s.width, s.height))
            else:
                if filePath in self.resourceMap:
                    context.fabric.Image.fromURL(self.resourceMap[filePath], didLoad)
                # else:
                #     context.fabric.Image.fromURL("Resources/"+filePath, didLoad)

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
                         'hasControls': False,
                         'hoverCursor': "arrow",
                         'filePath': oldObj.filePath,
                         'left': int(options['left']), 'top': int(options['top']),
                         'visible': options['visible']
                         })
                self.fabObjs[uid] = img
                img.setCoords()
                self.fabCanvas.insertAt(img, index, False)
                if self.isDoneLoading:
                    self.Render()

            origImage.cloneAsImage(setImg, {'left': int(options['clipLeft']), 'top': int(options['clipTop']),
                                            'width': int(options['clipWidth']), 'height': int(options['clipHeight'])})

        elif msg == "imgNewStatic":  # uid, img_path, options
            uid = args[0]
            path = args[1]
            options = args[2]

            # Set up placeholder rect
            fabObj = context.fabric.Rect.new(
                {'csid': uid,
                 'isType': "Rect",
                 'strokeWidth': 0,
                 'selectable': False,
                 'hasControls': False,
                 'hoverCursor': "arrow"})
            self.fabObjs[uid] = fabObj
            self.fabCanvas.add(fabObj)
            oldObj = self.fabObjs[uid]

            def didLoad(img, failed):
                if not failed:
                    img.set({'csid': uid,
                             'isType': "Image",
                             'angle': options['angle'],
                             'selectable': False,
                             'hasControls': False,
                             'hoverCursor': "arrow",
                             'left': int(options['left']), 'top': int(options['top']),
                             'scaleX': options['scaleX'], 'scaleY': options['scaleY'],
                             'visible': options['visible']
                             })
                    index = [o.csid for o in self.fabCanvas.getObjects()].index(oldObj.csid)
                    self.fabCanvas.remove(oldObj)
                    self.fabObjs[uid] = img
                    img.setCoords()
                    self.fabCanvas.insertAt(img, index, False)
                    if self.isDoneLoading:
                        self.Render()

            context.fabric.Image.fromURL(path, didLoad)

        elif msg == "imgReplaceStatic":  # uid, img_path, options
            uid = args[0]
            path = args[1]
            options = args[2]

            oldObj = self.fabObjs[uid]

            def didLoad(img, failed):
                if not failed:
                    img.set({'csid': uid,
                             'isType': "Image",
                             'angle': options['angle'],
                             'selectable': False,
                             'hasControls': False,
                             'hoverCursor': "arrow",
                             'left': int(options['left']), 'top': int(options['top']),
                             'scaleX': options['scaleX'], 'scaleY': options['scaleY'],
                             'visible': options['visible']
                             })
                    index = [o.csid for o in self.fabCanvas.getObjects()].index(oldObj.csid)
                    self.fabCanvas.remove(oldObj)
                    self.fabObjs[uid] = img
                    img.setCoords()
                    self.fabCanvas.insertAt(img, index, False)
                    if self.isDoneLoading:
                        self.Render()

            context.fabric.Image.fromURL(path, didLoad)

        elif msg == "fieldNew":  # uid, text, options
            # Add a new TextField object to the canvas
            uid = args[0]
            text = args[1]
            fabObj = context.fabric.Textbox.new(text, args[2])

            fabObj.set({'csid': uid,
                        'isType': 'TextField',
                        'selectable': False,
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
            fabObj.oldOnKeyUp = fabObj.onKeyUp
            fabObj.onKeyUp = self.OnTextFieldKeyUp

        elif msg == "fabReplace":  # uid, type, options
            # replace a fabric object with this one (used when user code sets line.points)
            uid = args[0]

            oldObj = self.fabObjs[uid]
            index = [o.csid for o in self.fabCanvas.getObjects()].index(oldObj.csid)
            self.fabCanvas.remove(oldObj)

            fabClass = context.fabric[args[1]]
            fabObj = fabClass.new(*args[2:])
            fabObj.set({'csid':uid,
                        'isType': args[1],
                        'selectable': False,
                        'hasControls': False,
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
                    print("delete: no object with uid", uid)

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

        elif msg == "fabOffset":  # uid, options
            # offset a fabric object's position by relative delta
            uid = args[0]
            options = args[1]
            fabObj = self.fabObjs[uid]
            fabObj.set({'left': fabObj.left + options['left'],
                        'top': fabObj.top + options['top']})
            fabObj.setCoords()

        elif msg == "fabReorder":  # uid, index
            # change an object's z-order
            uid = args[0]
            index = args[1]
            fabObj = self.fabObjs[uid]
            self.fabCanvas.moveTo(fabObj, index)

        elif msg == "loadDone":
            self.isDoneLoading = True
            self.Render()
            if context.requestThumbnail:
                self.GetThumbnail()

        elif msg == "render":  # No args
            self.Render()

        elif msg == "fabLabelAutoSize":
            uid = args[0]
            fabObj = self.fabObjs[uid]
            self.UpdateTextSize(fabObj)

        elif msg == "focus":  # uid
            # focus a textfield
            uid = args[0]
            wasFocused = self.fabCanvas.getActiveObject() and self.fabCanvas.getActiveObject().csid == uid
            field = self.fabObjs[uid]
            if uid == 0:
                self.fabCanvas.discardActiveObject()
            else:
                self.fabCanvas.setActiveObject(field)
                field.enterEditing()
                if not wasFocused:
                    length = len(field.text)
                    field.setSelectionStart(length)
                    field.setSelectionEnd(length)
                if self.IsMobileBrowser() and context.navigator.hasOwnProperty("virtualKeyboard"):
                    context.navigator.virtualKeyboard.show()

        elif msg == "alert":  # text
            # open an alert (Just an OK button).  first make sure our render is up to date, by requesting a render
            # and waiting for the next frame.  then actually open the alert.  The Worker will wait until the user
            # closes the alert, so we need to update waitSA32[0] and notify that it has been updated,since this is
            # what the Worker is waiting on.
            self.fabCanvas.requestRenderAll()
            timer.set_timeout(self.HandleOneMessage, 20, ("alertInternal", *args))
        elif msg == "alertInternal":
            text = args[0]
            self.activeAlert = None
            def onKeyDown(e):
                if e.code in ["Enter", "Escape"]:
                    self.activeAlert.close()
            def onDone(e):
                document.unbind("keydown", onKeyDown)
                self.activeAlert = None
                self.dataSA16[0] = 0
                self.waitSA32[0] = 1
                context.Atomics.notify(self.waitSA32, 0)
                if self.needsResize:
                    self.needsResize = False
                    self.OnWindowResize(None)

            document.bind("keydown", onKeyDown)
            self.activeAlert = context.Attention.Confirm.new({"title": "CardStock", "content": str(text),
                                                             "buttonCancel": "-", "buttonConfirm": "OK",
                                                             "afterClose": onDone})

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
            self.activeAlert = None
            def onKeyDown(e):
                if e.code == "Enter":
                    self.dataSA16[0] = 1
                    self.activeAlert.close()
                elif e.code in "Escape":
                    self.dataSA16[0] = 0
                    self.activeAlert.close()
            def onConfirm(e):
                self.dataSA16[0] = 1
            def onCancel(e):
                self.dataSA16[0] = 0
            def onDone(e):
                document.unbind("keydown", onKeyDown)
                self.activeAlert = None
                self.waitSA32[0] = 1
                context.Atomics.notify(self.waitSA32, 0)
                if self.needsResize:
                    self.needsResize = False
                    self.OnWindowResize(None)

            document.bind("keydown", onKeyDown)
            self.activeAlert = context.Attention.Confirm.new({"title": "CardStock", "content": str(text),
                                                             "buttonCancel": "No", "buttonConfirm": "Yes",
                                                             "onConfirm": onConfirm, "onCancel": onCancel,
                                                             "afterClose": onDone})

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
            self.activeAlert = None
            default = "" if len(args) < 2 else args[1]
            self.dataSA16[0] = -1
            def onKeyDown(e):
                if e.code == "Escape":
                    self.activeAlert.close()
            def onSubmit(e, result):
                if result is not None:
                    self.dataSA16[0] = len(result)
                    for i in range(len(result)):
                        self.dataSA16[i + 1] = ord(result[i])
            def onDone(e):
                document.unbind("keydown", onKeyDown)
                self.activeAlert = None
                self.waitSA32[0] = 1
                context.Atomics.notify(self.waitSA32, 0)
                if self.needsResize:
                    self.needsResize = False
                    self.OnWindowResize(None)


            document.bind("keydown", onKeyDown)
            self.activeAlert = context.Attention.Prompt.new({"title": "CardStock", "content": str(text),
                                                            "placeholderText": "", "submitText": "OK",
                                                            "onSubmit": onSubmit, "afterClose": onDone})
            self.activeAlert.input.value = str(default)
            self.activeAlert.input.select()
            self.activeAlert.input.focus()

        elif msg == "open_url":  # url, in_place
            url = args[0]
            in_place = args[1]
            if in_place:
                context.location = url
            else:
                context.open(url, '_blank').focus()

        elif msg == "playAudio":  # filePath
            # play an audio file
            file = args[0]
            self.soundCache[file].play()
            if file in self.resourceMap:
                path = self.resourceMap[file]
                snd = context.Howl.new({'src': [path]})
                snd.play()

        elif msg == "stopAudio":  # No args
            # stop all audio
            context.Howler.stop()

        elif msg == "write":  # text
            # Allows printing from the worker thread
            print(args[0], end='')

        elif msg == "echo":  # args
            # pop the first arg ("echo") and send back the rest.
            # This is used from the worker to queue up a message in its own message queue
            self.stackWorker.send(args)

        elif msg == "closeWindow":
            context.close()

        else:
            print("StackCanvas received bad msg:", msg)

    def IsMobileBrowser(self):
        toMatch = ["Android", "webOS", "iPhone", "iPad", "iPod", "Windows Phone"]
        ua = context.navigator.userAgent
        for m in toMatch:
            if m in ua:
                return True
        return False

    def SendBuffer(self):
        # print out any buffered writes from the worker thread's print() calls
        if len(self.writeBuffer):
            print(context.stackCanvas.writeBuffer, end='')
            self.writeBuffer = ""

    def ConvPoint(self, x, y):
        rect = self.canvas.getBoundingClientRect()
        # Flip coords vertically to match cardstock: (0,0) = Bottom Left
        return (int(x-rect.left), int(self.canvasSize[1] - y + rect.top))

    def OnMouseDown(self, options):
        if self.activeAlert: return
        uid = 0
        if options.target:
            uid = options.target.csid
            if options.target.isType == "TextField":
                self.OnTextFieldMouseDown(options.target, options.e)
        if "touch" in options.e.type:
            self.isUsingTouch = True
            pos = (options.e.touches[0].clientX, options.e.touches[0].clientY)
        else:
            self.isUsingTouch = False
            pos = (options.e.clientX, options.e.clientY)
        self.DoMouseDown(uid, pos[0], pos[1], self.isUsingTouch)

    def DoMouseDown(self, uid, x, y, isTouch):
        # Flip points vertically and send to the worker.  Also fix TextField selection on click.
        pos = self.ConvPoint(x, y)
        self.lastMousePos = pos
        self.isMouseDown = True
        self.stackWorker.send(("mouseDown", uid, pos, isTouch))

    def OnMouseMove(self, options):
        if self.activeAlert: return
        uid = 0
        if options.target:
            uid = options.target.csid
        if options.e.type.startswith("touch"):
            self.isUsingTouch = True
            pos = (options.e.touches[0].clientX, options.e.touches[0].clientY)
        else:
            self.isUsingTouch = False
            pos = (options.e.clientX, options.e.clientY)
        self.DoMouseMove(uid, pos[0], pos[1], self.isUsingTouch)

    def DoMouseMove(self, uid, x, y, isTouch):
        # Flip points vertically and send to the worker.
        pos = self.ConvPoint(x, y)
        if pos[0] != self.lastMousePos[0] or pos[1] != self.lastMousePos[1]:
            self.lastMousePos = pos
            # keep track of how many OnMouseMove calls are pending, so the worker doesn't get bogged down
            # if it's slow to process these
            context.Atomics.add(self.countsSA32, 0, 1)
            self.stackWorker.send(("mouseMove", uid, pos, isTouch))

    def OnMouseUp(self, options):
        if self.activeAlert: return
        uid = 0
        if options.target:
            uid = options.target.csid
        if options.e.type.startswith("touch"):
            self.isUsingTouch = True
            pos = self.lastMousePos
        else:
            self.isUsingTouch = False
            pos = (options.e.clientX, options.e.clientY)
        self.DoMouseUp(uid, pos[0], pos[1], self.isUsingTouch)

    def DoMouseUp(self, uid, x, y, isTouch):
        # Flip points vertically and send to the worker.
        pos = self.ConvPoint(x, y)
        self.lastMousePos = pos
        self.isMouseDown = False
        self.stackWorker.send(("mouseUp", uid, pos, isTouch))

    def OnMouseDocUp(self, e):
        if self.activeAlert: return
        timer.set_timeout(self.DoMouseDocUp, 10)

    def DoMouseDocUp(self):
        if self.isMouseDown:
            self.DoMouseUp(0, self.lastMousePos[0], self.lastMousePos[1], self.isUsingTouch)

    def OnMouseCancel(self, e):
        self.DoMouseUp(0, self.lastMousePos[0], self.lastMousePos[1], True)

    def OnKeyDown(self, e):
        # Don't tab focus out of the canvas
        # forward these events on to the worker
        if self.activeAlert: return
        if e.key == "Tab":
            e.preventDefault()
        if not e.repeat:
            self.stackWorker.send(("keyDown", e.key))

    def OnKeyUp(self, e):
        # forward these events on to the worker
        if self.activeAlert: return
        self.stackWorker.send(("keyUp", e.key))

    def OnTabVisibilityChanged(self, e):
        # forward these events on to the worker
        self.stackWorker.send(("visibilityChanged", document.visibilityState == "visible"))

    def OnTabFocused(self, e):
        # forward these events on to the worker
        self.stackWorker.send(("stackFocus", True))

    def OnTabFocusLost(self, e):
        # forward these events on to the worker
        self.stackWorker.send(("stackFocus", False))

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
        if self.activeAlert: return
        self.fabCanvas.setActiveObject(field)
        field.enterEditing()
        field.setCursorByClick(e)

    def OnTextFieldKeyDown(self, e):
        # Forward arrow keys to the card, and catch Enter/Return so we can run "OnEnter"
        # Also avoid adding newlines to non-multiline text fields
        if self.activeAlert:
            e.preventDefault()
            return
        fabObj = self.fabCanvas.getActiveObject()
        if fabObj and fabObj.isType == 'TextField':
            if e.key not in ("Enter", "Return"):
                fabObj.oldOnKeyDown(e)
            if not e.repeat:
                if "Arrow" in e.key:
                    self.OnKeyDown(e)
            if e.key in ("Enter", "Return"):
                if not fabObj.isMultiline:
                    e.preventDefault()
                    self.stackWorker.send(("textEnter", fabObj.csid))

    def OnTextFieldKeyUp(self, e):
        # Forward arrow keys to the card, and catch Enter/Return so we can run "OnEnter"
        # Also avoid adding newlines to non-multiline text fields
        if self.activeAlert:
            e.preventDefault()
            return
        fabObj = self.fabCanvas.getActiveObject()
        if fabObj and fabObj.isType == 'TextField':
            if e.key not in ("Enter", "Return"):
                fabObj.oldOnKeyUp(e)
            if "Arrow" in e.key:
                self.OnKeyUp(e)
            if e.key in ("Enter", "Return"):
                if not fabObj.isMultiline:
                    e.preventDefault()

    def OnTextFieldSelected(self, options):
        # tell the worker that the field got focused
        fabObj = options.target
        self.stackWorker.send(("objectFocus", fabObj.csid))

    def OnTextChanged(self, options):
        # Tell the worker that the field's text changed
        uid = options.target.csid
        textbox = self.fabObjs[uid]
        self.stackWorker.send(("textChanged", uid, textbox.text))

    def OnTextFieldDeselected(self, options):
        # tell the worker that the field got un-focused
        fabObj = options.target
        fabObj.exitEditing()
        fabObj = self.fabCanvas.getActiveObject()
        if not fabObj:
            self.stackWorker.send(("objectFocus", 0))

    def OnWindowResize(self, _e, force=False):
        # tell the worker that the window resized
        if self.canResize or force:
            if self.activeAlert:
                self.needsResize = True
                return
            self.canvas.style.border = "1px solid transparent"
            self.fabCanvas.setWidth(0)
            self.fabCanvas.setHeight(0)
            canvasDiv = document.getElementById('canvasContainer')
            self.stackWorker.send(("windowSized", min(MAX_CANVAS_WIDTH, canvasDiv.scrollWidth),
                                             min(MAX_CANVAS_HEIGHT, canvasDiv.scrollHeight)))

    def GetThumbnail(self):
        def got_full(imageBlob):
            def on_complete(aj):
                if aj.status == 200:
                    print("Thumbnail updated")
                else:
                    print(f"Thumbnail upload error: {aj.status} {aj.text}")

            url = f"{context.location.protocol}//{context.location.host}/v/2/upload_thumbnail"
            req = ajax.Ajax()
            form_data = ajax.form_data()
            form_data.append("stackname", context.stackName)
            form_data.append("csrfmiddlewaretoken", context.CSRF_TOKEN)
            form_data.append("thumbnail", imageBlob)
            req.open('POST', url)
            req.bind('complete', on_complete)
            req.send(form_data)

        self.canvas.toBlob(got_full)

    # THUMBNAIL_SIZE = 160
    #
    # def GetThumbnail(self):
    #     def got_full(imageBitmap):
    #         def got_thumb(imageBlog):
    #             def on_complete(aj):
    #                 if aj.status != 200:
    #                     print(f"Thumbnail upload error: {aj.status} {aj.text}")
    #                 else:
    #                     print(f"Response: {aj.text}")
    #
    #             url = f"{context.location.protocol}//{context.location.host}/v/2/upload_thumbnail"
    #             req = ajax.Ajax()
    #             form_data = ajax.form_data()
    #             form_data.append("stack_id", context.stackId)
    #             form_data.append("csrfmiddlewaretoken", context.CSRF_TOKEN)
    #             form_data.append("thumbnail", imageBlog)
    #             req.open('POST', url)
    #             req.bind('complete', on_complete)
    #             req.send(form_data)
    #
    #         scale = 0.5 #  160 / max(*self.canvasSize)
    #         thumbSize = (int(self.canvasSize[0] * scale), int(self.canvasSize[1] * scale))
    #         oc = document.createElement('canvas')
    #         oc.width = thumbSize[0]
    #         oc.height = thumbSize[1]
    #         document.getElementById('canvasContainer').appendChild(oc)
    #         oc.getContext('2d').drawImage(imageBitmap, 0, 0, imageBitmap.width, imageBitmap.height, 0, 0, thumbSize[0], thumbSize[1])
    #         oc.toBlob(got_thumb)
    #
    #     context.createImageBitmap(self.canvas.getContext('2d').getImageData(0, 0, self.canvasSize[0], self.canvasSize[1])).then(got_full)
