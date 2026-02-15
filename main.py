import sys
import os

sys.dont_write_bytecode = True 

import json

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.engine import generate_video

BASE_DIR = current_dir
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
DATA_DIR = os.path.join(BASE_DIR, 'data')

def main():
    script_path = os.path.join(DATA_DIR, 'script.json')
    
    if not os.path.exists(script_path):
        print(f"Error: Script file not found at {script_path}")
        return

    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            script_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON file. {e}")
        return

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

    if not os.path.exists(assets_paths['background']):
        print(f"Warning: Background image not found at {assets_paths['background']}")

    output_file = os.path.join(BASE_DIR, 'output_video.mp4')
    print("--- Starting video generation ---")
    
    try:
        generate_video(output_file, script_data, assets_paths, DATA_DIR)
        print(f"--- Done! Video saved to: {output_file} ---")
    except Exception as e:
        print(f"An error occurred during generation: {e}")

if __name__ == "__main__":
    main()