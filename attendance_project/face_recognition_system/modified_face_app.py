#!/usr/bin/env python3
# face_modified.py
# ===========================================
# Modified Face Recognition App - Auto Attendance
# Improved: robust attendance file handling (create if missing, Excel/CSV fallback),
# atomic writes, helpful diagnostics.
# ===========================================

from flask import Flask, render_template, request, jsonify, send_from_directory
import base64
import os
import pandas as pd
import face_recognition
import pickle
import numpy as np
from datetime import datetime
from io import BytesIO
import traceback
import tempfile
import sys

# -------------------------------
# Directories & Path Resolution
# -------------------------------
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CUR_DIR, ".."))

STUDENT_DATA_DIR = os.path.join(ROOT_DIR, "student_data")
os.makedirs(STUDENT_DATA_DIR, exist_ok=True)

# We prefer to keep attendance.xlsx inside the face_recognition_system folder (CUR_DIR),
# but will create it if missing. If Excel write/read fails (no openpyxl), we'll fallback to CSV.
ATTENDANCE_XLSX = os.path.join(CUR_DIR, "attendance.xlsx")
ATTENDANCE_CSV = os.path.join(CUR_DIR, "attendance.csv")

LOCAL_STUDENT_INFO = os.path.join(CUR_DIR, "student_info.csv")
ROOT_STUDENT_INFO = os.path.join(ROOT_DIR, "student_info.csv")
STUDENT_INFO_FILE = LOCAL_STUDENT_INFO if os.path.exists(LOCAL_STUDENT_INFO) or not os.path.exists(ROOT_STUDENT_INFO) else ROOT_STUDENT_INFO

LOCAL_STUDENTS_XLSX = os.path.join(CUR_DIR, "students.xlsx")
ROOT_STUDENTS_XLSX = os.path.join(ROOT_DIR, "students.xlsx")
STUDENT_EXCEL_FILE = LOCAL_STUDENTS_XLSX if os.path.exists(LOCAL_STUDENTS_XLSX) or not os.path.exists(ROOT_STUDENTS_XLSX) else ROOT_STUDENTS_XLSX

LOCAL_ENCODINGS = os.path.join(CUR_DIR, "face_encodings.pkl")
ROOT_ENCODINGS = os.path.join(ROOT_DIR, "face_encodings.pkl")
ENCODINGS_FILE = LOCAL_ENCODINGS if os.path.exists(LOCAL_ENCODINGS) or not os.path.exists(ROOT_ENCODINGS) else ROOT_ENCODINGS

# Print diagnostic paths
print("🔍 CUR_DIR (script):", CUR_DIR)
print("🔍 ROOT_DIR (project):", ROOT_DIR)
print("📁 STUDENT_DATA_DIR:", STUDENT_DATA_DIR)
print("📊 ATTENDANCE_XLSX:", ATTENDANCE_XLSX)
print("📊 ATTENDANCE_CSV (fallback):", ATTENDANCE_CSV)
print("📁 STUDENT_INFO_FILE:", STUDENT_INFO_FILE)
print("📁 STUDENT_EXCEL_FILE:", STUDENT_EXCEL_FILE)
print("🧠 ENCODINGS_FILE:", ENCODINGS_FILE)

# Global flag telling whether attendance is stored as CSV (True) or XLSX (False)
ATTENDANCE_IS_CSV = False

def ensure_attendance_file():
    """
    Ensure attendance file exists. Prefer XLSX; if Excel engine not available,
    fall back to CSV (and set ATTENDANCE_IS_CSV accordingly).
    """
    global ATTENDANCE_IS_CSV, ATTENDANCE_XLSX, ATTENDANCE_CSV
    # If XLSX exists, prefer it
    if os.path.exists(ATTENDANCE_XLSX):
        ATTENDANCE_IS_CSV = False
        print("✅ Found existing attendance.xlsx.")
        return
    # If CSV exists (from previous fallback), use it
    if os.path.exists(ATTENDANCE_CSV):
        ATTENDANCE_IS_CSV = True
        print("✅ Found existing attendance.csv (using CSV fallback).")
        return

    # Try to create an empty XLSX first
    df = pd.DataFrame(columns=['Folder Name', 'Timestamp'])
    try:
        # Use temporary file + atomic replace to avoid partial writes
        fd, tmp_path = tempfile.mkstemp(suffix=".xlsx", dir=CUR_DIR)
        os.close(fd)
        try:
            df.to_excel(tmp_path, index=False, engine='openpyxl')
            os.replace(tmp_path, ATTENDANCE_XLSX)
            ATTENDANCE_IS_CSV = False
            print("✅ Created new attendance.xlsx.")
            return
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
    except Exception as e:
        print("⚠️ Could not create XLSX (openpyxl missing or other error):", str(e))
        # fallback to CSV
        try:
            fd, tmp_path = tempfile.mkstemp(suffix=".csv", dir=CUR_DIR)
            os.close(fd)
            df.to_csv(tmp_path, index=False)
            os.replace(tmp_path, ATTENDANCE_CSV)
            ATTENDANCE_IS_CSV = True
            print("✅ Created new attendance.csv (fallback).")
            return
        except Exception as e2:
            print("done")
            raise

# Call to ensure file exists at startup
try:
    ensure_attendance_file()
except Exception as e:
    print("Fatal: attendance file could not be created. Exiting.", e)
    sys.exit(1)

# -------------------------------
# Flask app (point to local templates)
# -------------------------------
app = Flask(__name__, template_folder=os.path.join(CUR_DIR, "templates"), static_folder=os.path.join(CUR_DIR, "static"))

# -------------------------------
# Load or Initialize Encodings
# -------------------------------
known_face_encodings = {}
if os.path.exists(ENCODINGS_FILE):
    try:
        with open(ENCODINGS_FILE, "rb") as f:
            known_face_encodings = pickle.load(f) or {}
        for k, v in list(known_face_encodings.items()):
            if v is None:
                known_face_encodings[k] = []
            elif isinstance(v, np.ndarray):
                known_face_encodings[k] = [v]
            elif isinstance(v, (list, tuple)):
                known_face_encodings[k] = list(v)
            else:
                known_face_encodings[k] = [v]
        print(f"✅ Loaded encodings for {len(known_face_encodings)} folders.")
    except Exception as e:
        print("⚠️ Failed to load encodings file:", e)
        print(traceback.format_exc())
        known_face_encodings = {}
else:
    print("ℹ️ No encodings file found (will create after enrollment).")

# -------------------------------
# Initialize Student Info Files (CSV + Excel)
# -------------------------------
def initialize_student_info():
    try:
        if not os.path.exists(STUDENT_INFO_FILE):
            df = pd.DataFrame(columns=['Student ID', 'Name'])
            df.to_csv(STUDENT_INFO_FILE, index=False)
            print(f"Created {STUDENT_INFO_FILE}")
    except Exception as e:
        print("Error creating student_info.csv:", e)

    # Create students.xlsx if missing (best-effort with Excel; fallback to CSV)
    try:
        if not os.path.exists(STUDENT_EXCEL_FILE):
            df = pd.DataFrame(columns=['Student ID', 'Name'])
            try:
                fd, tmp_path = tempfile.mkstemp(suffix=".xlsx", dir=CUR_DIR)
                os.close(fd)
                df.to_excel(tmp_path, index=False, engine='openpyxl')
                os.replace(tmp_path, STUDENT_EXCEL_FILE)
                print(f"Created {STUDENT_EXCEL_FILE}")
            finally:
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
    except Exception as e:
        print("Warning: could not create students.xlsx (will continue). Error:", e)

initialize_student_info()

# -------------------------------
# Helper read/write attendance
# -------------------------------
def read_attendance_df():
    """Read attendance into a DataFrame, handling XLSX or CSV fallback."""
    global ATTENDANCE_IS_CSV, ATTENDANCE_XLSX, ATTENDANCE_CSV
    try:
        if ATTENDANCE_IS_CSV:
            if os.path.exists(ATTENDANCE_CSV):
                df = pd.read_csv(ATTENDANCE_CSV, dtype=str)
            else:
                df = pd.DataFrame(columns=['Folder Name', 'Timestamp'])
        else:
            if os.path.exists(ATTENDANCE_XLSX):
                # use engine explicitly
                df = pd.read_excel(ATTENDANCE_XLSX, dtype=str, engine='openpyxl')
            else:
                df = pd.DataFrame(columns=['Folder Name', 'Timestamp'])
        return df
    except Exception as e:
        print("Error reading attendance file:", e)
        # attempt to recover by switching to CSV fallback
        try:
            if not ATTENDANCE_IS_CSV:
                if os.path.exists(ATTENDANCE_XLSX):
                    # try converting to CSV
                    df = pd.read_excel(ATTENDANCE_XLSX, dtype=str, engine='openpyxl')
                else:
                    df = pd.DataFrame(columns=['Folder Name', 'Timestamp'])
                df.to_csv(ATTENDANCE_CSV, index=False)
                ATTENDANCE_IS_CSV = True
                print("Recovered: converted attendance.xlsx to attendance.csv and using CSV from now on.")
                return df
        except Exception as e2:
            print("Recovery attempt failed:", e2)
            return pd.DataFrame(columns=['Folder Name', 'Timestamp'])

def atomic_write_attendance_df(df):
    """Write DataFrame atomically to chosen attendance file format."""
    global ATTENDANCE_IS_CSV, ATTENDANCE_XLSX, ATTENDANCE_CSV
    try:
        if ATTENDANCE_IS_CSV:
            fd, tmp_path = tempfile.mkstemp(suffix=".csv", dir=CUR_DIR)
            os.close(fd)
            df.to_csv(tmp_path, index=False)
            os.replace(tmp_path, ATTENDANCE_CSV)
            print("✅ Attendance written to CSV (atomic).")
        else:
            fd, tmp_path = tempfile.mkstemp(suffix=".xlsx", dir=CUR_DIR)
            os.close(fd)
            df.to_excel(tmp_path, index=False, engine='openpyxl')
            os.replace(tmp_path, ATTENDANCE_XLSX)
            print("✅ Attendance written to XLSX (atomic).")
    except Exception as e:
        print("Error writing attendance atomically:", e)
        # fallback: try CSV write
        try:
            fd, tmp_path = tempfile.mkstemp(suffix=".csv", dir=CUR_DIR)
            os.close(fd)
            df.to_csv(tmp_path, index=False)
            os.replace(tmp_path, ATTENDANCE_CSV)
            ATTENDANCE_IS_CSV = True
            print("✅ Fallback: Attendance written to CSV.")
        except Exception as e2:
            print("done")
            raise

# -------------------------------
# Routes
# -------------------------------
@app.route('/')
def home():
    return render_template('face_index.html')

@app.route('/student_data/<student_folder>/<filename>')
def student_image(student_folder, filename):
    folder = os.path.join(STUDENT_DATA_DIR, student_folder)
    return send_from_directory(folder, filename)

@app.route('/create_new', methods=['GET', 'POST'])
def create_new():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        student_id = request.form.get('student_id', '').strip()
        if not name or not student_id:
            return render_template('create_new.html', error="Name and Student ID are required.")
        save_student_info(student_id, name)
        return render_template('capture_photos.html', name=name, student_id=student_id)
    return render_template('create_new.html')

def save_student_info(student_id, name):
    try:
        # CSV student_info
        if os.path.exists(STUDENT_INFO_FILE):
            df_csv = pd.read_csv(STUDENT_INFO_FILE, dtype=str)
        else:
            df_csv = pd.DataFrame(columns=['Student ID', 'Name'])
        if str(student_id) in df_csv['Student ID'].astype(str).values:
            print(f"Student ID {student_id} already exists in {STUDENT_INFO_FILE}. Skipping CSV insert.")
        else:
            df_csv = pd.concat([df_csv, pd.DataFrame([[student_id, name]], columns=['Student ID', 'Name'])], ignore_index=True)
            df_csv.to_csv(STUDENT_INFO_FILE, index=False)
            print(f"Saved to CSV: {student_id}, {name}")

        # Excel students.xlsx (best-effort)
        try:
            if os.path.exists(STUDENT_EXCEL_FILE):
                df_excel = pd.read_excel(STUDENT_EXCEL_FILE, dtype=str, engine='openpyxl')
            else:
                df_excel = pd.DataFrame(columns=['Student ID', 'Name'])
            if str(student_id) in df_excel['Student ID'].astype(str).values:
                print(f"Student ID {student_id} already exists in {STUDENT_EXCEL_FILE}. Skipping Excel insert.")
            else:
                df_excel = pd.concat([df_excel, pd.DataFrame([[student_id, name]], columns=['Student ID', 'Name'])], ignore_index=True)
                # atomic write
                fd, tmp_path = tempfile.mkstemp(suffix=".xlsx", dir=CUR_DIR)
                os.close(fd)
                df_excel.to_excel(tmp_path, index=False, engine='openpyxl')
                os.replace(tmp_path, STUDENT_EXCEL_FILE)
                print(f"Saved to Excel: {student_id}, {name}")
        except Exception as e:
            print("Warning: could not update students.xlsx (continuing). Error:", e)

    except Exception as e:
        print("Error saving student info:", e)
        print(traceback.format_exc())

@app.route('/save_image', methods=['POST'])
def save_image():
    try:
        if 'image' not in request.files or 'student_id' not in request.form or 'name' not in request.form:
            return jsonify({"success": False, "message": "Missing image, student ID, or name"}), 400

        student_id = request.form['student_id'].strip()
        name = request.form['name'].strip()
        image_file = request.files['image']

        if not student_id or not name:
            return jsonify({"success": False, "message": "Empty student_id or name"}), 400

        student_folder_name = f"{name}_{student_id}"
        student_folder = os.path.join(STUDENT_DATA_DIR, student_folder_name)
        os.makedirs(student_folder, exist_ok=True)

        image_filename = f"{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        image_path = os.path.join(student_folder, image_filename)
        image_file.save(image_path)

        update_face_encodings(student_folder_name, image_path)

        return jsonify({"success": True, "message": "Image saved successfully.", "path": image_path}), 200
    except Exception as e:
        print("Error in /save_image:", e)
        print(traceback.format_exc())
        return jsonify({"success": False, "message": str(e)}), 500

def update_face_encodings(folder_name, image_path):
    global known_face_encodings
    try:
        image = face_recognition.load_image_file(image_path)
        encs = face_recognition.face_encodings(image)
        if not encs:
            print(f"⚠️ No face found in {image_path}; not updating encodings.")
            return False
        enc = encs[0]
        prev = known_face_encodings.get(folder_name, [])
        if isinstance(prev, list):
            prev.append(enc)
        else:
            prev = [prev, enc]
        known_face_encodings[folder_name] = prev
        with open(ENCODINGS_FILE, "wb") as f:
            pickle.dump(known_face_encodings, f)
        print(f"✅ Encoding updated for {folder_name} (total encodings for folder: {len(known_face_encodings[folder_name])})")
        return True
    except Exception as e:
        print("Error updating encodings:", e)
        print(traceback.format_exc())
        return False

# -------------------------------
# Automatic Attendance (API + Page)
# -------------------------------
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        try:
            data = request.get_json(force=True)
            image_data = data.get('image')
            if not image_data:
                return jsonify({"success": False, "message": "No image provided"}), 400

            if ',' in image_data:
                header, encoded = image_data.split(',', 1)
            else:
                encoded = image_data

            try:
                decoded = base64.b64decode(encoded)
            except Exception as e:
                return jsonify({"success": False, "message": "Invalid base64 image"}), 400

            image = face_recognition.load_image_file(BytesIO(decoded))
            uploaded_face_encodings = face_recognition.face_encodings(image)
            if not uploaded_face_encodings:
                return jsonify({"success": False, "message": "No face found in uploaded image"}), 400

            uploaded_enc = uploaded_face_encodings[0]

            known_enc_list = []
            known_ids = []
            for folder, encs in known_face_encodings.items():
                if isinstance(encs, (list, tuple)):
                    for e in encs:
                        known_enc_list.append(e)
                        known_ids.append(folder)
                else:
                    known_enc_list.append(encs)
                    known_ids.append(folder)

            if len(known_enc_list) == 0:
                return jsonify({"success": False, "message": "No registered students"}), 400

            distances = face_recognition.face_distance(known_enc_list, uploaded_enc)
            best_idx = int(np.argmin(distances))
            best_distance = float(distances[best_idx])

            THRESHOLD = 0.5

            if best_distance < THRESHOLD:
                matched_folder = known_ids[best_idx]
                mark_attendance(matched_folder)
                return jsonify({
                    "success": True,
                    "message": f"Attendance marked for {matched_folder}",
                    "folder": matched_folder,
                    "distance": best_distance
                }), 200
            else:
                return jsonify({"success": False, "message": "Face not recognized", "best_distance": best_distance}), 404

        except Exception as e:
            print("Error in attendance POST:", e)
            print(traceback.format_exc())
            return jsonify({"success": False, "message": str(e)}), 500

    return render_template('attendance.html')

# -------------------------------
# Attendance Logging (Excel/CSV with safe atomic writes)
# -------------------------------
def mark_attendance(folder_name):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        df = read_attendance_df()

        today = datetime.now().strftime('%Y-%m-%d')
        if 'Timestamp' in df.columns:
            already = (df['FolderName'] == folder_name) & (df['Timestamp'].astype(str).str.startswith(today))
            if already.any():
                print(f"⚠️ Attendance already marked today for: {folder_name}")
                return False

        new_row = pd.DataFrame([[folder_name, timestamp]], columns=['Folder Name', 'Timestamp'])
        df = pd.concat([df, new_row], ignore_index=True)
        atomic_write_attendance_df(df)
        print(f"✅ Attendance marked: {folder_name} at {timestamp}")
        return True
    except Exception as e:
        print("Error writing attendance:", e)
        print(traceback.format_exc())
        return False

# -------------------------------
# API Endpoints (info)
# -------------------------------
@app.route('/api/face/status')
def face_system_status():
    return jsonify({
        "system": "face_recognition",
        "status": "active",
        "port": 5001,
        "encodings_count": sum(len(v) if isinstance(v, (list, tuple)) else 1 for v in known_face_encodings.values()),
        "students_registered": len(known_face_encodings),
        "attendance_using_csv": ATTENDANCE_IS_CSV
    })

@app.route('/api/face/students')
def api_get_students():
    try:
        if os.path.exists(STUDENT_INFO_FILE):
            df = pd.read_csv(STUDENT_INFO_FILE, dtype=str)
            students = df.to_dict('records')
        else:
            students = []
        return jsonify({"success": True, "students": students, "count": len(students)})
    except Exception as e:
        print("Error in /api/face/students:", e)
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/face/attendance')
def api_get_attendance():
    try:
        df = read_attendance_df()
        records = df.to_dict('records')
        return jsonify({"success": True, "attendance": records, "count": len(records)})
    except Exception as e:
        print("Error in /api/face/attendance:", e)
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/student_attendance/<student_name>')
def student_attendance(student_name):
    try:
        # Use same attendance file logic as above
        df = read_attendance_df()
        if df.empty:
            return jsonify({"error": "Attendance file is empty or missing."}), 404

        print("Columns found in attendance file:", df.columns.tolist())

        normalized = {c: c.strip().lower() for c in df.columns}
        folder_col = None
        time_col = None
        folder_keywords = ['folder', 'folder name', 'folder_name', 'student', 'name', 'id']
        time_keywords = ['timestamp', 'time', 'date', 'datetime']

        for orig_col, norm in normalized.items():
            if any(kw in norm for kw in folder_keywords):
                folder_col = orig_col
                break
        for orig_col, norm in normalized.items():
            if any(kw in norm for kw in time_keywords):
                time_col = orig_col
                break

        if not folder_col:
            for orig_col in df.columns:
                if any(part in orig_col.lower() for part in ['folder', 'student', 'name', 'id']):
                    folder_col = orig_col
                    break
        if not time_col:
            for orig_col in df.columns:
                if any(part in orig_col.lower() for part in ['time', 'date', 'stamp']):
                    time_col = orig_col
                    break

        if not folder_col or not time_col:
            return jsonify({
                "error": "Could not detect required columns automatically.",
                "found_columns": df.columns.tolist(),
                "note": "Expected a column containing 'folder'/'student'/'name' and a column with 'timestamp'/'time'/'date'."
            }), 400

        df[folder_col] = df[folder_col].astype(str)
        matched = df[df[folder_col].str.lower() == student_name.lower()]
        if matched.empty:
            matched = df[df[folder_col].str.lower().str.contains(student_name.lower())]

        if matched.empty:
            sample_values = df[folder_col].astype(str).unique().tolist()[:10]
            return jsonify({
                "error": f"No attendance found for '{student_name}'",
                "checked_column": folder_col,
                "sample_values_in_column": sample_values,
                "hint": "Try searching with the exact 'Folder Name' value shown in sample_values."
            }), 404

        try:
            dates = pd.to_datetime(matched[time_col]).dt.date.astype(str)
        except Exception:
            dates = matched[time_col].astype(str)

        date_counts = dates.value_counts().sort_index().to_dict()
        total = int(len(matched))

        return jsonify({
            "name": student_name,
            "total": total,
            "date_counts": date_counts,
            "used_columns": {"folder_col": folder_col, "time_col": time_col}
        })
    except Exception as e:
        print("Unhandled error in student_attendance:", e)
        print(traceback.format_exc())
        return jsonify({"error": "Unhandled error", "detail": str(e)}), 500

@app.route('/student_search')
def student_search():
    return render_template('student_search.html')

# -------------------------------
# Main Entry Point
# -------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("👤 FACE RECOGNITION SYSTEM (Auto Attendance)")
    print("=" * 60)
    print(f"✅ Known Encodings (folders): {len(known_face_encodings)}")
    print("🌐 Running on: http://localhost:5001")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
