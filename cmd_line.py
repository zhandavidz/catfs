import argparse
from directory import DirectoryTree

def parse_command(command):
    """Parses a command string into a list of arguments."""
    parser = argparse.ArgumentParser(description="Command parser")
    parser.add_argument('args', nargs=argparse.REMAINDER, help="Command arguments")
    return parser.parse_args(command.split()).args

def command_prompt():
    """Starts the command prompt loop."""
    dt = DirectoryTree()
    
    # Set initial role (can be changed via command line argument)
    import sys
    role = "Admin"  # default role
    if len(sys.argv) > 1:
        role = sys.argv[1]

    dt.set_permissions(role)

    while True:
        try:
            user_input = input("catfs 🐱 ")
            if user_input.strip().lower() in {"exit", "quit"}:
                print("Exiting command prompt. Goodbye!")
                break
                
            args = parse_command(user_input)
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
            elif command == "put" and len(args) == 1:
                dt.put(args[0])
            elif command == "mkcby" and len(args) == 1:
                dt.mkcby(args[0])
            elif command == "prowl":
                dt.prowl()
            else:
                print("Invalid command or arguments. Available commands:")
                print("cat [cat_name] - View cat details")
                print("meow [cat_name] [property] [value] - Update cat properties")
                print("boop [cat_name] - Execute cat")
                print("rescue [cat_name] [permissions] - Create new cat")
                print("pawprint - Show current directory")
                print("copycat [cat_name] [new_cat_name] - Copy cat")
                print("recollar [cat_name] [new_name] - Rename cat")
                print("walk [new_location] - Change directory")
                print("adopted [cat_name] - Remove cat")
                print("carry [cat_name] - Try to carry cat")
                print("carrying - List carried cats")
                print("put [cat_name|all] - Drop cat(s)")
                print("mkcby [cubby_name] - Create directory")
                print("prowl - List directory contents")
                
        except KeyboardInterrupt:
            print("\nExiting command prompt. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    command_prompt()

