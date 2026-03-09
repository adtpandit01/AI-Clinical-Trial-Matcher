import sqlite3
from pathlib import Path

# Database file path
DB_PATH = Path("clinical_matcher.db")


def get_connection():
    """
    Creates and returns a database connection.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows dict-like row access
    return conn


def init_db():
    """
    Initializes all required tables.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # TRIALS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nct_id TEXT UNIQUE,
        title TEXT,
        condition TEXT,
        phase TEXT,
        eligibility_text TEXT,
        last_fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # EVALUATIONS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        trial_id INTEGER,
        patient_json TEXT,
        match_score REAL,
        confidence_score REAL,
        final_status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(trial_id) REFERENCES trials(id)
    )
    """)

    # AUDIT LOGS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evaluation_id INTEGER,
        agent_name TEXT,
        input_snapshot TEXT,
        output_snapshot TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(evaluation_id) REFERENCES evaluations(id)
    )
    """)

    # FEEDBACK TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evaluation_id INTEGER,
        user_id INTEGER,
        override_decision TEXT,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(evaluation_id) REFERENCES evaluations(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()