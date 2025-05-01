import argparse
from typing import Optional, Callable

def parse_command(command):
    """Parses a command string into a list of arguments."""
    parser = argparse.ArgumentParser(description="Command parser")
    parser.add_argument('args', nargs=argparse.REMAINDER, help="Command arguments")
    return parser.parse_args(command.split()).args

def command_prompt(get_prefix: Optional[Callable] = None, parser: Optional[argparse.ArgumentParser] = None):
    exit_cmds  = {"exit", "quit"}
    exit_msg = "\nLeaving CatFS, goodbye!"
    while True:
        try:
            prefix = f"{get_prefix()} " if get_prefix else ""
            user_input = input(f"{prefix}🐱  ")
            user_input = user_input.strip()
            if not user_input:
                continue
            if user_input.strip().lower() in exit_cmds:
                print(exit_msg)
                break
            parsed_input = parser.parse_args(user_input.split()) if parser else user_input.split()
            print(f"Parsed command: {parsed_input}")
        except KeyboardInterrupt:
            print(exit_msg)
            break
        except Exception as e:
            print(f"Error: {e}")