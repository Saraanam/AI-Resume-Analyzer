from io import BytesIO
from xml.sax.saxutils import escape
import re

import streamlit as st
import plotly.graph_objects as go

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

from resume_reader import extract_text_from_pdf
from skill_extractor import extract_skills
from skills import SKILLS
from job_matcher import match_job_description
from recommendations import LEARNING_RESOURCES


# ------------------------------
# PDF REPORT
# ------------------------------
def create_pdf_report(
    resume_skills,
    matched_required,
    missing_required,
    matched_optional,
    missing_optional,
    required_score,
    optional_score,
    learning_resources,
):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1769E0"),
        spaceAfter=16,
    ))
    styles.add(ParagraphStyle(
        name="ReportHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#1769E0"),
        spaceBefore=12,
        spaceAfter=6,
    ))

    story = [
        Paragraph("AI Resume Analyzer Report", styles["ReportTitle"]),
        Paragraph("Resume and job description comparison", styles["BodyText"]),
        Spacer(1, 16),
        Paragraph("Match Summary", styles["ReportHeading"]),
    ]

    summary_data = [
        ["Metric", "Result"],
        ["Mandatory skill match", f"{required_score:.1f}%"],
        ["Optional skill match", f"{optional_score:.1f}%"],
        ["Resume skills identified", str(len(resume_skills))],
        [
            "Mandatory skills matched",
            f"{len(matched_required)}/{len(matched_required) + len(missing_required)}",
        ],
        ["Mandatory skills missing", str(len(missing_required))],
    ]
    summary_table = Table(summary_data, colWidths=[3.6 * inch, 2.0 * inch])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1769E0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.extend([summary_table, Spacer(1, 12)])

    def add_skill_section(title, skills):
        story.append(Paragraph(escape(title), styles["ReportHeading"]))
        if skills:
            for skill in sorted(skills):
                story.append(Paragraph("&#8226; " + escape(str(skill)), styles["BodyText"]))
        else:
            story.append(Paragraph("None identified.", styles["BodyText"]))
        story.append(Spacer(1, 6))

    add_skill_section("Skills Identified in Resume", resume_skills)
    add_skill_section("Matched Mandatory Skills", matched_required)
    add_skill_section("Missing Mandatory Skills", missing_required)
    add_skill_section("Matched Optional Skills", matched_optional)
    add_skill_section("Missing Optional Skills", missing_optional)

    story.append(Paragraph("Learning Recommendations", styles["ReportHeading"]))
    if missing_required:
        for skill in sorted(missing_required):
            story.append(Paragraph("<b>" + escape(str(skill)) + "</b>", styles["BodyText"]))
            resources = learning_resources.get(skill, [
                "Study the fundamentals of this skill.",
                "Practice related interview questions.",
                "Build a small project using this skill.",
            ])
            for resource in resources:
                story.append(Paragraph("&#8226; " + escape(str(resource)), styles["BodyText"]))
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No recognized mandatory skills were missing.", styles["BodyText"]))

    story.extend([
        Spacer(1, 14),
        Paragraph(
            "Note: This report uses keyword matching against the project's skill dictionary. "
            "It does not measure overall employability or guarantee selection.",
            styles["Italic"],
        ),
    ])
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ------------------------------
# PAGE CONFIG + VISUAL STYLE
# ------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --blue: #1677e8;
    --blue-dark: #1258b5;
    --teal: #19bdb4;
    --ink: #14233b;
    --muted: #64748b;
    --line: #e4ebf5;
    --soft: #f4f8ff;
}
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background: linear-gradient(135deg, #edf5ff 0%, #f8fbff 55%, #e8fbfa 100%);
    color: var(--ink);
}
[data-testid="stHeader"] { background: rgba(248, 251, 255, 0.75); }
.block-container { max-width: 1240px; padding-top: 2rem; padding-bottom: 3rem; }
h1, h2, h3 { color: var(--ink); letter-spacing: -0.025em; }
p, label, .stMarkdown { color: #34445d; }
.hero {
    background: linear-gradient(115deg, #1677e8 0%, #2467d8 58%, #19bdb4 125%);
    border-radius: 24px;
    padding: 30px 34px;
    color: white;
    box-shadow: 0 16px 38px rgba(22, 119, 232, .20);
    margin-bottom: 24px;
}
.hero h1 { color: white; font-size: 2.25rem; margin: 0 0 8px 0; }
.hero p { color: #eaf4ff; font-size: 1.02rem; margin: 0; }
.eyebrow { font-size: .76rem; font-weight: 800; text-transform: uppercase; letter-spacing: .13em; color: #d6eaff; margin-bottom: 9px; }
.panel {
    background: rgba(255,255,255,.94);
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 8px 26px rgba(31, 65, 114, .06);
    margin-bottom: 18px;
}
.panel-title { font-size: 1.12rem; font-weight: 750; color: var(--ink); margin-bottom: 4px; }
.panel-subtitle { color: var(--muted); font-size: .9rem; margin-bottom: 16px; }
[data-testid="stMetric"] {
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 6px 20px rgba(31, 65, 114, .05);
}
[data-testid="stMetricLabel"] { color: #60728d; font-weight: 600; }
[data-testid="stMetricValue"] { color: var(--blue-dark); font-weight: 800; }
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(90deg, #1677e8, #245fd3);
    color: white;
    border: 0;
    border-radius: 12px;
    padding: .72rem 1.2rem;
    font-weight: 700;
    min-height: 46px;
    box-shadow: 0 6px 16px rgba(22, 119, 232, .18);
}
.stButton > button:hover, .stDownloadButton > button:hover {
    color: white;
    border: 1px solid #0e56b5;
    background: #125fc8;
}
[data-testid="stTextArea"] textarea {
    background: #fbfdff;
    color: var(--ink);
    border: 1px solid #d6e1f0;
    border-radius: 12px;
}
[data-testid="stFileUploader"] {
    background: #f7faff;
    border: 1.5px dashed #9dbde9;
    border-radius: 14px;
    padding: 12px;
}
[data-baseweb="tab-list"] { gap: 8px; }
[data-baseweb="tab"] {
    background: #edf4ff;
    border-radius: 10px;
    padding: 10px 15px;
}
[data-baseweb="tab"][aria-selected="true"] {
    background: #dcecff;
    color: #1258b5;
}
[data-testid="stExpander"] {
    background: white;
    border: 1px solid var(--line);
    border-radius: 14px;
}
hr { border-color: var(--line); }
.small-note { color: #6c7d95; font-size: .82rem; }
.skill-chip {
    display: inline-block; margin: 4px 5px 4px 0; padding: 7px 11px;
    border-radius: 999px; background: #e9f3ff; color: #1557a6;
    border: 1px solid #d2e6ff; font-size: .86rem; font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="eyebrow">Career toolkit · Resume intelligence</div>
  <h1>AI Resume Analyzer</h1>
  <p>Find your strengths, uncover skill gaps, and make your next learning step clear.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------
# INPUTS
# ------------------------------
st.markdown('<div class="panel"><div class="panel-title">Start your analysis</div><div class="panel-subtitle">Upload a PDF resume and paste the job description you want to target.</div>', unsafe_allow_html=True)
input_col1, input_col2 = st.columns([0.9, 1.1], gap="large")

with input_col1:
    st.markdown("**1 · Upload your resume**")
    resume_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload a text-based PDF resume for best results.",
        label_visibility="collapsed",
    )
    if resume_file:
        st.success(f"Ready to analyze: {resume_file.name}")

with input_col2:
    st.markdown("**2 · Add the job description**")
    job_description = st.text_area(
        "Job description",
        height=190,
        placeholder=(
            "Paste the complete job description here...\n\n"
            "Example:\nRequired skills: Python, SQL, Flask, Git.\n"
            "Experience with React is a plus."
        ),
        label_visibility="collapsed",
    )

analyze_clicked = st.button("Analyze Resume  →", type="primary", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------
# ANALYSIS
# ------------------------------
if analyze_clicked:
    if resume_file is None:
        st.warning("Please upload your resume PDF.")
    elif not job_description.strip():
        st.warning("Please paste a job description.")
    else:
        try:
            with st.spinner("Reading your resume and comparing skills..."):
                resume_text = extract_text_from_pdf(resume_file)
                if not resume_text.strip():
                    st.error("No readable text was found in this PDF. Try a text-based PDF resume.")
                    st.stop()

                resume_skills = extract_skills(resume_text, SKILLS)
                job_skills = extract_skills(job_description, SKILLS)

                optional_keywords = [
                    "is a plus", "nice to have", "optional", "bonus",
                    "preferred", "desirable", "good to have",
                ]
                sentences = re.split(r'[!?\n]+|(?<!\w)\.(?!\w)', job_description)
                optional_skills = set()
                for skill in job_skills:
                    for sentence in sentences:
                        sentence_lower = sentence.lower()
                        if skill.lower() in sentence_lower and any(
                            keyword in sentence_lower for keyword in optional_keywords
                        ):
                            optional_skills.add(skill)
                            break

                required_skills = set(job_skills) - optional_skills
                (
                    matched_required,
                    missing_required,
                    matched_optional,
                    missing_optional,
                    required_score,
                    optional_score,
                ) = match_job_description(resume_skills, required_skills, optional_skills)

            st.markdown("## Your skills gap analysis")
            st.markdown(
                '<div class="panel-subtitle">A quick view of how your recognized resume skills compare with this job description.</div>',
                unsafe_allow_html=True,
            )

            metric1, metric2, metric3 = st.columns(3, gap="medium")
            with metric1:
                st.metric("Mandatory skills match", f"{required_score:.1f}%")
            with metric2:
                st.metric("Skills found in resume", len(resume_skills))
            with metric3:
                st.metric("Mandatory skills missing", len(missing_required))

            chart_col, detail_col = st.columns([0.85, 1.15], gap="large")
            with chart_col:
                st.markdown('<div class="panel"><div class="panel-title">Match overview</div><div class="panel-subtitle">Mandatory skill coverage</div>', unsafe_allow_html=True)
                fig = go.Figure(go.Pie(
                    labels=["Matched", "Missing"],
                    values=[len(matched_required), len(missing_required)],
                    hole=0.72,
                    marker=dict(colors=["#1677e8", "#19bdb4"], line=dict(color="#ffffff", width=4)),
                    textinfo="none",
                    hovertemplate="%{label}: %{value}<extra></extra>",
                ))
                fig.update_layout(
                    height=255,
                    margin=dict(t=5, b=5, l=5, r=5),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.08, xanchor="center", x=0.5),
                    annotations=[dict(
                        text=f"{required_score:.0f}%",
                        x=0.5, y=0.5, font_size=30, font_color="#14233b",
                        showarrow=False,
                    )],
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

            with detail_col:
                st.markdown('<div class="panel"><div class="panel-title">Progress snapshot</div><div class="panel-subtitle">Recognized mandatory skills in this job description</div>', unsafe_allow_html=True)
                st.markdown(f"**Matched skills** <span style='float:right;color:#1677e8;font-weight:700'>{len(matched_required)}</span>", unsafe_allow_html=True)
                st.progress(min(1.0, len(matched_required) / max(1, len(required_skills))))
                st.markdown(f"**Missing skills** <span style='float:right;color:#0e9f98;font-weight:700'>{len(missing_required)}</span>", unsafe_allow_html=True)
                st.progress(min(1.0, len(missing_required) / max(1, len(required_skills))))
                st.markdown(f"**Optional skills match** <span style='float:right;color:#1677e8;font-weight:700'>{optional_score:.1f}%</span>", unsafe_allow_html=True)
                st.progress(min(1.0, max(0.0, optional_score / 100)))
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("### Skills breakdown")
            matched_tab, missing_tab, optional_tab, resume_tab = st.tabs([
                "Matched", "Missing", "Preferred", "Resume skills"
            ])
            with matched_tab:
                if matched_required or matched_optional:
                    st.success("These recognized skills were found in your resume.")
                    for skill in sorted(matched_required):
                        st.markdown(f"- 🟦 **{skill}** · Mandatory")
                    for skill in sorted(matched_optional):
                        st.markdown(f"- 🟢 **{skill}** · Preferred")
                else:
                    st.info("No recognized job-description skills matched your resume.")
            with missing_tab:
                if missing_required:
                    st.warning("These mandatory skills were not detected in the resume text.")
                    for skill in sorted(missing_required):
                        st.markdown(f"- **{skill}**")
                else:
                    st.success("All recognized mandatory skills matched.")
            with optional_tab:
                if matched_optional or missing_optional:
                    if matched_optional:
                        st.markdown("**Already present**")
                        st.write(", ".join(sorted(matched_optional)))
                    if missing_optional:
                        st.markdown("**Potential skills to learn next**")
                        st.write(", ".join(sorted(missing_optional)))
                else:
                    st.info("No optional skills were identified in the job description.")
            with resume_tab:
                if resume_skills:
                    st.markdown("".join(
                        f'<span class="skill-chip">{escape(str(skill))}</span>'
                        for skill in sorted(resume_skills)
                    ), unsafe_allow_html=True)
                else:
                    st.info("No skills from the current skill dictionary were detected.")

            st.markdown("## Your learning plan")
            st.markdown(
                '<div class="panel-subtitle">Start with the mandatory gaps. The recommendations below are starting points, not a guarantee of job readiness.</div>',
                unsafe_allow_html=True,
            )
            if missing_required:
                for skill in sorted(missing_required):
                    with st.expander(f"Learn {skill}"):
                        resources = LEARNING_RESOURCES.get(skill, [
                            "Study the fundamentals of this skill.",
                            "Practice related interview questions.",
                            "Build a small project using this skill.",
                        ])
                        for resource in resources:
                            st.markdown(f"- {resource}")
            else:
                st.success("No recognized mandatory skill gaps were found for this job description.")

            st.markdown("## Download your report")
            pdf_bytes = create_pdf_report(
                resume_skills=resume_skills,
                matched_required=matched_required,
                missing_required=missing_required,
                matched_optional=matched_optional,
                missing_optional=missing_optional,
                required_score=required_score,
                optional_score=optional_score,
                learning_resources=LEARNING_RESOURCES,
            )
            st.download_button(
                label="Download PDF report",
                data=pdf_bytes,
                file_name="resume_analysis_report.pdf",
                mime="application/pdf",
                type="primary",
            )
            st.caption(
                "Note: Matching is based on keywords in the project's skill dictionary. "
                "It does not measure overall employability or guarantee selection."
            )
        except Exception as error:
            st.error(f"Analysis failed: {error}")
            st.info("Check that your PDF is readable and all project modules are configured correctly.")
