import wx
import wx.html
import version


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

<h2>Properties, Events, and Functions</h2>

<h3>All objects</h3>
<table border=1><tr>
<tr><th>Property</th> <th>Type</th> <th>Description</th></tr>
<tr><td>name</td> <td>string</td> <td>Every object has a name property.  These are forced to be unique within each card, since these become
the names of your object variables that you access from your code.</td></tr>
<tr><td>position</td> <td>point</td> <td>The position property is a point (a list of 2 numbers) that describes where on the
card this object's top-left corner is'.  The first number is how many pixels the object is from the left edge of the card.
The second number is how far down from the top.  All objects except for cards have a position.</td></tr>
<tr><td>size</td> <td>point</td> <td>The size property is a point (a list of 2 numbers) that describes how big this object is'.
The first number is how wide the object is, and the second number is how tall.</td></tr>
</table>
<br/><br/>

<h3>Card</h3>
<table border=1><tr>
<tr><th>Property</th> <th>Type</th> <th>Description</th></tr>
<tr><td>bgColor</td> <td>color</td> <td>Color to use for the background of the card</td></tr>
</table>
<br/><br/>

<h3>Button</h3>
<table border=1><tr>
<tr><th>Property</th> <th>Type</th> <th>Description</th></tr>
<tr><td>title</td> <td>string</td> <td>The visible text that appears on the button.</td></tr>
<tr><td>border</td> <td>bool</td> <td>Should the button show a border around it?</td></tr>
</table>
<br/><br/>

<h3>Text Field</h3>
<table border=1><tr>
<tr><th>Property</th> <th>Type</th> <th>Description</th></tr>
<tr><td>text</td> <td>string</td> <td>The visible text that appears in the text field</td></tr>
<tr><td>alignment</td> <td>(Left, Center, Right)</td> <td>Text alignment Left, Center, or Right.</td></tr>
<tr><td>editable</td> <td>bool</td> <td>Should your users be able to edit this text field?</td></tr>
<tr><td>multiline</td> <td>bool</td> <td>Can this text field show more than 1 line of text?</td></tr>
</table>
<br/><br/>

<h3>Text Label</h3>
<table border=1><tr>
<tr><th>Property</th> <th>Type</th> <th>Description</th></tr>
<tr><td>text</td> <td>string</td> <td>The visible text that appears in the text field</td></tr>
<tr><td>alignment</td> <td>(Left, Center, Right)</td> <td>Text alignment Left, Center, or Right.</td></tr>
<tr><td>font</td> <td>font</td> <td>Which font should this label use?</td></tr>
<tr><td>fontSize</td> <td>int</td> <td>And what font size?</td></tr>
<tr><td>textColor</td> <td>color</td> <td>Color to use for the text</td></tr>
</table>
<br/><br/>

<h3>Image</h3>
<table border=1><tr>
<tr><th>Property</th> <th>Type</th> <th>Description</th></tr>
<tr><td>file</td> <td>string</td> <td>The filename of the image file to show in this image object</td></tr>
<tr><td>fit</td> <td>(Center, Stretch, Fill)</td> <td>How to fit the original image into the image object.
Center will just center the image, and show it full size, and only show the section that fits inside of the image
object.  Fill will resize the image to fit it into your image object, keeping the original aspect-ratio, so it doesn't
look stretched.  Stretch fits the image exactly into you image object by stretching it horizontally or vertically if
needed.</td></tr>
<tr><td>bgColor</td> <td>color</td> <td>Color to use for the background</td></tr>
</table>
<br/><br/>

<h3>Shape</h3>
<table border=1><tr>
<tr><th>Property</th> <th>Type</th> <th>Description</th></tr>
<tr><td>penColor</td> <td>color</td> <td>Color to use for the line/edge of the shape</td></tr>
<tr><td>penThickness</td> <td>int</td> <td>Thickness for the line/edge of the shape</td></tr>
<tr><td>fillColor</td> <td>color</td> <td>Color to use to fill the shape (not available for line or pen shapes)</td></tr>
<tr><td>cornerRadius</td> <td>int</td> <td>For rounded rectangles, this is the radius of the circle used for the corners.</td></tr>
</table>
<br/><br/>

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
