import subprocess
import time
import webbrowser
import os
import sys
import signal

# --- 🔹 SETTINGS ---
VENV_PYTHON = r"A:\Facial Attendance\attendance_env\Scripts\python.exe"
UNIFORM_APP = r"A:\Facial Attendance\attendance_project\uniform_detection_system\modified_uniform_app.py"
FACE_APP = r"A:\Facial Attendance\attendance_project\face_recognition_system\modified_face_app.py"

# --- 🔹 Function to start an app inside venv ---
def run_in_venv(script_path, port):
    print(f"▶️ Starting {os.path.basename(script_path)} ...")
    return subprocess.Popen(
        [VENV_PYTHON, script_path],
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )

if __name__ == "__main__":
    print("🚀 Starting Combined Attendance System using virtual environment...\n")

    # 1️⃣ Start Uniform Detection App
    uniform_proc = run_in_venv(UNIFORM_APP, 5000)
    time.sleep(5)  # Wait for model/camera to load

    # 2️⃣ Start Face Recognition App
    face_proc = run_in_venv(FACE_APP, 5001)
    time.sleep(5)

    # 3️⃣ Open Uniform Detection page in browser
    print("🌐 Opening Uniform Detection Interface...")
    webbrowser.open("http://localhost:5000", new=1)

    print("\n✅ Both modules launched successfully!")
    print("🟢 Uniform Detection → http://localhost:5000")
    print("🟢 Face Recognition → http://localhost:5001")
    print("\nPress CTRL + C to stop everything.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all systems...")
        for p in [uniform_proc, face_proc]:
            try:
                p.terminate()
            except Exception:
                pass
        print("✅ All systems stopped cleanly.")
        sys.exit(0)
