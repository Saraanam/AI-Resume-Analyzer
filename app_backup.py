
import re
import streamlit as st

from resume_reader import extract_text_from_pdf
from skill_extractor import extract_skills
from skills import SKILLS
from job_matcher import match_job_description
from recommendations import LEARNING_RESOURCES

#C:\Users\saaan\Downloads\saraResume.pdf.pdf


# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


# -----------------------------
# Header
# -----------------------------
st.title("📄 AI Resume Analyzer")

st.write(
    "Compare your resume with a job description "
    "and discover the skills you need to improve."
)

st.divider()


# -----------------------------
# User Inputs
# -----------------------------
st.subheader("Upload Your Resume")

resume_file = st.file_uploader(
    "Choose your resume (PDF)",
    type=["pdf"]
)

st.subheader("Job Description")

job_description = st.text_area(
    "Paste the job description here",
    height=220,
    placeholder=(
        "Example: Required skills include Python, "
        "SQL, Flask, and Machine Learning..."
    )
)


# -----------------------------
# Analyze Button
# -----------------------------
if st.button("Analyze Resume", type="primary"):

    if resume_file is None:
        st.warning("Please upload your resume PDF.")

    elif not job_description.strip():
        st.warning("Please paste a job description.")

    else:
        try:
            # -----------------------------
            # Step 1: Read Resume PDF
            # -----------------------------
            with st.spinner("Reading your resume..."):
                resume_text = extract_text_from_pdf(
                    resume_file
                )

            if not resume_text.strip():
                st.error(
                    "No readable text was found in this PDF. "
                    "Try a text-based PDF resume."
                )
                st.stop()

            # -----------------------------
            # Step 2: Extract Skills
            # -----------------------------
            resume_skills = extract_skills(
                resume_text,
                SKILLS
            )

            job_skills = extract_skills(
                job_description,
                SKILLS
            )

            # -----------------------------
            # Step 3: Detect Optional Skills
            # -----------------------------
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

            # -----------------------------
            # Step 4: Match Skills
            # -----------------------------
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

            # -----------------------------
            # Step 5: Results Dashboard
            # -----------------------------
            st.divider()
            st.header("📊 Analysis Results")

            # Mandatory match progress
            st.subheader("Mandatory Skills Match")

            progress_value = min(
                max(int(round(required_score)), 0),
                100
            )

            st.progress(progress_value)

            st.caption(
                f"You match {required_score:.1f}% "
                "of the recognized mandatory skills."
            )

            # Summary cards
            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Resume Skills Found",
                len(resume_skills)
            )

            col2.metric(
                "Mandatory Skills Matched",
                f"{len(matched_required)}/"
                f"{len(required_skills)}"
            )

            col3.metric(
                "Mandatory Skills Missing",
                len(missing_required)
            )

            # -----------------------------
            # Step 6: Resume Skills
            # -----------------------------
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

            # -----------------------------
            # Step 7: Mandatory Skills
            # -----------------------------
            st.subheader("✅ Matched Mandatory Skills")

            if matched_required:
                st.success(
                    ", ".join(sorted(matched_required))
                )
            else:
                st.info("No mandatory skills matched.")

            st.subheader("❌ Missing Mandatory Skills")

            if missing_required:
                st.warning(
                    ", ".join(sorted(missing_required))
                )
            else:
                st.success(
                    "All recognized mandatory skills matched!"
                )

            # -----------------------------
            # Step 8: Optional Skills
            # -----------------------------
            st.subheader("⭐ Matched Optional Skills")

            if matched_optional:
                st.success(
                    ", ".join(sorted(matched_optional))
                )
            else:
                st.write("None")

            st.subheader("📝 Missing Optional Skills")

            if missing_optional:
                st.info(
                    ", ".join(sorted(missing_optional))
                )
            else:
                st.write("None")

            # Optional match percentage
            st.metric(
                "Optional Skills Match",
                f"{optional_score:.1f}%"
            )

            # -----------------------------
            # Step 9: Learning Recommendations
            # -----------------------------
            st.divider()
            st.header(
                "📚 Personalized Learning Recommendations"
            )

            if missing_required:

                st.write(
                    "Focus on these missing mandatory skills "
                    "to improve your preparation for this role."
                )

                for skill in sorted(missing_required):

                    st.markdown(f"### {skill}")

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
                    "Great! No recognized mandatory skills "
                    "are missing from your resume for this job."
                )

            # -----------------------------
            # Step 10: Important Note
            # -----------------------------
            st.caption(
                "Note: Results are based on keyword matching "
                "against the skills in the project's skill list. "
                "They do not measure overall employability "
                "or guarantee interview selection."
            )

        except Exception as error:
            st.error(
                f"Analysis failed: {error}"
            )

            st.info(
                "Check that the PDF is readable and all "
                "project modules are configured correctly."
            )