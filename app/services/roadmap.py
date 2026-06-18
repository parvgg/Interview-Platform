import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

ROADMAP_PROMPT = """You are a career coach creating a personalized improvement roadmap for an interview candidate.

Based on these combined scores from a mock interview session:
- Technical accuracy: {technical_accuracy}/10
- Completeness: {completeness}/10
- Clarity: {clarity}/10
- Confidence (from speech delivery): {confidence}/10
- Communication (vocabulary, coherence): {communication}/10
- Speaking rate: {speaking_rate} words per minute (ideal: 120-150)
- Filler word count: {filler_count}

Weaknesses noted: {weaknesses}

Generate a personalized 5-point improvement roadmap. Respond with ONLY a valid JSON object (no markdown, no extra text, no ```json fences) in this exact format:
{{
  "roadmap": [
    {{
      "title": "<short action title>",
      "skill_area": "<e.g. Technical Depth, Communication, Confidence>",
      "description": "<2-3 sentence specific action plan>",
      "priority": "<high|medium|low>",
      "estimated_hours": <number>
    }}
  ]
}}

Order items by priority (high first). Be specific and actionable, not generic.
"""

def generate_roadmap(scores: dict, audio_features: dict, nlp_features: dict) -> list:
    prompt = ROADMAP_PROMPT.format(
        technical_accuracy=scores.get("technical_accuracy", 0),
        completeness=scores.get("completeness", 0),
        clarity=scores.get("clarity", 0),
        confidence=round(min(10, max(0, 10 - audio_features.get("pause_count", 0))), 1),
        communication=round(nlp_features.get("coherence_score", 0) * 10, 1),
        speaking_rate=audio_features.get("speaking_rate_wpm", 0),
        filler_count=audio_features.get("filler_word_count", 0),
        weaknesses=scores.get("weaknesses", "Not specified")
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )

    parsed = json.loads(response.text)

    if isinstance(parsed, dict):
        for key in parsed:
            if isinstance(parsed[key], list):
                return parsed[key]
        return []
    return parsed