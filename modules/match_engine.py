from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_match_score(resume_text: str, jd_text: str) -> float:
    if not resume_text or not jd_text:
        return 0.0
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    corpus = [resume_text, jd_text]
    try:
        matrix = vectorizer.fit_transform(corpus)
        score = float(cosine_similarity(matrix[0:1], matrix[1:2]).flatten()[0])
    except ValueError:
        score = 0.0
    return round(score * 100, 1)


def compare_skill_sets(resume_skills: List[str], jd_skills: List[str]) -> Dict[str, List[str]]:
    resume_set = {skill.lower() for skill in resume_skills}
    jd_set = {skill.lower() for skill in jd_skills}
    matching = sorted([skill for skill in resume_skills if skill.lower() in jd_set])
    missing = sorted([skill.title() for skill in jd_set if skill not in resume_set])
    strengths = matching[:8]
    weaknesses = missing[:8]
    return {
        "matching_skills": matching,
        "missing_skills": missing,
        "strength_areas": strengths,
        "weakness_areas": weaknesses,
    }


def build_match_summary(resume_text: str, jd_text: str, resume_skills: List[str], jd_skills: List[str]) -> Dict[str, object]:
    score = compute_match_score(resume_text, jd_text)
    skill_comparison = compare_skill_sets(resume_skills, jd_skills)
    return {
        "score": score,
        **skill_comparison,
    }
