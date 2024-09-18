# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import wx.html
import version
import platform
from helpDataGen import HelpData, HelpDataTypes

OUTPUT_HTML = False


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
        super().__init__(parent, -1, 'About CardStock', size=(parent.FromDIP(500), parent.FromDIP(200)))

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
text fields (user-editable), text labels (just text drawn on the screen), images, and 
drawings, using lines, shapes, and a pen tool.  You can group objects together if you want to be able to move them
as one piece, and that group becomes a new object itself.</p>

<br/><br/>

<h2>Designer Layout</h2>
<p>The CardStock Designer application is where you design, build, draw, and code your CardStock programs.  The Designer
window is split into two main parts.  On the left is your stack, that shows the currently selected card and its objects.
On the right is the control panel.  Along the top are controls that let you move between cards, test-run your stack, 
and choose an editing tool.</p>
<p>The first tool is the selection/hand tool, which
lets you select, move, rotate, and resize objects, and edit their properties and code.  Select an object by clicking it, and add 
or remove objects from the selection by Shift-clicking them.  You can also drag out a selection rectangle to select all objects
whose centers it contains.  You can also cycle forwards and backwards through objects on the current card using Tab and
Shift-Tab.  While objects are selected, you can use the Object menu items to group them, flip them, align or distribute 
them, or re-order them to adjust which
objects are in front of, or behind, which others.  But note that currently, Text Fields and Web Views are always displayed in 
front of other objects.  When an object is selected, you can resize it by dragging the rectangular, blue resize knobs in the 
corners of the selected object.  Holding down the Shift key while resizing will keep the object's aspect
ratio stable.  You can drag selected objects to move them, or use the arrow keys to move selected objects by 1 pixel at
a time, or by 5 or 20 pixels at a time by holding down Shift or Alt/Option, respectively.  You can also rotate an object 
by dragging the round, blue rotation knob at the top of the selected object, and can constrain rotation to multiples of
5 degrees by holding down the Shift key.</p>
<p>The next five tools are the button, text field, web view, image, and text label tools.  (Note that web-views are not 
currently supported on cardstock.run.)  These tools each let you create that type of object, by drawing out the new 
object's shape on the card on the left.  You can also double-click a text field or text label to edit its text in-place 
on the card.  Note that you can set a Button object's style, to make it it appear and behave as either a regular button 
with a Border, a Borderless button, a Checkbox, or a Radio button.
</p>
<p>The next six tools are the drawing tools, which let you draw with a pen, drag out an oval, a rectangle, a 
rounded rectangle, a polygon, or a line.  While creating a shape, you can hold down the Shift key to constrain ovals 
and rectangles to being circles and squares, and to make new lines stay perfectly horizontal, vertical, or 45 degrees 
diagonal. After creating an object, CardStock will switch back to the Hand tool.  Pressing Escape in the Designer will 
also always return you to the Hand tool.</p>
 
<p>Additionally there are keyboard shortcuts for selecting all of the tools.  Those shortcuts are shown when the mouse 
is over that tool's button in the control panel.  They are:<br/>
<ul>
<li>H (or Escape) for <b>H</b>and
<li>B for <b>B</b>utton
<li>F for Text <b>F</b>ield
<li>T for <b>T</b>ext Label
<li>W for <b>W</b>eb View
<li>I for <b>I</b>mage
<li>P for <b>P</b>en
<li>O for <b>O</b>val
<li>R for <b>R</b>ectangle
<li>D for Roun<b>D</b> Rectangle
<li>G for Poly<b>G</b>on
<li>L for <b>L</b>ine
</ul>
</p>
<p>To the right of your card editor is the control panel.  When you select a single object 
in your card, the control panel will show the two main object editing areas:  The property editor shows, and lets you edit, a
list of the selected object's properties, like name, size, position on the card, colors, etc.  Below the property editor is 
the code editor.  The code editor lets you view and edit the code that runs when events are triggered for this object.
For example, if you select a button object,
you could edit the code for its <b>on_click</b> event, which runs when that button is clicked.  In between the two editors is 
the Context Help box.  (On cardstock.run, this is actually located on the bottom left of the page.)  This shows 
information about the most recently selected property or event, or the last 
autocompleted term in the code editor.  You can resize the Context Help box by dragging the bottom-right, blue corner,
and can hide it using the command in CardStock's Help Menu if you already know the info it's telling you, you want the
space back, or its incessant helpfulness otherwise offends your sensibilities.</p>

<br/><br/>

<h2>Property Editor</h2>
<p>Each object in your stack, including each card, button, text field, shape, group, etc., has properties that
you can change in the property editor when that object is selected. You can change things like the object's
position and size. And each type of object also has its own specific properties.  For example, a card has a <b>fill_color</b>, 
and a button has a <b>text</b> property.  Each object also has a name, which is how you control it from your python code. 
CardStock makes sure that these names are unique within each card. See the CardStock Reference for a description of each
property, for each type of object.</p>

<br/><br/>

<h2>Code Editor</h2>
<p>The real fun begins when you start adding python code into your objects!  Your CardStock program works by running
certain parts of your program's code when different types of events happen.  For example, you can add some code to a
button object's on_click event, and it will be run when that button is clicked.  Just select the button, and if you don't 
already see a "def on_click():" heading in the code editor, then click the "+ Add Event" button at the top of the code editor, and choose 
"on_click()".  Then add your code into the button's on_click event in the code editor, and now when you run your 
stack, whenever that button is clicked, this code will run.  The "+ Add Event" popup shows all of the events that apply to the
selected object.  For example, only buttons have an on_click() event, and only cards have an on_show_card() event.
See the CardStock Reference for a description of each type of event, and when they each get run.</p>

<p>In your python event-handling code, you have access to all of the objects in your stack, including their
properties and methods, and some global variables and functions that are always available.  So if your button is called 
yes_button, you could write <b>yes_button.text = "Done"</b> to change your button's text to the string "Done".  You can 
also use the variables that are passed into each event function, which are listed inside the parentheses after the event
name.  All events receive a variable called self, which refers to the object who's event is being run.  
So in a button's on_click(self) code, self refers to that button object.  In a card's on_show_card(self) code, self will 
refer to that card object.  Some events also receive other relevant information, for example, on_key_press(self, key_name)
includes key_name, so that your code can see which key was pressed, and on_mouse_move(self, mouse_pos) includes the current 
mouse position as a variable called mouse_pos.  See the CardStock Reference for a list of all 
variables that are automatically provided to your code.  You can of course also create your own variables as well.  It 
is suggested that when you do, you set up the starting value of each variable in one of your objects' on_setup() events, 
to make sure that it will always have a value, from the very beginning of your stack running.</p>

<p>When a stack first starts running, all of the cards and all objects on all of the cards will run their on_setup() 
events.  on_setup() will also run for any new objects you create using any of the card's add methods like card.add_button().  
Then the first card's on_show_card() event will run.  Any time you go to another card, the current card's on_hide_card() 
event will run, immediately followed by the new card's on_show_card() event.  After your stack is done starting up, all 
of the current card's objects (including the card itself) will start running their on_periodic() events, approximately every 
1/30th of a second.  This is a 
great place to run any periodic checks that need to keep happening often.  The on_resize() event runs on a card object 
when the stack window is resized while that card is shown, to give your stack a chance to re-layout objects based on 
the new card size.  The on_message() event runs on an object when any of your other code calls that object's 
object.send_message() method, or calls the broadcast_message() method on this object's card, or on the stack, which sends the 
message to all objects on the card or the whole stack, respectively.</p>

<p>The on_key_press() and on_key_release() events of the current card run when a keyboard key is pressed down, and released, 
respectively.  And on_key_hold() is called approximately every 1/30th of a second for each key that remains held pressed 
down.</p>

<p>The on_mouse_enter() and on_mouse_exit() events for an object are run when the mouse enters and exits screen space that 
overlaps that object.  The on_mouse_press() and on_mouse_release() events of an object are run when the main mouse button is 
pressed and released while the mouse is inside that object.  These do not necessarily come in pairs for any particular 
object, as the mouse could be pressed down while inside one object, moved, and then released outside of that object, or 
vice versa.  The on_mouse_move() event of an object is run when the mouse position moves, while inside that object, 
whether or not the mouse button is down.  The on_mouse_press(), on_mouse_move(), and on_mouse_release() events are all run for the 
topmost object over which the mouse is 
hovering, and then also called for any other objects underneath the mouse, top to bottom, all the way down to the current 
card.  This allows, for example, a card's on_mouse_move() event to continue running for mouse movements, even when the 
mouse moves over an oval object.  If you still want to allow the oval to handle this on_mouse_move() event, 
but block the lower objects like the card from running their on_mouse_move() code too, then you can call the 
stop_handling_mouse_event() function in the oval's on_mouse_move() code, and then no other objects' event code will run for 
this particular mouse movement.  You can read more details about each of these 
events in the CardStock Reference.</p>

<p>You can also animate changes to many objects' properties.  For example, you could animate the current card's 
background color from its current color to red, over a duration of 2 seconds, using the code: 
card.animate_fill_color(2, 'red').  If you animate a property that is already animating, it will queue up the animation to 
start after the existing animations finish.  So you could make a circle's size grow and shrink over 2 seconds total, 
using the code:<br/>
&nbsp;&nbsp;&nbsp;&nbsp;circle.animate_size(1, [300,300])<br/>
&nbsp;&nbsp;&nbsp;&nbsp;circle.animate_size(1, [100,100])<br/>
You can also animate multiple properties of the same object at the same time, since animations only queue up if they are 
animating the same property, otherwise they will animate in parallel.
To stop or interrupt an animation on an object, you can call object.stop_animating(), and can stop all animations running 
anywhere on a given card or group, including on its children, by calling containerObject.stop_all_animating().  Both of 
these methods can optionally take a property_name argument as well, to stop only animations on that property.  For 
example: card.stop_all_animating("position") will stop any animations of any objects' position properties on the current 
card.</p>

<p>While editing your code, you'll notice that the editor uses syntax highlighting to help you better read your code.
Keywords like 'if', 'for', and 'return' are colored, as are numbers, strings, and comments.  Also while you edit, 
whenever your code is not structurally correct, the spot where python gets confused by a Syntax Error is underlined 
in red, to help you spot problems before even running your code.</p>

<p>When you want to try running your stack from within the Designer app, and see how it works, you can use the Run Stack menu item
in the File menu, or from the button in the Toolbar.  Or if you want to test directly from the current card, instead
of starting from the first card, use Run From Current Card from the menu or toolbar.  Then when you want to return to the 
Designer to continue building and editing, just close your running stack window.</p>

<br/><br/>

<h2>Moving Objects</h2>

<p>From your code, there are a few ways to get objects on a card to move.  You can set an object's position (the location of its bottom 
left corner) or center to instantly move the object to that position, for example: object.center = [100,200].  
Or you can animate an object's position or 
center to move it smoothly from its current position to the new one, for example: object.animate_center(1.5, [100,200]) 
to smoothly move the object over 1.5 seconds.</p>

<p>Another way to make an object move is to give it a non-zero speed value.  Speed in CardStock is given in pixels per 
second for both x and y axes.  To make an object start moving diagonally up and right, you can set
object.speed=[100,100].  It will then keep moving in that direction (including past the edge of the card) until you 
change its speed again.  Setting the speed to [0,0] will make it stop moving.  If you want an object to automatically 
bounce off of the edge of the card, or off of other objects, you can call set_bounce_objects() with a list of the objects
you would like it to bounce off of, for example object.set_bounce_objects([card, button_1]).  This is used in the pong 
example stack to make the ball bounce off of the card edges, and the paddle.  When an object bounces, its on_bounce(other_object, edge)
event will run, which additionally tells your code which object it ran into, and which edge of that object it hit.  For
example, if a ball object bounces off of the top edge of the card, the ball object's on_bounce() event will run, with
other_object set to card, and edge set to "Top".</p>

<p>An easy way to make an object's movement look like it is being affected by gravity is to give the object a speed, and
then add a line like <b>self.speed.y -= 30</b> into the object's on_periodic() event.</p>

<br/><br/>

<h2>Web Views</h2>

<p>CardStock also allows you to embed web pages into your stacks, using Web View objects.  But note that currently 
Web Views only work when your stack is run as a program on your computer, and not on the cardstock.run website.  
You can set the URL property
of a Web View, and it will load the web page at that URL.  Or you can set the HTML property of a Web View, and it will 
display that HTML.  You can restrict a Web View to only allow loading pages from a specific set of hosts, by setting its allowed_hosts
property.  For example, if you only want to allow loading pages from my-fun-game.com, then you can set webview_1.URL to
https://my-fun-game.com/starting-page.html, and set webview_1.allowed_hosts to ['my-fun-game.com'].  This way it will 
not allow users to navigate off of the my-fun-game.com site.</p>

<p>When a page loads, either because you set the Web View's URL, or because the user clicked a link to navigate to 
another page, your Web View will run the event on_done_loading(URL, did_load) with the URL as a string, and did_load as
True if the page loaded successfully, and False if the page was unable to load.</p>

<p>From within your CardStock code, you can inject and run JavaScript code into a Web View by calling
webview_1.run_java_script("some(javaScript);code;"), and if your JavaScript code returns a value, it will be returned by the run_java_script() call.
If you want the web page inside your Web View to be able to affect the rest of your CardStock stack, you can set up 
your web page to try to load a URL using the cardstock: scheme, and this will show up in your Web View's on_card_stock_link()
event.  For example, if your HTML includes a link to 'cardstock:test', then when that link is clicked, your Web View's
on_card_stock_link(message) will be called with message='test'.</p>

<br/><br/>

<h2>Other Features</h2>

<p>If your stack makes any print() calls, or otherwise causes any text to get written out to the console (to stdout or 
stderr), this will appear in the Viewer application's Console window, which will automatically appear on the first 
text written out.  You can also open the Console manually using the "Show/Hide Console" menu item.  The 
Console window also allows you to enter python commands while your stack is running.  You can interactively check variable 
values, and call functions to help debug your code.  You can also use the Console while in the Designer, and modify 
your stack using python commands.<p>

<p>CardStock also offers a Variable inspector window while your stack is running.  You can open it using the 
"Show/Hide Variables" menu item.  This window shows you a list of all variables in use by your stack, and allows you to open 
object and list variables hierarchically to see their items and properties, by clicking the right-arrow button on a row.  
For example, you could click the right arrow on the "card" row to see your current card's properties, and then on the 
"children" row to see all objects on that card.  Then on a button's row to see all the properties of that button.  For 
rows representing numbers, strings, boolean values, etc., you can click on the row's value to edit it live, while your 
stack is running.  (This feature is not currently available on cardstock.run.)</p>

<p>If any errors occur while running your stack, error messages will be written to the console window, and then after 
you return to the Designer, they will be listed in the red-colored Error List window that will
appear.  You can also open this window from the Help menu.  Clicking on an error in this list will take you to the 
offending line in the code editor for that event.</p>

<p>If you want to look at all of your code at once, instead of only at one object's code at a time,
you can open the All Code window from the Help menu.  Clicking a line in the All Code editor will take you to that
line of that object's event code in the code editor.  (This feature is not currently available on cardstock.run.)</p>

<p>Note that CardStock has a full Find and Replace system, that lets you find, and optionally replace, strings in your
code and properties throughout your whole stack.</p>

<br/><br/>

<h2>Digging In</h2>

<p>There are lots of example stacks that come with CardStock.  Try playing with some of them, and then dig in deeper
to figure out how they work, and make some changes to see if you can make things work the way you want them to.</p>

<p>Later, once you've built a stack that you want to let other people try, you can run the Export Stack command from 
the Designer's File menu to export your stack, either to the web, or as a stand-alone application, that you can send to other people,
who can run it from their computers without installing CardStock.  The export process will try to find and include any image and 
sound files that your stack uses, and will include any external python modules that you've imported into your stack.  To 
export a stack to the web, CardStock will guide you to set up a cardstock.run account, so you can access your uploaded 
stack, run it on the web, and send out links to let others run it.</p>

</body>
</html>
'''

    def __init__(self, parent):
        super().__init__(parent, -1, 'CardStock Manual', size=(parent.FromDIP(800), parent.FromDIP(600)))

        html = wx.html.HtmlWindow(self, -1)
        htmlStr = self.GetHTML()
        if OUTPUT_HTML:
            f = open("manual.html","w")
            f.write(htmlStr)
            f.close()
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
<p>These global variables are available in all of your event code.  There are also variables for each object on
the current card.  And you can access objects on other cards as, for example, stack.card_3.button_1.</p>
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
                                                 "properties or methods as, for example, object_name.size or "
                                                 "object_name.show()")}
<hr/>
{HelpData.ObjectSection("stack", "Stack", "The stack object represents your whole CardStock program.  You can always "
                                          "access the stack as the global variable <b>stack</b>.  And you can access "
                                          "any of the stack's cards as stack.cardName.")}
<hr/>
{HelpData.ObjectSection("card", "Card", "Cards are the pages of your stack.  Each card has its own set of objects, and"
                                         "its own code for handling events.  The below properties, methods, and "
                                         "events, in addition to those in the All Objects section, apply to card "
                                         "objects.  Access an object's properties or methods as, for example, "
                                         "object_name.size or object_name.show().  You can also access a child object "
                                         "of this card as card.object_name.")}
<hr/>
{HelpData.ObjectSection("button", "Button", "Buttons in CardStock come in 4 styles.  <b>Border</b> style buttons "
                                            "show their <b>text</b> centered inside of a rounded rectangle border, and when clicked, "
                                            "run their on_click() event code.  <b>Borderless</b> buttons behave the same, but "
                                            "are transparent and do not display a border.  A <b>Checkbox</b> button shows its "
                                            "text left-justified, after a checkbox that shows a check when it is selected. "
                                            "When a user clicks a Checkbox, its selection state toggles between selected and not,"
                                            "and the object's on_selection_changed() event is run.  A <b>Radio</b> button shows its "
                                            "text left-justified, after an indicator circle, that shows a dot inside when it is selected. "
                                            "When a user clicks a Radio button, it is selected, and any other Radio "
                                            "buttons in the same Radio group are deselected, "
                                            "and both objects' on_selection_changed() events is run, first the deselection, "
                                            "and then the selection.  All Radio buttons directly on the card are in one Radio group. "
                                            "All Radio buttons that have been grouped together into the same Group object are in their own "
                                            "Radio group. "
                                            "The below properties, methods, and events, in addition to those "
                                            "in the All Objects section, apply to button objects.  Access an object's "
                                            "properties or methods as, for example, object_name.size or "
                                            "object_name.show()")}
<hr/>
{HelpData.ObjectSection("textfield", "Text Field", "Text fields are object where your stack's users can enter or "
                                                    "edit text.  The below properties, methods, and events, in "
                                                    "addition to those in the All Objects section, apply to text field "
                                                    "objects.  Access an object's properties or methods as, for "
                                                    "example, object_name.size or object_name.show()")}
<hr/>
{HelpData.ObjectSection("textlabel", "Text Label", "Text labels are objects that show text on the card, but are not "
                                                    "editable by users. The below properties, methods, and events, in "
                                                    "addition to those in the All Objects section, apply to text labels.  "
                                                    "Access an object's properties or methods as, for "
                                                    "example, object_name.size or object_name.show()")}
<hr/>
{HelpData.ObjectSection("webview", "Web View", "Web views are objects that let you load web pages into your stacks. "
                                               "The below properties, methods, and events, in "
                                                    "addition to those in the All Objects section, apply to web view "
                                                    "objects.  Access an object's properties or methods as, for "
                                                    "example, object_name.size or object_name.show()")}
<hr/>
{HelpData.ObjectSection("image", "Image", "Image objects show an image from an image file.  "
                                           "The below properties, methods, and events, in addition to those in the "
                                           "All Objects section, apply to image objects.  Access an object's "
                                           "properties or methods as, for example, object_name.size or "
                                           "object_name.show()")}
<hr/>
{HelpData.ObjectSection("line", "Shape - Line and Pen", "A line shape is a straight line connecting two points.  A "
                                                         "pen shape is whatever shape you draw out with the pen tool. "
                                                         "Both have a pen_color and a pen_thickness.  "
                                                         "The below properties and methods, in addition to "
                                                         "everything in the All Objects section, apply to these shape "
                                                         "objects.")}
<hr/>
{HelpData.ObjectSection("shape", "Shape - Oval, Rectangle, and Polygon", "Oval rectangle, and polygon shapes have a pen_color and "
                                                                "pen_thickness like Line and Pen objects, but also have "
                                                                "a fill_color.  The below properties, methods, and "
                                                                "events, in addition to those in the "
                                                                "All Objects section, apply to these shape objects.")}
<hr/>
{HelpData.ObjectSection("roundrect", "Shape - Round Rectangle", "A round rectangle shape has a Rectangle shape's "
                                                                 "properties, and additionally has a corner_radius. "
                                                                 "The below properties and methods, in addition to "
                                                                 "everything in the All Objects section, apply to "
                                                                 "these shape objects.")}
<hr/>
{HelpData.ObjectSection("group", "Group", "A group object is created when you group other objects together.  It can "
                                          "then be moved, resized, and rotated like other objects, and can contain code to "
                                          "handle the all-objects events, but beware that ungrouping a group destroys "
                                          "any code in the group object itself.  (But all code in the objects inside "
                                          "the group remains intact.)  Group objects don't have their own specific "
                                          "properties or events, but respond to the following methods, along with "
                                          "everything in the "
                                          "All Objects section.  Access an object's properties or methods as, for "
                                          "example, object_name.size or object_name.show().  You can also access a "
                                          "child object of this group as groupName.object_name")}

</body>
</html>
'''

    def __init__(self, parent):
        super().__init__(parent, -1, 'CardStock Reference',
                          size=(parent.FromDIP(900), parent.FromDIP(950)))

        self.splitter = wx.SplitterWindow(self, style=wx.SP_3DSASH | wx.SP_LIVE_UPDATE)

        self.html = wx.html.HtmlWindow(self.splitter, -1)
        htmlStr = self.GetHTML()
        if OUTPUT_HTML:
            f = open("reference.html","w")
            f.write(htmlStr)
            f.close()
        self.html.SetPage(htmlStr)
        self.html.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        toc = wx.html.HtmlWindow(self.splitter)
        toc.SetPage(HelpData.TOCPage())
        toc.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.TOCLinkClicked)
        toc.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        self.splitter.SplitVertically(toc, self.html)
        self.splitter.SetMinimumPaneSize(self.FromDIP(120))
        self.splitter.SetSashPosition(self.FromDIP(200))
        self.splitter.SetSashGravity(0.0)

        self.Layout()
        self.CentreOnParent(wx.BOTH)
        self.html.SetFocus()

    def TOCLinkClicked(self, event):
        self.html.ScrollToAnchor(event.GetLinkInfo().Href)
        return True

    def OnKeyDown(self, event):
        code = event.GetKeyCode()
        if code == wx.WXK_ESCAPE or (code == ord("W") and event.ControlDown()):
            self.Close()
        event.Skip()
