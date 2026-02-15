# 📱 WhatsApp Chat & Video Call Simulator

A highly realistic, Python-based engine to generate fake WhatsApp chat videos and linear video call simulations. Designed for content creators, prank videos, and UI mockups, this tool creates pixel-perfect animations based on a simple JSON script.

## 🚀 Key Features

* **Realistic UI:** Replicates the WhatsApp interface with precision (Header, Bubbles, Ticks, Time).
* **Smart Typing Simulation:** Automatically generates realistic typing animations and sounds before messages appear.
* **Multimedia Support:** Send text messages, images (with rounded corners!), and simulates audio messages.
* **Video Call Mode:** Seamless transition from chat to a "fake" incoming video call overlay.
* **Hebrew/RTL Support:** Full support for Right-to-Left languages (Hebrew/Arabic) using `python-bidi`.
* **Customizable Header:** Dynamic group name, participant list (hides "myself" automatically), and icons.
* **No Backend Required:** Runs entirely locally using Python.

## 🛠️ Installation

1.  **Clone the repository** (or download the files).
2.  **Install dependencies**:
    This project relies on `MoviePy`, `Pillow`, and `python-bidi`.
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: Ensure you have ImageMagick installed if required by MoviePy on your system).*

## 🎬 How to Use

### 1. Setup Your Assets
Place your media files in the `data/` folder:
* **Profile Pictures:** `data/profiles/` (e.g., `mom.jpg`, `me.jpg`).
* **Chat Images:** `data/chat_media/` (images sent inside the chat).

### 2. Write the Script (`data/script.json`)
Edit the `data/script.json` file to define the conversation flow.

**Example Structure:**
```json
{
  "scenario_name": "Family Chat",
  "my_name": "Daniel",
  "group_info": {
    "name": "משפחה",
    "image": "profiles/group_icon.png"
  },
  "participants": {
    "Daniel": "profiles/me.jpg",
    "Mom": "profiles/mom.jpg",
    "Dad": "profiles/dad.jpg"
  },
  "messages": [
    {
      "time": 1,
      "text": "הקבוצה 'משפחה' נוצרה",
      "is_system": true
    },
    {
      "time": 3,
      "sender": "Mom",
      "text": "מתי אתה מגיע?",
      "timestamp": "19:00"
    },
    {
      "time": 7,
      "sender": "Daniel",
      "text": "תראו איזה נוף!",
      "image": "chat_media/nature.jpg",
      "timestamp": "19:03"
    }
  ]
}
