import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
from faster_whisper import WhisperModel
from ai.answer_evaluation.evaluate_answer import evaluate_answer
from ai.scoring.score import score_answer, communication_score, engagement_indicator
from ai.adaptive_engine.engine import InterviewState, next_action

model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe("hr_6.mp4", language="en")
transcript = " ".join(s.text.strip() for s in segments)
print("Transcript:", transcript)

with open("ai/question_bank/hr_questions.json") as f:
    questions = json.load(f)
q = next(q for q in questions if q["id"] == "hr_q6")

eval_result = evaluate_answer(transcript, q["reference_answer"], q["expected_concepts"])

total_words = len(transcript.split())
comm_score = communication_score(speaking_rate_wpm=140, filler_word_count=1, total_words=total_words)
engagement = engagement_indicator(interview_state="calm", confidence=0.6)  # placeholder until SER is wired in

result = score_answer(eval_result, comm_score, engagement)
print("\nScore:", result)

state = InterviewState()
decision = next_action(state, result["overall_score"], q["topic"])
print("\nAdaptive decision:", decision)