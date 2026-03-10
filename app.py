"""
Advanced Study Tracker — Flask Backend
Author: AST Portal
Deploy on: Render.com (free tier)
Database: SQLite (file-based, persists across restarts on Render disk)
"""

import os
import uuid
import sqlite3
from flask import Flask, request, jsonify, g
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")  # allow GitHub Pages frontend

# ── Database path ──────────────────────────────────────────────────────────────
# On Render, /opt/render/project/src is writable; locally uses current dir
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "ast.db"))


# ── DB helpers ─────────────────────────────────────────────────────────────────
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id TEXT PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            credits REAL DEFAULT 0,
            syllabusBase64 TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            subjectCode TEXT,
            subjectName TEXT,
            lesson TEXT,
            topic TEXT,
            type TEXT,
            priority TEXT,
            deadline TEXT,
            status TEXT,
            proofBase64 TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS physical (
            id TEXT PRIMARY KEY,
            date TEXT,
            name TEXT,
            category TEXT,
            description TEXT,
            deadline TEXT,
            status TEXT,
            reason TEXT,
            proofBase64 TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS reading (
            id TEXT PRIMARY KEY,
            date TEXT,
            title TEXT,
            pages TEXT,
            notes TEXT,
            status TEXT,
            reason TEXT,
            proofBase64 TEXT
        )
    """)

    db.commit()
    db.close()


# ── SUBJECTS ───────────────────────────────────────────────────────────────────
@app.route("/subjects", methods=["GET"])
def get_subjects():
    db = get_db()
    rows = db.execute("SELECT * FROM subjects").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/subjects", methods=["POST"])
def add_subject():
    data = request.get_json(force=True)
    db = get_db()

    code = (data.get("code") or "").strip()
    name = (data.get("name") or "").strip()
    credits = float(data.get("credits") or 0)
    syllabus = data.get("syllabusBase64") or None

    if not code or not name:
        return jsonify({"error": "code and name required"}), 400

    existing = db.execute("SELECT id FROM subjects WHERE code=?", (code,)).fetchone()

    if existing:
        db.execute(
            "UPDATE subjects SET name=?, credits=?, syllabusBase64=? WHERE code=?",
            (name, credits, syllabus, code)
        )
        db.commit()
        row = db.execute("SELECT * FROM subjects WHERE code=?", (code,)).fetchone()
    else:
        new_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO subjects (id,code,name,credits,syllabusBase64) VALUES (?,?,?,?,?)",
            (new_id, code, name, credits, syllabus)
        )
        db.commit()
        row = db.execute("SELECT * FROM subjects WHERE id=?", (new_id,)).fetchone()

    return jsonify(dict(row)), 201


@app.route("/subjects/<subject_id>", methods=["DELETE"])
def delete_subject(subject_id):
    db = get_db()
    # cascade delete tasks
    subject = db.execute("SELECT code FROM subjects WHERE id=?", (subject_id,)).fetchone()
    if subject:
        db.execute("DELETE FROM tasks WHERE subjectCode=?", (subject["code"],))
    db.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
    db.commit()
    return jsonify({"deleted": subject_id})


# ── TASKS ──────────────────────────────────────────────────────────────────────
@app.route("/tasks", methods=["GET"])
def get_tasks():
    db = get_db()
    rows = db.execute("SELECT * FROM tasks").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json(force=True)
    db = get_db()
    new_id = str(uuid.uuid4())
    db.execute(
        """INSERT INTO tasks
           (id,subjectCode,subjectName,lesson,topic,type,priority,deadline,status,proofBase64)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (
            new_id,
            data.get("subjectCode", ""),
            data.get("subjectName", ""),
            data.get("lesson", ""),
            data.get("topic", ""),
            data.get("type", "Theory"),
            data.get("priority", "Medium"),
            data.get("deadline", ""),
            data.get("status", "Pending"),
            data.get("proofBase64") or None,
        )
    )
    db.commit()
    row = db.execute("SELECT * FROM tasks WHERE id=?", (new_id,)).fetchone()
    return jsonify(dict(row)), 201


@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    db.commit()
    return jsonify({"deleted": task_id})


# ── PHYSICAL ───────────────────────────────────────────────────────────────────
@app.route("/physical", methods=["GET"])
def get_physical():
    db = get_db()
    rows = db.execute("SELECT * FROM physical ORDER BY date DESC").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/physical", methods=["POST"])
def add_physical():
    data = request.get_json(force=True)
    db = get_db()
    new_id = str(uuid.uuid4())
    db.execute(
        """INSERT INTO physical
           (id,date,name,category,description,deadline,status,reason,proofBase64)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (
            new_id,
            data.get("date", ""),
            data.get("name", ""),
            data.get("category", ""),
            data.get("description", ""),
            data.get("deadline", ""),
            data.get("status", "Not Completed"),
            data.get("reason", ""),
            data.get("proofBase64") or None,
        )
    )
    db.commit()
    row = db.execute("SELECT * FROM physical WHERE id=?", (new_id,)).fetchone()
    return jsonify(dict(row)), 201


@app.route("/physical/<entry_id>", methods=["DELETE"])
def delete_physical(entry_id):
    db = get_db()
    db.execute("DELETE FROM physical WHERE id=?", (entry_id,))
    db.commit()
    return jsonify({"deleted": entry_id})


# ── READING ────────────────────────────────────────────────────────────────────
@app.route("/reading", methods=["GET"])
def get_reading():
    db = get_db()
    rows = db.execute("SELECT * FROM reading ORDER BY date DESC").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/reading", methods=["POST"])
def add_reading():
    data = request.get_json(force=True)
    db = get_db()
    new_id = str(uuid.uuid4())
    db.execute(
        """INSERT INTO reading
           (id,date,title,pages,notes,status,reason,proofBase64)
           VALUES (?,?,?,?,?,?,?,?)""",
        (
            new_id,
            data.get("date", ""),
            data.get("title", ""),
            data.get("pages", ""),
            data.get("notes", ""),
            data.get("status", "Not Completed"),
            data.get("reason", ""),
            data.get("proofBase64") or None,
        )
    )
    db.commit()
    row = db.execute("SELECT * FROM reading WHERE id=?", (new_id,)).fetchone()
    return jsonify(dict(row)), 201


@app.route("/reading/<entry_id>", methods=["DELETE"])
def delete_reading(entry_id):
    db = get_db()
    db.execute("DELETE FROM reading WHERE id=?", (entry_id,))
    db.commit()
    return jsonify({"deleted": entry_id})


# ── HEALTH CHECK ───────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "AST Backend running", "db": DB_PATH})


@app.route("/health", methods=["GET"])
def health2():
    return jsonify({"status": "ok"})


# ── STARTUP ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
else:
    # Called by gunicorn — still need to init DB
    init_db()
