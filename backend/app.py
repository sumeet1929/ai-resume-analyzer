from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import jwt
import datetime
import re
import pdfplumber
import PyPDF2
import pytesseract
from PIL import Image

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)
CORS(app)

SECRET_KEY = "super_secret_key_2026_resume_ai"


# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# ---------------- HOME ----------------
@app.route("/")
def home():
    return "AI Resume Analyzer Running"


# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (email,password) VALUES (?,?)",
        (email, password)
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        token = jwt.encode(
            {
                "email": email,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=5)
            },
            SECRET_KEY,
            algorithm="HS256"
        )

        return jsonify({
            "success": True,
            "token": token
        })

    return jsonify({"success": False})


# ---------------- PROFILE ----------------
@app.route("/profile")
def profile():
    token = request.headers.get("Authorization")

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({"email": data["email"]})
    except:
        return jsonify({"error": "Invalid token"}), 401


# ---------------- ANALYZE ----------------
@app.route("/analyze", methods=["POST"])
def analyze():

    file = request.files.get("resume")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    text = ""

    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
    except:
        pass

    if len(text.strip()) < 50:
        try:
            file.seek(0)
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        except:
            pass

    if len(text.strip()) < 50:
        try:
            file.seek(0)
            image = Image.open(file)
            text = pytesseract.image_to_string(image)
        except:
            pass

    if len(text.strip()) == 0:
        return jsonify({"error": "Unable to read resume"})

    text_lower = text.lower()

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    name = lines[0] if lines else "Candidate"

    experience = 0
    exp = re.findall(r'(\d+)\+?\s*(year|years)', text_lower)
    if exp:
        experience = max([int(x[0]) for x in exp])

    skills_db = [
        "python","java","javascript","react","node","flask","django",
        "aws","azure","gcp","docker","kubernetes","jenkins",
        "terraform","ansible","linux","git","devops",
        "sql","mysql","postgresql","mongodb",
        "html","css","bootstrap",
        "pandas","numpy","tensorflow","machine learning"
    ]

    found_skills = [s for s in skills_db if s in text_lower]

    education = "Not Found"

    if "b.tech" in text_lower or "btech" in text_lower:
        education = "B.Tech"
    elif "be " in text_lower:
        education = "B.E"
    elif "m.tech" in text_lower:
        education = "M.Tech"
    elif "bsc" in text_lower:
        education = "B.Sc"

    score = 30
    score += len(found_skills) * 4
    score += min(experience * 2, 20)

    if "project" in text_lower:
        score += 10

    if "github" in text_lower:
        score += 5

    score = min(score, 95)

    strengths = []

    if experience > 0:
        strengths.append("Has industry experience")

    if len(found_skills) >= 5:
        strengths.append("Strong technical skillset")

    if "project" in text_lower:
        strengths.append("Project experience")

    if not strengths:
        strengths.append("Basic technical foundation")

    recommendations = []

    if experience == 0:
        recommendations.append("Add internship or project experience")

    if len(found_skills) < 5:
        recommendations.append("Add more technical skills")

    if "github" not in text_lower:
        recommendations.append("Add GitHub profile")

    if "certification" not in text_lower:
        recommendations.append("Add certifications")

    tips = [
        "Add quantified achievements",
        "Add project descriptions",
        "Use action verbs",
        "Add LinkedIn profile",
        "Include skills section"
    ]

    summary = f"""
{name} is a {experience} years candidate with {education} background.
Key skills include {', '.join(found_skills[:5]) if found_skills else 'various technologies'}.
The resume shows strengths like {', '.join(strengths)}.
To improve ATS score, consider: {', '.join(recommendations[:2])}.
"""

    return jsonify({
        "name": name,
        "experience": f"{experience} years",
        "education": education,
        "skills": found_skills,
        "score": f"{score}%",
        "strengths": strengths,
        "recommendations": recommendations,
        "tips": tips,
        "summary": summary
    })


# ---------------- AI REWRITE ----------------
@app.route("/rewrite", methods=["POST"])
def rewrite():

    data = request.json

    skills = ", ".join(data.get("skills", []))
    experience = data.get("experience", "0 years")

    summary = f"""
Results-driven professional with {experience}.
Strong experience in {skills}.
Proven ability to design scalable systems, deliver projects,
and collaborate with cross-functional teams.

Demonstrates strong analytical thinking,
problem solving skills and technical expertise.
"""

    return jsonify({
        "summary": summary
    })


# ---------------- LINKEDIN ----------------
@app.route("/linkedin", methods=["POST"])
def linkedin():

    data = request.json
    url = data.get("url")

    try:
        name = url.split("/")[-2].replace("-", " ").title()

        skills = [
            "Python","AWS","Docker",
            "React","Flask","SQL"
        ]

        summary = f"""
{name} is a professional with strong experience in
{", ".join(skills[:5])}.

Demonstrates ability to build scalable applications,
work with cloud infrastructure and deliver projects.
"""

        return jsonify({
            "name": name,
            "skills": skills,
            "summary": summary,
            "experience": "From LinkedIn profile",
            "education": "Not specified",
            "score": "78%",
            "strengths": [
                "Strong LinkedIn presence",
                "Technical skillset",
                "Cloud experience"
            ],
            "recommendations": [
                "Add project links",
                "Add certifications",
                "Add measurable achievements"
            ],
            "tips": [
                "Keep headline clear",
                "Add GitHub link",
                "Add portfolio",
                "Use keywords"
            ]
        })

    except:
        return jsonify({"error":"LinkedIn import failed"})


# ---------------- JOB MATCH ----------------
@app.route("/job-match", methods=["POST"])
def job_match():

    data = request.json

    resume_skills = [s.lower() for s in data.get("skills", [])]
    job_desc = data.get("job", "").lower()

    skills_db = [
        "python","java","react","node","flask","django",
        "aws","azure","gcp","docker","kubernetes",
        "jenkins","terraform","ansible",
        "sql","mongodb","mysql","postgresql",
        "linux","git","devops",
        "html","css","javascript",
        "machine learning","tensorflow"
    ]

    job_skills = [s for s in skills_db if s in job_desc]

    matched = [s for s in job_skills if s in resume_skills]
    missing = [s for s in job_skills if s not in resume_skills]

    if len(job_skills) == 0:
        score = 0
    else:
        score = int((len(matched) / len(job_skills)) * 100)

    suggestions = []

    if missing:
        suggestions.append("Add missing skills: " + ", ".join(missing[:5]))

    if score < 60:
        suggestions.append("Resume not optimized for this job")

    if score > 80:
        suggestions.append("Strong match for this role")

    return jsonify({
        "match": f"{score}%",
        "matched": matched,
        "missing": missing,
        "suggestions": suggestions
    })


if __name__ == "__main__":
    print("FLASK SERVER STARTED")
    app.run(host="0.0.0.0", port=5000, debug=True)