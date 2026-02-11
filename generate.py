from PIL import Image, ImageDraw, ImageFont, ImageFilter

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
    draw.text((35 * SCALE, 55 * SCALE), value, fill=color, font=font_main)
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

def create_card_v2(symbol, status, value, percent, change, issueSummary):
    # Colors for each card type
    colors = {
        "UP":    "#4AFF47",  # green
        "DOWN":  "#FF0000",  # red
        "EQUAL": "#FFFFFF",  # white/gray
    }

    change_symbols = {
        "UP":    "+",
        "DOWN":  "-",
        "EQUAL": "",
    }

    status_upper = status.upper()
    color = colors.get(status_upper, "#000000")
    change_symbol = change_symbols.get(status_upper, "")

    # 3× scale factor
    SCALE = 3
    W, H = 280 * SCALE, 125 * SCALE
    RADIUS = 20 * SCALE  # Rounded corner radius for the whole card

    # 1. Load and prepare background image
    try:
        bg_path = f"images/background-down-2.jpg" if status_upper == "UP-SKIP" else f"images/background-{status.lower()}.png"
        bg_img = Image.open(bg_path).convert("RGBA")
    except:
        bg_img = Image.new("RGBA", (W, H), (50, 50, 50, 255)) # Fallback
    
    bg_img = bg_img.resize((W, H))

    # 2. Apply Background Blur
    # Adjust radius for intensity (e.g., 5 * SCALE)
    bg_img = bg_img.filter(ImageFilter.GaussianBlur(radius=4 * SCALE))

    # 3. Create a Rounded Mask for the whole card
    # This gives the card its rounded corners against the final background
    mask = Image.new("L", (W, H), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle([0, 0, W, H], radius=RADIUS, fill=255)

    # 4. Create final image with transparency support
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.paste(bg_img, (0, 0), mask=mask)

    draw = ImageDraw.Draw(img)

    # 5. Rounded left border (accent bar)
    # We draw this on top of the blurred background
    draw.rounded_rectangle([-16 * SCALE, 0, 12 * SCALE, H], radius=RADIUS, fill=color)

    # Load Fonts
    try:
        font_main = ImageFont.truetype("fonts/DejaVuSans-Bold.ttf", 34 * SCALE)
        font_small = ImageFont.truetype("fonts/DejaVuSans-Bold.ttf", 26 * SCALE)
        font_smallest = ImageFont.truetype("fonts/DejaVuSans-Bold.ttf", 10 * SCALE)
    except Exception as e:
        font_main = font_small = font_smallest = ImageFont.load_default()

    # Draw text
    draw.text((35 * SCALE, 15 * SCALE), symbol, fill=color, font=font_main)
    draw.text((35 * SCALE, 55 * SCALE), value, fill=color, font=font_main)
    draw.text((35 * SCALE, 90 * SCALE), percent, fill=color, font=font_small)
    
    # Corrected white color for summary
    draw.text((127 * SCALE, 108 * SCALE), issueSummary, fill="#FFFFFF", font=font_smallest)

    # Dynamic X-position for change value
    text = change_symbol + str(change)
    bbox = draw.textbbox((0, 0), text, font=font_small)
    text_width = bbox[2] - bbox[0]
    draw.text(( (260 * SCALE) - text_width, 78 * SCALE), text, fill=color, font=font_small)

    # Save as PNG to preserve transparency/rounded corners
    filename = "images/output_v2.png"
    img.save(filename)
    print(f"✔ Saved {filename}")

    return filename

