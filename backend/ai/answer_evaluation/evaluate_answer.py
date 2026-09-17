"""
Hybrid answer evaluation: semantic similarity (Sentence-BERT) + explicit
concept coverage checklist.
"""
from sentence_transformers import SentenceTransformer, util

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def semantic_similarity(candidate_answer, reference_answer):
    model = get_model()
    emb = model.encode([candidate_answer, reference_answer], convert_to_tensor=True)
    return float(util.cos_sim(emb[0], emb[1]).item())


def concept_coverage(candidate_answer, expected_concepts):
    model = get_model()
    answer_emb = model.encode(candidate_answer, convert_to_tensor=True)
    covered = []
    for concept in expected_concepts:
        concept_emb = model.encode(concept, convert_to_tensor=True)
        sim = float(util.cos_sim(answer_emb, concept_emb).item())
        covered.append({"concept": concept, "covered": sim >= 0.45, "similarity": round(sim, 3)})
    n_covered = sum(1 for c in covered if c["covered"])
    return {
        "concepts": covered,
        "coverage_ratio": n_covered / len(expected_concepts) if expected_concepts else 0.0,
    }


def evaluate_answer(candidate_answer, reference_answer, expected_concepts):
    sim = semantic_similarity(candidate_answer, reference_answer)
    coverage = concept_coverage(candidate_answer, expected_concepts)
    return {
        "relevance_score": round(sim, 3),
        "concept_coverage": coverage,
        "technical_score": round(0.5 * sim + 0.5 * coverage["coverage_ratio"], 3),
    }


if __name__ == "__main__":
    result = evaluate_answer(
        candidate_answer="A REST API uses HTTP methods to let clients interact with server resources statelessly.",
        reference_answer="REST is an architectural style using stateless HTTP requests to access resources.",
        expected_concepts=["statelessness", "HTTP methods", "resource-based URLs", "client-server separation"],
    )
    print(result)