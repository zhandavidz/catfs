from cmd_line import command_prompt
import argparse

cur_dir = "/"

def get_dir():
    return cur_dir

def main():

    parser = argparse.ArgumentParser(description="CatFS command parser")
    parser.add_argument("ls", nargs="*", help="List the cats and rooms in the current room")



    command_prompt(get_prefix=get_dir)

if __name__ == "__main__":
    main()