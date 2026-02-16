import os
import random
import PIL.Image

if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
from . import drawer, config, utils

def generate_video(output_path, script_data, assets_paths, data_dir_path):
    print("Loading assets...")
    
    bg_img = None
    if os.path.exists(assets_paths['background']):
        bg_img = PIL.Image.open(assets_paths['background']).convert("RGBA").resize((config.WIDTH, config.HEIGHT))
        overlay = PIL.Image.new('RGBA', bg_img.size, (240, 242, 245, 200)) 
        bg_img = PIL.Image.alpha_composite(bg_img, overlay).convert("RGB")
    else:
        print(f"Warning: Background image not found at {assets_paths['background']}")

    participants_imgs = {}
    default_avatar_path = assets_paths['default_avatar']
    
    for name, relative_path in script_data['participants'].items():
        full_path = os.path.join(data_dir_path, relative_path)
        if not os.path.exists(full_path):
             full_path = os.path.join(data_dir_path, 'profiles', os.path.basename(relative_path))
            
        final_path = full_path if os.path.exists(full_path) else default_avatar_path
        participants_imgs[name] = utils.get_circular_avatar(final_path)

    group_img_path = script_data.get('group_info', {}).get('image')
    final_group_path = assets_paths.get('default_group')
    if group_img_path:
        full_group_path = os.path.join(data_dir_path, group_img_path)
        if os.path.exists(full_group_path):
            final_group_path = full_group_path
    
    group_avatar = None
    if final_group_path and os.path.exists(final_group_path):
        group_avatar = utils.get_circular_avatar(final_group_path)

    chat_media = {}
    for msg in script_data['messages']:
        if 'image' in msg and msg['image']:
            img_path = os.path.join(data_dir_path, msg['image'])
            if not os.path.exists(img_path):
                img_path = os.path.join(data_dir_path, 'chat_media', os.path.basename(msg['image']))
            
            if os.path.exists(img_path):
                try:
                    loaded_img = PIL.Image.open(img_path).convert("RGBA")
                    chat_media[msg['image']] = loaded_img
                except Exception:
                    pass

    static_assets = {}
    if os.path.exists(assets_paths['video_icon']):
         static_assets['video_icon'] = PIL.Image.open(assets_paths['video_icon']).resize((50,40))
    if os.path.exists(assets_paths['phone_icon']):
         static_assets['phone_icon'] = PIL.Image.open(assets_paths['phone_icon']).resize((40,40))
    
    # טעינת שתי המקלדות
    keyboard_path = assets_paths.get('keyboard_image') or os.path.join(assets_paths['base_assets_dir'], 'images', 'keyboard.png')
    if os.path.exists(keyboard_path):
        static_assets['keyboard'] = PIL.Image.open(keyboard_path).convert("RGBA").resize((config.WIDTH, config.KEYBOARD_HEIGHT))
    else:
        static_assets['keyboard'] = None

    emoji_kb_path = os.path.join(assets_paths['base_assets_dir'], 'images', 'emoji_keyboard.png')
    if os.path.exists(emoji_kb_path):
        static_assets['emoji_keyboard'] = PIL.Image.open(emoji_kb_path).convert("RGBA").resize((config.WIDTH, config.KEYBOARD_HEIGHT))
    else:
        print("Warning: emoji_keyboard.png not found. Falling back to regular keyboard.")
        static_assets['emoji_keyboard'] = static_assets['keyboard']

    send_icon_path = os.path.join(assets_paths['base_assets_dir'], 'images', 'send_icon.png')
    if os.path.exists(send_icon_path):
        static_assets['send_icon'] = PIL.Image.open(send_icon_path).convert("RGBA").resize((50, 50))
    else:
        static_assets['send_icon'] = None
        
    typing_sounds = []
    
    type_sound_path_1 = os.path.join(assets_paths['base_assets_dir'], 'sounds', 'type_sound.mp3')
    if os.path.exists(type_sound_path_1):
        typing_sounds.append(AudioFileClip(type_sound_path_1))
        
    type_sound_path_2 = os.path.join(assets_paths['base_assets_dir'], 'sounds', 'type_sound_2.mp3')
    if os.path.exists(type_sound_path_2):
        typing_sounds.append(AudioFileClip(type_sound_path_2))
    
    sound_sent = None
    if os.path.exists(assets_paths['sounds']['sent']):
        sound_sent = AudioFileClip(assets_paths['sounds']['sent'])
    
    sound_received = None
    if os.path.exists(assets_paths['sounds']['received']):
        sound_received = AudioFileClip(assets_paths['sounds']['received'])

    typing_events = [] 
    audio_clips = [] 
    
    last_msg_end_time = 0 
    my_name = script_data['my_name']

    for msg in script_data['messages']:
        if msg['time'] < last_msg_end_time + 0.5:
             msg['time'] = last_msg_end_time + 1.0

        is_me = (msg['sender'] == my_name)
        text = msg.get('text', "")
        
        if is_me and text and not msg.get('is_system'):
            actions_sequence = []
            current_mode = 'text'
            
            for char in text:
                is_em = utils.is_emoji(char)
                
                if is_em and current_mode == 'text':
                    actions_sequence.append({'type': 'click_emoji_btn', 'char': None, 'duration': 0.4})
                    current_mode = 'emoji'
                
                elif not is_em and current_mode == 'emoji':
                    actions_sequence.append({'type': 'click_abc_btn', 'char': None, 'duration': 0.4})
                    current_mode = 'text'
                
                if current_mode == 'emoji':
                    actions_sequence.append({'type': 'type_emoji', 'char': char, 'duration': 0.6}) 
                else:
                    base_dur = 0.12
                    if char in " ,.": base_dur += 0.1
                    dur = random.uniform(base_dur * 0.8, base_dur * 1.2)
                    actions_sequence.append({'type': 'type_text', 'char': char, 'duration': dur})
            
            total_duration = sum(a['duration'] for a in actions_sequence)
            
            ideal_start_time = msg['time'] - total_duration
            earliest_possible_start = last_msg_end_time + 0.5
            
            if ideal_start_time < earliest_possible_start:
                actual_start = earliest_possible_start
                actual_end = actual_start + total_duration
                msg['time'] = actual_end
            else:
                actual_start = ideal_start_time
                actual_end = msg['time']

            char_events = []
            current_t = actual_start
            current_typed_str = ""
            active_kb_mode = 'text'
            
            for action in actions_sequence:
                action_type = action['type']
                char = action['char']
                
                event_data = {
                    'time': current_t,
                    'duration': action['duration'],
                    'action': action_type,
                    'char': char,
                    'kb_mode_at_start': active_kb_mode
                }
                
                if action_type == 'click_emoji_btn':
                    active_kb_mode = 'emoji'
                elif action_type == 'click_abc_btn':
                    active_kb_mode = 'text'
                elif action_type in ['type_text', 'type_emoji']:
                    current_typed_str += char
                    
                if typing_sounds and action_type in ['type_text', 'type_emoji']:
                    chosen_sound = random.choice(typing_sounds)
                    clip_len = min(0.1, action['duration']) 
                    clip = chosen_sound.subclip(0, clip_len).set_start(current_t)
                    audio_clips.append(clip)
                
                char_events.append(event_data)
                current_t += action['duration']

            typing_events.append({
                'start': actual_start,
                'end': actual_end,
                'text': text,
                'schedule': char_events
            })

        last_msg_end_time = msg['time']
        
        if is_me and sound_sent and not msg.get('is_system'):
            audio_clips.append(sound_sent.set_start(msg['time']))
        elif not is_me and sound_received and not msg.get('is_system'):
            audio_clips.append(sound_received.set_start(msg['time']))

    def get_typing_state(t):
        for group in typing_events:
            if group['start'] <= t < group['end']:
                current_text = ""
                current_kb_mode = 'text'
                active_touch = None 
                active_char = None 
                
                for event in group['schedule']:
                    if t >= event['time']:
                        if event['action'] in ['type_text', 'type_emoji']:
                             current_text += event['char']
                        
                        if event['action'] == 'click_emoji_btn':
                            current_kb_mode = 'emoji'
                        elif event['action'] == 'click_abc_btn':
                            current_kb_mode = 'text'
                        elif event['kb_mode_at_start'] == 'emoji':
                            current_kb_mode = 'emoji'

                        time_since_event = t - event['time']
                        if 0 <= time_since_event < 0.15:
                            if event['action'] == 'type_text':
                                active_char = event['char']
                                active_touch = utils.get_key_position(event['char'])
                            elif event['action'] == 'type_emoji':
                                active_touch = utils.get_emoji_position(event['char'])
                            elif event['action'] == 'click_emoji_btn':
                                active_touch = config.BUTTON_EMOJI_SWITCH_POS
                            elif event['action'] == 'click_abc_btn':
                                active_touch = config.BUTTON_ABC_SWITCH_POS
                    else:
                        break
                        
                return {
                    'is_typing': True, 
                    'current_text': current_text, 
                    'active_char': active_char,
                    'active_touch': active_touch,
                    'kb_mode': current_kb_mode
                }
        return {'is_typing': False, 'current_text': "", 'active_char': None, 'active_touch': None, 'kb_mode': 'text'}

    initial_group_name = script_data.get('group_info', {}).get('name', 'Group')
    group_info = script_data.get('group_info', {})
    if 'initial_members' in group_info:
        initial_participants = group_info['initial_members']
    else:
        initial_participants = list(script_data['participants'].keys())
        
    def get_current_chat_state(t):
        current_name = initial_group_name
        current_members = initial_participants[:] 

        for msg in script_data['messages']:
            if msg['time'] > t:
                break
            
            if msg.get('is_system') and msg.get('action'):
                action = msg.get('action')
                val = msg.get('value')
                
                if action == 'change_subject' and val:
                    current_name = val
                
                elif action == 'add_participant' and val:
                    if val not in current_members:
                        current_members.append(val)
                
                elif action == 'remove_participant' and val:
                    if val in current_members:
                        current_members.remove(val)
        
        return current_name, current_members

    final_duration = last_msg_end_time + 3
    
    def make_frame(t):
        t_state = get_typing_state(t)
        cur_grp_name, cur_grp_members = get_current_chat_state(t)
        
        return drawer.render_frame(
            t, 
            script_data['messages'], 
            participants_imgs, 
            script_data['group_info'], 
            group_avatar,
            my_name, 
            bg_img,
            static_assets,
            chat_media,
            t_state,
            current_group_name=cur_grp_name,
            current_group_members=cur_grp_members
        )

    clip = VideoClip(make_frame, duration=final_duration)
    
    if audio_clips:
        clip = clip.set_audio(CompositeAudioClip(audio_clips))
    
    print(f"Rendering video to {output_path}...")
    clip.write_videofile(output_path, fps=config.FPS)