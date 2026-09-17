import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
from faster_whisper import WhisperModel
from ai.answer_evaluation.evaluate_answer import evaluate_answer

# ---- Step 1: Transcribe the recorded answer ----
model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe("hr_6.mp4", language="en")

transcript = " ".join(segment.text.strip() for segment in segments)
print("Transcript:", transcript)

# ---- Step 2: Load the matching question ----
with open("ai/question_bank/hr_questions.json") as f:
    questions = json.load(f)

q = next(q for q in questions if q["id"] == "hr_q6")  # change to whichever question you answered

# ---- Step 3: Score the transcribed answer ----
result = evaluate_answer(
    candidate_answer=transcript,
    reference_answer=q["reference_answer"],
    expected_concepts=q["expected_concepts"],
)

print(f"\nQuestion: {q['question']}")
print(result)