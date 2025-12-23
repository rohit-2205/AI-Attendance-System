#!/usr/bin/env python3
# modified_uniform_app.py

import cv2
import numpy as np
import time
import threading
import queue
from flask import Flask, Response, jsonify, render_template_string
from flask_cors import CORS
from ultralytics import YOLO
import torch

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ---------------- Device & model ----------------
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
print(f"✅ Using device: {device}")

YOLO_MODEL_PATH = r"A:\\Facial Attendance\\attendance_project\\uniform_detection_system\\best.pt"
model = YOLO(YOLO_MODEL_PATH)
if device.startswith('cuda'):
    model.to(device)

# ---- Performance / accuracy trade-offs ----
MODEL_CONF = 0.35  # stricter to reduce false positives
IMG_SZ = (224, 160)
DETECT_EVERY = 6
ENCODE_QUALITY = 60
OUTPUT_FPS = 15

# ---------------- Camera ----------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 20)
try:
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
except Exception:
    pass

if not cap.isOpened():
    print("❌ Cannot open camera")
    exit()

frame_q = queue.Queue(maxsize=2)
latest_frame = None
latest_processed_frame = None
stop_event = threading.Event()
status_lock = threading.Lock()
detection_status = {'shirt_detected': False, 'pants_detected': False, 'uniform_detected': False}
handoff_flag = {'released': False}

# ---------------- HTML ----------------
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Uniform Detection</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:"Poppins",sans-serif;}
body{height:100vh;display:flex;justify-content:center;align-items:center;background:linear-gradient(135deg,#6a11cb,#2575fc);color:#fff;}
.uniform-container{background:rgba(255,255,255,0.1);backdrop-filter:blur(15px);border-radius:25px;padding:40px;width:90%;max-width:600px;text-align:center;box-shadow:0 8px 32px rgba(0,0,0,0.25);}
.logo{width:100px;height:100px;border-radius:50%;margin-bottom:15px;border:2px solid rgba(255,255,255,0.3);}
h1{font-size:1.8rem;margin-bottom:25px;color:#fff;}
.video-container{display:flex;justify-content:center;margin-bottom:20px;}
#video{border:3px solid rgba(255,255,255,0.4);border-radius:15px;width:480px;height:360px;}
#status{margin-top:15px;font-weight:600;color:#00ffcc;}
.good{color:#0a8f3a;font-weight:700;}
.bad{color:#c0392b;font-weight:700;}
</style>
</head>
<body>
<div class="uniform-container">
<img src="{{ url_for('static', filename='images/logo.png') }}" alt="logo" class="logo" />
<h1>Uniform Detection System</h1>
<div class="video-container"><img id="video" src="/video_feed" alt="Live feed" /></div>
<div id="status">Checking uniform...</div>
</div>
<script>
const STATUS_POLL_MS=500;const REDIRECT_DELAY_MS=600;
async function checkStatus(){
 try{
  const resp=await fetch('/detection_status',{cache:"no-store"});
  if(!resp.ok)return;
  const data=await resp.json();
  const s=document.getElementById('status');
  if(data.uniform_detected){
    s.innerHTML="<span class='good'>✅ UNIFORM DETECTED! Preparing attendance...</span>";
    await fetch('/reset_status',{method:'POST'});
    setTimeout(()=>{window.location.href="http://localhost:5001/attendance";},REDIRECT_DELAY_MS);
  }else{
    let parts=[];
    parts.push(data.shirt_detected?"<span class='good'>Shirt</span>":"<span class='bad'>Shirt</span>");
    parts.push(data.pants_detected?"<span class='good'>Pants</span>":"<span class='bad'>Pants</span>");
    s.innerHTML=parts.join(" &nbsp; ");
  }
 }catch(e){document.getElementById('status').innerHTML="Connecting to camera...";}
}
setInterval(checkStatus,STATUS_POLL_MS);checkStatus();
</script>
</body>
</html>
"""

# ---------------- Helpers ----------------
def fast_color_ratio_b_dominant(region, downsize=(32, 32)):
    if region.size == 0:
        return 0.0, 0.0
    small = cv2.resize(region, downsize, interpolation=cv2.INTER_AREA)
    b, g, r = cv2.split(small)
    delta = 20
    blue_mask = (b.astype(int) > (r.astype(int) + delta)) & (b.astype(int) > (g.astype(int) + delta))
    ratio = float(np.count_nonzero(blue_mask)) / blue_mask.size
    mean_val = np.mean(cv2.cvtColor(small, cv2.COLOR_BGR2HSV)[:, :, 2])
    return ratio, mean_val

def detect_uniform_vertical(frame, person_bbox=None):
    SHIRT_BLUE_RATIO_THRESH = 0.12
    PANTS_BLUE_RATIO_THRESH = 0.12
    MIN_BRIGHTNESS = 45

    if person_bbox:
        x, y, w, h = person_bbox
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(frame.shape[1], x+w), min(frame.shape[0], y+h)
        region = frame[y1:y2, x1:x2]
    else:
        region = frame

    if region.size == 0:
        return False, False

    height = region.shape[0]
    upper = region[0:height//2, :]
    lower = region[height//2:, :]

    upper_ratio, upper_val = fast_color_ratio_b_dominant(upper)
    lower_ratio, lower_val = fast_color_ratio_b_dominant(lower)

    shirt_detected = (upper_val > MIN_BRIGHTNESS) and (upper_ratio > SHIRT_BLUE_RATIO_THRESH)
    pants_detected = (lower_val > MIN_BRIGHTNESS) and (lower_ratio > PANTS_BLUE_RATIO_THRESH)

    return shirt_detected, pants_detected

# ---------------- Capture Thread ----------------
def capture_thread_fn():
    global latest_frame
    while not stop_event.is_set():
        if handoff_flag['released']:
            break
        grabbed = cap.grab()
        if not grabbed:
            time.sleep(0.01)
            continue
        ret, frame = cap.retrieve()
        if not ret or frame is None:
            time.sleep(0.01)
            continue
        latest_frame = frame.copy()
        try:
            frame_q.put_nowait(frame.copy())
        except queue.Full:
            try:
                frame_q.get_nowait()
                frame_q.put_nowait(frame.copy())
            except queue.Empty:
                pass
        time.sleep(0.005)

threading.Thread(target=capture_thread_fn, daemon=True).start()

# ---------------- HOG Person Detector ----------------
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def detect_person_hog(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    small = cv2.resize(rgb, (640, 480))
    rects, _ = hog.detectMultiScale(small, winStride=(8, 8), padding=(8, 8), scale=1.05)
    if len(rects) == 0:
        return None
    areas = [w*h for (x, y, w, h) in rects]
    idx = int(np.argmax(areas))
    x, y, w, h = rects[idx]
    sx = frame.shape[1] / 640.0
    sy = frame.shape[0] / 480.0
    return (int(x*sx), int(y*sy), int(w*sx), int(h*sy))

# ---------------- Inference & Stability Thread ----------------
def inference_thread_fn():
    global latest_processed_frame
    frame_count = 0
    MOTION_THRESHOLD_PIXELS = 5.0
    STABLE_TIME_REQUIRED = 0.5
    motion_ema = 0.0
    motion_alpha = 0.25
    stable_start_time = None

    consecutive_uniform_needed = 4
    consecutive_uniform_counter = 0
    handoff_initiated = False
    last_person_bbox = None

    while not stop_event.is_set():
        try:
            frame = frame_q.get(timeout=0.25)
        except queue.Empty:
            if handoff_flag['released']:
                break
            continue

        frame_count += 1
        small_frame = cv2.resize(frame, IMG_SZ)

        # ----------------- Person detection -----------------
        if last_person_bbox is None or frame_count % (DETECT_EVERY*2) == 0:
            pb = detect_person_hog(frame)
            if pb:
                last_person_bbox = pb

        # ----------------- Motion stability -----------------
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if last_person_bbox:
            x, y, w, h = last_person_bbox
            roi = gray[y:y+h, x:x+w]
        else:
            roi = gray

        small_gray = cv2.resize(roi, IMG_SZ)
        blur = cv2.GaussianBlur(small_gray, (5,5), 0)
        diff = cv2.absdiff(small_gray, blur)
        median_motion = float(np.median(diff)) / 255.0 * max(IMG_SZ)
        motion_ema = (motion_alpha * median_motion) + (1 - motion_alpha) * motion_ema
        frame_stable = False
        if motion_ema <= MOTION_THRESHOLD_PIXELS:
            if stable_start_time is None:
                stable_start_time = time.time()
            frame_stable = (time.time() - stable_start_time) >= STABLE_TIME_REQUIRED
        else:
            stable_start_time = None
            frame_stable = False

        # ----------------- Uniform detection -----------------
        shirt_detected, pants_detected = detect_uniform_vertical(frame, last_person_bbox)
        uniform_detected = shirt_detected and pants_detected and frame_stable

        if uniform_detected:
            consecutive_uniform_counter += 1
        else:
            consecutive_uniform_counter = 0

        if consecutive_uniform_counter >= consecutive_uniform_needed and not handoff_initiated:
            handoff_initiated = True
            with status_lock:
                detection_status['shirt_detected'] = True
                detection_status['pants_detected'] = True
                detection_status['uniform_detected'] = True
            try:
                cap.release()
                handoff_flag['released'] = True
                print("🔁 Handoff: camera released for next module.")
            except Exception as e:
                print("⚠️ Error releasing camera:", e)

        if not handoff_initiated:
            with status_lock:
                detection_status['shirt_detected'] = shirt_detected
                detection_status['pants_detected'] = pants_detected
                detection_status['uniform_detected'] = uniform_detected
        else:
            with status_lock:
                detection_status['shirt_detected'] = True
                detection_status['pants_detected'] = True
                detection_status['uniform_detected'] = True

        # ----------------- Display -----------------
        display = cv2.resize(frame, (640, 480))
        if last_person_bbox:
            x, y, w, h = last_person_bbox
            color = (0,255,0) if uniform_detected else (0,255,255)
            cv2.rectangle(display, (x, y), (x+w, y+h), color, 2)
            cv2.putText(display, f"S:{shirt_detected} P:{pants_detected}", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        if handoff_initiated:
            cv2.putText(display, "✅ UNIFORM DETECTED - handoff", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        elif not frame_stable:
            cv2.putText(display, "Slight motion - hold briefly...", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        latest_processed_frame = display

threading.Thread(target=inference_thread_fn, daemon=True).start()

# ---------------- Flask Routes ----------------
@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/video_feed')
def video_feed():
    def gen():
        last_enc_time = 0.0
        min_period = 1.0 / OUTPUT_FPS
        while not stop_event.is_set():
            if latest_processed_frame is not None:
                now = time.time()
                if now - last_enc_time < min_period:
                    time.sleep(min_period - (now - last_enc_time))
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), ENCODE_QUALITY]
                _, jpeg = cv2.imencode('.jpg', latest_processed_frame, encode_param)
                last_enc_time = time.time()
                yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n'
            else:
                blank = np.zeros((480, 640, 3), dtype=np.uint8)
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), ENCODE_QUALITY]
                _, jpeg = cv2.imencode('.jpg', blank, encode_param)
                yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n'

            if handoff_flag['released'] and latest_processed_frame is None:
                break

    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection_status')
def get_detection_status():
    with status_lock:
        # Convert all values to native Python bool
        return jsonify({k: bool(v) for k, v in detection_status.items()})


@app.route('/reset_status', methods=['POST'])
def reset_status():
    with status_lock:
        detection_status.update({'shirt_detected': False, 'pants_detected': False, 'uniform_detected': False})
    return jsonify({"message": "Status reset"})

@app.route('/shutdown', methods=['POST'])
def shutdown():
    stop_event.set()
    time.sleep(0.2)
    try:
        cap.release()
    except Exception:
        pass
    cv2.destroyAllWindows()
    return jsonify({"message": "Shutting down"})

if __name__ == '__main__':
    print("🌐 Running Uniform Detection on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, use_reloader=False)
