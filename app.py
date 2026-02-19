import streamlit as st
import os
import tempfile
import base64
from src.engine import generate_video
import sys

sys.dont_write_bytecode = True 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
DEFAULT_AVATAR_PATH = os.path.join(ASSETS_DIR, 'images', 'default_avatar.png')

st.markdown("""
<style>
/* Thumbnail Image (Small) */
.chat-img-thumb {
    height: 50px;
    width: auto;
    border-radius: 5px;
    cursor: zoom-in;
    margin-left: 10px;
    border: 1px solid rgba(0,0,0,0.1);
    transition: transform 0.2s;
    display: block; /* Fix spacing */
}
.chat-img-thumb:hover {
    opacity: 0.9;
    transform: scale(1.05);
}

/* The Hidden Checkbox (Controls the state) */
.zoom-chk {
    display: none;
}

/* The Overlay (Hidden by default, shown when checked) */
.zoom-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0,0,0,0.85);
    z-index: 99999;
    justify-content: center;
    align-items: center;
    cursor: zoom-out;
}

/* Logic: When checkbox is checked, show the overlay sibling */
.zoom-chk:checked + .zoom-overlay {
    display: flex;
    animation: fadeIn 0.2s ease-in-out;
}

/* The Large Image inside Overlay */
.zoom-img-large {
    max-width: 90%;
    max-height: 90%;
    border-radius: 8px;
    box-shadow: 0 0 30px rgba(0,0,0,0.5);
    cursor: zoom-out;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* Layout Tweaks */
.chat-bubble-container {
    position: relative;
    margin-bottom: 15px; /* Added spacing between messages */
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="WhatsApp Video Maker", layout="wide")
st.title("🎬 WhatsApp Video Maker")

if 'participants' not in st.session_state:
    st.session_state.participants = {}
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'temp_media_dir' not in st.session_state:
    st.session_state.temp_media_dir = tempfile.mkdtemp()

if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None
if 'pending_delete_user' not in st.session_state:
    st.session_state.pending_delete_user = None

if 'uploader_key_participant' not in st.session_state:
    st.session_state.uploader_key_participant = 0
if 'uploader_key_chat' not in st.session_state:
    st.session_state.uploader_key_chat = 1000

def get_image_base64(path):
    """Helper to convert image to base64 for HTML embedding"""
    if not path or not os.path.exists(path):
        return None
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/jpeg;base64,{encoded_string}"

def save_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return None
    file_path = os.path.join(st.session_state.temp_media_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def recalculate_times():
    current_time = 0.0
    for msg in st.session_state.messages:
        delay = msg.get('delay', 2.0)
        current_time += delay
        msg['appearance_time'] = current_time

def add_participant_callback():
    p_name = st.session_state.get("new_p_name", "")
    use_color = st.session_state.get("new_p_color_chk", False)
    
    avatar_key = f"p_avatar_{st.session_state.uploader_key_participant}"
    p_avatar_file = st.session_state.get(avatar_key)

    if p_name:
        avatar_path = save_uploaded_file(p_avatar_file)
        p_color = None
        if use_color:
            p_color = st.session_state.get("new_p_color")

        st.session_state.participants[p_name] = {
            "color": p_color, 
            "image": avatar_path 
        }
        
        st.session_state.new_p_name = ""
        st.session_state.new_p_color_chk = False
        st.session_state.uploader_key_participant += 1

def add_message_callback():
    msg_type = st.session_state.get("msg_type_radio")
    sender = st.session_state.get("msg_sender")
    delay = st.session_state.get("msg_delay", 2.0)
    display_time = st.session_state.get("msg_display_time", "")
    
    final_msg_data = None
    should_reset_chat_uploader = False
    
    base_data = {
        "delay": delay,
        "sender": sender,
        "is_system": False,
        "timestamp": display_time 
    }
    
    if msg_type == "Regular Message":
        text_content = st.session_state.get("msg_content", "")
        
        img_key = f"chat_img_{st.session_state.uploader_key_chat}"
        img_file = st.session_state.get(img_key)
        
        image_path = None
        if img_file:
            image_path = save_uploaded_file(img_file)
            should_reset_chat_uploader = True
        elif st.session_state.edit_index is not None:
            old_msg = st.session_state.messages[st.session_state.edit_index]
            if old_msg.get('image') and not old_msg.get('is_system'):
                image_path = old_msg['image']
        
        use_custom_duration = st.session_state.get("chk_duration", False)
        typing_dur = st.session_state.get("num_duration", 1.0)
        
        if text_content or image_path:
            final_msg_data = base_data.copy()
            final_msg_data["text"] = text_content
            
            if image_path:
                final_msg_data["image"] = image_path
            
            if use_custom_duration:
                final_msg_data["typing_duration"] = typing_dur
            
            st.session_state.msg_content = ""

    elif msg_type == "System Message":
        action_type = st.session_state.get("sys_action_type")
        sys_text = ""
        value = ""
        action_code = None
        
        if action_type == "Add Participant":
            value = st.session_state.get("sys_val_add", "")
            sys_text = f"{sender} added {value}"
            action_code = "add_participant"
            st.session_state.sys_val_add = ""
            
        elif action_type == "Remove Participant":
            value = st.session_state.get("sys_val_remove")
            sys_text = f"{sender} removed {value}"
            action_code = "remove_participant"
            
        elif action_type == "Change Subject":
            value = st.session_state.get("sys_val_subject", "")
            sys_text = f"{sender} changed the subject to '{value}'"
            action_code = "change_subject"
            st.session_state.sys_val_subject = ""
            
        elif action_type == "Custom Message":
            sys_text = st.session_state.get("sys_val_custom", "")
            action_code = None
            st.session_state.sys_val_custom = ""

        valid = True
        if action_type != "Custom Message" and not value:
            valid = False
            
        if valid and sys_text:
            final_msg_data = base_data.copy()
            final_msg_data["text"] = sys_text
            final_msg_data["is_system"] = True
            final_msg_data["action"] = action_code
            final_msg_data["value"] = value

    if final_msg_data:
        if st.session_state.edit_index is not None:
            st.session_state.messages[st.session_state.edit_index] = final_msg_data
            st.session_state.edit_index = None
        else:
            st.session_state.messages.append(final_msg_data)
        
        if should_reset_chat_uploader:
            st.session_state.uploader_key_chat += 1
            
        recalculate_times()
    
    elif msg_type == "Regular Message" and not final_msg_data and st.session_state.edit_index is None:
         pass 

with st.sidebar:
    st.header("Settings & Participants")
    
    with st.expander("Group Settings", expanded=True):
        group_name = st.text_input("Group Name", "")
        my_name = st.text_input("My Name (Phone Owner)", "")
        group_img_file = st.file_uploader("Group Icon (Optional)", type=['jpg', 'png', 'jpeg'])
        group_img_path = save_uploaded_file(group_img_file)

    st.subheader("Add Participants")
    
    st.text_input("Participant Name", key="new_p_name")
    
    use_custom_color = st.checkbox("Pick custom color?", key="new_p_color_chk")
    if use_custom_color:
        st.color_picker("Pick Color", "#000000", key="new_p_color")
    
    st.file_uploader("Profile Picture", type=['jpg', 'png', 'jpeg'], key=f"p_avatar_{st.session_state.uploader_key_participant}")
    
    st.button("➕ Add Participant", on_click=add_participant_callback)

    if st.session_state.pending_delete_user:
        st.error(f"⚠️ {st.session_state.pending_delete_user} has existing messages!")
        st.write("Delete them and all their messages?")
        c_yes, c_no = st.columns(2)
        if c_yes.button("Yes, Delete All"):
            user_to_del = st.session_state.pending_delete_user
            del st.session_state.participants[user_to_del]
            
            new_msgs = []
            for m in st.session_state.messages:
                is_sender = (m['sender'] == user_to_del)
                is_related_sys = (m.get('is_system') and m.get('value') == user_to_del)
                if not is_sender and not is_related_sys:
                    new_msgs.append(m)
            
            st.session_state.messages = new_msgs
            recalculate_times()
            st.session_state.pending_delete_user = None
            st.rerun()
            
        if c_no.button("Cancel"):
            st.session_state.pending_delete_user = None
            st.rerun()
        st.divider()

    st.write("Registered Participants:")
    participants_list = list(st.session_state.participants.items())
    
    for name, data in participants_list:
        col_img, col_text, col_del = st.columns([1, 3, 1])
        with col_img:
            img_to_show = data['image'] if data['image'] else DEFAULT_AVATAR_PATH
            if os.path.exists(img_to_show):
                st.image(img_to_show, width=40)
            else:
                st.write("📷")
        with col_text:
            st.write(f"**{name}**")
        with col_del:
            if st.button("🗑️", key=f"del_{name}", use_container_width=True):
                user_has_messages = any(m['sender'] == name for m in st.session_state.messages)
                user_in_system = any(m.get('value') == name for m in st.session_state.messages if m.get('is_system'))
                
                if user_has_messages or user_in_system:
                    st.session_state.pending_delete_user = name
                    st.rerun()
                else:
                    del st.session_state.participants[name]
                    st.rerun()

    all_participant_names = list(st.session_state.participants.keys())
    full_select_options = all_participant_names + [my_name]

    st.divider()
    st.write("Who is in the group initially?")
    st.success(f"✅  (You always in group)")
    other_initial_members = st.multiselect(
        "Select additional participants:",
        options=all_participant_names,
        default=all_participant_names
    )
    final_initial_members_list = [my_name] + other_initial_members

st.header("Build the Chat")

is_edit_mode = st.session_state.edit_index is not None
form_title = "✏️ Edit Message" if is_edit_mode else "➕ Add New Event"
submit_label = "Update Message" if is_edit_mode else "Add Message"

default_type = 0 
default_sender_idx = 0
default_delay = 2.0
default_text = ""
default_display_time = "" 
default_sys_action_idx = 0
default_sys_value = ""

edit_msg_data = None
if is_edit_mode:
    edit_msg_data = st.session_state.messages[st.session_state.edit_index]
    default_delay = float(edit_msg_data.get('delay', 2.0))
    default_display_time = edit_msg_data.get('timestamp', '')
    
    if edit_msg_data.get('is_system'):
        default_type = 1 
        default_text = edit_msg_data.get('text', '')
        act = edit_msg_data.get('action')
        if act == 'add_participant': default_sys_action_idx = 0
        elif act == 'remove_participant': default_sys_action_idx = 1
        elif act == 'change_subject': default_sys_action_idx = 2
        else: default_sys_action_idx = 3
        default_sys_value = edit_msg_data.get('value', '')
        
    else:
        default_type = 0
        default_text = edit_msg_data.get('text', '')

    try:
        if edit_msg_data['sender'] in full_select_options:
            default_sender_idx = full_select_options.index(edit_msg_data['sender'])
    except:
        pass

with st.container(border=True):
    st.subheader(form_title)
    
    if is_edit_mode:
        if st.button("Cancel Edit"):
            st.session_state.edit_index = None
            st.rerun()

    msg_type_options = ["Regular Message", "System Message"]
    msg_type = st.radio("Message Type:", msg_type_options, index=default_type, horizontal=True, key="msg_type_radio")
    
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        sender = st.selectbox("Sender / Actor?", full_select_options, index=default_sender_idx, key="msg_sender")
    with c2:
        delay = st.number_input("Wait Time (seconds)", min_value=0.5, value=default_delay, step=0.5, key="msg_delay")
    with c3:
        st.text_input("Display Time (e.g. 12:30)", value=default_display_time, key="msg_display_time")

    if msg_type == "Regular Message":
        
        if is_edit_mode and default_type == 0 and edit_msg_data.get('image'):
            st.info(f"🖼️ Current Image: {os.path.basename(edit_msg_data['image'])}")

        st.file_uploader("Image (Optional)", type=['jpg', 'png', 'jpeg'], key=f"chat_img_{st.session_state.uploader_key_chat}")
        
        st.text_input("Message Content / Caption", value=default_text if default_type==0 else "", key="msg_content")
        
        def_typing = False
        def_typing_val = 1.0
        if is_edit_mode and default_type == 0 and "typing_duration" in edit_msg_data:
            def_typing = True
            def_typing_val = edit_msg_data["typing_duration"]

        use_custom_duration = st.checkbox("Set typing/sending duration?", value=def_typing, key="chk_duration")
        if use_custom_duration:
            st.number_input("Duration (seconds)", min_value=0.1, value=def_typing_val, key="num_duration")
        
        st.button(submit_label, on_click=add_message_callback)

    elif msg_type == "System Message":
        action_options = ["Add Participant", "Remove Participant", "Change Subject", "Custom Message"]
        action_type = st.selectbox("Action Type", action_options, index=default_sys_action_idx, key="sys_action_type")
        
        current_val = default_sys_value if (is_edit_mode and default_type==1) else ""
        current_custom_text = default_text if (is_edit_mode and default_type==1 and default_sys_action_idx==3) else "Messages and calls are end-to-end encrypted."

        if action_type == "Add Participant":
            st.text_input("Who to add? (Name)", value=current_val, key="sys_val_add")
            
        elif action_type == "Remove Participant":
            idx_remove = 0
            if current_val in full_select_options:
                idx_remove = full_select_options.index(current_val)
            st.selectbox("Who to remove?", full_select_options, index=idx_remove, key="sys_val_remove")
            
        elif action_type == "Change Subject":
            st.text_input("New Subject", value=current_val, key="sys_val_subject")
            
        elif action_type == "Custom Message":
            st.text_input("System message content", value=current_custom_text, key="sys_val_custom")

        st.button(submit_label, on_click=add_message_callback)

st.divider()
st.subheader("📝 Chat Script (Preview)")

if st.session_state.messages:
    for i, msg in enumerate(st.session_state.messages):
        t_val = msg.get('appearance_time', 0.0)
        t_str = f"{t_val:.1f}s"
        
        if st.session_state.edit_index == i:
            st.markdown("👇 **You are currently editing this message:**")
        
        col_content, col_actions = st.columns([15, 2], vertical_alignment="center")
        
        with col_content:
            if msg.get('is_system'):
                border_color = "rgba(13, 202, 240, 0.5)" 
                bg_color = "rgba(13, 202, 240, 0.1)"
                icon = "⚙️"
            elif msg.get('image'):
                border_color = "rgba(255, 193, 7, 0.5)"
                bg_color = "rgba(255, 193, 7, 0.1)"
                icon = "📷"
            else:
                border_color = "rgba(25, 135, 84, 0.5)"
                bg_color = "rgba(25, 135, 84, 0.1)"
                icon = "💬"
            
            sender_part = f"<strong>{msg['sender']}</strong>" if not msg.get('is_system') else "<strong>System</strong>"
            text_part = f"{msg['text']}" if msg.get('text') else ""
            
            display_time_str = f"🕒 {msg['timestamp']}" if msg.get('timestamp') else ""
            typing_info = ""
            if msg.get("typing_duration"):
                 typing_info = f"(⏳ {msg['typing_duration']}s)"
            
            img_html = ""
            if msg.get('image'):
                 b64_img = get_image_base64(msg['image'])
                 if b64_img:
                     unique_id = f"img-zoom-{i}"
                     img_html = f"""<label for="{unique_id}"><img src="{b64_img}" class="chat-img-thumb" title="Click to zoom"></label><input type="checkbox" id="{unique_id}" class="zoom-chk"><div class="zoom-overlay"><label for="{unique_id}" style="width:100%;height:100%;display:flex;justify-content:center;align-items:center;"><img src="{b64_img}" class="zoom-img-large"></label></div>"""

            html_card = f'<div class="chat-bubble-container" style="border: 1px solid {border_color}; background-color: {bg_color}; border-radius: 8px; padding: 10px; display: flex; flex-direction: row; justify-content: space-between; align-items: center; width: 100%;"><div style="flex-grow: 1; margin-right: 15px; font-size: 16px; display: flex; align-items: center; flex-wrap: wrap;"><div style="margin-right: 10px;">{icon} {sender_part}: {text_part}</div></div><div style="flex-shrink: 0;">{img_html}</div><div style="text-align: right; font-size: 13px; color: rgba(255, 255, 255, 0.6); min-width: 90px; line-height: 1.4; border-left: 1px solid rgba(255,255,255,0.2); padding-left: 10px; margin-left: 10px;"><span>⏱️ {t_str}</span><br>{display_time_str} {typing_info}</div></div>'
            st.markdown(html_card, unsafe_allow_html=True)
        
        with col_actions:
            c_edit, c_del = st.columns([1, 1], gap="small")
            if c_edit.button("✏️", key=f"edit_msg_{i}", use_container_width=True):
                st.session_state.edit_index = i
                st.rerun()
            
            if c_del.button("🗑️", key=f"del_msg_{i}", use_container_width=True):
                if st.session_state.edit_index == i:
                    st.session_state.edit_index = None
                st.session_state.messages.pop(i)
                recalculate_times()
                st.rerun()

    if st.button("🗑️ Clear Entire Chat"):
        st.session_state.messages = []
        st.session_state.edit_index = None
        st.rerun()
else:
    st.info("No messages yet. Add messages from above.")

st.divider()
if st.button("🎬 Generate Full Video", type="primary"):
    if not st.session_state.messages:
        st.error("Chat is empty!")
    else:
        recalculate_times()
        
        final_participants = {}
        for name, data in st.session_state.participants.items():
            p_entry = {}
            if data['image']:
                p_entry['image'] = data['image']
            else:
                p_entry['image'] = "default_avatar.png"
            
            if data['color']:
                p_entry['color'] = data['color']
            
            final_participants[name] = p_entry

        if my_name not in final_participants:
            final_participants[my_name] = {"image": "default_avatar.png"}

        script_data = {
            "scenario_name": "Pro Generated Video",
            "my_name": my_name,
            "group_info": {
                "name": group_name,
                "image": group_img_path if group_img_path else None,
                "initial_members": final_initial_members_list
            },
            "participants": final_participants,
            "messages": st.session_state.messages
        }

        assets_paths = {
            "background": os.path.join(ASSETS_DIR, 'images', 'background.jpg'),
            "base_assets_dir": ASSETS_DIR,
            "video_icon": os.path.join(ASSETS_DIR, 'images', 'video_icon.png'),
            "phone_icon": os.path.join(ASSETS_DIR, 'images', 'phone_icon.png'),
            "default_avatar": os.path.join(ASSETS_DIR, 'images', 'default_avatar.png'),
            "default_group": os.path.join(ASSETS_DIR, 'images', 'default_grupe_img.png'),
            "sounds": {
                "sent": os.path.join(ASSETS_DIR, 'sounds', 'msg_sent.mp3'),
                "received": os.path.join(ASSETS_DIR, 'sounds', 'msg_received.mp3')
            }
        }

        with st.spinner('Generating video... ⏳'):
            try:
                output_path = os.path.join(st.session_state.temp_media_dir, 'final_output.mp4')
                
                generate_video(
                    output_path, 
                    script_data, 
                    assets_paths, 
                    data_dir_path=st.session_state.temp_media_dir
                )
                
                st.success("✅ Video is ready!")
                
                c_left, c_center, c_right = st.columns([1, 1, 1])
                with c_center:
                    st.video(output_path)
                
                with open(output_path, 'rb') as f:
                    st.download_button('Download Video 📥', f, file_name='whatsapp_chat.mp4')
                    
            except Exception as e:
                st.error(f"Error during generation: {e}")