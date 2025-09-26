import os
import subprocess
import customtkinter as ctk
from PIL import Image, ImageTk
import minecraft_launcher_lib
import mod_manager
import time

# === Настройки лаунчера ===
MINECRAFT_DIR = r"C:\Users\mrwer\AppData\Roaming\.minecraft"
VERSION = "ForgeOptiFine 1.12.2"
JAVA_PATH = r"C:\Program Files\Java\jre1.8.0_361\bin\javaw.exe"
BACKGROUND_IMAGE = "background.jpg"
NICKS_FILE = "nicks.txt"

GAME_WIDTH = 1280
GAME_HEIGHT = 720
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 580

# === Работа с никами ===
def load_nicks():
    if os.path.exists(NICKS_FILE):
        with open(NICKS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def save_nick(nick):
    nicks = load_nicks()
    if nick in nicks:
        nicks.remove(nick)
    nicks.append(nick)
    with open(NICKS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(nicks))

# === Функции лаунчера ===
def open_minecraft_folder():
    if os.path.exists(MINECRAFT_DIR):
        subprocess.Popen(f'explorer "{MINECRAFT_DIR}"')
    else:
        ctk.CTkMessagebox.show_error("Ошибка", f"Папка {MINECRAFT_DIR} не найдена!")

def animate_progress(progress_bar, target=100, speed=1):
    value = progress_bar.get() * 100
    if value < target:
        value += speed
        progress_bar.set(value / 100)
        root.after(50, animate_progress, progress_bar, target, speed)

def launch_game():
    username = nick_var.get().strip()
    version = version_var.get().strip()
    if not username or username == "Введите ник" or not version:
        ctk.CTkMessagebox.show_error("Ошибка", "Введите ник и версию!")
        return

    save_nick(username)

    # Плавно скрываем нижнюю панель
    bottom_frame.pack_forget()

    # Создаём прогрессбар
    progress_frame = ctk.CTkFrame(root, fg_color="#24304e", corner_radius=15)
    progress_frame.pack(side="bottom", fill="x", padx=20, pady=20)

    progress_label = ctk.CTkLabel(progress_frame, text="Проверка модов...", font=("Segoe UI", 12), fg_color="#24304e")
    progress_label.pack(pady=5)

    progress_bar = ctk.CTkProgressBar(progress_frame, width=WINDOW_WIDTH - 40)
    progress_bar.set(0)
    progress_bar.pack(pady=5)

    root.update_idletasks()

    # Проверка и докачка модов с обратным вызовом для прогресса
    def update_progress(value):
        progress_bar.set(value / 100)
        root.update_idletasks()

    mod_manager.ensure_mods(progress_callback=update_progress)

    # Плавная анимация до 100%, затем запуск игры
    animate_progress(progress_bar, target=100, speed=2)

    def start_minecraft():
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
            ctk.CTkMessagebox.show_error("Ошибка запуска", str(e))

    # Запускаем Minecraft через 1 сек после заполнения прогрессбара
    root.after(1500, start_minecraft)

# === Настройка UI ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.title("Minecraft Launcher")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

# Центрирование окна
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - WINDOW_WIDTH) // 2
y = (screen_height - WINDOW_HEIGHT) // 2
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
root.resizable(False, False)

# === Фон ===
if os.path.exists(BACKGROUND_IMAGE):
    bg_image = Image.open(BACKGROUND_IMAGE).resize((WINDOW_WIDTH, WINDOW_HEIGHT))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = ctk.CTkLabel(root, image=bg_photo, text="")  # text="" чтобы не отображался CTkLabel
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# === Нижняя панель с кнопками ===
bottom_frame = ctk.CTkFrame(root, fg_color="#24304e", corner_radius=15)
bottom_frame.pack(side="bottom", fill="x", padx=20, pady=20)

# Поле ввода ника
nick_var = ctk.StringVar()
nicks = load_nicks()
if nicks:
    nick_var.set(nicks[-1])  # Последний ник
else:
    nick_var.set("Введите ник")  # Подсказка

nick_entry = ctk.CTkEntry(bottom_frame, textvariable=nick_var, width=200)
nick_entry.pack(side="left", padx=10, pady=10)

def on_entry_focus_in(event):
    if nick_var.get() == "Введите ник":
        nick_var.set("")
nick_entry.bind("<FocusIn>", on_entry_focus_in)

def on_entry_focus_out(event):
    if not nick_var.get().strip() and not load_nicks():
        nick_var.set("Введите ник")
nick_entry.bind("<FocusOut>", on_entry_focus_out)

# Поле версии
version_var = ctk.StringVar(value=VERSION)
version_entry = ctk.CTkEntry(bottom_frame, textvariable=version_var, width=150, state="readonly")
version_entry.pack(side="left", padx=10, pady=10)

# Кнопка открытия папки
btn_folder = ctk.CTkButton(bottom_frame, text="Папка Minecraft", command=open_minecraft_folder, width=150)
btn_folder.pack(side="right", padx=10, pady=10)

# Кнопка запуска
btn_launch = ctk.CTkButton(bottom_frame, text="Запустить", command=launch_game, width=150)
btn_launch.pack(side="right", padx=10, pady=10)

root.mainloop()
