import os
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display
from . import config

def load_font(size, bold=False):
    font_names = ["arialbd.ttf" if bold else "arial.ttf", "DejaVuSans.ttf"]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except IOError:
            continue
    return ImageFont.load_default()

def process_text(text):
    return get_display(text, base_dir='R')

def get_circular_avatar(path):
    try:
        img = Image.open(path).convert("RGBA")
        img = img.resize((config.AVATAR_SIZE, config.AVATAR_SIZE))
        
        mask = Image.new("L", (config.AVATAR_SIZE, config.AVATAR_SIZE), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, config.AVATAR_SIZE, config.AVATAR_SIZE), fill=255)
        
        output = Image.new("RGBA", (config.AVATAR_SIZE, config.AVATAR_SIZE), (0,0,0,0))
        output.paste(img, (0,0), mask)
        return output
    except Exception as e:
        print(f"Warning: Could not load avatar {path}: {e}")
        img = Image.new("RGBA", (config.AVATAR_SIZE, config.AVATAR_SIZE), (200, 200, 200, 255))
        return img
    
def get_key_position(char):
    kb_height = config.KEYBOARD_HEIGHT
    kb_width = config.WIDTH

    row1 = "'קראטוןםפ"
    row2 = "שדגכעיחלךף"
    row3 = "זסבהנמצתץ"

    if char == " ":
        return (kb_width // 2, int(kb_height * 0.90))

    if char in row1:
        idx = row1.index(char)
        margin = kb_width * 0.04
        effective_width = kb_width - (2 * margin)
        key_width = effective_width / 9
        
        x = margin + (idx * key_width) + (key_width / 2)
        y = kb_height * 0.15
        return (int(x), int(y))

    if char in row2:
        idx = row2.index(char)
        key_width = kb_width / 10
        
        x = (idx * key_width) + (key_width / 2)
        y = kb_height * 0.41
        return (int(x), int(y))

    if char in row3:
        idx = row3.index(char)
        key_width = kb_width / 10
        
        x = (idx * key_width) + (key_width / 2)
        y = kb_height * 0.67 
        return (int(x), int(y))

    replacements = {'מ': 'ם', 'נ': 'ן', 'צ': 'ץ', 'פ': 'ף', 'כ': 'ך'}
    if char in replacements:
        return get_key_position(replacements[char])
    
    reverse_replacements = {v: k for k, v in replacements.items()}
    if char in reverse_replacements:
        pass 

    return None