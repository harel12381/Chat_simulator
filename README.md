# 📱 WhatsApp Chat & Video Call Simulator

A realistic, customizable WhatsApp simulation engine designed to stage fake chat scenarios and video calls. This project focuses on **linear message flows** (scripted events) rather than fully functional conversations, making it perfect for creating pranks, demo videos, or UI mockups.

## 🚀 Key Features

* **Scripted Chat Flow:** Messages appear automatically based on a JSON timeline (no backend required).
* **multimedia Support:** Simulates sending/receiving text, images, and audio messages.
* **Fake Video Call Trigger:** Seamlessly transitions from chat to a simulated video call overlay.
    * *Background:* Plays a pre-recorded video file.
    * *Foreground:* Shows the user's real camera feed (picture-in-picture).
* **Realistic Audio:** Includes WhatsApp-style sounds for typing, sent, delivered, and incoming calls.
* **Data-Driven Architecture:** "Fake" content (profiles, photos, scripts) is completely separated from the app's source code.

## 📂 Project Structure

The project strictly separates **Application Assets** (static UI resources) from **Simulation Data** (customizable scenarios).

```text
WHATSAPP_CHAT_SIMULATOR/
├── assets/                     # 🎨 Static UI Resources (Icons, Fonts, Sounds)
│   ├── images/                 # Standard WhatsApp icons (mic, camera, checks)
│   └── sounds/                 # System sounds (pop.mp3, ringtone.mp3)
│
├── data/                       # 🎭 USER DATA (The "Script")
│   ├── profiles/               # Avatars for fake users (mom.jpg, boss.jpg)
│   ├── chat_media/             # Images/Videos sent inside the chat
│   └── scripts/                # JSON files defining the message timing
│
├── src/                        # 🛠️ Source Code
│   ├── components/             # Reusable UI (MessageBubble, ChatHeader)
│   ├── screens/                # Main Views (ActiveChat, VideoCall)
│   └── utils/                  # Logic (SoundManager, TimeParser)
└── App.js