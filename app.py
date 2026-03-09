import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- PASTE THE CODE BELOW THIS LINE ---
portal_stats = {
    "streak": 0,
    "last_active": None
}
# --- PASTE THE CODE ABOVE THIS LINE ---

subjects = []
tasks = []
physical_entries = []
reading_entries = []

subject_id_counter = 1
task_id_counter = 1
physical_id_counter = 1
reading_id_counter = 1   

@app.route("/")
def health():
    return jsonify({"status": "ok", "message": "Backend Live"})

@app.route("/subjects", methods=["GET", "POST"])
def handle_subjects():
    global subject_id_counter, subjects
    if request.method == "POST":
        data = request.get_json() or {}
        new_subject = {"id": subject_id_counter, "code": data.get("code"), "name": data.get("name"), "credits": data.get("credits"), "syllabusBase64": data.get("syllabusBase64")}
        subject_id_counter += 1
        subjects.append(new_subject)
        return jsonify(new_subject), 201
    return jsonify(subjects)

@app.route("/tasks", methods=["GET", "POST"])
def handle_tasks():
    global task_id_counter, tasks
    if request.method == "POST":
        data = request.get_json() or {}
        new_task = {"id": task_id_counter, "subjectCode": data.get("subjectCode"), "subjectName": data.get("subjectName", ""), "lesson": data.get("lesson"), "topic": data.get("topic"), "type": data.get("type"), "priority": data.get("priority"), "deadline": data.get("deadline"), "status": data.get("status"), "proofBase64": data.get("proofBase64")}
        task_id_counter += 1
        tasks.append(new_task)
        return jsonify(new_task), 201
    return jsonify(tasks)

@app.route("/physical", methods=["GET", "POST"])
def handle_physical():
    global physical_id_counter, physical_entries
    if request.method == "POST":
        data = request.get_json() or {}
        new_entry = {"id": physical_id_counter, "date": data.get("date"), "name": data.get("name"), "category": data.get("category"), "description": data.get("description"), "deadline": data.get("deadline"), "status": data.get("status"), "proofBase64": data.get("proofBase64")}
        physical_id_counter += 1
        physical_entries.append(new_entry)
        return jsonify(new_entry), 201
    return jsonify(physical_entries)

@app.route("/reading", methods=["GET", "POST"])
def handle_reading():
    global reading_id_counter, reading_entries
    if request.method == "POST":
        data = request.get_json() or {}
        new_entry = {"id": reading_id_counter, "date": data.get("date"), "title": data.get("title"), "pages": data.get("pages"), "notes": data.get("notes"), "status": data.get("status"), "proofBase64": data.get("proofBase64")}
        reading_id_counter += 1
        reading_entries.append(new_entry)
        return jsonify(new_entry), 201
    return jsonify(reading_entries)

@app.route("/api/system/purge", methods=["POST"])
def purge_system():
    global subjects, tasks, physical_entries, reading_entries
    global subject_id_counter, task_id_counter, physical_id_counter, reading_id_counter
    subjects=[]; tasks=[]; physical_entries=[]; reading_entries=[]
    subject_id_counter=1; task_id_counter=1; physical_id_counter=1; reading_id_counter=1
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    # RENDER NEEDS THIS OS.ENVIRON LINE TO WORK
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
