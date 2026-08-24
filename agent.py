import os
import json
import time
import urllib.request
import urllib.error
import textwrap
import random

from PIL import Image, ImageDraw, ImageFont


GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]


# ------------------------------------------------
# ASK GEMINI TO CREATE THE CONTENT
# ------------------------------------------------

prompt = """
You are the content agent for AI Business Toolkit.

Create ONE useful Pinterest post for people interested in:
- starting an online business
- AI tools
- business automation
- free or low-cost online business tools

The goal is useful educational content, not spam.

Return valid JSON only with:
{
  "title": "Pinterest title under 90 characters",
  "description": "Useful Pinterest description under 450 characters",
  "image_headline": "Short powerful headline, maximum 8 words",
  "topic": "Short topic name, maximum 4 words",
  "image_subtitle": "One short useful supporting sentence, maximum 12 words"
}

Make the headline easy to read on a Pinterest image.

Do not make income guarantees.
Do not invent statistics.
Do not use clickbait.
Do not claim personal experience.
"""


url = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-3.5-flash:generateContent"
)


payload = {
    "contents": [
        {
            "parts": [
                {"text": prompt}
            ]
        }
    ],
    "generationConfig": {
        "responseMimeType": "application/json"
    }
}


request = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    },
    method="POST"
)


for attempt in range(3):

    try:

        with urllib.request.urlopen(
            request,
            timeout=180
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        break

    except urllib.error.HTTPError as e:

        error_body = e.read().decode("utf-8")
        print(error_body)

        if e.code in (429, 503) and attempt < 2:

            time.sleep(60)

        else:

            raise


text = result["candidates"][0]["content"]["parts"][0]["text"]

content = json.loads(text)


print("AI BUSINESS TOOLKIT")
print("----------------------------------")
print("Title:", content["title"])
print("Description:", content["description"])
print("Image headline:", content["image_headline"])
print("Topic:", content["topic"])
print("Image subtitle:", content["image_subtitle"])


# ------------------------------------------------
# SAVE CONTENT
# ------------------------------------------------

with open(
    "generated_content.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        content,
        f,
        ensure_ascii=False,
        indent=2
    )


print("Saved generated_content.json")


# ------------------------------------------------
# PINTEREST IMAGE
# ------------------------------------------------

WIDTH = 1000
HEIGHT = 1500


# ------------------------------------------------
# DESIGN THEMES
# ------------------------------------------------

themes = [

    {
        "background": (244, 247, 252),
        "dark": (18, 29, 52),
        "accent": (62, 105, 190),
        "light": (222, 232, 248),
        "text": (20, 27, 40)
    },

    {
        "background": (248, 246, 241),
        "dark": (31, 38, 44),
        "accent": (52, 120, 110),
        "light": (221, 237, 232),
        "text": (25, 30, 35)
    },

    {
        "background": (247, 245, 250),
        "dark": (37, 29, 58),
        "accent": (108, 78, 170),
        "light": (232, 224, 245),
        "text": (30, 25, 40)
    }
]


theme = random.choice(themes)


image = Image.new(
    "RGB",
    (WIDTH, HEIGHT),
    theme["background"]
)


draw = ImageDraw.Draw(image)


# ------------------------------------------------
# FONTS
# ------------------------------------------------

try:

    brand_font = ImageFont.truetype(
        "DejaVuSans-Bold.ttf",
        34
    )

    topic_font = ImageFont.truetype(
        "DejaVuSans-Bold.ttf",
        28
    )

    headline_font = ImageFont.truetype(
        "DejaVuSans-Bold.ttf",
        82
    )

    subtitle_font = ImageFont.truetype(
        "DejaVuSans.ttf",
        34
    )

    small_bold_font = ImageFont.truetype(
        "DejaVuSans-Bold.ttf",
        27
    )

except OSError:

    brand_font = ImageFont.load_default()
    topic_font = ImageFont.load_default()
    headline_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()
    small_bold_font = ImageFont.load_default()


# ------------------------------------------------
# DECORATIVE BACKGROUND
# ------------------------------------------------

draw.ellipse(
    (700, -180, 1150, 270),
    fill=theme["light"]
)

draw.ellipse(
    (-220, 1120, 250, 1590),
    fill=theme["light"]
)


# Small decorative circles

for x, y, size in [
    (110, 240, 22),
    (155, 240, 12),
    (190, 240, 8)
]:

    draw.ellipse(
        (
            x - size,
            y - size,
            x + size,
            y + size
        ),
        fill=theme["accent"]
    )


# ------------------------------------------------
# TOP BRAND
# ------------------------------------------------

draw.text(
    (80, 95),
    "AI BUSINESS TOOLKIT",
    font=brand_font,
    fill=theme["dark"]
)


draw.rounded_rectangle(
    (80, 155, 240, 165),
    radius=5,
    fill=theme["accent"]
)


# ------------------------------------------------
# TOP VISUAL CARD
# ------------------------------------------------

draw.rounded_rectangle(
    (650, 80, 900, 330),
    radius=45,
    fill=theme["dark"]
)


# AI-style simple graphic

draw.ellipse(
    (715, 140, 835, 260),
    outline="white",
    width=8
)


draw.line(
    (775, 110, 775, 140),
    fill="white",
    width=8
)

draw.line(
    (775, 260, 775, 290),
    fill="white",
    width=8
)

draw.line(
    (685, 200, 715, 200),
    fill="white",
    width=8
)

draw.line(
    (835, 200, 865, 200),
    fill="white",
    width=8
)


draw.text(
    (775, 200),
    "AI",
    font=brand_font,
    fill="white",
    anchor="mm"
)


# ------------------------------------------------
# TOPIC
# ------------------------------------------------

topic = content["topic"].upper()


topic_width = min(
    760,
    max(
        300,
        len(topic) * 22
    )
)


draw.rounded_rectangle(
    (
        80,
        380,
        80 + topic_width,
        460
    ),
    radius=25,
    fill=theme["light"]
)


draw.text(
    (
        80 + topic_width / 2,
        420
    ),
    topic,
    font=topic_font,
    fill=theme["dark"],
    anchor="mm"
)


# ------------------------------------------------
# HEADLINE
# ------------------------------------------------

headline = content["image_headline"]


wrapped_headline = textwrap.fill(
    headline,
    width=17
)


draw.multiline_text(
    (80, 540),
    wrapped_headline,
    font=headline_font,
    fill=theme["text"],
    spacing=18
)


# ------------------------------------------------
# ACCENT LINE
# ------------------------------------------------

draw.rounded_rectangle(
    (80, 900, 520, 915),
    radius=7,
    fill=theme["accent"]
)


# ------------------------------------------------
# SUBTITLE
# ------------------------------------------------

subtitle = content.get(
    "image_subtitle",
    "Practical AI tools for building your online business."
)


wrapped_subtitle = textwrap.fill(
    subtitle,
    width=38
)


draw.multiline_text(
    (80, 970),
    wrapped_subtitle,
    font=subtitle_font,
    fill=(70, 75, 85),
    spacing=12
)


# ------------------------------------------------
# FEATURE BOXES
# ------------------------------------------------

features = [
    "AI TOOLS",
    "AUTOMATION",
    "ONLINE BUSINESS"
]


box_y = 1170


for feature in features:

    text_box = draw.textbbox(
        (0, 0),
        feature,
        font=small_bold_font
    )

    text_width = (
        text_box[2] -
        text_box[0]
    )

    box_width = text_width + 55


    draw.rounded_rectangle(
        (
            80,
            box_y,
            80 + box_width,
            box_y + 65
        ),
        radius=20,
        fill=theme["light"]
    )


    draw.text(
        (
            80 + box_width / 2,
            box_y + 32
        ),
        feature,
        font=small_bold_font,
        fill=theme["dark"],
        anchor="mm"
    )


    box_y += 85


# ------------------------------------------------
# BOTTOM BRAND
# ------------------------------------------------

draw.text(
    (920, 1415),
    "AI Business Toolkit",
    font=small_bold_font,
    fill=theme["dark"],
    anchor="ra"
)


draw.ellipse(
    (80, 1385, 130, 1435),
    fill=theme["accent"]
)


draw.text(
    (105, 1410),
    "AI",
    font=small_bold_font,
    fill="white",
    anchor="mm"
)


# ------------------------------------------------
# SAVE IMAGE
# ------------------------------------------------

image.save(
    "pinterest_image.png",
    quality=95
)


print("Saved pinterest_image.png")
print("Agent completed successfully.")
