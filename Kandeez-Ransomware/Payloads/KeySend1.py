import socket
import platform
import uuid
import os
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def get_machine_info():
    """Collect information about the machine."""
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


def send_encryption_key_to_atlas(encryption_key):
    """Send encryption key and machine info to MongoDB Atlas using pymongo."""
    uri = "mongodb+srv://gaourangbaria1002:rgAG1ac59Bvj28Wy@cluster0.jwx8zgp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster00"

    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        return

    db = client["test"]
    collection = db["encryptionkeys"]

    machine_info = get_machine_info()
    if "error" in machine_info:
        return

    # Get current local time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    document = {
        **machine_info,
        "encryption_key": encryption_key,
        "state": "secured",  # Default is now "secured"
        "sent_at": current_time  # Local date and time when the key was sent
    }

    try:
        result = collection.insert_one(document)
        print(f"Document inserted with ID: {result.inserted_id}")
        return result
    except Exception as e:
        print(f"Failed to insert document: {str(e)}")
        return


# Example usage
if __name__ == "__main__":
    sample_key = "sefeg"
    send_encryption_key_to_atlas(sample_key)
