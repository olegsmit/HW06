import os
import re
from pathlib import Path
from normalize import normalize

dir_suf_dict = {"Images": ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.ico', '.bmp', '.webp', '.svg'],
                "Documents": [".md", ".epub", ".txt", ".docx", ".doc", ".ods", ".odt", ".dotx", ".docm", ".dox",
                              ".rvg", ".rtf", ".rtfd", ".wpd", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".xml"],
                "Archives": [".iso", ".tar", ".gz", ".7z", ".dmg", ".rar", ".zip"],
                "Audio": [".aac", ".m4a", ".mp3", "ogg", ".raw", ".wav", ".wma"],
                "Video": [".avi", ".flv", ".wmv", ".mov", ".mp4", ".webm", ".vob", ".mpg", ".mpeg", ".3gp"],
                "PDF": [".pdf"],
                "HTML": [".html", ".htm", ".xhtml"],
                "EXE_MSI": [".exe", ".msi"],
                "PYTHON": [".py", ".pyw"]}


def normalize(name: str) -> str:
    CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
    TRANSLATION = (
    "a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
    "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "u", "ja", "je", "ji", "g")

    trans = {}
    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        trans[ord(c)] = l
        trans[ord(c.upper())] = l.upper()
    t_name = name.translate(trans)
    t_name = re.sub(r'\W', '_', t_name)
    return t_name


def move_file(dir_p: Path, path_file: Path):
    """
    Создается папка с названием группы расширений.
    Перемещается текущий файл в созданную папку.
    :param dir_p: объект Path для создания папки.
    :param path_file: объект Path содержащий путь к файлу.
    """
    dir_p.mkdir(exist_ok=True)
    if (Path(dir_p) / path_file.name).exists():
        path_file.rename(dir_p.joinpath(f'{path_file.name[0:-len(path_file.suffix)]}_c{path_file.suffix}'))
        print(f"Возможно дубликат: {path_file.name}")
    else:
        path_file.rename(dir_p / path_file.name)


def extension_comparison(curr_dir: Path, path_file: Path, suf: str) -> bool:
    """
    Выполняется проверка, входит ли расширение текущего файла
    хотя бы в одну из групп представленных в словаре. Если входит -
    возвращается True, нет - False.
    :param curr_dir: объект Path с путем к директории проверки.
    :param path_file: объект Path с путем к текущему файлу.
    :param suf: строка, содержащая ключ из словаря с группами расширений.
    :return: True или False, в зависимости от результатов проверки.
    """
    if path_file.suffix in dir_suf_dict[suf]:
        move_file(Path(curr_dir) / suf, path_file)
        return True
    return False


def name_normalize(root: str, file: str) -> Path:
    """
    Нормализации (приведение к нужному виду, то есть, в данном случае
    замена кириллицы на латинские буквы).
    Переименование текущего файла в соответствии с результатами нормализации.
    :param root: строка с путем к текущему файлу.
    :param file: имя текущего файла с расширением.
    :return: объект Path с путем к переименованному файлу.
    """
    path_file = Path(root) / file
    normalize_n = f"{normalize(path_file.name[0:-len(path_file.suffix)])}{path_file.suffix}"
    path_file = path_file.rename(Path(root) / normalize_n)
    return path_file


def remove_dir(subdir: list):
    """
    Удаление пустых директорий, которые остались
    после перемещения из них файлов при сортировке.
    :param subdir: список с абсолютными путями к удаляемым директориям.
    """
    for path in subdir:
        if len(os.listdir(path)) > 0 or Path(path).name in dir_suf_dict:
            continue
        Path(path).rmdir()


def sort_func(path_d: str) -> tuple:
    """
    Сортировка файлов на основе расширения, а также вхождении
    расширения в одну из групп из словаря.
    Создаются списки с начальными поддиректориями в директории сортировки.
    Нормализация (замена кириллицы на латиницу) имен файлов.
    Проверка принадлежности расширения файла к одной из групп словаря.
    Перемещение в соответствии с принадлежностью к группе или, если принадлежности
    к группе не найдено, в папку "Other".
    Удаление пустых папок после сортировки.
    :param path_d: строка содержащая путь к директории для сортировки.
    :return: кортеж из списков с распознанными и не распознанными расширениями.
    """
    curr_dir = Path(path_d)
    subdir = []
    known_extensions, unknown_extensions = set(), set()
    for root, dirs, files in os.walk(path_d):
        for d in dirs:
            if not d:
                continue
            subdir.append(f"{curr_dir / d}")
        for file in files:
            path_file = name_normalize(root, file)
            ex_comp = False
            for suf in dir_suf_dict:
                ex_comp = extension_comparison(curr_dir, path_file, suf)
                if ex_comp:
                    known_extensions.add(path_file.suffix)
                    break
            if not ex_comp:
                move_file(Path(curr_dir) / "Other", path_file)
                unknown_extensions.add(path_file.suffix)

    remove_dir(subdir)
    return list(known_extensions), list(unknown_extensions)


def main():
    """
    Запрос у пользователя директории для сортировки файлов.
    Проверка директории на существование.
    Запуск функции сортировки с передачей полученного от пользователя пути.
    Проверка количества элементов в возвращенных словарях. Если кол-во элементов
    меньше или равно 0, сообщение не печатается. Если больше нуля, то
    выводиться в терминал список полученный после работы функции сортировки.
    """
    known, unknown = "", ""
    path_d = input('[+] Введите путь к директории для сортировки: ')
    if not Path(path_d).exists():
        print('[-] Директории не существует')
    else:
        known, unknown = sort_func(path_d)

    if len(known) >= 0:
        print(f"\nРаспознанные расширения:\n{known}")
    if len(unknown) >= 0:
        print(f"Не распознанные расширения:\n{unknown}")

    print('[!] Сортировка завершена')


if __name__ == "__main__":
    main()