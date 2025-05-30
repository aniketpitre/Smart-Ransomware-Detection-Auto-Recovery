import time
import os
import shutil
import logging
import threading
import zipfile
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from restore import restore_latest_backup
from email_utils import send_email_alert

WATCH_DIR = "data"
QUARANTINE_DIR = "quarantine"
SUSPICIOUS_EXTENSIONS = [".locked", ".encrypted", ".enc"]
LOG_FILE = "logs/activity.log"

observer = None
processed_files = set()  # To avoid duplicate triggers

class RansomwareHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        self.handle_event(event)

    def on_modified(self, event):
        if event.is_directory:
            return
        self.handle_event(event)

    def handle_event(self, event):
        filename = os.path.basename(event.src_path)
        ext = os.path.splitext(filename)[1].lower()

        if ext in SUSPICIOUS_EXTENSIONS and not is_from_backup(event.src_path):
            if filename in processed_files:
                return  # Avoid duplicate action
            processed_files.add(filename)

            logging.critical(f"[THREAT] Suspicious encrypted file detected: {filename}")
            send_email_alert("🚨 Ransomware Detected",
                             f"Suspicious file `{filename}` detected.\n"
                             "Quarantining and restoring...")
            quarantine_data()

            # Do the restore + restart in a separate thread
            threading.Thread(
                target=lambda: restore_latest_backup(on_restore_callback=restart_watcher),
                daemon=True
            ).start()

def is_from_backup(path):
    return "backups" in path or "snapshot" in path

def quarantine_data():
    if not os.path.exists(QUARANTINE_DIR):
        os.makedirs(QUARANTINE_DIR)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    dest = os.path.join(QUARANTINE_DIR, f"quarantine_{timestamp}")

    zip_quarantine_folder(WATCH_DIR, dest)

    logging.warning(f"[QUARANTINE] Data zipped and moved to {dest}.zip")

def zip_quarantine_folder(source_folder, dest_folder):
    zip_path = f"{dest_folder}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, source_folder))
    logging.info(f"[QUARANTINE] Folder {source_folder} has been zipped to {zip_path}")

def start_watcher():
    global observer
    event_handler = RansomwareHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=True)
    observer.start()
    print("[WATCHER] 🔄 Watcher is now ACTIVE.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def restart_watcher():
    global observer
    print("[WATCHER] ♻️ Restarting watcher...")
    if observer and observer.is_alive():
        observer.stop()
        observer.join()
    time.sleep(1)
    threading.Thread(target=start_watcher, daemon=True).start()
