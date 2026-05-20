import sqlite3 as sqlt
from datetime import datetime

DB_PATH = "job_applications.db"

def init_db():
    conn = sqlt.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,    
            internal_job_id INTEGER,    
            title TEXT,
            company TEXT,
            location TEXT,
            salary INTEGER,
            link TEXT,
            source TEXT,
            description TEXT,
            relevance_score INTEGER,
            status TEXT DEFAULT 'pending',
            applied_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
    ''')
    conn.commit()
    conn.close()


def save_job_application(title, company, location, link, source, description="", salary=0):
    conn = sqlt.connect(DB_PATH)
    cursor = conn.cursor()
    
    try: 
        cursor.execute('''
        INSERT OR IGNORE INTO job_applications
            (title, company, location, salary, link, source, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)            
        ''', (title, company, location, salary, link, source, description))
    except Exception as e:
        print(f"Error saving job: {e}")
    finally:
        conn.close()

def mark_applied(job_id):
    conn = sqlt.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE job_applications SET status = 'applied', applied_at = ? WHERE id = ?
''', (datetime, job_id))
    
    conn.commit()
    conn.close()