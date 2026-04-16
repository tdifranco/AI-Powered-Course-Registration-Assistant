from __future__ import annotations

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


def generate_ai_summary(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    print("GEMINI_API_KEY found:", bool(os.getenv("GEMINI_API_KEY")))
    print("GOOGLE_API_KEY found:", bool(os.getenv("GOOGLE_API_KEY")))

    if not api_key:
        return "No Gemini API key detected. Add GEMINI_API_KEY to your .env file."

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )

        text = getattr(response, "text", None)
        if text and text.strip():
            return text.strip()

        return f"Gemini returned no text. Raw response: {response}"

    except Exception as exc:
        return f"Gemini request failed: {exc}"