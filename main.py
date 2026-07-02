#!/usr/bin/env python3
"""GYM OS ULTIMATE - Personal Fitness Operating System"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import init_db
from src.ui import run


def main():
    print("🏋️ GYM OS ULTIMATE - Initializing...")
    init_db()
    print("✅ Database ready.")
    print("🚀 Launching application...")
    sys.exit(run())


if __name__ == "__main__":
    main()
