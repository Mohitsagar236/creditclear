"""Mock middleware module to fix import issues."""

import sys
import os

# Add this directory to sys.path so we can use the mock middleware
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
