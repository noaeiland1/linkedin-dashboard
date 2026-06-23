#!/usr/bin/env python3
"""Generate LinkedIn content for Noa's dashboard using Claude API."""

import os
import json
import urllib.request
import urllib.error
import datetime
import re
import sys


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: {path} not found", file=sys.stderr)
        return ""


brand     = read_file("context/brand-guidelines.md")
me        = read_file("context/me.md")
business  = read_file("context/business.md")
strategy  = read_file("1-strategy/strategy.md")
profiles  = read_file("4-data/profiles-to-follow.md")
sop02     = read_file("3-sops/02-write-post.md")
sop03     = read_file("3-sops/03-rewrite-and-sharpen.md")

today = datetime.datetime.now().strftime("%d.%m.%Y")
now   = datetime.datetime.now().strftime("%H:%M")

try:
    with open("content.json", "r", encoding="utf-8") as f:
        existing = json.load(f)
    published_log = existing.get("publishedLog", [])
except Exception:
    published_log = []

prompt = f"""אתה עוזר תוכן ללינקדאין של נוע אילנד. היום: {today}.

=== מי היא נוע ===
{me}

=== הנחיות מותג ===
{brand}

=== אסטרטגיית תוכן ===
{strategy}

=== עסק ===
{business}

=== פרופילים למעקב — לזיהוי נושאים חמים ===
{profiles}

=== איך לכתוב פוסט (SOP 02) ===
{sop02}

=== איך לחדד פוסט (SOP 03) ===
{sop03}

---

המשימה: צור תוכן לדשבורד הלינקדאין של נוע לתאריך {today}.

החזר JSON תקני בלבד — ללא markdown, ללא הסבר, ללא ```json:

{{
  "topics": [
    {{
      "id": "topic-1",
      "name": "שם הנושא (עד 8 מילים)",
      "hot": "מה רועש עכשיו סביב הנושא הזה",
      "angle": "הזווית הייחודית של נוע — לא עוד פוסט גנרי",
      "potential": "גבוה",
      "example": "פוסט לדוגמה שיכול לצאת מהפרופילים ברשימה"
    }},
    {{
      "id": "topic-2",
      "name": "...",
      "hot": "...",
      "angle": "...",
      "potential": "בינוני",
      "example": "..."
    }},
    {{
      "id": "topic-3",
      "name": "...",
      "hot": "...",
      "angle": "...",
      "potential": "גבוה",
      "example": "..."
    }}
  ],
  "posts": [
    {{
      "id": "post-1",
      "topicId": "topic-1",
      "topicName": "שם הנושא",
      "type": "trending",
      "text": "הפוסט המלא..."
    }},
    {{
      "id": "post-2",
      "topicId": "topic-2",
      "topicName": "שם הנושא",
      "type": "trending",
      "text": "..."
    }},
    {{
      "id": "post-3",
      "topicId": "topic-3",
      "topicName": "שם הנושא",
      "type": "trending",
      "text": "..."
    }},
    {{
      "id": "post-4",
      "topicId": "wildcard",
      "topicName": "Wild Card",
      "type": "wildcard",
      "text": "..."
    }},
    {{
      "id": "post-5",
      "topicId": "inner-shift",
      "topicName": "Inner Shift",
      "type": "inner-shift",
      "text": "..."
    }}
  ]
}}

כללים לנושאים:
- 3 נושאים רלוונטיים לקהל של נוע: מנהלים בכירים, יזמים, ארגונים בשינוי
- נסה לזהות מה הפרופילים ברשימה מדברים עליו עכשיו
- "angle" חייב להיות הזווית הספציפית של נוע — 17 שנות ניסיון, Inner Shift, שינוי אמיתי

כללים לפוסטים:
- כתוב בעברית
- משפט אחד לשורה — שבר שורה (\\n) בין כל משפט
- ללא מקפים ארוכים (—), ללא סימני קריאה, ללא buzzwords
- HOOK: ספציפי ואמיתי — עוצר מנהל בכיר מלגלול
- גוף: 6-12 שורות, בונה דרך ניסיון אמיתי או מחקר
- CTA: שאלה רכה או הזמנה, לא מכירה
- פוסטים 1-3: מבוססים על הנושאים
- פוסט 4 (wildcard): תובנה נצחית מ-17 שנות ניסיון
- פוסט 5 (inner-shift): מדע ה-behavioral change דרך עדשת מנהיגות — לא wellness
- 150-300 מילים לפוסט
"""

api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
    sys.exit(1)

payload = json.dumps({
    "model": "claude-sonnet-4-6",
    "max_tokens": 4096,
    "messages": [{"role": "user", "content": prompt}]
}).encode("utf-8")

req = urllib.request.Request(
    "https://api.anthropic.com/v1/messages",
    data=payload,
    headers={
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    },
)

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
except urllib.error.HTTPError as e:
    print(f"ERROR: HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
    sys.exit(1)

text = result["content"][0]["text"].strip()
text = re.sub(r"^```\w*\n?", "", text)
text = re.sub(r"\n?```$", "", text).strip()

try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    print(f"ERROR: Failed to parse Claude response as JSON: {e}", file=sys.stderr)
    print(f"Response was:\n{text[:500]}", file=sys.stderr)
    sys.exit(1)

output = {
    "generatedAt": f"{today} {now}",
    "topics": data["topics"],
    "posts": data["posts"],
    "publishedLog": published_log,
}

with open("content.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ {today} {now}: {len(data['topics'])} topics, {len(data['posts'])} posts")
