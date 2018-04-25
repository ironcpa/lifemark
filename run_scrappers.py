import sys
import os
sys.path.append("scrapper")
import si_com_nfl_main_reader
import si_com_nfl_peter_reader


def remove_old_files():
    dir_name = 'static/gen'

    if not os.path.isdir(dir_name):
        return

    files = [f for f in os.listdir(dir_name)]
    for f in files:
        os.remove(f)


def main():
    remove_old_files()
    si_com_nfl_main_reader.main()
    si_com_nfl_peter_reader.main()


if __name__ == '__main__':
    main()
