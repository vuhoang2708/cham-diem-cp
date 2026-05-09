import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'scores.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            symbol TEXT PRIMARY KEY,
            total_score REAL,
            mcdx_score REAL,
            banker_value REAL,
            rrg_quadrant TEXT,
            rs_ratio REAL,
            rs_mom REAL,
            tail_5d REAL,
            updated_at DATETIME
        )
    ''')
    conn.commit()
    conn.close()

def save_score(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO scores 
        (symbol, total_score, mcdx_score, banker_value, rrg_quadrant, rs_ratio, rs_mom, tail_5d, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['symbol'],
        data['total_score'],
        data['mcdx_score'],
        data['banker_value'],
        data['quadrant'],
        data['rs_ratio'],
        data['rs_mom'],
        data['tail_5d'],
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    conn.commit()
    conn.close()

def get_all_scores():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM scores ORDER BY total_score DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
