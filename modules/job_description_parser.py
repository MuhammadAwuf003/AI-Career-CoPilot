import re
from typing import Dict, List

from modules.skill_extractor import extract_skills, extract_keywords, extract_technologies

EXPERIENCE_PATTERN = re.compile(r"(\d+)\+?\s*(?:\+?years|yrs|years)\b", re.IGNORECASE)


def parse_job_description(text: str) -> Dict[str, object]:
    normalized = text.strip()
    skills = extract_skills(normalized)
    technologies = extract_technologies(normalized)
    keywords = extract_keywords(normalized)
    experience_matches = EXPERIENCE_PATTERN.findall(normalized)
    experience = f"{experience_matches[0]}+ years" if experience_matches else "Not specified"
    requirements = []
    for line in normalized.splitlines():
        if line.strip().startswith("-") or re.search(r"\b(responsibilities|requires|must|should|preferred|skills)\b", line, re.IGNORECASE):
            requirements.append(line.strip("- \t"))
    if not requirements:
        requirements = keywords[:8]
    return {
        "clean_text": normalized,
        "skills": skills,
        "technologies": sorted(set(technologies)),
        "keywords": keywords,
        "experience": experience,
        "requirements": requirements,
    }
