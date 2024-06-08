# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Allow migrating older file formats to newer ones

import re

def MigrateDataFromFormatVersion(fromVer, dataDict):
    # Migration code to run on json before loading it into models

    if fromVer < 3:
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

    if fromVer < 5:
        """
        In File Format Version 5, naming changed from camelCase to snake_case
        """
        # Update names
        def replaceNames(dataDict):
            if 'isVisible' in dataDict['properties']: dataDict['properties']['is_visible'] = dataDict['properties'].pop(
                'isVisible')
            if 'hasFocus' in dataDict['properties']: dataDict['properties']['has_focus'] = dataDict['properties'].pop(
                'hasFocus')
            if 'fillColor' in dataDict['properties']: dataDict['properties']['fill_color'] = dataDict['properties'].pop(
                'fillColor')
            if 'canSave' in dataDict['properties']: dataDict['properties']['can_save'] = dataDict['properties'].pop(
                'canSave')
            if 'canResize' in dataDict['properties']: dataDict['properties']['can_resize'] = dataDict['properties'].pop(
                'canResize')
            if 'numCards' in dataDict['properties']: dataDict['properties']['num_cards'] = dataDict['properties'].pop(
                'numCards')
            if 'currentCard' in dataDict['properties']: dataDict['properties']['current_card'] = dataDict[
                'properties'].pop('currentCard')
            if 'hasBorder' in dataDict['properties']: dataDict['properties']['has_border'] = dataDict['properties'].pop(
                'hasBorder')
            if 'canAutoShrink' in dataDict['properties']: dataDict['properties']['can_auto_shrink'] = dataDict[
                'properties'].pop('canAutoShrink')
            if 'textColor' in dataDict['properties']: dataDict['properties']['text_color'] = dataDict['properties'].pop(
                'textColor')
            if 'fontSize' in dataDict['properties']: dataDict['properties']['font_size'] = dataDict['properties'].pop(
                'fontSize')
            if 'isBold' in dataDict['properties']: dataDict['properties']['is_bold'] = dataDict['properties'].pop(
                'isBold')
            if 'isItalic' in dataDict['properties']: dataDict['properties']['is_italic'] = dataDict['properties'].pop(
                'isItalic')
            if 'isUnderlined' in dataDict['properties']: dataDict['properties']['is_underlined'] = dataDict[
                'properties'].pop('isUnderlined')
            if 'selectedText' in dataDict['properties']: dataDict['properties']['selected_text'] = dataDict[
                'properties'].pop('selectedText')
            if 'isEditable' in dataDict['properties']: dataDict['properties']['is_editable'] = dataDict[
                'properties'].pop('isEditable')
            if 'isMultiline' in dataDict['properties']: dataDict['properties']['is_multiline'] = dataDict[
                'properties'].pop('isMultiline')
            if 'canGoBack' in dataDict['properties']: dataDict['properties']['can_go_back'] = dataDict[
                'properties'].pop('canGoBack')
            if 'canGoForward' in dataDict['properties']: dataDict['properties']['can_go_forward'] = dataDict[
                'properties'].pop('canGoForward')
            if 'allowedHosts' in dataDict['properties']: dataDict['properties']['allowed_hosts'] = dataDict[
                'properties'].pop('allowedHosts')
            if 'penThickness' in dataDict['properties']: dataDict['properties']['pen_thickness'] = dataDict[
                'properties'].pop('penThickness')
            if 'penColor' in dataDict['properties']: dataDict['properties']['pen_color'] = dataDict['properties'].pop(
                'penColor')
            if 'fillColor' in dataDict['properties']: dataDict['properties']['fill_color'] = dataDict['properties'].pop(
                'fillColor')
            if 'cornerRadius' in dataDict['properties']: dataDict['properties']['corner_radius'] = dataDict[
                'properties'].pop('cornerRadius')
            if 'childModels' in dataDict:
                for child in dataDict['childModels']:
                    replaceNames(child)

        replaceNames(dataDict)
        for c in dataDict['cards']:
            replaceNames(c)

    if fromVer < 6:
        """
        In File Format Version 6, button.has_border changed to button.style
        """
        def replaceNames(dataDict):
            if "has_border" in dataDict['properties']:
                dataDict['properties']["style"] = ("Border" if dataDict['properties'].pop("has_border") else "Borderless")
            if 'childModels' in dataDict:
                for child in dataDict['childModels']:
                    replaceNames(child)
        for c in dataDict['cards']:
            replaceNames(c)

    if fromVer < 9:
        """
        In File Format Version 9, button.title changed to button.text
        """
        def replaceNames(d):
            if "title" in d['properties']:
                d['properties']["text"] = d['properties'].pop("title")
            if 'childModels' in d:
                for child in d['childModels']:
                    replaceNames(child)
        for c in dataDict['cards']:
            c['properties']['size'] = dataDict['properties']['size']
            c['properties']['can_resize'] = dataDict['properties']['can_resize']
            replaceNames(c)
        dataDict['properties'].pop('size')
        dataDict['properties'].pop('can_resize')


def MigrateModelFromFormatVersion(fromVer, stackModel):
    # Migration code to run after loading the json into models

    if fromVer < 2:
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

    if fromVer < 3:
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

    if fromVer < 4:
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
                    val = re.sub(r"\bColor\(", "ColorRGB(", val)
                    val = val.replace("IsMouseDown(", "IsMousePressed(")
                    obj.handlers[k] = val
            for child in obj.childModels:
                replaceNames(child)
        replaceNames(stackModel)

    if fromVer < 5:
        """
        In File Format Version 5, naming changed from camelCase to snake_case
        """
        # Update names of StopAnimating methods, OnIdle->OnPeriodic
        def replaceNames(obj):
            if "OnSetup"        in obj.handlers: obj.handlers["on_setup"] = obj.handlers.pop("OnSetup")
            if "OnShowCard"     in obj.handlers: obj.handlers["on_show_card"] = obj.handlers.pop("OnShowCard")
            if "OnHideCard"     in obj.handlers: obj.handlers["on_hide_card"] = obj.handlers.pop("OnHideCard")
            if "OnClick"        in obj.handlers: obj.handlers["on_click"] = obj.handlers.pop("OnClick")
            if "OnTextEnter"    in obj.handlers: obj.handlers["on_text_enter"] = obj.handlers.pop("OnTextEnter")
            if "OnTextChanged"  in obj.handlers: obj.handlers["on_text_changed"] = obj.handlers.pop("OnTextChanged")
            if "OnMousePress"   in obj.handlers: obj.handlers["on_mouse_press"] = obj.handlers.pop("OnMousePress")
            if "OnMouseMove"    in obj.handlers: obj.handlers["on_mouse_move"] = obj.handlers.pop("OnMouseMove")
            if "OnMouseRelease" in obj.handlers: obj.handlers["on_mouse_release"] = obj.handlers.pop("OnMouseRelease")
            if "OnMouseEnter"   in obj.handlers: obj.handlers["on_mouse_enter"] = obj.handlers.pop("OnMouseEnter")
            if "OnMouseExit"    in obj.handlers: obj.handlers["on_mouse_exit"] = obj.handlers.pop("OnMouseExit")
            if "OnDoneLoading"  in obj.handlers: obj.handlers["on_done_loading"] = obj.handlers.pop("OnDoneLoading")
            if "OnCardStockLink" in obj.handlers:obj.handlers["on_card_stock_link"] = obj.handlers.pop("OnCardStockLink")
            if "OnBounce"       in obj.handlers: obj.handlers["on_bounce"] = obj.handlers.pop("OnBounce")
            if "OnMessage"      in obj.handlers: obj.handlers["on_message"] = obj.handlers.pop("OnMessage")
            if "OnKeyPress"     in obj.handlers: obj.handlers["on_key_press"] = obj.handlers.pop("OnKeyPress")
            if "OnKeyHold"      in obj.handlers: obj.handlers["on_key_hold"] = obj.handlers.pop("OnKeyHold")
            if "OnKeyRelease"   in obj.handlers: obj.handlers["on_key_release"] = obj.handlers.pop("OnKeyRelease")
            if "OnResize"       in obj.handlers: obj.handlers["on_resize"] = obj.handlers.pop("OnResize")
            if "OnPeriodic"     in obj.handlers: obj.handlers["on_periodic"] = obj.handlers.pop("OnPeriodic")
            if "OnExitStack"    in obj.handlers: obj.handlers["on_exit_stack"] = obj.handlers.pop("OnExitStack")

            for k ,v in obj.handlers.items():
                if len(v):
                    val = v
                    val = re.sub(r"\bOnSetup\b", "on_setup", val)
                    val = re.sub(r"\bOnShowCard\b", "on_show_card", val)
                    val = re.sub(r"\bOnHideCard\b", "on_hide_card", val)
                    val = re.sub(r"\bOnClick\b", "on_click", val)
                    val = re.sub(r"\bOnTextEnter\b", "on_text_enter", val)
                    val = re.sub(r"\bOnTextChanged\b", "on_text_changed", val)
                    val = re.sub(r"\bOnMousePress\b", "on_mouse_press", val)
                    val = re.sub(r"\bOnMouseMove\b", "on_mouse_move", val)
                    val = re.sub(r"\bOnMouseRelease\b", "on_mouse_release", val)
                    val = re.sub(r"\bOnMouseEnter\b", "on_mouse_enter", val)
                    val = re.sub(r"\bOnMouseExit\b", "on_mouse_exit", val)
                    val = re.sub(r"\bOnDoneLoading\b", "on_done_loading", val)
                    val = re.sub(r"\bOnCardStockLink\b", "on_card_stock_link", val)
                    val = re.sub(r"\bOnBounce\b", "on_bounce", val)
                    val = re.sub(r"\bOnMessage\b", "on_message", val)
                    val = re.sub(r"\bOnKeyPress\b", "on_key_press", val)
                    val = re.sub(r"\bOnKeyHold\b", "on_key_hold", val)
                    val = re.sub(r"\bOnKeyRelease\b", "on_key_release", val)
                    val = re.sub(r"\bOnResize\b", "on_resize", val)
                    val = re.sub(r"\bOnPeriodic\b", "on_periodic", val)
                    val = re.sub(r"\bOnExitStack\b", "on_exit_stack", val)
                    val = re.sub(r"\bmousePos\b", "mouse_pos", val)
                    val = re.sub(r"\bkeyName\b", "key_name", val)
                    val = re.sub(r"\belapsedTime\b", "elapsed_time", val)
                    val = re.sub(r"\botherObject\b", "other_object", val)
                    val = re.sub(r"\bdidLoad\b", "did_load", val)
                    val = re.sub(r"\bWait\b", "wait", val)
                    val = re.sub(r"\bRunAfterDelay\b", "run_after_delay", val)
                    val = re.sub(r"\bAlert\b", "alert", val)
                    val = re.sub(r"\bAskYesNo\b", "ask_yes_no", val)
                    val = re.sub(r"\bAskText\b", "ask_text", val)
                    val = re.sub(r"\bGotoCard\b", "goto_card", val)
                    val = re.sub(r"\bGotoNextCard\b", "goto_next_card", val)
                    val = re.sub(r"\bGotoPreviousCard\b", "goto_previous_card", val)
                    val = re.sub(r"\bRunStack\b", "run_stack", val)
                    val = re.sub(r"\bPlaySound\b", "play_sound", val)
                    val = re.sub(r"\bStopSound\b", "stop_sound", val)
                    val = re.sub(r"\bBroadcastMessage\b", "broadcast_message", val)
                    val = re.sub(r"\bIsKeyPressed\b", "is_key_pressed", val)
                    val = re.sub(r"\bIsMousePressed\b", "is_mouse_pressed", val)
                    val = re.sub(r"\bIsUsingTouchScreen\b", "is_using_touch_screen", val)
                    val = re.sub(r"\bGetMousePos\b", "get_mouse_pos", val)
                    val = re.sub(r"\bisVisible\b", "is_visible", val)
                    val = re.sub(r"\bhasFocus\b", "has_focus", val)
                    val = re.sub(r"\bfillColor\b", "fill_color", val)
                    val = re.sub(r"\bcanSave\b", "can_save", val)
                    val = re.sub(r"\bcanResize\b", "can_resize", val)
                    val = re.sub(r"\bnumCards\b", "num_cards", val)
                    val = re.sub(r"\bcurrentCard\b", "current_card", val)
                    val = re.sub(r"\bhasBorder\b", "has_border", val)
                    val = re.sub(r"\bcanAutoShrink\b", "can_auto_shrink", val)
                    val = re.sub(r"\btextColor\b", "text_color", val)
                    val = re.sub(r"\bfontSize\b", "font_size", val)
                    val = re.sub(r"\bisBold\b", "is_bold", val)
                    val = re.sub(r"\bisItalic\b", "is_italic", val)
                    val = re.sub(r"\bisUnderlined\b", "is_underlined", val)
                    val = re.sub(r"\bselectedText\b", "selected_text", val)
                    val = re.sub(r"\bisEditable\b", "is_editable", val)
                    val = re.sub(r"\bisMultiline\b", "is_multiline", val)
                    val = re.sub(r"\bcanGoBack\b", "can_go_back", val)
                    val = re.sub(r"\bcanGoForward\b", "can_go_forward", val)
                    val = re.sub(r"\ballowedHosts\b", "allowed_hosts", val)
                    val = re.sub(r"\bpenThickness\b", "pen_thickness", val)
                    val = re.sub(r"\bpenColor\b", "pen_color", val)
                    val = re.sub(r"\bfillColor\b", "fill_color", val)
                    val = re.sub(r"\bcornerRadius\b", "corner_radius", val)
                    val = re.sub(r"\bSendMessage\b", "send_message", val)
                    val = re.sub(r"\bFocus\b", "focus", val)
                    val = re.sub(r"\bChildWithBaseName\b", "child_with_base_name", val)
                    val = re.sub(r"\bFlipHorizontal\b", "flip_horizontal", val)
                    val = re.sub(r"\bFlipVertical\b", "flip_vertical", val)
                    val = re.sub(r"\bOrderToFront\b", "order_to_front", val)
                    val = re.sub(r"\bOrderForward\b", "order_forward", val)
                    val = re.sub(r"\bOrderBackward\b", "order_backward", val)
                    val = re.sub(r"\bOrderToBack\b", "order_to_back", val)
                    val = re.sub(r"\bOrderToIndex\b", "order_to_index", val)
                    val = re.sub(r"\bGetEventCode\b", "get_event_code", val)
                    val = re.sub(r"\bSetEventCode\b", "set_event_code", val)
                    val = re.sub(r"\bStopHandlingMouseEvent\b", "stop_handling_mouse_event", val)
                    val = re.sub(r"\bIsTouching\b", "is_touching", val)
                    val = re.sub(r"\bSetBounceObjects\b", "set_bounce_objects", val)
                    val = re.sub(r"\bIsTouchingPoint\b", "is_touching_point", val)
                    val = re.sub(r"\bIsTouchingEdge\b", "is_touching_edge", val)
                    val = re.sub(r"\bAnimatePosition\b", "animate_position", val)
                    val = re.sub(r"\bAnimateCenter\b", "animate_center", val)
                    val = re.sub(r"\bAnimateSize\b", "animate_size", val)
                    val = re.sub(r"\bAnimateRotation\b", "animate_rotation", val)
                    val = re.sub(r"\bStopAnimating\b", "stop_animating", val)
                    val = re.sub(r"\bAddButton\b", "add_button", val)
                    val = re.sub(r"\bAddTextField\b", "add_text_field", val)
                    val = re.sub(r"\bAddTextLabel\b", "add_text_label", val)
                    val = re.sub(r"\bAddImage\b", "add_image", val)
                    val = re.sub(r"\bAddOval\b", "add_oval", val)
                    val = re.sub(r"\bAddRectangle\b", "add_rectangle", val)
                    val = re.sub(r"\bAddRoundRectangle\b", "add_round_rectangle", val)
                    val = re.sub(r"\bAddLine\b", "add_line", val)
                    val = re.sub(r"\bAddPolygon\b", "add_polygon", val)
                    val = re.sub(r"\bAddGroup\b", "add_group", val)
                    val = re.sub(r"\bAnimateFillColor\b", "animate_fill_color", val)
                    val = re.sub(r"\bStopAllAnimating\b", "stop_all_animating", val)
                    val = re.sub(r"\bAddCard\b", "add_card", val)
                    val = re.sub(r"\bCardWithNumber\b", "card_with_number", val)
                    val = re.sub(r"\bReturnFromStack\b", "return_from_stack", val)
                    val = re.sub(r"\bGetSetupValue\b", "get_setup_value", val)
                    val = re.sub(r"\bAnimateTextColor\b", "animate_text_color", val)
                    val = re.sub(r"\bAnimateTextColor\b", "animate_text_color", val)
                    val = re.sub(r"\bSelectAll\b", "select_all", val)
                    val = re.sub(r"\bRunJavaScript\b", "run_java_script", val)
                    val = re.sub(r"\bGoForward\b", "go_forward", val)
                    val = re.sub(r"\bGoBack\b", "go_back", val)
                    val = re.sub(r"\bUngroup\b", "ungroup", val)
                    val = re.sub(r"\bStopAllAnimating\b", "stop_all_animating", val)
                    val = re.sub(r"\bAnimatePenThickness\b", "animate_pen_thickness", val)
                    val = re.sub(r"\bAnimatePenColor\b", "animate_pen_color", val)
                    val = re.sub(r"\bAnimateFillColor\b", "animate_fill_color", val)
                    val = re.sub(r"\bAnimateCornerRadius\b", "animate_corner_radius", val)
                    val = re.sub(r"\bTime\b", "time", val)
                    val = re.sub(r"\bPaste\b", "paste", val)
                    val = re.sub(r"\bQuit\b", "quit", val)
                    val = re.sub(r"\bDistance\b", "distance", val)
                    val = re.sub(r"\bCut\b", "cut", val)
                    val = re.sub(r"\bCopy\b", "copy", val)
                    val = re.sub(r"\bClone\b", "clone", val)
                    val = re.sub(r"\bDelete\b", "delete", val)
                    val = re.sub(r"\bShow\b", "show", val)
                    val = re.sub(r"\bHide\b", "hide", val)
                    val = re.sub(r"\bEnter\b", "enter", val)
                    val = re.sub(r"\bClick\b", "click", val)
                    obj.handlers[k] = val
            for child in obj.childModels:
                replaceNames(child)
        replaceNames(stackModel)

    if fromVer < 7:
        """
        In File Format Version 7, get and set event_code functions were renamed
        """
        # Update names of StopAnimating methods, OnIdle->OnPeriodic
        def replaceNames(obj):
            for k ,v in obj.handlers.items():
                if len(v):
                    val = v
                    val = val.replace(".get_event_code(", ".get_code_for_event(")
                    val = val.replace(".set_event_code(", ".set_code_for_event(")
                    obj.handlers[k] = val
            for child in obj.childModels:
                replaceNames(child)
        replaceNames(stackModel)

    if fromVer < 9:
        """
        In File Format Version 9, broadcast_message() changed from a global func to a method on stacks and cards
        """
        def replaceNames(obj):
            for k ,v in obj.handlers.items():
                if len(v):
                    val = v
                    val = re.sub(r"\bbroadcast_message\(", "card.broadcast_message(", val)
                    val = re.sub(r"\bColorRGB\(", "color_rgb(", val)
                    val = re.sub(r"\bColorHSB\(", "color_hsb(", val)
                    val = re.sub(r"\.title\b", ".text", val)
                    obj.handlers[k] = val
            for child in obj.childModels:
                replaceNames(child)
        replaceNames(stackModel)

    if fromVer < 10:
        """
        In File Format Version 10, we're moving from 3 to 4-space indentation
        """
        def replaceNames(obj):
            for k ,v in obj.handlers.items():
                if len(v):
                    val = v
                    val = re.sub(r" {3}(?= *$)", "    ", val[::-1], flags=re.MULTILINE)[::-1]
                    obj.handlers[k] = val
            for child in obj.childModels:
                replaceNames(child)
        replaceNames(stackModel)
