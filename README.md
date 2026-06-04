# AI Career Copilot

AI Career Copilot is a polished career management platform built with Python and Streamlit. It helps job seekers analyze resumes, assess fit against job descriptions, identify skill gaps, receive resume improvement suggestions, and track applications with analytics.

## Features

- Resume PDF upload and structured resume parsing
- Job description analysis and keyword extraction
- Resume-to-job matching with TF-IDF and cosine similarity
- Skill gap detection with priority recommendations
- Resume optimization advisor for section-level feedback
- SQLite-based application tracker with add/edit/delete support
- Analytics dashboard with Plotly visualizations
- Professional UI with sidebar navigation and expandable sections

## Architecture

- `app.py` — Streamlit application entry point
- `modules/` — Modular backend logic for parsing, matching, recommendations, and analytics
- `database/` — SQLite initialization and storage
- `assets/` — Sample job descriptions and resume text
- `screenshots/` — Placeholder for presentation screenshots

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ai-career-copilot.git
cd ai-career-copilot
```

2. Create a Python virtual environment:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Initialize the database (optional):

```bash
python database/init_db.py
```

2. Run the Streamlit app:

```bash
streamlit run app.py
```

3. Use the sidebar to navigate between:

- Resume Analysis
- Job Match
- Skill Gap Analysis
- Resume Optimizer
- Application Tracker
- Analytics

## Sample Data

- `assets/sample_job_description.txt` — example job description text
- `assets/sample_resume.txt` — sample resume text for quick testing

## Future Improvements

- Add user authentication and multi-user workspace
- Support .docx resume uploads and richer parsing
- Integrate GPT-powered recommendation summaries
- Add export options for resume and application snapshots
- Add automated resume formatting preview

## Notes

- The app uses a lightweight SQLite database stored at `database/applications.db`
- Resume parsing uses keyword heuristics and skill inventory matching
- The platform is designed for professional presentation and recruiter-ready workflows

## Live Demo

Deployed on Render:
https://ai-career-copilot-0pno.onrender.com/
