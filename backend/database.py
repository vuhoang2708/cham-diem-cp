import sqlite3
import os
import json
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
    cursor.execute("PRAGMA table_info(scores)")
    columns = {row[1] for row in cursor.fetchall()}
    migrations = {
        "rrg_score": "ALTER TABLE scores ADD COLUMN rrg_score REAL DEFAULT 0",
        "extra_score": "ALTER TABLE scores ADD COLUMN extra_score REAL DEFAULT 0",
        "score_max": "ALTER TABLE scores ADD COLUMN score_max REAL DEFAULT 2",
        "score_components": "ALTER TABLE scores ADD COLUMN score_components TEXT",
        "adx_value": "ALTER TABLE scores ADD COLUMN adx_value REAL DEFAULT 0",
        "di_plus": "ALTER TABLE scores ADD COLUMN di_plus REAL DEFAULT 0",
        "di_minus": "ALTER TABLE scores ADD COLUMN di_minus REAL DEFAULT 0",
        "adx_1d": "ALTER TABLE scores ADD COLUMN adx_1d REAL DEFAULT 0",
        "adx_3d": "ALTER TABLE scores ADD COLUMN adx_3d REAL DEFAULT 0",
        "adx_score": "ALTER TABLE scores ADD COLUMN adx_score REAL DEFAULT 0",
    }
    for column, statement in migrations.items():
        if column not in columns:
            cursor.execute(statement)
    conn.commit()
    conn.close()

def save_score(data, category='vn100'):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now()
    updated_at = now.strftime('%Y-%m-%d %H:%M:%S')
    updated_date = now.strftime('%Y-%m-%d')
    rrg_score = data.get('rrg_score', round(data['total_score'] - data['mcdx_score'], 4))
    extra_score = data.get('extra_score', 0)
    score_max = data.get('score_max', 2)
    score_components = data.get('score_components')
    if score_components is None:
        score_components = {
            'mcdx_score': data['mcdx_score'],
            'rrg_score': rrg_score,
        }
    score_components_json = json.dumps(score_components, ensure_ascii=False)
    
    cursor.execute('''
        INSERT OR REPLACE INTO scores 
        (symbol, category, total_score, mcdx_score, rrg_score, extra_score, score_max, score_components, banker_value, banker_left, banker_right, rrg_quadrant, rs_ratio, rs_mom, tail_5d, adx_value, di_plus, di_minus, adx_1d, adx_3d, adx_score, updated_at, updated_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['symbol'],
        category,
        data['total_score'],
        data['mcdx_score'],
        rrg_score,
        extra_score,
        score_max,
        score_components_json,
        data['banker_value'],
        data.get('banker_left', 0),
        data.get('banker_right', 0),
        data['quadrant'],
        data['rs_ratio'],
        data['rs_mom'],
        data['tail_5d'],
        data.get('adx_value', 0),
        data.get('di_plus', 0),
        data.get('di_minus', 0),
        data.get('adx_1d', 0),
        data.get('adx_3d', 0),
        data.get('adx_score', data.get('score_components', {}).get('adx_score', 0) if isinstance(data.get('score_components'), dict) else 0),
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
    
    params: list = []
    if category:
        query += " WHERE s1.category = ?"
        params.append(category)

    query += ' ORDER BY s1.total_score DESC'

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    records = []
    for row in rows:
        record = dict(row)
        if record.get('score_components'):
            try:
                record['score_components'] = json.loads(record['score_components'])
            except (TypeError, json.JSONDecodeError):
                pass
        records.append(record)
    return records

def export_to_json(category=None):
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
