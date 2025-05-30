import threading
import os
import logging
from dotenv import load_dotenv
from backup import create_local_backup
from watcher import start_watcher, restart_watcher
from restore import monitor_for_restore
from email_utils import send_email_alert
import time

# ✅ Save watcher start time to /tmp file
with open('/tmp/ransomware_watcher_start_time.txt', 'w') as f:
    f.write(str(int(time.time())))


load_dotenv()

if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/activity.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def schedule_cloud_backups():
    try:
        print("[SCHEDULER] ⏳ Creating a scheduled backup...")
        create_local_backup()
        print("[SCHEDULER] ✅ Backup created.")
        logging.info("Backup created successfully.")
    except Exception as e:
        logging.error(f"[BACKUP ERROR] Failed to create backup: {e}")
    
    threading.Timer(1800, schedule_cloud_backups).start()  # 30 mins

def start_all():
    print("[SYSTEM] 🚀 Smart Ransomware Watcher starting...")
    send_email_alert("🟢 Monitoring Started", "Monitoring of /data has started.")

    try:
        print("[SYSTEM] 📦 Creating initial backup...")
        create_local_backup(initial=True)
        print("[SYSTEM] ✅ Initial backup complete.")
        send_email_alert("📦 Initial Backup Complete", "Initial backup of /data completed.")
    except Exception as e:
        logging.error(f"[INITIAL BACKUP ERROR] {e}")
        send_email_alert("❌ Initial Backup Failed", f"Error creating initial backup: {e}")
        return

    print("[SYSTEM] ⏲️ Scheduling automatic backups every 30 minutes...")
    schedule_cloud_backups()

    print("[SYSTEM] 🔍 Starting initial watcher thread...")
    threading.Thread(target=start_watcher, daemon=True).start()

    print("[SYSTEM] 🛡️ Monitoring restore triggers...")
    monitor_for_restore(on_restore_callback=restart_watcher)

if __name__ == "__main__":
    start_all()
