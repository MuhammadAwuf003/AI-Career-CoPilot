import re
from collections import Counter
from typing import List, Set, Dict

# Core technical and professional skill inventory used across resume and JD parsing.
DEFAULT_SKILLS: Set[str] = {
    "python", "sql", "excel", "power bi", "tableau", "aws", "azure", "google cloud",
    "docker", "kubernetes", "git", "github", "gitlab", "jira", "confluence",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib",
    "plotly", "streamlit", "flask", "django", "fastapi", "html", "css",
    "javascript", "react", "node.js", "node", "typescript", "rest api", "api design",
    "data analysis", "data visualization", "machine learning", "deep learning",
    "natural language processing", "nlp", "computer vision", "leadership", "communication",
    "project management", "agile", "scrum", "business intelligence", "customer success",
    "risk management", "problem solving", "critical thinking", "presentation",
    "time management", "teamwork", "sql server", "postgresql", "mysql", "mongodb",
    "databricks", "spark", "hadoop", "devops", "automation", "testing", "jenkins",
    "linux", "bash", "shell scripting", "google analytics", "seo", "content strategy",
    "financial modeling", "budgeting", "forecasting", "recruiting", "talent acquisition",
}

STOPWORDS = {
    "the", "and", "for", "with", "that", "from", "this", "will", "have", "has",
    "are", "were", "was", "project", "projects", "work", "experience", "years",
    "year", "using", "using", "based", "team", "business", "management", "skills",
    "including", "including", "strong", "stronger", "ability", "able",
}

SKILL_PATTERN = re.compile(r"\b([a-zA-Z0-9+\.\- ]{2,40})\b")


def normalize_text(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"[\r\n]+", " ", text)
    cleaned = re.sub(r"[^\w\s\+\-\.\/]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
    return cleaned


def extract_skills(text: str) -> List[str]:
    normalized = normalize_text(text)
    found = set()
    for skill in sorted(DEFAULT_SKILLS, key=lambda x: -len(x)):
        pattern = re.escape(skill.lower())
        if re.search(rf"\b{pattern}\b", normalized):
            found.add(skill.title() if skill.islower() else skill)
    if not found:
        tokens = normalized.split()
        for token in tokens:
            if token in DEFAULT_SKILLS:
                found.add(token.title())
    return sorted(found)


def extract_keywords(text: str, top_n: int = 15) -> List[str]:
    normalized = normalize_text(text)
    tokens = [token for token in re.findall(r"\b[a-zA-Z0-9\+\-\.]{2,}\b", normalized)]
    tokens = [token for token in tokens if token not in STOPWORDS]
    frequencies = Counter(tokens)
    common = [word for word, _ in frequencies.most_common(top_n)]
    return common


def extract_technologies(text: str) -> List[str]:
    return extract_skills(text)


def extract_professional_terms(text: str) -> List[str]:
    return extract_keywords(text, top_n=20)
