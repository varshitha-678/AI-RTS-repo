"""
Views for AI ATS Application — page views + REST API endpoints.
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from ats_app.models import UserProfile, UploadedResume
from backend.resume_parser import parse_resume_bytes
from backend.ats_engine import parse_resume, calculate_ats_score
from backend.skill_gap import analyze_skill_gap
from backend.career_path import generate_career_path

import database.mongodb as db


# ── Auth Views ──────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "login.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")
        role = request.POST.get("role", "user")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "register.html")

        user = User.objects.create_user(username=username, email=email, password=password)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role if role in ["user", "guest"] else "user"
        profile.save()
        login(request, user)
        return redirect("dashboard")

    return render(request, "register.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# ── Page Views ───────────────────────────────────────────────────────────────

@login_required
def dashboard_view(request):
    results = db.get_results_by_user(str(request.user.id))
    # Convert ObjectId to string for template
    for r in results:
        r["_id"] = str(r["_id"])
    profile = getattr(request.user, "profile", None)
    role = profile.role if profile else "user"
    return render(request, "dashboard.html", {
        "user": request.user,
        "results": results,
        "role": role,
    })


@login_required
def upload_view(request):
    return render(request, "upload.html", {"user": request.user})


@login_required
def result_view(request, result_id):
    import bson
    try:
        result_doc = db.get_results_collection().find_one({"_id": bson.ObjectId(result_id)})
        if not result_doc:
            messages.error(request, "Result not found.")
            return redirect("dashboard")
        result_doc["_id"] = str(result_doc["_id"])
        career = db.get_career_path(result_id)
        if career:
            career["_id"] = str(career["_id"])
        return render(request, "result.html", {
            "result": result_doc,
            "career": career,
            "user": request.user,
        })
    except Exception as e:
        messages.error(request, f"Error loading result: {e}")
        return redirect("dashboard")


@login_required
def career_path_view(request, result_id):
    import bson
    try:
        career = db.get_career_path(result_id)
        if not career:
            messages.error(request, "Career path not found.")
            return redirect("dashboard")
        career["_id"] = str(career["_id"])
        return render(request, "career_path.html", {
            "career": career,
            "result_id": result_id,
            "user": request.user,
        })
    except Exception as e:
        messages.error(request, f"Error: {e}")
        return redirect("dashboard")


@login_required
def admin_panel_view(request):
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("dashboard")
    all_results = db.get_all_results()
    for r in all_results:
        r["_id"] = str(r["_id"])
    all_users = list(User.objects.all().values("id", "username", "email", "date_joined"))
    return render(request, "admin_panel.html", {
        "results": all_results,
        "users": all_users,
        "user": request.user,
    })


# ── API Endpoints ─────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def upload_resume(request):
    """POST /upload_resume — upload and parse a resume file."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=401)
    try:
        resume_file = request.FILES.get("resume")
        if not resume_file:
            return JsonResponse({"error": "No resume file provided."}, status=400)

        allowed_ext = {".pdf", ".docx", ".doc", ".txt"}
        ext = os.path.splitext(resume_file.name)[1].lower()
        if ext not in allowed_ext:
            return JsonResponse({"error": f"Unsupported file type: {ext}"}, status=400)

        file_bytes = resume_file.read()
        resume_text = parse_resume_bytes(file_bytes, resume_file.name)

        if not resume_text.strip():
            return JsonResponse({"error": "Could not extract text from resume."}, status=400)

        parsed_data = parse_resume(resume_text)
        resume_id = db.save_resume(
            user_id=str(request.user.id),
            filename=resume_file.name,
            text=resume_text,
            parsed_data={
                k: v for k, v in parsed_data.items() if k != "tokens"
            },
        )

        # Save reference in Django model
        UploadedResume.objects.create(
            user=request.user,
            filename=resume_file.name,
            mongo_resume_id=resume_id,
        )

        return JsonResponse({
            "success": True,
            "resume_id": resume_id,
            "filename": resume_file.name,
            "extracted_skills": parsed_data["skills"],
            "name": parsed_data["name"],
            "experience_years": parsed_data["experience_years"],
            "education": parsed_data["education"],
            "preview": resume_text[:300],
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def analyze_resume(request):
    """POST /analyze_resume — full ATS analysis."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=401)
    try:
        data = json.loads(request.body)
        resume_id = data.get("resume_id")
        job_description = data.get("job_description", "").strip()
        job_title = data.get("job_title", "Target Role").strip()

        if not resume_id or not job_description:
            return JsonResponse({"error": "resume_id and job_description are required."}, status=400)

        resume_doc = db.get_resume_by_id(resume_id)
        if not resume_doc:
            return JsonResponse({"error": "Resume not found."}, status=404)

        resume_text = resume_doc["text"]
        parsed_resume = parse_resume(resume_text)
        ats_result = calculate_ats_score(resume_text, job_description, parsed_resume)

        # Skill gap
        gap = analyze_skill_gap(parsed_resume["skills"], ats_result["jd_skills"])
        ats_result["skill_gap"] = gap

        # Career path
        career = generate_career_path(
            resume_skills=parsed_resume["skills"],
            jd_skills=ats_result["jd_skills"],
            ats_score=ats_result["ats_score"],
            job_title=job_title,
        )
        ats_result["career_path"] = career
        ats_result["job_title"] = job_title

        # Save to MongoDB
        result_id = db.save_result(
            user_id=str(request.user.id),
            resume_id=resume_id,
            job_description=job_description,
            ats_result=ats_result,
        )
        db.save_career_path(
            user_id=str(request.user.id),
            result_id=result_id,
            career_data=career,
        )

        return JsonResponse({
            "success": True,
            "result_id": result_id,
            "ats_result": ats_result,
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ats_score(request):
    """POST /ats_score — quick score from raw text."""
    try:
        data = json.loads(request.body)
        resume_text = data.get("resume_text", "")
        jd_text = data.get("job_description", "")
        if not resume_text or not jd_text:
            return JsonResponse({"error": "resume_text and job_description required."}, status=400)
        result = calculate_ats_score(resume_text, jd_text)
        return JsonResponse({"ats_score": result["ats_score"], "match_percentage": result["match_percentage"]})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def skill_gap(request):
    """POST /skill_gap — skill gap between resume and JD."""
    try:
        data = json.loads(request.body)
        resume_skills = data.get("resume_skills", [])
        jd_skills = data.get("jd_skills", [])
        gap = analyze_skill_gap(resume_skills, jd_skills)
        return JsonResponse(gap)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def career_path_api(request):
    """POST /career_path — generate career roadmap."""
    try:
        data = json.loads(request.body)
        resume_skills = data.get("resume_skills", [])
        jd_skills = data.get("jd_skills", [])
        ats_score_val = data.get("ats_score", 50.0)
        job_title = data.get("job_title", "Target Role")
        path = generate_career_path(resume_skills, jd_skills, ats_score_val, job_title)
        return JsonResponse(path)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def ranking(request):
    """GET /ranking — rank all resumes by ATS score."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=401)
    try:
        profile = getattr(request.user, "profile", None)
        if profile and profile.role == "admin":
            results = db.get_all_results()
        else:
            results = db.get_results_by_user(str(request.user.id))

        ranked = []
        for r in results:
            ats = r.get("ats_result", {})
            ranked.append({
                "result_id": str(r["_id"]),
                "name": ats.get("name", "Unknown"),
                "ats_score": ats.get("ats_score", 0),
                "match_percentage": ats.get("match_percentage", 0),
                "job_title": ats.get("job_title", ""),
                "created_at": str(r.get("created_at", "")),
            })

        ranked.sort(key=lambda x: x["ats_score"], reverse=True)
        for i, r in enumerate(ranked):
            r["rank"] = i + 1

        return JsonResponse({"rankings": ranked})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
