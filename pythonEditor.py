import wx
import wx.stc as stc
import keyword
import analyzer
import helpData

"""
The PythonEditor is used for the CodeEditor in the Designer's ControlPanel.
It offers syntax highlighting, brace pairing, and simple code autocompletion.
"""

TAB_WIDTH = 3
ANALYSIS_TIMEOUT = 500  # in ms


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
    def __init__(self, parent, cPanel, stackManager, **kwargs):
        super().__init__(parent=parent, **kwargs)

        self.stackManager = stackManager
        self.currentModel = None
        self.currentHandler = None
        self.cPanel = cPanel

        self.analyzer = analyzer.CodeAnalyzer()
        self.analysisTimer = wx.Timer()
        self.analysisTimer.Bind(wx.EVT_TIMER, self.OnAnalysisTimer)

        self.SetAutoLayout(True)

        self.SetTabWidth(TAB_WIDTH)
        self.SetUseTabs(0)
        self.SetTabIndents(True)
        self.SetBackSpaceUnIndents(True)
        # self.SetIndentationGuides(True)
        self.SetUseAntiAliasing(True)
        self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 24)
        self.SetUndoCollection(False)
        self.CmdKeyClear(ord("Z"), stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord("Z"), stc.STC_SCMOD_CTRL|stc.STC_SCMOD_SHIFT)
        self.CmdKeyClear(ord("Y"), stc.STC_SCMOD_CTRL)

        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,    'face:%(mono)s,fore:#000000,size:%(size)d' % faces)
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER, 'face:%(mono)s,fore:#999999,back:#EEEEEE' % faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, 'face:%(mono)s,fore:#000000,back:#DDDDFF,bold' % faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,   'face:%(mono)s,fore:#000000,back:#FFCCCC,bold' % faces)
        self.StyleSetSpec(stc.STC_P_DEFAULT,        'face:%(mono)s,fore:#000000,size:%(size)d' % faces)
        self.StyleSetSpec(stc.STC_P_NUMBER,         'face:%(mono)s,fore:#007F7F' % faces)
        self.StyleSetSpec(stc.STC_P_CHARACTER,      'face:%(mono)s,fore:#007F7F,bold' % faces)
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

        self.IndicatorSetStyle(2, stc.STC_INDIC_SQUIGGLE)
        self.IndicatorSetForeground(2, wx.RED)
        self.IndicatorSetAlpha(2, 127)
        self.IndicatorSetUnder(2, True)

        self.AutoCompSetAutoHide(False)
        self.AutoCompSetIgnoreCase(True)
        self.AutoCompSetFillUps("\t\r\n")
        self.AutoCompSetCancelAtStart(True)
        self.AutoCompSetDropRestOfWord(True)
        self.AutoCompSetCaseInsensitiveBehaviour(stc.STC_CASEINSENSITIVEBEHAVIOUR_IGNORECASE)
        self.Bind(stc.EVT_STC_AUTOCOMP_COMPLETED, self.OnACCompleted)
        self.Bind(stc.EVT_STC_AUTOCOMP_CANCELLED, self.OnACCancelled)
        self.Bind(stc.EVT_STC_AUTOCOMP_SELECTION_CHANGE, self.OnACSelectionChange)

        self.Bind(stc.EVT_STC_CHANGE, self.PyEditorOnChange)
        self.Bind(wx.EVT_SET_FOCUS, self.PyEditorOnFocus)
        self.Bind(wx.EVT_KILL_FOCUS, self.PyEditorOnLoseFocus)
        self.Bind(wx.EVT_KEY_DOWN, self.PyEditorOnKeyPress)
        self.Bind(stc.EVT_STC_ZOOM, self.PyEditorOnZoom)
        self.Bind(stc.EVT_STC_UPDATEUI, self.PyEditorOnUpdateUi)

    def PyEditorOnKeyPress(self, event):
        key = event.GetKeyCode()
        if key == stc.STC_KEY_RETURN:
            if self.AutoCompActive():
                self.AutoCompComplete()
            else:
                numSpaces = self.GetLineIndentation(self.GetCurrentLine())
                line = self.GetLine(self.GetCurrentLine())
                pos = self.GetCurrentPos()
                if pos > 1 and self.GetCharAt(pos-1) == ord(":"):
                    numSpaces += TAB_WIDTH
                self.AddText("\n" + " "*numSpaces)
        else:
            if key == ord("Z") and event.ControlDown():
                if not event.ShiftDown():
                    self.stackManager.Undo()
                else:
                    self.stackManager.Redo()
                return
            elif ord('a') <= key <= ord('z') or ord('A') <= key <= ord('Z'):
                wx.CallAfter(self.UpdateAC)
            elif self.AutoCompActive() and (key == wx.WXK_BACK or (event.ShiftDown() and key == ord('-')) or \
                                            (not event.ShiftDown() and ord('0') <= key <= ord('9'))):
                wx.CallAfter(self.UpdateAC)
            elif self.AutoCompActive() and (key in [stc.STC_KEY_ESCAPE, ord(' '), ord('['), ord('.'), ord("'"),
                    ord('`'), ord(']'), ord(';'), ord(','), ord('.'), ord('\\'), ord('/'), ord('-'), ord('=')] or \
                    (event.ShiftDown() and ord('0') <= key <= ord('9'))):
                self.AutoCompCancel()
            event.Skip()

    def PyEditorOnZoom(self, event):
        # Disable Zoom
        z = event.GetEventObject().GetZoom()
        if z != 0:
            event.GetEventObject().SetZoom(0)

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

        if braceAtCaret != -1 and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)
            pt = self.PointFromPosition(braceOpposite)
            self.Refresh(True, wx.Rect(pt.x, pt.y, 5,5))
            self.Refresh(False)

    def PyEditorOnFocus(self, event):
        self.RunDeferredAnalysis()
        event.Skip()

    def PyEditorOnLoseFocus(self, event):
        if self.AutoCompActive():
            self.AutoCompCancel()
        event.Skip()

    def PyEditorOnChange(self, event):
        if self.HasFocus():
            self.RunDeferredAnalysis()
        event.Skip()

    def RunDeferredAnalysis(self):
        self.analysisTimer.StartOnce(ANALYSIS_TIMEOUT)

    def OnAnalysisTimer(self, event):
        self.UpdateACLists()

    def UpdateACLists(self):
        if not self.cPanel:
            return
        self.analyzer.ScanCode(self.cPanel.stackManager.stackModel, self.currentHandler, self.ScanFinished)

    def MarkSyntaxError(self, startPos, length):
        self.SetIndicatorCurrent(2)
        self.IndicatorFillRange(startPos, length)

    def ScanFinished(self):
        key = self.currentModel.GetPath() + "." + self.currentHandler
        self.SetIndicatorCurrent(2)
        self.IndicatorClearRange(0, self.GetLastPosition())
        if key in self.analyzer.syntaxErrors:
            e = self.analyzer.syntaxErrors[key]
            # lineStr = e[1]
            lineNum = e[2]-1
            linePos = e[3]-1
            lineStartPos = self.GetLineEndPosition(lineNum)-self.GetLineLength(lineNum)
            startPos = lineStartPos + linePos-1
            remaining = self.GetLastPosition() - (startPos)
            self.MarkSyntaxError(startPos, min(2, remaining))

        allCodeWin = self.stackManager.designer.allCodeWindow
        if allCodeWin and allCodeWin.IsShown():
            allCodeWin.Update()

    def UpdateAC(self):
        if self.IsInCommentOrString():
            # Don't autocomplete inside a comment or string
            if self.AutoCompActive():
                self.AutoCompCancel()
            return

        # Find the word start
        currentPos = self.GetCurrentPos()
        wordStartPos = self.WordStartPosition(currentPos, True)

        # Display the autocompletion list
        lenEntered = currentPos - wordStartPos
        if wordStartPos > 0 and chr(self.GetCharAt(wordStartPos-1)) == '.':
            acList = self.analyzer.ACAttributes
        else:
            acList = self.analyzer.ACNames

        if lenEntered > 0:
            prefix = self.GetTextRange(wordStartPos, currentPos).lower()
            acList = [s for s in acList if prefix in s.lower()]
            if len(acList) > 1 or (len(acList) == 1 and len(prefix) < len(acList[0])):
                self.AutoCompShow(lenEntered, " ".join(acList))
            else:
                if self.AutoCompActive():
                    self.AutoCompCancel()

    def OnACCompleted(self, event):
        s = event.GetString()
        if s.endswith("()"):
            def moveBackOne():
                car = self.GetCurrentPos()
                self.SetSelection(car-1, car-1)
            wx.CallAfter(moveBackOne)
            self.AutoCompCancel()

    def OnACCancelled(self, event):
        self.cPanel.UpdateHelpText("")

    def OnACSelectionChange(self, event):
        if not self.cPanel:
            return

        s = event.GetString()
        if s:
            helpText = helpData.HelpData.GetHelpForName(s)
            if helpText:
                self.cPanel.UpdateHelpText(helpText)
                return
        self.cPanel.UpdateHelpText("")

    def IsInCommentOrString(self):
        # Use STC's syntax coloring styles to determine whether we're in a comment or string
        pos = self.GetCurrentPos()
        styles = [self.GetStyleAt(pos-i) for i in (0, 2)]
        inString = styles[0] == styles[1] and styles[1] in [stc.STC_P_CHARACTER, stc.STC_P_STRING,
                                                stc.STC_P_STRINGEOL, stc.STC_P_TRIPLE, stc.STC_P_TRIPLEDOUBLE]
        isEndPosString = pos == self.GetLastPosition() and styles[1] in [stc.STC_P_STRINGEOL]
        inComment = styles[1] in [stc.STC_P_COMMENTLINE, stc.STC_P_COMMENTBLOCK]
        return inString or isEndPosString or inComment
