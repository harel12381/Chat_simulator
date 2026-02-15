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
        overlay = PIL.Image.new('RGBA', bg_img.size, (240, 242, 245, 200)) # המספר 200 הוא רמת השקיפות
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
    
    keyboard_path = assets_paths.get('keyboard_image') or os.path.join(assets_paths['base_assets_dir'], 'images', 'keyboard.png')
    if os.path.exists(keyboard_path):
        static_assets['keyboard'] = PIL.Image.open(keyboard_path).convert("RGBA").resize((config.WIDTH, config.KEYBOARD_HEIGHT))
    else:
        static_assets['keyboard'] = None
    send_icon_path = os.path.join(assets_paths['base_assets_dir'], 'images', 'send_icon.png')
    if os.path.exists(send_icon_path):
        static_assets['send_icon'] = PIL.Image.open(send_icon_path).convert("RGBA").resize((50, 50))
    else:
        static_assets['send_icon'] = None
        print("Warning: send_icon.png not found!")
    typing_sounds = []
    
    type_sound_path_1 = os.path.join(assets_paths['base_assets_dir'], 'sounds', 'type_sound.mp3')
    if os.path.exists(type_sound_path_1):
        typing_sounds.append(AudioFileClip(type_sound_path_1))
        
    type_sound_path_2 = os.path.join(assets_paths['base_assets_dir'], 'sounds', 'type_sound_2.mp3')
    if os.path.exists(type_sound_path_2):
        typing_sounds.append(AudioFileClip(type_sound_path_2))
    
    if not typing_sounds:
        print("Warning: No typing sounds found!")

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
        
        if is_me and text:
            avg_time_per_char = 0.12
            total_duration = max(len(text) * avg_time_per_char, 1.0)
            
            ideal_start_time = msg['time'] - total_duration
            earliest_possible_start = last_msg_end_time + 0.5
            
            if ideal_start_time < earliest_possible_start:
                actual_start = earliest_possible_start
                actual_end = actual_start + total_duration
                msg['time'] = actual_end
            else:
                actual_start = ideal_start_time
                actual_end = msg['time']

            char_weights = []
            for char in text:
                weight = random.uniform(0.5, 1.5)
                
                if char in " ,.":
                    weight += 1.5 
                
                char_weights.append(weight)
            
            total_weight = sum(char_weights)
            normalized_intervals = [(w / total_weight) * total_duration for w in char_weights]
            
            char_events = []
            current_t = actual_start
            
            for idx, char in enumerate(text):
                char_events.append({'char': char, 'time': current_t})
                
                if typing_sounds:
                    chosen_sound = random.choice(typing_sounds)
                    clip_len = min(0.1, normalized_intervals[idx]) 
                    clip = chosen_sound.subclip(0, clip_len).set_start(current_t)
                    audio_clips.append(clip)
                
                current_t += normalized_intervals[idx]

            typing_events.append({
                'start': actual_start,
                'end': actual_end,
                'text': text,
                'char_schedule': char_events
            })

        last_msg_end_time = msg['time']
        
        if is_me and sound_sent:
            audio_clips.append(sound_sent.set_start(msg['time']))
        elif not is_me and sound_received:
            audio_clips.append(sound_received.set_start(msg['time']))

    def get_typing_state(t):
        for event in typing_events:
            if event['start'] <= t < event['end']:
                current_text = ""
                active_char = None
                for ce in event['char_schedule']:
                    if ce['time'] <= t:
                        current_text += ce['char']
                        if t - ce['time'] < 0.15: 
                            active_char = ce['char']
                return {'is_typing': True, 'current_text': current_text, 'active_char': active_char}
        return {'is_typing': False, 'current_text': "", 'active_char': None}

    final_duration = last_msg_end_time + 3
    
    def make_frame(t):
        t_state = get_typing_state(t)
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
            t_state
        )

    clip = VideoClip(make_frame, duration=final_duration)
    
    if audio_clips:
        clip = clip.set_audio(CompositeAudioClip(audio_clips))
    
    print(f"Rendering video to {output_path}...")
    clip.write_videofile(output_path, fps=config.FPS)