import textwrap
import numpy as np
import math
from PIL import Image, ImageDraw
from bidi.algorithm import get_display
from . import config, utils

def safe_color(color):
    if isinstance(color, str): return color
    if not color: return (0, 0, 0)
    return tuple(int(c) for c in color[:3])

def draw_ticks(draw, x, y, color):
    c = safe_color(color)
    x, y = int(x), int(y)
    draw.line([(x, y+6), (x+4, y+10), (x+10, y+1)], fill=c, width=2)
    draw.line([(x+6, y+6), (x+10, y+10), (x+16, y+1)], fill=c, width=2)

def draw_header_icons(img, draw, static_assets):
    icon_color = safe_color(config.COLOR_HEADER_TEXT)
    mx, my = 15, 35
    for i in range(3):
        x1, y1 = mx, my + i*11
        x2, y2 = mx+6, y1+6
        draw.ellipse((x1, y1, x2, y2), fill=icon_color)

    if 'phone_icon' in static_assets:
        p_icon = static_assets['phone_icon']
        if p_icon.width != 50: p_icon = p_icon.resize((50, 50))
        img.paste(p_icon, (50, 25), p_icon)

    if 'video_icon' in static_assets:
        v_icon = static_assets['video_icon']
        if v_icon.width != 60: v_icon = v_icon.resize((60, 45))
        img.paste(v_icon, (110, 28), v_icon)

def draw_tail(draw, x, y, bubble_w, color, is_left_side):
    c = safe_color(color)
    
    if is_left_side:
        points = [
            (x + 10, y),      
            (x - 10, y),      
            (x + 10, y + 20)  
        ]
    else:
        right_edge = x + bubble_w
        points = [
            (right_edge - 10, y),  
            (right_edge + 10, y),    
            (right_edge - 10, y + 20) 
        ]
        
    draw.polygon(points, fill=c)


def draw_typing_bubble(img_target, draw, x, y, t, typers_avatars):
    bubble_w = 80
    bubble_h = 50
    bg_color = safe_color(config.COLOR_BUBBLE_IN)
    
    draw.rounded_rectangle([(x, y), (x + bubble_w, y + bubble_h)], radius=15, fill=bg_color)
    
    draw_tail(draw, x, y, bubble_w, bg_color, is_left_side=False)

    dot_radius = 4
    base_dot_y = y + (bubble_h // 2)
    start_dot_x = x + 25
    gap = 15
    speed = 8.0 
    
    for i in range(3):
        offset_y = math.sin(t * speed + (i * 1.5)) * 5 
        dx = start_dot_x + (i * gap)
        dy = base_dot_y + offset_y
        dot_color = getattr(config, 'COLOR_TYPING_DOT', (160, 160, 160))
        draw.ellipse((dx - dot_radius, dy - dot_radius, dx + dot_radius, dy + dot_radius), fill=dot_color)

    if typers_avatars and img_target:
        avatar_x_base = config.WIDTH - config.PADDING - config.AVATAR_SIZE
        for i, avatar in enumerate(reversed(typers_avatars)):
            offset = i * 25 
            cur_x = avatar_x_base - offset
            draw.ellipse((cur_x-2, y-2, cur_x + config.AVATAR_SIZE+2, y + config.AVATAR_SIZE+2), fill=safe_color(config.COLOR_BG_SOLID))
            img_target.paste(avatar, (cur_x, int(y)), avatar)

    return bubble_h
def draw_bubble(img_target, draw, msg, is_me, y_pos, chat_media, ticks_color=None):
    font_text = utils.load_font(config.FONT_SIZE_TEXT)
    font_time = utils.load_font(config.FONT_SIZE_TIME)
    font_name = utils.load_font(config.FONT_SIZE_NAME, bold=True)
    
    text_content = msg.get('text', "")
    image_key = msg.get('image')
    sender_name = msg.get('sender', "")
    time_str = msg.get('timestamp', "")
    
    if msg.get('is_system'):
        words = text_content.split(' ')
        wrapped_lines = []
        current_line = []
        max_sys_width = config.WIDTH * 0.85
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            w = draw.textlength(test_line, font=font_text)
            if w <= max_sys_width:
                current_line.append(word)
            else:
                if current_line: wrapped_lines.append(' '.join(current_line))
                current_line = [word]
        if current_line: wrapped_lines.append(' '.join(current_line))
        
        display_text = "\n".join(wrapped_lines)
        final_text = get_display(display_text, base_dir='R')
        
        bbox = draw.multiline_textbbox((0, 0), final_text, font=font_text, align='center')
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        bubble_w = text_w + 30
        bubble_h = text_h + 16
        x = (config.WIDTH - bubble_w) // 2
        y = int(y_pos)
        
        sys_color = getattr(config, 'COLOR_SYSTEM_BG', (225, 245, 254))
        draw.rounded_rectangle([(x, y), (x + bubble_w, y + bubble_h)], radius=10, fill=safe_color(sys_color))
        text_x = x + (bubble_w - text_w) / 2
        text_y = y + 8 
        draw.multiline_text((x + bubble_w / 2, text_y), final_text, font=font_text, fill=(0,0,0), align='center', anchor="ma")
        return bubble_h

    img_obj = None
    img_w, img_h = 0, 0
    if image_key and chat_media and image_key in chat_media:
        raw_img = chat_media[image_key]
        max_img_width = int(config.MAX_BUBBLE_WIDTH)
        ratio = max_img_width / raw_img.width
        img_w = max_img_width
        img_h = int(raw_img.height * ratio)
        img_obj = raw_img.resize((img_w, img_h))

    text_w, text_h = 0, 0
    final_text = ""
    
    if text_content:
        words = text_content.split(' ')
        wrapped_lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            w = draw.textlength(test_line, font=font_text)
            
            if w <= config.MAX_BUBBLE_WIDTH:
                current_line.append(word)
            else:
                if current_line:
                    wrapped_lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            wrapped_lines.append(' '.join(current_line))
            
        display_text = "\n".join(wrapped_lines)
        final_text = get_display(display_text, base_dir='R')
        
        bbox = draw.multiline_textbbox((0, 0), final_text, font=font_text, align='right')
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

    time_w = draw.textlength(time_str, font=font_time)
    
    content_w = 0
    if img_obj: content_w = max(content_w, img_w + 10)
    if text_content: content_w = max(content_w, text_w + 30)
    bubble_w = max(content_w, time_w + 40)
    
    padding_top, padding_bottom = 10, 12
    gap_name_content, gap_img_text, gap_content_meta = 5, 8, 10
    
    cursor_y = padding_top
    name_draw_y = cursor_y
    if not is_me:
        cursor_y += 22 + gap_name_content

    img_draw_y = cursor_y
    if img_obj:
        cursor_y += img_h
        if text_content: cursor_y += gap_img_text

    text_draw_y = cursor_y
    if text_content: cursor_y += text_h
    
    cursor_y += gap_content_meta
    meta_draw_y = cursor_y
    cursor_y += 18 + padding_bottom
    bubble_h = cursor_y
    
    if is_me:
        x = config.PADDING
        bg_color = safe_color(config.COLOR_BUBBLE_OUT)
        time_x = x + bubble_w - 15 - time_w 
    else:
        x = config.WIDTH - bubble_w - config.PADDING - config.AVATAR_SIZE - 10
        bg_color = safe_color(config.COLOR_BUBBLE_IN)
        time_x = x + 15
        
    x, y_pos = int(x), int(y_pos)
    bubble_w, bubble_h = int(bubble_w), int(bubble_h)
    
    draw.rounded_rectangle([(x, y_pos), (x + bubble_w, y_pos + bubble_h)], radius=15, fill=bg_color)
    
    draw_tail(draw, x, y_pos, bubble_w, bg_color, is_left_side=is_me)

    if not is_me:
        final_sender = get_display(sender_name, base_dir='R')
        name_w = draw.textlength(final_sender, font=font_name)
        name_x = int(x + bubble_w - name_w - 15)
        draw.text((name_x, y_pos + name_draw_y), final_sender, font=font_name, fill="orange")

    if img_obj and img_target:
        img_target.paste(img_obj, (x + 5, int(y_pos + img_draw_y)), img_obj)

    if text_content:
        text_draw_x = int(x + bubble_w - 15)
        draw.multiline_text((text_draw_x, y_pos + text_draw_y), final_text, font=font_text, fill=safe_color(config.COLOR_TEXT_MAIN), align='right', anchor="ra")
    
    draw.text((int(time_x), y_pos + meta_draw_y), time_str, font=font_time, fill=safe_color(config.COLOR_TEXT_META))
    if is_me and ticks_color:
        draw_ticks(draw, int(time_x - 22), y_pos + meta_draw_y + 2, ticks_color)
    
    return bubble_h

def draw_keyboard_interface(img, draw, keyboard_img, current_text, active_char, static_assets):
    font_input = utils.load_font(30)
    line_height = 38 
    base_padding = 24
    button_area_width = 80 
    max_text_width_px = config.WIDTH - 20 - button_area_width
    
    full_text = (current_text or "") + "|"
    words = full_text.split(' ')
    
    wrapped_lines = []
    current_line_words = []
    
    for word in words:
        test_line = ' '.join(current_line_words + [word])
        test_width = draw.textlength(get_display(test_line, base_dir='R'), font=font_input)
        
        if test_width <= max_text_width_px:
            current_line_words.append(word)
        else:
            if current_line_words:
                wrapped_lines.append(' '.join(current_line_words))
            current_line_words = [word] 
            
    if current_line_words:
        wrapped_lines.append(' '.join(current_line_words))
        
    if not wrapped_lines:
        wrapped_lines = ["|"]

    num_lines = len(wrapped_lines)
    calculated_height = (num_lines * line_height) + base_padding
    final_bar_height = max(config.INPUT_BAR_HEIGHT, calculated_height)

    kb_y = config.HEIGHT - config.KEYBOARD_HEIGHT
    input_y = kb_y - final_bar_height
    
    if keyboard_img:
        img.paste(keyboard_img, (0, kb_y))
    else:
        draw.rectangle([(0, kb_y), (config.WIDTH, config.HEIGHT)], fill=(220, 220, 220))

    draw.rectangle([(0, input_y), (config.WIDTH, kb_y)], fill=safe_color(config.COLOR_INPUT_BG))
    draw.line([(0, input_y), (config.WIDTH, input_y)], fill=(200, 200, 200), width=1)
    
    send_icon = static_assets.get('send_icon')
    if send_icon:
        button_center_y = input_y + (final_bar_height // 2)
        paste_x = 20
        paste_y = button_center_y - 25
        
        img.paste(send_icon, (paste_x, int(paste_y)), send_icon)

    current_text_y = input_y + (base_padding // 2) - 2
    
    for line in wrapped_lines:
        final_line = get_display(line, base_dir='R')
        w = draw.textlength(final_line, font=font_input)
        
        text_x = config.WIDTH - 20 - w
        draw.text((text_x, current_text_y), final_line, font=font_input, fill=(0,0,0))
        
        current_text_y += line_height

    if active_char:
        pos = utils.get_key_position(active_char)
        if pos:
            key_x, key_y_rel = pos
            abs_key_y = kb_y + key_y_rel
            pop_w, pop_h = 60, 90
            pop_x = key_x - (pop_w // 2)
            pop_y = abs_key_y - pop_h + 20 
            
            draw.rounded_rectangle([(pop_x, pop_y), (pop_x + pop_w, pop_y + 60)], radius=10, fill=safe_color(config.COLOR_KEY_POPUP))
            points = [(pop_x + 10, pop_y + 50), (pop_x + pop_w - 10, pop_y + 50), (key_x, abs_key_y)]
            draw.polygon(points, fill=safe_color(config.COLOR_KEY_POPUP))
            
            font_pop = utils.load_font(40, bold=True)
            char_display = get_display(active_char, base_dir='R')
            w = draw.textlength(char_display, font=font_pop)
            draw.text((pop_x + (pop_w-w)/2, pop_y + 5), char_display, font=font_pop, fill=safe_color(config.COLOR_KEY_POPUP_TEXT))   

def render_frame(t, script, participants_imgs, group_info, group_avatar, my_name, bg_img, static_assets, chat_media, typing_state=None):
    img = Image.new("RGB", (config.WIDTH, config.HEIGHT), safe_color(config.COLOR_BG_SOLID))
    if bg_img: img.paste(bg_img, (0,0))
    draw = ImageDraw.Draw(img)
    
    visible_msgs = [m for m in script if m['time'] <= t]
    
    typers = []
    for m in script:
        if t < m['time'] <= (t + 1.0) and m['sender'] != my_name and not m.get('is_system'):
            typers.append(m['sender'])
    typers = list(set(typers)) 
    
    temp_img = Image.new("RGB", (1,1)) 
    temp_draw = ImageDraw.Draw(temp_img)
    
    total_h = 0
    msg_heights = []
    
    for msg in visible_msgs:
        h = draw_bubble(None, temp_draw, msg, msg['sender']==my_name, 0, chat_media, None)
        msg_heights.append(h)
        total_h += h + config.MESSAGE_SPACING
        
    if typers:
        total_h += 50 + config.MESSAGE_SPACING

    bottom_margin = 20
    
    if typing_state and typing_state['is_typing']:
        font_input = utils.load_font(30)
        current_text = typing_state['current_text']
        button_area_width = 80 
        max_text_width_px = config.WIDTH - 20 - button_area_width
        
        full_text = (current_text or "") + "|"
        words = full_text.split(' ')
        
        wrapped_lines = []
        current_line_words = []
        
        for word in words:
            test_line = ' '.join(current_line_words + [word])
            test_width = temp_draw.textlength(get_display(test_line, base_dir='R'), font=font_input)
            
            if test_width <= max_text_width_px:
                current_line_words.append(word)
            else:
                if current_line_words: wrapped_lines.append(' '.join(current_line_words))
                current_line_words = [word]
        if current_line_words: wrapped_lines.append(' '.join(current_line_words))
        if not wrapped_lines: wrapped_lines = ["|"]
            
        num_lines = len(wrapped_lines)
        line_height = 38
        base_padding = 24
        calculated_bar_height = (num_lines * line_height) + base_padding
        final_bar_height = max(config.INPUT_BAR_HEIGHT, calculated_bar_height)
        
        bottom_margin += config.KEYBOARD_HEIGHT + final_bar_height

    visible_area = config.HEIGHT - config.HEADER_HEIGHT - bottom_margin
    
    start_y = config.HEADER_HEIGHT + 20
    if total_h > visible_area:
        start_y -= (total_h - visible_area)

    current_y = start_y
    
    for i, msg in enumerate(visible_msgs):
        is_me = (msg['sender'] == my_name)
        msg_h = msg_heights[i]

        if current_y + msg_h > config.HEADER_HEIGHT:
            ticks = config.COLOR_TICKS_GREY
            if is_me:
                all_participants = set(participants_imgs.keys())
                other_participants = all_participants - {my_name}
                subsequent_msgs = visible_msgs[i+1:]
                subsequent_senders = {m['sender'] for m in subsequent_msgs}
                if other_participants.issubset(subsequent_senders):
                    ticks = config.COLOR_TICKS_BLUE
            
            draw_bubble(img, draw, msg, is_me, current_y, chat_media, ticks)
            
            if not is_me and not msg.get('is_system'):
                avatar = participants_imgs.get(msg['sender'])
                if avatar:
                    avatar_x = config.WIDTH - config.PADDING - config.AVATAR_SIZE
                    img.paste(avatar, (avatar_x, int(current_y)), avatar)
                    
        current_y += msg_h + config.MESSAGE_SPACING

    if typers and current_y > config.HEADER_HEIGHT:
        typers_avatars = [participants_imgs.get(name) for name in typers if participants_imgs.get(name)]
        typing_x = config.WIDTH - 80 - config.PADDING - config.AVATAR_SIZE - 10
        draw_typing_bubble(img, draw, typing_x, current_y, t, typers_avatars)

    # Header
    draw.rectangle([(0, 0), (config.WIDTH, config.HEADER_HEIGHT)], fill=safe_color(config.COLOR_HEADER))
    header_offset = 70 
    grp_name = get_display(group_info['name'], base_dir='R')
    f_header = utils.load_font(24, bold=True)
    draw.text((config.WIDTH - 80 - header_offset, 25), grp_name, font=f_header, fill="white", anchor="rs")
    
    parts_txt = ", ".join(participants_imgs.keys())
    if len(parts_txt) > 30: parts_txt = parts_txt[:30] + "..."
    parts_display = get_display(parts_txt, base_dir='R')
    f_sub = utils.load_font(18)
    draw.text((config.WIDTH - 80 - header_offset, 60), parts_display, font=f_sub, fill=(200,200,200), anchor="rs")
    
    if group_avatar:
        dest_x = config.WIDTH - 70 - header_offset
        img.paste(group_avatar, (dest_x, 25), group_avatar)
    else:
        draw.ellipse((config.WIDTH - 70 - header_offset, 25, config.WIDTH - 20 - header_offset, 75), fill=(200,200,200))

    back_color = (255, 255, 255)
    draw.line([(config.WIDTH - 35, 35), (config.WIDTH - 20, 50), (config.WIDTH - 35, 65)], fill=back_color, width=3)
    font_back = utils.load_font(28) 
    draw.text((config.WIDTH - 45, 50), "4", font=font_back, fill=back_color, anchor="rm")
    draw_header_icons(img, draw, static_assets)

    if typing_state and typing_state['is_typing']:
        kb_img = static_assets.get('keyboard')
        draw_keyboard_interface(
            img, 
            draw, 
            kb_img, 
            typing_state['current_text'], 
            typing_state['active_char'],
            static_assets
        )

    return np.array(img)