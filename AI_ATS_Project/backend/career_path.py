"""
Career Path & Roadmap Generation Module
"""
from backend.skill_gap import analyze_skill_gap, get_skill_certifications, SKILL_RESOURCES


RESUME_TIPS = [
    "Add a strong professional summary at the top tailored to the job description.",
    "Quantify your achievements (e.g., 'Improved performance by 30%').",
    "Use action verbs: Built, Developed, Optimized, Led, Designed.",
    "Include relevant keywords from the job description to pass ATS filters.",
    "Keep resume to 1–2 pages; remove irrelevant experience.",
    "Add a dedicated Skills section with all technical skills listed.",
    "Include GitHub profile, LinkedIn, or portfolio links.",
    "List projects with tech stack, impact, and links.",
    "Tailor your resume for each job application.",
    "Use a clean, ATS-friendly format (no tables, no images, simple fonts).",
]


def generate_learning_steps(missing_skills: list) -> list:
    """Generate step-by-step learning path for missing skills."""
    steps = []
    step_num = 1
    for skill in missing_skills:
        info = SKILL_RESOURCES.get(
            skill.lower(), {"resource": "Search YouTube / Udemy", "time_weeks": 2}
        )
        steps.append({
            "step": step_num,
            "action": f"Learn {skill.title()} Fundamentals",
            "resource": info["resource"],
            "time_weeks": info["time_weeks"],
        })
        step_num += 1
        steps.append({
            "step": step_num,
            "action": f"Build a Project Using {skill.title()}",
            "resource": "GitHub / Personal Portfolio",
            "time_weeks": 1,
        })
        step_num += 1
    return steps


def generate_project_suggestions(missing_skills: list, job_title: str = "") -> list:
    """Suggest projects that cover missing skills."""
    projects = []
    if not missing_skills:
        return ["Build a full-stack portfolio project showcasing your current skills."]

    all_skills = ", ".join(s.title() for s in missing_skills[:3])
    projects.append(f"Build a full-stack web app using {all_skills}.")
    projects.append("Contribute to an open-source project on GitHub.")
    projects.append("Create an API integration project and deploy it to the cloud.")
    projects.append(f"Develop a CRUD application with REST API using {missing_skills[0].title()} if applicable.")
    projects.append("Build a data pipeline / automation script using Python.")
    return projects[:5]


def estimate_readiness_time(missing_skills: list) -> str:
    """Estimate total weeks needed to become job-ready."""
    total_weeks = 0
    for skill in missing_skills:
        info = SKILL_RESOURCES.get(skill.lower(), {"time_weeks": 2})
        total_weeks += info["time_weeks"]
    # Assume some parallel learning
    adjusted = max(int(total_weeks * 0.6), 1)
    if adjusted <= 2:
        return "1–2 Weeks"
    elif adjusted <= 4:
        return "2–4 Weeks"
    elif adjusted <= 8:
        return "4–8 Weeks"
    elif adjusted <= 12:
        return "2–3 Months"
    elif adjusted <= 20:
        return "3–5 Months"
    else:
        return "5–8 Months"


def generate_career_path(
    resume_skills: list,
    jd_skills: list,
    ats_score: float,
    job_title: str = "Target Role",
) -> dict:
    """Full career roadmap generation."""
    gap = analyze_skill_gap(resume_skills, jd_skills)
    missing = gap["missing_skills"]

    steps = generate_learning_steps(missing)
    # Final steps always include apply
    apply_step = len(steps) + 1
    steps.append({
        "step": apply_step,
        "action": "Polish Resume and Add New Projects",
        "resource": "Resume review / peer feedback",
        "time_weeks": 1,
    })
    steps.append({
        "step": apply_step + 1,
        "action": f"Apply for {job_title} Positions",
        "resource": "LinkedIn / Indeed / Company Careers Pages",
        "time_weeks": 0,
    })

    certifications = get_skill_certifications(missing)
    projects = generate_project_suggestions(missing, job_title)
    estimated_time = estimate_readiness_time(missing)

    # Readiness level
    if ats_score >= 80:
        readiness = "High — You're nearly ready to apply!"
        priority = "low"
    elif ats_score >= 60:
        readiness = "Medium — Close, but some upskilling needed."
        priority = "medium"
    elif ats_score >= 40:
        readiness = "Low-Medium — Significant upskilling required."
        priority = "high"
    else:
        readiness = "Low — Substantial learning needed before applying."
        priority = "critical"

    resume_tips = RESUME_TIPS[:6]

    return {
        "job_title": job_title,
        "ats_score": ats_score,
        "readiness_level": readiness,
        "priority": priority,
        "missing_skills": missing,
        "matched_skills": gap["matched_skills"],
        "coverage_percentage": gap["coverage_percentage"],
        "learning_steps": steps,
        "project_suggestions": projects,
        "certifications": certifications,
        "resume_improvement_tips": resume_tips,
        "estimated_time": estimated_time,
        "career_roadmap": [
            f"Step {s['step']}: {s['action']} ({s['time_weeks']}w)" if s['time_weeks'] > 0
            else f"Step {s['step']}: {s['action']}"
            for s in steps
        ],
    }
