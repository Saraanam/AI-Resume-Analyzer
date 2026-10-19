
import re
from resume_reader import extract_text_from_pdf
from skill_extractor import extract_skills
from skills import SKILLS
from job_matcher import match_job_description
from recommendations import recommend_learning

# C:\Users\saaan\Downloads\saraResume.pdf


# Step 1: Get resume PDF path
pdf_path = input(
    "Enter the full path of your PDF resume: "
).strip().strip('"')


# Step 2: Extract text from resume
resume_text = extract_text_from_pdf(pdf_path)


# Step 3: Extract skills from resume
found_skills = extract_skills(resume_text, SKILLS)

print("\n--- Skills Found in Your Resume ---")
for skill in sorted(found_skills):
    print("-", skill)

print(f"\nTotal skills found: {len(found_skills)}")


# Step 4: Accept a multiline job description
print("\nPaste the job description below.")
print("Type END on a new line when finished.")

lines = []

while True:
    line = input()

    if line.strip().upper() == "END":
        break

    lines.append(line)

job_description = "\n".join(lines)


# Step 5: Extract skills from the job description
all_job_skills = extract_skills(job_description, SKILLS)


# Step 6: Identify optional skills

import re

optional_keywords = [
    "is a plus",
    "nice to have",
    "optional",
    "bonus"
]

sentences = re.split(r'[!?\n]+|(?<!\w)\.(?!\w)', job_description)

optional_skills = set()

for skill in all_job_skills:
    for sentence in sentences:
        sentence_lower = sentence.lower()

        if skill.lower() in sentence_lower:
            if any(keyword in sentence_lower for keyword in optional_keywords):
                optional_skills.add(skill)
                break



# Step 7: Separate mandatory and optional skills
required_skills = set(all_job_skills) - optional_skills

print("\n--- Mandatory Skills ---")
for skill in sorted(required_skills):
    print("-", skill)

print("\n--- Optional Skills ---")
if optional_skills:
    for skill in sorted(optional_skills):
        print("-", skill)
else:
    print("No optional skills detected.")


# Step 8: Compare resume skills with job skills
(
    matched_required,
    missing_required,
    matched_optional,
    missing_optional,
    required_score,
    optional_score
) = match_job_description(
    found_skills,
    required_skills,
    optional_skills
)


# Step 9: Display job match results
print("\n--- Job Match Results ---")

print("\nMatched mandatory skills:")
for skill in sorted(matched_required):
    print("-", skill)

print("\nMissing mandatory skills:")
if missing_required:
    for skill in sorted(missing_required):
        print("-", skill)
else:
    print("None")

print(f"\nMandatory match: {required_score:.1f}%")


print("\nMatched optional skills:")
if matched_optional:
    for skill in sorted(matched_optional):
        print("-", skill)
else:
    print("None")

print("\nMissing optional skills:")
if missing_optional:
    for skill in sorted(missing_optional):
        print("-", skill)
else:
    print("None")

print(f"\nOptional match: {optional_score:.1f}%")

# Step 10: Recommend learning resources for missing skills
if missing_required:
    print("\n--- Personalized Learning Recommendations ---")
    recommend_learning(missing_required)
else:
    print("\nGreat! No mandatory skills are missing.")
