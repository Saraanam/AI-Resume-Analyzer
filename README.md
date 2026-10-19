# AI Resume Analyzer 🎯

An AI-powered resume analysis tool that extracts skills from a PDF resume and compares them with a job description to identify skill matches, missing skills, and learning opportunities.

## 🚀 Features

- **Resume Parsing:** Upload a PDF resume and extract its text.
- **Skill Extraction:** Identify technical skills mentioned in the resume.
- **Job Description Matching:** Compare resume skills with the requirements of a job description.
- **Matched and Missing Skills:** Identify required skills you already have and skills you need to learn.
- **Skill Match Score:** Calculate a match percentage to help evaluate alignment with a job description.
- **Learning Recommendations:** Get learning resources for skills that need improvement.
- **PDF Report:** Download a report summarizing your resume analysis.

## 🛠️ Technologies Used

- Python
- Streamlit
- PyMuPDF
- Plotly
- ReportLab
- Regular Expressions (Regex)
- Git and GitHub

## 📂 Project Structure

```text
AI-Resume-Analyzer/
├── app.py
├── main.py
├── skills.py
├── skill_extractor.py
├── resume_reader.py
├── job_matcher.py
├── recommendations.py
├── requirements.txt
├── README.md
└── .gitignore
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Saraanam/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run app.py
```

The application will open in your browser, usually at `http://localhost:850
