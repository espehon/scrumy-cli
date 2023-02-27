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


for meeting in meetings:
    print(meeting)
    for tab in meetings[meeting]:
        print(f"\t{tab}")
        if is_note(meetings[meeting][tab]):
            print(f"\t\t{meetings[meeting][tab]}")
        else:
            for subtab in meetings[meeting][tab]:
                print(f"\t\t{subtab}")
                if is_note(meetings[meeting][tab][subtab]):
                    print(f"\t\t\t{meetings[meeting][tab][subtab]}")
                else:
                    for note in meetings[meeting][tab][subtab]:
                        print(f"\t\t\t{note}")
                        print(f"\t\t\t\t{meetings[meeting][tab][subtab][note]}")

# print(is_note(meetings))
# print(is_note(meetings['meeting_name_1']))
# print(is_note(meetings['meeting_name_1']['tab_1']))
# print(is_note(meetings['meeting_name_1']['tab_1']['topic_1']))
# print(is_note(meetings['meeting_name_1']['tab_1']['topic_1']['item_1']))