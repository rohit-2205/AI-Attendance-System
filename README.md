Vision-Based Attendance System

AI-Powered Attendance with Face Recognition & YOLOv8

A real-time, contactless attendance system that combines computer vision, AI, and a modern web stack to eliminate proxy attendance and manual errors.

🚀 What’s Cool About This Project

Imagine walking into a classroom and having attendance marked automatically — no roll calls, no cards, no cheating.
That’s exactly what this system does.

By verifying who the person is (face recognition) and whether they meet uniform rules (YOLOv8), attendance is recorded only when both conditions are satisfied.

🧠 How It Thinks (Under the Hood)

🎥 Reads live video from a camera

👕 YOLOv8 checks uniform compliance in real time

🧑‍🎓 Face recognition confirms identity

✅ Attendance is marked only when both checks pass

📊 Records are served instantly to the web UI

This dual-validation approach is what makes the system reliable and proxy-proof.

🛠️ Tech That Powers It

React.js — interactive frontend UI

Flask (Python) — REST API backend

YOLOv8 (Ultralytics) — real-time object detection

OpenCV — video processing

Face Recognition — identity verification

CSV / SQLite / MySQL — attendance storage

👀 See It in Action
<img width="633" height="578" alt="image" src="https://github.com/user-attachments/assets/dd5a915d-84f6-483e-873d-11a6157fda16" />

Uniform Detection

<img width="870" height="462" alt="image" src="https://github.com/user-attachments/assets/a9f4686d-ed56-42cf-b1b0-e318e25042d0" />

Login Page

<img width="870" height="470" alt="image" src="https://github.com/user-attachments/assets/aa0dbc6d-7526-4d98-80eb-98410d7f69c5" />

Home Interface

<img width="43" height="80" alt="image" src="https://github.com/user-attachments/assets/9cfd77a9-133b-4aa6-917a-97debd03513a" />

Live Detection (Uniform + Face Recognition)


<img width="870" height="428" alt="image" src="https://github.com/user-attachments/assets/4b6f4f3b-863c-46b1-828c-776419144222" />

Attendance Records

<img width="870" height="462" alt="image" src="https://github.com/user-attachments/assets/6d795b96-d3c7-4096-9675-6a6cec8e21d0" />

Admin Dashboard

💡 Why This Matters

❌ No manual attendance

❌ No proxy entries

❌ No paperwork

✅ Faster classrooms

✅ Accurate records

✅ Scalable AI solution

This project shows how AI can move beyond demos and solve real institutional problems.

📈 What I Learned

Designing end-to-end AI systems

Building production-style REST APIs

Integrating ML models with real applications

Handling real-time data pipelines

Writing cleaner, modular, scalable code

🔮 What’s Next

Authentication & role-based access

Cloud database + deployment

Analytics & attendance insights

Mobile-friendly UI

Dockerized setup

👤 About the Author

Rohit Gakhare
Final-Year Engineering Student
🔗 LinkedIn: https://linkedin.com/in/rohit-gakhare-b5a431325

📜 License

Built for learning, experimentation, and showcasing skills.
