import os
import json
import time
import urllib.request
import urllib.error
import textwrap

from PIL import Image, ImageDraw, ImageFont


GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]


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
  "image_headline": "Short headline suitable for a Pinterest image",
  "topic": "main topic"
}

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
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
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


# Save JSON
with open("generated_content.json", "w", encoding="utf-8") as f:
    json.dump(content, f, ensure_ascii=False, indent=2)

print("Saved generated_content.json")


# ------------------------------------------------
# CREATE PINTEREST IMAGE
# ------------------------------------------------

WIDTH = 1000
HEIGHT = 1500

image = Image.new(
    "RGB",
    (WIDTH, HEIGHT),
    (245, 247, 250)
)

draw = ImageDraw.Draw(image)


# Fonts
try:
    brand_font = ImageFont.truetype(
        "DejaVuSans-Bold.ttf", 36
    )

    topic_font = ImageFont.truetype(
        "DejaVuSans-Bold.ttf", 32
    )

    headline_font = ImageFont.truetype(
        "DejaVuSans-Bold.ttf", 76
    )

    small_font = ImageFont.truetype(
        "DejaVuSans.ttf", 30
    )

except OSError:
    brand_font = ImageFont.load_default()
    topic_font = ImageFont.load_default()
    headline_font = ImageFont.load_default()
    small_font = ImageFont.load_default()


# Top banner
draw.rounded_rectangle(
    (70, 70, 930, 180),
    radius=30,
    fill=(25, 35, 55)
)

draw.text(
    (500, 125),
    "AI BUSINESS TOOLKIT",
    font=brand_font,
    fill="white",
    anchor="mm"
)


# Topic label
topic = content["topic"].upper()

draw.rounded_rectangle(
    (90, 270, 910, 355),
    radius=25,
    fill=(220, 230, 245)
)

draw.text(
    (500, 312),
    topic,
    font=topic_font,
    fill=(25, 35, 55),
    anchor="mm"
)


# Headline
headline = content["image_headline"]

wrapped_headline = textwrap.fill(
    headline,
    width=18
)

draw.multiline_text(
    (500, 650),
    wrapped_headline,
    font=headline_font,
    fill=(20, 25, 35),
    anchor="mm",
    align="center",
    spacing=22
)


# Divider
draw.rounded_rectangle(
    (250, 930, 750, 945),
    radius=7,
    fill=(80, 110, 180)
)


# Supporting message
supporting_text = (
    "Practical AI tools and automation ideas "
    "for building smarter online businesses."
)

wrapped_support = textwrap.fill(
    supporting_text,
    width=38
)

draw.multiline_text(
    (500, 1070),
    wrapped_support,
    font=small_font,
    fill=(70, 75, 85),
    anchor="mm",
    align="center",
    spacing=12
)


# Bottom branding box
draw.rounded_rectangle(
    (100, 1270, 900, 1400),
    radius=30,
    fill=(25, 35, 55)
)

draw.text(
    (500, 1335),
    "AI Business Toolkit",
    font=brand_font,
    fill="white",
    anchor="mm"
)


# Save image
image.save(
    "pinterest_image.png",
    quality=95
)

print("Saved pinterest_image.png")
