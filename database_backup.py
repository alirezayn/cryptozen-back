import os
import datetime
import subprocess
import django

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cryptozen.settings")
django.setup()

from django.conf import settings

def backup_database():
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_dir = os.path.join(BASE_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    db = settings.DATABASES["default"]
    db_name = db["NAME"]
    db_engine = db["ENGINE"]
    db_user = db.get("USER", "")
    db_pass = db.get("PASSWORD", "")
    db_host = db.get("HOST", "")
    db_port = db.get("PORT", "")

    backup_file = os.path.join(backup_dir, f"{db_name}_backup_{now}.sql")

    try:
        if "sqlite" in db_engine:
            print("📦 Backing up SQLite database...")
            subprocess.run(["cp", db_name, backup_file])
        elif "postgresql" in db_engine:
            print("📦 Backing up PostgreSQL database...")
            env = os.environ.copy()
            env["PGPASSWORD"] = db_pass
            subprocess.run([
                "pg_dump",
                "-h", db_host or "localhost",
                "-p", str(db_port or 5432),
                "-U", db_user,
                "-F", "c",
                "-b",
                "-v",
                "-f", backup_file,
                db_name
            ], env=env)
        elif "mysql" in db_engine:
            print("📦 Backing up MySQL database...")
            subprocess.run([
                "mysqldump",
                "-h", db_host or "localhost",
                "-P", str(db_port or 3306),
                "-u", db_user,
                f"--password={db_pass}",
                db_name
            ], stdout=open(backup_file, "w"))
        else:
            print("❌ Unsupported database engine.")
            return

        print(f"✅ Backup created successfully: {backup_file}")

        import glob, time
        now_ts = time.time()
        for f in glob.glob(os.path.join(backup_dir, "*.sql")):
            if os.stat(f).st_mtime < now_ts - 7 * 86400:
                os.remove(f)
                print(f"🗑️ Removed old backup: {f}")

    except Exception as e:
        print(f"❌ Backup failed: {e}")

if __name__ == "__main__":
    backup_database()
