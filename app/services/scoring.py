import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SCORING_PROMPT = """You are an expert technical interviewer evaluating a candidate's spoken answer.

Question: {question}

Candidate's Transcribed Answer: {transcript}

Evaluate the answer and respond with ONLY a valid JSON object (no markdown, no extra text, no ```json fences) in this exact format:
{{
  "technical_accuracy": <0-10 float>,
  "completeness": <0-10 float>,
  "clarity": <0-10 float>,
  "depth": <0-10 float>,
  "relevance": <0-10 float>,
  "strengths": "<2-3 sentence summary of what the candidate did well>",
  "weaknesses": "<2-3 sentence summary of what needs improvement>",
  "feedback": "<actionable, encouraging feedback in 2-4 sentences>"
}}

Be fair but rigorous, as if grading for a real job interview at a competitive tech company.
"""

def score_answer(question: str, transcript: str) -> dict:
    if not transcript or len(transcript.strip()) < 5:
        return {
            "technical_accuracy": 0, "completeness": 0, "clarity": 0,
            "depth": 0, "relevance": 0,
            "strengths": "No answer detected.",
            "weaknesses": "The response was too short or empty to evaluate.",
            "feedback": "Please provide a complete answer to receive scoring."
        }

    prompt = SCORING_PROMPT.format(question=question, transcript=transcript)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )

    result = json.loads(response.text)
    return result