import wx
import os
import shutil
import PyInstaller.__main__

"""PyInstaller commands for building the standalone Designer and Viewer apps on Mac and Windows"""

def pyinstall(cmd):
    args = cmd.split(" ")
    PyInstaller.__main__.run(args)

if wx.Platform == "__WXMAC__":
    pyinstall("--onedir --clean -y --windowed -n standalone standalone.py")
    shutil.rmtree("dist/containerDir")
    # using --add-data to add a directory includes its contents, not the directory itself, and since apps are
    # directories, then in order to add the app, we need to --add-data a container directory with the app inside of it.
    os.mkdir("dist/containerDir")
    shutil.move("dist/standalone.app", "dist/containerDir/")
    pyinstall("--onedir --clean -y --windowed --exclude-module PyInstaller --add-data dist/containerDir:. -n CardStock_Designer designer.py")
    pyinstall("--onedir --clean -y --windowed -n CardStock_Viewer viewer.py")

elif wx.Platform == "__WXMSW__":
    pyinstall("--onefile --clean -y --windowed -n standalone standalone.py")
    pyinstall("--onefile --clean -y --windowed --exclude-module PyInstaller --add-data dist/standalone.exe;. -n CardStock_Designer designer.py")
    pyinstall("--onefile --clean -y --windowed -n CardStock_Viewer viewer.py")

else:
    pyinstall("--onefile --clean -y --windowed -n standalone standalone.py")
    pyinstall("--onefile --clean -y --windowed --exclude-module PyInstaller --add-data dist/standalone:. -n CardStock_Designer designer.py")
    pyinstall("--onefile --clean -y --windowed -n CardStock_Viewer viewer.py")
