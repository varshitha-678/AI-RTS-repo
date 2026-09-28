# AI-Powered ATS Resume & Skill Gap Analyzer

A full-stack web application that uses NLP, BERT embeddings, and ensemble machine learning to analyze resumes, calculate ATS scores, identify skill gaps, and generate personalized career roadmaps.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | HTML5, Tailwind CSS, JavaScript |
| Backend | Python 3.8+, Django 4.2 |
| Database | MongoDB (PyMongo) + SQLite (Django auth) |
| AI/NLP | Sentence-BERT, BERT, TF-IDF, Word2Vec, NLTK, spaCy |
| ML | Scikit-learn (RF, LR, SVM), PyTorch, Hugging Face Transformers |
| Parsing | PyPDF2, python-docx, Apache Tika |

---

## Project Structure

```
AI_ATS_Project/
├── manage.py
├── requirements.txt
├── README.md
├── ats_project/             # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── ats_app/                 # Django app
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── backend/                 # Core logic
│   ├── ats_engine.py        # NER, preprocessing, ATS scoring
│   ├── resume_parser.py     # PDF/DOCX/TXT parsing
│   ├── skill_gap.py         # Skill gap analysis
│   ├── career_path.py       # Career roadmap generation
│   └── embeddings.py        # Unified embedding utility
├── ai_models/               # AI model implementations
│   ├── bert_model.py
│   ├── sentence_transformer.py
│   ├── tfidf_model.py
│   └── ensemble_model.py
├── database/
│   └── mongodb.py           # MongoDB collections & helpers
└── frontend/                # HTML templates
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── upload.html
    ├── result.html
    ├── career_path.html
    └── admin_panel.html
```

---

## Setup Instructions (Windows / VS Code)

### Prerequisites
- Python 3.8+ installed
- MongoDB Community Server running on `localhost:27017`
- VS Code with Python extension

### Step 1 — Clone / Extract Project

```bash
# Extract the zip and open folder in VS Code
cd AI_ATS_Project
```

### Step 2 — Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** PyTorch installation may require the CUDA or CPU wheel. If `pip install torch` fails, visit https://pytorch.org/get-started/ and install the CPU version:
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cpu
> ```

### Step 4 — Download NLTK Data

```python
python -c "import nltk; nltk.download('all')"
```

### Step 5 — Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### Step 6 — Start MongoDB

Make sure MongoDB is running:
```bash
# Windows — MongoDB should be running as a service, or start manually:
"C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath C:\data\db
```

### Step 7 — Configure Environment (Optional)

Create a `.env` file or set environment variables:
```
DJANGO_SECRET_KEY=your-secret-key-here
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=ats_database
DEBUG=True
```

### Step 8 — Run Django Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 9 — Create Admin User

```bash
python manage.py createsuperuser
```

Then assign admin role in Django shell:
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
from ats_app.models import UserProfile
user = User.objects.get(username='your_admin_username')
profile, _ = UserProfile.objects.get_or_create(user=user)
profile.role = 'admin'
profile.save()
```

### Step 10 — Run the Server

```bash
python manage.py runserver
```

Open in browser: **http://127.0.0.1:8000**

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/upload_resume` | Upload and parse a resume file |
| POST | `/analyze_resume` | Full ATS analysis |
| POST | `/ats_score` | Quick score from raw text |
| POST | `/skill_gap` | Skill gap analysis |
| POST | `/career_path` | Generate career roadmap |
| GET | `/ranking` | Resume ranking by ATS score |

---

## Pages

| URL | Description |
|---|---|
| `/login/` | Login page |
| `/register/` | Registration page |
| `/dashboard/` | User dashboard with history |
| `/upload/` | Upload resume & enter JD |
| `/result/<id>/` | Full ATS result page |
| `/career-path/<id>/` | Career roadmap page |
| `/admin-panel/` | Admin-only panel (requires admin role) |

---

## Features

1. **User Auth** — Register/login with role-based access (Admin, User, Guest)
2. **Resume Parsing** — PDF (PyPDF2), DOCX (python-docx), TXT, with Apache Tika fallback
3. **NER Extraction** — Name, email, phone, skills, education, experience, certifications
4. **Text Preprocessing** — Lowercase, stopword removal, lemmatization, tokenization
5. **Semantic Matching** — TF-IDF, Word2Vec, Sentence-BERT, BERT embeddings
6. **Ensemble ML** — Random Forest + Logistic Regression + SVM for final ATS score
7. **Skill Gap Analysis** — Missing skills with learning resources
8. **Career Path Generator** — Step-by-step roadmap, projects, certifications, time estimate
9. **Resume Ranking** — Sort candidates by ATS score
10. **Bias Mitigation** — Skill-based scoring, no name/gender bias
11. **Admin Panel** — View all users and rankings

---

## Troubleshooting

- **Tika errors**: Apache Tika requires Java. Install JDK 11+ from https://adoptium.net/
- **BERT slow on first run**: Models are downloaded from Hugging Face on first use (~400MB). Ensure internet access.
- **MongoDB connection error**: Make sure MongoDB service is running on port 27017.
- **Missing NLTK data**: Run `python -c "import nltk; nltk.download('all')"`
