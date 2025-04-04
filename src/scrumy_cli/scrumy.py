# Copyright (c) 2023, espehon
# License: https://www.gnu.org/licenses/gpl-3.0.html

import os
import sys
import argparse
import json
import importlib.metadata

import copykitten
import questionary



try:
    __version__ = f"scrumy {importlib.metadata.version('scrumy_cli')} from scrumy_cli"
except importlib.metadata.PackageNotFoundError:
    __version__ = "Package not installed..."


# Set master folder
storage_folder = os.path.expanduser("~/.local/share/scrumy/")

# Check if storage folder exists, create it if missing.
if os.path.exists(os.path.expanduser(storage_folder)) == False:
    os.makedirs(storage_folder)

# Get list of sub-folders
meeting_folders = [f for f in os.listdir(storage_folder) if os.path.isdir(os.path.join(storage_folder, f))]

# Set wording for new meeting selection
new_meeting_prompt = "Create a new meeting"


# Set argument parsing
parser = argparse.ArgumentParser(
    description="Scrumy: Agile meeting notes and tasks from the commandline!",
    epilog="(scrum with no arguments will start interactive selection)\n\nExample:\n> todo -n pi 3.14159265359\n> fet pi\n3.14159265359\n\nHomepage: https://github.com/espehon/fetchy-cli",
    allow_abbrev=False,
    add_help=False,
    usage="todo [Name] [-n Name Value] [-c Name] [-d Name1 ...] [-r OldName NewName] [-l] [-?] ",
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument('-?', '--help', action='help', help='Show this help message and exit.')
parser.add_argument('-v', '--version', action='version', version=__version__, help="Show package version and exit.")
parser.add_argument('-l', '--list', action='store_true', help='List meetings and exit.')
parser.add_argument('-n', '--new', nargs='?', type=str, metavar='N', action='store', default=False, help='Create new meeting. Named [N] if supplied.')
parser.add_argument('-r', '--rename', nargs=2, type=str, metavar=('O', 'N'), action='store', help='Rename [O] to [N].')
parser.add_argument('-d', '--delete', nargs=1, metavar=('N1'), action='store', type=str, help='Delete [N].')
parser.add_argument("name", nargs='?', help="Name of meeting to view. (Case sensitive)")


def interactive_select():
    if len(meeting_folders) == 0:
        if questionary.confirm('No meetings have been created yet. Would you like to make one now?', default=False, auto_enter=False).ask():
            print('Start new meeting prompt.')
        else:
            sys.exit(0)
    else:
        selection = questionary.select("Select meeting...", choices=[meeting_folders.append(new_meeting_prompt)]).ask()
        if selection == new_meeting_prompt:
            print("Start new meeting prompt.")
        elif selection in meeting_folders:
            print("Start selected meeting.")
        else:
            print("Invalid selection!")
            sys.exit(1)


def create_new_meeting(meeting_name=None) -> bool:
    """Create a new meeting (ask for name if one wasn't given).
    Return True if successful and False if not"""

    if meeting_name == None:
        meeting_name = questionary.text("Enter the new meeting's name:").ask()
    
    # Data validation
    if type(meeting_name) == str:
        meeting_name = meeting_name.strip()
    if meeting_name == None or len(meeting_name) < 1:
        print("No name was supplied. Aborting...")
        sys.exit(0)
    if meeting_name == new_meeting_prompt:
        print(f"'{meeting_name}' is the trigger for a new meeting and is not allowed to be a meeting's name. Aborting...")
        sys.exit(0)
    if ' ' in meeting_name or '\t' in meeting_name:
        if questionary.confirm("There are white spaces in this name. These will be replaced with underscores (_). Do you want to proceed?", default=True, auto_enter=False).ask():
            meeting_name = meeting_name.replace(' ', '_')
            meeting_name = meeting_name.replace('\t', '_')
        else:
            print("Aborting...")
            sys.exit(0)
    if meeting_name in meeting_folders:
        print(f"'{meeting_name}' already exists! Aborting...")
        sys.exit(0)
    
    # Finally we can create the folder
    meeting_folder_path = storage_folder + meeting_name

    try:
        if os.path.exists(os.path.expanduser(meeting_folder_path)) == False:
            os.makedirs(meeting_folder_path)
            print(f"{meeting_name} directory created.")
            with open(meeting_folder_path + 'Notes.txt', 'w'):
                print("Notes.txt created.")
            print("Still gotta do the tasks part") #TODO
    except Exception as e:
        print("An error occurred while trying to create the folder or files...")
        print(e)
        sys.exit(1)






def cli(argv=None):
    args = parser.parse_args(argv) #Execute parse_args()
    print(args)
    if len(sys.argv) == 1:
        interactive_select()
    elif args.list:
        print('List meetings and exit.')
    elif args.new or args.new == None:
        if args.new:
            print(f'Create {args.new}.')
        else:
            print('Start new meeting proc.')
    elif args.rename:
        print('Rename meeting.')
    elif args.delete:
        print('Delete meeting.')
    elif args.name:
        print(f'Start {args.name}.')
    
