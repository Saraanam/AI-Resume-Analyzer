
LEARNING_RESOURCES = {
    "Machine Learning": [
        "Learn supervised and unsupervised learning",
        "Practice with NumPy, Pandas, and scikit-learn",
        "Build a simple house-price prediction project"
    ],
    "Python": [
        "Revise functions, lists, dictionaries, and file handling",
        "Practice Python coding problems",
        "Build a small automation project"
    ],
    "SQL": [
        "Practice JOINs, GROUP BY, and subqueries",
        "Learn CTEs and window functions",
        "Solve SQL interview questions"
    ],
    "Git": [
        "Learn add, commit, push, and pull",
        "Practice branching and merging",
        "Upload a project to GitHub"
    ],
    "Flask": [
        "Learn routes and HTTP methods",
        "Build a REST API with Flask",
        "Connect Flask to a database"
    ],
    "React": [
        "Learn components, props, and state",
        "Practice useState and useEffect",
        "Build a small interactive web app"
    ],
    "Node.js": [
        "Learn modules and npm",
        "Build a basic Express.js API",
        "Practice handling API requests"
    ]
}


def recommend_learning(missing_skills):
    for skill in sorted(missing_skills):
        print(f"\n--- Recommendations for {skill} ---")

        resources = LEARNING_RESOURCES.get(skill)

        if resources:
            for resource in resources:
                print("-", resource)
        else:
            print("- Search for beginner tutorials and build a small project.")
