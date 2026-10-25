"""Lokal lagring utan nätverksberoende."""
import json
import sqlite3
from pathlib import Path

class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS saved (id INTEGER PRIMARY KEY, name TEXT NOT NULL, data TEXT NOT NULL)')

    def get(self, key, default=None):
        row = self.db.execute('SELECT value FROM settings WHERE key=?', (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def set(self, key, value):
        with self.db:
            self.db.execute('INSERT OR REPLACE INTO settings VALUES (?,?)', (key, json.dumps(value)))

    def save(self, name, data):
        with self.db:
            self.db.execute('INSERT INTO saved(name,data) VALUES (?,?)', (name, json.dumps(data)))

    def saved(self):
        return [(i, name, json.loads(data)) for i, name, data in self.db.execute('SELECT * FROM saved ORDER BY id DESC')]

    def delete(self, identifier):
        with self.db:
            self.db.execute('DELETE FROM saved WHERE id=?', (identifier,))
