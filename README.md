# CardStock

## About

**CardStock** is a cross-platform tool for quickly and easily building graphical programs, called **stacks**, which can be made up of multiple pages called **cards**.  It provides a drawing-program-like editor for building Graphical User Interfaces, and a code editor for adding event-driven python code.

![Pong example](https://github.com/benjie-git/CardStock/wiki/images/pong.png?raw=true)

There have been many open source projects in the past that tried to capture the fun and simplicity of building programs in HyperCard, but in my opinion, none of them offered the open-ended possibilities and ease of use that made HyperCard such a magical-feeling tool.  So in the grand open source tradition, I built my own.

The guiding principles behind my vision for CardStock are the following, in order of importance:
1. Keep it approachable, understandable, and simple to use for python beginners, through the most salty of Senior Software Engineers.
2. Make it as capable as possible, without interfering with the previous priority.

## Features

### The Basics
* CardStock works on MacOS, Windows, and GNU/Linux.
* You can build programs using objects including text and graphics, images, buttons, and text entry fields.
* You can use your own python code to manipulate the objects and respond to mouse and keyboard events.
* You can play sound files from your code.
* You can search and use clip art in your stacks, thanks to integration with openclipart.com.
* Design and build your stack in the CardStock Designer, and run it from there to test it out.  Or run your stack directly using the CardStock Viewer.
* In-context help appears in the app, right where you need it.  And can be turned off when you no longer want it taking up space.
* All of the creature comforts you've come to expect from a proper application, like full Undo/Redo, and a Find/Replace system that works throughout all of your code and object properties.

### More Advanced
* You can animate most properties of objects, to bring your creations to life.
* Objects can have speed, and can be set up to automatically bounce off of other objects.
* You can **import** other python modules into your code, and use them make web requests and display the results, control robots, or run machine learning code, all from within your CardStock stack.
* Basic IDE features, like syntax highlighting, underlining syntax errors while editing, and autocomplete for objects, variables, functions, methods, properties.
* Run python commands in an interactive Console window while your stack runs, to check or set variable values, call functions, or any other python you want to run.
* View all code used in a whole stack in one place, and click a line to jump to that line in that object's code for that event.
* View recent error messages, and click one to jump to the offending line of code in the Designer.
* You can export a stack into a standalone application that you can share and distribute.

### Future Plans
* Allow exporting a stack as a web page, to allow running it on any web-capable platform.
* Add a rotation property (like on Images) to all shapes and text labels too.
* Add a WebView object type, to allow viewing web content within a stack.
* Update the code editor UI to show all code for an object in one place.
* Allow filling shapes with color gradients.
* Add app icons for the CardStock Designer and Viewer.

________
## Known Issues
* Buttons and text fields always remain in front of shapes and images, which get drawn directly on the card view.
* Visual selection indicators (the blue dotted outlines) are drawn behind native views, and so can hide behind overlapping buttons and text fields.
* Stacks can only import additional modules, and export stacks that include them, when running from source.  Not when running from the prebuilt applications. (The prebuilt applications are built with a few additional libraries: requests, pyserial, and more could be added by request.)

## Requirements
The prebuilt applications for Mac and Windows have no external dependencies.

Running CardStock from source requires Python 3.7 or newer (3.9.x recommended), and wxPython 4.1 or newer.
CardStock also requires installing the modules simpleaudio, PyInstaller, and requests.

## Installation
You can either:

### 1. Run it from source:
1. install python3
2. Linux-only: apt install libasound2-dev libwebkit2gtk-4.0-dev  # or equivalent on non-debian/ubuntu distros
3. pip install wxpython PyInstaller simpleaudio requests  # note that wxpython can take a long time to build
4. download or clone this repository
5. run designer.py and viewer.py as desired
6. optionally run build.py to create your own standalone applications for the Designer and Viewer applications.

### 2. Install using pip/pypi:
1. Linux-only: apt install libasound2-dev libwebkit2gtk-4.0-dev  # or equivalent on non-debian/ubuntu distros
2. pip install cardstock  # note that the dependency wxpython can take a very long time to build
3. run using the newly installed commands cardstock and cardstock_viewer

### 3. Or download the latest, pre-built CardStock application for Mac or Windows here:
https://github.com/benjie-git/CardStock/releases/latest

## Reference
* [CardStock Wiki](https://github.com/benjie-git/CardStock/wiki)
* [CardStock Manual](https://github.com/benjie-git/CardStock/wiki/Manual)
* [CardStock Tutorial](https://github.com/benjie-git/CardStock/wiki/Tutorial)
* [CardStock Reference Guide](https://github.com/benjie-git/CardStock/wiki/Reference)
