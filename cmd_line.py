import argparse

def parse_command(command):
    """Parses a command string into a list of arguments."""
    parser = argparse.ArgumentParser(description="Command parser")
    parser.add_argument('args', nargs=argparse.REMAINDER, help="Command arguments")
    return parser.parse_args(command.split()).args

def command_prompt():
    """Starts the command prompt loop."""
    while True:
        try:
            user_input = input("catfs 🐱 ")
            if user_input.strip().lower() in {"exit", "quit"}:
                print("Exiting command prompt. Goodbye!")
                break
            parsed_input = parse_command(user_input)
            print(f"Parsed command: {parsed_input}")
        except KeyboardInterrupt:
            print("\nExiting command prompt. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")