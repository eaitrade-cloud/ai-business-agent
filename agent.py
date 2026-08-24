import os
import json
import time
import urllib.request
import urllib.error
import socket

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

prompt = """
You are the content agent for AI Business Toolkit.

Create ONE useful Pinterest post for people interested in:
- starting an online business
- AI tools
- business automation
- free or low-cost online business tools

The goal is useful educational content, not spam.

Return valid JSON only in exactly this structure:

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
    "models/gemini-2.5-flash:generateContent"
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
        "responseMimeType": "application/json"
    }
}

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": GEMINI_API_KEY
}

request = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers=headers,
    method="POST"
)

result = None

for attempt in range(3):
    try:
        print(f"Gemini request attempt {attempt + 1}/3")

        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        break

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")

        print(f"Gemini HTTP error: {e.code}")
        print(error_body)

        if e.code not in (429, 500, 502, 503, 504) or attempt == 2:
            raise

        print("Temporary Gemini error. Retrying in 60 seconds...")
        time.sleep(60)

    except (TimeoutError, socket.timeout) as e:
        print(f"Gemini request timed out: {e}")

        if attempt == 2:
            raise

        print("Retrying in 60 seconds...")
        time.sleep(60)

if result is None:
    raise RuntimeError("Gemini did not return a result.")

try:
    text = result["candidates"][0]["content"]["parts"][0]["text"]
except (KeyError, IndexError) as e:
    print("Unexpected Gemini response:")
    print(json.dumps(result, indent=2))
    raise RuntimeError("Gemini returned an unexpected response.") from e

content = json.loads(text)

required_fields = [
    "title",
    "description",
    "image_headline",
    "topic"
]

for field in required_fields:
    if field not in content:
        raise ValueError(f"Gemini response is missing: {field}")

print()
print("AI BUSINESS TOOLKIT - TEST CONTENT")
print("----------------------------------")
print("Title:", content["title"])
print("Description:", content["description"])
print("Image headline:", content["image_headline"])
print("Topic:", content["topic"])

with open(
    "generated_content.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        content,
        f,
        indent=2,
        ensure_ascii=False
    )

print()
print("generated_content.json created successfully.")
