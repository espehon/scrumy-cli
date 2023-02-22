# Copyright (c) 2023, espehon
# License: https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os
import argparse
import json
import importlib.metadata


from colorama import Fore, init
init(autoreset = True)

try:
    __version__ = f"scrumy {importlib.metadata.version('scrumy_cli')} from scrumy_cli"
except importlib.metadata.PackageNotFoundError:
    __version__ = "Package not installed..."







#DATA_PATH = os.path.expanduser('~/.local/share/scrumy/meetings.json')
DATA_PATH = os.path.expanduser('~/github/scrumy/test/test.json')



with open(DATA_PATH, 'r') as data:
    meetings = json.load(data)



for meeting in meetings:
    print(meeting)