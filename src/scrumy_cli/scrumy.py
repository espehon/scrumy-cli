# Copyright (c) 2023, espehon
# License: https://www.gnu.org/licenses/gpl-3.0.html

import os
import sys
import argparse
import json
import importlib.metadata

# import copykitten
import questionary
from colorama import Fore, Style, init
init(autoreset=True)



try:
    __version__ = f"scrumy {importlib.metadata.version('scrumy_cli')} from scrumy_cli"
except importlib.metadata.PackageNotFoundError:
    __version__ = "Package not installed..."


DEFAULT_SETTINGS = {
                    'storage_path': '~/.local/share/scrumy/',
                    'hightlight_tags': {
                        '!': 'brightred',
                        '@': 'cyan',
                        '#': 'brightwhite',
                        '$': 'brightgreen',
                        '%': 'brightyellow'
                    },
                    'escape_characters': [
                        '\\',
                        '`'
                    ]
}


# Set config file
config_path = os.path.expanduser("~/.config/scrumy/")
if os.path.exists(config_path) == False:
    print(f"Initializing config path at '{config_path}'")
    os.makedirs(config_path)
config_path = os.path.join(config_path, 'settings.json')
if os.path.exists(config_path) == False:
    with open(config_path, 'w') as file:
        print(f"Initializing config file at '{config_path}'")
        json.dump(DEFAULT_SETTINGS, file, indent=4)

# Load configs
try:
    with open(config_path, 'r') as file:
        settings = json.load(file)
except FileNotFoundError:
    print("Config file missing!") # This should never happen as the previous block checks and creates the file if missing
    settings = {} # Return empty dictionary if file doesn't exist

# Validate settings
for key in DEFAULT_SETTINGS:
    if key not in settings:
        print(f"The settings file is missing {key}! Using defaults...")
        settings[key] = DEFAULT_SETTINGS[key]


# Set master folder
storage_folder = os.path.expanduser(settings['storage_path'])

# Check if storage folder exists, create it if missing.
if os.path.exists(os.path.expanduser(storage_folder)) == False:
    print(f"Storage path '{storage_folder}' is missing! Creating path...")
    os.makedirs(storage_folder)


# Set wording for new meeting selection
new_meeting_prompt = "Create a new meeting"

# get terminal width
terminal_width = os.get_terminal_size().columns


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

def get_meeting_folders():
    """Get all meeting folders in the storage folder.
    Returns a list of meeting names."""
    meeting_folders = [f for f in os.listdir(storage_folder) if os.path.isdir(os.path.join(storage_folder, f))]
    return meeting_folders

def is_meeting_foler(meeting_name):
    meeting_folders = get_meeting_folders()
    if meeting_name in meeting_folders:
        return True
    return False

def interactive_select():
    meeting_folders = get_meeting_folders()
    if len(meeting_folders) == 0:
        if questionary.confirm('No meetings have been created yet. Would you like to make one now?', default=False, auto_enter=False).ask():
            return create_new_meeting()
        else:
            sys.exit(0)
    else:
        meeting_folders.append(new_meeting_prompt)
        selection = questionary.select("Select meeting...", choices=meeting_folders).ask()
        if selection == new_meeting_prompt:
            return create_new_meeting()
        elif selection in meeting_folders:
            return selection
        else:
            print("Invalid selection!")
            sys.exit(1)


def create_new_meeting(meeting_name=None) -> str:
    """Create a new meeting (ask for name if one wasn't given).
    Returns meeting name if successful"""

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
    if meeting_name in get_meeting_folders():
        print(f"'{meeting_name}' already exists! Aborting...")
        sys.exit(0)
    
    # Finally we can create the folder
    meeting_folder_path = os.path.join(storage_folder, meeting_name)

    try:
        if os.path.exists(meeting_folder_path) == False:
            os.makedirs(meeting_folder_path)
            print(f"{meeting_name} directory created.")
        note_file_path = os.path.join(meeting_folder_path, 'Notes.txt')
        if os.path.exists(note_file_path) == False:
            with open(note_file_path, 'w'):
                print("Notes.txt created.")
            #TODO: create tasks file
    except Exception as e:
        print("An error occurred while trying to create the folder or files...")
        print(e)
        sys.exit(1)
    return meeting_name

def render_meeting(meeting_name):
    try:
        meeting_path = os.path.join(storage_folder, meeting_name)
        assert os.path.exists(meeting_path)
        note_file = os.path.join(meeting_path, 'Notes.txt')

        if os.path.exists(note_file) == False:
            with open(note_file, 'w') as file:
                print(f"{note_file} is missing! Creating blank note file...")
        with open(note_file, 'r') as file:
            notes = file.read()

        #TODO: check for and read in tasks file

        print('\n' * 4) # add some blank lines for visual padding
        print((Fore.LIGHTWHITE_EX + meeting_name + Style.RESET_ALL).center(terminal_width, '─')) # Title
        print('    ' + Fore.LIGHTWHITE_EX + '[Notes]') # Notes header
        print(notes) # Notes
        print() # Padding
        print('    ' + Fore.LIGHTWHITE_EX + '[Tasks]') # Tasks header
        #TODO: render tasks
        print() # Last padding


    except AssertionError:
        print(f"{meeting_name} not found in {storage_folder}")
        sys.exit(1)


def run_meeting(meeting_name):
    """This is the main meeting function.
    This will loop rendering the meetings then running the prompt process"""
    meeting_folders = get_meeting_folders()
    try:
        assert meeting_name in meeting_folders
        while True:
            render_meeting(meeting_name)
            #TODO: prompt()
            input("This is a placeholder to pause the loop in (Ctrl + C to exit)")


    except AssertionError:
        print(f"Invalid meeting name: {meeting_name}")
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)





def cli(argv=None):
    args = parser.parse_args(argv) #Execute parse_args()
    print(args)
    if len(sys.argv) == 1:
        meeting_name = interactive_select()
        run_meeting(meeting_name)
    elif args.list:
        print('Meetings:')
        for meeting in get_meeting_folders():
            print(f"    {meeting}")
        print() # padding
    elif args.new or args.new == None:
        meeting_name = create_new_meeting(args.new)
        run_meeting(meeting_name)
    elif args.rename:
        print('Rename meeting.')
    elif args.delete:
        print('Delete meeting.')
    elif args.name:
        run_meeting(args.name)
    
