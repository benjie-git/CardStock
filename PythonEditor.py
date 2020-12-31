import wx
import wx.stc as stc
import keyword


if wx.Platform == '__WXMSW__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Courier New',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 12,
              'size2': 10,
             }
elif wx.Platform == '__WXMAC__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Monaco',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 14,
              'size2': 12,
             }
else:
    faces = { 'times': 'Times',
              'mono' : 'Courier',
              'helv' : 'Helvetica',
              'other': 'new century schoolbook',
              'size' : 14,
              'size2': 12,
             }


def CreatePythonEditor(parent):
    editor = stc.StyledTextCtrl(id=-1, parent=parent, style=wx.VSCROLL | wx.HSCROLL)

    # editor.SetAutoLayout(True)
    # editor.SetConstraints(LayoutAnchors(editor, True, True, True, True))

    editor.SetTabWidth(2)
    editor.SetUseTabs(0)
    editor.SetTabIndents(True)
    editor.SetBackSpaceUnIndents(True)
    #editor.SetIndentationGuides(True)
    editor.SetUseAntiAliasing(True)
    editor.SetMarginWidth(1, 0)

    # editor.SetStyleBits(7)
    editor.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(mono)s,size:%(size)d" % faces)
    # editor.StyleClearAll()  # Reset all to be like the default

    editor.SetLexer(stc.STC_LEX_PYTHON)
    editor.SetKeyWords(0, " ".join(keyword.kwlist))

    editor.Bind(wx.EVT_KEY_DOWN, PyEditorOnKeyPress)
    editor.Bind(stc.EVT_STC_UPDATEUI, PyEditorOnUpdateUI)

    editor.SetText("def a:\n  if 1:\n    print(1)\n  else:\n    print(0)\n")

    return editor


def PyEditorOnKeyPress(event):
    editor = event.GetEventObject()
    if event.GetKeyCode() == stc.STC_KEY_RETURN:
        numSpaces = editor.GetLineIndentation(editor.GetCurrentLine())
        line = editor.GetLine(editor.GetCurrentLine())
        if line.strip()[-1:] == ":":
            numSpaces += 2
        editor.AddText("\n" + " "*numSpaces)
    else:
        event.Skip()


def PyEditorOnUpdateUI(event):
    editor = event.GetEventObject()

    # check for matching braces
    braceAtCaret = -1
    braceOpposite = -1
    charBefore = None
    caretPos = editor.GetCurrentPos()

    if caretPos > 0:
        charBefore = editor.GetCharAt(caretPos - 1)
        styleBefore = editor.GetStyleAt(caretPos - 1)

    # check before
    if charBefore and chr(charBefore) in "[]{}()" and styleBefore == stc.STC_P_OPERATOR:
        braceAtCaret = caretPos - 1

    # check after
    if braceAtCaret < 0:
        charAfter = editor.GetCharAt(caretPos)
        styleAfter = editor.GetStyleAt(caretPos)

        if charAfter and chr(charAfter) in "[]{}()" and styleAfter == stc.STC_P_OPERATOR:
            braceAtCaret = caretPos

    if braceAtCaret >= 0:
        braceOpposite = editor.BraceMatch(braceAtCaret)

    if braceAtCaret != -1  and braceOpposite == -1:
        editor.BraceBadLight(braceAtCaret)
    else:
        editor.BraceHighlight(braceAtCaret, braceOpposite)
        pt = editor.PointFromPosition(braceOpposite)
        editor.Refresh(True, wx.Rect(pt.x, pt.y, 5,5))
        #print(pt)
        editor.Refresh(False)
