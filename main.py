from cmd_line import command_prompt
from commands import command_handlers

tree = {
    "current_dir": [],
    "get_dirname": lambda dirname: f"/{'/'.join(dirname)}",
    "data": {
        "replace this": "data stuff"
    }
}

def main():
    command_prompt(tree, command_handlers=command_handlers, get_prefix=lambda: tree["get_dirname"](tree["current_dir"]))

if __name__ == "__main__":
    main()