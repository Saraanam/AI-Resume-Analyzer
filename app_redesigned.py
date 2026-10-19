

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.units import inch

import re
import streamlit as st

from resume_reader import extract_text_from_pdf
from skill_extractor import extract_skills
from skills import SKILLS
from job_matcher import match_job_description
from recommendations import LEARNING_RESOURCES


def create_pdf_report(
    resume_skills,
    matched_required,
    missing_required,
    matched_optional,
    missing_optional,
    required_score,
    optional_score,
    learning_resources
):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#4338CA"),
        spaceAfter=16
    ))

    styles.add(ParagraphStyle(
        name="ReportHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#4338CA"),
        spaceBefore=12,
        spaceAfter=6
    ))

    story = [
        Paragraph(
            "AI Resume Analyzer Report",
            styles["ReportTitle"]
        ),
        Paragraph(
            "Resume and job description comparison",
            styles["BodyText"]
        ),
        Spacer(1, 16),
        Paragraph("Match Summary", styles["ReportHeading"])
    ]

    summary_data = [
        ["Metric", "Result"],
        ["Mandatory skill match", f"{required_score:.1f}%"],
        ["Optional skill match", f"{optional_score:.1f}%"],
        ["Resume skills identified", str(len(resume_skills))],
        [
            "Mandatory skills matched",
            f"{len(matched_required)}/"
            f"{len(matched_required) + len(missing_required)}"
        ],
        ["Mandatory skills missing", str(len(missing_required))]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[3.6 * inch, 2.0 * inch]
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#4338CA")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5,
         colors.HexColor("#D1D5DB")),
        ("BACKGROUND", (0, 1), (-1, -1),
         colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "TOP")
    ]))

    story.extend([
        summary_table,
        Spacer(1, 12)
    ])

    def add_skill_section(title, skills):
        story.append(
            Paragraph(
                escape(title),
                styles["ReportHeading"]
            )
        )

        if skills:
            for skill in sorted(skills):
                story.append(
                    Paragraph(
                        "&#8226; " + escape(str(skill)),
                        styles["BodyText"]
                    )
                )
        else:
            story.append(
                Paragraph("None identified.", styles["BodyText"])
            )

        story.append(Spacer(1, 6))

    add_skill_section(
        "Skills Identified in Resume",
        resume_skills
    )

    add_skill_section(
        "Matched Mandatory Skills",
        matched_required
    )

    add_skill_section(
        "Missing Mandatory Skills",
        missing_required
    )

    add_skill_section(
        "Matched Optional Skills",
        matched_optional
    )

    add_skill_section(
        "Missing Optional Skills",
        missing_optional
    )

    story.append(
        Paragraph(
            "Learning Recommendations",
            styles["ReportHeading"]
        )
    )

    if missing_required:
        for skill in sorted(missing_required):
            story.append(
                Paragraph(
                    "<b>" + escape(str(skill)) + "</b>",
                    styles["BodyText"]
                )
            )

            resources = learning_resources.get(
                skill,
                [
                    "Study the fundamentals of this skill.",
                    "Practice related interview questions.",
                    "Build a small project using this skill."
                ]
            )

            for resource in resources:
                story.append(
                    Paragraph(
                        "&#8226; " + escape(str(resource)),
                        styles["BodyText"]
                    )
                )

            story.append(Spacer(1, 6))

    else:
        story.append(
            Paragraph(
                "No recognized mandatory skills were missing.",
                styles["BodyText"]
            )
        )

    story.extend([
        Spacer(1, 14),
        Paragraph(
            "Note: This report uses keyword matching against "
            "the project's skill dictionary. It does not measure "
            "overall employability or guarantee selection.",
            styles["Italic"]
        )
    ])

    doc.build(story)

    buffer.seek(0)
    return buffer.getvalue()

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


# ==========================================
# CUSTOM DARK THEME
# ==========================================
st.markdown("""
<style>
    .stApp {
        background-color: #0b1020;
        color: #e5e7eb;
    }

    [data-testid="stHeader"] {
        background-color: rgba(11, 16, 32, 0.9);
    }

    h1, h2, h3 {
        color: #f8fafc;
    }

    p, label {
        color: #cbd5e1;
    }

    [data-testid="stMetric"] {
        background-color: #151d31;
        border: 1px solid #293550;
        padding: 20px;
        border-radius: 14px;
    }

    [data-testid="stMetricLabel"] {
        color: #a5b4fc;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff;
    }

    .stButton > button {
        background: linear-gradient(90deg, #7c3aed, #4f46e5);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 22px;
        font-weight: 600;
    }

    .stButton > button:hover {
        border: 1px solid #a78bfa;
        color: white;
    }

    [data-testid="stTextArea"] textarea {
        background-color: #151d31;
        color: #f8fafc;
        border: 1px solid #374151;
        border-radius: 10px;
    }

    [data-testid="stFileUploader"] {
        background-color: #151d31;
        border-radius: 12px;
        padding: 12px;
    }

    [data-baseweb="tab-list"] {
        gap: 8px;
    }

    [data-baseweb="tab"] {
        background-color: #151d31;
        border-radius: 8px;
        padding: 10px 16px;
    }

    hr {
        border-color: #293550;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
    }

    .section-card {
        background-color: #151d31;
        border: 1px solid #293550;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# HEADER
# ==========================================
st.title("📄 AI Resume Analyzer")

st.markdown(
    '<p class="hero-subtitle">'
    'Analyze your resume, compare job requirements, '
    'and discover skills to improve.'
    '</p>',
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# INPUT SECTION
# ==========================================
st.subheader("📝 Start Your Analysis")

resume_file = st.file_uploader(
    "Upload your resume (PDF)",
    type=["pdf"],
    help="Upload a text-based PDF resume."
)

job_description = st.text_area(
    "Job Description",
    height=220,
    placeholder=(
        "Paste the complete job description here...\n\n"
        "Example:\n"
        "Required skills: Python, SQL, Flask, Git.\n"
        "Experience with React is a plus."
    )
)


# ==========================================
# ANALYZE RESUME
# ==========================================
if st.button("🚀 Analyze Resume", type="primary"):

    if resume_file is None:
        st.warning("Please upload your resume PDF.")

    elif not job_description.strip():
        st.warning("Please paste a job description.")

    else:
        try:
            with st.spinner("Analyzing your resume..."):

                # STEP 1: READ PDF
                resume_text = extract_text_from_pdf(
                    resume_file
                )

                if not resume_text.strip():
                    st.error(
                        "No readable text was found in this PDF. "
                        "Try a text-based PDF resume."
                    )
                    st.stop()

                # STEP 2: EXTRACT SKILLS
                resume_skills = extract_skills(
                    resume_text,
                    SKILLS
                )

                job_skills = extract_skills(
                    job_description,
                    SKILLS
                )

                # STEP 3: DETECT OPTIONAL SKILLS
                optional_keywords = [
                    "is a plus",
                    "nice to have",
                    "optional",
                    "bonus"
                ]

                sentences = re.split(
                    r'[!?\n]+|(?<!\w)\.(?!\w)',
                    job_description
                )

                optional_skills = set()

                for skill in job_skills:
                    for sentence in sentences:
                        sentence_lower = sentence.lower()

                        if skill.lower() in sentence_lower:
                            if any(
                                keyword in sentence_lower
                                for keyword in optional_keywords
                            ):
                                optional_skills.add(skill)
                                break

                required_skills = (
                    set(job_skills) - optional_skills
                )

                # STEP 4: MATCH SKILLS
                (
                    matched_required,
                    missing_required,
                    matched_optional,
                    missing_optional,
                    required_score,
                    optional_score
                ) = match_job_description(
                    resume_skills,
                    required_skills,
                    optional_skills
                )

            # ==========================================
            # RESULTS DASHBOARD
            # ==========================================
            st.divider()
            st.header("📊 Your Analysis Results")

            # PROGRESS BAR
            st.subheader("Mandatory Skills Match")

            progress_value = min(
                max(int(round(required_score)), 0),
                100
            )

            st.progress(progress_value)

            st.caption(
                f"{required_score:.1f}% of recognized "
                "mandatory skills matched."
            )

            # SUMMARY CARDS
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Resume Skills Found",
                    len(resume_skills)
                )

            with col2:
                st.metric(
                    "Mandatory Skills Matched",
                    f"{len(matched_required)}/"
                    f"{len(required_skills)}"
                )

            with col3:
                st.metric(
                    "Mandatory Skills Missing",
                    len(missing_required)
                )

            # OPTIONAL MATCH
            st.metric(
                "Optional Skills Match",
                f"{optional_score:.1f}%"
            )

            # ==========================================
            # RESUME SKILLS
            # ==========================================
            with st.expander(
                "🔍 Skills Found in Your Resume"
            ):
                if resume_skills:
                    st.write(
                        ", ".join(sorted(resume_skills))
                    )
                else:
                    st.info(
                        "No recognized skills were found."
                    )

            # ==========================================
            # SKILL BREAKDOWN TABS
            # ==========================================
            st.divider()
            st.subheader("🎯 Skill Breakdown")

            matched_tab, missing_tab, optional_tab = st.tabs(
                [
                    "✅ Matched",
                    "❌ Missing",
                    "⭐ Optional"
                ]
            )

            # MATCHED TAB
            with matched_tab:
                st.markdown(
                    "#### Mandatory skills found in your resume"
                )

                if matched_required:
                    st.success(
                        "You match these mandatory skills:"
                    )

                    for skill in sorted(matched_required):
                        st.markdown(f"- 🟢 **{skill}**")
                else:
                    st.info(
                        "No mandatory skills matched yet."
                    )

                if matched_optional:
                    st.markdown("#### Matched optional skills")

                    for skill in sorted(matched_optional):
                        st.markdown(f"- 🟢 {skill}")

            # MISSING TAB
            with missing_tab:
                st.markdown(
                    "#### Mandatory skills to improve"
                )

                if missing_required:
                    for skill in sorted(missing_required):
                        st.markdown(f"- 🔴 **{skill}**")
                else:
                    st.success(
                        "All recognized mandatory skills matched!"
                    )

                if missing_optional:
                    st.markdown("#### Missing optional skills")

                    for skill in sorted(missing_optional):
                        st.markdown(f"- 🟡 {skill}")

            # OPTIONAL TAB
            with optional_tab:
                st.markdown("#### Preferred skills")

                if matched_optional:
                    st.success(
                        "Optional skills already present:"
                    )

                    for skill in sorted(matched_optional):
                        st.markdown(f"- 🟢 {skill}")
                else:
                    st.write(
                        "No optional skills matched."
                    )

                if missing_optional:
                    st.info(
                        "Optional skills you could learn:"
                    )

                    for skill in sorted(missing_optional):
                        st.markdown(f"- 🟡 {skill}")

            # ==========================================
            # LEARNING RECOMMENDATIONS
            # ==========================================
            st.divider()
            st.header("📚 Personalized Learning Plan")

            if missing_required:
                st.write(
                    "Focus on these missing mandatory skills "
                    "to prepare for this role."
                )

                for skill in sorted(missing_required):
                    with st.expander(
                        f"📘 Learn {skill}"
                    ):
                        resources = LEARNING_RESOURCES.get(
                            skill,
                            [
                                "Study the fundamentals of this skill.",
                                "Practice related interview questions.",
                                "Build a small project using this skill."
                            ]
                        )

                        for resource in resources:
                            st.markdown(f"- {resource}")

            else:
                st.success(
                    "No recognized mandatory skills are missing "
                    "from your resume for this job."
                )
                
            # ==========================================
            # DOWNLOAD PDF REPORT
            # ==========================================
            st.divider()
            st.subheader("📥 Download Your Report")

            pdf_bytes = create_pdf_report(
                resume_skills=resume_skills,
                matched_required=matched_required,
                missing_required=missing_required,
                matched_optional=matched_optional,
                missing_optional=missing_optional,
                required_score=required_score,
                optional_score=optional_score,
                learning_resources=LEARNING_RESOURCES
            )

            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_bytes,
                file_name="resume_analysis_report.pdf",
                mime="application/pdf",
                type="primary"
            )


            # ==========================================
            # FOOTNOTE
            # ==========================================
            st.divider()

            st.caption(
                "Note: Matching is based on keywords in the "
                "project's skill dictionary. It does not measure "
                "overall employability or guarantee selection."
            )

        except Exception as error:
            st.error(
                f"Analysis failed: {error}"
            )

            st.info(
                "Check that your PDF is readable and all "
                "project modules are configured correctly."
            )
