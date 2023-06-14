import json
import os
from pathlib import Path


class Config:
    PATH = Path("config.json")

    def __init__(self):
        if self.PATH.exists():
            with open(self.PATH) as f:
                self.file = json.load(f)
        else:
            self.file = {}

    def save(self):
        with open(self.PATH, "w") as f:
            json.dump(self.file, f, indent=2)

    def get(self, key, default=None):
        return os.environ.get(key) or self.get_or_write(key, default)

    def get_or_write(self, key, default):
        if key in self.file:
            return self.file[key]
        self.file[key] = default
        self.save()
        return default

    @property
    def token(self):
        return self.get("DISCORD_TOKEN")

    @property
    def prefix(self):
        return self.get("PREFIX", "!")

    @property
    def db_url(self):
        return self.get("DB_URL", "sqlite:///app.db")
