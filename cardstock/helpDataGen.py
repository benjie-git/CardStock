# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import uiView
import keyword
from helpData import *

"""
This file includes descriptions of all CardStock objects, properties, methods, and event handlers for use in
context help, reference docs, and in the future, code completion.
"""


class HelpData():
    reservedNames = None

    @classmethod
    def ForObject(cls, obj):
        return cls.ForType(obj.type)

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
    def GetPropertyHelp(cls, model, key):
        data = cls.ForObject(model)
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
    def GetHandlerHelp(cls, model, key):
        data = cls.ForObject(model)
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


helpClasses = [HelpDataObject, HelpDataCard, HelpDataStack, HelpDataButton, HelpDataTextLabel, HelpDataTextField,
               HelpDataWebView, HelpDataImage, HelpDataGroup, HelpDataLine, HelpDataShape, HelpDataRoundRectangle,
               HelpDataString, HelpDataList]
