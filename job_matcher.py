

def match_job_description(resume_skills, required_skills, optional_skills=None):
    if optional_skills is None:
        optional_skills = set()

    # Convert resume skills to lowercase for comparison
    resume_skills_lower = {
        skill.lower() for skill in resume_skills
    }

    # Check mandatory skills
    matched_required = []
    missing_required = []

    for skill in required_skills:
        if skill.lower() in resume_skills_lower:
            matched_required.append(skill)
        else:
            missing_required.append(skill)

    # Check optional skills
    matched_optional = []
    missing_optional = []

    for skill in optional_skills:
        if skill.lower() in resume_skills_lower:
            matched_optional.append(skill)
        else:
            missing_optional.append(skill)

    # Calculate mandatory match percentage
    if required_skills:
        required_score = (
            len(matched_required) / len(required_skills)
        ) * 100
    else:
        required_score = 0

    # Calculate optional match percentage
    if optional_skills:
        optional_score = (
            len(matched_optional) / len(optional_skills)
        ) * 100
    else:
        optional_score = 0

    return (
        matched_required,
        missing_required,
        matched_optional,
        missing_optional,
        required_score,
        optional_score
    )
