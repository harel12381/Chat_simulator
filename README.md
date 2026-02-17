# 📱 WhatsApp Chat Simulator

A high-fidelity Python-based engine designed to generate realistic WhatsApp chat simulation videos. This tool creates pixel-perfect animations based on a simple JSON script, featuring full support for Right-to-Left (RTL) languages like Hebrew, image sharing, dynamic system messages, and precise timing control.

## 🚀 Key Features

* **🎨 Realistic UI:** Exact replication of the WhatsApp interface, including the Header, Message Bubbles, Blue Ticks, and Status Bar.
* **⌨️ Advanced Typing Simulation:**
    * **For "Me":** Full on-screen keyboard animation featuring visual touch ripples, letter pop-ups, and dynamic human-like typing speed.
    * **For Others:** Realistic "typing..." bubble animation with animated dots appearing before the message.
* **✅ Smart Read Receipts:** Integrated **Blue Ticks** logic! Ticks automatically turn blue when other participants respond, simulating that the message has been read.
* **🎭 Dynamic System Messages:** Fully functional system events that update the UI in real-time:
    * `add_participant`: Adds a name to the header's participant list.
    * `remove_participant`: Removes a name from the header.
    * `change_subject`: Instantly updates the group title.
* **🌈 Participant Customization:** Assign specific **HEX colors** to participants' names or let the system assign a consistent random color (consistent per name) just like the real app.
* **🖼️ Multimedia Support:** Seamlessly send text messages and images with.
* **⏱️ Precision Timing:** Total manual control over the `appearance_time` (when a message pops up) and `typing_duration` (how long the typing animation lasts).
* **🛡️ Script Validation:** Built-in console warnings to detect "Time Travel" (unordered messages), "Ghost Messages" (sender not in group), and "Typing Overlaps."

---

## 🛠️ Installation & Usage

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the Generator:**
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
Used for status updates or modifying the group state.
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
* **Negative Time:** If a message is scheduled to start typing before the video begins.
* **Typing Overlap:** If a participant starts typing a new message before finishing the previous one.
* **Ghost Message:** If a participant sends a message but is not currently a member of the group.
* **Time Travel:** If the order of messages in the JSON does not match their `appearance_time`.

**Recommendation:** Always monitor the terminal output to ensure your script timings are logical!

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
      "image": "chat_media/logo.jpg"
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
