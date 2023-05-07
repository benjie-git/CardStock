# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import sys
import os
# Add the CardStock directory to the path, so importing files works correctly when running as a module
path = os.path.dirname(sys.modules[__name__].__file__)
sys.path.insert(0, path)
