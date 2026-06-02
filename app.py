import os
from datetime import datetime

import streamlit as st

from modules.analytics import build_metrics
from modules.application_tracker import ApplicationTracker, STATUSES
from modules.gap_analyzer import analyze_skill_gaps
from modules.job_description_parser import parse_job_description
from modules.match_engine import build_match_summary
from modules.recommendation_engine import generate_recommendations
from modules.resume_parser import extract_text_from_pdf, parse_resume


def init_session() -> None:
    defaults = {
        "resume_text": "",
        "parsed_resume": {},
        "job_description_text": "",
        "parsed_jd": {},
        "match_summary": {},
        "gap_report": {},
        "recommendations": {},
        "application_form_status": "Applied",
        "selected_application": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_page_style() -> None:
    st.markdown(
        """
        <style>
        .metric-card { padding: 1rem; border-radius: 0.75rem; background: #f8fafc; }
        .small-heading { color: #1f2937; margin-bottom: 0.25rem; }
        .status-pill { border-radius: 999px; padding: 0.25rem 0.75rem; display: inline-block; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard_intro() -> None:
    st.title("AI Career Copilot")
    st.write(
        "A professional career management platform for resume analysis, job matching, skill gap detection, application tracking, and productivity analytics."
    )


def render_resume_analysis() -> None:
    st.header("Resume Analysis")
    st.write("Upload your resume PDF and turn it into a structured career snapshot.")

    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"], help="Upload a resume PDF to extract skills, education, experience, and projects.")
    if uploaded_file:
        try:
            text = extract_text_from_pdf(uploaded_file)
            if not text.strip():
                st.error("The uploaded PDF is empty or not readable. Please try a different resume file.")
                return
            parsed = parse_resume(text)
            st.session_state["resume_text"] = parsed["clean_text"]
            st.session_state["parsed_resume"] = parsed
        except ValueError as exc:
            st.error(str(exc))
            return

    if st.session_state["parsed_resume"]:
        parsed = st.session_state["parsed_resume"]
        cols = st.columns([1, 1, 1, 1])
        cols[0].metric("Skills", len(parsed["skills"]))
        cols[1].metric("Education Items", len(parsed["education"]))
        cols[2].metric("Experience Lines", len(parsed["experience"]))
        cols[3].metric("Projects", len(parsed["projects"]))

        with st.expander("Resume Summary", expanded=True):
            st.write(parsed["clean_text"][:6000] + ("..." if len(parsed["clean_text"]) > 6000 else ""))

        st.subheader("Parsed Sections")
        left, right = st.columns(2)
        with left:
            st.markdown("**Skills**")
            st.write(parsed["skills"] or ["No skills detected."])
            st.markdown("**Education**")
            st.write(parsed["education"] or ["No education section detected."])
            st.markdown("**Experience**")
            st.write(parsed["experience"] or ["No experience section detected."])
        with right:
            st.markdown("**Projects**")
            st.write(parsed["projects"] or ["No project section detected."])
            st.markdown("**Keywords**")
            st.write(parsed["keywords"] or ["No keywords extracted."])
    else:
        st.info("Upload a resume PDF to begin your career analysis.")


def render_job_match() -> None:
    st.header("Job Description Analyzer & Match")
    st.write("Paste a job description and compare it against your resume for fit, skill alignment, and opportunities.")

    jd_text = st.text_area("Paste job description here", value=st.session_state["job_description_text"], height=220)
    if st.button("Analyze Job Description"):
        if not jd_text.strip():
            st.error("Please enter a job description before analyzing.")
            return
        parsed_jd = parse_job_description(jd_text)
        st.session_state["job_description_text"] = jd_text
        st.session_state["parsed_jd"] = parsed_jd
        if st.session_state["parsed_resume"]:
            st.session_state["match_summary"] = build_match_summary(
                st.session_state["resume_text"],
                jd_text,
                st.session_state["parsed_resume"]["skills"],
                parsed_jd["skills"],
            )
            st.session_state["gap_report"] = analyze_skill_gaps(
                st.session_state["parsed_resume"]["skills"], parsed_jd["skills"]
            )
            st.session_state["recommendations"] = generate_recommendations(
                st.session_state["parsed_resume"],
                st.session_state["gap_report"],
                st.session_state["match_summary"],
            )

    if st.session_state["parsed_jd"]:
        parsed_jd = st.session_state["parsed_jd"]
        cols = st.columns([1, 1, 1])
        cols[0].metric("Required Skills", len(parsed_jd["skills"]))
        cols[1].metric("Experience", parsed_jd["experience"])
        cols[2].metric("Keywords", len(parsed_jd["keywords"]))

        with st.expander("Job Description Requirements", expanded=True):
            st.write("\n".join(parsed_jd["requirements"][:12]) or "No explicit requirements detected.")

        left, right = st.columns(2)
        with left:
            st.markdown("**Extracted Skills**")
            st.write(parsed_jd["skills"] or ["No skills detected."])
            st.markdown("**Technologies**")
            st.write(parsed_jd["technologies"] or ["No technologies detected."])
        with right:
            st.markdown("**Top Keywords**")
            st.write(parsed_jd["keywords"] or ["No keywords detected."])

        if st.session_state["match_summary"]:
            summary = st.session_state["match_summary"]
            st.subheader("Resume Match Score")
            st.progress(int(summary["score"]))
            st.metric("Match Score", f"{summary['score']}%")
            st.markdown("**Matching Skills**")
            st.write(summary["matching_skills"] or ["No matching skills found."])
            st.markdown("**Missing Skills**")
            st.write(summary["missing_skills"] or ["Resume contains all detected skills."])
    else:
        st.info("Paste a job description and click Analyze to extract requirements and measure fit.")


def render_skill_gap_analysis() -> None:
    st.header("Skill Gap Analysis")
    if not st.session_state["parsed_jd"] or not st.session_state["parsed_resume"]:
        st.warning("Complete resume and job description analysis before viewing skill gaps.")
        return

    gap_report = st.session_state["gap_report"]
    st.markdown("### Skill Gap Report")
    for sentence in gap_report.get("summary", []):
        st.write(f"- {sentence}")

    st.markdown("#### Priority Gaps")
    for priority, skills in gap_report.get("breakdown", {}).items():
        if skills:
            st.markdown(f"**{priority}**")
            st.write(skills)
        else:
            st.write(f"**{priority}**: None identified yet.")

    if gap_report.get("missing_skills"):
        st.markdown("#### Recommended learning focus")
        for skill in gap_report["missing_skills"][:5]:
            st.write(f"- Learn {skill} through practice projects and certification resources.")
    else:
        st.success("No major skill gaps detected relative to the current job description. Great alignment!")


def render_resume_optimizer() -> None:
    st.header("Resume Optimization Advisor")
    if not st.session_state["parsed_resume"]:
        st.warning("Upload a resume to receive optimization guidance.")
        return

    if not st.session_state["parsed_jd"]:
        st.info("Analysis is stronger when you also paste a job description for matching context.")

    recommendations = st.session_state.get("recommendations") or generate_recommendations(
        st.session_state["parsed_resume"],
        st.session_state.get("gap_report", {"missing_skills": [], "breakdown": {}}),
        st.session_state.get("match_summary", {"score": 0}),
    )

    st.markdown("### Actionable Feedback")
    for item in recommendations["suggestions"]:
        st.write(f"- {item}")

    st.markdown("### Recommended Roadmap")
    for item in recommendations["roadmap"]:
        st.write(f"- {item}")

    st.markdown("### Resume Sections Checklist")
    checklist = {
        "Skills section": bool(st.session_state["parsed_resume"]["skills"]),
        "Education section": bool(st.session_state["parsed_resume"]["education"]),
        "Experience bullets": bool(st.session_state["parsed_resume"]["experience"]),
        "Project descriptions": bool(st.session_state["parsed_resume"]["projects"]),
    }
    for label, condition in checklist.items():
        status = "✅" if condition else "⚠️"
        st.write(f"{status} {label}")


def render_application_tracker() -> None:
    st.header("Application Tracker")
    tracker = ApplicationTracker()
    st.write("Track every job application with deadlines, status updates, and notes.")

    with st.form(key="application_form"):
        company = st.text_input("Company", value="")
        role = st.text_input("Job Role", value="")
        application_date = st.date_input("Application Date", value=datetime.today())
        status = st.selectbox("Status", STATUSES, index=0)
        notes = st.text_area("Notes", value="", height=120)
        submitted = st.form_submit_button("Add Application")

        if submitted:
            if not company.strip() or not role.strip():
                st.error("Company and Job Role are required.")
            else:
                tracker.add_application(
                    company=company,
                    role=role,
                    application_date=application_date.isoformat(),
                    status=status,
                    notes=notes,
                )
                st.success("Application added successfully.")

    applications = tracker.get_applications()
    if applications:
        st.markdown("---")
        st.subheader("Active Applications")
        st.dataframe(applications)

        edit_id = st.selectbox(
            "Select application to update or delete",
            options=[app["id"] for app in applications],
            format_func=lambda id_val: next((app["company"] + " — " + app["role"] for app in applications if app["id"] == id_val), ""),
        )
        selected = next((app for app in applications if app["id"] == edit_id), None)
        if selected:
            with st.form(key="edit_form"):
                company = st.text_input("Company", value=selected["company"])
                role = st.text_input("Job Role", value=selected["role"])
                application_date = st.date_input("Application Date", value=datetime.fromisoformat(selected["application_date"]).date())
                status = st.selectbox("Status", STATUSES, index=STATUSES.index(selected["status"]) if selected["status"] in STATUSES else 0)
                notes = st.text_area("Notes", value=selected["notes"] or "", height=120)
                update_btn = st.form_submit_button("Update Application")
                delete_btn = st.form_submit_button("Delete Application")
                if update_btn:
                    tracker.update_application(
                        selected["id"], company, role, application_date.isoformat(), status, notes
                    )
                    st.success("Application updated.")
                if delete_btn:
                    tracker.delete_application(selected["id"])
                    st.success("Application deleted.")
    else:
        st.info("No tracked applications yet. Add your first application to begin monitoring progress.")


def render_analytics() -> None:
    st.header("Analytics Dashboard")
    tracker = ApplicationTracker()
    applications = tracker.get_applications()
    metrics = build_metrics(applications)

    if not applications:
        st.warning("Add applications in the tracker to visualize analytics.")
        return

    cols = st.columns(4)
    cols[0].metric("Total Applications", metrics["total"])
    cols[1].metric("Interviews", metrics["interview"])
    cols[2].metric("Offers", metrics["offer"])
    cols[3].metric("Success Rate", f"{metrics['success_rate']}%")

    st.plotly_chart(metrics["status_chart"], use_container_width=True)
    st.plotly_chart(metrics["monthly_chart"], use_container_width=True)
    st.plotly_chart(metrics["conversion_chart"], use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="AI Career Copilot", layout="wide", page_icon="💼")
    init_session()
    set_page_style()

    with st.sidebar:
        st.title("AI Career Copilot")
        choice = st.radio(
            "Navigation",
            [
                "Resume Analysis",
                "Job Match",
                "Skill Gap Analysis",
                "Resume Optimizer",
                "Application Tracker",
                "Analytics",
            ],
        )
        st.markdown("---")
        st.write("Built for career growth, recruiter-friendly job search, and focused application management.")

    render_dashboard_intro()
    st.markdown("---")

    if choice == "Resume Analysis":
        render_resume_analysis()
    elif choice == "Job Match":
        render_job_match()
    elif choice == "Skill Gap Analysis":
        render_skill_gap_analysis()
    elif choice == "Resume Optimizer":
        render_resume_optimizer()
    elif choice == "Application Tracker":
        render_application_tracker()
    elif choice == "Analytics":
        render_analytics()


if __name__ == "__main__":
    main()
