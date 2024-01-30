# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import uiView
import keyword

"""
This file includes descriptions of all CardStock objects, properties, methods, and event handlers for use in
context help, reference docs, and in the future, code completion.
"""


class HelpData():
    reservedNames = None

    @classmethod
    def ForObject(cls, obj):
        return cls.ForType(obj.model.type)

    @classmethod
    def ForType(cls, typeStr):
        if typeStr == "button":                   return HelpDataButton
        elif typeStr == "textfield":              return HelpDataTextField
        elif typeStr == "textlabel":              return HelpDataTextLabel
        elif typeStr == "image":                  return HelpDataImage
        elif typeStr == "webview":                return HelpDataWebView
        elif typeStr == "group":                  return HelpDataGroup
        elif typeStr in ["line", "pen"]:          return HelpDataLine
        elif typeStr in ["shape", "oval", "rect", "polygon"]:return HelpDataShape
        elif typeStr == "roundrect":              return HelpDataRoundRectangle
        elif typeStr == "card":                   return HelpDataCard
        elif typeStr == "stack":                  return HelpDataStack
        return HelpDataObject

    @classmethod
    def GetTypeForProp(cls, propName):
        for c in helpClasses:
            if propName in c.properties:
                return c.properties[propName]["type"]
        return None

    @classmethod
    def GetTypeForMethod(cls, methodName):
        for c in helpClasses:
            if methodName in c.methods:
                return c.methods[methodName]["return"]
        return None

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
    def GetHelpForName(cls, key, objType):
        isFunc = key.endswith("()")
        if objType is None:
            return None
        elif objType == "global":
            allClasses = [HelpDataGlobals]
        elif objType != "any":
            allClasses = []
            c = cls.ForType(objType)
            while c:
                allClasses.append(c)
                c = c.parent
        else:
            allClasses = [HelpDataGlobals]
            allClasses.extend(helpClasses)
            allClasses.remove(HelpDataString)
            allClasses.remove(HelpDataList)
        if not isFunc:
            for c in allClasses:
                if key in c.properties:
                    prop = c.properties[key]
                    text = "<b>" + key + "</b>:<i>" + prop["type"] + "</i> - " + prop["info"]
                    return text
        else:
            key = key[:-2]
            for c in allClasses:
                if key in c.methods:
                    method = c.methods[key]
                    argText = ""
                    for name, arg in method["args"].items():
                        typeText = (":<i>" + arg["type"] + " </i>") if "type" in arg else ""
                        argText += "&nbsp;&nbsp;&nbsp;&nbsp;<b>" + name + "</b>" + typeText + " - " + arg[
                            "info"] + "<br/>"
                    ret = ("Returns: <i>" + method["return"] + "</i><br/>") if method["return"] else ""
                    name = key + "(" + ', '.join(method["args"].keys()) + ")"
                    text = f"<b>{name}</b><br/>{argText}{ret}<br/>{method['info']}"
                    return text
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
            for key in sorted(data.properties):
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
                    argText += "&nbsp;&nbsp;&nbsp;&nbsp;<b>" + name + "</b>:<i>" + arg["type"] + " </i> - " + arg["info"] + "<br/>"
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
            for key in sorted(data.handlers):
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
            for key in sorted(data.methods):
                method = data.methods[key]
                argText = ""
                for name, arg in method["args"].items():
                    typeText = (":<i>" + arg["type"] + " </i>") if "type" in arg else ""
                    argText += "<b>" + name + "</b>" + typeText + " - " + arg["info"] + "<br/>"
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
        for key in sorted(data.variables):
            var = data.variables[key]
            rows.append([key, "<i>" + var["type"] + "</i>", var["info"]])
        return cls.HtmlTableFromLists(rows)

    @classmethod
    def GlobalFunctionsTable(cls):
        data = HelpDataGlobals
        rows = []
        rows.append(["Method", "Arguments", "Return", "Description"])
        for key in sorted(data.functions):
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
                 ["Text Field", "textfield"], ["Text Label", "textlabel"], ["Web View", "webview"],
                 ["Image", "image"], ["Line & Pen", "line"],
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
            cls.reservedNames = ["key_name", "mouse_pos", "message", "URL", "did_load", "other_object", "edge", "elapsed_time"]
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
                 ["<i>bool</i>", "A bool or boolean value holds a simple True or False."],
                 ["<i>int</i>", "An int or integer value holds any whole number, positive or negative."],
                 ["<i>float</i>", "A float or floating point value holds any number, including with a decimal point."],
                 ["<i>string</i>", "A string value holds text."],
                 ["<i>list</i>", "A list value is a container that holds a list of other values."],
                 ["<i>dictionary</i>", "A dictionary value is a container that holds named items, as key, value pairs."],
                 ["<i>point</i>", "A point value is like a list of two numbers, x and y, that describes a location in "
                                  "the card.  For a point variable p, you can access the x value as p[0] or p.x, and "
                                  "the y value as either p[1] or p.y."],
                 ["<i>size</i>", "A size value is like a list of two numbers, width and height, that describes the "
                                 "size of an object in the card.  For a size variable s, you can access the width "
                                 "value as s[0] or s.width, and the height value as either s[1] or s.height"],
                 ["<i>object</i>", "An object value can hold any CardStock object, like a button, card, or oval."],
                 ["<i>button, textfield, textlabel, webview, image, oval, rect, roundrect, polygon, line</i>",
                  "A value of any of these types holds a CardStock object of that specific type."],
                 ]


class HelpDataGlobals():
    variables = {
        "self": {"type": "object",
                  "info": "In any object's event code, <b>self</b> always refers to the object that contains this code."},
        "stack": {"type": "stack",
                  "info": "The <b>stack</b> is the object that represents your whole program.  You can access cards "
                          "in this stack as stack.cardName."},
        "card": {"type": "card",
                 "info": "The <b>card</b> is the object that represents the currently loaded card in your stack.  You "
                         "can access the objects on this card as card.objectName."},
    }
    properties = variables

    functions = {
        "wait": {"args": {"duration": {"type": "float", "info": "Number of seconds to delay."}}, "return": None,
                 "info": "Delays the program from running for <b>duration</b> seconds.  No movements or animations "
                         "will happen during this time."},
        "distance": {"args": {"pointA": {"type": "point", "info": "One location on the card."},
                              "pointB": {"type": "point", "info": "Another location on the card."}}, "return": "float",
                     "info": "Return the distance between <b>pointA</b> and <b>pointB</b>."},
        "angle_from_points": {"args": {"pointA": {"type": "point", "info": "One location on the card."},
                              "pointB": {"type": "point", "info": "Another location on the card."}}, "return": "float",
                     "info": "Return the angle between the bottom edge of the card, and the line from <b>pointA</b> to "
                             "<b>pointB</b>, rotating clockwise.  This can be useful to find the rotation angle to use "
                             "to point an object at <b>pointA</b> towards <b>pointB</b>."},
        "rotate_point": {"args": {"point": {"type": "point", "info": "A distance in x and y, from (0,0)."},
                              "angle": {"type": "float", "info": "An angle in degrees to rotate the point around (0,0)."}}, "return": "point",
                     "info": "Returns a new point, calculated by rotating <b>point</b> by <b>angle</b> degrees, "
                             "clockwise around the point (0,0).  This is useful to, for example, set the speed of a "
                             "cannonball that should be moving in the direction that a cannon is already pointing."},
        "run_after_delay": {"args": {"duration": {"type": "float", "info": "Number of seconds to delay."},
                                   "func": {"type": "function", "info": "A function to call after the delay."},
                                   "*args": {"type": "any", "info": "0 or more arguments and/or keyword arguments to pass into <b>func</b>."}}, "return": None,
                          "info": "This function lets your program continue running while a timer waits for <b>duration</b> seconds, "
                                  "and then runs the functions <b>func</b>, passing it any additional arguments you add "
                                  "after <b>func</b>.  Movements, animations, and user interaction "
                                  "will all continue during this time."},
        "time": {"args": {}, "return": "float",
                 "info": "Returns the time in seconds since 'The Unix Epoch', midnight UTC on January 1st, 1970.  That "
                         "date doesn't usually matter, since most often, you'll store the time at one point in your "
                         "program, and then compare it to the new time somewhere else, to determine the difference."},
        "paste": {"args": {}, "return": "list",
                  "info": "Pastes any CardStock objects in the clipboard from a previous Copy or Cut command onto the "
                          "current card, and returns a list of these pasted objects."},
        "alert": {"args": {"message": {"type": "any", "info": "Text to show in the alert dialog."}}, "return": None,
                  "info": "Shows an alert dialog to the user, with the <b>message</b> you provide, and offers an OK button."},
        "ask_yes_no": {"args": {"message": {"type": "any", "info": "Text to show in the dialog."}}, "return": "bool",
                "info": "Shows an alert dialog to the user, with the <b>message</b> you provide, and offers Yes and No "
                        "buttons.  Returns True if Yes is clicked, and False if No is clicked."},
        "ask_text": {"args": {"message": {"type": "any", "info": "alert text to show in the dialog."},
                             "defaultResponse": {"type": "any", "info": "An optional default value to pre-fill the result field."}},
                    "return": "string",
                "info": "Shows an alert dialog to the user, with the <b>message</b> you provide, and a text field "
                        "to enter a response, along with Ok and Cancel buttons.  Returns the user-entered text in the "
                        "response field if the Ok button is clicked, or None if Cancel is clicked."},
        "goto_card": {"args": {"card": {"type": "(object, string, or int)", "info": "A card object, a card name, or the number of a card to go to."}}, "return": None,
                     "info": "Goes to the card passed in as <b>card</b>, the card with the name passed in as <b>card</b>, "
                             "or the card number passed in as <b>card</b>.  This sends the on_hide_card event "
                             "for the current card, and then the on_show_card event for the new card, or does nothing if "
                             "there is no card with that name or number."},
        "goto_next_card": {"args": {}, "return": None,
                         "info": "Goes to the next card in the stack.  If we're already on the last card, then loop back to "
                                 "the first card.  This sends the on_hide_card event for the current card, and then the "
                                 "on_show_card event for the new card."},
        "goto_previous_card": {"args": {}, "return": None,
                             "info": "Goes to the previous card in the stack.  If we're already on the first card, then loop back to "
                                     "the last card.  This sends the on_hide_card event for the current card, and then the "
                                     "on_show_card event for the new card."},
        "run_stack": {"args": {"filename": {"type": "string", "info": "The path to a stack file to run"},
                               "cardNumber": {"type": "int", "info": "An optional card number of the new stack to start on.  This defaults to card number 1, the first card."},
                               "setupValue": {"type": "any", "info": "An optional value to pass into the new stack."}},
                      "return": "any",
                      "info": "Opens the stack at the path given by the <b>filename</b> argument, and optionally starts on "
                              "the card number specified by the <b>cardNumber</b> argument.  If you include a "
                              "<b>setupValue</b> argument, this will be passed into the new stack, which can access it by "
                              "calling <b>stack.get_setup_value()</b>.  The <b>run_stack()</b> call waits "
                              "until the new stack exits by calling <b>stack.return_from_stack(returnVal)</b>, and then "
                              "this <b>run_stack()</b> call returns that returnVal value, or None if no returnValue was given."},
        "open_url": {"args": {"URL": {"type": "string",
                                        "info": "This is the URL to open."},
                              "in_place": {"type": "bool",
                                      "info": "Optional parameter: When running in-browser after uploading your stack, if this is set to "
                                              "True, the <b>URL</b> will open in the current tab, instead of opening a new tab.  Defaults to False."}
                              },
                      "return": None,
                      "info": "Opens the given <b>URL</b> in the default browser."},
        "request_url": {"args": {"URL": {"type": "string",
                                         "info": "This is the URL to request."},
                                 "params": {"type": "dictionary",
                                         "info": "This optionally holds query parameters for your request."},
                                 "headers": {"type": "dictionary",
                                         "info": "This optionally holds HTTP headers for your request."},
                                 "method": {"type": "string",
                                         "info": "This optionally holds an HTTP method name like \"GET\" or \"POST\".  "
                                                 "Requests default to \"GET\"."},
                                 "timeout": {"type": "float",
                                         "info": "This optionally allows setting a timeout in seconds, after which the "
                                                 "request will be cancelled."},
                                 "on_done": {"type": "function",
                                         "info": "This optional function is called when the request has received a "
                                                 "response.  This callback function receives 2 arguments: an HTTP "
                                                 "status code as an int, and the response as a string, or as binary "
                                                 "data if the response is not text."},
                                },
                        "return": None,
                        "info": "Requests the given <b>URL</b>.  If an <b>on_done function</b> is provided, this request_url() "
                                "function will return immediately, and when the response is received, the given "
                                "<b>on_done(status, result)</b> function will run.  If no <b>on_done</b> function is provided, "
                                "this request_url() will wait until it gets a response, and will return the response "
                                "data as text or binary data.  Optional <b>headers</b> and query <b>params</b> can be "
                                "provided as dictionaries, and <b>method</b> and <b>timeout</b> can be provided as well, "
                                "if needed. <br/><br/><b>Examples:</b><br/><br/>"
                                "# Request the text from a URL and wait until we get it back<br/>"
                                "htmlString = request_url(\"https://google.com/\")<br/><br/>"
                                "# Request the text from a URL without waiting.  got_result() is called when it's ready.<br/>"
                                "def got_result(status, text):<br/>"
                                "&nbsp;&nbsp;&nbsp;&nbsp;if status == 200:<br/>"
                                "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print(text)<br/>"
                                "request_url(\"https://google.com/\", on_done=got_result)<br/><br/>"
                                "# Request the text from a URL, with parameters, and wait until we get it back<br/>"
                                "jokeJson = request_url(\"https://geek-jokes.sameerkumar.website/api\", params={\"format\": \"json\"})"},
        "play_sound": {"args": {"file": {"type": "string",
                                        "info": "This is the filename of the .wav format audio file to play, relative to where the stack file lives."}},
                      "return": None,
                      "info": "Starts playing the .wav formatted sound file at location <b>file</b>."},
        "stop_sound": {"args": {},
                      "return": None,
                      "info": "Stops all currently playing sounds."},
        "broadcast_message": {"args": {"message": {"type": "string",
                                        "info": "This is the message to send."}},
                      "return": None,
                      "info": "Sends the <b>message</b> to this card, and all objects on this card, causing each of their "
                              "on_message events to run with this <b>message</b>."},
        "is_key_pressed": {"args": {"key_name": {"type": "string", "info": "The name of the key to check."}},
                         "return": "bool",
                         "info": "Returns <b>True</b> if the named keyboard key is currently pressed down, otherwise "
                                 "returns <b>False</b>."},
        "is_mouse_pressed": {"args": {},
                         "return": "bool",
                         "info": "Returns <b>True</b> if the main mouse button is currently pressed down, or the user "
                                 "is touching a touch screen, otherwise returns <b>False</b>."},
        "is_using_touch_screen": {"args": {},
                         "return": "bool",
                         "info": "Returns <b>True</b> if the most recent 'mouse' event came from a touch "
                                 "screen, otherwise returns <b>False</b>."},
        "get_mouse_pos": {"args": {},
                         "return": "point",
                         "info": "Returns the current position of the mouse, whether or not it is inside of the stack "
                                 "window.  This point's x and y values can be negative, if the mouse is to the left "
                                 "or below the bottom left corner of the stack window."},
        "clear_focus": {"args": {},
                             "return": None,
                             "info": "If any TextField has focus, unfocus it, so that any typing will no longer be entered there."},
        "ColorRGB": {"args": {"red": {"type": "float", "info": "The red component of the color as a number from 0.0 to 1.0."},
                               "green": {"type": "float", "info": "The green component of the color as a number from 0.0 to 1.0."},
                               "blue": {"type": "float", "info": "The blue component of the color as a number from 0.0 to 1.0."}},
                         "return": "string",
                         "info": "Returns an HTML color string of the form '#rrggbb' based on the red, green, and blue values given.  For example "
                                 "<b>ColorRGB(1, 0, 0)</b> returns '#FF0000' which is bright red."},
        "ColorHSB": {"args": {"hue": {"type": "float", "info": "The hue of the color as a number from 0.0 to 1.0, where 0 means red, and goes up through the rainbow, back to red again at 1.0."},
                               "saturation": {"type": "float", "info": "The saturation of the color as a number from 0.0 to 1.0, where 0 means gray and 1 means fully saturated color."},
                               "brightness": {"type": "float", "info": "The brightness component of the color as a number from 0.0 to 1.0, where 0 means black."}},
                         "return": "string",
                         "info": "Returns an HTML color string of the form '#rrggbb'.  For example "
                                 "<b>ColorHSB(0, 1, 1)</b> returns '#FF0000' which is bright red."},
        "Point": {"args": {"x": {"type": "float", "info": "The x (horizontal) part of this point."},
                           "y": {"type": "float", "info": "The y (vertical) part of this point."}},
                         "return": "point",
                         "info": "Returns a point object."},
        "Size": {"args": {"width": {"type": "int", "info": "The width (horizontal) part of this size."},
                           "height": {"type": "int", "info": "The height (vertical) part of this size."}},
                         "return": "size",
                         "info": "Returns a size object."},
        "quit": {"args": {},
                      "return": None,
                      "info": "Stops running the stack, closes the stack window, and exits the stack viewer program."},
    }
    methods = functions

class HelpDataObject():
    parent = None
    types = ["object"]
    properties = {
        "name": {"type": "string",
                 "info": "Every object has a <b>name</b> property.  These are forced to be unique within each card, "
                         "since these become the names of your object variables that you access from your code.  From "
                         "your code, you can get an object's name, but you can not set it."},
        "type": {"type": "string",
                 "info": "Every object has a <b>type</b> property.  It will be one of 'button', 'textfield', 'textlabel', "
                         "'webview', 'image', 'line', 'oval', 'rect, 'roundrect', 'polygon', 'stack', 'card', 'group'.  Your code can get "
                         "this value, but not set it."},
        "data": {"type": "dictionary",
                 "info": "Every object has a <b>data</b> property.  It is a dictionary that allows you to persistently "
                         "store arbitrary data in any object within a stack that has <b>can_save</b> set to True."},
        "position": {"type": "point",
                     "info": "The <b>position</b> property is a point value that describes where on the "
                             "card this object's bottom-left corner is.  The first number, <b>x</b>, is how many pixels the object is "
                             "from the left edge of the card.  The second number, <b>y</b>, is how far up from the bottom."},
        "size": {"type": "size",
                 "info": "The <b>size</b> property is a size value that describes how big this object is on screen. "
                         "The first number, <b>width</b>, is how wide the object is, and the second number, <b>height</b>, is how tall."},
        "center": {"type": "point",
                   "info": "The <b>center</b> property is a point value that describes where on the card this "
                           "object's center point is.  The first number, <b>x</b>, is how many pixels the object's center "
                           "is from the left edge of the card.  The second number, <b>y</b>, is how far up from the bottom.  "
                           "This value is not stored, but computed based on position and size."},
        "rotation": {"type": "float",
                     "info": "This is the angle in degrees clockwise to rotate this object.  0 is upright.  Note that "
                             "not all objects can be rotated.  Card and stack objects can not rotate, and text fields "
                             "and web views can't rotate either."},
        "speed": {"type": "point",
                  "info": "This is a point value corresponding to the current speed of the object, in pixels/second "
                          "in both the <b>x</b> and <b>y</b> directions."},
        "is_visible": {"type": "bool",
                    "info": "<b>True</b> if this object <b>is_visible</b>, or <b>False</b> if it is hidden.  If this "
                            "object is in a group that has been hidden, this object's <b>is_visible</b> property will be "
                            "<b>False</b> as well."},
        "parent": {"type": "object",
                   "info": "<b>parent</b> is the object that contains this object.  For most objects, it is the card, unless this "
                           "object has been grouped, in which case its <b>parent</b> is the group object  A card's "
                           "<b>parent</b> is the stack.  The stack has no <b>parent</b>, so stack.parent is <b>None</b>."},
        "children": {"type": "list",
                     "info": "<b>children</b> is the list of objects that this object contains.  A stack has children "
                             "that are cards.  A card and a group can both have children objects. Other objects have "
                             "no children."},
    }

    methods = {
        "copy": {"args": {},
                 "return": None,
                 "info": "Copies this object onto the clipboard, just like the Edit menu Copy command."},
        "cut": {"args": {},
                "return": None,
                "info": "Copies this object onto the clipboard and then deletes it, just like the Edit menu Cut command."},
        "clone": {"args": {"...": {"type": "Any", "info": "optionally set more properties here.  For example, "
                                           "include position=(10,10)"}},
                  "return": "object",
                  "info": "Duplicates this object, and updates the new object's name to be unique, and then returns "
                          "the new object for you to store into a variable."},
        "delete": {"args": {},
                   "return": None,
                   "info": "Deletes this object.  Like Cut, but the object does not get copied to the clipboard."},
        "send_message": {"args": {"message": {"type": "string", "info": "The message being sent to this object."}},
                        "return": None,
                        "info": "Sends a <b>message</b> to this object, that the object can handle in its on_message event code.  For "
                                "example, you could send the message 'reset' to an object, and in its on_message code, "
                                "it could check for whether <b>message</b> == 'reset', and then set some variables back to their initial values."},
        "show": {"args": {},
                 "return": None,
                 "info": "Shows this object if it was not visible."},
        "hide": {"args": {},
                 "return": None,
                 "info": "Hides this object if it was visible."},
        "child_with_base_name": {"args": {"baseName": {"type": "string", "info": "The beginning of the name of the child object to find."}},
                              "return": "object",
                              "info": "Returns this object's first child object whose name starts with <b>baseName</b>.  For example, "
                                      "if you have multiple group objects that each contain one button, named button_1, button_2, etc.,"
                                      "then you can call each group's group.child_with_base_name('button') to get that group's button object."},
        "flip_horizontal": {"args": {},
                 "return": None,
                 "info": "Flips the object horizontally.  This only visibly changes cards, images, groups, and some shapes."},
        "flip_vertical": {"args": {},
                 "return": None,
                 "info": "Flips the object vertically.  This only visibly changes cards, images, groups, and some shapes."},
        "order_to_front": {"args": {},
                 "return": None,
                 "info": "Moves this object to the front of the card or group it is contained in, in front of all other objects.  But note that "
                         "currently, all text fields and web views will be displayed in front of other objects."},
        "order_forward": {"args": {},
                 "return": None,
                 "info": "Moves this object one position closer to the front of the card or group it is contained in.  But note that "
                         "currently, all text fields and web views will be displayed in front of other objects."},
        "order_backward": {"args": {},
                 "return": None,
                 "info": "Moves this object one position closer to the back of the card or group it is contained in.  But note that "
                         "currently, all text fields and web views will be displayed in front of other objects."},
        "order_to_back": {"args": {},
                 "return": None,
                 "info": "Moves this object to the back of the card or group it is contained in, behind all other objects.  But note that "
                         "currently, all text fields and web views will be displayed in front of other objects."},
        "order_to_index": {"args": {"toIndex": {"type": "int", "info": "The index to move this object to, in the list of "
                                 "the card or group's children.  Index 0 is at the back."}},
                       "return": None,
                         "info": "Moves this object to the given index, in the list of "
                                 "its parent's children, with 0 being at the back.  But note that "
                         "currently, all text fields and web views will be displayed in front of other objects."},
        "get_code_for_event": {"args": {"eventName": {"type": "string", "info": "The name of the event to look up."}},
                            "return": "string",
                            "info": "Returns a string containing this object's event code for the given "
                                    "<b>eventName</b>.  For example, button_1.get_code_for_event('on_click') will "
                                    "return the code in the object named button_1 for the 'on_click' event."},
        "set_code_for_event": {"args": {"eventName": {"type": "string", "info": "The name of the event to set."},
                                     "code": {"type": "string", "info": "The code to run on this event."}},
                            "return": None,
                            "info": "Sets the <b>code</b> to be run when the event named <b>eventName</b> triggers for this object.  "
                                    "For example, button_1.set_code_for_event('on_click', 'alert(\"Hello\")') will set up "
                                    "button_1 to show an alert when clicked."},
        "stop_handling_mouse_event": {"args": {},
                                   "return": None,
                                   "info": "If you call this method from your event code for any on_mouse_press(), on_mouse_move(), "
                                           "or on_mouse_release() event, CardStock will skip running code for this event "
                                           "for any overlapping objects underneath this object, which would otherwise "
                                           "be run immediately after this object's event code finishes.  Calling "
                                           "this method from any non-mouse event code does nothing.  Should be run as self.stop_handling_mouse_event()."},
        "is_touching": {"args": {"other": {"type": "object", "info": "The other object to compare to this one"}},
                       "return": "bool",
                       "info": "Returns <b>True</b> if this object is touching the <b>other</b> object passed into "
                               "this function, otherwise returns <b>False</b>."},
        "set_bounce_objects": {"args": {"objects": {"type": "list", "info": "A list of objects that this object should bounce off of"}},
                             "return": None,
                             "info": "Sets up this object so that it will automatically bounce off "
                                     "of the given objects, if it intersects with an edge of "
                                     "any of the objects in the list, while this object's speed is non-zero.  When an "
                                     "object bounces, its on_bounce() event will run."},
        "is_touching_point": {"args": {"point": {"type": "point", "info": "Checks whether this point is inside the object."}},
                       "return": "bool",
                       "info": "Returns <b>True</b> if this object is touching the <b>point</b> passed into "
                               "this function, otherwise returns <b>False</b>."},
        "is_touching_edge": {"args": {"other": {"type": "object", "info":"The other object to compare to this one"}},
                           "return": "list",
                           "info": "Returns an empty list if this object is not touching any edges of the <b>other</b> "
                                   "object passed into this function.  If this object is touching any edges of the "
                                   "other object, the return value will be a list including one or more of the strings:"
                                   " 'Top', 'Bottom', 'Left', or 'Right', accordingly."},
        "animate_position": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                     "end_position": {"type": "point",
                                                     "info": "the destination bottom-left corner position at the end of the animation"},
                                     "on_finished": {"type": "function",
                                                    "info": "an optional function to run when the animation finishes"},
                                     "*args": {"type": "any", "info": "0 or more arguments and/or keyword arguments to pass into <b>on_finished</b>."}},
                            "return": None,
                            "info": "Visually animates the movement of this object from its current position to <b>end_position</b>, "
                                    "over <b>duration</b> seconds.  When the animation completes, runs the "
                                    "<b>on_finished</b> function, if one was passed in."},

        "animate_center": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                   "end_position": {"type": "point",
                                                   "info": "the destination center position at the end of the animation"},
                                   "on_finished": {"type": "function",
                                                  "info": "an optional function to run when the animation finishes"},
                                   "*args": {"type": "any", "info": "0 or more arguments and/or keyword arguments to pass into <b>on_finished</b>."}},
                          "return": None,
                          "info": "Visually animates the movement of this object from its current position to have its center at <b>end_center</b>, "
                                  "over <b>duration</b> seconds.  When the animation completes, runs the "
                                  "<b>on_finished</b> function, if one was passed in."},

        "animate_size": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                 "end_size": {"type": "size", "info": "the final size of this object at the end of the animation"},
                                 "on_finished": {"type": "function", "info": "an optional function to run when the animation finishes"},
                                 "*args": {"type": "any", "info": "0 or more arguments and/or keyword arguments to pass into <b>on_finished</b>."}},
                        "return": None,
                        "info": "Visually animates the <b>size</b> of this object from its current size to <b>end_size</b>, "
                                "over <b>duration</b> seconds.  When the animation completes, runs the "
                                "<b>on_finished</b> function, if one was passed in."},
        "animate_rotation": {"args": {"duration": {"type": "float", "info": "time in seconds to run the animation"},
                                     "end_rotation": {"type": "int",
                                                             "info": "the final rotation angle in degrees clockwise at "
                                                                     "the end of the animation"},
                                     "force_direction":{"type": "int",
                                                               "info": "an optional hint to tell CardStock which direction "
                                                                       "you want the object to rotate.  A positive value forces "
                                                                       "clockwise rotation, and a negative value forces counter-clockwise."},
                                     "on_finished": {"type": "function",
                                                    "info": "an optional function to run when the animation finishes."},
                                     "*args": {"type": "any", "info": "0 or more arguments and/or keyword arguments to pass into <b>on_finished</b>."}},
                            "return": None,
                            "info": "Visually animates changing this object's <b>rotation</b> angle to <b>end_rotation</b>, "
                                    "over <b>duration</b> seconds.  When the animation completes, runs the "
                                    "<b>on_finished</b> function, if one was passed in."},
        "stop_animating": {"args": {"property_name": {"type": "string",
                                                    "info": "optional name of the property to stop animating, for "
                                                            "example: \"size\" or \"position\".  If left blank, stops "
                                                            "all animations of properties of this object."}},
                           "return": None,
                           "info": "Stops the animation specified by <b>property_name</b> from running on this object, "
                                   "or if no <b>property_name</b> is specified, stops all running animations on this "
                                   "object.  Any animated properties are left at their current, mid-animation values."},
    }

    handlers = {
        "on_setup": {"args": {},
                    "info": "The <b>on_setup</b> event is run once for every object in your stack, immediately when the stack "
                            "starts running, before showing the first card.  This is a great place to run any imports that your "
                            "program needs, and to define functions, and set up any variables with their initial values."},
        "on_mouse_press": {"args": {"mouse_pos": {"type": "point", "info": "This is the current position of the mouse pointer on the card."}},
                        "info": "The <b>on_mouse_press</b> event is run when the mouse button gets pressed down inside of this object, "
                                "and gives you the current mouse position as the point <b>mouse_pos</b>.  This event will be "
                                "run for all objects underneath the mouse pointer, from the topmost object, down to the card "
                                "itself, unless this propagation is stopped by calling self.stop_handling_mouse_event() from your code.  "
                                "Note that Mouse events are run whether you use a mouse, trackpad, touchscreen, or any other pointing device."},
        "on_mouse_move": {"args": {"mouse_pos": {"type": "point", "info": "This is the current position of the mouse pointer on the card."}},
                        "info": "The <b>on_mouse_move</b> event is run every time the mouse moves, while over this object, whether "
                                "or not the mouse button is down, and gives you the current mouse position as the point <b>mouse_pos</b>.  "
                                "This event will be "
                                "run for all objects underneath the mouse pointer, from the topmost object, down to the card "
                                "itself, unless this propagation is stopped by calling self.stop_handling_mouse_event() from your code.  "
                                "Note that Mouse events are run whether you use a mouse, trackpad, touchscreen, or any other pointing device."},
        "on_mouse_release": {"args": {"mouse_pos": {"type": "point", "info": "This is the current position of the mouse pointer on the card."}},
                      "info": "The <b>on_mouse_release</b> event is run when the mouse button is released over this object, and "
                              "gives you the current mouse position as the point <b>mouse_pos</b>.  This event will be "
                                "run for all objects underneath the mouse pointer, from the topmost object, down to the card "
                                "itself, unless this propagation is stopped by calling self.stop_handling_mouse_event() from your code.  "
                                "Note that Mouse events are run whether you use a mouse, trackpad, touchscreen, or any other pointing device."},
        "on_mouse_enter": {"args": {"mouse_pos": {"type": "point", "info": "This is the current position of the mouse pointer on the card."}},
                         "info": "The <b>on_mouse_enter</b> event is run when the mouse pointer moves onto this object."},
        "on_mouse_exit": {"args": {"mouse_pos": {"type": "point", "info": "This is the current position of the mouse pointer on the card."}},
                        "info": "The <b>on_mouse_exit</b> event is run when the mouse pointer moves back off of this object."},
        "on_bounce": {"args": {"other_object": {"type": "object", "info": "The other object that this object just bounced off of.",},
                              "edge": {"type": "string", "info": "The edge of the other object that we just bounced off of ('Left', 'Right', 'Top', or 'Bottom')."}},
                     "info": "The <b>on_bounce</b> event is run whenever this object collides with an object that it "
                             "knows to bounce off of.  Set up the list of objects that this object will bounce off "
                             "of by calling object.set_bounce_objects(list) with that list of objects.  For example, if "
                             "you have called ball.set_bounce_objects([card]), then the ball object will bounce off of "
                             "the edges of the card.  And when the ball touches the top of the card, ball.speed.y will "
                             "flip from positive to negative, so that the ball will start moving downwards, and the "
                             "<b>on_bounce(other_object, edge)</b> event will run with other_object=card and edge='Top'."},
        "on_message": {"args": {"message": {"type": "string", "info": "This is the message string that was passed into "
                                                                     "a send_message() or broadcast_message() call."}},
                      "info": "The <b>on_message</b> event is run when broadcast_message() is called, or send_message() "
                              "is called on this object.  The <b>message</b> string passed into send_message() or "
                              "broadcast_message() is delivered here."},
        "on_periodic": {"args": {"elapsed_time": {"type": "float", "info": "This is the number of seconds since the last time this event was run, normally about 0.03."}},
                   "info": "The <b>on_periodic</b> event is run approximately 30 times per second on every object on the current page, "
                           "and gives your object a chance to run periodic checks, for example checking for collisions using is_touching()."},
    }


class HelpDataButton():
    parent = HelpDataObject
    types = ["button"]

    properties = {
        "title": {"type": "string",
                  "info": "The <b>title</b> property is the visible text on the button."},
        "style": {"type": "[Border, Borderless, Checkbox, Radio]",
                   "info": "Buttons with style <b>Border</b> show a rounded rectangular border, "
                           "depending on your computer's operating system.  This is the most commonly seen style of "
                           "button.  The <b>Borderless</b> style behaves the same, but is drawn without a border."
                           "You can also set style to be <b>Checkbox</b>, which allows users to alternately select and "
                           "deselect this button, and it is drawn with a checkbox to show the selection state.  "
                           "You can set the style to <b>Radio</b>, which allows selecting only one button at a time from a "
                           "group of Radio buttons, and is drawn with a round selection indicator.  All <b>Radio</b> "
                           "buttons with the same immediate parent (the Card, or a Group) are considered to be in the "
                           "same Radio button group, and selecting any of these will automatically deselect all of the "
                           "rest in the group."},
        "is_selected": {"type": "bool",
                        "info": "For Border and Borderless style buttons, this is always False.  For Checkbox style "
                                "buttons, this is True when the Checkbox is checked.  For Radio buttons, this is True "
                                "when this Radio button is the selected button in its group."}
    }

    methods = {
        "click": {"args": {}, "return": None,
                    "info": "Runs this button's on_click event code."},
        "get_radio_group": {"args": {}, "return": "list",
                  "info": "If this button is a Radio button, then return a list of all Radio buttons in this button's "
                          "Radio group, which is defined as all Radio buttons with the same direct parent (Card or "
                          "Group).  Otherwise returns an empty list."},
        "get_radio_group_selection": {"args": {}, "return": "button",
                  "info": "If this button is a Radio button, then return the selected Radio button in this button's "
                          "Radio group. If this button is not a Radio button, or if none of the buttons in the group are "
                          "selected, returns None."},
    }

    handlers = {
        "on_click": {"args": {},
                    "info": "The <b>on_click</b> event is run when a user clicks down on this button, and releases the "
                            "mouse, while still inside the button.  It is also run when the button's click() "
                            "method is called."},
        "on_selection_changed": {"args": {"is_selected": {"type": "bool",
                                                          "info": "The new selection state of this button.  True "
                                                                  "if this button was just selected, otherwise False."}},
                                 "info": "Used by Checkbox and Radio style buttons only, the <b>on_selection_changed</b> event "
                                         "is run when a user selects or deselects this button. When a Radio button is "
                                         "selected, this event will be run first for any previously selected Radio "
                                         "button, with <b>is_selected</b> = False to deselect the old choice, and then "
                                         "for this newly selected Radio button with <b>is_selected</b> = True."},
    }


class HelpDataTextField():
    parent = HelpDataObject
    types = ["textfield"]

    properties = {
        "text": {"type": "string",
                 "info": "The <b>text</b> property holds the contents of this field as a string."},
        "alignment": {"type": "[Left, Center, Right]",
                      "info": "By default, text fields start aligned to the left, but you can change this property to make "
                              "your text centered, or aligned to the right."},
        "text_color": {"type": "string",
                      "info": "The color used for the text in this field.  This can be a color word like red, or an "
                              "HTML color like #333333 for dark gray."},
        "font": {"type": "[Default, Serif, Sans-Serif, Mono]",
                 "info": "The <b>font</b> used for the text in this field."},
        "font_size": {"type": "int",
                     "info": "The point size for the font used for the text in this field."},
        "is_bold": {"type": "bool",
                 "info": "Set to True if this object's text is bold."},
        "is_italic": {"type": "bool",
                   "info": "Set to True if this object's text is italic."},
        "has_focus": {"type": "bool",
                     "info": "<b>True</b> if this TextField is focused (if it is selected for typing into), otherwise "
                             "<b>False</b>. This value is not settable, but you can call the method focus() to try to "
                             "focus this Field."},
        "selection": {"type": "list",
                      "info": "A text field's <b>selection</b> value is a list of 2 numbers.  The first is the start position "
                              "of the selection within the field's text, and the second is the position of the end "
                              "of the selection.  For example, if the text is 'Hello', and the 'He' is selected, then "
                              "the value of <b>selection</b> would be (0, 2)."},
        "selected_text": {"type": "string",
                         "info": "A text field's <b>selected_text</b> value is the string that is currently selected within "
                                 "the field's text.  For example, if the text is 'Hello', and the 'He' is selected, "
                                 "then the <b>selected_text</b> value would be 'He'."},
        "is_editable": {"type": "bool",
                     "info": "By default text fields can be edited by the user.  But you can set this to <b>False</b> "
                             "so that the text can not be edited."},
        "is_multiline": {"type": "bool",
                      "info": "By default, text fields hold only one line of text.  But you can set the "
                              "<b>is_multiline</b> property to <b>True</b> to let them hold multiple lines of text."},
    }

    methods = {
        "animate_font_size": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                      "end_size": {"type": "string",
                                                   "info": "the final font_size at the end of the animation"},
                                      "on_finished": {"type": "function",
                                                     "info": "an optional function to run when the animation finishes."},
                                      "*args": {"type": "any", "info": "0 or more arguments and/or keyword arguments to pass into <b>on_finished</b>."}},
                             "return": None,
                             "info": "Visually animates changing this object's <b>font_size</b> to <b>end_size</b>, "
                                     "over <b>duration</b> seconds.  When the animation completes, runs the "
                                     "<b>on_finished</b> function, if one was passed in."},
        "animate_text_color": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                      "end_color": {"type": "string",
                                                   "info": "the final text_color at the end of the animation"},
                                      "on_finished": {"type": "function",
                                                     "info": "an optional function to run when the animation finishes."},
                                      "*args": {"type": "any", "info": "0 or more arguments and/or keyword arguments to pass into <b>on_finished</b>."}},
                             "return": None,
                             "info": "Visually animates fading this object's <b>text_color</b> to <b>end_color</b>, "
                                     "over <b>duration</b> seconds.  When the animation completes, runs the "
                                     "<b>on_finished</b> function, if one was passed in."},
        "enter": {"args": {}, "return": None,
                    "info": "Runs this text field's on_text_enter event code."},
        "select_all": {"args": {}, "return": None,
                      "info": "Selects all text in this text field."},
        "focus": {"args": {},
                  "return": None,
                  "info": "Selects this TextField so that it will handle key presses.  Typed words will get entered "
                          "into the currently focused TextField."},
    }

    handlers = {
        "on_text_changed": {"args": {},
                          "info": "The <b>on_text_changed</b> event is run every time the user makes any change to the text in this text field."},
        "on_text_enter": {"args": {},
                        "info": "The <b>on_text_enter</b> event is run when the user types the Enter key in this text field."},
    }


class HelpDataTextLabel():
    parent = HelpDataObject
    types = ["textlabel"]

    properties = {
        "text": {"type": "string",
                 "info": "The <b>text</b> property is the text contents of this label."},
        "alignment": {"type": "[Left, Center, Right]",
                      "info": "By default text fields start aligned to the left, but you can change this property to make "
                              "your text centered, or aligned to the right."},
        "can_auto_shrink": {"type": "bool",
                       "info": "When the <b>can_auto_shrink</b> property is True, the <b>font_size</b> of the text in this "
                               "label will shrink if needed, to fit into the label object's current size."},
        "text_color": {"type": "string",
                      "info": "The color used for the text in this label.  This can be a color word like red, or an "
                              "HTML color like #333333 for dark gray."},
        "font": {"type": "[Default, Serif, Sans-Serif, Mono]",
                 "info": "The <b>font</b> used for the text in this label."},
        "font_size": {"type": "int",
                     "info": "The point size for the font used for the text in this label."},
        "is_bold": {"type": "bool",
                 "info": "Set to True if this object's text is bold."},
        "is_italic": {"type": "bool",
                   "info": "Set to True if this object's text is italic."},
        "is_underlined": {"type": "bool",
                       "info": "Set to True if this object's text is underlined."},
    }

    methods = {
        "animate_font_size": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                      "end_size": {"type": "string",
                                                   "info": "the final font_size at the end of the animation"},
                                      "on_finished": {"type": "function",
                                                     "info": "an optional function to run when the animation finishes."},
                                      "*args": {"type": "any", "info": "0 or more arguments and/or keyword arguments to pass into <b>on_finished</b>."}},
                             "return": None,
                             "info": "Visually animates changing this object's <b>font_size</b> to <b>end_size</b>, "
                                     "over <b>duration</b> seconds.  When the animation completes, runs the "
                                     "<b>on_finished</b> function, if one was passed in."},
        "animate_text_color": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                      "end_color": {"type": "string",
                                                   "info": "the final text_color at the end of the animation"},
                                      "on_finished": {"type": "function",
                                                     "info": "an optional function to run when the animation finishes."},
                                      "*args": {"type": "any", "info": "0 or more arguments and/or keyword arguments to pass into <b>on_finished</b>."}},
                             "return": None,
                             "info": "Visually animates fading this object's <b>text_color</b> to <b>end_color</b>, "
                                     "over <b>duration</b> seconds.  When the animation completes, runs the "
                                     "<b>on_finished</b> function, if one was passed in."},
    }

    handlers = {}


class HelpDataWebView():
    parent = HelpDataObject
    types = ["webview"]

    properties = {
        "URL": {"type": "string",
                "info": "This is the current URL being shown by the Web View.  Set this property to go to a web page."},
        "HTML": {"type": "string",
                "info": "This is the current HTML content of the webview."},
        "can_go_back": {"type": "bool",
                "info": "This is True if the webview has pages in its history to go back to, otherwise it is False. "
                        "This value can be read but not set."},
        "can_go_forward": {"type": "bool",
                "info": "This is True if the webview has gone back, and has history pages available to go forward to, "
                        "otherwise it is False.  This value can be read but not set."},
        "allowed_hosts": {"type": "list",
                 "info": "If the <b>allowed_hosts</b> list is empty, then this WebView will be allowed to load any URL. "
                         "If this list contains hostnames like 'google.com', then the WebView will only be allowed to "
                         "load URLs from these web hosts, and attempts to load other URLs, either by setting the "
                         "<b>URL</b> property directly, or by clicking a link, will fail."},
    }

    methods = {
        "run_java_script": {"args": {"code": {"type": "string", "info": "The JavaScript code to run in this Web View"}},
                            "return": "string",
                            "info": "Runs the given JavaScript <b>code</b> and returns any result."},
        "go_forward": {"args": {},
                      "return": None,
                      "info": "Make the WebView go forward through its history list."},
        "go_back": {"args": {},
                   "return": None,
                   "info": "Make the WebView go back through its history list."},
    }

    handlers = {
        "on_done_loading": {"args": {"URL": {"type": "string", "info": "This is the URL of the web page that just loaded."},
                                   "did_load": {"type": "bool", "info": "True if the URL loaded successfully, otherwise False."}},
                          "info": "The <b>on_done_loading</b> event is run whenever a web page finishes loading.",
                          },
        "on_card_stock_link": {
            "args": {"message": {"type": "string", "info": "This is the message part of a 'cardstock:message' URL."}},
            "info": "The <b>on_card_stock_link</b> event is run whenever a web page tries to load a URL of the form "
                    "cardstock:message.  You can add code in this event to respond to actions in a web page that call "
                    "a cardstock: URL.",
            },
    }


class HelpDataImage():
    parent = HelpDataObject
    types = ["image"]

    properties = {
        "file": {"type": "string",
                 "info": "The file path of the image file to display in this image object."},
        "fit": {"type": "[Center, Stretch, Contain, Fill]",
                "info": "This property controls how the image is resized to fit into the image object.  Center shows "
                        "the image full size, centered in the image object, and clipped at the image object border. "
                        "Stretch resizes and stretches the image to fit exactly into the image object. Contain sizes the "
                        "image to fit inside the image object, while keeping the original image aspect ratio. Fill "
                        "sizes the image to just barely fill the entire image object, while keeping the original image "
                        "aspect ratio."},
    }

    methods = {}

    handlers = {}


class HelpDataGroup():
    parent = HelpDataObject
    types = ["group"]

    properties = {}

    methods = {
        "ungroup":{"args": {},
                   "return": None,
                   "info": "Ungroups this group.  Removes the group object from the card, and adds all of its "
                           "children back onto the card as individual objects."},
        "stop_all_animating": {"args": {"property_name": {"type": "string",
                                       "info": "optional name of the property to stop animating, for "
                                               "example: \"size\" or \"position\".  If left blank, stops "
                                               "all animations of properties of this group and its children."}},
                              "return": None,
                              "info": "Stops the animation specified by <b>property_name</b> from running on this group "
                                      "and on all objects in this group, or if no <b>property_name</b> is specified, "
                                      "stops all running animations on this group and on all objects in this group.  "
                                      "Any animated properties are left at their current, mid-animation values."},
    }

    handlers = {}


class HelpDataLine():
    parent = HelpDataObject
    types = ["line", "pen"]

    properties = {
        "pen_thickness": {"type": "int",
                         "info": "The thickness of the line or shape border in pixels."},
        "pen_color": {"type": "string",
                     "info": "The color used for the line or shape border.  This can be a color word like red, or an "
                             "HTML color like #FF0000 for pure red."},
        "points":   {"type": "list",
                     "info": "This is the list of points that define this line, pen, or polygon object.  The other "
                             "shape types do not provide access to this list."},
    }

    methods = {
        "animate_pen_thickness": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                 "end_thickness": {"type": "int",
                                                 "info": "the final pen_thickness at the end of the animation"},
                                 "on_finished": {"type": "function",
                                                "info": "an optional function to run when the animation finishes."},
                                         "*args": {"type": "any", "info": "0 or more arguments and/or keyword arguments to pass into <b>on_finished</b>."}},
                        "return": None,
                        "info": "Visually animates changing this object's <b>pen_thickness</b> to <b>end_thickness</b>, "
                                "over <b>duration</b> seconds.  When the animation completes, runs the "
                                "<b>on_finished</b> function, if one was passed in."},

        "animate_pen_color": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                 "end_color": {"type": "string",
                                                 "info": "the final pen color at the end of the animation"},
                                 "on_finished": {"type": "function",
                                                "info": "an optional function to run when the animation finishes."},
                                     "*args": {"type": "any", "info": "0 or more arguments and/or keyword arguments to pass into <b>on_finished</b>."}},
                        "return": None,
                        "info": "Visually animates fading this object's <b>pen_color</b> to <b>end_color</b>, "
                                "over <b>duration</b> seconds.  When the animation completes, runs the "
                                "<b>on_finished</b> function, if one was passed in."},
    }

    handlers = {}


class HelpDataShape():
    parent = HelpDataLine
    types = ["oval", "rect", "polygon"]

    properties = {
        "fill_color": {"type": "string",
                      "info": "The color used to fill the inside area of the shape.  This can be a color word like "
                              "red, or an HTML color like #FF0000 for pure red."},
    }

    methods = {
        "animate_fill_color": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                     "end_color": {"type": "string",
                                                  "info": "the final fill_color at the end of the animation"},
                                     "on_finished": {"type": "function",
                                                    "info": "an optional function to run when the animation finishes."},
                                      "*args": {"type": "any", "info": "0 or more arguments and/or keyword arguments to pass into <b>on_finished</b>."}},
                            "return": None,
                            "info": "Visually animates fading this object's <b>fill_color</b> to <b>end_color</b>, "
                                    "over <b>duration</b> seconds.  When the animation completes, runs the "
                                    "<b>on_finished</b> function, if one was passed in."},
    }

    handlers = {}


class HelpDataRoundRectangle():
    parent = HelpDataShape
    types = ["roundrect"]

    properties = {
        "corner_radius": {"type": "int",
                         "info": "The radius used to draw this round rectangle's rounded corners."},
    }

    methods = {
        "animate_corner_radius": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                         "end_corner_radius": {"type": "int",
                                                          "info": "the final corner_radius at the end of the animation"},
                                         "on_finished": {"type": "function",
                                                        "info": "an optional function to run when the animation finishes."},
                                         "*args": {"type": "any", "info": "0 or more arguments and/or keyword arguments to pass into <b>on_finished</b>."}},
                                "return": None,
                                "info": "Visually animates changing this round rectangle's <b>corner_radius</b> to <b>end_corner_radius</b>, "
                                        "over <b>duration</b> seconds.  When the animation completes, runs the <b>on_finished</b> function, "
                                        "if one was passed in."},
    }

    handlers = {}


class HelpDataCard():
    parent = HelpDataObject
    types = ["card"]

    properties = {
        "fill_color": {"type": "string",
                    "info": "The fill_color is used to fill in the background of this card.  This can be a color word like white, "
                            "or an HTML color like #EEEEEE for a light grey."},
        "number": {"type": "int",
                  "info": "This is the card number of this card.  The first card is <b>number</b> 1.  You can "
                          "read this value, but not set it."},
        "can_save": {"type": "bool",
                    "info": "If <b>can_save</b> is <b>True</b>, the user can save the stack while running it. "
                            "If it's <b>False</b>, the user can't save, so the stack will always start out in the same "
                            "state."},
        "can_resize": {"type": "bool",
                      "info": "If <b>can_resize</b> is <b>True</b>, the user can resize the stack window while running it. "
                              "If it's <b>False</b>, the user can't resize the window while the stack runs."},
    }

    methods = {
        "add_button": {"args": {"name": {"type": "string", "info": "an optional argument giving the name to use for this "
                                                                "new Button object.  If omitted, the name will be "
                                                                "'button_{N}'."},
                               "...": {"type": "Any", "info": "optionally set more properties here.  For example, "
                                                              "include position=(10,10)"}},
                    "return": "button",
                    "info": "Adds a new Button to the card, and returns the new object."},
        "add_text_field": {"args": {"name": {"type": "string", "info": "an optional argument giving the name to use for this "
                                                                "new Text Field object.  If omitted, the name will be "
                                                                "'field_{N}'."},
                                  "...": {"type": "Any", "info": "optionally set more properties here.  For example, "
                                                                 "include position=(10,10)"}},
                    "return": "textfield",
                    "info": "Adds a new Text Field to the card, and returns the new object."},
        "add_text_label": {"args": {"name": {"type": "string", "info": "an optional argument giving the name to use for this "
                                                                "new Text Label object.  If omitted, the name will be "
                                                                "'label_{N}'."},
                                  "...": {"type": "Any", "info": "optionally set more properties here.  For example, "
                                                                 "include position=(10,10)"}},
                         "return": "textlabel",
                    "info": "Adds a new Text Label object to the card, and returns the new object."},
        "add_image": {"args": {"name": {"type": "string", "info": "an optional argument giving the name to use for this "
                                                                "new Image object.  If omitted, the name will be "
                                                                "'image_{N}'."},
                              "...": {"type": "Any", "info": "optionally set more properties here.  For example, "
                                                             "include position=(10,10)"}},
                     "return": "image",
                     "info": "Adds a new Image to the card, and returns the new object."},
        "add_oval": {"args": {"name": {"type": "string", "info": "an optional argument giving the name to use for this "
                                                                "new Oval object.  If omitted, the name will be "
                                                                "'shape_{N}'."},
                             "...": {"type": "Any", "info": "optionally set more properties here.  For example, "
                                                            "include position=(10,10)"}},
                    "return": "oval",
                    "info": "Adds a new Image to the card, and returns the new object."},
        "add_rectangle": {"args": {"name": {"type": "string", "info": "an optional argument giving the name to use for this "
                                                                "new Rectangle object.  If omitted, the name will be "
                                                                "'shape_{N}'."},
                                  "...": {"type": "Any", "info": "optionally set more properties here.  For example, "
                                                                 "include position=(10,10)"}},
                         "return": "rect",
                    "info": "Adds a new Rectangle to the card, and returns the new object."},
        "add_round_rectangle": {"args": {"name": {"type": "string", "info": "an optional argument giving the name to use for this "
                                                                "new Round Rectangle object.  If omitted, the name will be "
                                                                "'shape_{N}'."},
                                       "...": {"type": "Any", "info": "optionally set more properties here.  For example, "
                                                       "include position=(10,10)"}},
                              "return": "roundrect",
                    "info": "Adds a new Round Rectangle to the card, and returns the new object."},
        "add_line": {"args": {"points": {"type": "list", "info": "a list of points, that are the locations of each "
                                                                "vertex along the line, relative to the bottom-left "
                                                                "corner of the card.  It can hold just two points "
                                                                "to create a simple line segment, or more to create a "
                                                                "more complex multi-segment line."},
                             "name": {"type": "string", "info": "an optional argument giving the name to use for this "
                                                                "new Line object.  If omitted, the name will be "
                                                                "'shape_{N}'."},
                             "...": {"type": "Any", "info": "optionally set more properties here.  For example, "
                                                            "include position=(10,10)"}},
                    "return": "line",
                    "info": "Adds a new Line to the card, and returns the new object."},
        "add_polygon": {"args": {"points": {"type": "list", "info": "a list of points, that are the locations of each "
                                                                   "vertex along the outline of the polygon, relative "
                                                                   "to the bottom-left corner of the card.  It must hold "
                                                                   "three or more points to display properly as a "
                                                                   "polygon."},
                             "name": {"type": "string", "info": "an optional argument giving the name to use for this "
                                                                "new Line object.  If omitted, the name will be "
                                                                "'shape_{N}'."},
                                "...": {"type": "Any", "info": "optionally set more properties here.  For example, "
                                                               "include position=(10,10)"}},
                       "return": "polygon",
                    "info": "Adds a new Polygon shape to the card, and returns the new object."},
        "add_group": {"args": {"objects": {"type": "list", "info": "a list of object, all on the same card, to include "
                                                                  "in the new group object."},
                             "name": {"type": "string", "info": "an optional argument giving the name to use for this "
                                                                "new Group object.  If omitted, the name will be "
                                                                "'group_{N}'."}
                             },
                    "return": "group",
                    "info": "Adds a new Group to the card, and returns the new object."},
        "animate_fill_color": {"args": {"duration": {"type": "float", "info": "time in seconds for the animation to run"},
                                      "end_color": {"type": "string",
                                                   "info": "the final fill_color at the end of the animation"},
                                      "on_finished": {"type": "function",
                                                     "info": "an optional function to run when the animation finishes."}},
                             "return": None,
                             "info": "Visually animates this card's <b>fill_color</b> to <b>end_color</b>, "
                                     "over <b>duration</b> seconds.  When the animation completes, runs the <b>on_finished</b> function, "
                                     "if one was passed in."},
        "stop_all_animating": {"args": {"property_name": {"type": "string",
                                       "info": "optional name of the property to stop animating, for "
                                               "example: \"size\" or \"position\".  If left blank, stops "
                                              "animations of all properties of this card and its children."}},
                              "return": None,
                              "info": "Stops the animation specified by <b>property_name</b> from running on this card "
                                      "and on all objects on this card, or if no <b>property_name</b> is specified, "
                                      "stops all running animations on this card and on all objects on this card.  "
                                      "Any animated properties are left at their current, mid-animation values."},
    }

    handlers = {
        "on_show_card": {"args": {},
                       "info": "The <b>on_show_card</b> event is run any time a card is shown, including when the "
                               "first card is initially shown when the stack starts running."},
        "on_hide_card": {"args": {},
                       "info": "The <b>on_hide_card</b> event is run when a card is hidden, right before the new "
                               "card's on_show_card event is run, when going to another card."},
        "on_exit_stack": {"args": {},
                        "info": "The <b>on_exit_stack</b> event is run for all cards when the stack exits, whether "
                                "from the File Close menu item, the quit() function, the stack.return_from_stack() method,"
                                "or closing the stack viewer window.  You can use this to clean up any external "
                                "resources -- for example, closing files.  This event needs to run quickly, so it's "
                                "not able to call functions like alert(), ask_text(), ask_yes_no(), run_stack(), etc."},
        "on_resize": {"args": {"is_initial": {"type": "bool", "info": "True if this event is running due to showing the "
                                                                      "card.  False if this event is running due to the "
                                                                      "card being resized."}},
                     "info": "The <b>on_resize</b> event is run on the currently visible card when the stack window is "
                             "resized.  It is also run each time a card is shown, to give the card a chance to set up "
                             "its initial layout for the current size.  Your code can distinguish between these two "
                             "cases by checking the value of <b>is_initial</b>."},
        "on_key_press": {"args": {"key_name": {"type": "string", "info": "The name of the pressed key"}},
                      "info": "The <b>on_key_press</b> event is run any time a keyboard key is pressed down.  Regular "
                              "keys are named as capital letters and digits, like 'A' or '1', and other keys have "
                              "keyNames like 'Shift', 'Return', 'Escape', 'Left', and 'Right'."},
        "on_key_hold": {"args": {"key_name": {"type": "string", "info": "The name of the key that is still being held down"},
                               "elapsed_time": {"type": "float", "info": "This is the number of seconds since the key "
                                                                        "press started, or since the last time this "
                                                                        "event was run, normally about 0.03."}},
                      "info": "The <b>on_key_hold</b> event is run repeatedly, while any keyboard key is pressed down.  "
                              "Regular keys are named as capital letters and digits, like 'A' or '1', and other keys "
                              "have keyNames like 'Shift', 'Return', 'Escape', 'Left', and 'Right'."},
        "on_key_release": {"args": {"key_name": {"type": "string", "info": "The name of the released key"}},
                    "info": "The <b>on_key_release</b> event is run any time a pressed keyboard key is released.  Regular "
                            "keys are named as capital letters and digits, like 'A' or '1', and other keys have "
                            "keyNames like 'Shift', 'Return', 'Escape', 'Left', and 'Right'."},
    }


class HelpDataStack():
    parent = HelpDataObject
    types = ["stack"]

    properties = {
        "num_cards": {"type": "int",
                     "info": "This is the number of cards in this stack.  You can "
                             "read this value, but not set it."},
        "current_card": {"type": "object",
                        "info": "This is the card object that is currently visible.  stack.<b>current_card</b>.number will "
                                "give you the number of the current card."},
    }

    methods = {
        "add_card": {"args": {"name": {"type": "string", "info": "an optional argument giving the name to use for this "
                                                                "new card object.  If omitted, the name will be "
                                                                "'card_{N}'."},
                             "atNumber": {"type": "int", "info": "an optional argument giving the card number in "
                                                                "the stack where the card should be added.  Number 1 is "
                                                                "at the beginning.  If omitted, the card will be added "
                                                                "at the end of the stack."},
                             },
                            "return": "card",
                            "info": "Adds a new empty card to the stack, and returns the card object."},
        "card_with_number": {"args": {"number": {"type": "int",
                                    "info": "the card number of the card to get."}},
                           "return": "card",
                           "info": "Returns the card at card <b>number</b>.  The first card is <b>number</b> 1."},
        "return_from_stack": {"args": {"returnValue": {"type": "any",
                                            "info": "An optional value to pass back to the previous stack, that we are returning to."}},
                            "return": None,
                            "info": "If this stack was started from within another stack, by calling <b>run_stack()</b>, this "
                                    "function will immediately stop the current event without returning, exit this stack, and return to the "
                                    "previous stack. If you include a <b>returnValue</b>, this value will "
                                    "be returned by the calling stack's <b>run_stack()</b> call, which will now finally return. "
                                    "If the current stack was not started by a <b>run_stack()</b> call, this function does "
                                    "nothing, and returns normally."},
        "get_setup_value": {"args": {}, "return": None,
                               "info": "If this stack was started by another stack calling run_stack() with a setupValue argument, "
                                       "you can call this <b>get_setup_value()</b> method "
                                       "to get the setupValue that was passed in from the calling stack.  Otherwise this "
                                       "will return None."},
    }

    handlers = {}


class HelpDataString():
    """ Just method names and return types, for better autocomplete handling """
    parent = None
    types = ["string"]
    properties = {}

    methods = {
        "capitalize": {"args": {},
                    "return": "string",
                    "info": ""},
        "casefold": {"args": {},
                       "return": "string",
                       "info": ""},
        "count": {"args": {},
                       "return": "int",
                       "info": ""},
        "encode": {"args": {},
                       "return": "string",
                       "info": ""},
        "endswith": {"args": {},
                   "return": "bool",
                   "info": ""},
        "expandtabs": {"args": {},
                   "return": "string",
                   "info": ""},
        "find": {"args": {},
                   "return": "int",
                   "info": ""},
        "format": {"args": {},
                   "return": "string",
                   "info": ""},
        "format_map": {"args": {},
                   "return": "string",
                   "info": ""},
        "index": {"args": {},
                   "return": "int",
                   "info": ""},
        "isalnum": {"args": {},
                  "return": "bool",
                  "info": ""},
        "isalpha": {"args": {},
                  "return": "bool",
                  "info": ""},
        "isascii": {"args": {},
                  "return": "bool",
                  "info": ""},
        "isdecimat": {"args": {},
                  "return": "bool",
                  "info": ""},
        "isidentifier": {"args": {},
                  "return": "bool",
                  "info": ""},
        "islower": {"args": {},
                    "return": "bool",
                    "info": ""},
        "isnumeric": {"args": {},
                    "return": "bool",
                    "info": ""},
        "isprintable": {"args": {},
                    "return": "bool",
                    "info": ""},
        "isspace": {"args": {},
                    "return": "bool",
                    "info": ""},
        "istitle": {"args": {},
                    "return": "bool",
                    "info": ""},
        "isupper": {"args": {},
                    "return": "bool",
                    "info": ""},
        "join": {"args": {},
                    "return": "string",
                    "info": ""},
        "ljust": {"args": {},
                    "return": "string",
                    "info": ""},
        "lower": {"args": {},
                  "return": "string",
                  "info": ""},
        "lstrip": {"args": {},
                  "return": "string",
                  "info": ""},
        "maketrans": {"args": {},
                  "return": "other",
                  "info": ""},
        "partition": {"args": {},
                  "return": "other",
                  "info": ""},
        "replace": {"args": {},
                  "return": "string",
                  "info": ""},
        "rfind": {"args": {},
                  "return": "int",
                  "info": ""},
        "rindex": {"args": {},
                  "return": "int",
                  "info": ""},
        "rjust": {"args": {},
                  "return": "string",
                  "info": ""},
        "rpartition": {"args": {},
                  "return": "other",
                  "info": ""},
        "rsplit": {"args": {},
                  "return": "list",
                  "info": ""},
        "rstrip": {"args": {},
                  "return": "string",
                  "info": ""},
        "split": {"args": {},
                  "return": "list",
                  "info": ""},
        "splitlines": {"args": {},
                  "return": "list",
                  "info": ""},
        "startswith": {"args": {},
                  "return": "bool",
                  "info": ""},
        "strip": {"args": {},
                       "return": "string",
                       "info": ""},
        "swapcase": {"args": {},
                       "return": "string",
                       "info": ""},
        "title": {"args": {},
                       "return": "string",
                       "info": ""},
        "translate": {"args": {},
                       "return": "string",
                       "info": ""},
        "upper": {"args": {},
                       "return": "string",
                       "info": ""},
        "zfill": {"args": {},
                  "return": "string",
                  "info": ""},
    }


class HelpDataList():
    """ Just method names and return types, for better autocomplete handling """
    parent = None
    types = ["list"]
    properties = {}

    methods = {
        "append": {"args": {},
                    "return": None,
                    "info": ""},
        "clear": {"args": {},
                   "return": None,
                   "info": ""},
        "copy": {"args": {},
                   "return": "list",
                   "info": ""},
        "count": {"args": {},
                   "return": "int",
                   "info": ""},
        "extend": {"args": {},
                   "return": None,
                   "info": ""},
        "index": {"args": {},
                   "return": "int",
                   "info": ""},
        "insert": {"args": {},
                   "return": None,
                   "info": ""},
        "pop": {"args": {},
                   "return": "any",
                   "info": ""},
        "remove": {"args": {},
                   "return": None,
                   "info": ""},
        "reverse": {"args": {},
                   "return": None,
                   "info": ""},
        "sort": {"args": {},
                   "return": None,
                   "info": ""},
    }


class HelpDataBuiltins():
    """ Just function names and return types, for better autocomplete handling """
    parent = None
    types = []
    properties = {}

    functions = {
        "abs": {"args": {},
                    "return": "int",
                    "info": ""},
        "str": {"args": {},
                   "return": "string",
                   "info": ""},
        "bool": {"args": {},
                   "return": "bool",
                   "info": ""},
        "list": {"args": {},
                   "return": "list",
                   "info": ""},
        "int": {"args": {},
                   "return": "int",
                   "info": ""},
        "float": {"args": {},
                   "return": "float",
                   "info": ""},
        "dict": {"args": {},
                   "return": "dict",
                   "info": ""},
        "tuple": {"args": {},
                   "return": "other",
                   "info": ""},
        "len": {"args": {},
                   "return": "int",
                   "info": ""},
        "min": {"args": {},
                   "return": "int",
                   "info": ""},
        "max": {"args": {},
                   "return": "int",
                   "info": ""},
        "print": {"args": {},
                "return": None,
                "info": ""},
        "range": {"args": {},
                "return": "other",
                "info": ""},
        "sorted": {"args": {},
                "return": "list",
                "info": ""},
        "filter": {"args": {},
                "return": "other",
                "info": ""},
        "format": {"args": {},
                "return": "string",
                "info": ""},
        "hex": {"args": {},
                "return": "string",
                "info": ""},
        "oct": {"args": {},
                "return": "string",
                "info": ""},
        "map": {"args": {},
                "return": "other",
                "info": ""},
        "ord": {"args": {},
                "return": "string",
                "info": ""},
        "open": {"args": {},
                "return": "other",
                "info": ""},
        "pow": {"args": {},
                "return": "int",
                "info": ""},
        "reversed": {"args": {},
                "return": "other",
                "info": ""},
        "round": {"args": {},
                "return": "float",
                "info": ""},
        "sum": {"args": {},
                "return": "float",
                "info": ""},
        "zip": {"args": {},
                "return": "other",
                "info": ""},
    }


helpClasses = [HelpDataObject, HelpDataCard, HelpDataStack, HelpDataButton, HelpDataTextLabel, HelpDataTextField,
               HelpDataWebView, HelpDataImage, HelpDataGroup, HelpDataLine, HelpDataShape, HelpDataRoundRectangle,
               HelpDataString, HelpDataList]
