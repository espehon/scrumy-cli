# Copyright (c) 2023, espehon
# License: https://www.gnu.org/licenses/gpl-3.0.html

import os
import sys
import argparse
import json
import shutil
import datetime
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
                    'highlight_tags': {
                        '!': 'brightred',
                        '@': 'cyan',
                        '#': 'brightwhite',
                        '$': 'brightgreen',
                        '%': 'brightyellow'
                    },
                    'escape_characters': [
                        '\\',
                        '`'
                    ],
                    'editors': [
                        'vim',
                        'nano',
                        'emacs',
                        'micro',
                        'ne',
                        'joe',
                        'ed',
                        'kak'
                    ],
                    'scrumy_commands': {
                        'notes_mode': [
                            'n',
                            'note',
                            'notes',
                            'edit'
                        ],
                        'tasks_mode': [
                            't',
                            'task',
                            'tasks'
                        ],
                        'exit': [
                            'q',
                            'quit',
                            'exit',
                            'abort',
                            'cancel',
                            'stop'
                        ],
                        'help': [
                            'h',
                            'help',
                            '?'
                        ]
                    },
                    'age_colors': {
                        '0': '',
                        '1': 'bright_white',
                        '2': 'bright_yellow',
                        '3': 'yellow',
                        '4': 'bright_red',
                        '5': 'red'
                    },
                    'task_types': {
                        'Action Item': {
                            'statuses': {
                                'Not Started':{
                                    'color': 'red',
                                    'icon': '(!)'
                                },
                                'Stopped': {
                                    'color': 'bright_red',
                                    'icon': '(.)'
                                },
                                'In Progress': {
                                    'color': 'bright_yellow',
                                    'icon': '(>)'
                                },
                                'Blocked': {
                                    'color': 'bright_red',
                                    'icon': '(X)'
                                },
                                'Completed': {
                                    'color': 'green',
                                    'icon': '(√)'
                                }
                            },
                        },
                        'Question': {
                            'statuses': {
                                'Unanswered':{
                                    'color': 'bright_cyan',
                                    'icon': '(?)'
                                },
                                'Answered': {
                                    'color': 'bright_green',
                                    'icon': '(a)'
                                }
                            }
                        }
                    }
}

COLORS = {
    'red':            Fore.RED,
    'yellow':         Fore.YELLOW,
    'green':          Fore.GREEN,
    'cyan':           Fore.CYAN,
    'blue':           Fore.BLUE,
    'magenta':        Fore.MAGENTA,
    'black':          Fore.BLACK,
    'white':          Fore.WHITE,

    'bright_red':     Fore.LIGHTRED_EX,
    'bright_yellow':  Fore.LIGHTYELLOW_EX,
    'bright_green':   Fore.LIGHTGREEN_EX, 
    'bright_cyan':    Fore.LIGHTCYAN_EX,
    'bright_blue':    Fore.LIGHTBLUE_EX,
    'bright_magenta': Fore.LIGHTMAGENTA_EX,
    'bright_black':   Fore.LIGHTBLACK_EX, 
    'bright_white':   Fore.LIGHTWHITE_EX
}





# Set config file
config_path = os.path.expanduser("~/.config/scrumy/").replace("\\", "/")
if os.path.exists(config_path) == False:
    print(f"Initializing config path at '{config_path}'")
    os.makedirs(config_path)
config_path = os.path.join(config_path, 'settings.json').replace("\\", "/")
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
missing_settings = []
for key in DEFAULT_SETTINGS:
    if key not in settings:
        print(f"The settings file is missing {key}! Restoring defaults...")
        settings[key] = DEFAULT_SETTINGS[key]
        missing_settings.append(key)
if len(missing_settings) > 0:
    with open(config_path, 'w') as file:
        print(f"Saving settings: {missing_settings}")
        json.dump(settings, file, indent=4)





# Set master folder
storage_folder = os.path.expanduser(settings['storage_path']).replace("\\", "/")

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
parser.add_argument('-r', '--rename', nargs=1, type=str, metavar='O', action='store', help='Rename [O]. (Will prompt for new name)')
parser.add_argument('-d', '--delete', nargs=1, type=str, metavar='N', action='store', help='Delete [N].')
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


def date_difference(first_date, second_date) -> int:
    try:
        output = second_date - first_date
        output = output.days
        assert type(output) == int
        return output
    except AssertionError:
        print("Date difference calculation did not return an integer!")
    except Exception as e:
        print("Date difference failed!")
        print(e)
        return None

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

def meeting_name_validation(meeting_name):
    """Check if the meeting name is valid.
    Returns a clean meeting name if valid, False otherwise."""
    meeting_name = meeting_name.strip()
    if meeting_name == None or len(meeting_name) < 1:
        print("No name was supplied.")
        return False
    if meeting_name == new_meeting_prompt:
        print(f"'{meeting_name}' is the trigger for a new meeting and is not allowed to be a meeting's name.")
        return False
    if ' ' in meeting_name or '\t' in meeting_name:
        if questionary.confirm("There are white spaces in this name. These will be replaced with underscores (_). Do you want to proceed?", default=True, auto_enter=False).ask():
            meeting_name = meeting_name.replace(' ', '_')
            meeting_name = meeting_name.replace('\t', '_')
        else:
            return False
    if meeting_name in get_meeting_folders():
        print(f"'{meeting_name}' already exists!")
        return False
    return meeting_name


def create_new_meeting(meeting_name=None) -> str:
    """Create a new meeting (ask for name if one wasn't given).
    Returns meeting name if successful"""

    if meeting_name == None:
        meeting_name = questionary.text("Enter the new meeting's name:").ask()
    
    # Data validation
    meeting_name = meeting_name_validation(meeting_name)
    if meeting_name == False or meeting_name == None:
        print("Aborting...")
        sys.exit(1)
    
    # Set meeting details
    description = questionary.text("Enter meeting description: ").ask()
    cadence = questionary.select("Select cadence (Meeting occurs ever [N] weeks): ", choices=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10','11', '12']).ask()
    if cadence == None or cadence == '':
        print("Aborting...")
        sys.exit(1)
    meeting_details = {
        'description': description,
        'cadence': int(cadence)
    }
    
    # Finally we can create the folder
    meeting_folder_path = os.path.join(storage_folder, meeting_name).replace("\\", "/")

    try:
        if os.path.exists(meeting_folder_path) == False:
            os.makedirs(meeting_folder_path)
            print(f"{meeting_name} directory created.")
        note_file_path = os.path.join(meeting_folder_path, 'Notes.txt').replace("\\", "/")
        if os.path.exists(note_file_path) == False:
            with open(note_file_path, 'w'):
                print("Notes.txt created.")
        task_file_path = os.path.join(meeting_folder_path, 'Tasks.json').replace("\\", "/")
        if os.path.exists(task_file_path) == False:
            with open(task_file_path, 'w') as file:
                json.dump({}, file, indent=4)
                print("Tasks.json created.")
        details_file = os.path.join(meeting_folder_path, 'Details.json').replace("\\", "/")
        if os.path.exists(details_file) == False:
            with open(details_file, 'w') as file:
                json.dump(meeting_details, file, indent=4)
                print("Details.json created.")
    except Exception as e:
        print("An error occurred while trying to create the folder or files...")
        print(e)
        sys.exit(1)
    return meeting_name

def render_meeting(meeting_name, description="", cadence=1):
    try:
        meeting_path = os.path.join(storage_folder, meeting_name).replace("\\", "/")
        assert os.path.exists(meeting_path)

        note_file = os.path.join(meeting_path, 'Notes.txt').replace("\\", "/")
        if os.path.exists(note_file) == False:
            with open(note_file, 'w') as file:
                print(f"{note_file} is missing! Creating blank note file...")
        with open(note_file, 'r') as file:
            notes = file.read()

        task_file = os.path.join(meeting_path, 'Tasks.json').replace("\\", "/")
        if os.path.exists(task_file) == False:
            with open(task_file, 'w') as file:
                print(f"{task_file} is missing! Creating blank task file...")
                json.dump({}, file, indent=4)
        with open(task_file, 'r') as file:
            tasks = json.load(file)

        #TODO: check for and delete completed tasks that have aged by 1 and reorder keys

        print((Fore.LIGHTWHITE_EX + meeting_name + Style.RESET_ALL).center(terminal_width, '─')) # Title
        print('    ' + Fore.LIGHTWHITE_EX + '[Notes]') # Notes header
        print(notes) # Notes
        print() # Padding
        print('    ' + Fore.LIGHTWHITE_EX + '[Tasks]') # Tasks header
        if len(tasks) == 0:
            print('None')
        else:
            for task in tasks:
                print(get_formatted_task(task, tasks, cadence=1)) # Tasks
        print() # Last padding

    except AssertionError:
        print(f"{meeting_name} not found in {storage_folder}")
        sys.exit(1)

def clean_tasks(tasks_dict: dict) -> dict:
    """Check for and remove completed tasks that have aged.
    Then reorder task indices (keys)"""
    pass


def index_data(current_dict: dict) -> list:
    """
    Return list of keys as int from data dict.
    This is to get around the JavaScript limitation of keys being strings
    """
    output = []
    for k in current_dict.keys():
        output.append(int(k))
    return output


def get_last_key(dictionary: dict) -> str:
    keys = list(dictionary.keys())
    return keys[-1]


def get_formatted_task(key, tasks, cadence) -> str:

    # Extract task details
    task = tasks[key]
    status = task['status']
    task_type = task['type']
    description = task['description']
    result = task.get('result', None)  # Default to None if result is not set
    result_str = f" -> {result}" if result else ""  # Include ': {result}' only if result is not None

    # Define bounds for some settings
    max_delinquency = get_last_key(settings['age_colors'])
    final_status = get_last_key(settings['task_types'][task_type]['statuses'])

    # Get color and icon from settings
    icon_color = COLORS[settings['task_types'][task_type]['statuses'][status]['color']]
    icon = settings['task_types'][task_type]['statuses'][status]['icon']

    # Get age and format
    age_days = date_difference(datetime.datetime.strptime(task['created_date'], '%Y-%m-%d').date(), datetime.datetime.now().date())
    if age_days is None:
        age_days = 0
    age_weeks = int(age_days / 7)
    if status == final_status:
        age_color = Fore.LIGHTBLACK_EX
        description = f"{Fore.LIGHTBLACK_EX}{description}{Style.RESET_ALL}"
    else:
        #TODO: description = get_formatted_description(description)
        age_delinquency = int(age_weeks / cadence) # how many times has the meeting passed
        if age_delinquency >= int(max_delinquency):
            age_color = get_age_color(max_delinquency)
        else:
            age_color = get_age_color(age_delinquency)




    # Format the task string
    task_formatted = f"{age_color}{key.rjust(2)}{Style.RESET_ALL} {icon_color}{icon}{Style.RESET_ALL} {description}{result_str} {age_color}({age_weeks}w){Style.RESET_ALL} "
    return task_formatted


def get_age_color(age_delinquency: int) -> str:
    """Takes an integer as the age factor. This should be how many meetings have passed.
    ie number of weeks divided by the cadence"""
    age_delinquency = str(age_delinquency)
    try:
        color_name = settings['age_colors'][age_delinquency]
        if color_name == '':
            output = ''
        else:
            output = COLORS[color_name]
    except Exception as e:
        print('Age coloring failed!')
        print(e)
        output = ''
    return output


def task_mode(meeting_name):
    """This is the task mode for the meeting.
    This is where the user can create and edit tasks."""
    meeting_path = os.path.join(storage_folder, meeting_name).replace("\\", "/")
    task_file = os.path.join(meeting_path, 'Tasks.json').replace("\\", "/")
    if os.path.exists(task_file) == False:
        print(f"{task_file} is missing!")
        return
    try:
        with open(task_file, 'r') as file:
            tasks_json = json.load(file)
    except Exception as e:
        print("An error occurred while trying to open the file...")
        print(e)
    task_list_formatted = []
    if len(tasks_json) > 0:
        for task_key in tasks_json:
            task_formatted = f"{task_key.rjust(2)} {settings['task_types'][tasks_json[task_key]['type']]['statuses'][tasks_json[task_key]['status']]['icon']} {tasks_json[task_key]['description']}"
            task_list_formatted.append(task_formatted)

    task_list_formatted.append('Add new task')
    user = questionary.select("Select task...", choices=task_list_formatted).ask()
    if user == 'Add new task':
        task_indies = index_data(tasks_json)
        if len(task_indies) > 0:
            next_key = max(task_indies) + 1
        else:
            next_key = 0
        
        new_task = create_new_task()
        if type(new_task) == dict:
            tasks_json[str(next_key)] = new_task
    
    elif user in task_list_formatted:
        task_index = str(task_list_formatted.index(user))
        list_of_statuses = list(settings['task_types'][tasks_json[task_index]['type']]['statuses'].keys())
        list_of_statuses.insert(-1, 'Delete')
        new_status = questionary.select("Update status to...", choices=list_of_statuses).ask()
        if new_status == None:
            return
        elif new_status == 'Delete':
            del tasks_json[task_index]
            print(f"Task #{task_index} was deleted.")
        else:
            tasks_json[task_index]['status'] = new_status
            # Check if the new_status is the last status in the list of statuses
            statuses = list(settings['task_types'][tasks_json[task_index]['type']]['statuses'].keys())
            if new_status == statuses[-1]:  # Compare with the last status
                user = questionary.text("Enter result (optional):").ask()
                tasks_json[task_index]['result'] = user
                # Set the completed_date to the current date
                tasks_json[task_index]['completed_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
    else:
        print("Invalid selection!")
        return
    try:
        with open(task_file, 'w') as file:
            json.dump(tasks_json, file, indent=4)
            print(f"Tasks updated in {task_file}")
    except Exception as e:
        print("An error occurred while trying to save the file...")
        print(e)


def create_new_task():
    """Create a new task for the meeting.
    This will have several prompts and return a task object as a dictionary."""
    task_object = {}
    try:
        task_object['type'] = questionary.select("Select task type...", choices=['Action Item', 'Question']).ask()
        assert task_object['type'] != None
        task_object['created_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
        task_object['completed_date'] = None
        task_object['status'] = list(settings['task_types'][task_object['type']]['statuses'].keys())[0]
        # task_object['icon'] = task_object['type']['statuses'][task_object['status']]['icon']
        task_object['description'] = questionary.text("Enter description:").ask()
        assert len(task_object['description'] ) > 0
        task_object['result'] = None
        return task_object
    except AssertionError:
        print("Cancelled task creation.")
        return None



def rename_meeting(old_name):
    """Rename a meeting folder. This will rename the folder"""
    old_meeting_path = os.path.join(storage_folder, old_name).replace("\\", "/")
    if os.path.exists(old_meeting_path) == False:
        print(f"{old_name} not found in {storage_folder}")
        sys.exit(1)
    try:
        new_name = questionary.text(f"Enter the new name for {old_name}:").ask()
        new_name = meeting_name_validation(new_name)
        if new_name == False or new_name == None:
            print("Aborting...")
            sys.exit(1)
        assert old_name != new_name
        new_meeting_path = os.path.join(storage_folder, new_name).replace("\\", "/")
        shutil.move(old_meeting_path, new_meeting_path)  # Use shutil.move to rename the folder
        print(f"{old_name} renamed to {new_name}.")
    except AssertionError:
        print(f"Invalid name: {new_name} is the same as {old_name}")
        sys.exit(1)
    except Exception as e:
        print("An error occurred while trying to rename the folder...")
        print(e)
        sys.exit(1)


def delete_meeting(meeting_name):
    """Delete the meeting folder and all its contents."""
    meeting_path = os.path.join(storage_folder, meeting_name).replace("\\", "/")
    if os.path.exists(meeting_path) == False:
        print(f"{meeting_name} not found in {storage_folder}")
        sys.exit(1)
    try:
        render_meeting(meeting_name)
        print(f"\n{Fore.LIGHTYELLOW_EX} Warning: This will delete the above meeting!")
        user = questionary.confirm(f"Are you sure you want to delete {meeting_name}?", default=False, auto_enter=False).ask()
        if user == False:
            print("Aborting...")
        elif user == True:
            shutil.rmtree(meeting_path)  # Use shutil.rmtree to delete non-empty directories
            print(f"{meeting_name} deleted.")
        else:
            print("Invalid choice!")
    except Exception as e:
        print("An error occurred while trying to delete the folder...")
        print(e)
        sys.exit(1)


def run_meeting(meeting_name):
    """This is the main meeting function.
    This will loop rendering the meetings then running the prompt process"""
    meeting_folders = get_meeting_folders()
    meeting_path = os.path.join(storage_folder, meeting_name).replace("\\", "/")
    assert os.path.exists(meeting_path)

    details_file = os.path.join(meeting_path, 'Details.json').replace("\\", "/")
    if os.path.exists(details_file) == False:
        with open(details_file, 'w') as file:
            print(f"{details_file} is missing! Creating plain details file...")
            json.dump({'description': 'Cadence: Weekly', 'cadence': 1}, file, indent=4)
    with open(details_file, 'r') as file:
        details = json.load(file)
    
    description = details['description']
    cadence = details['cadence']

    try:
        assert meeting_name in meeting_folders
        print('\n' * 4) # add some blank lines for visual padding
        while True:
            render_meeting(meeting_name, description=description, cadence=cadence)
            meeting_command_prompt(meeting_name)
    except AssertionError:
        print(f"Invalid meeting name: {meeting_name}")
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)


def clear_screen():
    """Clear the screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def meeting_command_prompt(meeting_name):
    """This is the command prompt for the meeting.
    This is where the user will enter commands to edit and interact with the meeting."""
    try:
        user = input("Scrumy> ").strip()
        if user.lower() in settings['scrumy_commands']['notes_mode']:
            edit_notes(meeting_name)
            clear_screen()
        elif user.lower() in settings['scrumy_commands']['tasks_mode']:
            task_mode(meeting_name)
        elif user.lower() in settings['scrumy_commands']['exit']:
            print("Exiting...")
            sys.exit(0)
        elif user.lower() in settings['scrumy_commands']['help']:
            print("Scrumy commands:")
            for command in settings['scrumy_commands']:
                print(f"    {command}: {settings['scrumy_commands'][command]}")
            questionary.press_any_key_to_continue().ask()
        else:
            print(f"Invalid command: '{user}'\nTry '?' for help.")
            questionary.press_any_key_to_continue().ask()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)

def edit_notes(meeting_name):
    """This will open the notes file in the default editor."""
    meeting_path = os.path.join(storage_folder, meeting_name).replace("\\", "/")
    note_file = os.path.join(meeting_path, 'Notes.txt').replace("\\", "/")
    if os.path.exists(note_file) == False:
        print(f"{note_file} is missing!")
        return
    try:
        editor = None
        for editor_name in settings['editors']:
            if shutil.which(editor_name) is not None:
                editor = editor_name
                break
        if editor is None:
            editor = os.environ.get('EDITOR') or 'notepad'  # Fallback to default editor if none found or notepad as a last resort
        os.system(f"{editor} {note_file}")
    except Exception as e:
        print("An error occurred while trying to open the file...")
        print(e)





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
        rename_meeting(args.rename[0])
    elif args.delete:
        delete_meeting(args.delete[0])
    elif args.name:
        run_meeting(args.name)
    
