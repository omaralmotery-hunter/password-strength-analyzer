"""
ai_predictor.py — AI-powered password prediction using Anthropic API
"""

import json
import re

SYSTEM_PROMPT = """You are a cybersecurity researcher specializing in password auditing and human behavior analysis.

Your task: given a person's personal details, generate the most comprehensive list of passwords they are realistically likely to use — exactly as a professional penetration tester would during an authorized security audit.

Base your predictions on:
- Name combinations (first, last, nickname, initials)
- Dates (birth year, full date, day+month, reversed)
- Meaningful people: partner, children, parents, friends
- Pets, places, teams, hobbies, job, company
- Favorite numbers, phone digits, ID patterns
- Common human patterns: appending 123, !, adding birth year, capitalizing first letter
- Leet speak: a→@/4, e→3, i→1/!, o→0, s→5/$, t→7
- Mixed combinations of all the above
- Common prefixes/suffixes: 123, 1234, !, !!, #, 01, 99, 2024

You MUST respond ONLY with a valid JSON object. No markdown, no explanation, no preamble.

JSON structure:
{
  "reasoning": "your strategy for this specific person",
  "predicted_passwords": [
    {
      "password": "ActualPassword123",
      "likelihood": "high|medium|low",
      "category": "name+date|name+team|leet|combination|etc",
      "reason": "concise Arabic or English explanation"
    }
  ],
  "patterns_identified": ["pattern1", "pattern2"],
  "risk_level": "critical|high|medium|low",
  "risk_assessment": "overall assessment in Arabic"
}

Generate 30 to 50 passwords. Order: high likelihood first, then medium, then low.
Be creative with combinations — think like a real attacker who knows this person well."""


def predict_passwords(personal_info: dict, api_key: str) -> dict:
    import urllib.request
    import urllib.error

    info_text = json.dumps(personal_info, ensure_ascii=False, indent=2)

    user_message = f"""قم بتحليل البيانات الشخصية التالية وتوليد قائمة شاملة من الباسووردات المتوقعة:

{info_text}

توليد أكبر عدد ممكن من التوليفات الواقعية. فكر في كل طريقة ممكنة يستخدمها الناس لبناء باسوورداتهم من هذه المعلومات.
تذكر: رد فقط بـ JSON object بدون أي نص إضافي."""

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4000,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_message}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"API Error {e.code}: {body}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network Error: {e.reason}")

    raw_text = "".join(
        block.get("text", "")
        for block in data.get("content", [])
        if block.get("type") == "text"
    )

    return _parse_json(raw_text)


def _parse_json(text: str) -> dict:
    text = text.strip()
    for attempt in [
        lambda t: json.loads(t),
        lambda t: json.loads(re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", t).group(1)),
        lambda t: json.loads(re.search(r"\{[\s\S]+\}", t).group()),
    ]:
        try:
            return attempt(text)
        except Exception:
            pass
    raise ValueError(f"Could not parse JSON from response:\n{text[:400]}")
