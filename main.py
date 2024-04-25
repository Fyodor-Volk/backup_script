import logging
import os
import sys
import shutil
import schedule
import time
import zipfile
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Создаем файл-хендлер для логирования
file_handler = logging.FileHandler('Backup/backup-log.log')
file_handler.setLevel(logging.DEBUG)

# Создаем форматтер для логирования
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Добавляем файл-хендлер к объекту логирования
logger.addHandler(file_handler)

def cleanup_backups():
    # Получаем текущую дату и время
    now = time.time()
    # Получаем список файлов в текущем каталоге
    files = os.listdir('Backup')
    # Проходим по каждому файлу
    for file in files:
        #Получаем относительный путь до файлов
        relative_path = os.path.basename('Backup') + '/' + file
        # Получаем время последнего изменения файла
        last_modified = os.path.getmtime(relative_path)
                # Если файл старше 7 дней, удаляем его
        if now - last_modified > 7 * 24 * 60 * 60:
            os.remove(relative_path)
            logger.info("Удалили последний файл бэкапа старше 7 дней" + file)


def backup_database():
    # Заменить 'source_folder' и 'destination_folder' на реальные пути к папкам
    source_folder = "db"
    destination_folder = "Backup"

    # Проверяем, существует ли папка с базой
    if not os.path.exists(source_folder):
        logger.error("Данная папка не существует")
        sys.exit()
    else:
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
            logger.info("Создали папку для резервного копирования")

    logger.info("Начало резервного копирования")
    # Создаем архив
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d_%H_%M_%S')
    with zipfile.ZipFile(destination_folder + '/' + os.path.basename(source_folder) + '_' + timestamp + '.zip', 'w', zipfile.ZIP_DEFLATED) as myzip:
        for folderName, subfolders, filenames in os.walk(source_folder):
            for filename in filenames:
                filePath = os.path.join(folderName, filename)
                myzip.write(filePath, os.path.relpath(filePath, source_folder))
                logger.info("Добавили файл '%s' в архив", filename)
    logger.info("Завершение резервного копирования")
    cleanup_backups()

schedule.every().day.at("10:46").do(backup_database)

while True:
    schedule.run_pending()
    time.sleep(60)
    logger.debug("Проверили наличие запланированных задач")

