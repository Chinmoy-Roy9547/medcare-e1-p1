import sqlite3
from pathlib import Path

DB = Path(__file__).with_name("medcare.db")

def get_db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = get_db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS distribution_centers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, city TEXT
    );
    CREATE TABLE IF NOT EXISTS inventory(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine TEXT, sku TEXT, dc_id INTEGER,
        batch_no TEXT, current_stock INTEGER, min_stock INTEGER,
        safety_stock INTEGER, days_to_expiry INTEGER
    );
    CREATE TABLE IF NOT EXISTS demand_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine TEXT, day TEXT, actual INTEGER, forecast INTEGER
    );
    CREATE TABLE IF NOT EXISTS replenishments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inventory_id INTEGER, recommended_qty INTEGER,
        source TEXT, priority TEXT, reason TEXT,
        status TEXT DEFAULT 'Pending'
    );
    CREATE TABLE IF NOT EXISTS alerts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT, title TEXT, detail TEXT, time_text TEXT
    );
    """)
    con.commit()
    con.close()
