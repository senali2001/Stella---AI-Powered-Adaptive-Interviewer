import json
import ollama

SYSTEM_PROMPT = """You are an interview feedback assistant. You will receive a
structured JSON record of a candidate's interview performance.
Generate feedback using ONLY the information present in the JSON.
Do not infer or assume anything about the candidate's personality,
psychological state, or competence beyond what the scores and concept
coverage explicitly show. Treat 'engagement_supplementary' as a minor,
uncertain signal only, never a standalone claim about emotional state.

Structure the feedback as:
1. Strengths (grounded in scores/coverage)
2. Areas for improvement (grounded in missed concepts)
3. Communication observations
4. Overall summary
"""


def generate_feedback(interview_record):
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(interview_record, indent=2)},
        ],
    )
    return response["message"]["content"]