import wx
import wx.html
import version
from helpData import HelpData


class CardStockAbout(wx.Dialog):
    """ An about box that uses an HTML view """

    text = f'''
<html>
<body bgcolor="#60acac">
<center><table bgcolor="#778899" width="100%%" cellspacing="0"
cellpadding="4" border="1">
<tr>
    <td align="center"><h1>CardStock {version.VERSION} </h1></td>
</tr>
</table>
</center>
<p><b>CardStock</b> is a tool for learning python using a GUI framework inspired by HyperCard of old.</p>
</body>
</html>
'''

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, 'About CardStock',
                          size=(420, 380) )

        html = wx.html.HtmlWindow(self, -1)
        html.SetPage(self.text)
        button = wx.Button(self, wx.ID_OK, "Okay")

        # Set up the layout with a Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, wx.SizerFlags(1).Expand().Border(wx.ALL, 5))
        sizer.Add(button, wx.SizerFlags(0).Align(wx.ALIGN_CENTER).Border(wx.BOTTOM, 5))
        self.SetSizer(sizer)
        self.Layout()

        self.CentreOnParent(wx.BOTH)
        wx.CallAfter(button.SetFocus)


class CardStockReference(wx.Frame):
    """ A help window that uses an HTML view """

    text = f'''
<html>
<body bgcolor="#EEEEEE">
<center><table bgcolor="#778899" width="100%%" cellspacing="0"
cellpadding="4" border="1">
<tr>
    <td align="center"><h1>CardStock {version.VERSION} </h1></td>
</tr>
</table>
</center>
<p><b>CardStock</b> is a tool for learning python using a live GUI-editor inspired by HyperCard.</p>
<br/><br/>

<h2>The Basics</h2>
<p>A program that you create in CardStock is called a stack.  It can have multiple pages, each called a card.
On each card, you can draw out your user interface, as you would in a drawing program -- laying out objects like buttons,
text fields (user-editable), text labels (just static text drawn on the scren), images, and 
drawings using lines, shapes, and a pen tool.  You can group objects together if you want to be able to move them
as one piece, and that group becomes a new object.</p>

<p>Each object in your stack, including each card, button, text field, shape, group, etc., has properties that
you can change in the property editor when that object is selected. You can change things like the object's
position and size. And many types of objects also have their own specific properties.  For example, a button has a title,
and a card has a background color.  Each object has a name property, which is how you control it from your python code.
See below for a description of each property for each kind of object.</p>

<p>The real fun begins when you start adding python code into your objects.  Your CardStock program works by running
certain parts of your program when different kinds of events happen.  For example, you can add some code to one of your
button objects that gets run when the button is clicked.  Just add your code into the button's OnClick event handler in the
code editor, and whenever that button is clicked, your code will run.  See below for a description of each kind of
event, and when they each get run.</p>

<p>In your python event-handling code, you have access to all of the objects in the current card, and some global variables
and functions that are always available.  You can always access a special variable called self, that refers to the object 
who's event is being run.  (So in a buttons OnClick code, self is that button.  In a card's OnShowCard code, self is that
card.)  There is also a variable for each object's name.  so if your button is called button_1, you could write
button_1.SetTitle("Hello") to change your buttons's title to Hello.  See below for a list of all variables that are
automatically provided to your code.  You can of course also create your own variables as well.  It is suggested that
when you do this (which will be often!), you set up the starting value of your variable in one of your objects' OnStart
events, to make sure that it will always have a value, from the very start of your program running.</p>
<br/><br/>

<h2>Global Variables</h2>
<p>Global variables are objects that are available in all of your event handlers' code.</p>
{HelpData.GlobalVariablesTable()}
<br/><br/>

<h2>Global Functions</h2>
<p>These global functions are available in all of your event handlers' code.</p>
{HelpData.GlobalFunctionsTable()}
<br/><br/>

{HelpData.ObjectSection("object", "All Objects", "Many properties, methods, and event handlers apply to objects of all types, so we'll list those all here just once.")}

{HelpData.ObjectSection("card", "Cards", None)}

{HelpData.ObjectSection("button", "Buttons", None)}

{HelpData.ObjectSection("textfield", "Text Fields", None)}

{HelpData.ObjectSection("textlabel", "Text Labels", None)}

{HelpData.ObjectSection("image", "Images", None)}

{HelpData.ObjectSection("line", "Shapes - Line and Pen", None)}

{HelpData.ObjectSection("shape", "Shapes - Oval and Rectangle", None)}

{HelpData.ObjectSection("round_rect", "Shapes - Round Rectangle", None)}

</body>
</html>
'''

    def __init__(self, parent):
        super().__init__(parent, -1, 'CardStock Reference',
                          size=(800, 600))

        html = wx.html.HtmlWindow(self, -1)
        html.SetPage(self.text)

        # Set up the layout with a Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, wx.SizerFlags(1).Expand().Border(wx.ALL, 5))
        self.SetSizer(sizer)
        self.Layout()

        self.CentreOnParent(wx.BOTH)
