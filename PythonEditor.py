import wx
import wx.stc as stc
import keyword

TAB_WIDTH = 3

if wx.Platform == '__WXMSW__':
    faces = { 'mono' : 'Courier New',
              'helv' : 'Arial',
              'size' : 12,
              'size2': 10,
             }
elif wx.Platform == '__WXMAC__':
    faces = { 'mono' : 'Monaco',
              'helv' : 'Arial',
              'size' : 14,
              'size2': 12,
             }
else:
    faces = { 'mono' : 'Courier',
              'helv' : 'Helvetica',
              'size' : 14,
              'size2': 12,
             }


class PythonEditor(stc.StyledTextCtrl):
    def __init__(self, parent, **kwargs):
        super().__init__(id=wx.ID_ANY, parent=parent, **kwargs)

        self.SetAutoLayout(True)
        # self.SetConstraints(stc.LayoutAnchors(self, True, True, True, True))

        self.SetTabWidth(TAB_WIDTH)
        self.SetUseTabs(0)
        self.SetTabIndents(True)
        self.SetBackSpaceUnIndents(True)
        # self.SetIndentationGuides(True)
        self.SetUseAntiAliasing(True)
        self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 24)

        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,    'face:%(mono)s,fore:#000000,size:%(size)d' % faces)
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER, 'face:%(mono)s,fore:#999999,back:#EEEEEE' % faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, 'face:%(mono)s,fore:#000000,back:#DDDDFF,bold' % faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,   'face:%(mono)s,fore:#000000,back:#FFCCCC,bold' % faces)
        self.StyleSetSpec(stc.STC_P_DEFAULT,        'face:%(mono)s,fore:#000000,size:%(size)d' % faces)
        self.StyleSetSpec(stc.STC_P_NUMBER,         'face:%(mono)s,fore:#007F7F' % faces)
        self.StyleSetSpec(stc.STC_P_CHARACTER,      'face:%(mono)s,fore:#7F007F' % faces)
        self.StyleSetSpec(stc.STC_P_WORD,           'face:%(mono)s,fore:#1111EE' % faces)
        self.StyleSetSpec(stc.STC_P_CLASSNAME,      'face:%(mono)s,fore:#2222FF' % faces)
        self.StyleSetSpec(stc.STC_P_DEFNAME,        'face:%(mono)s,fore:#2222FF' % faces)
        self.StyleSetSpec(stc.STC_P_DECORATOR,      'face:%(mono)s,fore:#2222FF' % faces)
        self.StyleSetSpec(stc.STC_P_OPERATOR,       'face:%(mono)s,fore:#000044,bold' % faces)
        self.StyleSetSpec(stc.STC_P_IDENTIFIER,     'face:%(mono)s,fore:#000000' % faces)
        self.StyleSetSpec(stc.STC_P_STRING,         'face:%(mono)s,fore:#007F7F,bold' % faces)
        self.StyleSetSpec(stc.STC_P_STRINGEOL,      'face:%(mono)s,fore:#000000,back:#E0C0E0,eol' % faces)
        self.StyleSetSpec(stc.STC_P_COMMENTLINE,    'face:%(mono)s,fore:#888888' % faces)
        self.StyleSetSpec(stc.STC_P_COMMENTBLOCK,   'face:%(mono)s,fore:#999999' % faces)
        self.StyleSetSpec(stc.STC_P_TRIPLE,         'face:%(mono)s,fore:#999999' % faces)
        self.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE,   'face:%(mono)s,fore:#999999' % faces)

        self.SetLexer(stc.STC_LEX_PYTHON)
        self.SetKeyWords(0, " ".join(keyword.kwlist))

        self.Bind(wx.EVT_KEY_DOWN, self.PyEditorOnKeyPress)
        self.Bind(stc.EVT_STC_UPDATEUI, self.PyEditorOnUpdateUi)

    def PyEditorOnKeyPress(self, event):
        if event.GetKeyCode() == stc.STC_KEY_RETURN:
            numSpaces = self.GetLineIndentation(self.GetCurrentLine())
            line = self.GetLine(self.GetCurrentLine())
            if line.strip()[-1:] == ":":
                numSpaces += TAB_WIDTH
            self.AddText("\n" + " "*numSpaces)
        else:
            event.Skip()

    def PyEditorOnUpdateUi(self, event):
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()

        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and chr(charBefore) in "[]{}()" and styleBefore == stc.STC_P_OPERATOR:
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)

            if charAfter and chr(charAfter) in "[]{}()" and styleAfter == stc.STC_P_OPERATOR:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1  and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)
            pt = self.PointFromPosition(braceOpposite)
            self.Refresh(True, wx.Rect(pt.x, pt.y, 5,5))
            self.Refresh(False)
