import os
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

    static_assets = {}
    if os.path.exists(assets_paths['video_icon']):
         static_assets['video_icon'] = PIL.Image.open(assets_paths['video_icon']).resize((50,40))
    if os.path.exists(assets_paths['phone_icon']):
         static_assets['phone_icon'] = PIL.Image.open(assets_paths['phone_icon']).resize((40,40))

    last_msg_time = script_data['messages'][-1]['time']
    duration = last_msg_time + 3
    my_name = script_data['my_name']
    
    def make_frame(t):
        return drawer.render_frame(
            t, 
            script_data['messages'], 
            participants_imgs, 
            script_data['group_info'], 
            my_name, 
            bg_img,
            static_assets
        )

    clip = VideoClip(make_frame, duration=duration)
    
    audio_clips = []
    sound_sent = None
    sound_received = None
    
    if os.path.exists(assets_paths['sounds']['sent']):
        sound_sent = AudioFileClip(assets_paths['sounds']['sent'])
    
    if os.path.exists(assets_paths['sounds']['received']):
        sound_received = AudioFileClip(assets_paths['sounds']['received'])

    for msg in script_data['messages']:
        is_me = (msg['sender'] == my_name)
        msg_time = msg['time']
        
        if is_me and sound_sent:
            audio_clips.append(sound_sent.set_start(msg_time))
        elif not is_me and sound_received:
            audio_clips.append(sound_received.set_start(msg_time))
    
    if audio_clips:
        clip = clip.set_audio(CompositeAudioClip(audio_clips))
        
    print(f"Rendering video to {output_path}...")
    clip.write_videofile(output_path, fps=config.FPS)