import os
import shutil
from datetime import datetime
import crypto_utils
import logging
from email_utils import send_email_alert

SOURCE = "data"
LOG_FILE = "logs/activity.log"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

def create_local_backup(initial=False):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    snapshot_name = f"snapshot_{timestamp}"
    snapshot_folder = os.path.join("backups", snapshot_name)

    shutil.copytree(SOURCE, snapshot_folder)
    print(f"[BACKUP] 📂 Folder snapshot created at {snapshot_folder}")

    archive_path = shutil.make_archive(snapshot_folder, "zip", snapshot_folder)
    encrypted_path = crypto_utils.encrypt_file(archive_path)

    shutil.rmtree(snapshot_folder)
    os.remove(archive_path)

    print(f"[BACKUP] 🔒 Encrypted backup created locally: {os.path.basename(encrypted_path)}")
    logging.info(f"Backup created and encrypted: {encrypted_path}")

    if not initial:
        send_email_alert("📦 Backup Complete", f"Encrypted backup created at {timestamp}")
