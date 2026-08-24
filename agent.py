import os
import json
import time
import urllib.request
import urllib.error
import random
import textwrap

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

WIDTH = 1000
HEIGHT = 1500

CONTENT_FILE = "generated_content.json"
IMAGE_FILE = "pinterest_image.png"


# ============================================================
# GEMINI CONTENT GENERATION
# ============================================================

prompt = """
You are the content agent for AI Business Toolkit.

Create ONE useful Pinterest post for people interested in:
- starting an online business
- AI tools
- business automation
- free or low-cost online business tools
- productivity tools for small businesses

Choose ONE specific useful idea.

Avoid repeating generic phrases such as:
"Start your business with free AI tools."

Return valid JSON only in exactly this structure:

{
  "title": "Pinterest title under 90 characters",
  "description": "Useful Pinterest description under 450 characters",
  "image_headline": "Strong useful headline, maximum 8 words",
  "topic": "Short category, maximum 4 words",
  "image_subtitle": "One useful supporting sentence, maximum 12 words"
}

Requirements:

The content must teach or suggest something useful.

The image headline must:
- be easy to understand
- be suitable for Pinterest
- contain no more than 8 words
- avoid clickbait
- vary between generations

The description must explain what the reader will learn.

Do not make income guarantees.
Do not invent statistics.
Do not use fake urgency.
Do not claim personal experience.
Do not promise easy money.
Do not produce misleading financial claims.

Return JSON only.
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
        "responseMimeType": "application/json",
        "temperature": 0.9
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


# ============================================================
# CALL GEMINI WITH RETRIES
# ============================================================

result = None

for attempt in range(3):

    try:

        print(
            f"Calling Gemini - attempt {attempt + 1}"
        )

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

        print("Gemini HTTP error:")
        print(error_body)

        if e.code in (429, 500, 502, 503, 504) and attempt < 2:

            print("Waiting before retry...")
            time.sleep(30)

        else:

            raise

    except urllib.error.URLError as e:

        print("Network error:", e)

        if attempt < 2:

            time.sleep(20)

        else:

            raise


if result is None:
    raise RuntimeError("Gemini did not return a result.")


# ============================================================
# PARSE GEMINI RESPONSE
# ============================================================

try:

    text = (
        result["candidates"][0]
        ["content"]["parts"][0]["text"]
    )

    content = json.loads(text)

except (KeyError, IndexError, json.JSONDecodeError) as e:

    print("Unexpected Gemini response:")
    print(json.dumps(result, indent=2))

    raise RuntimeError(
        "Could not parse Gemini response."
    ) from e


required_fields = [
    "title",
    "description",
    "image_headline",
    "topic",
    "image_subtitle"
]

for field in required_fields:

    if field not in content:
        raise RuntimeError(
            f"Gemini response is missing: {field}"
        )


# ============================================================
# CLEAN CONTENT
# ============================================================

for key in required_fields:

    content[key] = str(
        content[key]
    ).strip()


content["title"] = content["title"][:90]

content["description"] = content["description"][:450]


print()
print("AI BUSINESS TOOLKIT")
print("----------------------------------")
print("Title:", content["title"])
print("Description:", content["description"])
print("Image headline:", content["image_headline"])
print("Topic:", content["topic"])
print("Image subtitle:", content["image_subtitle"])
print()


# ============================================================
# SAVE JSON
# ============================================================

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


print(f"Saved {CONTENT_FILE}")


# ============================================================
# DESIGN THEMES
# ============================================================

themes = [

    {
        "background": (245, 248, 252),
        "dark": (20, 31, 51),
        "accent": (55, 104, 190),
        "light": (222, 233, 249),
        "text": (20, 27, 40),
        "secondary": (75, 83, 96)
    },

    {
        "background": (248, 247, 242),
        "dark": (29, 40, 43),
        "accent": (48, 121, 105),
        "light": (220, 238, 231),
        "text": (24, 31, 34),
        "secondary": (73, 82, 80)
    },

    {
        "background": (248, 246, 251),
        "dark": (40, 31, 61),
        "accent": (107, 78, 171),
        "light": (233, 226, 246),
        "text": (32, 27, 43),
        "secondary": (79, 72, 91)
    },

    {
        "background": (249, 247, 243),
        "dark": (35, 36, 40),
        "accent": (183, 105, 54),
        "light": (243, 229, 216),
        "text": (31, 31, 34),
        "secondary": (82, 77, 72)
    }
]

theme = random.choice(themes)


# ============================================================
# CREATE IMAGE
# ============================================================

image = Image.new(
    "RGB",
    (WIDTH, HEIGHT),
    theme["background"]
)

draw = ImageDraw.Draw(image)


# ============================================================
# FONTS
# ============================================================

def load_font(size, bold=False):

    filename = (
        "DejaVuSans-Bold.ttf"
        if bold
        else "DejaVuSans.ttf"
    )

    try:
        return ImageFont.truetype(
            filename,
            size
        )

    except OSError:
        return ImageFont.load_default()


brand_font = load_font(31, True)
topic_font = load_font(27, True)
headline_font = load_font(78, True)
subtitle_font = load_font(31)
feature_font = load_font(25, True)
footer_font = load_font(24, True)
icon_font = load_font(37, True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def rounded_box(
    xy,
    fill,
    radius=20
):

    draw.rounded_rectangle(
        xy,
        radius=radius,
        fill=fill
    )


def fit_headline(
    text,
    max_width=820,
    max_height=380
):

    for font_size in range(
        82,
        51,
        -2
    ):

        font = load_font(
            font_size,
            True
        )

        for wrap_width in range(
            14,
            24
        ):

            wrapped = textwrap.fill(
                text,
                width=wrap_width
            )

            box = draw.multiline_textbbox(
                (0, 0),
                wrapped,
                font=font,
                spacing=15
            )

            width = box[2] - box[0]
            height = box[3] - box[1]

            if (
                width <= max_width
                and
                height <= max_height
            ):

                return wrapped, font

    return (
        textwrap.fill(
            text,
            width=18
        ),
        load_font(52, True)
    )


# ============================================================
# BACKGROUND GRAPHICS
# ============================================================

draw.ellipse(
    (
        720,
        -170,
        1160,
        270
    ),
    fill=theme["light"]
)

draw.ellipse(
    (
        -250,
        1160,
        260,
        1670
    ),
    fill=theme["light"]
)


# Decorative lines

draw.rounded_rectangle(
    (
        80,
        180,
        260,
        191
    ),
    radius=5,
    fill=theme["accent"]
)


# ============================================================
# BRAND
# ============================================================

draw.text(
    (80, 100),
    "AI BUSINESS TOOLKIT",
    font=brand_font,
    fill=theme["dark"]
)


# ============================================================
# AI VISUAL
# ============================================================

card_left = 690
card_top = 75
card_right = 910
card_bottom = 295

rounded_box(
    (
        card_left,
        card_top,
        card_right,
        card_bottom
    ),
    theme["dark"],
    42
)


centre_x = (
    card_left + card_right
) // 2

centre_y = (
    card_top + card_bottom
) // 2


draw.ellipse(
    (
        centre_x - 55,
        centre_y - 55,
        centre_x + 55,
        centre_y + 55
    ),
    outline="white",
    width=7
)


draw.text(
    (
        centre_x,
        centre_y
    ),
    "AI",
    font=icon_font,
    fill="white",
    anchor="mm"
)


# Circuit lines

draw.line(
    (
        centre_x,
        centre_y - 85,
        centre_x,
        centre_y - 55
    ),
    fill="white",
    width=7
)

draw.line(
    (
        centre_x,
        centre_y + 55,
        centre_x,
        centre_y + 85
    ),
    fill="white",
    width=7
)

draw.line(
    (
        centre_x - 85,
        centre_y,
        centre_x - 55,
        centre_y
    ),
    fill="white",
    width=7
)

draw.line(
    (
        centre_x + 55,
        centre_y,
        centre_x + 85,
        centre_y
    ),
    fill="white",
    width=7
)


# ============================================================
# TOPIC LABEL
# ============================================================

topic = content["topic"].upper()

topic_bbox = draw.textbbox(
    (0, 0),
    topic,
    font=topic_font
)

topic_text_width = (
    topic_bbox[2] -
    topic_bbox[0]
)

topic_width = min(
    760,
    max(
        260,
        topic_text_width + 80
    )
)


rounded_box(
    (
        80,
        365,
        80 + topic_width,
        440
    ),
    theme["light"],
    24
)


draw.text(
    (
        80 + topic_width / 2,
        402
    ),
    topic,
    font=topic_font,
    fill=theme["dark"],
    anchor="mm"
)


# ============================================================
# HEADLINE
# ============================================================

headline = content[
    "image_headline"
]

wrapped_headline, final_headline_font = (
    fit_headline(headline)
)


draw.multiline_text(
    (
        80,
        515
    ),
    wrapped_headline,
    font=final_headline_font,
    fill=theme["text"],
    spacing=15
)


headline_bbox = draw.multiline_textbbox(
    (
        80,
        515
    ),
    wrapped_headline,
    font=final_headline_font,
    spacing=15
)

headline_bottom = headline_bbox[3]


# ============================================================
# ACCENT LINE
# ============================================================

accent_y = min(
    headline_bottom + 65,
    910
)

draw.rounded_rectangle(
    (
        80,
        accent_y,
        475,
        accent_y + 13
    ),
    radius=6,
    fill=theme["accent"]
)


# ============================================================
# SUBTITLE
# ============================================================

subtitle = content[
    "image_subtitle"
]

wrapped_subtitle = textwrap.fill(
    subtitle,
    width=42
)


subtitle_y = accent_y + 70


draw.multiline_text(
    (
        80,
        subtitle_y
    ),
    wrapped_subtitle,
    font=subtitle_font,
    fill=theme["secondary"],
    spacing=11
)


# ============================================================
# VALUE LABELS
# ============================================================

features = [
    "AI TOOLS",
    "AUTOMATION",
    "ONLINE BUSINESS"
]

feature_y = 1160


for feature in features:

    bbox = draw.textbbox(
        (0, 0),
        feature,
        font=feature_font
    )

    text_width = (
        bbox[2] -
        bbox[0]
    )

    box_width = (
        text_width + 60
    )

    rounded_box(
        (
            80,
            feature_y,
            80 + box_width,
            feature_y + 62
        ),
        theme["light"],
        20
    )

    draw.text(
        (
            80 + box_width / 2,
            feature_y + 31
        ),
        feature,
        font=feature_font,
        fill=theme["dark"],
        anchor="mm"
    )

    feature_y += 78


# ============================================================
# FOOTER BRAND
# ============================================================

draw.ellipse(
    (
        80,
        1380,
        132,
        1432
    ),
    fill=theme["accent"]
)


draw.text(
    (
        106,
        1406
    ),
    "AI",
    font=load_font(18, True),
    fill="white",
    anchor="mm"
)


draw.text(
    (
        920,
        1407
    ),
    "AI Business Toolkit",
    font=footer_font,
    fill=theme["dark"],
    anchor="ra"
)


# ============================================================
# SAVE PINTEREST IMAGE
# ============================================================

image.save(
    IMAGE_FILE,
    format="PNG"
)


print(
    f"Saved {IMAGE_FILE}"
)

print()
print("Agent completed successfully.")
