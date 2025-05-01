def ls_command(tree, args: list[str]):
    print("Listing files:", tree.get("data", {}).keys())

def cd_command(tree, args: list[str]):
    if len(args) != 1:
        raise ValueError("Usage: cd <directory>")
    
    argument = args[0]
    if argument == "..":
        new_dir = tree["current_dir"][:-1]
    elif argument == "." or argument == "":
        pass
    elif argument[0:1] == "./":
        argument = argument[2:]
    elif argument[0:2] == "../":
        new_dir = tree["current_dir"][:-1]
        argument = argument[3:]

    if argument[0] == "/":
        new_dir = argument[1:].split("/")
    else:
        new_dir = tree["current_dir"] + argument.split("/")
    print("Changing directory to:", tree["get_dirname"](new_dir))
    tree["current_dir"] = new_dir

def pwd_command(tree, args: list[str]):
    print("Current directory:", tree["get_dirname"](tree["current_dir"]))

command_handlers = {
    "ls": ls_command,
    "cd": cd_command,
    "pwd": pwd_command
}
