from openpyxl import load_workbook
import streamlit as st
import pdfplumber
from docx import Document
from typing import List, Dict,Any
import json
import requests
import os
import re
from reportlab.lib.pagesizes import A4
from pathlib import Path
import base64
import requests




API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
API_KEY = "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"

url = API_URL
    
headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
# TO EXTRACT DATA FROM THE UPLOADED FILE#

import requests, json, streamlit as st
from typing import Dict, Any


@st.cache_data
def get_base64_of_file(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_image_as_bg(image_file):
    # Get file extension to set correct MIME type
    ext = os.path.splitext(image_file)[1].lower()
    if ext == ".png":
        mime_type = "image/png"
    elif ext == ".jpg" or ext == ".jpeg":
        mime_type = "image/jpeg"
    else:
        st.error("Unsupported file type!")
        return

    bin_str = get_base64_of_file(image_file)
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:{mime_type};base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)



def extract_details_from_text(extracted_text: str) -> Dict[str, Any]:
    """
    Extract structured details from resume text and return as Python dictionary.
    Captures all standard fields and any additional fields present in the resume.
    """
    
    prompt = f"""
    Extract structured information from the following text and return it in JSON format only.
    
    Include all fields you can detect, even if they are not listed below. 
    Standard fields to include (if present):
    - name, email, phone, skills, experience, education, certifications, summary, projects
    For experience:
        - title, company, duration, description (array of strings), overview
    For projects:
        - name, description (array of strings), overview
    Include any other sections present (interests, languages, hobbies, awards, etc.)
    
    Text to analyze:
    {extracted_text}
    
    Return only valid JSON.
    """

    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {"role": "system", "content": "You are an expert at extracting structured information from resumes. Return JSON with all fields present, even if custom or unusual."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 4000
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        response_text = result['choices'][0]['message']['content']

        # Extract JSON
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start == -1 or json_end <= json_start:
            st.error("Could not find valid JSON in response")
            return {}

        data = json.loads(response_text[json_start:json_end])

        # Convert experience and project descriptions to lists
        for exp in data.get("experience", []):
            if isinstance(exp.get("description"), str):
                exp["description"] = [line.strip() for line in exp["description"].split("\n") if line.strip()]
        for proj in data.get("projects", []):
            if isinstance(proj.get("description"), str):
                proj["description"] = [line.strip() for line in proj["description"].split("\n") if line.strip()]

        # Ensure skills, certifications, education are lists
        for key in ["skills", "certifications", "education"]:
            if key in data and not isinstance(data[key], list):
                data[key] = [data[key]]

        return data

    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return {}
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON response: {str(e)}")
        return {}
    except Exception as e:
        st.error(f"Error extracting details: {str(e)}")
        return {}


def call_llm(payload):
    response = requests.post(API_URL, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    llm_text = data['choices'][0]['message']['content']
    return llm_text


SKILL_CACHE_FILE = "../ask.ai/json/skill.json"

@st.cache_data(show_spinner=False)
def get_all_skills_from_llm():
    if os.path.exists(SKILL_CACHE_FILE):
        with open(SKILL_CACHE_FILE, "r") as f:
            return json.load(f)

    prompt = (
        "Provide a comprehensive list of skills commonly required across various job roles and industries, "
        "including technical, soft, and domain-specific skills. "
        "Return only a JSON array of skill names without any categories, explanations, or extra text."
    )

    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {"role": "system", "content": "You are a skill extraction expert. Return a clean JSON array."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 3000
    }

    llm_response = call_llm(payload)

    try:
        skills_list = json.loads(llm_response)
    except json.JSONDecodeError:
        cleaned_text = re.sub(r'[0-9]+\w*', '', llm_response) 
        skills_list = [
            skill.strip().strip('"') for skill in re.split(r'[\n,•*-]+', cleaned_text) if skill.strip()
        ]

    clean_skills = []
    for skill in skills_list:
        skill = skill.strip().strip('"').strip()
        if skill.lower().startswith("category"):
            continue
        if re.search(r'\(e\.g\.?$', skill.lower()):
            continue
        if skill:
            clean_skills.append(skill.title())

    unique_skills = sorted(set(clean_skills))

    with open(SKILL_CACHE_FILE, "w") as f:
        json.dump(unique_skills, f, indent=2)

    return unique_skills



# ALL THE JOB ROLE LIST#


CACHE_FILE = "../ask.ai/json/job_roles.json"

def get_all_roles_from_llm():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    prompt = (
    "You are a global expert in careers. Provide an exhaustive list of job roles "
    "across all industries worldwide. Include detailed job roles from major fields like "
    "software development, software testing, hardware engineering, IT infrastructure, networking, "
    "cybersecurity, manufacturing, healthcare, finance, marketing, and more. "
    "List entry-level, mid-level, senior, and specialized roles such as 'Software Tester', "
    "'Automation Tester', 'Hardware Design Engineer', 'Firmware Developer', 'Network Administrator', "
    "'Security Analyst', and all variations in these fields. "
    "Return only a JSON array of job role names without extra text."
)


    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {"role": "system", "content": "You are a global expert in careers worldwide."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 3500
    }

    llm_response = call_llm(payload)

    try:
        roles_list = json.loads(llm_response)
        roles = sorted(set(role.strip().title() for role in roles_list if role.strip()))
    except json.JSONDecodeError:
        cleaned = llm_response.replace("[", "").replace("]", "").replace('"', "").replace("\n", "")
        roles = [role.strip().title() for role in cleaned.split(",") if role.strip()]
        roles = sorted(set(roles))

    with open(CACHE_FILE, "w") as f:
        json.dump(roles, f, indent=2)

    return roles






# exract excel column contents
def extract_skills_from_column(ws, example_col_index):
    all_skills = []
    seen = set()
    for row in ws.iter_rows(min_row=2):
        skill = row[example_col_index].value
        if skill and skill not in seen:
            seen.add(skill)
            all_skills.append(skill)
    return all_skills

# extract the excel file
@st.cache_data(show_spinner=False)
def load_excel_data(filename):
    wb = load_workbook(filename=filename)
    ws = wb.active
    header = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    return ws, header

# read the pdf file
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""
    
# read the document file
def extract_text_from_docx(docx_file):
    """Extract text from DOCX file"""
    try:
        doc = Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return ""
    

def extract_details_from_jd(job_description_text: str) -> dict:
    prompt = f"""
Extract structured information from the following job description. Return valid JSON only.

Extract these fields:
- job_title
- company
- location
- employment_type
- required_skills (list)
- responsibilities (list)
- qualifications (list)
- salary_range
- benefits (list)
- job_summary

Text to analyze:
{job_description_text}

Return only valid JSON format without any additional text.
"""

    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {"role": "system", "content": "You are an expert at extracting job description details. Always return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 2000
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    response_text = result['choices'][0]['message']['content']

    # Extract JSON substring
    json_start = response_text.find('{')
    json_end = response_text.rfind('}') + 1
    if json_start != -1 and json_end > json_start:
        json_text = response_text[json_start:json_end]
        jd_structured = json.loads(json_text)
        return jd_structured
    else:
        raise ValueError("Valid JSON not found in LLM response")



def lower_set(arr: List[str]) -> set:
    return set([s.lower().strip() for s in arr])

def highlight_missing_items(source: List[str], required: List[str]) -> List[str]:
    source_set = lower_set(source)
    required_set = lower_set(required)
    missing = required_set - source_set
    return list(missing)

def enhance_resume_with_jd_skills(resume_skills: List[str], jd_skills: List[str]) -> List[str]:
    updated = resume_skills.copy()
    resume_lower = lower_set(updated)
    for skill in jd_skills:
        if skill.lower().strip() not in resume_lower:
            updated.append(skill)
    return updated



def rewrite_resume_for_job(resume_data: dict, jd_data: dict) -> dict:
    """
    Rewrite the candidate's resume content to align with the job description.
    Emphasizes skills, achievements, experience, and projects in an ATS-friendly way.
    """
    rewritten_resume = resume_data.copy()

    # --- 1. Separate education and certifications ---
    education_all = resume_data.get("education", [])
    education_list, certification_list = [], []

    for item in education_all:
        if any(k in item for k in ["duration", "gpa", "degree"]):
            education_list.append(item)
        elif any(k in item for k in ["issuer", "name"]):
            certification_list.append(item)
        else:
            education_list.append(item)

   
    cert_data = resume_data.get("certifications", [])
    if isinstance(cert_data, list):
        certification_list.extend(cert_data)

    rewritten_resume["education"] = education_list
    rewritten_resume["certifications"] = certification_list

   
    candidate_skills = resume_data.get("skills", [])
    if isinstance(candidate_skills, list) and candidate_skills:
        if isinstance(candidate_skills[0], dict):
            flat_skills = []
            for group in candidate_skills:
                if isinstance(group, dict):
                    for vals in group.values():
                        if isinstance(vals, list):
                            flat_skills.extend([str(v) for v in vals if v])
            candidate_skills = flat_skills
        else:
            candidate_skills = [str(s) for s in candidate_skills if s]
    else:
        candidate_skills = []

    # --- 3. Prepare experience and project data ---
    experience = resume_data.get("experience", [])
    projects = resume_data.get("projects", [])

    all_exp_desc = []
    for exp in experience:
        desc = exp.get("description", [])
        if isinstance(desc, str):
            desc = [line.strip() for line in desc.split("\n") if line.strip()]
        all_exp_desc.extend(desc if isinstance(desc, list) else [])

    # --- 4. Collect job info ---
    job_title = jd_data.get("job_title", "")
    job_summary = jd_data.get("job_summary", "")
    responsibilities = jd_data.get("responsibilities", [])
    required_skills = jd_data.get("required_skills", [])

    responsibilities = [str(r) for r in responsibilities if r] if isinstance(responsibilities, list) else []
    required_skills = [str(s) for s in required_skills if s] if isinstance(required_skills, list) else []

    # --- 5. Rewrite professional summary ---
    summary_prompt = f"""
    You are an expert career coach. Rewrite a professional summary for {resume_data.get('name','')}
    applying for a {job_title} position at {jd_data.get('company','')}.
    Highlight relevant skills, achievements, and experience. Use the candidate's original summary:
    {resume_data.get('summary','')} and experience highlights: {all_exp_desc[:10]}
    Consider the job requirements: {', '.join(required_skills)}
    Return 2-3 sentence polished ATS-friendly summary only.
    with out description
    """
    rewritten_resume["summary"] = call_llm_api(summary_prompt, 200)
    rewritten_resume["job_title"] = job_title

    # --- 6. Rewrite experience ---
    if experience:
        exp_prompt = f"""
        Rewrite the candidate's experience for a {job_title} role at {jd_data.get('company','')}.
        Include measurable achievements, relevant keywords, and ATS-friendly formatting.
        Maintain JSON structure: description (array of strings), overview.
        Original Experience: {json.dumps(experience)}
        Responsibilities: {', '.join(responsibilities)}
        Required Skills: {', '.join(required_skills)}
        Return ONLY valid JSON array.
        """
        rewritten_exp_text = call_llm_api(exp_prompt, 500)
        try:
            json_start = rewritten_exp_text.find('[')
            json_end = rewritten_exp_text.rfind(']') + 1
            rewritten_experience = json.loads(rewritten_exp_text[json_start:json_end])
            for exp in rewritten_experience:
                desc = exp.get("description", [])
                if not desc or (isinstance(desc, list) and not any(line.strip() for line in desc)):
                    position = exp.get("position", "Professional")
                    company = exp.get("company", "A Company")
                    placeholder_desc = generate_basic_description(position, company, candidate_skills, call_llm_api)
                    exp["description"] = placeholder_desc
                    desc = placeholder_desc
                if isinstance(desc, str):
                    exp["description"] = [line.strip() for line in desc.split("\n") if line.strip()]
            rewritten_resume["experience"] = rewritten_experience
        except:
            rewritten_resume["experience"] = experience

    # --- 7. Rewrite projects ---
    if projects:
        proj_prompt = f"""
        Rewrite the candidate's project descriptions for a {job_title} role.
        Highlight achievements and relevant skills, keep JSON: name, description (array of strings), overview.
        Original Projects: {json.dumps(projects)}
        Responsibilities: {', '.join(responsibilities)}
        Required Skills: {', '.join(required_skills)}
        Return ONLY valid JSON array.
        """
        rewritten_proj_text = call_llm_api(proj_prompt, 400)
        try:
            json_start = rewritten_proj_text.find('[')
            json_end = rewritten_proj_text.rfind(']') + 1
            rewritten_projects = json.loads(rewritten_proj_text[json_start:json_end])
            for proj in rewritten_projects:
                desc = proj.get("description", [])
                if isinstance(desc, str):
                    proj["description"] = [line.strip() for line in desc.split("\n") if line.strip()]
            rewritten_resume["projects"] = rewritten_projects
        except:
            rewritten_resume["projects"] = projects

    # --- 8. Categorize and align skills ---
    skills_prompt = f"""
    Analyze and categorize the candidate's skills for a {job_title} role.
    Merge existing skills with required skills. Categorize into:
    technicalSkills, tools, cloudSkills, softSkills, languages.
    Candidate Skills: {', '.join(candidate_skills[:30])}
    Required Skills: {', '.join(required_skills)}
    Return ONLY a JSON object with above categories.
    """
    skills_text = call_llm_api(skills_prompt, 300)
    try:
        json_start = skills_text.find('{')
        json_end = skills_text.rfind('}') + 1
        parsed_skills = json.loads(skills_text[json_start:json_end])
        categorized_skills = {k: parsed_skills.get(k, []) for k in 
                              ["technicalSkills","tools","cloudSkills","softSkills","languages"]}
        rewritten_resume["skills"] = {k: v for k,v in categorized_skills.items() if v}
    except:
        rewritten_resume["skills"] = candidate_skills

    return rewritten_resume


def generate_basic_description(position: str, company: str, candidate_skills: list, call_llm_api) -> str:
    key_skills = candidate_skills[:5]
    prompt = f"""
    You are a resume filler AI. Generate a single, short paragraph (2-3 sentences maximum) 
    describing the general responsibilities for a '{position}' role at '{company}'. 
    
    The description MUST incorporate these key skills: {', '.join(key_skills)}. 
    
    Start with an action verb and provide a summary of work done. Do not include bullet points.
    Return ONLY the paragraph.
    """
    return call_llm_api(prompt, 100)

# --- Helper function for LLM API ---
def call_llm_api(prompt: str, max_tokens: int = 200) -> str:
    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {"role": "system", "content": "You are an expert AI assistant for resume optimization and job matching."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": max_tokens
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    return result['choices'][0]['message']['content']





def analyze_and_improve_resume(resume_data: Dict[str, Any], job_description: str = "") -> Dict[str, Any]:
    """
    Automatically improve resume content with better grammar, stronger action verbs,
    and professional formatting while preserving all information, using an external API.
    """
    

    resume_text = json.dumps(resume_data, indent=2)
    
    # The prompt now includes the job_description for context
    prompt = f"""
    Improve the following resume while maintaining all factual information and structure.
    
    Make these improvements:
    1. Fix all grammar, spelling, and punctuation errors
    2. Replace weak verbs with strong action verbs (Led, Spearheaded, Optimized, etc.)
    3. Ensure consistent tense (past for previous jobs, present for current)
    4. Improve clarity and impact of descriptions
    5. Ensure professional tone throughout
    6. Make descriptions more concise and impactful
    7. Ensure consistent formatting (dates, capitalization, etc.)
    
    **Job Description for Context (if available):**
    {job_description or "N/A"}
    
    IMPORTANT:
    - Keep the exact same JSON structure
    - Do NOT remove or add any sections
    - Do NOT change facts, dates, or company names
    - Only improve the language and presentation
    
    Resume Data:
    {resume_text}

    Return the improved resume in the EXACT SAME JSON structure, with only the text content improved.
    Return only valid JSON.
    """

    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {"role": "system", "content": "You are an expert resume writer who improves content while preserving structure and facts. Return improved resume in exact same JSON format."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 5000
    }

    try:
        # Perform API call
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # NOTE: Assumes the Llama model response structure wraps the content
        response_text = result['choices'][0]['message']['content']

        # Extract JSON (robustly handle text wrapping)
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start == -1 or json_end <= json_start:
            st.error("Could not find valid JSON in improved resume response")
            return resume_data

        improved_data = json.loads(response_text[json_start:json_end])
        st.success("🤖 Content successfully refined and improved using Llama API.")
        return improved_data

    except requests.exceptions.RequestException as e:
        # Crucial: Check API config and network connectivity
        st.error(f"External API request failed: {str(e)}. Check your `url` and `headers` config.")
        return resume_data
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON response: {str(e)}. Using original data.")
        return resume_data
    except KeyError as e:
        st.error(f"Unexpected response structure from external API. Missing key: {str(e)}. Using original data.")
        return resume_data
    except Exception as e:
        st.error(f"Error improving resume: {str(e)}. Using original data.")
        return resume_data



def check_specific_section(section_name: str, section_data: Any) -> Dict[str, Any]:
    """
    Check a specific section for grammar, clarity, and professional quality.
    Useful for real-time checking as user edits.
    """
    
    section_text = json.dumps({section_name: section_data}, indent=2)
    
    prompt = f"""
    Review this resume section for quality and provide quick feedback.
    
    Check for:
    - Grammar and spelling errors
    - Clarity and professionalism
    - Strong action verbs
    - Consistency
    
    Section:
    {section_text}

    Return feedback in JSON format:
    {{
        "has_issues": true/false,
        "issues": ["list of specific issues found"],
        "suggestions": ["list of improvement suggestions"],
        "quality_score": <number 0-10>
    }}

    Return only valid JSON.
    """

    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {"role": "system", "content": "You are a resume quality checker. Provide concise, actionable feedback."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1000
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        response_text = result['choices'][0]['message']['content']

        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start == -1 or json_end <= json_start:
            return {"has_issues": False, "issues": [], "suggestions": [], "quality_score": 5}

        feedback = json.loads(response_text[json_start:json_end])
        return feedback

    except Exception as e:
        return {"has_issues": False, "issues": [], "suggestions": [], "quality_score": 5}



def rewrite_resume_for_job_manual(resume_data: dict, jd_data: dict) -> dict:

    """
    Rewrite the candidate's resume content to align with the job description.
    Emphasizes skills, achievements, experience, and projects in an ATS-friendly way.
    """
    # del st.session_state['enhanced_resume']
    rewritten_resume = resume_data.copy()

    # -------------------- Education and Certifications --------------------
    education_all = resume_data.get("education", [])
    education_list, certification_list = [], []

    for item in education_all:
        if any(k in item for k in ["duration", "gpa", "degree", "course", "university"]):
            education_list.append(item)
        elif any(k in item for k in ["issuer", "name", "provider_name", "certificate_name"]):
            certification_list.append(item)
        else:
            education_list.append(item)

    cert_data = resume_data.get("certificate", [])
    if isinstance(cert_data, list):
        certification_list.extend(cert_data)

    rewritten_resume["education"] = education_list
    rewritten_resume["certifications"] = certification_list

    # -------------------- Flatten Candidate Skills --------------------
    candidate_skills = resume_data.get("skills", [])
    if isinstance(candidate_skills, list) and candidate_skills:
        if isinstance(candidate_skills[0], dict):
            flat_skills = []
            for group in candidate_skills:
                if isinstance(group, dict):
                    for vals in group.values():
                        if isinstance(vals, list):
                            flat_skills.extend([str(v) for v in vals if v])
            candidate_skills = flat_skills
        else:
            candidate_skills = [str(s) for s in candidate_skills if s]
    else:
        candidate_skills = []

    # -------------------- Job Info --------------------
    job_title = jd_data.get("job_title", "")
    responsibilities = jd_data.get("responsibilities", [])
    required_skills = jd_data.get("required_skills", [])

    rewritten_resume["job_title"] = job_title
    responsibilities = [str(r) for r in responsibilities if r] if isinstance(responsibilities, list) else []
    required_skills = [str(s) for s in required_skills if s] if isinstance(required_skills, list) else []

# -------------------- Normalize experience data --------------------
    experience_all = []

    if "experience" in resume_data and isinstance(resume_data["experience"], list):
        experience_all.extend(resume_data["experience"])

    if "professional_experience" in resume_data and isinstance(resume_data["professional_experience"], list):
        experience_all.extend(resume_data["professional_experience"])

    # Remove the old keys from rewritten_resume
    rewritten_resume.pop("experience", None)
    rewritten_resume.pop("professional_experience", None)
    rewritten_resume.pop("input_method", None)  # optional, if not needed

# Remove duplicates based on company + position
    seen = set()
    merged_experience = []
    for exp in experience_all:
        key = (exp.get("company", ""), exp.get("position", ""))
        if key not in seen:
            merged_experience.append(exp)
            seen.add(key)

    # Assign merged experience
    rewritten_resume["experience"] = merged_experience
    rewritten_resume["total_experience_count"] = len(merged_experience)


    # Remove old keys
    resume_data.pop("experience", None)
    resume_data.pop("professional_experience", None)
    # resume_data.pop("input_method", None)  # Remove if not needed

    # Remove duplicates based on company + position
    seen = set()
    merged_experience = []
    for exp in experience_all:
        key = (exp.get("company", ""), exp.get("position", ""))
        if key not in seen:
            merged_experience.append(exp)
            seen.add(key)

    # -------------------- Generate Experience Descriptions --------------------
    rewritten_experience = []
    all_exp_desc = []

    for exp in merged_experience:
        position = exp.get("position", "Professional")
        company = exp.get("company", "A Company")
        start_date = exp.get("start_date", "")
        end_date = exp.get("end_date", "")
        exp_skills = exp.get("exp_skills", [])

        exp_prompt = f"""
        You are an expert career coach. Rewrite the professional experience for {resume_data.get('name','')}
        for a {position} position at {company}, from {start_date} to {end_date}.
        Include relevant skills naturally, achievements, and responsibilities in a human-readable way.
        Mention the candidate's skills implicitly in the description: {', '.join(exp_skills)}
        Consider the job requirements: {', '.join(required_skills)}
        Return ONLY a JSON array with one object: {{"description": ["sentence1", "sentence2", ...]}}
        """

        rewritten_exp_text = call_llm_api(exp_prompt, 500)

        try:
            json_start = rewritten_exp_text.find('[')
            json_end = rewritten_exp_text.rfind(']') + 1
            rewritten_exp_list = json.loads(rewritten_exp_text[json_start:json_end])
            rewritten_exp_obj = rewritten_exp_list[0] if rewritten_exp_list else {}
            desc = rewritten_exp_obj.get("description", [])
            if isinstance(desc, str):
                desc = [line.strip() for line in desc.split("\n") if line.strip()]

            new_exp = {
                "company": company,
                "position": position,
                "start_date": start_date,
                "end_date": end_date,
                "description": desc if desc else [f"Worked as a {position} at {company}."]
            }
            rewritten_experience.append(new_exp)
            all_exp_desc.extend(desc)

        except Exception:
            fallback_desc = [f"Worked as a {position} at {company}, utilizing skills: {', '.join(exp_skills)}."]
            new_exp = {
                "company": company,
                "position": position,
                "start_date": start_date,
                "end_date": end_date,
                "description": fallback_desc
            }
            rewritten_experience.append(new_exp)
            all_exp_desc.extend(fallback_desc)

    # Finalize experience
    rewritten_resume["experience"] = rewritten_experience
    rewritten_resume["total_experience_count"] = len(rewritten_experience)

    # -------------------- Generate Professional Summary --------------------
    summary_prompt = f"""
    You are an expert career coach. Rewrite a professional summary for {resume_data.get('name','')}
    applying for a {job_title} position at {jd_data.get('company','')}.
    Highlight relevant skills, achievements, and experience. Use the candidate's original summary:
    {resume_data.get('summary','')} and experience highlights: {all_exp_desc[:10]}
    Consider the job requirements: {', '.join(required_skills)}
    Return 2-3 sentence polished ATS-friendly summary only.
    """
    rewritten_resume["summary"] = call_llm_api(summary_prompt, 200)

    # -------------------- Generate Project Descriptions --------------------
    if "project" in resume_data:
        projects = resume_data.get("project", [])
        rewritten_projects = []

        for proj in projects:
            project_name = proj.get("projectname", proj.get("name", "Project"))
            tools_used = proj.get("tools", [])
            original_desc = proj.get("description", proj.get("decription", ""))

            proj_prompt = f"""
            You are an expert career coach. Rewrite this project description for a {job_title} role:
            Project Name: {project_name}
            Original Description: {original_desc}
            Tools used: {', '.join(tools_used)}
            Highlight achievements, responsibilities, and relevant skills in a human-readable way.
            Do NOT include the tools as a separate field in JSON, but mention them naturally in the description.
            Return ONLY a JSON array with one object:
            {{
                "name": "{project_name}",
                "description": ["sentence1", "sentence2", ...],
                "overview": ""
            }}
            """

            rewritten_proj_text = call_llm_api(proj_prompt, 300)

            try:
                json_start = rewritten_proj_text.find('[')
                json_end = rewritten_proj_text.rfind(']') + 1
                parsed_proj = json.loads(rewritten_proj_text[json_start:json_end])

                proj_obj = parsed_proj[0] if parsed_proj else {}
                desc = proj_obj.get("description", [])
                if isinstance(desc, str):
                    proj_obj["description"] = [line.strip() for line in desc.split("\n") if line.strip()]

                proj_obj["name"] = project_name
                proj_obj["overview"] = proj_obj.get("overview", "")
                rewritten_projects.append(proj_obj)

            except:
                fallback_desc = (
                    [line.strip() for line in original_desc.split("\n") if line.strip()]
                    if isinstance(original_desc, str)
                    else [f"Worked on {project_name} using {', '.join(tools_used)}."]
                )
                rewritten_projects.append({
                    "name": project_name,
                    "description": fallback_desc,
                    "overview": ""
                })

        rewritten_resume["projects"] = rewritten_projects

    # -------------------- Categorize Skills --------------------
    skills_prompt = f"""
    Analyze and categorize the candidate's skills for a {job_title} role.
    Merge existing skills with required skills. Categorize into:
    technicalSkills, tools, cloudSkills, softSkills, languages.
    Candidate Skills: {', '.join(candidate_skills[:30])}
    Required Skills: {', '.join(required_skills)}
    Return ONLY a JSON object with above categories.
    """
    skills_text = call_llm_api(skills_prompt, 300)
    try:
        json_start = skills_text.find('{')
        json_end = skills_text.rfind('}') + 1
        parsed_skills = json.loads(skills_text[json_start:json_end])
        categorized_skills = {k: parsed_skills.get(k, []) for k in 
                              ["technicalSkills","tools","cloudSkills","softSkills","languages"]}
        rewritten_resume["skills"] = {k: v for k,v in categorized_skills.items() if v}
    except:
        rewritten_resume["skills"] = candidate_skills

    # ✅ --- Final Cleanup: Remove old singular keys ---
    if "project" in rewritten_resume and "projects" in rewritten_resume:
        del rewritten_resume["project"]

    if "certificate" in rewritten_resume and "certifications" in rewritten_resume:
        del rewritten_resume["certificate"]

    rewritten_resume["projects"] = rewritten_resume.get("projects", [])
    rewritten_resume["certifications"] = rewritten_resume.get("certifications", [])

    return rewritten_resume


def save_user_resume(email, resume_data, input_method=None):
    """Save or update a user's resume without affecting other users"""
    user_data_file = Path(__file__).parent.parent / "user_resume_data.json"

    # Convert date objects to strings
    def convert_dates(obj):
        if isinstance(obj, dict):
            return {k: convert_dates(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_dates(item) for item in obj]
        elif hasattr(obj, 'isoformat'):  # date/datetime
            return obj.isoformat()
        return obj

    resume_data = convert_dates(resume_data)

    # ✅ Inject input_method into resume data
    if input_method:
        resume_data["input_method"] = input_method

    # Load existing data
    try:
        if user_data_file.exists():
            with open(user_data_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
        else:
            all_data = {}
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        all_data = {}

    # Update only this user
    all_data[email] = resume_data

    # Save back
    try:
        with open(user_data_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving resume data: {e}")
        return False