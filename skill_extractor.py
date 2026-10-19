
import re

def extract_skills(resume_text, skills):
    found_skills = []

    for skill in skills:
        prefix = r'(?<!\w)' if skill[0].isalnum() else ''
        suffix = r'(?!\w)' if skill[-1].isalnum() else ''

        pattern = prefix + re.escape(skill) + suffix

        if re.search(pattern, resume_text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills
