import re


def extract_text_from_pdf(file_path: str) -> str:
    """Extract plain text from a PDF resume."""
    try:
        import PyPDF2
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""


def extract_text_from_docx(file_path: str) -> str:
    """Extract plain text from a DOCX resume."""
    try:
        from docx import Document
        doc = Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs)
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return ""


def calculate_ats_score(resume_text: str, skills_required: str, requirements: str) -> float:
    """
    ATS scoring algorithm — mirrors how real ATS systems work.

    Scoring breakdown:
      60%  — Skill keyword match (most important)
      25%  — Requirements keyword coverage
      15%  — Resume structure quality (experience, education sections, years)

    Returns a float between 0.0 and 100.0
    """
    resume_lower = resume_text.lower()

    # ── Skills matching (60 points) ──────────────────────────────────────────
    required_skills = [s.strip().lower() for s in skills_required.split(",") if s.strip()]
    skills_score = 0.0
    if required_skills:
        matched = sum(1 for skill in required_skills if skill in resume_lower)
        skills_score = (matched / len(required_skills)) * 60

    # ── Requirements keyword coverage (25 points) ────────────────────────────
    req_words = re.findall(r"\b[a-zA-Z]{4,}\b", requirements.lower())
    # Remove common stop words
    stop_words = {"that", "this", "with", "have", "will", "from", "they", "been", "your", "more", "also"}
    req_keywords = list(set(w for w in req_words if w not in stop_words))
    req_score = 0.0
    if req_keywords:
        matched_req = sum(1 for kw in req_keywords if kw in resume_lower)
        # Cap at 100% of a reasonable threshold (30% keyword match = full score)
        req_score = min((matched_req / max(len(req_keywords) * 0.3, 1)) * 25, 25)

    # ── Resume structure quality (15 points) ─────────────────────────────────
    structure_score = 0.0
    # Has major sections
    if any(kw in resume_lower for kw in ["experience", "work history", "employment"]):
        structure_score += 5
    if any(kw in resume_lower for kw in ["education", "university", "degree", "bachelor", "master"]):
        structure_score += 4
    if any(kw in resume_lower for kw in ["skills", "technologies", "tools"]):
        structure_score += 3
    # Has achievement-oriented language
    if any(kw in resume_lower for kw in ["achieved", "developed", "built", "led", "managed", "improved", "increased"]):
        structure_score += 2
    # Has years (indicates dated experience entries)
    if re.search(r"\b(19|20)\d{2}\b", resume_text):
        structure_score += 1

    total = skills_score + req_score + structure_score
    return min(round(total, 1), 100.0)


def parse_resume_and_score(file_path: str, skills_required: str, requirements: str) -> float:
    """Entry point: extract text then score against the job."""
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        return 0.0

    if not text.strip():
        return 0.0

    return calculate_ats_score(text, skills_required, requirements)