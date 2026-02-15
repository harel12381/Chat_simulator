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
    """Handles Hebrew BiDi rendering"""
    return get_display(text, base_dir='R')

def get_circular_avatar(path):
    """Crops an image into a circle"""
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