import wx
import wx.html
import version
import platform
from helpData import HelpData, HelpDataTypes


class CardStockAbout(wx.Dialog):
    """ An about box that uses an HTML view. """

    def GetHTML(self):
        return f'''
<html>
<body bgcolor="#EEEEEE">
<center><table bgcolor='#D0DFEE' cellspacing="0" cellpadding="4" border="0">
<tr>
    <td align="center"><h1>CardStock</h1>
    CardStock version {version.VERSION} | 
    Python version {platform.python_version()} |  
    wxPython version {wx.__version__}
    </td>
</tr>
</table>
</center>
<p><b>CardStock</b> is a cross-platform tool for quickly and easily building and running graphical desktop applications.
It provides a drawing-program-like editor for building Graphical User Interfaces, and a code editor for adding
event-driven python code.  It is inspired by the simplicity and power of Apple's old HyperCard tool.</p>
</body>
</html>
'''

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, 'About CardStock',
                          size=(500, 200) )

        html = wx.html.HtmlWindow(self, -1)
        html.SetPage(self.GetHTML())
        button = wx.Button(self, wx.ID_OK, "Okay")

        # Set up the layout with a Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, wx.SizerFlags(1).Expand().Border(wx.ALL, 5))
        sizer.Add(button, wx.SizerFlags(0).Align(wx.ALIGN_CENTER).Border(wx.BOTTOM, 5))
        self.SetSizer(sizer)
        self.Layout()

        self.CentreOnParent(wx.BOTH)
        wx.CallAfter(button.SetFocus)


class CardStockManual(wx.Frame):
    """ A help window that uses an HTML view.  This is the manual, which explains how to use CardStock. """

    def GetHTML(self):
        return f'''
<html>
<body bgcolor="#EEEEEE">
<center><table bgcolor='#D0DFEE' cellspacing="0" cellpadding="4" border="0">
<tr>
    <td align="center"><h1>CardStock Manual</h1>
    CardStock version {version.VERSION} | 
    Python version {platform.python_version()} |  
    wxPython version {wx.__version__}
    </td>
</tr>
</table>
</center>
<p><b>CardStock</b> is a cross-platform tool for quickly and easily building and running graphical desktop applications.
It provides a drawing-program-like editor for building Graphical User Interfaces, and a code editor for adding
event-driven python code.  It is inspired by the simplicity and power of Apple's old HyperCard tool.</p>

<br/><br/>

<h2>The Basics</h2>
<p>A program that you create in CardStock is called a stack.  It can have multiple pages, each called a card.
On each card, you can draw out your user interface, as you would in a drawing program -- laying out objects like buttons,
text fields (user-editable), text labels (just static text drawn on the screen), images, and 
drawings, using lines, shapes, and a pen tool.  You can group objects together if you want to be able to move them
as one piece, and that group becomes a new object itself.</p>

<br/><br/>

<h2>Designer Layout</h2>
<p>The CardStock Designer application is where you design, build, draw, and code your CardStock programs.  The Designer
window is split into two main parts.  On the left is your stack, that shows the currently selected card and its objects.
On the right
is the control panel.  The top of the control panel lets you choose an editing tool.  The first is the hand tool, which
lets you select, move, and resize objects, and edit their properties and code.  
The next four are the button, text field, text label, and image tools.  These each 
let you create that type of object, by drawing out the new object's shape on the card on the left.  The next five tools
are the drawing tools, which let you draw with a pen, drag out an oval, a rectangle, a rounded rectangle, and a line.
The area in the control panel below the tools changes depending on which tool you're using, and which objects are 
selected in the card.</p>
<p>When a drawing tool is selected, the control panel offers you settings to choose the pen color,
pen thickness, and fill color for the shapes you draw next.  Then click and drag out the shape you want to add to the 
card.  While creating a shape, you can hold down the Shift key to make ovals and rectangles stay circles and squares, 
and to make new lines stay perfectly horizontal or vertical.</p>  
<p>When the hand tool is enabled, you can select, move, and resize objects.  Select an object by clicking it, and add 
more objects to the selection by Shift-clicking them.  You can also drag out a selection rectangle to select multiple
objects.  While objects are selected, you can use the Object menu items to group them, or re-order them to adjust which
objects are in front of, or behind which others.  But note that buttons, text fields, and text labels always stay in 
front of shapes and images.</p>
<p>When you select a single object 
in your card, the control panel will show the two main object editing areas.  The property editor shows, and lets you edit, a
list of the selected object's properties, like name, size, position on the card, colors, etc.  Below the property editor is 
the code editor.  The code editor lets you choose an event for the selected object that you want to edit, and 
gives you space to write your code that runs when that event is triggered.  For example, if you select a button object,
you could edit the code for its OnClicked event, which runs when that button is clicked.  In between the two editors is 
the Context Help box.  This shows information about the most recently selected property or event.  You can hide the 
Context Help box in CardStock's Help Menu.</p>

<br/><br/>

<h2>Property Editor</h2>
<p>Each object in your stack, including each card, button, text field, shape, group, etc., has properties that
you can change in the property editor when that object is selected. You can change things like the object's
position and size. And many types of objects also have their own specific properties.  For example, a button has a title,
and a card has a background color.  Each object also has a name, which is how you control it from your python code. 
CardStock makes sure that these names are unique within each card. See the CardStock Reference for a description of each
property, for each kind of object.</p>

<br/><br/>

<h2>Code Editor</h2>
<p>The real fun begins when you start adding python code into your objects!  Your CardStock program works by running
certain parts of your program when different types of events happen.  For example, you can add some code to a
button object's OnClicked event, that gets run when that button is clicked.  Just choose the OnClicked() event in the 
event picker at the top of the code editor, and then add your code into the button's OnClicked event in the code editor,
and whenever that button is clicked, your code will run.  See the CardStock Reference for a description of each type of
event, and when they each get run.</p>

<p>In your python event-handling code, you have access to all of the objects in the current card, including their
properties and methods, and some global variables and functions that are always available.
You can always access a special variable called self, which refers to the object 
who's event is being run.  (So in a button's OnClick code, self refers to that button object.  In a card's OnShowCard code, self is that
card object.)  There is also a variable for each object's name.  So if your button is called yes_button, you could write
yes_button.SetTitle("Done") to change your button's title to Done.  See the CardStock Reference for a list of all 
variables that are automatically provided to your code.  You can of course also create your own variables as well.  It 
is suggested that when you do, you set up the starting value of each variable in one of your
objects' OnStart events, to make sure that it will always have a value, from the very start of your program running.</p>

<p>When you want to try running your stack from within the Designer app, and see how it works, you can use the Run Stack menu item
in the File menu.  Then just close your running stack window to return to the Designer to continue editing.</p>

<p>There are lots of example stacks that come with CardStock.  Try playing with some of them, and then dig in deeper
to figure out how they work, and make some changes to see if you can make things work the way you want them to.</p>

<p>Later, once you've built a stack that you want to let other people try, you can run it in the CardStock Viewer 
program (instead of in the Designer). which lets a user run the stack, but not edit it.</p>

</body>
</html>
'''

    def __init__(self, parent):
        super().__init__(parent, -1, 'CardStock Manual',
                          size=(800, 600))

        html = wx.html.HtmlWindow(self, -1)
        htmlStr = self.GetHTML()
        html.SetPage(htmlStr)

        # Set up the layout with a Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, wx.SizerFlags(1).Expand().Border(wx.ALL, 5))
        self.SetSizer(sizer)
        self.Layout()

        self.CentreOnParent(wx.BOTH)


class CardStockReference(wx.Frame):
    """ A help window that uses an HTML view.  This is the Reference Guide, which lists and explains the details of
     each kind of CardStock object. """

    def GetHTML(self):
        return f'''
<html>
<body bgcolor="#EEEEEE">
<a name="#top"/>
<center><table bgcolor='#D0DFEE' cellspacing="0" cellpadding="4" border="0">
<tr>
    <td align="center"><h1>CardStock Reference</h1>
    CardStock version {version.VERSION} | 
    Python version {platform.python_version()} |  
    wxPython version {wx.__version__}
    </td>
</tr>
</table>
</center>

<p>Below is a full listing of the CardStock-specific variables, functions, objects, methods and events 
available to you in your CardStock code.  Additionally, you can import other python packages and use them however you'd
like, to make network connections, control other software or hardware, or perform other calculations.  For more
information on how to use CardStock, see the CardStock Manual in the Help menu.</p>
<br/><br/>
<hr/>
<a name="#dataTypes"/>
<h2>Data Types Used in CardStock</h2>
<p>These are the data types used by the properties, functions, and events in CardStock.</p>
{HelpData.HtmlTableFromLists(HelpDataTypes)}
<br/><br/>
<hr/>
<a name="#globalVars"/>
<h2>Global Variables</h2>
<p>These global variables are available in all of your event code.</p>
{HelpData.GlobalVariablesTable()}
<br/><br/>
<hr/>
<a name="#globalFuncs"/>
<h2>Global Functions</h2>
<p>These global functions are available in all of your event code.</p>
{HelpData.GlobalFunctionsTable()}
<br/><br/>
<hr/>
{HelpData.ObjectSection("object", "All Objects", "Many properties, methods, and events apply to objects of all "
                                                 "types, so we'll list those all here just once.  Access an object's "
                                                 "properties or methods as, for example, objectName.size or "
                                                 "objectName.Focus()")}
<hr/>
{HelpData.ObjectSection("stack", "Stack", "The stack object represents your whole CardStock program.  You can always "
                                          "access the stack as the global variable <b>stack</b>.")}
<hr/>
{HelpData.ObjectSection("card", "Card", "Cards are the pages of your stack.  Each card has its own set of objects, and"
                                         "its own code for handling events.  The below properties, methods, and "
                                         "events, in addition to those in the All Objects section, apply to card "
                                         "objects.  Access an object's properties or methods as, for example, "
                                         "objectName.size or objectName.Focus().  You can also access a child object "
                                         "of this card as card.objectName.")}
<hr/>
{HelpData.ObjectSection("button", "Button", "Buttons show their title, and when clicked, run their OnClicked event "
                                             "code.  The below properties, methods, and events, in addition to those "
                                             "in the All Objects section, apply to button objects.  Access an object's "
                                             "properties or methods as, for example, objectName.size or "
                                             "objectName.Focus()")}
<hr/>
{HelpData.ObjectSection("textfield", "Text Field", "Text fields are object where your stack's users can enter or "
                                                    "edit text.  The below properties, methods, and events, in "
                                                    "addition to those in the All Objects section, apply to text field "
                                                    "objects.  Access an object's properties or methods as, for "
                                                    "example, objectName.size or objectName.Focus()")}
<hr/>
{HelpData.ObjectSection("textlabel", "Text Label", "Text labels are objects that show text on the card, but are not "
                                                    "editable by users. The below properties, methods, and events, in "
                                                    "addition to those in the All Objects section, apply to text label "
                                                    "objects.  Access an object's properties or methods as, for "
                                                    "example, objectName.size or objectName.Focus()")}
<hr/>
{HelpData.ObjectSection("image", "Image", "Image objects show an image from an image file, and can be rotated.  "
                                           "The below properties, methods, and events, in addition to those in the "
                                           "All Objects section, apply to image objects.  Access an object's "
                                           "properties or methods as, for example, objectName.size or "
                                           "objectName.Focus()")}
<hr/>
{HelpData.ObjectSection("line", "Shape - Line and Pen", "A line shape is a straight line connecting two points.  A "
                                                         "pen shape is whatever shape you draw out with the pen tool. "
                                                         "Both have a penColor and a penThickness.  "
                                                         "The below properties and methods, in addition to "
                                                         "everything in the All Objects section, apply to these shape "
                                                         "objects.")}
<hr/>
{HelpData.ObjectSection("shape", "Shape - Oval and Rectangle", "Oval and rectangle shapes have a penColor and "
                                                                "penThickness like Line and Pen objects, but also have "
                                                                "a fillColor.  The below properties, methods, and "
                                                                "events, in addition to those in the "
                                                                "All Objects section, apply to these shape objects.")}
<hr/>
{HelpData.ObjectSection("roundrect", "Shape - Round Rectangle", "A round rectangle shape has a Rectangle shape's "
                                                                 "properties, and additionally has a cornerRadius. "
                                                                 "The below properties and methods, in addition to "
                                                                 "everything in the All Objects section, apply to "
                                                                 "these shape objects.")}
<hr/>
{HelpData.ObjectSection("group", "Group", "A group object is created when you group other objects together.  It can "
                                           "then be moved and resized like other objects, and can contain code to "
                                           "handle the all-objects events, but beware that ungrouping a group destroys "
                                           "any code in the group object itself.  (But all code in the objects inside "
                                           "the group remains intact.)  Group objects don't have their own specific "
                                           "properties, methods, or events, but respond to everything in the "
                                           "All Objects section.  Access an object's properties or methods as, for "
                                           "example, objectName.size or objectName.Focus().  You can also access a "
                                           "child object of this group as groupName.objectName")}

</body>
</html>
'''

    def __init__(self, parent):
        super().__init__(parent, -1, 'CardStock Reference',
                          size=(900, 950))

        self.splitter = wx.SplitterWindow(self, style=wx.SP_3DSASH | wx.SP_LIVE_UPDATE)

        self.html = wx.html.HtmlWindow(self.splitter, -1)
        htmlStr = self.GetHTML()
        self.html.SetPage(htmlStr)

        toc = wx.html.HtmlWindow(self.splitter)
        toc.SetPage(HelpData.TOCPage())
        toc.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.TOCLinkClicked)

        self.splitter.SplitVertically(toc, self.html)
        self.splitter.SetMinimumPaneSize(120)
        self.splitter.SetSashPosition(200)
        self.splitter.SetSashGravity(0.0)

        self.Layout()
        self.CentreOnParent(wx.BOTH)

    def TOCLinkClicked(self, event):
        self.html.ScrollToAnchor(event.GetLinkInfo().Href)
        return True
