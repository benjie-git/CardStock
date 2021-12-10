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
        html.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        # Set up the layout with a Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, wx.SizerFlags(1).Expand().Border(wx.ALL, 5))
        sizer.Add(button, wx.SizerFlags(0).Align(wx.ALIGN_CENTER).Border(wx.BOTTOM, 5))
        self.SetSizer(sizer)
        self.Layout()

        self.CentreOnParent(wx.BOTH)
        wx.CallAfter(button.SetFocus)

    def OnKeyDown(self, event):
        code = event.GetKeyCode()
        if code == wx.WXK_ESCAPE or (code == ord("W") and event.ControlDown()):
            self.Close()
        event.Skip()


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
is the control panel.  The top of the control panel lets you choose an editing tool.</p>
<p>The first is the hand tool, which
lets you select, move, and resize objects, and edit their properties and code.  Select an object by clicking it, and add 
or remove objects from the selection by Shift-clicking them.  You can also drag out a selection rectangle to select all objects
whose centers it contains.  You can also cycle forwards and backwards through objects on the current card using Tab and
Shift-Tab.  While objects are selected, you can use the Object menu items to group them, flip them, or re-order them to adjust which
objects are in front of, or behind which others.  But note that buttons and text fields always stay in 
front of shapes, images, and text labels.  When an object is selected, you can resize it by dragging the blue resize knob in the 
bottom right corner of the selected object.  Holding down the Shift key while resizing will keep the object's aspect
ratio stable.  You can drag selected objects to move them, or use the arrow keys to move selected objects by 1 pixel at
a time, or by 5 or 20 pixels at a time by holding down Shift or Alt/Option, respectively.</p>
<p>The next four tools are the button, text field, text label, and image tools.  These each 
let you create that type of object, by drawing out the new object's shape on the card on the left.  You can double-click
a text field or text label to edit its text in-place on the card.</p>
<p>The next six tools
are the drawing tools, which let you draw with a pen, drag out an oval, a rectangle, a rounded rectangle, a polygon, 
and a line.
While creating a shape, you can hold down the Shift key to constrain ovals and rectangles to being circles and squares, 
and to make new lines stay perfectly horizontal, vertical, or 45° diagonal.  After creating an object, CardStock will 
switch back to the Hand tool.  Pressing Escape in the Designer will also always return you to the Hand tool.  
Additionally there are keyboard shortcuts for selecting all of the tools.  Those shortcuts are shown when the mouse 
is over that tool's button in the control panel.  They are:<br/>
<ul>
<li>H or Escape for <b>H</b>and
<li>B for <b>B</b>utton
<li>F for Text <b>F</b>ield
<li>T for <b>T</b>ext Label
<li>I for <b>I</b>mage
<li>P for <b>P</b>en
<li>O for <b>O</b>val
<li>R for <b>R</b>ectangle
<li>D for Roun<b>D</b> Rectangle
<li>L for <b>L</b>ine
</ul>
</p>
<p>The area in the control panel below the tools changes depending on which tool you're using, and which objects are 
selected in the card.  When a drawing tool is selected, the control panel offers you settings to choose the pen color,
pen thickness, and fill color for the shapes you draw next.  Then click and drag out the shape you want to add to the 
card.</p>
<p>When you select a single object 
in your card, the control panel will show the two main object editing areas.  The property editor shows, and lets you edit, a
list of the selected object's properties, like name, size, position on the card, colors, etc.  Below the property editor is 
the code editor.  The code editor lets you choose an event for the selected object that you want to edit, and 
gives you space to write your code that runs when that event is triggered.  For example, if you select a button object,
you could edit the code for its OnClicked event, which runs when that button is clicked.  In between the two editors is 
the Context Help box.  This shows information about the most recently selected property or event, or the last 
autocompleted term in the code editor.  You can resize the Context Help box by dragging the bottom-right, blue corner,
and can hide it using the command in CardStock's Help Menu if you already know the info it's telling you, you want the
space back, or it otherwise offends your sensibilities.</p>

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
and whenever that button is clicked, your code will run.  The event picker shows all of the events that apply to the
selected object, and includes the prefix "def " if you already have any code defined for that event.  This helps you
scan the list of events and see which ones have code in them, and also matches the python syntax for defining a
function.  See the CardStock Reference for a description of each type of event, and when they each get run.</p>

<p>In your python event-handling code, you have access to all of the objects in the current card, including their
properties and methods, and some global variables and functions that are always available.
You can always access a special variable called self, which refers to the object who's event is being run.
(So in a button's OnClick code, self refers to that button object.  In a card's OnShowCard code, self is that
card object.)  There is also a variable for each object's name.  So if your button is called yes_button, you could write
yes_button.SetTitle("Done") to change your button's title to Done.  See the CardStock Reference for a list of all 
variables that are automatically provided to your code.  You can of course also create your own variables as well.  It 
is suggested that when you do, you set up the starting value of each variable in one of your
objects' OnSetup events, to make sure that it will always have a value, from the very start of your program running.</p>

<p>When a stack first starts running, all of the cards and all objects on all of the cards will run their OnSetup() 
events.  OnSetup() will also run for any new objects you create using any of the card.AddObject() methods.  
Then the first card's OnShowCard() event will run.  Any time you Goto another card, the current card's OnHideCard() 
event will run, immediately followed by the next card's OnShowCard() event.  After your stack is done starting up, all 
of the current card's objects (including the card itself) will start running their OnPeriodic() events, approximately every 
1/30th of a second.  This is a 
great place to run any periodic checks that need to keep happening often.  The OnResize() event runs on a card object 
when the stack window is resized while that card is shown, to give your stack a chance to re-layout objects based on 
the new card size.  The OnMessage() event runs on an object when any of your other code calls that object's 
object.SendMessage() method, or calls the BroadcastMessage() function, which sends the message to all objects in the 
stack.</p>

<p>The OnKeyDown() and OnKeyUp() events of the current card run when a keyboard key is pressed down, and released, 
respectively.  And OnKeyHold() is called approximately every 1/30th of a second for each key that remains held pressed 
down.</p>

<p>The OnMouseEnter() and OnMouseExit() events for an object are run when the mouse enters and exits screen space that 
overlaps that object.  The OnMouseDown() and OnMouseUp() events of an object are run when the main mouse button is 
pressed and released while the mouse is inside that object.  These do not necessarily come in pairs for any particular 
object, as the mouse could be pressed down while inside one object, moved, and then released outside of that object, or 
vice versa.  The OnMouseMove() event of an object is run when the mouse position moves, while inside that object, 
whether or not the mouse button is down.  The OnMouseDown(), OnMouseMove(), and OnMouseUp() events are all run for the 
topmost object over which the mouse is 
hovering, and then also called for any other objects underneath the mouse, top to bottom, all the way down to the current 
card.  This allows, for example, a card's OnMouseMove() event to continue running for mouse movements, even when the 
mouse moves over an oval object.  If you still want to allow the oval to handle this OnMouseMove() event, 
but block the lower objects like the card from running their OnMouseMove() code too, then you can call the 
StopHandlingMouseEvent() function in the oval's OnMouseMove() code, and then no other objects' event code will run for 
this particular mouse movement.  You can read more details about each of these 
events in the CardStock Reference.</p>

<p>You can also animate changes to many objects' properties.  For example, you could animate the current card's 
background color from its current color to red, over a duration of 2 seconds, using the code: 
card.AnimateBgColor(2, 'red').  If you animate a property that is already animating, it will queue up the animation to 
start after the existing animations finish.  So you could make a circle's size grow and shrink over 2 seconds total, 
using the code:<br/>
&nbsp;&nbsp;&nbsp;&nbsp;circle.AnimateSize(1, [300,300])<br/>
&nbsp;&nbsp;&nbsp;&nbsp;circle.AnimateSize(1, [100,100])<br/>
You can also animate multiple properties of the same object at the same time, since animations only queue up if they are 
animating the same property, otherwise they will animate in parallel.
To stop or interrupt an animation on an object, you can call object.StopAnimating(), and can stop all animations running 
anywhere on a given card or group, including on its children, by calling containerObject.StopAllAnimating().  Both of 
these methods can optionally take a propertyName argument as well, to stop only animations on that property.  For 
example: card.StopAllAnimating("position") will stop any animations of any objects' position properties on the current 
card.</p>

<p>While editing your code, you'll notice that the editor uses syntax highlighting to help you better read your code.
Keywords like 'if', 'for', and 'return' are colored, as are numbers, strings, and comments.  Also while you edit, 
whenever your code is not structurally correct, the spot where python gets confused by a Syntax Error is underlined 
in red, to help you spot problems before even running your code.</p>

<p>When you want to try running your stack from within the Designer app, and see how it works, you can use the Run Stack menu item
in the File menu.  Then just close your running stack window to return to the Designer to continue building and editing!</p>

<br/><br/>

<h2>Moving Objects</h2>

<p>There are a few ways to get objects on a card to move.  You can set an object's position or center to instantly move 
the object to that position, for example: object.center = [100,200].  Or you can animate an object's position or 
center to move it smoothly from its current position to the new one, for example: object.AnimateCenter(1.5, [100,200]) 
to smoothly move the object over 1.5 seconds.</p>

<p>Another way to make an object move is to give it a non-zero speed value.  Speed in CardStock is given in pixels per 
second for both x and y axes.  To make an object start moving diagonally up and right, you can set
object.speed=[100,100].  It will then keep moving in that direction (including past the edge of the card) until you 
change its speed again.  Setting the speed to [0,0] will make it stop moving.  If you want an object to automatically 
bounce off of the edge of the card, or off of other objects, you can call SetBounceObjects() with a list of the objects
you would like it to bounce off of, for example object.SetBounceObjects([card, button_1]).  This is used in the pong 
example stack to make the ball bounce off of the card edges, and the paddle.</p>

<p>An easy way to make an object's movement look like it is being affected by gravity is to give the object a speed, and
then add a line like self.speed.y -= 30 into the object's OnPeriodic() event.</p>

<br/><br/>

<h2>Other Features</h2>

<p>If your stack makes any print() calls, or otherwise causes any text to get written out to the console (to stdout or 
stderr), this will appear in the Viewer application's Console window, which will automatically appear on the first 
non-error text written out.  You can also open the Console manually using the "Show/Hide Console" menu item.  The 
Console window also allows you to enter commands while your stack is running.  You can interactively check variable 
values, and call functions to help debug your code.<p>

<p>If any errors come up while running your stack, you will see them in the status bar at the bottom the running stack's
window.  Any errors will also appear after your return to the Designer, in the red-colored Error List window that will
appear.  You can also open it from the Help menu.  Clicking on an error will take you to the offending line in the code
editor.</p>

<p>If you want to look at all of your code at once, instead of only at one object's code for one event at a time,
you can open the All Code window from the Help menu.  Clicking a line in the All Code editor will also take you to that
line of that object's event code in the code editor.</p>

<p>Note that CardStock has a full Find and Replace system, that lets you find, and optionally replace, strings in your
code and properties throughout your whole stack.  It allows finding using python style regular expression syntax, if you
want to use that to search for more complex expressions.</p>
 
<p>There are lots of example stacks that come with CardStock.  Try playing with some of them, and then dig in deeper
to figure out how they work, and make some changes to see if you can make things work the way you want them to.</p>

<p>Later, once you've built a stack that you want to let other people try, you can run it in the CardStock Viewer 
program (instead of in the Designer). which lets a user run the stack, but not edit it.  You can also run the Export
Stack command from the File menu to export your stack as a stand-alone application, that you can send to other people,
who can run it from their computers without installing CardStock.  This will try to find and include any image and 
sound files that your stack uses, and will include any external python modules that you've imported from your stack.</p>

</body>
</html>
'''

    def __init__(self, parent):
        super().__init__(parent, -1, 'CardStock Manual',
                          size=(800, 600))

        html = wx.html.HtmlWindow(self, -1)
        htmlStr = self.GetHTML()
        # print(htmlStr)
        html.SetPage(htmlStr)
        html.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        # Set up the layout with a Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, wx.SizerFlags(1).Expand().Border(wx.ALL, 5))
        self.SetSizer(sizer)
        self.Layout()

        self.CentreOnParent(wx.BOTH)

    def OnKeyDown(self, event):
        code = event.GetKeyCode()
        if code == wx.WXK_ESCAPE or (code == ord("W") and event.ControlDown()):
            self.Close()
        event.Skip()

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
                                          "access the stack as the global variable <b>stack</b>.  And you can access "
                                          "any of the stack's cards as stack.cardName.")}
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
        # print(htmlStr)
        self.html.SetPage(htmlStr)
        self.html.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        toc = wx.html.HtmlWindow(self.splitter)
        toc.SetPage(HelpData.TOCPage())
        toc.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.TOCLinkClicked)
        toc.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        self.splitter.SplitVertically(toc, self.html)
        self.splitter.SetMinimumPaneSize(120)
        self.splitter.SetSashPosition(200)
        self.splitter.SetSashGravity(0.0)

        self.Layout()
        self.CentreOnParent(wx.BOTH)

    def TOCLinkClicked(self, event):
        self.html.ScrollToAnchor(event.GetLinkInfo().Href)
        return True

    def OnKeyDown(self, event):
        code = event.GetKeyCode()
        if code == wx.WXK_ESCAPE or (code == ord("W") and event.ControlDown()):
            self.Close()
        event.Skip()
