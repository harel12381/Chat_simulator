# 🎬 WhatsApp Chat Simulator - Video Engine & Web App

![Python](https://img.shields.io/badge/Python-3.8+-3670A0?style=flat&logo=python&logoColor=ffdd54)
![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![MoviePy](https://img.shields.io/badge/MoviePy-Video_Editing-red?style=flat)
![Pillow](https://img.shields.io/badge/Pillow-Image_Processing-blue?style=flat)

A high-fidelity Python-based engine and interactive web app designed to generate realistic WhatsApp chat simulation videos. This tool creates pixel-perfect animations based on a simple JSON script, featuring full support for Right-to-Left (RTL) languages like Hebrew, dynamic system messages, and precise timing control.

*(**Note:** Insert a GIF or screenshot of your generated video/web app here!)*
`![Demo](link_to_your_gif.gif)`

## 🚀 Key Features

* **🌐 Interactive Web App:** Wrapped in a **Streamlit** frontend, allowing users to upload JSON scripts, configure settings, and generate videos directly from the browser.
* **🎨 Realistic UI:** Exact replication of the WhatsApp interface, including the Header, Message Bubbles, and Status Bar.
* **⌨️ Advanced Typing Simulation:**
    * **For "Me":** Full on-screen keyboard animation featuring visual touch ripples, letter pop-ups, and dynamic human-like typing speed.
    * **For Others:** Realistic "typing..." bubble animation with animated dots.
* **✅ Smart Read Receipts:** Integrated **Blue Ticks** logic! Ticks automatically turn blue when other participants respond.
* **🎭 Dynamic System Messages:** Fully functional system events that update the UI in real-time (`add_participant`, `remove_participant`, `change_subject`).
* **🌈 Participant Customization:** Assign specific **HEX colors** to participants' names or let the system assign a consistent random color.
* **🛡️ Script Validation:** Built-in console warnings to detect "Time Travel" (unordered messages), "Ghost Messages" (sender not in group), and "Typing Overlaps."

---

## 🛠️ Installation & Usage

1.  **Clone & Install Dependencies:**
    ```bash
    git clone [https://github.com/harel12381/Chat_simulator.git](https://github.com/harel12381/Chat_simulator.git)
    cd Chat_simulator
    pip install -r requirements.txt
    ```
2.  **Run the Web App (Streamlit GUI):**
    ```bash
    streamlit run app.py
    ```
3.  **Or Run the Video Engine (CLI):**
    ```bash
    python main.py
    ```

---

## 🎬 How to Use

### 1. Setup Your Assets
Place your media files in the `data/` folder:
* **Profile Pictures:** `data/profiles/`
* **Chat Images:** `data/chat_media/`

### 2. Write the Script (`data/script.json`)
The script defines the metadata, participants, and the flow of the conversation.

---

## 📝 Script Guide (`script.json`)

The JSON file is the heart of the simulation. Below is a detailed breakdown of all fields:

### 1. Root Fields
| Field | Type | Required/Optional | Description |
| :--- | :--- | :--- | :--- |
| `scenario_name` | String | **Required** | The name of the scenario (internal use). |
| `my_name` | String | **Required** | The name designated as "Me" (triggers the keyboard and right-side bubbles). |
| `group_info` | Object | **Required** | Group settings (see details below). |
| `participants` | Object | **Required** | List of participants and their settings. |
| `messages` | Array | **Required** | List of messages and events in chronological order. |

### 2. `group_info` Object
| Field | Type | Required/Optional | Description | Default Value |
| :--- | :--- | :--- | :--- | :--- |
| `name` | String | **Required** | The group name displayed in the header. | - |
| `image` | String | **Required** | Path to the group's profile picture. | - |
| `initial_members` | Array | Optional | List of names to display in the header from the start. | All names in `participants`. |

### 3. `participants` Object
| Field | Type | Required/Optional | Description | Default Value |
| :--- | :--- | :--- | :--- | :--- |
| **Name (Key)** | String | Required | Unique identifier for the participant (used in `sender`). | - |
| `image` | String | Optional | Path to the profile picture in `profiles/`. | Generic grey avatar |
| `color` | String | Optional | Hex color code for the participant's name. | Auto-generated hash color |

---

### 4. `messages` Object

Messages are divided into two types: **Regular** and **System**.

#### 🗨️ Regular Message (Text / Image)
| Field | Type | Required/Optional | Description | Default Value |
| :--- | :--- | :--- | :--- | :--- |
| `appearance_time` | Number | **Required** | The exact second the message bubble appears. | - |
| `sender` | String | **Required** | The sender's name (must match a key in `participants`). | - |
| `text` | String | Optional | The message content. Required if no `image` is provided. | - |
| `image` | String | Optional | Path to an image to be sent within the chat. | - |
| `timestamp` | String | Optional | The time displayed inside the message bubble. | Empty string. |
| `typing_duration` | Number | Optional | Duration of the typing animation in seconds. | ~0.15s per char (Me) / 1.0s (Others). |

#### ⚙️ System Message
| Field | Type | Required/Optional | Description |
| :--- | :--- | :--- | :--- |
| `is_system` | Boolean | **Required** | Must be `true`. |
| `appearance_time` | Number | **Required** | When the system message appears. |
| `text` | String | **Required** | The text displayed in the center of the screen. |
| `action` | String | Optional | Action to perform: `add_participant`, `remove_participant`, `change_subject`. |
| `value` | String | Required if `action` used | The name of the participant or the new group subject. |

---

## 🛡️ Console Validation System
During generation, the engine will print yellow warnings for the following cases:
* **Negative Time:** Message scheduled before the video begins.
* **Typing Overlap:** A participant starts typing a new message before finishing the previous one.
* **Ghost Message:** A participant sends a message but is not currently a member of the group.
* **Time Travel:** Message order in JSON does not match their `appearance_time`.

**Example Snippet:**
```json
{
  "scenario_name": "Quick Catch-up",
  "my_name": "Alex",
  "group_info": {
    "name": "Group",
    "image": "profiles/Group.jpg",
    "initial_members": ["Jordan"]
   },
  "participants": {
    "Alex": { "image": "profiles/me.jpg" },
    "Jordan": { "color": "#1F7AC4" },
    "Sam": { }
  },
  "messages": [
    {
      "appearance_time": 1,
      "sender": "Alex",
      "text": "Project Group Created",
      "is_system": true
    },
    {
      "appearance_time": 3,
      "sender": "Jordan",
      "text": "Check out the new logo!",
      "image": "chat_media/logo.jpg",
      "timestamp": "10:00"
    },
    {
      "appearance_time": 6,
      "sender": "Alex",
      "text": "Looks great! Typing the feedback now...",
      "typing_duration": 1.5
    }
  ]
}
