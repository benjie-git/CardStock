# Allow migrating older file formats to newer ones

def MigrateDataFromFormatVersion(fromVer, dataDict):
    # Migration code to run on json before loading it into models
    if fromVer <= 2:
        """
        In File Format Version 3, some properties and methods were renamed.
        """
        # Update names
        def replaceNames(dataDict):
            if dataDict['type'] == "poly":
                dataDict['type'] = "polygon"
            if "bgColor" in dataDict['properties']:
                dataDict['properties']["fillColor"] = dataDict['properties'].pop("bgColor")
            if "border" in dataDict['properties']:
                dataDict['properties']["hasBorder"] = dataDict['properties'].pop("border")
            if "editable" in dataDict['properties']:
                dataDict['properties']["isEditable"] = dataDict['properties'].pop("editable")
            if "multiline" in dataDict['properties']:
                dataDict['properties']["isMultiline"] = dataDict['properties'].pop("multiline")
            if "autoShrink" in dataDict['properties']:
                dataDict['properties']["canAutoShrink"] = dataDict['properties'].pop("autoShrink")
            if 'childModels' in dataDict:
                for child in dataDict['childModels']:
                    replaceNames(child)
        for c in dataDict['cards']:
            replaceNames(c)


def MigrateModelFromFormatVersion(fromVer, stackModel):
    # Migration code to run after loading the json into models
    if fromVer <= 1:
        """
        In File Format Version 1, the cards used the top-left corner as the origin, y increased while moving down.
        In File Format Version 2, the cards use the bottom-left corner as the origin, y increases while moving up.
        Migrate all of the static objects to look the same in the new world order, but user code will need updating.
        Also update names of the old StopAnimations() and StopAllAnimations() methods, and move OnIdle to OnPeriodic.
        """
        def UnflipImages(obj):
            if obj.type == "image":
                obj.PerformFlips(False, True)
            else:
                for c in obj.childModels:
                    UnflipImages(c)

        for card in stackModel.childModels:
            card.PerformFlips(False, True)
            UnflipImages(card)

        # Update names of StopAnimating methods, OnIdle->OnPeriodic
        def replaceNames(obj):
            if "OnIdle" in obj.handlers:
                obj.handlers["OnPeriodic"] = obj.handlers.pop("OnIdle")
            for k ,v in obj.handlers.items():
                val = v
                val = val.replace(".StopAnimations(", ".StopAnimating(")
                val = val.replace(".StopAllAnimations(", ".StopAllAnimating(")
                obj.handlers[k] = val
            for child in obj.childModels:
                replaceNames(child)
        replaceNames(stackModel)
    if fromVer <= 2:
        """
        In File Format Version 3, some properties and methods were renamed.
        """
        # Update names
        def replaceNames(obj):
            for k ,v in obj.handlers.items():
                if len(v):
                    val = v
                    val = val.replace(".bgColor", ".fillColor")
                    val = val.replace(".AnimateBgColor(", ".AnimateFillColor(")
                    val = val.replace(".border", ".hasBorder")
                    val = val.replace(".editable", ".isEditable")
                    val = val.replace(".multiline", ".isMultiline")
                    val = val.replace(".autoShrink", ".canAutoShrink")
                    val = val.replace(".visible", ".isVisible")
                    val = val.replace(".GetEventHandler(", ".GetEventCode(")
                    val = val.replace(".SetEventHandler(", ".SetEventCode(")
                    obj.handlers[k] = val
            for child in obj.childModels:
                replaceNames(child)
        replaceNames(stackModel)
    if fromVer <= 3:
        """
        In File Format Version 4, some properties and methods were renamed.
        """
        # Update names of StopAnimating methods, OnIdle->OnPeriodic
        def replaceNames(obj):
            if "OnMouseDown" in obj.handlers: obj.handlers["OnMousePress"]   = obj.handlers.pop("OnMouseDown")
            if "OnMouseUp"   in obj.handlers: obj.handlers["OnMouseRelease"] = obj.handlers.pop("OnMouseUp")
            if "OnKeyDown"   in obj.handlers: obj.handlers["OnKeyPress"]     = obj.handlers.pop("OnKeyDown")
            if "OnKeyUp"     in obj.handlers: obj.handlers["OnKeyRelease"]   = obj.handlers.pop("OnKeyUp")
            for k ,v in obj.handlers.items():
                if len(v):
                    val = v
                    val = val.replace("Color(", "ColorRGB(")
                    val = val.replace("IsMouseDown(", "IsMousePressed(")
                    obj.handlers[k] = val
            for child in obj.childModels:
                replaceNames(child)
        replaceNames(stackModel)
