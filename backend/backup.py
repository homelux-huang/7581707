#!/usr/bin/env python3
"""Offline private SQLite backup and verified restore. Never serve these files over HTTP."""
import argparse
import hashlib
import os
from pathlib import Path
import sqlite3


def verify_database(path):
    path = Path(path)
    if not path.is_file():
        raise ValueError("Backup does not exist")
    with sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True) as db:
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Database integrity check failed")
        tables = {x[0] for x in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {"admins", "students", "sessions", "shares", "adjustments"} <= tables:
            raise ValueError("Not a SUDU private database")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def backup_database(source, destination):
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve() or destination.exists():
        raise ValueError("Backup destination must be a new private file")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Create with owner-only permissions before writing credentials or student records.
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    try:
        with sqlite3.connect(f"file:{source.resolve()}?mode=ro", uri=True) as src, sqlite3.connect(destination) as dst:
            src.backup(dst)
        checksum = verify_database(destination)
        sidecar = Path(str(destination) + ".sha256")
        fd = os.open(sidecar, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as out:
            out.write(checksum + "\n")
        return checksum
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def restore_database(source, destination):
    source, destination = Path(source), Path(destination)
    expected = Path(str(source) + ".sha256").read_text().strip()
    if verify_database(source) != expected:
        raise ValueError("Backup checksum mismatch")
    # The current database is never overwritten. Operators stop the service and
    # choose a new file; revocation/deletion records after this backup need replay.
    return backup_database(source, destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("backup", "restore", "verify"))
    parser.add_argument("source")
    parser.add_argument("destination", nargs="?")
    args = parser.parse_args()
    if args.action == "verify":
        verify_database(args.source)
    else:
        if not args.destination:
            parser.error("A new private destination is required")
        (backup_database if args.action == "backup" else restore_database)(args.source, args.destination)
    print("PASS: private database integrity verified")
