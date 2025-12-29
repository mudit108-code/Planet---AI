import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "flood_network.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS agents (
        agent_id TEXT PRIMARY KEY,
        name TEXT,
        role TEXT,
        trust REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        region TEXT,
        probability REAL,
        severity TEXT,
        timestamp TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        region TEXT,
        message TEXT,
        confidence REAL,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()
