import argparse
import os
import pickle
from directory import DirectoryTree, Role
import textwrap

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Cat Cafe File System")
    parser.add_argument("-c", "--cache", type=int, default=0, help="Cache size (not implemented yet)")
    parser.add_argument("-p", "--perm", type=str, default="visitor", choices=["visitor", "volunteer", "staff", "admin"], help="Role permission level")
    parser.add_argument("-n", "--name", type=str, required=True, help="Name of the cafe to open")
    return parser.parse_args()

def load_or_create_tree(name, role):
    """Load DirectoryTree from pickle file or create a new one."""
    pkl_path = os.path.join("cafes", f"{name}.pkl")
    if os.path.exists(pkl_path):
        with open(pkl_path, "rb") as f:
            tree = pickle.load(f)
            tree.role = role  # update role for this session
            return tree
    else:
        return DirectoryTree(name=name, role=role)

def command_prompt(dt):
    """Starts the command prompt loop."""
    while True:
        try:
            user_input = input("catfs 🐱 ")
            if user_input.strip().lower() in {"exit", "quit"}:
                print("Exiting command prompt. Goodbye!")
                break
                
            args = user_input.split()
            if not args:
                continue
                
            command = args[0].lower()
            args = args[1:]
            
            if command == "cat" and len(args) == 1:
                dt.cat(args[0])
            elif command == "meow" and len(args) == 3:
                dt.meow(args[0], args[1], args[2])
            elif command == "boop" and len(args) == 1:
                dt.boop(args[0])
            elif command == "rescue" and len(args) == 2:
                dt.rescue(args[0], args[1])
            elif command == "rescue" and len(args) == 1:
                dt.rescue(args[0])
            elif command == "find" and len(args) == 1:
                dt.find(args[0])
            elif command == "pawprint":
                dt.pawprint()
            elif command == "copycat" and len(args) == 2:
                dt.copycat(args[0], args[1])
            elif command == "recollar" and len(args) == 2:
                dt.recollar(args[0], args[1])
            elif command == "walk" and len(args) == 1:
                dt.walk(args[0])
            elif command == "adopted" and len(args) == 1:
                dt.adopted(args[0])
            elif command == "carry" and len(args) == 1:
                dt.carry(args[0])
            elif command == "carrying":
                dt.carrying()
            elif command == "put" and len(args) == 0:
                dt.put()
            elif command == "put" and len(args) == 1:
                dt.put(args[0])
            elif command == "mkcby" and len(args) == 1:
                dt.mkcby(args[0])
            elif command == "prowl":
                dt.prowl()
            elif command.lower() == "help" or command.lower() == "?":
                print("Available commands:")
                commands = [
                    ("help", "Show this help message"),
                    ("exit", "Exit the command prompt"),
                    ("cat [cat_name]", "View details of a cat"),
                    ("meow [cat_name] [property] [value]", "Update/set the `age`, `mood`, `date_found`, and `date_fed` of a cat"),
                    ("boop [cat_name]", "Execute the cat"),
                    ("rescue [cat_name] [permissions]", "Create new cat, permissions are optional"),
                    ("find [cat_name]", "Searches for cat in the whole cafe"),
                    ("pawprint", "Show the path it takes to get to the current cubby (pwd)"),
                    ("copycat [cat_name] [new_cat_name]", "... copy the cat"),
                    ("recollar [cat_name] [new_name]", "Rename the cat"),
                    ("walk [new_location]", "Walk to a different cubby"),
                    ("adopted [cat_name]", "Have some adopt the cat, removing it from our cubby"),
                    ("carry [cat_name]", "Try to carry cat so you can move it somewhere else, but cats are elusive and may run away"),
                    ("carrying", "List carried cats"),
                    ("put [cat_name]", "Drop cat(s) into current cubby, omit name to drop all"),
                    ("mkcby [cubby_name]", "Create a cubby (directory)"),
                    ("prowl", "List all cats and cubbies in current cubby")
                ]

                max_len = max(len(cmd[0]) for cmd in commands)
                for cmd, desc in commands:
                    print(f"  {cmd.ljust(max_len + 2)}{desc}")
            else:
                print("Invalid command or arguments. Run `help` to view available commands.")
                
        except KeyboardInterrupt:
            print("\nExiting command prompt. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main entry point for the program."""
    args = parse_args()
    role_map = {
        "visitor": Role.VISITOR,
        "volunteer": Role.VOLUNTEER,
        "staff": Role.STAFF,
        "admin": Role.ADMIN
    }
    dt = load_or_create_tree(args.name, role_map[args.perm])
    command_prompt(dt)

if __name__ == "__main__":
    main()

