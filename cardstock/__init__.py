import sys
import os
# Add the CardStock directory to the path, so importing files works correctly when running as a module
path = os.path.dirname(sys.modules[__name__].__file__)
sys.path.insert(0, path)
