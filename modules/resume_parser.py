import re
from typing import Dict, List, Optional
from PyPDF2 import PdfReader

from modules.skill_extractor import extract_skills, extract_keywords

EDUCATION_TERMS = [
    "bachelor", "master", "phd", "associate", "mba", "bs", "ba", "ms", "doctorate",
    "high school", "degree", "diploma",
]

SECTION_HEADERS = {
    "skills": ["skills", "technical skills", "skill set", "areas of expertise"],
    "education": ["education", "academic background", "qualifications"],
    "experience": ["experience", "work experience", "professional experience", "employment history"],
    "projects": ["projects", "project experience", "selected projects", "academic projects", "portfolio"],
    "summary": ["summary", "professional summary", "profile", "about me"],
}

EMAIL_PATTERN = re.compile(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"\b(?:\+?\d[\d\s\-()]{6,}\d)\b")


def extract_text_from_pdf(uploaded_file) -> str:
    try:
        reader = PdfReader(uploaded_file)
        text = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text.append(page_text)
        return "\n".join(text).strip()
    except Exception as exc:
        raise ValueError("Unable to parse PDF file. Please upload a valid resume PDF.") from exc


def clean_text(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"\r", "", text)
    cleaned = re.sub(r"\t", " ", cleaned)
    cleaned = re.sub(r"\n{2,}", "\n", cleaned)
    cleaned = re.sub(r"[ ]{2,}", " ", cleaned)
    return cleaned.strip()


def normalize_heading(line: str) -> str:
    return re.sub(r"[:\s]+$", "", line.strip().lower())


def is_contact_line(line: str) -> bool:
    return bool(EMAIL_PATTERN.search(line) or PHONE_PATTERN.search(line))


def sectionize_resume(text: str) -> Dict[str, List[str]]:
    cleaned = clean_text(text)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    sections: Dict[str, List[str]] = {"header": []}
    current_section = "header"

    for line in lines:
        normalized = normalize_heading(line)
        found = None
        for section, headings in SECTION_HEADERS.items():
            if normalized in headings:
                found = section
                break
        if found:
            current_section = found
            sections.setdefault(current_section, [])
            continue

        sections.setdefault(current_section, []).append(line)

    return sections


def extract_education(text: str) -> List[str]:
    sections = sectionize_resume(text)
    education_lines = sections.get("education", [])
    if education_lines:
        cleaned = [line for line in education_lines if not is_contact_line(line)]
        return cleaned[:8]

    cleaned = clean_text(text)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    education_lines = []
    for idx, line in enumerate(lines):
        lower = line.lower()
        if any(term in lower for term in EDUCATION_TERMS):
            education_lines.append(line)
            for next_line in lines[idx + 1 : idx + 3]:
                if next_line and len(next_line) < 120 and not is_contact_line(next_line):
                    education_lines.append(next_line)
    if not education_lines:
        pattern = re.compile(r"(\b(?:Bachelor|Master|MBA|PhD|Associate|Diploma|Degree)\b[^\n]*)", re.IGNORECASE)
        education_lines = [match.group(1).strip() for match in pattern.finditer(cleaned)]
    return sorted(dict.fromkeys(education_lines))[:8]


def extract_experience(text: str) -> List[str]:
    sections = sectionize_resume(text)
    experience_lines = sections.get("experience", [])
    if experience_lines:
        cleaned = [line for line in experience_lines if line and not is_contact_line(line)]
        return cleaned[:10]

    cleaned = clean_text(text)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    experience_lines = [
        line
        for line in lines
        if re.search(r"\b(years|experience|managed|led|built|delivered|developed|designed|collaborated|created)\b", line, re.IGNORECASE)
        and not is_contact_line(line)
    ]
    return experience_lines[:10]


def extract_projects(text: str) -> List[str]:
    sections = sectionize_resume(text)
    project_lines = sections.get("projects", [])
    if project_lines:
        cleaned = [line for line in project_lines if line and not is_contact_line(line)]
        return cleaned[:10]

    cleaned = clean_text(text)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    project_lines = [
        line
        for line in lines
        if re.search(r"\b(project|built|developed|designed|created|implementation|deployed|model)\b", line, re.IGNORECASE)
        and not is_contact_line(line)
    ]
    return project_lines[:10]


def parse_resume(text: str) -> Dict[str, object]:
    cleaned = clean_text(text)
    skills = extract_skills(cleaned)
    keywords = extract_keywords(cleaned)
    education = extract_education(cleaned)
    experience = extract_experience(cleaned)
    projects = extract_projects(cleaned)
    return {
        "clean_text": cleaned,
        "skills": skills,
        "keywords": keywords,
        "education": education,
        "experience": experience,
        "projects": projects,
    }
