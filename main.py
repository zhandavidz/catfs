from cmd_line import command_prompt
import sys

def main():
    if len(sys.argv) > 1:
        role = sys.argv[1]
        if role not in ["Visitor", "Volunteer", "Staff", "Admin"]:
            print("Invalid role. Must be one of: Visitor, Volunteer, Staff, Admin")
            sys.exit(1)
    command_prompt()
    # dt = DirectoryTree()
    # print(dt.root)

if __name__ == "__main__":
    main()