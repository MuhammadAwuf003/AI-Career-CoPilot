from typing import Dict, List


def generate_recommendations(parsed_resume: Dict[str, object], gap_report: Dict[str, object], match_summary: Dict[str, object]) -> Dict[str, List[str]]:
    suggestions = []
    roadmap = []

    if not parsed_resume.get("education"):
        suggestions.append("Add a clear education section with degrees, institutions, and dates.")
    if not parsed_resume.get("experience"):
        suggestions.append("Include a professional experience section with measurable results.")
    if not parsed_resume.get("projects"):
        suggestions.append("Add at least one project to highlight technical delivery and impact.")
    if not parsed_resume.get("skills"):
        suggestions.append("List your core technical and business skills in a dedicated section.")

    if match_summary.get("score", 0) < 60:
        suggestions.append("Align your resume bullets with the job description using matching keywords.")
    if match_summary.get("score", 0) < 40:
        suggestions.append("Review your resume formatting for clarity and improve each accomplishment statement.")

    missing_skills = gap_report.get("missing_skills", [])
    if missing_skills:
        suggestions.append("Prioritize learning or highlighting the missing skills below to improve your fit.")
        roadmap.extend([f"Study {skill} fundamentals and add one related project." for skill in missing_skills[:4]])
    else:
        roadmap.append("Continue strengthening your resume by adding recent achievements and performance metrics.")

    if len(parsed_resume.get("skills", [])) < 6:
        roadmap.append("Expand your skills section with tools, languages, and frameworks you regularly use.")

    if not suggestions:
        suggestions.append("Your resume appears well structured. Continue refining bullet points with measurable outcomes.")

    return {
        "suggestions": suggestions,
        "roadmap": roadmap,
    }
