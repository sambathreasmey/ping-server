import datetime
import os
import re
import zoneinfo

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps

def create_card(symbol, status, value, percent, change, issueSummary):
    # Colors for each card type
    colors = {
        "UP":    "#4AFF47",  # green
        "DOWN":  "#FF0000",  # red
        "EQUAL": "#FFFFFF",  # gray
    }

    chagne_symbols = {
        "UP":    "+",  # green
        "DOWN":  "-",  # red
        "EQUAL": "",  # gray
    }

    color = colors.get(status.upper(), "#000000")
    chagne_symbol = chagne_symbols.get(status.upper(), "")

    # 2× scale factor
    SCALE = 3

    # Card size
    W, H = 280 * SCALE, 125 * SCALE


    # img = Image.new("RGB", (W, H), "white")
    # Load background image
    if status.upper() == "UP-SKIP":
        bg_img = Image.open(f"images/background-down-2.jpg")
    else:
        bg_img = Image.open(f"images/background-{status.lower()}.png")
    bg_img = bg_img.resize((W, H))         # resize to card size

    # Create card image based on background
    img = bg_img.convert("RGB")             # ensure RGB mode


    draw = ImageDraw.Draw(img)

    # Rounded left border (scaled)
    draw.rounded_rectangle([-16, 0, 36, H], radius=20, fill=color)

    # Load Bold Fonts (scaled)
    try:
        font_main = ImageFont.truetype("fonts/DejaVuSans-Bold.ttf", 34 * SCALE)
        font_small = ImageFont.truetype("fonts/DejaVuSans-Bold.ttf", 26 * SCALE)
        font_smallest = ImageFont.truetype("fonts/DejaVuSans-Bold.ttf", 6 * SCALE)
    except Exception as e:
        print("Font loading error:", e)
        font_main = ImageFont.load_default()
        font_main = ImageFont.load_default()

    # Draw text (scaled positions)
    draw.text((35 * SCALE, 15 * SCALE), symbol, fill=color, font=font_main)
    draw.text((35 * SCALE, 55 * SCALE), value, fill=colors.get("#FFFFFF"), font=font_main)
    draw.text((35 * SCALE, 90 * SCALE), percent, fill=color, font=font_small)
    draw.text((127 * SCALE, 108 * SCALE), issueSummary, fill=colors.get("#FFFFFF"), font=font_smallest)

    text = chagne_symbol + str(change)
    right_x = 260 * SCALE
    y = 78 * SCALE

    # Option 1: Using textbbox (new Pillow)
    bbox = draw.textbbox((0, 0), text, font=font_small)
    text_width = bbox[2] - bbox[0]

    x = right_x - text_width
    draw.text((x, y), text, fill=color, font=font_small)

    # Save
    filename = f"images/output.png"
    img.save(filename)
    print(f"✔ Saved {filename}")

    return filename


WHITE = "#FFFFFF"
MUTED = "#D8DCE3"  # soft off-white for secondary text
UP_COLOR = "#3DDC55"
DOWN_COLOR = "#FF4747"

STATUS_COLORS = {
    "UP": "#3DDC55",     # green
    "DOWN": "#FF4747",   # red
    "EQUAL": "#B7BDC6",  # neutral gray
}

STATUS_SYMBOLS = {
    "UP": "+",
    "DOWN": "-",
    "EQUAL": "",
}


# ==========================================
# HELPER FUNCTIONS
# ==========================================
def get_now():
    tz = zoneinfo.ZoneInfo("Asia/Phnom_Penh")
    now = datetime.datetime.now(tz)
    return now.strftime("%Y %b %d | %I:%M:%S %p")


def safe_float(val, default=0.0):
    if val is None:
        return default
    try:
        return float(str(val).replace(',', '').strip())
    except (ValueError, TypeError):
        return default


def get_summary_text(summaries, issue_name):
    if isinstance(summaries, list):
        for item in summaries:
            if item.get("issue_name") == issue_name:
                return item.get("title", "")
    return ""


def parse_issue_summary(issueSummary):
    """
    Parses issue summary strings dynamically.
    Handles dual levels ("Upper (...) +0% | Lower (...) -0%"), 
    single level ("Lower (7,000) -0.28%"), or plain text.
    """
    levels = []
    if not issueSummary:
        return levels

    upper = re.search(r"Upper\s*\(([\d,\.]+)\)\s*([+-][\d\.]+%)", issueSummary)
    if upper:
        levels.append(("▲", UP_COLOR, upper.group(1), upper.group(2)))

    lower = re.search(r"Lower\s*\(([\d,\.]+)\)\s*([+-][\d\.]+%)", issueSummary)
    if lower:
        levels.append(("▼", DOWN_COLOR, lower.group(1), lower.group(2)))

    return levels


def _load_font(path, size, fallback_size=None):
    try:
        return ImageFont.truetype(path, size)
    except Exception as e:
        print(f"Font loading error ({path}, {size}): {e}")
        return ImageFont.load_default(size=fallback_size or size)


def _luminance(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def _auto_stroke_color(fill_hex):
    return (0, 0, 0, 235) if _luminance(fill_hex) > 0.5 else (255, 255, 255, 235)


def _auto_stroke_width(font, factor=0.03, min_w=1, max_w=6):
    size = getattr(font, "size", 24)
    # Cast to explicit int to prevent Pillow float stroke error
    return int(max(min_w, min(max_w, round(size * factor))))


def _auto_gap(font, factor=0.3):
    size = getattr(font, "size", 24)
    return round(size * factor)


def _draw_text(draw, xy, text, font, fill, stroke_width=None, stroke_fill=None):
    if stroke_width is None:
        stroke_width = _auto_stroke_width(font)
    if stroke_fill is None:
        stroke_fill = _auto_stroke_color(fill)
    draw.text(xy, text, fill=fill, font=font,
              stroke_width=stroke_width, stroke_fill=stroke_fill)


def _content_scrim(W, H, dark_until=0.6, min_alpha=25, max_alpha=175):
    grad = Image.new("L", (W, 1))
    for x in range(W):
        t = x / W
        if t <= dark_until:
            alpha = max_alpha
        else:
            fade = (t - dark_until) / (1 - dark_until)
            alpha = int(max_alpha - fade * (max_alpha - min_alpha))
        grad.putpixel((x, 0), alpha)
    grad = grad.resize((W, H))
    scrim = Image.new("RGBA", (W, H), (4, 8, 10, 0))
    scrim.putalpha(grad)
    return scrim


def _rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255
    )
    return mask


def _load_watermark_logo(logos_dir, symbol, max_size, opacity=70):
    candidates = [symbol, symbol.upper(), symbol.lower()]
    path = None
    for name in candidates:
        p = os.path.join(logos_dir, f"{name}.png")
        if os.path.isfile(p):
            path = p
            break
    if path is None:
        return None

    try:
        logo = Image.open(path).convert("RGBA")
    except Exception as e:
        print(f"Logo loading error ({path}): {e}")
        return None

    logo.thumbnail(max_size, Image.LANCZOS)
    r, g, b, a = logo.split()
    a = a.point(lambda p: int(p * opacity / 255))
    logo.putalpha(a)
    return logo


def _draw_levels_footer(draw, levels, text_x, right_edge, top_y, font_label, font_num, row_gap=None):
    if row_gap is None:
        row_gap = _auto_gap(font_label, factor=0.45)

    num_bbox = draw.textbbox((0, 0), "0", font=font_num)
    num_center = (num_bbox[1] + num_bbox[3]) / 2
    row_h = num_bbox[3]

    pct_w = max(draw.textbbox((0, 0), pct, font=font_num)[2] for _, _, _, pct in levels)
    label_gap = _auto_gap(font_label, factor=0.9)

    row_y = top_y + 10
    for label, color, value, pct in levels:
        lab_bbox = draw.textbbox((0, 0), label, font=font_label)
        label_w = lab_bbox[2]
        label_y = round(row_y + num_center - (lab_bbox[1] + lab_bbox[3]) / 2)
        _draw_text(draw, (text_x, label_y), label, font_label, color)

        _draw_text(draw, (text_x + label_w + label_gap, row_y), str(value), font_num, WHITE)
        _draw_text(draw, (right_edge - pct_w, row_y), pct, font_num, color)

        row_y += row_h + row_gap
    return row_y


# ==========================================
# CARD GENERATOR V2
# ==========================================
def create_card_v2(symbol, status, value, percent, change, issueSummary,
                   images_dir="images", fonts_dir="fonts", logos_dir="symbols",
                   logo_opacity=70, out_path="images/output.png"):
    status_key = status.upper()
    color = STATUS_COLORS.get(status_key, "#B7BDC6")
    change_symbol = STATUS_SYMBOLS.get(status_key, "")

    SCALE = 3
    W, H = 280 * SCALE, 125 * SCALE
    CORNER_RADIUS = 14 * SCALE
    MARGIN = 22 * SCALE

    # Background
    bg_path = f"{images_dir}/background-{status.lower()}.png"
    if os.path.exists(bg_path):
        bg_img = Image.open(bg_path).convert("RGB")
    else:
        bg_img = Image.new("RGB", (W, H), (20, 24, 30))

    bg_img = ImageOps.fit(bg_img, (W, H))
    img = bg_img.convert("RGBA")

    # Watermark
    watermark = _load_watermark_logo(
        logos_dir, symbol, max_size=(round(W * 0.55), round(H * 0.95)), opacity=logo_opacity
    )
    if watermark is not None:
        wx = W - watermark.width - round(MARGIN * 0.4)
        wy = (H - watermark.height) // 2
        img.alpha_composite(watermark, (wx, wy))

    scrim = _content_scrim(W, H)
    img = Image.alpha_composite(img, scrim)
    draw = ImageDraw.Draw(img)

    # Fonts
    font_symbol = _load_font(f"{fonts_dir}/DejaVuSans-Bold.ttf", 16 * SCALE)
    font_value = _load_font(f"{fonts_dir}/DejaVuSans-Bold.ttf", 26 * SCALE)
    font_change = _load_font(f"{fonts_dir}/DejaVuSans-Bold.ttf", 16 * SCALE)
    font_change_only = _load_font(f"{fonts_dir}/DejaVuSans-Bold.ttf", 20 * SCALE)
    font_summary = _load_font(f"{fonts_dir}/DejaVuSans-Bold.ttf", 11 * SCALE)
    font_level_label = _load_font(f"{fonts_dir}/DejaVuSans-Bold.ttf", 7 * SCALE)
    font_level_num = _load_font(f"{fonts_dir}/DejaVuSans-Bold.ttf", 8 * SCALE)
    font_datetime = _load_font(f"{fonts_dir}/DejaVuSans-Bold.ttf", 5 * SCALE)

    # Accent bar
    bar_w = 10 * SCALE
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle([0, 0, bar_w + 6 * SCALE, H], fill=(0, 0, 0, 60))
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, bar_w, H], fill=color)

    text_x = MARGIN + bar_w

    def line_height(txt, font):
        bbox = draw.textbbox((0, 0), txt, font=font)
        return bbox[3] - bbox[1]

    # Footer processing
    levels = parse_issue_summary(issueSummary)
    if levels:
        row_h = draw.textbbox((0, 0), "0", font=font_level_num)[3]
        LEVEL_ROW_GAP = _auto_gap(font_level_label, factor=0.45)
        footer_h = row_h * len(levels) + LEVEL_ROW_GAP * (len(levels) - 1)
    elif issueSummary:
        footer_h = line_height(issueSummary, font_summary)
    else:
        footer_h = 0

    footer_y = H - MARGIN - footer_h
    cursor_y = MARGIN - _auto_gap(font_symbol, factor=0.3)

    # Draw Symbol Header
    symbol_y = cursor_y
    _draw_text(draw, (text_x, cursor_y), symbol.upper(), font_symbol, color, stroke_width=0)

    # Date/Time badge
    dt_text = get_now()
    dt_bbox = draw.textbbox((0, 0), dt_text, font=font_datetime)
    dt_w = dt_bbox[2] - dt_bbox[0]
    dt_h = dt_bbox[3] - dt_bbox[1]

    pad_x = 7 * SCALE
    pad_y = 4 * SCALE
    badge_w = dt_w + pad_x * 2
    badge_h = dt_h + pad_y * 2 - 3

    sym_bbox = draw.textbbox((0, 0), symbol.upper(), font=font_symbol)
    sym_center_y = symbol_y + (sym_bbox[1] + sym_bbox[3]) / 2

    badge_x1 = W - MARGIN
    badge_x0 = badge_x1 - badge_w
    badge_y0 = round(sym_center_y - badge_h / 2)

    r, g, b = ImageColor.getrgb(color)
    badge_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(badge_layer).rounded_rectangle(
        [badge_x0, badge_y0, badge_x1, badge_y0 + badge_h],
        radius=badge_h // 2,
        fill=(0, 0, 0, 72),
        outline=(r, g, b, 0),
        width=SCALE,
    )
    img = Image.alpha_composite(img, badge_layer)
    draw = ImageDraw.Draw(img)

    _draw_text(
        draw,
        (badge_x0 + pad_x - dt_bbox[0], badge_y0 + pad_y - dt_bbox[1]),
        dt_text, font_datetime, MUTED, stroke_width=0,
    )

    cursor_y += line_height(symbol.upper(), font_symbol) + _auto_gap(font_symbol, factor=0.45)

    # Main Price Value
    _draw_text(draw, (text_x, cursor_y), str(value), font_value, WHITE)
    cursor_y += line_height(str(value), font_value) + _auto_gap(font_value, factor=0.18)

    # Secondary values
    row_gap = _auto_gap(font_change, factor=0.4)
    cursor_y = min(cursor_y, footer_y - row_gap - line_height(str(percent), font_change)) + 5
    _draw_text(draw, (text_x, cursor_y), str(percent), font_change, MUTED)

    change_text = f"{change_symbol}{change}"
    bbox = draw.textbbox((0, 0), change_text, font=font_change)
    change_w = bbox[2] - bbox[0]
    change_x = W - MARGIN - change_w - 22
    _draw_text(draw, (change_x, cursor_y), change_text, font_change_only, color, stroke_width=1)

    # Draw Footers
    if levels:
        _draw_levels_footer(
            draw, levels,
            text_x=text_x, right_edge=W - MARGIN, top_y=footer_y,
            font_label=font_level_label, font_num=font_level_num,
            row_gap=LEVEL_ROW_GAP,
        )
    elif issueSummary:
        _draw_text(draw, (text_x, footer_y), issueSummary, font_summary, MUTED)

    # Mask Corners
    mask = _rounded_mask((W, H), CORNER_RADIUS)
    final = Image.new("RGBA", (W, H))
    final.paste(img, (0, 0), mask)
    final = final.convert("RGB")

    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    final.save(out_path)
    print(f"Saved {out_path}")
    return out_path
 
 
if __name__ == "__main__":
    issueName = "ABC"
    changeUpDown = "up"
    currentPrice = "11,020"
    percentChange = "0.18"
    change = 20
    issueSummary = "Upper (11,020) +4.36% | Lower (10,700) -2.73%"
 
    img_path = create_card_v2(
        issueName, changeUpDown, currentPrice, f"{percentChange}%", change, issueSummary
    )