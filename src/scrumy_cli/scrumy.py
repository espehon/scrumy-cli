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




def is_note(object: any) -> bool:
    if type(object) == str:
        return True
    return False


def print_meeting(meeting_name, meeting_date):
    record = meetings[meeting_name][meeting_date]
    print(f"{str(' ' + meeting_name + ' ').center(60, '-')}")
    for tab in record:
        if is_note(record[tab]):
            print(f"{tab}: {record[tab]}")
        else:
            print(f"{tab}")
            for subtab in record[tab]:
                if is_note(record[tab][subtab]):
                    print(f"{' '*4}{subtab}: {record[tab][subtab]}")
                else:
                    print(f"{' '*4}{subtab}")
                    for note in record[tab][subtab]:
                        print(f"{' '*8}{note}: {record[tab][subtab][note]}")


def pars_argv(args: list):
    if str.lower(args[1]) == "new":
        #TODO: #1 Create new meeting function
        pass
    elif str.lower(args[1]) in meetings:
        #TODO: #2 Check for meeting notes for today
        #TODO: #3 Create meeting note entry function
        pass



for arg in sys.argv:
    print(f"{arg =}")
print_meeting("meeting_name_1", "1")