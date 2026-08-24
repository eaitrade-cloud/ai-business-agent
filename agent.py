import os
import json
import urllib.request
import time

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
    "models/gemini-2.5-flash-lite:generateContent"
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
        if e.code not in (429, 503) or attempt == 2:
            raise
        time.sleep(60)
    except TimeoutError:
        if attempt == 2:
            raise
        time.sleep(60)

text = result["candidates"][0]["content"]["parts"][0]["text"]
content = json.loads(text)

print("AI BUSINESS TOOLKIT — TEST CONTENT")
print("----------------------------------")
print("Title:", content["title"])
print("Description:", content["description"])
print("Image headline:", content["image_headline"])
print("Topic:", content["topic"])

with open("generated_content.json", "w", encoding="utf-8") as f:
    json.dump(content, f, indent=2, ensure_ascii=False)
