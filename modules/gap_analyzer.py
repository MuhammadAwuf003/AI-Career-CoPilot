from typing import Dict, List

PRIORITY_CATEGORIES = ["High", "Medium", "Low"]


def _rank_missing_skills(missing_skills: List[str]) -> Dict[str, List[str]]:
    high = missing_skills[:3]
    medium = missing_skills[3:7]
    low = missing_skills[7:12]
    return {"High": high, "Medium": medium, "Low": low}


def analyze_skill_gaps(resume_skills: List[str], jd_skills: List[str]) -> Dict[str, object]:
    resume_lower = {skill.lower() for skill in resume_skills}
    missing = sorted([skill.title() for skill in jd_skills if skill.lower() not in resume_lower])
    gap_breakdown = _rank_missing_skills(missing)
    summary = []
    if missing:
        summary.append(f"{len(missing)} required skills are not present in your resume.")
        if len(missing) > 5:
            summary.append("Start with high-priority technical skills and certifications.")
    else:
        summary.append("Your resume already covers the core requirements for this role.")
    return {
        "missing_skills": missing,
        "breakdown": gap_breakdown,
        "summary": summary,
    }
