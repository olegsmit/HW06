import sys
from pathlib import Path
from normalize import normalize


folder_to_del = []
def move_file(target_path:Path, file:Path):
    file.replace(target_path / file.name)


def rm_dir(folder_for_scan:Path):
    for folder in folder_for_scan.glob('**'):
        folder_to_del.append(folder)
    del_folder = folder_to_del[::-1]
    for folder in del_folder[0:-1]:
        try:
            folder.rmdir()
        except OSError as err:
            print(err)
def scan(folder:Path):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('archives', 'video', 'audio', 'documents', 'images', 'OTHER'):
                FOLDERS.append(item)
                scan(item)
            continue

    for item in folder_for_scan.glob('**/*.*'):
        move_file(folder_for_scan, item)

    rm_dir(folder_for_scan)

    normalize()


# print(type(path))

# def move_file(target_path: Path, file: Path):
#     file.replace(target_path / file.name)
#
#
# for item in path.glob('**/*.*'):
#     move_file(path, item)
# #
# for item in path.glob('**/*.*'):
#     print(item.suffix, item.stem)
#
# folders_to_del = []
#
# for item in path.glob('**'):
#     folders_to_del.append(item)
#
# for item in folders_to_del[::-1]:
#     try:
#         item.rmdir()
#     except Exception as e:
#         print(e)

# print(folders_to_del[::-1])


# CATEGORIES = {'audio': ['.mp3', '.aiff']}

#
if __name__ == '__main__':

    try:
        if sys.argv[1]:
            folder_for_scan = Path(sys.argv[1])
            scan(folder_for_scan)
    except IndexError as err:
        print("Specify a folder for sorting")