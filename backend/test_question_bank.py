import json
from ai.answer_evaluation.evaluate_answer import evaluate_answer

with open("ai/question_bank/hr_questions.json") as f:
    questions = json.load(f)

# test hr_q6 — Teamwork
q = next(q for q in questions if q["id"] == "hr_q6")

candidate_answer = "In a group project, we split tasks based on strengths and I kept everyone updated on my progress. When one part was delayed, I let the team know early so we could adjust the plan together, and we submitted on time."

result = evaluate_answer(
    candidate_answer=candidate_answer,
    reference_answer=q["reference_answer"],
    expected_concepts=q["expected_concepts"],
)
print(f"Question: {q['question']}")
print(result)