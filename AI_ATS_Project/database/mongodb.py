"""
MongoDB connection and collection management.
"""
import pymongo
import os
from datetime import datetime

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.environ.get("MONGO_DB_NAME", "ats_database")

_client = None


def get_client():
    global _client
    if _client is None:
        _client = pymongo.MongoClient(MONGO_URI)
    return _client


def get_db():
    return get_client()[DB_NAME]


# --- Collections ---

def get_users_collection():
    return get_db()["users"]


def get_resumes_collection():
    return get_db()["resumes"]


def get_jobs_collection():
    return get_db()["jobs"]


def get_results_collection():
    return get_db()["results"]


def get_career_paths_collection():
    return get_db()["career_paths"]


# --- User helpers ---

def create_user(username, email, password_hash, role="user"):
    col = get_users_collection()
    if col.find_one({"email": email}):
        return None, "Email already exists"
    user = {
        "username": username,
        "email": email,
        "password": password_hash,
        "role": role,
        "created_at": datetime.utcnow(),
    }
    result = col.insert_one(user)
    return str(result.inserted_id), None


def find_user_by_email(email):
    return get_users_collection().find_one({"email": email})


def find_user_by_id(user_id):
    from bson import ObjectId
    return get_users_collection().find_one({"_id": ObjectId(user_id)})


# --- Resume helpers ---

def save_resume(user_id, filename, text, parsed_data):
    col = get_resumes_collection()
    doc = {
        "user_id": user_id,
        "filename": filename,
        "text": text,
        "parsed_data": parsed_data,
        "uploaded_at": datetime.utcnow(),
    }
    result = col.insert_one(doc)
    return str(result.inserted_id)


def get_resume_by_id(resume_id):
    from bson import ObjectId
    return get_resumes_collection().find_one({"_id": ObjectId(resume_id)})


# --- Result helpers ---

def save_result(user_id, resume_id, job_description, ats_result):
    col = get_results_collection()
    doc = {
        "user_id": user_id,
        "resume_id": resume_id,
        "job_description": job_description,
        "ats_result": ats_result,
        "created_at": datetime.utcnow(),
    }
    result = col.insert_one(doc)
    return str(result.inserted_id)


def get_results_by_user(user_id):
    col = get_results_collection()
    return list(col.find({"user_id": user_id}).sort("created_at", -1))


def get_all_results():
    col = get_results_collection()
    return list(col.find().sort("created_at", -1))


# --- Career Path helpers ---

def save_career_path(user_id, result_id, career_data):
    col = get_career_paths_collection()
    doc = {
        "user_id": user_id,
        "result_id": result_id,
        "career_data": career_data,
        "created_at": datetime.utcnow(),
    }
    result = col.insert_one(doc)
    return str(result.inserted_id)


def get_career_path(result_id):
    return get_career_paths_collection().find_one({"result_id": result_id})
