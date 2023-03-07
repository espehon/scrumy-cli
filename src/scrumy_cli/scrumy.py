# Copyright (c) 2023, espehon
# License: https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os
import argparse
import json
import datetime
import importlib.metadata


from colorama import Fore, init
init(autoreset = True)

try:
    __version__ = f"scrumy {importlib.metadata.version('scrumy_cli')} from scrumy_cli"
except importlib.metadata.PackageNotFoundError:
    __version__ = "Package not installed..."







#DATA_PATH = os.path.expanduser('~/.local/share/scrumy/meetings.json')
DATA_PATH = os.path.expanduser('~/github/scrumy/test/test.json')
SCRUMY_KEYWORDS = ["new", "delete", "print", "echo", "output", "view"]
TODAY = str(datetime.datetime.now().date())


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
            print(f"{tab}...")
            for subtab in record[tab]:
                if is_note(record[tab][subtab]):
                    print(f"{' '*4}{subtab}: {record[tab][subtab]}")
                else:
                    print(f"{' '*4}{subtab}...")
                    for note in record[tab][subtab]:
                        print(f"{' '*8}{note}: {record[tab][subtab][note]}")

def create_new_meeting(meeting_name: str):
    r"""
    Asserts name is not a keyword.
    Asserts name is not already used.
    Loops user entry until told to stop.
    ']' followed by text is used to single new tab (indentation).
        ']This is a new tab' 
    '[' on a blank line is used to end current tab.
    '[[' on a blank line returns to first level indentation
    \\ is used to end entry
    """

    if meeting_name in SCRUMY_KEYWORDS:
        print("Meeting name cannot be a keyword.")
        print(f"{SCRUMY_KEYWORDS = }")
        return 1
    if meeting_name in meetings:
        print("A meeting already exists with this name.")
        return 1
    
    user = '' # priming for loop
    indent_level = 0
    meetings[meeting_name] = {}
    meetings[meeting_name]['template'] = {}

    while user.strip() != r"\\":
        if user == '':
            pass
        elif user[0] == ']':
            pass
        elif user.strip() == '[':
            pass
        elif user.strip() == '[[':
            pass
        else:
            meetings[meeting_name]['template'][user] = ''

        #TODO: write changes

        user = input(f"{'    '*indent_level}> ")

    # testing 
    print_meeting(meeting_name, 'template')
    

def pars_argv(args: list):
    if len(args) == 1:
        # print meeting names
        pass
        return 0
    if str.lower(args[1]) == "new" and len(args) == 3:
        create_new_meeting(str.lower(args[2]))
        pass
        return 0
    if str.lower(args[1]) in meetings:
        #TODO: #2 Check for meeting notes for today
        #TODO: #3 Create meeting note entry function
        pass
        return 0



# for arg in sys.argv:
#     print(f"{arg =}")
# print_meeting("meeting_name_1", "1")
def cli():
    pars_argv(sys.argv)