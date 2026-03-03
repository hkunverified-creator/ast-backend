from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow your frontend to call this backend from the browser

# --- In‑memory "database" (resets when server restarts) ---
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
    return jsonify({"status": "ok", "message": "AST backend running"})


# ---------- SUBJECTS ----------
@app.route("/subjects", methods=["GET"])
def get_subjects():
    return jsonify(subjects)


@app.route("/subjects", methods=["POST"])
def create_or_update_subject():
    global subject_id_counter, subjects

    data = request.get_json() or {}
    code = (data.get("code") or "").strip()
    name = (data.get("name") or "").strip()
    credits = data.get("credits", 0)
    syllabus_base64 = data.get("syllabusBase64")

    if not code or not name:
        return jsonify({"error": "code and name are required"}), 400

    # update if subject with same code already exists
    for subj in subjects:
        if subj["code"] == code:
            subj["name"] = name
            subj["credits"] = credits
            if syllabus_base64 is not None:
                subj["syllabusBase64"] = syllabus_base64
            return jsonify(subj)

    # otherwise create new
    new_subject = {
        "id": subject_id_counter,
        "code": code,
        "name": name,
        "credits": credits,
        "syllabusBase64": syllabus_base64,
    }
    subject_id_counter += 1
    subjects.append(new_subject)
    return jsonify(new_subject), 201


# ---------- TASKS ----------
@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)


@app.route("/tasks", methods=["POST"])
def create_task():
    global task_id_counter, tasks

    data = request.get_json() or {}

    required_fields = ["subjectCode", "lesson", "topic", "type", "priority", "deadline", "status"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    new_task = {
        "id": task_id_counter,
        "subjectCode": data.get("subjectCode"),
        "subjectName": data.get("subjectName", ""),
        "lesson": data.get("lesson"),
        "topic": data.get("topic"),
        "type": data.get("type"),
        "priority": data.get("priority"),
        "deadline": data.get("deadline"),
        "status": data.get("status"),
        "proofBase64": data.get("proofBase64"),
    }
    task_id_counter += 1
    tasks.append(new_task)
    return jsonify(new_task), 201

# ---------- PHYSICAL ACTIVITY ----------
@app.route("/physical", methods=["GET"])
def get_physical():
    return jsonify(physical_entries)


@app.route("/physical", methods=["POST"])
def create_physical():
    global physical_id_counter, physical_entries

    data = request.get_json() or {}

    required_fields = ["date", "name", "category", "description", "deadline", "status"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    new_entry = {
        "id": physical_id_counter,
        "date": data.get("date"),
        "name": data.get("name"),
        "category": data.get("category"),
        "description": data.get("description"),
        "deadline": data.get("deadline"),
        "status": data.get("status"),
        "reason": data.get("reason"),
        "proofBase64": data.get("proofBase64"),
    }
    physical_id_counter += 1
    physical_entries.append(new_entry)
    return jsonify(new_entry), 201


# ---------- READING ----------
@app.route("/reading", methods=["GET"])
def list_reading():
    return jsonify(reading_entries)


@app.route("/reading", methods=["POST"])
def create_reading():
    global reading_id_counter, reading_entries

    data = request.get_json() or {}

    required_fields = ["date", "title", "pages", "notes", "status"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    new_entry = {
        "id": reading_id_counter,
        "date": data.get("date"),
        "title": data.get("title"),
        "pages": data.get("pages"),
        "notes": data.get("notes"),
        "status": data.get("status"),
        "reason": data.get("reason"),
        "proofBase64": data.get("proofBase64"),
    }
    reading_id_counter += 1
    reading_entries.append(new_entry)
    return jsonify(new_entry), 201


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


