#!/usr/bin/env python
import os
import gzip
import subprocess
from pathlib import Path
import environ

# Load env
env = environ.Env()
env.read_env('.env.local')

db_url = env('DATABASE_URL', default=None)
backup_file = Path('db_cluster-03-10-2025@01-36-22.backup.gz')

print(f"Backup file exists: {backup_file.exists()}")
print(f"Database URL configured: {bool(db_url)}")

# Extract the backup
if backup_file.exists():
    print("Extracting backup...")
    extract_path = backup_file.stem  # removes .gz
    
    with gzip.open(str(backup_file), 'rb') as f_in:
        with open(extract_path, 'wb') as f_out:
            f_out.write(f_in.read())
    
    print(f"✓ Extracted to: {extract_path}")
    print(f"✓ Extracted file size: {Path(extract_path).stat().st_size / 1024 / 1024:.2f} MB")
    
    # Now restore using pg_restore
    print("\nRestoring database...")
    try:
        # Try to restore with pg_restore (custom format)
        cmd = [
            'pg_restore',
            '--no-owner',
            '--clean',
            '-v',
            '-d', db_url,
            extract_path
        ]
        result = subprocess.run(cmd, capture_output=False, text=True)
        if result.returncode == 0:
            print("✓ Database restored successfully!")
        else:
            print(f"pg_restore exit code: {result.returncode}")
    except FileNotFoundError:
        print("⚠ pg_restore not found in PATH. Trying using Django...")
        # Fallback: use dbshell with SQL
        print("Note: pg_restore not available. You may need to restore manually via Supabase dashboard.")
else:
    print("ERROR: Backup file not found!")
