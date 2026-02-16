"""
Pytest configuration for weather service tests.
Configures Python path to allow importing from app module.
"""
import sys
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent.parent
sys.path.insert(0, str(server_dir))
