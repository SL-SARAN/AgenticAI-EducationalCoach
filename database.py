# database.py
import sqlite3
import os

DB_FILE = "learning_coach.db"


def connect_db():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Enable dict-like access on rows
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_db():
    """Create all tables if they do not exist. Run on app startup."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS learners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL DEFAULT 'Learner',
            level TEXT NOT NULL DEFAULT 'Beginner',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS learning_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id INTEGER NOT NULL,
            goal_text TEXT NOT NULL,
            start_date DATE NOT NULL,
            deadline DATE NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            FOREIGN KEY (learner_id) REFERENCES learners(id)
        );

        CREATE TABLE IF NOT EXISTS learning_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER NOT NULL,
            topic_name TEXT NOT NULL,
            target_date DATE,
            completed INTEGER NOT NULL DEFAULT 0,
            score INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (goal_id) REFERENCES learning_goals(id)
        );

        CREATE TABLE IF NOT EXISTS mistake_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id INTEGER NOT NULL,
            mistake_type TEXT NOT NULL,
            count INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (learner_id) REFERENCES learners(id)
        );

        CREATE TABLE IF NOT EXISTS progress_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            score INTEGER NOT NULL DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (learner_id) REFERENCES learners(id)
        );
    """)

    # Ensure a default learner (id=1) always exists
    existing = cursor.execute("SELECT id FROM learners WHERE id = 1").fetchone()
    if not existing:
        cursor.execute("INSERT INTO learners (name, level) VALUES ('Learner', 'Beginner')")

    conn.commit()
    conn.close()


def execute_query(query, params=()):
    """Execute a write query (INSERT/UPDATE/DELETE). Returns lastrowid."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id


def fetch_query(query, params=()):
    """Execute a read query (SELECT). Returns list of sqlite3.Row objects."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows
