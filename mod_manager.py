import os
import requests
import zipfile
import io

MINECRAFT_DIR = r"C:\Users\mrwer\AppData\Roaming\.minecraft"
MODS_DIR = os.path.join(MINECRAFT_DIR, "mods")

# Прямая публичная ссылка на архив с модами
MODS_ARCHIVE_URL = "https://disk.yandex.ru/d/xEAvcbv0irqdDg/download"  # ссылка на скачивание архива

def ensure_mods(progress_callback=None):
    """Скачивает архив с модами и распаковывает его в папку mods, заменяя файлы при совпадении."""
    if not os.path.exists(MODS_DIR):
        os.makedirs(MODS_DIR)

    print("[Mod Manager] Скачиваем архив модов...")
    response = requests.get(MODS_ARCHIVE_URL, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    chunks = []

    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            chunks.append(chunk)
            downloaded += len(chunk)
            if progress_callback and total_size > 0:
                progress_callback(int(downloaded / total_size * 100))

    archive_data = io.BytesIO(b''.join(chunks))

    print("[Mod Manager] Распаковываем архив...")
    with zipfile.ZipFile(archive_data) as zip_ref:
        for member in zip_ref.namelist():
            filename = os.path.basename(member)
            if not filename:
                continue  # пропускаем папки
            source = zip_ref.open(member)
            target_path = os.path.join(MODS_DIR, filename)
            with open(target_path, "wb") as target:
                with source:
                    target.write(source.read())
    print("[Mod Manager] Все моды обновлены.")