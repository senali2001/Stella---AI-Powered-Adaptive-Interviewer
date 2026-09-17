WEIGHTS = {
    "technical": 0.45,
    "communication": 0.25,
    "relevance": 0.20,
    "engagement": 0.10,
}

def communication_score(speaking_rate_wpm, filler_word_count, total_words):
    ideal_rate = 140
    rate_penalty = min(abs(speaking_rate_wpm - ideal_rate) / ideal_rate, 1.0)
    filler_ratio = filler_word_count / max(1, total_words)
    filler_penalty = min(filler_ratio * 5, 1.0)
    return round(1.0 - 0.5 * rate_penalty - 0.5 * filler_penalty, 3)


def engagement_indicator(interview_state, confidence):
    favorable_states = {"calm", "confident"}
    base = 0.7 if interview_state in favorable_states else 0.4
    return round(base * confidence, 3)


def score_answer(technical_result, comm_score, engagement):
    technical = technical_result["technical_score"]
    relevance = technical_result["relevance_score"]

    overall = (
        WEIGHTS["technical"] * technical
        + WEIGHTS["communication"] * comm_score
        + WEIGHTS["relevance"] * relevance
        + WEIGHTS["engagement"] * engagement
    )
    return {
        "overall_score": round(overall, 3),
        "breakdown": {
            "technical": technical,
            "communication": comm_score,
            "relevance": relevance,
            "engagement_supplementary": engagement,
        },
    }