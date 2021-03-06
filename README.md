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
* Design and build your stack in the CardStock Designer, and run it from there to test it out.  Or run your stack directly using the CardStock Viewer.
* In-context help appears in the app, right where you need it.  And can be turned off when you no longer want it taking up space.
* All of the creature comforts you've come to expect from a proper application, like full Undo/Redo, and a Find/Replace system that works throughout all of your code and object properties.

### More Advanced
* You can animate most properties of objects, to bring your creations to life.
* You can **import** other python packages into your code, and use them make web requests and display the results, control robots, or run machine learning code, all from within your CardStock stack.
* Basic IDE features, like syntax highlighting, underlining syntax errors while editing, and autocomplete for objects, variables, functions, methods, properties.
* View all code used in a whole stack in one place, and click a line to jump to that line in that object's code for that event.
* View recent error messages, and click one to jump to the offending line of code in the Designer.
* You can export a stack into a standalone application that you can share and distribute.

### Future Plans
* A built-in media library with some basic icons/images, and sound files.
* Allow filling shapes with color gradients
* Add python async support
* Add app icons for the CardStock Designer and Viewer
________
## Known Issues
* Buttons and text fields always remain in front of shapes and images, which get drawn directly on the card view.
* Visual selection indicators (the blue dotted outlines) are drawn behind native views, and so can hide behind overlapping buttons and text fields.
* Stacks can only import additional modules, and export stacks that include them, when running from source.  Not when running from the prebuilt applications. (The prebuilt applications are built with a few additional libraries: requests, pyserial, and more could be added by request.)

## Requirements
The prebuilt applications for Mac and Windows have no external dependencies.

Running CardStock from source requires Python 3.7 or newer (3.9+ recommended), and wxPython 4.1 or newer.
For more responsive Sound playing on Windows, and for any sound playing on Linux, you can optionally install the 
python module simpleaudio.  To export standalone applications, install the python module pyinstaller.

## Installation
You can either, run it from source:
1. install python
2. pip install wxPython
3. pip install simpleaudio (optional, but recommended for Windows and Linux)
4. pip install pyinstaller (optional, but required for exporting stacks)
5. download or clone this repository
6. run designer.py and viewer.py as desired
7. or run build.py to create your own standalone applications for the Designer and Viewer applications.

Or download the ready-to-go CardStock application for Mac or Windows here:
https://github.com/benjie-git/CardStock/releases/latest

## Reference
* [CardStock Wiki](https://github.com/benjie-git/CardStock/wiki)
* [CardStock Manual](https://github.com/benjie-git/CardStock/wiki/Manual)
* [CardStock Tutorial](https://github.com/benjie-git/CardStock/wiki/Tutorial)
* [CardStock Reference Guide](https://github.com/benjie-git/CardStock/wiki/Reference)
