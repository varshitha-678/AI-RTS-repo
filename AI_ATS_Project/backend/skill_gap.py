"""
Skill Gap Analysis Module
"""


SKILL_RESOURCES = {
    "python": {"resource": "Python.org / Codecademy", "time_weeks": 4},
    "java": {"resource": "MOOC.fi Java / Udemy", "time_weeks": 6},
    "javascript": {"resource": "javascript.info / freeCodeCamp", "time_weeks": 4},
    "typescript": {"resource": "typescriptlang.org / Udemy", "time_weeks": 3},
    "react": {"resource": "react.dev / Scrimba", "time_weeks": 4},
    "angular": {"resource": "angular.io / Udemy", "time_weeks": 5},
    "vue": {"resource": "vuejs.org / Scrimba", "time_weeks": 3},
    "node.js": {"resource": "nodejs.org / The Odin Project", "time_weeks": 4},
    "django": {"resource": "djangoproject.com / Real Python", "time_weeks": 4},
    "flask": {"resource": "flask.palletsprojects.com / Real Python", "time_weeks": 3},
    "sql": {"resource": "SQLZoo / Mode Analytics", "time_weeks": 3},
    "mongodb": {"resource": "MongoDB University (free)", "time_weeks": 2},
    "postgresql": {"resource": "PostgreSQL Docs / Udemy", "time_weeks": 3},
    "docker": {"resource": "docs.docker.com / Docker & Kubernetes Udemy", "time_weeks": 2},
    "kubernetes": {"resource": "kubernetes.io / CKA Course", "time_weeks": 4},
    "aws": {"resource": "AWS Skill Builder / A Cloud Guru", "time_weeks": 6},
    "azure": {"resource": "Microsoft Learn (free)", "time_weeks": 6},
    "gcp": {"resource": "Google Cloud Skills Boost", "time_weeks": 6},
    "git": {"resource": "git-scm.com / GitHub Learning Lab", "time_weeks": 1},
    "machine learning": {"resource": "Andrew Ng ML Course / fast.ai", "time_weeks": 8},
    "deep learning": {"resource": "deeplearning.ai / fast.ai", "time_weeks": 8},
    "nlp": {"resource": "Hugging Face Course / CS224N Stanford", "time_weeks": 8},
    "tensorflow": {"resource": "tensorflow.org / Coursera", "time_weeks": 4},
    "pytorch": {"resource": "pytorch.org / fast.ai", "time_weeks": 4},
    "rest api": {"resource": "REST API Tutorial / Postman Learning", "time_weeks": 2},
    "html": {"resource": "MDN Web Docs / freeCodeCamp", "time_weeks": 2},
    "css": {"resource": "MDN Web Docs / freeCodeCamp", "time_weeks": 2},
    "tailwind": {"resource": "tailwindcss.com / Scrimba", "time_weeks": 1},
    "data science": {"resource": "Kaggle / Coursera Data Science", "time_weeks": 12},
    "devops": {"resource": "DevOps Roadmap / Udemy", "time_weeks": 8},
    "linux": {"resource": "Linux Foundation / OverTheWire", "time_weeks": 3},
}


SKILL_CERTIFICATIONS = {
    "aws": ["AWS Certified Cloud Practitioner", "AWS Certified Solutions Architect"],
    "azure": ["Microsoft Certified: Azure Fundamentals AZ-900", "AZ-204 Developer"],
    "gcp": ["Google Cloud Associate Cloud Engineer", "Professional Data Engineer"],
    "docker": ["Docker Certified Associate (DCA)"],
    "kubernetes": ["Certified Kubernetes Administrator (CKA)", "CKAD"],
    "machine learning": ["Google Professional ML Engineer", "AWS ML Specialty"],
    "data science": ["IBM Data Science Professional Certificate", "Coursera Data Science"],
    "devops": ["AWS DevOps Engineer", "Azure DevOps Engineer"],
    "python": ["PCEP - Python Certified Entry Programmer", "PCAP"],
    "sql": ["Oracle SQL Certified Expert", "Microsoft DP-900"],
    "react": ["Meta Front-End Developer Certificate"],
    "nlp": ["Hugging Face NLP Course Certificate", "deeplearning.ai NLP Specialization"],
}


def analyze_skill_gap(resume_skills: list, jd_skills: list) -> dict:
    """
    Compare resume skills vs JD skills and produce gap analysis.
    """
    resume_set = set(s.lower() for s in resume_skills)
    jd_set = set(s.lower() for s in jd_skills)

    matched = resume_set & jd_set
    missing = jd_set - resume_set
    extra = resume_set - jd_set

    gap_details = []
    for skill in sorted(missing):
        info = SKILL_RESOURCES.get(skill, {"resource": "Search online / YouTube", "time_weeks": 2})
        gap_details.append({
            "skill": skill,
            "resource": info["resource"],
            "time_weeks": info["time_weeks"],
        })

    return {
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "extra_skills": sorted(extra),
        "gap_details": gap_details,
        "total_required": len(jd_set),
        "total_matched": len(matched),
        "coverage_percentage": round(len(matched) / len(jd_set) * 100, 2) if jd_set else 100.0,
    }


def get_skill_certifications(missing_skills: list) -> list:
    certs = []
    for skill in missing_skills:
        skill_lower = skill.lower()
        if skill_lower in SKILL_CERTIFICATIONS:
            for cert in SKILL_CERTIFICATIONS[skill_lower]:
                if cert not in certs:
                    certs.append(cert)
    return certs[:8]
