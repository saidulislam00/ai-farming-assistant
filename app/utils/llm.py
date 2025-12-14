import os
import requests

def llm_enabled() -> bool:
    return bool(os.getenv("LLM_API_KEY")) and bool(os.getenv("LLM_BASE_URL")) and bool(os.getenv("LLM_MODEL"))

def llm_bangla_explain(rules_text_bn: str, context: dict) -> str:
    """
    OpenAI-compatible chat endpoint (works with many providers).
    Set:
      LLM_BASE_URL = https://api.groq.com/openai/v1  (example)
      LLM_API_KEY
      LLM_MODEL
    """
    if not llm_enabled():
        return rules_text_bn

    base = os.environ["LLM_BASE_URL"].rstrip("/")
    key = os.environ["LLM_API_KEY"]
    model = os.environ["LLM_MODEL"]

    prompt = f"""
আপনি একজন কৃষি বিশেষজ্ঞ। নিচের নিয়মভিত্তিক পরামর্শকে আরও স্বাভাবিক, সংক্ষিপ্ত ও কার্যকর বাংলায় লিখুন।
- অপ্রয়োজনীয় কথা বলবেন না
- পরিমাপ/সময়/মাত্রা থাকলে রাখবেন
- কৃষকের জন্য সহজ ভাষা ব্যবহার করবেন

নিয়মভিত্তিক পরামর্শ:
{rules_text_bn}

প্রাসঙ্গিক তথ্য (JSON):
{context}
""".strip()

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful agriculture assistant who writes in Bangla."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }

    r = requests.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=payload,
        timeout=25
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()
