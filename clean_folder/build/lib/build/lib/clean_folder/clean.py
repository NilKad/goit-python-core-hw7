import sys
# from genericpath import isdir
import os
import re
import shutil
import zipfile

path_for_sorting = ""

if len(sys.argv) > 1:
    path_for_sorting = sys.argv[1]
else:
    print("Need added path")
    sys.exit()


# path_for_sorting = "c:/My-project/goit/!python/1-python-core/for-sort/"

schemas = {
    "images": ["JPEG", "PNG", "JPG", "SVG", "GIF"],
    "video": ["AVI", "MP4", "MOV", "MKV"],
    "audio": ["MP3", "OGG", "WAV", "AMR"],
    "documents": [
        "DOC",
        "DOCX",
        "TXT",
        "PDF",
        "XLS",
        "XLSX",
        "PPT",
        "PPTX",
        "ODS",
        "ODT",
        "ODP",
    ],
    "archive": ["ZIP", "GZ", "TAR", "RAR"],
}

other_ext = "other"
folder_list_schemas = dict.keys(schemas)
found_famous_ext = set()
found_other_ext = set()


# result_files_list = dict.fromkeys(schemas, [])
result_files_list = {key: list() for key in schemas}
result_files_list[other_ext] = []


def transscript(str):
    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    TRANSLATION = (
        "a",
        "b",
        "v",
        "g",
        "d",
        "e",
        "e",
        "j",
        "z",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "r",
        "s",
        "t",
        "u",
        "f",
        "h",
        "ts",
        "ch",
        "sh",
        "sch",
        "",
        "y",
        "",
        "e",
        "yu",
        "ya",
        "je",
        "i",
        "ji",
        "g",
    )

    TRANS = {}

    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANS[ord(c)] = l
        TRANS[ord(c.upper())] = l.upper()
        # TRANS[ord(c.upper())] = l.capitalize()

    result = str.translate(TRANS)
    return result


def normalize(str):
    tr = transscript(str)
    new_tr = re.sub("[^\\w]", "_", tr)
    # print(f"tr: {tr}\tnew_tr: {new_tr}")
    return new_tr


def find_dir_from_ext(ext):
    if ext == "":
        return other_ext
    new_ext = ext
    if new_ext.startswith("."):
        new_ext = new_ext[1:].lower()
    for key, value in schemas.items():
        for it in value:
            if it.lower() == new_ext:
                return key
    return other_ext


def add_sufix_filename(full_path):
    if not os.path.exists(full_path):
        return full_path
    dir_name = os.path.dirname(full_path)
    full_file_name = os.path.basename(full_path)
    file_name, file_ext = os.path.splitext(full_file_name)
    count = 1

    while count < 10:
        new_file_name = f"{file_name}({count}){file_ext}"
        new_fullpath_file_name = os.path.join(dir_name, new_file_name)
        if os.path.exists(new_fullpath_file_name):
            count += 1
            continue
        return new_fullpath_file_name
    return full_path


def move_file(src, dst_fullpath):
    # if os.path.isdir(dst_fullpath):
    #     print("this Directory")
    # else:
    #     print("this File")

    dst_path = os.path.dirname(dst_fullpath)

    if not os.path.exists(dst_path):
        try:
            os.mkdir(dst_path)
        except:
            print(f"Cant create folder - {dst_path}")

    # dst_full_name = os.path.join(dst_path, os.path.basename(src))
    dst = dst_fullpath

    if os.path.exists(dst_fullpath):
        dst = add_sufix_filename(dst_fullpath)

    try:
        os.rename(src, dst)
    except OSError:
        print("OSError")


def del_el_fs(target):
    if not os.path.exists(target):
        return False
    if os.path.isdir(target):
        try:
            os.rmdir(target)
        except FileNotFoundError:
            print(f"! FileNotFoundError cant find directory {target}")
        except OSError:
            print(f"! OSError cant delete directory {target}")
        else:
            return True
    else:
        try:
            os.remove(target)
        except FileNotFoundError:
            print(f"! FileNotFoundError cant find directory {target}")
        except OSError:
            print(f"! OSError cant delete directory {target}")
        else:
            return True


def read_dir(files_list, src_path, dst_path):
    if not os.path.exists(src_path):
        return []
    current_dir_list = os.listdir(src_path)

    for elem_fs in current_dir_list:
        file_fullpath = os.path.join(src_path, elem_fs)

        if os.path.isfile(file_fullpath):
            file_name, file_ext = os.path.splitext(elem_fs)

            folder = find_dir_from_ext(file_ext)
            if folder == other_ext:
                found_other_ext.add(file_ext)
            else:
                found_famous_ext.add(file_ext)

            dst_categoty_path = os.path.join(dst_path, folder)

            if dst_categoty_path == src_path:
                # print(f"+++ skip this folder: {src_path}")
                return

            norm_file_name = normalize(file_name)
            norm_file_name_ext = norm_file_name + file_ext
            new_file_full_path = os.path.join(dst_categoty_path, norm_file_name_ext)

            if folder == "archive":
                unpack_to_dir = os.path.join(dst_categoty_path, norm_file_name)
                try:
                    shutil.unpack_archive(file_fullpath, unpack_to_dir)
                except IOError:
                    # print(Exception)
                    print("IOError unpack file")
                    del_el_fs(unpack_to_dir)
                    continue
                except zipfile.BadZipFile:
                    print("error unpack file BadFile")
                    del_el_fs(unpack_to_dir)
                    continue
                else:
                    new_file_full_path = unpack_to_dir
                finally:
                    del_el_fs(file_fullpath)

            move_file(file_fullpath, new_file_full_path)

        if os.path.isdir(file_fullpath):
            read_dir(files_list, file_fullpath, dst_path)

    if src_path != dst_path:
        del_el_fs(src_path)


read_dir(result_files_list, path_for_sorting, path_for_sorting)
print(f"Famous ext: {found_famous_ext}")
print(f"Other ext: {found_other_ext}")
