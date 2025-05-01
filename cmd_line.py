# import argparse
from typing import Optional, Callable

# def parse_command(command):
#     """Parses a command string into a list of arguments."""
#     parser = argparse.ArgumentParser(description="Command parser")
#     parser.add_argument('args', nargs=argparse.REMAINDER, help="Command arguments")
#     return parser.parse_args(command.split()).args

def command_prompt(tree, get_prefix: Optional[Callable] = None, command_handlers: Optional[dict] = None):
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

            args = user_input.split()
            command = args[0]
            command_args = args[1:]

            if command_handlers and command in command_handlers:
                command_handlers[command](tree, command_args)
            else:
                print(f"Unknown command: {command}")
        except KeyboardInterrupt:
            print(exit_msg)
            break
        except Exception as e:
            print(f"Error: {e}")