import logging
import os
import shutil
import subprocess
import time
from datetime import date as dt
from pathlib import Path
from re import sub

logging.basicConfig(filename=f"F:/logs/log_backup_{time.strftime('%Y_%m_%d')}.txt",
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# copy files or copy last file
def copy_file(path_destination, path_resource):
    # copy files
 
        # sorted_files вернет отсортированный список кортежей из имени файла и даты создания (отсортированы по
        # дате создания
        sorted_tuple = sorted_files(path_resource)
        # проверит если файлов больше 31 то оставит 15 файлов
        if len(sorted_tuple) > 31:
            del_extra_files(path_resource, sorted_tuple[-15:])
        # копирование 2 последних файлов
        shutil.copy(path_resource / sorted_tuple[0][0], path_destination)


# функция сортировки файлов на ресурсе (необходимо чтоб забрать самый новый файл)
def sorted_files(path_resource):
    # создаем словарь, в котором ключом будет название файла/папки, значение дата создания(изменения)
    dict_files = {}
    for item in path_resource.glob("*"):
        dict_files[item.name] = os.path.getctime(item)
    # сортировка по дате создания и возвращение отсортированного списка
    return sorted(dict_files.items(), key=lambda x: x[1], reverse=True)


# функция для удаления лишних файлов с ресурса
def del_extra_files(res_path, list_tuple_files):
    for file in list_tuple_files:
        os.remove(res_path / file[0])


# функция для бекапа папок через 7zip
def zip_use(path, name_backup, path_my_resource):
    path_7z = Path("F:/7-Zip/7z.exe")
    command = f"{path_7z} a -tzip -ssw -mx1 -r0 {path_my_resource}\\" \
              f"{name_backup}_{time.strftime('%Y_%d_%m')}.7z {path}"
    logging.debug(f'Create command: "{command}"')
    try:
        start_time = time.time()
        logging.debug(f'Start run command : {start_time}')
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout
        time_delta = time.time() - start_time
        logging.debug(f'Finished command, time: "{time_delta}" sec.')
        logging.debug(f'Result command: "{output}"')
    except Exception:
        logging.exception(f"meh - im fuckedup with {path}")

def del_folder(path):
    for sub in path.iterdir():
        if 'syscon' in sub.name:
            continue
        else:
            if sub.is_dir():
                del_folder(sub)
            else:
                try:
                    sub.unlink()
                except PermissionError:
                    subprocess.run(f"takeown /F {sub} /A", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    subprocess.run(f"icacls", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    sub.unlink()

def main():
    logging.debug('Begin: ')
    # список путей откуда забирать бекапы
    list_paths = [
            #т.к. я забираю  бэкапы с win серверов то вписываю сюда пути вида
            # Path("//<ip>/path/to/folder"),
    ]
    

    current_date = time.strftime('%d-%m-%Y')
    if not os.path.exists(f"F:/backup/{current_date}"):
        path_folder=f"F:/backup/{current_date}"
        os.makedirs(path_folder)
    for path in list_paths:
        logging.debug(f"Start backup {path}")
        path_my_resource = Path(f"F:/backup/{current_date}")
        if '10.55.112.7' in str(path):
            copy_file(path_my_resource,path)
        else:
            name_backup = sub(r"[^a-zA-Z\d]{1,3}", "_", str(path)).lower()
            if "avserver1" in str(path):
                name_backup = sorted_files(path)[0][0]

            zip_use(path, name_backup, path_my_resource)



if __name__ == "__main__":
    main()
