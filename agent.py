import os
import json
import time
import random
import textwrap
import urllib.request
import urllib.error

from PIL import Image, ImageDraw, ImageFont


# --------------------------------------------------
# CONFIG
# --------------------------------------------------

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

MODEL = "gemini-3.5-flash"

WIDTH = 1000
HEIGHT = 1500

CONTENT_FILE = "generated_content.json"
IMAGE_FILE = "pinterest_image.png"


# --------------------------------------------------
# GEMINI CONTENT GENERATION
# --------------------------------------------------

prompt = """
You are the content agent for AI Business Toolkit.

Create ONE useful Pinterest post for people interested in:

- starting an online business
- practical AI tools
- business automation
- productivity
- free or low-cost online business tools

Choose a different practical angle each time.

The content must be educational and useful.

Avoid hype.
Do not make income guarantees.
Do not invent statistics.
Do not use clickbait.
Do not claim personal experience.

Return VALID JSON ONLY.

Use exactly this structure:

{
  "title": "Pinterest title under 90 characters",
  "description": "Pinterest description under 450 characters",
  "image_headline": "Short powerful headline, maximum 8 words",
  "image_subtitle": "One useful supporting sentence under 80 characters",
  "topic": "Short category",
  "tag1": "Short relevant tag",
  "tag2": "Short relevant tag",
  "tag3": "Short relevant tag"
}
"""

url = (
    "https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL}:generateContent?key={GEMINI_API_KEY}"
)

payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": prompt
                }
            ]
        }
    ],
    "generationConfig": {
        "temperature": 0.9,
        "responseMimeType": "application/json"
    }
}

data = json.dumps(payload).encode("utf-8")

request = urllib.request.Request(
    url,
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST"
)

result = None

for attempt in range(3):
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )
        break

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(error_body)

        if e.code in (429, 500, 502, 503, 504) and attempt < 2:
            print("Temporary API error. Retrying...")
            time.sleep(30 * (attempt + 1))
        else:
            raise

if result is None:
    raise RuntimeError("Gemini did not return a result.")


# --------------------------------------------------
# READ GEMINI RESPONSE
# --------------------------------------------------

text = (
    result["candidates"][0]
    ["content"]["parts"][0]["text"]
)

content = json.loads(text)

required_fields = [
    "title",
    "description",
    "image_headline",
    "image_subtitle",
    "topic",
    "tag1",
    "tag2",
    "tag3"
]

for field in required_fields:
    if field not in content:
        raise ValueError(f"Gemini response missing: {field}")


# --------------------------------------------------
# SAVE JSON
# --------------------------------------------------

with open(
    CONTENT_FILE,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        content,
        f,
        ensure_ascii=False,
        indent=2
    )

print("Generated content")
print("------------------------------")
print("Title:", content["title"])
print("Description:", content["description"])
print("Headline:", content["image_headline"])
print("Topic:", content["topic"])


# --------------------------------------------------
# FONT HELPERS
# --------------------------------------------------

def get_font(size, bold=False):
    possible_fonts = []

    if bold:
        possible_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ]
    else:
        possible_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]

    for font_path in possible_fonts:
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)

    return ImageFont.load_default()


font_brand = get_font(31, True)
font_category = get_font(27, True)
font_headline = get_font(72, True)
font_subtitle = get_font(29)
font_tag = get_font(24, True)
font_footer = get_font(23, True)
font_ai = get_font(35, True)


# --------------------------------------------------
# TEXT WRAPPING
# --------------------------------------------------

def wrap_text(draw, text, font, max_width):
    words = text.split()

    lines = []
    current_line = ""

    for word in words:
        test_line = (
            current_line + " " + word
        ).strip()

        bbox = draw.textbbox(
            (0, 0),
            test_line,
            font=font
        )

        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


# --------------------------------------------------
# CREATE PINTEREST IMAGE
# --------------------------------------------------

image = Image.new(
    "RGB",
    (WIDTH, HEIGHT),
    (247, 247, 244)
)

draw = ImageDraw.Draw(image)


# --------------------------------------------------
# BACKGROUND DECORATION
# --------------------------------------------------

layout = random.choice([1, 2, 3])

if layout == 1:
    draw.rectangle(
        (0, 0, 26, HEIGHT),
        fill=(39, 48, 65)
    )

    draw.rectangle(
        (26, 0, 42, HEIGHT),
        fill=(207, 221, 216)
    )

elif layout == 2:
    draw.rectangle(
        (0, 0, WIDTH, 22),
        fill=(39, 48, 65)
    )

    draw.rectangle(
        (0, HEIGHT - 28, WIDTH, HEIGHT),
        fill=(207, 221, 216)
    )

else:
    draw.rectangle(
        (0, 0, WIDTH, 180),
        fill=(238, 242, 239)
    )


# --------------------------------------------------
# BRAND
# --------------------------------------------------

draw.text(
    (100, 100),
    "AI BUSINESS TOOLKIT",
    font=font_brand,
    fill=(54, 63, 72)
)

draw.rounded_rectangle(
    (100, 150, 245, 160),
    radius=5,
    fill=(80, 105, 103)
)


# --------------------------------------------------
# AI ICON
# --------------------------------------------------

icon_x1 = 735
icon_y1 = 75
icon_x2 = 900
icon_y2 = 240

draw.rounded_rectangle(
    (icon_x1, icon_y1, icon_x2, icon_y2),
    radius=32,
    fill=(48, 54, 66)
)

cx = (icon_x1 + icon_x2) // 2
cy = (icon_y1 + icon_y2) // 2

draw.ellipse(
    (cx - 45, cy - 45, cx + 45, cy + 45),
    outline=(245, 245, 245),
    width=6
)

ai_bbox = draw.textbbox(
    (0, 0),
    "AI",
    font=font_ai
)

ai_width = ai_bbox[2] - ai_bbox[0]
ai_height = ai_bbox[3] - ai_bbox[1]

draw.text(
    (
        cx - ai_width / 2,
        cy - ai_height / 2 - 5
    ),
    "AI",
    font=font_ai,
    fill=(255, 255, 255)
)

draw.line(
    (cx, cy - 75, cx, cy - 48),
    fill=(255, 255, 255),
    width=5
)

draw.line(
    (cx, cy + 48, cx, cy + 75),
    fill=(255, 255, 255),
    width=5
)

draw.line(
    (cx - 75, cy, cx - 48, cy),
    fill=(255, 255, 255),
    width=5
)

draw.line(
    (cx + 48, cy, cx + 75, cy),
    fill=(255, 255, 255),
    width=5
)


# --------------------------------------------------
# CATEGORY
# --------------------------------------------------

topic = content["topic"].upper()

topic_bbox = draw.textbbox(
    (0, 0),
    topic,
    font=font_category
)

topic_width = topic_bbox[2] - topic_bbox[0]

draw.rounded_rectangle(
    (
        100,
        325,
        min(900, 145 + topic_width),
        385
    ),
    radius=18,
    fill=(231, 237, 234)
)

draw.text(
    (122, 340),
    topic,
    font=font_category,
    fill=(62, 73, 78)
)


# --------------------------------------------------
# MAIN HEADLINE
# --------------------------------------------------

headline = content["image_headline"]

headline_lines = wrap_text(
    draw,
    headline,
    font_headline,
    790
)

headline_y = 465

for line in headline_lines[:4]:

    draw.text(
        (100, headline_y),
        line,
        font=font_headline,
        fill=(30, 34, 39)
    )

    headline_y += 88


# --------------------------------------------------
# ACCENT LINE
# --------------------------------------------------

line_y = headline_y + 20

draw.rounded_rectangle(
    (100, line_y, 440, line_y + 10),
    radius=5,
    fill=(75, 103, 101)
)


# --------------------------------------------------
# SUBTITLE
# --------------------------------------------------

subtitle_y = line_y + 65

subtitle_lines = wrap_text(
    draw,
    content["image_subtitle"],
    font_subtitle,
    760
)

for line in subtitle_lines[:3]:

    draw.text(
        (100, subtitle_y),
        line,
        font=font_subtitle,
        fill=(89, 94, 97)
    )

    subtitle_y += 42


# --------------------------------------------------
# TAGS
# --------------------------------------------------

tags = [
    content["tag1"],
    content["tag2"],
    content["tag3"]
]

tag_y = 1190

for tag in tags:

    tag_text = tag.upper()

    bbox = draw.textbbox(
        (0, 0),
        tag_text,
        font=font_tag
    )

    tag_width = bbox[2] - bbox[0]

    draw.rounded_rectangle(
        (
            100,
            tag_y,
            min(650, 145 + tag_width),
            tag_y + 50
        ),
        radius=15,
        fill=(238, 240, 237)
    )

    draw.text(
        (120, tag_y + 11),
        tag_text,
        font=font_tag,
        fill=(62, 68, 72)
    )

    tag_y += 65


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

draw.ellipse(
    (100, 1400, 145, 1445),
    fill=(54, 63, 72)
)

small_ai_font = get_font(17, True)

draw.text(
    (112, 1411),
    "AI",
    font=small_ai_font,
    fill=(255, 255, 255)
)

footer_text = "AI Business Toolkit"

footer_bbox = draw.textbbox(
    (0, 0),
    footer_text,
    font=font_footer
)

footer_width = footer_bbox[2] - footer_bbox[0]

draw.text(
    (
        WIDTH - footer_width - 100,
        1408
    ),
    footer_text,
    font=font_footer,
    fill=(60, 65, 70)
)


# --------------------------------------------------
# SAVE IMAGE
# --------------------------------------------------

image.save(
    IMAGE_FILE,
    "PNG",
    optimize=True
)

print("Saved:", CONTENT_FILE)
print("Saved:", IMAGE_FILE)
print("Selected layout:", layout)
