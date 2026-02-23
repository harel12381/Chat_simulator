import os
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display
import random
from . import config
import unicodedata

def load_font(size, bold=False):
    font_name = "assets/fonts/Heebo.ttf" if bold else "assets/fonts/Rubik.ttf"
    
    try:
        return ImageFont.truetype(font_name, size, layout_engine=ImageFont.Layout.BASIC)
    except IOError:
        try:
            return ImageFont.truetype("arial.ttf", size, layout_engine=ImageFont.Layout.BASIC)
        except:
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

def is_emoji(char):
    if char in " \n.,?!-'\"()": return False
    cat = unicodedata.category(char)
    if 'L' in cat or 'N' in cat: 
        return False
    return True

def get_emoji_position(char):
    kb_top = config.HEIGHT - config.KEYBOARD_HEIGHT
    kb_bottom = config.HEIGHT
    
    start_x = 50
    end_x = config.WIDTH - 50
    start_y = kb_top + 60 
    end_y = kb_bottom - 80 
    
    return (random.randint(start_x, end_x), random.randint(start_y, end_y))

def get_key_position(char):
    kb_height = config.KEYBOARD_HEIGHT
    kb_width = config.WIDTH
    
    if is_emoji(char):
        return None 

    row1 = "'קראטוןםפ"
    row2 = "שדגכעיחלךף"
    row3 = "זסבהנמצתץ"

    base_y_offset = config.HEIGHT - kb_height

    if char == " ":
        return (kb_width // 2, int(base_y_offset + kb_height * 0.90))

    if char in row1:
        idx = row1.index(char)
        margin = kb_width * 0.04
        effective_width = kb_width - (2 * margin)
        key_width = effective_width / 9
        
        x = margin + (idx * key_width) + (key_width / 2)
        y = kb_height * 0.15
        return (int(x), int(base_y_offset + y))

    if char in row2:
        idx = row2.index(char)
        key_width = kb_width / 10
        
        x = (idx * key_width) + (key_width / 2)
        y = kb_height * 0.41
        return (int(x), int(base_y_offset + y))

    if char in row3:
        idx = row3.index(char)
        key_width = kb_width / 10
        
        x = (idx * key_width) + (key_width / 2)
        y = kb_height * 0.67 
        return (int(x), int(base_y_offset + y))

    replacements = {'מ': 'ם', 'נ': 'ן', 'צ': 'ץ', 'פ': 'ף', 'כ': 'ך'}
    if char in replacements:
        return get_key_position(replacements[char])
    
    reverse_replacements = {v: k for k, v in replacements.items()}
    if char in reverse_replacements:
        return get_key_position(reverse_replacements[char])

    return None