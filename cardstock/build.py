# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import os
import shutil
import PyInstaller.__main__
import version

EXTRA_MODULES = []

try:
    import serial
    EXTRA_MODULES.append("serial")
except ModuleNotFoundError:
    pass

"""PyInstaller commands for building the standalone CardStock app on Mac and Windows"""


extraModsStr = " ".join([f"--hidden-import {mod}" for mod in EXTRA_MODULES])


def pyinstall(cmd):
    args = cmd.split(" ")
    PyInstaller.__main__.run(args)


if os.path.exists("build"):
    shutil.rmtree("build")

if os.path.exists("dist"):
    shutil.rmtree("dist")


if wx.Platform == "__WXMAC__":
    # Build the standalone binary
    pyinstall(f"--onedir --clean -y --windowed {extraModsStr} -n standalone standalone.py")
    shutil.rmtree("dist/standalone")

    # Build the designer binary
    # using --add-data to add a directory includes its contents, not the directory itself, and since apps are
    # directories, then in order to add the app, we need to --add-data a container directory with the app inside of it.
    if os.path.exists("dist/containerDir"):
        shutil.rmtree("dist/containerDir")
    os.mkdir("dist/containerDir")
    shutil.move("dist/standalone.app", "dist/containerDir/")
    pyinstall("-y CardStock_Designer_mac.spec")
    shutil.rmtree("dist/containerDir")
    shutil.rmtree("dist/CardStock")

    # Build the package directory
    package_dir = f"dist/CardStock_v{version.VERSION}"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.mkdir(package_dir)
    shutil.move("dist/CardStock.app", package_dir)
    shutil.copytree("../examples", package_dir + "/CardStock.app/Contents/MacOS/examples")
    shutil.copy("../README.md", package_dir)
    shutil.copy("../LICENSE", package_dir)

    # More cleanup
    shutil.rmtree("__pycache__")
    shutil.rmtree("build")
    os.remove("standalone.spec")


elif wx.Platform == "__WXMSW__":
    # Build the binaries
    pyinstall(f"--onefile --clean -y --windowed {extraModsStr} -n standalone standalone.py")
    pyinstall(f"--onefile --clean -y --windowed {extraModsStr} --exclude-module PyInstaller --add-data dist/standalone.exe;. -n CardStock designer.py")
    os.remove("dist/standalone.exe")

    # Build the package directory
    package_dir = f"dist/CardStock_v{version.VERSION}"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.mkdir(package_dir)
    shutil.move("dist/CardStock.exe", package_dir)
    shutil.copytree("../examples", package_dir + "/examples")
    shutil.copy("../README.md", package_dir)
    shutil.copy("../LICENSE", package_dir)

    # More cleanup
    shutil.rmtree("__pycache__")
    shutil.rmtree("build")
    os.remove("standalone.spec")
    os.remove("CardStock.spec")


else:
    # Build the binaries
    pyinstall(f"--onefile --clean -y --windowed {extraModsStr} -n standalone standalone.py")
    pyinstall(f"--onefile --clean -y --windowed {extraModsStr} --exclude-module PyInstaller --add-data dist/standalone:. -n CardStock designer.py")
    os.remove("dist/standalone")

    # Build the package directory
    package_dir = f"dist/CardStock_v{version.VERSION}"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.mkdir(package_dir)
    shutil.move("dist/CardStock", package_dir)
    shutil.copytree("../examples", package_dir + "/examples")
    shutil.copy("../README.md", package_dir)
    shutil.copy("../LICENSE", package_dir)

    # More cleanup
    shutil.rmtree("__pycache__")
    shutil.rmtree("build")
    os.remove("standalone.spec")
    os.remove("CardStock.spec")
