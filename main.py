import sys
from pathlib import Path
import re
from normalize import normalize
import shutil


CATEGORIES = {}
folders_to_del = []

def load_categories() -> dict:

    with open("categories.txt") as file:
        for line in file:
            value: object
            key, *value = re.split(': |, ', line[:-1])
            CATEGORIES[key] = value


def move_file(file: Path):
    for key, value in CATEGORIES.items():
        if file.suffix in value:
            cr_dir = Path(folder_for_scan / key)
            cr_dir.mkdir(exist_ok=True, parents=True)
            file.replace(folder_for_scan / key / file.name)


def rm_dir(folder_for_rm: Path):

    try:
        folder_for_rm.rmdir()
    except OSError:
        print(f"Folder '{folder_for_rm}' is not empty.")


def unpack(file):

    for key, value in CATEGORIES.items():
        if key == 'archives':
            if file.suffix in CATEGORIES[key]:
                try:
                    foldder_for_file = Path(folder_for_scan / key / file.stem)
                    foldder_for_file.mkdir(exist_ok=True, parents=True)
                    shutil.unpack_archive(file, foldder_for_file)
                    file.unlink()

                except shutil.ReadError:
                    print(f'{file} - не вдалося розпакувати!')
                    foldder_for_file.rmdir()
                    return None
                break


def scan(folder: Path):

    load_categories()

    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('archives', 'video', 'audio', 'documents', 'images'):
                scan(item)
                rm_dir(item)
            continue
        else:
            normalize(item.name)
            if item.suffix in [".zip", ".gz", ".tar"]:
                unpack(item)
            else:
                move_file(item)



if __name__ == '__main__':

    try:
        if sys.argv[1]:
            folder_for_scan = Path(sys.argv[1])
            scan(folder_for_scan)
    except IndexError as err:
        print("Specify a folder for sorting")
