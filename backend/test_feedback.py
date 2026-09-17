from ai.feedback.generate_feedback import generate_feedback

sample_record = {
    "candidate_role": "Software Engineering Intern",
    "questions": [
        {
            "topic": "Teamwork",
            "overall_score": 0.689,
            "breakdown": {"technical": 0.576, "communication": 0.952, "relevance": 0.751},
        },
    ],
}

print(generate_feedback(sample_record))