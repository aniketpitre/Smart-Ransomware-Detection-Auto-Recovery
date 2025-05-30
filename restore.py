import os
import glob
import shutil
import crypto_utils
import logging
import time
from email_utils import send_email_alert

DATA_DIR = "data"
BACKUP_DIR = "backups"
LOG_FILE = "logs/activity.log"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

def restore_latest_backup(on_restore_callback=None):
    backup_files = sorted(glob.glob(os.path.join(BACKUP_DIR, "*.zip.enc")))
    if not backup_files:
        print("[RESTORE] No encrypted backups found.")
        logging.warning("[RESTORE] No encrypted backups found.")
        return

    latest = backup_files[-1]
    decrypted_path = crypto_utils.decrypt_file(latest)

    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
    os.makedirs(DATA_DIR, exist_ok=True)
    shutil.unpack_archive(decrypted_path, DATA_DIR)
    os.remove(decrypted_path)

    msg = f"[RESTORE] Restored from {os.path.basename(latest)}"
    print(msg)
    logging.info(msg)
    send_email_alert("✅ Restored", msg)

    if on_restore_callback:
        print("[RESTORE] Restarting watcher...")
        on_restore_callback()

def monitor_for_restore(on_restore_callback):
    print("[MONITOR] Monitoring for ransomware attack signals...")
    while True:
        trigger_path = os.path.join(DATA_DIR, "TRIGGER_RESTORE")
        if os.path.exists(trigger_path):
            print("[ALERT] Restore trigger detected!")
            logging.warning("Restore trigger detected. Starting restore.")
            restore_latest_backup(on_restore_callback=on_restore_callback)
            os.remove(trigger_path)
        time.sleep(5)
