import sqlite3
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "truthguard.db"

def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, version TEXT,
        doc_type TEXT, effective_date TEXT, approval_status TEXT,
        supersedes TEXT, applies_to TEXT, content TEXT NOT NULL, stored_path TEXT DEFAULT '', uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    columns={r[1] for r in db.execute('PRAGMA table_info(documents)')}
    if 'stored_path' not in columns: db.execute("ALTER TABLE documents ADD COLUMN stored_path TEXT DEFAULT ''")
    db.commit()
    return db

def list_documents():
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT id,name,version,doc_type,effective_date,approval_status,supersedes,applies_to,uploaded_at FROM documents ORDER BY id DESC")]

def get_documents():
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT * FROM documents ORDER BY id")]

def add_document(doc):
    with connect() as db:
        cur = db.execute("INSERT INTO documents(name,version,doc_type,effective_date,approval_status,supersedes,applies_to,content,stored_path) VALUES(?,?,?,?,?,?,?,?,?)",
            (doc['name'],doc.get('version',''),doc.get('doc_type','Policy'),doc.get('effective_date',''),doc.get('approval_status','Approved'),doc.get('supersedes',''),doc.get('applies_to',''),doc['content'],doc.get('stored_path','')))
        return cur.lastrowid

def delete_document(doc_id):
    with connect() as db:
        row=db.execute("SELECT stored_path FROM documents WHERE id=?",(doc_id,)).fetchone()
        db.execute("DELETE FROM documents WHERE id=?", (doc_id,))
        if row and row['stored_path']:
            try: Path(row['stored_path']).unlink(missing_ok=True)
            except OSError: pass
