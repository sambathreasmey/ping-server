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

def create_glass_card(symbol, status, value, percent, change, issueSummary):
    # Setup colors and scales
    colors = {"UP": "#4AFF47", "DOWN": "#FF0000", "EQUAL": "#FFFFFF"}
    status_upper = status.upper()
    color = colors.get(status_upper, "#000000")
    
    SCALE = 3
    W, H = 280 * SCALE, 125 * SCALE
    RADIUS = 25 * SCALE 

    # 1. Load Sharp Background
    try:
        bg_path = f"images/background-{status.lower()}.png"
        base_bg = Image.open(bg_path).convert("RGBA").resize((W, H))
    except:
        base_bg = Image.new("RGBA", (W, H), (40, 44, 52, 255))

    # 2. Create Blurred Layer
    # Blur the background heavily
    blurred_layer = base_bg.filter(ImageFilter.GaussianBlur(radius=10 * SCALE))

    # 3. Create Rounded Mask
    mask = Image.new("L", (W, H), 0)
    mask_draw = ImageDraw.Draw(mask)
    # The card area (e.g., slightly inset from the edges if you want)
    card_box = [10 * SCALE, 10 * SCALE, W - 10 * SCALE, H - 10 * SCALE]
    mask_draw.rounded_rectangle(card_box, radius=RADIUS, fill=255)

    # 4. Create Glass Tint (Optional but recommended)
    # Adds a faint white/dark glow so text is readable
    tint = Image.new("RGBA", (W, H), (255, 255, 255, 30)) # 30 = very transparent

    # 5. Composite Layers
    # Paste blurred version onto sharp background using the mask
    base_bg.paste(blurred_layer, (0, 0), mask=mask)
    # Paste the subtle tint over the blurred area using the same mask
    base_bg.alpha_composite(tint, (0, 0), (0, 0))

    # 6. Draw Sharp UI Elements
    draw = ImageDraw.Draw(base_bg)
    
    # Rounded Accent Bar (Pill shape on the left)
    draw.rounded_rectangle([10 * SCALE, 10 * SCALE, 22 * SCALE, H - 10 * SCALE], 
                           radius=RADIUS, fill=color)

    # Load and Draw Text
    try:
        font_main = ImageFont.truetype("fonts/DejaVuSans-Bold.ttf", 34 * SCALE)
        font_small = ImageFont.truetype("fonts/DejaVuSans-Bold.ttf", 24 * SCALE)
    except:
        font_main = font_small = ImageFont.load_default()

    draw.text((40 * SCALE, 25 * SCALE), symbol, fill=color, font=font_main)
    draw.text((40 * SCALE, 65 * SCALE), value, fill="#FFFFFF", font=font_main)

    # Save final result
    base_bg.save("images/output_v2.png")
    return "images/output_v2.png"