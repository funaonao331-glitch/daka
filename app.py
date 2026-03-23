from flask import Flask, request, jsonify
import sqlite3
import datetime
import os

app = Flask(__name__, template_folder='.')
DB_FILE = "刷题打卡.db"

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        realname TEXT NOT NULL,
        count INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    users = [("fu-jingya", "付静雅"), ("chai-guangjia", "柴广家"), 
             ("deng-zhenyu", "邓震玉"), ("chen-xinwei", "陈欣唯")]
    for username, realname in users:
        cursor.execute('INSERT OR IGNORE INTO user_progress (username, realname) VALUES (?, ?)', (username, realname))
    conn.commit()
    conn.close()

init_db()

# 跨域设置
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# 前端页面（直接返回你要的精美HTML）
@app.route('/')
def index():
    # 这里把你要的精美HTML内容直接写进去（太长，我简化为读取文件，下面会说）
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

# 接口1：获取进度（和原接口完全一致）
@app.route('/api/progress')
def get_progress():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT username, realname, count FROM user_progress")
        rows = cursor.fetchall()
        conn.close()
        users = [{"username": r[0], "realname": r[1], "count": r[2]} for r in rows]
        return jsonify({"success": True, "data": users})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

# 接口2：更新进度（和原接口完全一致）
@app.route('/api/update', methods=['POST'])
def update_progress():
    try:
        data = request.get_json()
        username = data.get('username')
        addCount = int(data.get('addCount', 0))
        if not username or addCount < 0:
            return jsonify({"success": False, "message": "参数错误"})
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT count FROM user_progress WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"success": False, "message": "用户不存在"})
        
        new_count = min(row[0] + addCount, 150)
        cursor.execute("UPDATE user_progress SET count = ?, updated_at = ? WHERE username = ?", 
                      (new_count, datetime.datetime.now(), username))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "data": {"count": new_count}})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

# 接口3：重置进度（和原接口完全一致）
@app.route('/api/reset', methods=['POST'])
def reset_progress():
    try:
        data = request.get_json()
        username = data.get('username')
        if not username:
            return jsonify({"success": False, "message": "参数错误"})
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE user_progress SET count = 0, updated_at = ? WHERE username = ?", 
                      (datetime.datetime.now(), username))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 3000))