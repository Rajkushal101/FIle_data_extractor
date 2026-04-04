"""
Tests Package
Unit and integration tests for the application
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
