# CardStock

## About

**CardStock** is a cross-platform tool for quickly and easily building graphical desktop applications, called **stacks**, which can be made up of multiple pages called **cards**.  It provides a drawing-program-like editor for building Graphical User Interfaces, and a code editor for adding event-driven python code.

![Pong example](https://github.com/benjie-git/CardStock/wiki/images/pong.png?raw=true)

There have been many open source projects in the past that tried to capture the fun and simplicity of building programs in HyperCard, but in my opinion, none of them offered the open-ended possibilities and ease of use that made HyperCard such a magical-feeling tool.  So in the grand open source tradition, I built my own.

The guiding principles behind my vision for CardStock are the following, in order of importance:
1. Keep it understandable, simple, and easy to use, for python beginners, through the most salty Senior Software Engineers.
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

### Future Plans
* A built-in media library with some basic icons/images, and sound files.
* Add code completion to the code editor.
* Allow exporting a stack into a standalone application that you can share.
* Add a way to view all code used in a whole stack in one place.
* Add a way to view recent error messages, and click to jump to the offending line of code in the Designer.


## Requirements
CardStock requires Python 3.7 or newer, and wxPython 4.0 or newer.  And for more responsive Sound playing, you can optionally install the python module simpleaudio.

## Installation
Currently, you'll need to:
1. install python
2. pip install wxPython
3. pip install simpleaudio
4. download or clone this repository
5. run designer.py and viewer.py as desired

Soon after the first release is ready, there will also be prebuilt bundles ready for download for various platforms, built using pyinstaller.

## Reference
* [CardStock Wiki](https://github.com/benjie-git/CardStock/wiki)
* [CardStock Manual](https://github.com/benjie-git/CardStock/wiki/Manual)
* [CardStock Reference Guide](https://github.com/benjie-git/CardStock/wiki/Reference)
