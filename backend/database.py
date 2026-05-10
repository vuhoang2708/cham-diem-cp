import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'scores.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Thêm cột category và updated_date để lưu lịch sử
    # Primary Key gồm (symbol, category, updated_date)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            symbol TEXT,
            category TEXT,
            total_score REAL,
            mcdx_score REAL,
            banker_value REAL,
            banker_left REAL,
            banker_right REAL,
            rrg_quadrant TEXT,
            rs_ratio REAL,
            rs_mom REAL,
            tail_5d REAL,
            updated_at DATETIME,
            updated_date DATE,
            PRIMARY KEY (symbol, category, updated_date)
        )
    ''')
    conn.commit()
    conn.close()

def save_score(data, category='vn100'):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now()
    updated_at = now.strftime('%Y-%m-%d %H:%M:%S')
    updated_date = now.strftime('%Y-%m-%d')
    
    cursor.execute('''
        INSERT OR REPLACE INTO scores 
        (symbol, category, total_score, mcdx_score, banker_value, banker_left, banker_right, rrg_quadrant, rs_ratio, rs_mom, tail_5d, updated_at, updated_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['symbol'],
        category,
        data['total_score'],
        data['mcdx_score'],
        data['banker_value'],
        data.get('banker_left', 0),
        data.get('banker_right', 0),
        data['quadrant'],
        data['rs_ratio'],
        data['rs_mom'],
        data['tail_5d'],
        updated_at,
        updated_date
    ))
    conn.commit()
    conn.close()

def get_latest_scores(category=None):
    """Lấy danh sách điểm mới nhất của từng mã trong một nhóm."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = '''
        SELECT s1.* FROM scores s1
        JOIN (
            SELECT symbol, category, MAX(updated_date) as max_date 
            FROM scores 
            GROUP BY symbol, category
        ) s2 ON s1.symbol = s2.symbol AND s1.category = s2.category AND s1.updated_date = s2.max_date
    '''
    
    if category:
        query += f" WHERE s1.category = '{category}'"
        
    query += ' ORDER BY s1.total_score DESC'
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def export_to_json(category=None):
    import json
    scores = get_latest_scores(category)
    # Nếu có category thì lưu vào file riêng, không thì lưu vào data.json chung
    filename = f'data_{category}.json' if category else 'data.json'
    json_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', filename)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)
    print(f"Exported {category if category else 'all'} scores to {json_path}")

def get_history(symbol, start_date=None, end_date=None):
    """Lấy lịch sử điểm của một mã cổ phiếu trong khoảng thời gian."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = 'SELECT * FROM scores WHERE symbol = ?'
    params = [symbol]
    
    if start_date:
        query += ' AND updated_date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND updated_date <= ?'
        params.append(end_date)
        
    query += ' ORDER BY updated_date DESC LIMIT 100' # Giới hạn để tránh quá tải
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    init_db()
    export_to_json()
    print("Database initialized and exported.")
