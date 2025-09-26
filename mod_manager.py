import os
import requests

# Папка Minecraft
MINECRAFT_DIR = r"C:\Users\mrwer\AppData\Roaming\.minecraft"
MODS_DIR = os.path.join(MINECRAFT_DIR, "mods")


REPO = "MrWerWolf12/bughunter_launcher"
BRANCH = "main"

def ensure_mods(progress_callback=None):
    """
    Проверяет список модов в GitHub-репозитории и скачивает недостающие .jar файлы.
    """
    if not os.path.exists(MODS_DIR):
        os.makedirs(MODS_DIR)

    print(f"[Mod Manager] Получаем список файлов из {REPO}/mods...")
    api_url = f"https://api.github.com/repos/{REPO}/contents/mods?ref={BRANCH}"
    response = requests.get(api_url)
    response.raise_for_status()
    files = response.json()

    # Оставляем только jar
    jar_files = [f for f in files if f["name"].endswith(".jar")]

    total_files = len(jar_files)
    downloaded = 0

    for f in jar_files:
        target_path = os.path.join(MODS_DIR, f["name"])
        if os.path.exists(target_path):
            print(f"[Mod Manager] Уже есть: {f['name']}")
            continue

        print(f"[Mod Manager] Скачиваем: {f['name']}...")
        download_url = f["download_url"]
        r = requests.get(download_url)
        r.raise_for_status()
        with open(target_path, "wb") as out_file:
            out_file.write(r.content)

        downloaded += 1
        if progress_callback and total_files > 0:
            progress_callback(int(downloaded / total_files * 100))

    print("[Mod Manager] Проверка завершена, недостающие моды загружены.")
