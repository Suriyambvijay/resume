from flask import Flask, render_template, request, jsonify, redirect, url_for
import pdfplumber
import docx
import re
import sqlite3
import os
from datetime import datetime
import json

app = Flask(__name__)

# ==========================
# DATABASE SETUP
# ==========================

def get_db():
    conn = sqlite3.connect("resumes.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        skills TEXT,
        experience TEXT,
        education TEXT,
        summary TEXT,
        filename TEXT,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

init_db()

# ==========================
# RESUME TEXT EXTRACTION
# ==========================

def extract_text(file_path):
    """Extract text from PDF or DOCX files"""
    try:
        if file_path.endswith(".pdf"):
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text

        elif file_path.endswith(".docx"):
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        print(f"Error extracting text: {e}")
    return ""


def extract_email(text):
    """Extract email addresses from text"""
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return emails[0] if emails else ""


def extract_phone(text):
    """Extract phone numbers from text"""
    phones = re.findall(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}', text)
    return phones[0] if phones else ""


def extract_name(text):
    """Extract name from text (usually first line or top of document)"""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    # Filter out common headers and short lines
    for line in lines[:5]:
        if len(line) < 50 and len(line.split()) <= 4:
            # Check if line contains common name patterns
            if not any(keyword in line.lower() for keyword in ['email', 'phone', 'linkedin', 'github', 'address', 'objective', 'summary']):
                return line
    
    return "Unknown" if not lines else lines[0]


def extract_skills(text):
    """Extract skills section from resume"""
    skills_keywords = ['skills', 'competencies', 'technical skills', 'core competencies']
    
    text_lower = text.lower()
    for keyword in skills_keywords:
        if keyword in text_lower:
            # Find the section start
            start_idx = text_lower.find(keyword)
            # Get next 500 characters
            section = text[start_idx:start_idx + 500]
            
            # Look for skills (words followed by commas or bullets)
            skills = re.findall(r'[•\-\*]\s*([A-Za-z\+\#\.]+)', section)
            if skills:
                return ', '.join(skills[:10])
    
    return ""


def extract_experience(text):
    """Extract work experience from resume"""
    exp_keywords = ['experience', 'professional experience', 'work experience', 'employment']
    
    text_lower = text.lower()
    for keyword in exp_keywords:
        if keyword in text_lower:
            start_idx = text_lower.find(keyword)
            section = text[start_idx:start_idx + 800]
            
            # Extract job titles (usually all caps or title case followed by dates)
            job_titles = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:\(|\||–|—|\d)', section)
            if job_titles:
                return ', '.join(job_titles[:3])
    
    return ""


def extract_education(text):
    """Extract education information from resume"""
    education_keywords = ['education', 'academic', 'degree', 'university', 'college', 'school']
    
    text_lower = text.lower()
    for keyword in education_keywords:
        if keyword in text_lower:
            start_idx = text_lower.find(keyword)
            section = text[start_idx:start_idx + 500]
            
            # Look for degree patterns
            degrees = re.findall(r'((?:Bachelor|Master|PhD|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?)[^,\n]*)', section)
            if degrees:
                return ', '.join(degrees[:2])
    
    return ""


def extract_summary(text):
    """Extract professional summary from resume"""
    summary_keywords = ['summary', 'objective', 'professional summary', 'about']
    
    text_lower = text.lower()
    for keyword in summary_keywords:
        if keyword in text_lower:
            start_idx = text_lower.find(keyword)
            section = text[start_idx:start_idx + 300]
            
            # Extract sentences
            sentences = re.split(r'[.!?\n]', section)
            if len(sentences) > 1:
                summary = sentences[1].strip()
                if len(summary) > 20:
                    return summary[:200]
    
    return ""


def parse_resume(file_path):
    """Parse resume and extract all relevant information"""
    text = extract_text(file_path)
    
    if not text:
        return None
    
    data = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "education": extract_education(text),
        "summary": extract_summary(text)
    }
    
    return data


# ==========================
# DATABASE OPERATIONS
# ==========================

def save_candidate(data, filename):
    """Save candidate data to database"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO candidates
        (name, email, phone, skills, experience, education, summary, filename)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name", "Unknown"),
        data.get("email", ""),
        data.get("phone", ""),
        data.get("skills", ""),
        data.get("experience", ""),
        data.get("education", ""),
        data.get("summary", ""),
        filename
    ))
    
    conn.commit()
    candidate_id = cursor.lastrowid
    conn.close()
    
    return candidate_id


def get_all_candidates():
    """Get all candidates from database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates ORDER BY upload_date DESC")
    candidates = cursor.fetchall()
    conn.close()
    return candidates


def search_candidates(keyword):
    """Search candidates by keyword"""
    conn = get_db()
    cursor = conn.cursor()
    
    search_term = f"%{keyword}%"
    cursor.execute("""
        SELECT * FROM candidates
        WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? 
              OR skills LIKE ? OR experience LIKE ? OR education LIKE ?
        ORDER BY upload_date DESC
    """, (search_term, search_term, search_term, search_term, search_term, search_term))
    
    candidates = cursor.fetchall()
    conn.close()
    return candidates


def get_candidate(candidate_id):
    """Get specific candidate by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    candidate = cursor.fetchone()
    conn.close()
    return candidate


def delete_candidate(candidate_id):
    """Delete candidate from database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()


# ==========================
# ROUTES
# ==========================

@app.route("/", methods=["GET", "POST"])
def index():
    """Home page - upload and display resumes"""
    data = None
    error = None
    
    candidates = get_all_candidates()
    
    if request.method == "POST":
        if "resume" in request.files:
            file = request.files["resume"]
            
            if file.filename != "":
                try:
                    filename = "uploaded_" + str(datetime.now().timestamp()) + "_" + file.filename
                    file.save(filename)
                    
                    # Parse resume
                    resume_data = parse_resume(filename)
                    
                    if resume_data:
                        # Save to database
                        candidate_id = save_candidate(resume_data, filename)
                        data = resume_data
                        
                        # Refresh candidates list
                        candidates = get_all_candidates()
                    else:
                        error = "Could not extract text from the resume file."
                        
                except Exception as e:
                    error = f"Error processing file: {str(e)}"
    
    return render_template(
        "index.html",
        data=data,
        candidates=candidates,
        error=error
    )


@app.route("/search", methods=["POST"])
def search():
    """Search candidates"""
    keyword = request.form.get("keyword", "")
    candidates = []
    
    if keyword:
        candidates = search_candidates(keyword)
    else:
        candidates = get_all_candidates()
    
    return render_template(
        "index.html",
        candidates=candidates,
        search_keyword=keyword
    )


@app.route("/candidate/<int:candidate_id>")
def view_candidate(candidate_id):
    """View detailed candidate information"""
    candidate = get_candidate(candidate_id)
    
    if not candidate:
        return redirect(url_for("index"))
    
    # Convert Row to dict for easier template access
    candidate_dict = dict(candidate)
    
    return render_template(
        "candidate_detail.html",
        candidate=candidate_dict
    )


@app.route("/delete/<int:candidate_id>", methods=["POST"])
def delete(candidate_id):
    """Delete candidate"""
    try:
        candidate = get_candidate(candidate_id)
        if candidate and candidate["filename"]:
            # Delete uploaded file
            if os.path.exists(candidate["filename"]):
                os.remove(candidate["filename"])
        
        # Delete from database
        delete_candidate(candidate_id)
    except Exception as e:
        print(f"Error deleting candidate: {e}")
    
    return redirect(url_for("index"))


@app.route("/api/candidates")
def api_candidates():
    """API endpoint to get all candidates as JSON"""
    candidates = get_all_candidates()
    candidates_list = [
        {
            "id": c["id"],
            "name": c["name"],
            "email": c["email"],
            "phone": c["phone"],
            "skills": c["skills"],
            "upload_date": c["upload_date"]
        }
        for c in candidates
    ]
    return jsonify(candidates_list)


@app.route("/api/search/<keyword>")
def api_search(keyword):
    """API endpoint to search candidates"""
    candidates = search_candidates(keyword)
    candidates_list = [
        {
            "id": c["id"],
            "name": c["name"],
            "email": c["email"],
            "phone": c["phone"],
            "skills": c["skills"],
            "upload_date": c["upload_date"]
        }
        for c in candidates
    ]
    return jsonify(candidates_list)


# ==========================
# MAIN
# ==========================

if __name__ == "__main__":
    app.run(debug=True)
