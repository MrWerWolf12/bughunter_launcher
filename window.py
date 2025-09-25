import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import minecraft_launcher_lib
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import mod_manager

# === Настройки лаунчера ===
MINECRAFT_DIR = r"C:\Users\mrwer\AppData\Roaming\.minecraft"
VERSION = "ForgeOptiFine 1.12.2"
JAVA_PATH = r"C:\Program Files\Java\jre1.8.0_361\bin\javaw.exe"
BACKGROUND_IMAGE = "background.jpg"
NICKS_FILE = "nicks.txt"

GAME_WIDTH = 1280
GAME_HEIGHT = 720

# === Работа с никами ===
def load_nicks():
    if os.path.exists(NICKS_FILE):
        with open(NICKS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def save_nick(nick):
    nicks = load_nicks()
    if nick not in nicks:
        nicks.append(nick)
        with open(NICKS_FILE, "w", encoding="utf-8") as f:
            for n in nicks:
                f.write(n + "\n")

# === Функции лаунчера ===
def open_minecraft_folder():
    if os.path.exists(MINECRAFT_DIR):
        subprocess.Popen(f'explorer "{MINECRAFT_DIR}"')
    else:
        messagebox.showerror("Ошибка", f"Папка {MINECRAFT_DIR} не найдена!")

def launch_game():
    username = nick_var.get().strip()
    version = entry_version.get().strip()
    if not username or not version:
        messagebox.showerror("Ошибка", "Введите ник и версию!")
        return

    save_nick(username)

    # Создаём окно прогресса модов
    progress_win = tk.Toplevel(root)
    progress_win.title("Проверка модов...")
    progress_win.geometry("400x80")
    tk.Label(progress_win, text="Проверка модов и докачка недостающих...").pack(pady=5)
    progress_bar = ttk.Progressbar(progress_win, length=350, mode="determinate")
    progress_bar.pack(pady=5)

    def update_progress(value):
        progress_bar['value'] = value
        progress_win.update_idletasks()

    # Проверка и докачка модов
    mod_manager.ensure_mods(progress_callback=update_progress)

    # Закрываем прогресс
    progress_win.destroy()

    # Запуск Minecraft
    options = {
        "username": username,
        "uuid": "00000000-0000-0000-0000-000000000000",
        "token": "0",
        "executablePath": JAVA_PATH,
        "gameArguments": [f"--width {GAME_WIDTH}", f"--height {GAME_HEIGHT}"]
    }
    try:
        minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(
            version, MINECRAFT_DIR, options
        )
        if minecraft_command:
            subprocess.Popen(minecraft_command, cwd=MINECRAFT_DIR)
            root.destroy()
    except Exception as e:
        messagebox.showerror("Ошибка запуска", str(e))

# === Интерфейс лаунчера ===
root = tk.Tk()
root.title("Майнкрафт Лаунчер")
win_width, win_height = 700, 400
screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
x = (screen_width - win_width) // 2
y = (screen_height - win_height) // 2
root.geometry(f"{win_width}x{win_height}+{x}+{y}")
root.resizable(False, False)

# Фон
if os.path.exists(BACKGROUND_IMAGE):
    bg_img = Image.open(BACKGROUND_IMAGE).resize((win_width, win_height))
    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Нижняя панель
bottom_frame = tk.Frame(root, bg="#24304e", bd=5)
bottom_frame.pack(side="bottom", fill="x", padx=5, pady=5)

# Поле выбора ника
tk.Label(bottom_frame, text="Ник:", font=("Segoe UI", 11), bg="#24304e", fg="white").pack(side="left", padx=5)
nick_var = tk.StringVar()
nick_combobox = ttk.Combobox(bottom_frame, textvariable=nick_var, font=("Segoe UI", 11), width=15)
nick_combobox['values'] = load_nicks()
nick_combobox.pack(side="left", padx=5)

# Поле для версии
tk.Label(bottom_frame, text="Версия:", font=("Segoe UI", 11), bg="#24304e", fg="white").pack(side="left", padx=5)
entry_version = tk.Entry(bottom_frame, font=("Segoe UI", 11), width=20)
entry_version.insert(0, VERSION)
entry_version.pack(side="left", padx=5)

# Кнопки справа
btn_open_folder = tk.Button(bottom_frame, text="Папка Minecraft", font=("Segoe UI", 11),
                            bg="#4caf50", fg="white", command=open_minecraft_folder)
btn_open_folder.pack(side="right", padx=5)

btn_launch = tk.Button(bottom_frame, text="Запустить", font=("Segoe UI", 11, "bold"),
                       bg="#356efb", fg="white", command=launch_game)
btn_launch.pack(side="right", padx=5)

root.mainloop()
