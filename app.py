from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import re

from PyPDF2 import PdfReader
from docx import Document


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------------------
# Home Page
# --------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------
# Check File Extension
# --------------------------------

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# --------------------------------
# Extract Text From PDF
# --------------------------------

def extract_pdf_text(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# --------------------------------
# Extract Text From DOCX
# --------------------------------

def extract_docx_text(file_path):

    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


# --------------------------------
# Extract Resume Text
# --------------------------------

def extract_text(file_path):

    extension = file_path.rsplit(".", 1)[1].lower()

    if extension == "pdf":
        return extract_pdf_text(file_path)

    elif extension == "docx":
        return extract_docx_text(file_path)

    return ""


# --------------------------------
# Skills Database
# --------------------------------

SKILLS = [
    "python",
    "java",
    "javascript",
    "html",
    "css",
    "flask",
    "django",
    "sql",
    "mysql",
    "mongodb",
    "git",
    "github",
    "react",
    "node.js",
    "machine learning",
    "artificial intelligence",
    "data analysis",
    "pandas",
    "numpy",
    "cybersecurity",
    "networking",
    "linux",
    "docker",
    "aws",
    "excel",
    "communication",
    "leadership",
    "problem solving"
]


# --------------------------------
# Extract Skills
# --------------------------------

def extract_skills(text):

    text = text.lower()

    found_skills = []

    for skill in SKILLS:

        if skill.lower() in text:

            found_skills.append(skill)

    return found_skills


# --------------------------------
# Extract Job Keywords
# --------------------------------

def extract_keywords(job_description):

    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z+#.-]{2,}\b",
        job_description.lower()
    )

    keywords = set()

    for word in words:

        if word in SKILLS:
            keywords.add(word)

    return list(keywords)


# --------------------------------
# Calculate Resume Score
# --------------------------------

def calculate_score(text, skills):

    score = 0

    text_lower = text.lower()

    # Skills
    score += min(len(skills) * 4, 40)

    # Contact information
    if re.search(r"\b[\w.-]+@[\w.-]+\.\w+\b", text_lower):
        score += 10

    # Education
    if any(word in text_lower for word in
           ["education", "bachelor", "master", "degree"]):
        score += 10

    # Experience
    if any(word in text_lower for word in
           ["experience", "internship", "work experience"]):
        score += 15

    # Projects
    if "project" in text_lower or "projects" in text_lower:
        score += 10

    # Resume length/content
    if len(text.split()) >= 150:
        score += 15

    return min(score, 100)


# --------------------------------
# Recommendations
# --------------------------------

def generate_recommendations(
    text,
    skills,
    missing_skills
):

    recommendations = []

    text_lower = text.lower()

    if len(text.split()) < 150:
        recommendations.append(
            "Add more relevant details about your education, projects, and experience."
        )

    if not re.search(
        r"\b[\w.-]+@[\w.-]+\.\w+\b",
        text_lower
    ):
        recommendations.append(
            "Add a professional email address."
        )

    if not any(
        word in text_lower
        for word in ["project", "projects"]
    ):
        recommendations.append(
            "Add a projects section with your practical work."
        )

    if not any(
        word in text_lower
        for word in [
            "experience",
            "internship",
            "work experience"
        ]
    ):
        recommendations.append(
            "Add your internship or work experience."
        )

    if missing_skills:
        recommendations.append(
            "Consider adding relevant missing skills from the job description."
        )

    if not recommendations:
        recommendations.append(
            "Your resume has a good structure. Keep improving it with measurable achievements."
        )

    return recommendations


# --------------------------------
# Analyze Resume
# --------------------------------

@app.route("/analyze", methods=["POST"])
def analyze():

    if "resume" not in request.files:

        return jsonify({
            "error": "Please upload a resume."
        }), 400


    resume = request.files["resume"]

    if resume.filename == "":

        return jsonify({
            "error": "No file selected."
        }), 400


    if not allowed_file(resume.filename):

        return jsonify({
            "error": "Only PDF and DOCX files are allowed."
        }), 400


    filename = secure_filename(resume.filename)

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    resume.save(file_path)


    # Extract resume text

    text = extract_text(file_path)


    if not text.strip():

        return jsonify({
            "error": "Could not extract text from the resume."
        }), 400


    # Extract skills

    skills = extract_skills(text)


    # Job description

    job_description = request.form.get(
        "job_description",
        ""
    ).strip()


    job_keywords = extract_keywords(
        job_description
    )


    # Find missing skills

    missing_skills = [
        skill
        for skill in job_keywords
        if skill not in skills
    ]


    # Matching percentage

    if job_keywords:

        matched = [
            skill
            for skill in job_keywords
            if skill in skills
        ]

        match_percentage = round(
            (len(matched) / len(job_keywords)) * 100
        )

    else:

        matched = []

        match_percentage = 0


    # Resume score

    score = calculate_score(
        text,
        skills
    )


    # Recommendations

    recommendations = generate_recommendations(
        text,
        skills,
        missing_skills
    )


    # Delete uploaded file after analysis

    try:
        os.remove(file_path)
    except:
        pass


    return jsonify({

        "score": score,

        "skills": skills,

        "missing_skills": missing_skills,

        "matched_skills": matched,

        "match_percentage": match_percentage,

        "recommendations": recommendations

    })


# --------------------------------
# Run Application
# --------------------------------

if __name__ == "__main__":

    app.run(debug=True)
