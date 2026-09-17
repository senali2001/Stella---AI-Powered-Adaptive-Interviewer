from dataclasses import dataclass, field


@dataclass
class InterviewState:
    topics_covered: dict = field(default_factory=dict)
    current_difficulty: int = 2
    history: list = field(default_factory=list)


def next_action(state, last_score, last_topic):
    state.history.append({"topic": last_topic, "score": last_score})
    state.topics_covered[last_topic] = max(state.topics_covered.get(last_topic, 0), last_score)

    if last_score >= 0.75:
        state.current_difficulty = min(5, state.current_difficulty + 1)
        action = "increase_difficulty_same_or_new_topic"
    elif last_score >= 0.45:
        action = "ask_followup_same_topic"
    else:
        state.current_difficulty = max(1, state.current_difficulty - 1)
        action = "ask_simpler_or_clarifying_question"

    return {"action": action, "target_difficulty": state.current_difficulty}