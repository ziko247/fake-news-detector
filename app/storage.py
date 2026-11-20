"""Historique local du prototype RGPH."""

import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path


@contextmanager
def connection(path):
    with closing(sqlite3.connect(path)) as db, db:
        db.execute("PRAGMA foreign_keys = ON")
        yield db


def initialize(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with connection(path) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL
            );
            INSERT OR IGNORE INTO users(name) VALUES ('local');
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users,
                article TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY, analysis_id INTEGER NOT NULL REFERENCES analyses,
                snapshot TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS feedback (
                claim_id INTEGER NOT NULL REFERENCES claims, user_id INTEGER NOT NULL REFERENCES users,
                comment TEXT NOT NULL, PRIMARY KEY(claim_id, user_id)
            );
        """)


def save_analysis(path, article, response):
    with connection(path) as db:
        analysis_id = db.execute(
            "INSERT INTO analyses(user_id, article) SELECT id, ? FROM users WHERE name = 'local'",
            (article,),
        ).lastrowid
        db.executemany(
            "INSERT INTO claims(analysis_id, snapshot) VALUES (?, ?)",
            ((analysis_id, claim.model_dump_json()) for claim in response.affirmations),
        )
