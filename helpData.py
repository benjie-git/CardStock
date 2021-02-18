import uiView
import keyword


class HelpData():
    reservedNames = None

    @classmethod
    def ForObject(cls, obj):
        return cls.ForType(obj.model.type)

    @classmethod
    def ForType(cls, typeStr):
        if typeStr == "button":                 return HelpDataButton
        if typeStr == "textfield":              return HelpDataTextField
        if typeStr == "textlabel":              return HelpDataTextLabel
        if typeStr == "image":                  return HelpDataImage
        if typeStr == "group":                  return HelpDataGroup
        if typeStr in ["line", "pen"]:          return HelpDataLine
        if typeStr in ["shape", "oval", "rect"]:return HelpDataShape
        if typeStr == "roundrect":             return HelpDataRoundRectangle
        if typeStr == "card":                   return HelpDataCard
        if typeStr == "stack":                  return HelpDataStack
        return HelpDataObject

    @classmethod
    def GetPropertyHelp(cls, obj, key):
        data = cls.ForObject(obj)
        while data:
            if key in data.properties:
                prop = data.properties[key]
                text = "<b>"+key+"</b>:<i>" + prop["type"] + "</i> - " + prop["info"]
                return text
            data = data.parent
        return None

    @classmethod
    def HtmlTableFromLists(cls, rows):
        if len(rows) < 2:
            return ""

        text =  "<table border='0' cellpadding='5' cellspacing='0'>\n"

        text += "<tr>"
        for cell in rows[0]:
            text += "<th align='left' valign='top'>" + cell + "</th>"
        text += "</tr>\n"

        bgcolors = [" bgcolor='#D0DFEE'", " bgcolor='#CCCCCC'"]
        bg = bgcolors[0]
        for row in rows[1:]:
            bg = bgcolors[0 if bg==bgcolors[1] else 1]
            text += "<tr>"
            text += "<th align='left' valign='top'"+bg+">" + row[0] + "</th>"
            for cell in row[1:]:
                text += "<td align='left' valign='top'"+bg+">" + cell + "</td>"
            text += "</tr>\n"
        text += "</table>"
        return text


    @classmethod
    def PropertyTable(cls, typeStr):
        data = cls.ForType(typeStr)
        rows = []
        rows.append(["Property", "Type", "Description"])
        while data:
            for key in data.properties:
                prop = data.properties[key]
                rows.append([key, "<i>" + prop["type"] + "</i>", prop["info"]])
            data = data.parent
            if data == HelpDataObject:
                break
        if len(rows) >= 2:
            return cls.HtmlTableFromLists(rows)
        else:
            return "<p>No additional properties for this object type.</p>"

    @classmethod
    def GetHandlerHelp(cls, obj, key):
        data = cls.ForObject(obj)
        while data:
            if key in data.handlers:
                handler = data.handlers[key]
                argText = ""
                for name, arg in handler["args"].items():
                    argText += "<b>" + name + "</b>:<i>" + arg["type"] + " </i> - " + arg["info"] + "<br/>"
                text = "<b>" + uiView.UiView.handlerDisplayNames[key] + "</b><br/>" + argText + "<br/>" + handler["info"]
                return text
            data = data.parent
        return None

    @classmethod
    def HandlerTable(cls, typeStr):
        data = cls.ForType(typeStr)
        rows = []
        rows.append(["Event", "Arguments", "Description"])
        while data:
            for key in data.handlers:
                handler = data.handlers[key]
                argText = ""
                for name, arg in handler["args"].items():
                    argText += "<b>" + name + "</b>:<i>" + arg["type"] + " </i> - " + arg["info"] + "<br/>"
                rows.append([uiView.UiView.handlerDisplayNames[key], argText, handler["info"]])
            data = data.parent
            if data == HelpDataObject:
                break
        if len(rows) >= 2:
            return cls.HtmlTableFromLists(rows)
        else:
            return "<p>No additional events for this object type.</p>"

    @classmethod
    def MethodTable(cls, typeStr):
        data = cls.ForType(typeStr)
        rows = []
        rows.append(["Method", "Arguments", "Return", "Description"])
        while data:
            for key in data.methods:
                method = data.methods[key]
                argText = ""
                for name, arg in method["args"].items():
                    argText += "<b>" + name + "</b>:<i>" + arg["type"] + " </i> - " + arg["info"] + "<br/>"
                ret = method["return"] if method["return"] else ""
                name = key + "(" + ', '.join(method["args"].keys()) + ")"
                rows.append([name, argText, "<i>"+ret+"</i>", method["info"]])
            data = data.parent
            if data == HelpDataObject:
                break
        if len(rows) >= 2:
            return cls.HtmlTableFromLists(rows)
        else:
            return "<p>No additional methods for this object type.</p>"

    @classmethod
    def GlobalVariablesTable(cls):
        data = HelpDataGlobals
        rows = []
        rows.append(["Variable", "Type", "Description"])
        for key in data.variables:
            var = data.variables[key]
            rows.append([key, "<i>" + var["type"] + "</i>", var["info"]])
        return cls.HtmlTableFromLists(rows)

    @classmethod
    def GlobalFunctionsTable(cls):
        data = HelpDataGlobals
        rows = []
        rows.append(["Method", "Arguments", "Return", "Description"])
        for key in data.functions:
            func = data.functions[key]
            argText = ""
            for name, arg in func["args"].items():
                argText += "<b>" + name + "</b>:<i>" + arg["type"] + " </i> - " + arg["info"] + "<br/>"
            ret = func["return"] if func["return"] else ""
            name = key+"(" + ', '.join(func["args"].keys())  + ")"
            rows.append([name, argText, "<i>"+ret+"</i>", func["info"]])
        return cls.HtmlTableFromLists(rows)

    @classmethod
    def ObjectSection(cls, typeStr, title, description):
        text = ""
        if description:
            text = "<p>" + description + "</p>\n"
        return f"""
<a name="#{typeStr}"/>
<h2>{title}</h2>
{text}
<br/><br/>
<a name="#{typeStr}.props"/>
<h3>Properties</h3>
{HelpData.PropertyTable(typeStr)}
<br/><br/>
<a name="#{typeStr}.methods"/>
<h3>Methods</h3>
{HelpData.MethodTable(typeStr)}
<br/><br/>
<a name="#{typeStr}.events"/>
<h3>Events</h3>
{HelpData.HandlerTable(typeStr)}
<br/><br/>
"""

    @classmethod
    def TOCPage(cls):
        types = [["All Objects", "object"], ["Stack", "stack"], ["Card", "card"], ["Button", "button"],
                 ["Text Field", "textfield"], ["Text Label", "textlabel"], ["Image", "image"], ["Line & Pen", "line"],
                 ["Oval & Rectangle", "shape"], ["Round Rectangle", "roundrect"], ["Group", "group"]]
        text = """
<html>
<body bgcolor="#EEEEEE">
<h2>Contents</h2>
<li><a href="#top">Reference</a><br>
<ul>
<li><a href="#dataTypes">Data Types</a>
<li><a href="#globalVars">Global Variables</a>
<li><a href="#globalFuncs">Global Functions</a>
"""
        for type in types:
            text += f"""
<li><a href="#{type[1]}">{type[0]}</a><br/>
<ul>
<li><a href="#{type[1]}">Properties</a></li>
<li><a href="#{type[1]+".methods"}">Methods</a></li>
<li><a href="#{type[1]+".events"}">Events</a></li>
</ul>
</li>
"""
        text += """
</ul>
</ul>
</body></html>
        """
        return text

    @classmethod
    def ReservedNames(cls):
        if not cls.reservedNames:
            cls.reservedNames = ["keyName", "mousePos", "message"]
            cls.reservedNames.extend(HelpDataGlobals.variables.keys())
            cls.reservedNames.extend(HelpDataGlobals.functions.keys())
            cls.reservedNames.extend(HelpDataObject.properties.keys())
            cls.reservedNames.extend(HelpDataObject.methods.keys())
            cls.reservedNames.extend(HelpDataCard.properties.keys())
            cls.reservedNames.extend(HelpDataCard.methods.keys())
            cls.reservedNames.extend(HelpDataStack.properties.keys())
            cls.reservedNames.extend(keyword.kwlist)
        return cls.reservedNames

HelpDataTypes = [["Type", "Description"],
                 ["<i>bool</i>", "A bool or boolean value holds a simple True or False"],
                 ["<i>int</i>", "An int or integer value holds any whole number, positive or negative"],
                 ["<i>float</i>", "A float or floating point value holds any number, including with a decimal point"],
                 ["<i>string</i>", "A string value holds text"],
                 ["<i>object</i>", "An object value holds a CardStock object, like a button, card, or oval"],
                 ["<i>list</i>", "A list value is a container that holds a list of other values."],
                 ["<i>point</i>", "A point value is like a list of two numbers, x and y, that describes a location in "
                                  "the card.  For a point variable p, you can access the x value as p[0] or p.x, and "
                                  "the y value as either p[1] or p.y."],
                 ["<i>size</i>", "A size value is like a list of two numbers, width and height, that describes the "
                                 "size of an object in the card.  For a size variable s, you can access the width "
                                 "value as s[0] or s.width, and the height value as either s[1] or s.height."],
                 ]


class HelpDataGlobals():
    variables = {
        "self": {"type": "object",
                  "info": "In any object's event code, <b>self</b> always refers to the object that contains this code."},
        "stack": {"type": "object",
                  "info": "The <b>stack</b> is the object that represents your whole program.  You can access cards "
                          "in this stack as stack.cardName."},
        "card": {"type": "object",
                 "info": "The <b>card</b> is the object that represents the currently loaded card in your stack.  You "
                         "can access the objects on this card as card.objectName."},
    }

    functions = {
        "Wait": {"args": {"duration": {"type": "float", "info": "Number of seconds to delay."}}, "return": None,
                 "info": "Delays the program from running for <b>duration</b> seconds.  No movements or animations "
                         "will happen during this time."},
        "RunAfterDelay": {"args": {"duration": {"type": "float", "info": "Number of seconds to delay."},
                                   "func": {"type": "function", "info": "A function to call after the delay."}}, "return": None,
                          "info": "This function lets your program continue running while a timer waits for <b>duration</b> seconds, "
                                  "and then runs the functions <b>func</b>.  Movements, animations, and user interaction "
                                  "will all continue during this time."},
        "Time": {"args": {}, "return": "float",
                 "info": "Returns the time in seconds since 'The Unix Epoch', midnight UTC on January 1st, 1970.  That "
                         "date doesn't usually matter, since most often, you'll store the time at one point in your "
                         "program, and then compare it to the new time somewhere else, to determine the difference."},
        "Paste": {"args": {}, "return": "list",
                  "info": "Pastes any CardStock objects in the clipboard from a previous Copy or Cut command onto the "
                          "current card, and returns a list of these pasted objects."},
        "Alert": {"args": {"message": {"type": "string", "info": "Text to show in the Alert dialog."}}, "return": None,
                  "info": "Shows an alert dialog to the user, with the <b>message</b> you provide, and offers an OK button."},
        "Ask": {"args": {"message": {"type": "string", "info": "Text to show in the Ask dialog."}}, "return": "bool",
                "info": "Shows an alert dialog to the user, with the <b>message</b> you provide, and offers Yes and No "
                        "buttons.  Returns True if Yes is clicked, and False if No is clicked."},
        "GotoCard": {"args": {"cardName": {"type": "string", "info": "The name of the card to go to."}}, "return": None,
                     "info": "Goes to the card with the name passed in as <b>cardName</b>.  This sends the OnHideCard event "
                             "for the current card, and then the OnShowCard event for the new card, or does nothing if "
                             "there is no card with that name."},
        "GotoCardIndex": {"args": {"cardIndex": {"type": "int", "info": "The number of the card to go to, with 0 meaning the first card."}}, "return": None,
                          "info": "Goes to the card with the index passed in as <b>cardIndex</b>.  This sends the OnHideCard event "
                                  "for the current card, and then the OnShowCard event for the new card, or does nothing "
                                  "if the index is less than 0, or larger than the number of cards-1."},
        "GotoNextCard": {"args": {}, "return": None,
                         "info": "Goes to the next card in the stack.  If we're already on the last card, then loop back to "
                                 "the first card.  This sends the OnHideCard event for the current card, and then the "
                                 "OnShowCard event for the new card."},
        "GotoPreviousCard": {"args": {}, "return": None,
                             "info": "Goes to the previous card in the stack.  If we're already on the first card, then loop back to "
                                     "the last card.  This sends the OnHideCard event for the current card, and then the "
                                     "OnShowCard event for the new card."},
        "PlaySound": {"args": {"file": {"type": "string",
                                        "info": "This is the filename of the .wav format audio file to play, relative to where the stack file lives."}},
                      "return": None,
                      "info": "Starts playing the .wav formatted sound file at location <b>file</b>."},
        "StopSound": {"args": {},
                      "return": None,
                      "info": "Stops all currently playing sounds."},
        "BroadcastMessage": {"args": {"message": {"type": "string",
                                        "info": "This is the message to send."}},
                      "return": None,
                      "info": "Sends the <b>message</b> to this card, and all objects on this card, causing each of their "
                              "OnMessage events to run with this <b>message</b>."},
        "IsKeyPressed": {"args": {"keyName": {"type": "string", "info": "The name of the key to check."}},
                         "return": "bool",
                         "info": "Returns <b>True</b> if the named keyboard key is currently pressed down, otherwise "
                                 "returns <b>False</b>."},
    }


class HelpDataObject():
    parent = None
    properties = {
        "name": {"type": "string",
                 "info": "Every object has a <b>name</b> property.  These are forced to be unique within each card, "
                         "since these become the names of your object variables that you access from your code.  From "
                         "your code, you can get an object's name, but you can not set it."},
        "type": {"type": "string",
                 "info": "Every object has a <b>type</b> property.  It will be one of 'button', 'textfield', 'textlabel', "
                         "'image', 'line', 'oval', 'rect, 'roundrect', 'stack', 'card', 'group'."},
        "position": {"type": "point",
                     "info": "The <b>position</b> property is a point value that describes where on the "
                             "card this object's top-left corner is'.  The first number, <b>x</b>, is how many pixels the object is "
                             "from the left edge of the card.  The second number, <b>y</b>, is how far down from the top."},
        "size": {"type": "size",
                 "info": "The <b>size</b> property is a size value that describes how big this object is on screen. "
                         "The first number, <b>width</b>, is how wide the object is, and the second number, <b>height</b>, is how tall."},
        "center": {"type": "point",
                   "info": "The <b>center</b> property is a point value that describes where on the "
                           "card this object's center is'.  The first number, <b>x</b>, is how many pixels the object's center "
                           "is from the left edge of the card.  The second number, <b>y</b>, is how far down from the top.  "
                           "This value is not stored, but computed based on position and size."},
        "speed": {"type": "point",
                  "info": "This is a point value corresponding to the current speed of the object, in pixels/second "
                          "in both the <b>x</b> and <b>y</b> directions."},
        "visible": {"type": "bool",
                    "info": "<b>True</b> if this object is <b>visible</b>, or <b>False</b> if it is hidden."},
        "hasFocus": {"type": "bool",
                     "info": "<b>True</b> if this object is focused (if it is selected for typing into), otherwise "
                             "<b>False</b>. This value is not settable, but you can call the method Focus() to try to "
                             "focus this object."},
        "parent": {"type": "string",
                   "info": "<b>parent</b> is the object that contains this object.  For most objects, it is the card, unless this "
                           "object has been grouped, in which case its <b>parent</b> is the group object  A card's "
                           "<b>parent</b> is the stack.  The stack has no <b>parent</b>, so stack.parent is <b>None</b>."},
        "children": {"type": "list",
                     "info": "<b>children</b> is the list of objects that this object contains.  A stack has children "
                             "that are cards.  A card and a group can both have children objects. Other objects have "
                             "no children."},
    }

    methods = {
        "Copy": {"args": {},
                 "return": None,
                 "info": "Copies this object onto the clipboard, just like the Edit menu Copy command."},
        "Cut": {"args": {},
                "return": None,
                "info": "Copies this object onto the clipboard and then deletes it, just like the Edit menu Cut command."},
        "Clone": {"args": {},
                  "return": "object",
                  "info": "Duplicates this object, and updates the new object's name to be unique, and then returns "
                          "the new object for you to store into a variable."},
        "Delete": {"args": {},
                   "return": None,
                   "info": "Deletes this object.  Like Cut, but the object does not get copied to the clipboard."},
        "SendMessage": {"args": {"message":{"type": "string", "info": "The message being sent to this object."}},
                        "return": None,
                        "info": "Sends a <b>message</b> to this object, that the object can handle in its OnMessage event code.  For "
                                "example, you could send the message 'reset' to an object, and in its OnMessage code, "
                                "it could check for whether <b>message</b> == 'reset', and then set some variables back to their initial values."},
        "Focus": {"args": {},
                  "return": None,
                  "info": "Selects this object so that it will handle key presses.  A focused button will appear "
                          "selected, and typing Enter/Return will click it.  Typed words will get entered into the "
                          "currently focused TextField."},
        "Show": {"args": {},
                 "return": None,
                 "info": "Shows this object if it was not visible."},
        "Hide": {"args": {},
                 "return": None,
                 "info": "Hides this object if it was visible."},
        "IsTouching": {"args": {"other": {"type": "object", "info": "The other object to compare to this one"}},
                       "return": "bool",
                       "info": "Returns <b>True</b> if this object is touching the <b>other</b> object passed into "
                               "this function, otherwise returns <b>False</b>."},
        "IsTouchingEdge": {"args": {"other": {"type": "object", "info":"The other object to compare to this one"}},
                           "return": "string",
                           "info": "Returns <b>None</b> if this object is not touching any edges of the <b>other</b> "
                                   "object passed into this function.  If this object is touching any edges of the "
                                   "other object, the return value will be 'Top', 'Bottom', 'Left', or 'Right', accordingly."},

        "AnimatePosition": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                     "endPosition": {"type": "point",
                                                     "info": "the destination top-left corner position at the end of the animation"},
                                     "onFinished": {"type": "function",
                                                    "info": "an optional function to run when the animation finishes"}},
                            "return": None,
                            "info": "Visually animates the movement of this object from its current position to <b>endPosition</b>, "
                                    "over <b>duration</b> seconds.  When the animation completes, runs the "
                                    "<b>onFinished</b> function, if one was passed in."},

        "AnimateCenter": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                   "endPosition": {"type": "point",
                                                   "info": "the destination center position at the end of the animation"},
                                   "onFinished": {"type": "function",
                                                  "info": "an optional function to run when the animation finishes"}},
                          "return": None,
                          "info": "Visually animates the movement of this object from its current position to have its center at <b>endCenter</b>, "
                                  "over <b>duration</b> seconds.  When the animation completes, runs the "
                                  "<b>onFinished</b> function, if one was passed in."},

        "AnimateSize": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                 "endSize": {"type": "size", "info": "the final size of this object at the end of the animation"},
                                 "onFinished": {"type": "function", "info": "an optional function to run when the animation finishes"}},
                        "return": None,
                        "info": "Visually animates the <b>size</b> of this object from its current size to <b>endSize</b>, "
                                "over <b>duration</b> seconds.  When the animation completes, runs the "
                                "<b>onFinished</b> function, if one was passed in."},
        "StopAnimations": {"args": {},
                           "return": None,
                           "info": "Stops all animations running on this object. "
                                   "Any animated properties are left at their current, mid-animation values."},
    }

    handlers = {
        "OnSetup": {"args": {},
                    "info": "The <b>OnSetup</b> event is run once for every object in your stack, immediately when the stack "
                            "starts running, before loading the first card.  This is a great place to run any imports that your "
                            "program needs, and to define functions, and set up any variables with their initial values."},
        "OnMouseDown": {"args": {"mousePos": {"type": "point", "info": "This is the current position of the mouse pointer on the card."}},
                        "info": "The <b>OnMouseDown</b> event is run when the mouse button gets clicked down inside of this object, "
                                "and gives you the current mouse position as the point <b>mousePos</b>."},
        "OnMouseMove": {"args": {"mousePos": {"type": "point", "info": "This is the current position of the mouse pointer on the card."}},
                        "info": "The <b>OnMouseMove</b> event is run every time the mouse moves, while over this object, whether "
                                "or not the mouse button is down, and gives you the current mouse position as the point <b>mousePos</b>."},
        "OnMouseUp": {"args": {"mousePos": {"type": "point", "info": "This is the current position of the mouse pointer on the card."}},
                      "info": "The <b>OnMouseUp</b> event is run when the mouse button is released over this object, and "
                              "gives you the current mouse position as the point <b>mousePos</b>."},
        "OnMouseEnter": {"args": {"mousePos": {"type": "point", "info": "This is the current position of the mouse pointer on the card."}},
                         "info": "The <b>OnMouseEnter</b> event is run when the mouse pointer moves onto this object."},
        "OnMouseExit": {"args": {"mousePos": {"type": "point", "info": "This is the current position of the mouse pointer on the card."}},
                        "info": "The <b>OnMouseExit</b> event is run when the mouse pointer moves back off of this object."},
        "OnMessage": {"args": {"message": {"type": "string", "info": "This is the message string that was passed into "
                                                                     "a SendMessage() or BroadcastMessage() call."}},
                      "info": "The <b>OnMessage</b> event is run when BroadcastMessage() is called, or SendMessage() "
                              "is called on this object.  The <b>message</b> string passed into SendMessage() or "
                              "BroadcastMessage() is delivered here."},
        "OnIdle": {"args": {"elapsedTime": {"type": "float", "info": "This is the number of seconds since the last time this event was run, normally about 0.03."}},
                   "info": "The <b>OnIdle</b> event is run approximately 30 times per second on every object on the current page, "
                           "and gives your object a chance to run periodic checks, for example checking for collisions using IsTouching()."},
    }


class HelpDataButton():
    parent = HelpDataObject

    properties = {
        "title": {"type": "string",
                  "info": "The <b>title</b> property is the visible text on the button."},
        "border": {"type": "bool",
                   "info": "By default buttons show a rectangular or rounded <b>border</b>, depending on your "
                           "computer's operating system.  But you can disable this border, so the "
                           "button is clear, just showing its title."},
    }

    methods = {
        "DoClick": {"args": {}, "return": None,
                    "info": "Runs this button's OnClick event code."},
    }

    handlers = {
        "OnClick": {"args": {},
                    "info": "The <b>OnClick</b> event is run when a user clicks down on this button, and releases the "
                            "mouse, while still inside the button.  It is also run when the button's DoClick() "
                            "method is called, or when the user pressed the Enter/Return key while the button is "
                            "focused."},
    }


class HelpDataTextField():
    parent = HelpDataObject

    properties = {
        "text": {"type": "string",
                 "info": "The <b>text</b> property holds the contents of this field as a string."},
        "alignment": {"type": "[Left, Center, Right]",
                      "info": "By default, text fields start aligned to the left, but you can change this property to make "
                              "your text centered, or aligned to the right."},
        "editable": {"type": "bool",
                     "info": "By default text fields can be edited by the user.  But you can set this to <b>False</b> "
                             "so that the text can not be edited."},
        "multiline": {"type": "bool",
                      "info": "By default, text fields hold only one line of text.  But you can set the "
                              "<b>multiline</b> property to <b>True</b> to let them hold multiple lines of text."},
    }

    methods = {
        "DoEnter": {"args": {}, "return": None,
                    "info": "Runs this text field's OnTextEnter event code."},
        "SelectAll": {"args": {}, "return": None,
                      "info": "Selects all text in this text field."},
    }

    handlers = {
        "OnTextChanged": {"args": {},
                          "info": "The <b>OnTextChanged</b> event is run every time the user makes any change to the text in this text field."},
        "OnTextEnter": {"args": {},
                        "info": "The <b>OnTextEnter</b> event is run when the user types the Enter key in this text field."},
    }


class HelpDataTextLabel():
    parent = HelpDataObject

    properties = {
        "text": {"type": "string",
                 "info": "The <b>text</b> property is the text contents of this label."},
        "alignment": {"type": "[Left, Center, Right]",
                      "info": "By default text fields start aligned to the left, but you can change this property to make "
                              "your text centered, or aligned to the right."},
        "textColor": {"type": "string",
                      "info": "The color used for the text in this label.  This can be a color word like red, or an "
                              "HTML color like #333333 for dark gray."},
        "font": {"type": "[Default, Serif, Sans-Serif, Mono]",
                 "info": "The <b>font</b> used for the text in this label."},
        "fontSize": {"type": "int",
                     "info": "The point size for the font used for the text in this label."},
    }

    methods = {
        "AnimateTextColor": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                      "endColor": {"type": "string",
                                                   "info": "the final textColor at the end of the animation"},
                                      "onFinished": {"type": "function",
                                                     "info": "an optional function to run when the animation finishes."}},
                             "return": None,
                             "info": "Visually animates fading this object's <b>textColor</b> to <b>endColor</b>, "
                                     "over <b>duration</b> seconds.  When the animation completes, runs the "
                                     "<b>onFinished</b> function, if one was passed in."},
    }

    handlers = {}


class HelpDataImage():
    parent = HelpDataObject

    properties = {
        "file": {"type": "string",
                 "info": "The file path of the image file to display in this image object."},
        "fit": {"type": "[Center, Stretch, Fit, Fill]",
                "info": "This property controls how the image is resized to fit into the image object.  Center shows "
                        "the image full size, centered in the image object, and clipped at the image object border. "
                        "Stretch resizes and stretches the image to fit exactly into the image object. Fit sizes the "
                        "image to fit inside the image object, while keeping the original image aspect ratio. Fill "
                        "sizes the image to just barely fill the entire image object, while keeping the original image "
                        "aspect ratio."},
        "rotation": {"type": "float",
                     "info": "This is the angle in degrees clockwise to rotate this image.  0 is upright."},
    }

    methods = {
        "AnimateRotation": {"args": {"duration": {"type": "float", "info": "time in seconds to run the animation"},
                                     "endRotation": {"type": "int",
                                                             "info": "the final rotation angle in degrees clockwise at "
                                                                     "the end of the animation"},
                                     "onFinished": {"type": "function",
                                                    "info": "an optional function to run when the animation finishes."}},
                            "return": None,
                            "info": "Visually animates changing this image's <b>rotation</b> angle to <b>endRotation</b>, "
                                    "over <b>duration</b> seconds.  When the animation completes, runs the "
                                    "<b>onFinished</b> function, if one was passed in."},
    }

    handlers = {}


class HelpDataGroup():
    parent = HelpDataObject

    properties = {}

    methods = {}

    handlers = {}


class HelpDataLine():
    parent = HelpDataObject

    properties = {
        "penThickness": {"type": "int",
                         "info": "The thickness of the line or shape border in pixels."},
        "penColor": {"type": "string",
                     "info": "The color used for the line or shape border.  This can be a color word like red, or an "
                             "HTML color like #FF0000 for pure red."},
    }

    methods = {
        "AnimatePenThickness": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                 "endThickness": {"type": "int",
                                                 "info": "the final penThickness at the end of the animation"},
                                 "onFinished": {"type": "function",
                                                "info": "an optional function to run when the animation finishes."}},
                        "return": None,
                        "info": "Visually animates changing this object's <b>penThickness</b> to <b>endThickness</b>, "
                                "over <b>duration</b> seconds.  When the animation completes, runs the "
                                "<b>onFinished</b> function, if one was passed in."},

        "AnimatePenColor": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                 "endColor": {"type": "string",
                                                 "info": "the final pen color at the end of the animation"},
                                 "onFinished": {"type": "function",
                                                "info": "an optional function to run when the animation finishes."}},
                        "return": None,
                        "info": "Visually animates fading this object's <b>penColor</b> to <b>endColor</b>, "
                                "over <b>duration</b> seconds.  When the animation completes, runs the "
                                "<b>onFinished</b> function, if one was passed in."},
    }

    handlers = {}


class HelpDataShape():
    parent = HelpDataLine

    properties = {
        "fillColor": {"type": "string",
                      "info": "The color used to fill the inside area of the shape.  This can be a color word like "
                              "red, or an HTML color like #FF0000 for pure red."},
    }

    methods = {
        "AnimateFillColor": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                     "endColor": {"type": "string",
                                                  "info": "the final fillColor at the end of the animation"},
                                     "onFinished": {"type": "function",
                                                    "info": "an optional function to run when the animation finishes."}},
                            "return": None,
                            "info": "Visually animates fading this object's <b>fillColor</b> to <b>endColor</b>, "
                                    "over <b>duration</b> seconds.  When the animation completes, runs the "
                                    "<b>onFinished</b> function, if one was passed in."},
    }

    handlers = {}


class HelpDataRoundRectangle():
    parent = HelpDataShape

    properties = {
        "cornerRadius": {"type": "int",
                         "info": "The radius used to draw this round rectangle's rounded corners."},
    }

    methods = {
        "AnimateCornerRadius": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                         "endCornerRadius": {"type": "int",
                                                          "info": "the final cornerRadius at the end of the animation"},
                                         "onFinished": {"type": "function",
                                                        "info": "an optional function to run when the animation finishes."}},
                                "return": None,
                                "info": "Visually animates changing this round rectangle's <b>cornerRadius</b> to <b>endCornerRadius</b>, "
                                        "over <b>duration</b> seconds.  When the animation completes, runs the <b>onFinished</b> function, "
                                        "if one was passed in."},
    }

    handlers = {}


class HelpDataCard():
    parent = HelpDataObject

    properties = {
        "bgColor": {"type": "string",
                    "info": "The color used for the background of this card.  This can be a color word like white, "
                            "or an HTML color like #EEEEEE for a light grey."},
        "index": {"type": "int",
                  "info": "This is the card number of this card.  The first card has <b>index</b> 0.  You can "
                          "read this value, but not set it."},
        "canSave": {"type": "bool",
                    "info": "If <b>canSave</b> is <b>True</b>, the user can save the stack while running it. "
                            "If it's <b>False</b>, the user can't save, so the stack will always start out in the same "
                            "state."},
        "canResize": {"type": "bool",
                      "info": "If <b>canResize</b> is <b>True</b>, the user can resize the stack window while running it. "
                              "If it's <b>False</b>, the user can't resize the window while the stack runs."},
    }

    methods = {
        "AnimateBgColor": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                      "endColor": {"type": "string",
                                                   "info": "the final backgroundColor at the end of the animation"},
                                      "onFinished": {"type": "function",
                                                     "info": "an optional function to run when the animation finishes."}},
                             "return": None,
                             "info": "Visually animates this card's <b>backgroundColor</b> to <b>endColor</b>, "
                                     "over <b>duration</b> seconds.  When the animation completes, runs the <b>onFinished</b> function, "
                                     "if one was passed in."},
    }

    handlers = {
        "OnShowCard": {"args": {},
                       "info": "The <b>OnShowCard</b> event is run any time a card is shown, including when the "
                               "first card is initially shown when the stack starts running."},
        "OnHideCard": {"args": {},
                       "info": "The <b>OnHideCard</b> event is run when a card is hidden, right before the new "
                               "card's OnShowCard event is run, when going to another card."},
        "OnKeyDown": {"args": {"keyName": {"type": "string", "info": "The name of the pressed key"}},
                      "info": "The <b>OnKeyDown</b> event is run any time a keyboard key is pressed down.  Regular "
                              "keys are named as capital letters and digits, like 'A' or '1', and other keys have "
                              "keyNames like 'Shift', 'Return', 'Escape', 'Left', and 'Right'."},
        "OnKeyUp": {"args": {"keyName": {"type": "string", "info": "The name of the released key"}},
                    "info": "The <b>OnKeyUp</b> event is run any time a pressed keyboard key is released.  Regular "
                            "keys are named as capital letters and digits, like 'A' or '1', and other keys have "
                            "keyNames like 'Shift', 'Return', 'Escape', 'Left', and 'Right'."},
    }


class HelpDataStack():
    parent = HelpDataObject

    properties = {
        "numCards": {"type": "int",
                     "info": "This is the number of cards in this stack.  You can "
                             "read this value, but not set it."},
    }

    methods = {}

    handlers = {}

