import textwrap
import numpy as np
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

def draw_bubble(img_target, draw, msg, is_me, y_pos, chat_media, ticks_color=None):
    """
    גרסה מתוקנת: חישוב גובה ליניארי (Stacking) להבטחת מרווחים אחידים.
    """
    font_text = utils.load_font(config.FONT_SIZE_TEXT)
    font_time = utils.load_font(config.FONT_SIZE_TIME)
    font_name = utils.load_font(config.FONT_SIZE_NAME, bold=True)
    
    text_content = msg.get('text', "")
    image_key = msg.get('image')
    sender_name = msg['sender']
    time_str = msg['timestamp']
    
    # 1. הכנת התמונה (מדידה ושינוי גודל)
    img_obj = None
    img_w, img_h = 0, 0
    
    if image_key and chat_media and image_key in chat_media:
        raw_img = chat_media[image_key]
        max_img_width = int(config.MAX_BUBBLE_WIDTH)
        ratio = max_img_width / raw_img.width
        img_w = max_img_width
        img_h = int(raw_img.height * ratio)
        img_obj = raw_img.resize((img_w, img_h))

    # 2. הכנת הטקסט (מדידה)
    text_w, text_h = 0, 0
    final_text = ""
    
    if text_content:
        avg_char_width = max(1, draw.textlength("a", font=font_text))
        chars_per_line = int(config.MAX_BUBBLE_WIDTH / avg_char_width)
        wrapped_lines = textwrap.wrap(text_content, width=chars_per_line)
        display_text = "\n".join(wrapped_lines)
        final_text = get_display(display_text, base_dir='R')
        
        bbox = draw.multiline_textbbox((0, 0), final_text, font=font_text, align='right')
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

    # 3. חישוב רוחב הבועה (Bubble Width)
    time_w = draw.textlength(time_str, font=font_time)
    
    content_w = 0
    if img_obj:
        content_w = max(content_w, img_w + 10) # 5px padding each side
    if text_content:
        content_w = max(content_w, text_w + 30) # 15px padding each side
        
    bubble_w = max(content_w, time_w + 40)
    
    # 4. חישוב גובה ומיקומים אנכיים (Stacking Logic)
    # אנו צוברים את הגובה למשתנה cursor_y
    
    padding_top = 10
    padding_bottom = 12
    gap_name_content = 5
    gap_img_text = 8      # רווח קבוע בין תמונה לטקסט
    gap_content_meta = 10 # רווח קבוע בין תוכן (טקסט/תמונה) לשעה
    
    cursor_y = padding_top # מתחילים מלמעלה
    
    # מיקום שם השולח
    name_draw_y = cursor_y
    if not is_me:
        cursor_y += 22 # גובה גופן משוער לשם
        cursor_y += gap_name_content

    # מיקום תמונה
    img_draw_y = cursor_y
    if img_obj:
        cursor_y += img_h
        # אם יש גם טקסט, נוסיף רווח ביניהם
        if text_content:
            cursor_y += gap_img_text

    # מיקום טקסט
    text_draw_y = cursor_y
    if text_content:
        cursor_y += text_h
    
    # הוספת הרווח הקבוע לפני השעה
    cursor_y += gap_content_meta
    
    # מיקום שעה
    meta_draw_y = cursor_y
    cursor_y += 18 # גובה שורה של השעה
    cursor_y += padding_bottom
    
    # גובה סופי
    bubble_h = cursor_y
    
    # 5. חישוב X וציור הרקע
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
    
    # ציור הרקע
    draw.rounded_rectangle([(x, y_pos), (x + bubble_w, y_pos + bubble_h)], radius=15, fill=bg_color)
    
    # 6. ציור האלמנטים לפי המיקומים שחישבנו
    
    # שם השולח
    if not is_me:
        final_sender = get_display(sender_name, base_dir='R')
        name_w = draw.textlength(final_sender, font=font_name)
        name_x = int(x + bubble_w - name_w - 15)
        # מוסיפים את y_pos למיקום היחסי
        draw.text((name_x, y_pos + name_draw_y), final_sender, font=font_name, fill="orange")

    # תמונה
    if img_obj:
        img_x = x + 5
        if img_target:
            img_target.paste(img_obj, (img_x, int(y_pos + img_draw_y)), img_obj)

    # טקסט
    if text_content:
        text_draw_x = int(x + bubble_w - 15)
        draw.multiline_text((text_draw_x, y_pos + text_draw_y), final_text, font=font_text, fill=safe_color(config.COLOR_TEXT_MAIN), align='right', anchor="ra")
    
    # שעה ו-V
    draw.text((int(time_x), y_pos + meta_draw_y), time_str, font=font_time, fill=safe_color(config.COLOR_TEXT_META))
    
    if is_me and ticks_color:
        ticks_x = int(time_x - 22)
        draw_ticks(draw, ticks_x, y_pos + meta_draw_y + 2, ticks_color)
    
    return bubble_h

def render_frame(t, script, participants_imgs, group_info, group_avatar, my_name, bg_img, static_assets, chat_media):
    img = Image.new("RGB", (config.WIDTH, config.HEIGHT), safe_color(config.COLOR_BG_SOLID))
    if bg_img:
        img.paste(bg_img, (0,0))
    
    draw = ImageDraw.Draw(img)
    
    visible_msgs = [m for m in script if m['time'] <= t]
    
    temp_img = Image.new("RGB", (1,1)) 
    temp_draw = ImageDraw.Draw(temp_img)
    
    total_h = 0
    msg_heights = []
    
    for msg in visible_msgs:
        h = draw_bubble(None, temp_draw, msg, msg['sender']==my_name, 0, chat_media, None)
        msg_heights.append(h)
        total_h += h + config.MESSAGE_SPACING

    visible_area = config.HEIGHT - config.HEADER_HEIGHT - 20
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
                else:
                    ticks = config.COLOR_TICKS_GREY
            
            draw_bubble(img, draw, msg, is_me, current_y, chat_media, ticks)
            
            if not is_me:
                avatar = participants_imgs.get(msg['sender'])
                if avatar:
                    avatar_x = config.WIDTH - config.PADDING - config.AVATAR_SIZE
                    img.paste(avatar, (avatar_x, int(current_y)), avatar)
                    
        current_y += msg_h + config.MESSAGE_SPACING

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
        dest_y = 25
        img.paste(group_avatar, (dest_x, dest_y), group_avatar)
    else:
        draw.ellipse((config.WIDTH - 70 - header_offset, 25, config.WIDTH - 20 - header_offset, 75), fill=(200,200,200))

    back_color = (255, 255, 255)
    arrow_tip = (config.WIDTH - 20, 50)
    arrow_top = (config.WIDTH - 35, 35)
    arrow_bottom = (config.WIDTH - 35, 65)
    draw.line([arrow_top, arrow_tip, arrow_bottom], fill=back_color, width=3)
    
    font_back = utils.load_font(28) 
    draw.text((config.WIDTH - 45, 50), "4", font=font_back, fill=back_color, anchor="rm")

    draw_header_icons(img, draw, static_assets)
    
    return np.array(img)