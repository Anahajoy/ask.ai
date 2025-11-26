from openpyxl import load_workbook
import streamlit as st
import pdfplumber
from docx import Document
from typing import List, Dict,Any
import json
import requests
import os
import io
from reportlab.lib.pagesizes import A4
from pathlib import Path
import base64
import requests
from difflib import SequenceMatcher
import re
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pptx import Presentation
from pptx.util import Pt
from docx import Document
from docx.shared import RGBColor
from collections import Counter
import hashlib
from copy import deepcopy
import time
import base64
from io import BytesIO
from datetime import datetime




API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
API_KEY = "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"

url = API_URL
    
headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
# TO EXTRACT DATA FROM THE UPLOADED FILE#

TEMPLATES_DIR = "uploaded_templates.json"
users_file = Path(__file__).parent / "users.json"
user_data_file = Path(__file__).parent/"user_resume_data.json"


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



@st.cache_data(show_spinner=False)
def load_skills_from_json():
    # """Load skills from the cached JSON file"""
    # get_all_skills_from_llm()
    try:
        if os.path.exists(SKILL_CACHE_FILE):
            with open(SKILL_CACHE_FILE, "r") as f:
                return json.load(f)
        else:
            # If file doesn't exist, generate it
            return get_all_skills_from_llm()
    except Exception as e:
        st.error(f"Error loading skills: {e}")
        # Fallback to basic skills if there's an error
        return ["Python", "JavaScript", "SQL", "Cloud Computing", "Project Management", "Data Analysis"]


SKILL_CACHE_FILE = "../ask.ai/json/skill.json"

@st.cache_data(show_spinner=False)
def get_all_skills_from_llm():
    if os.path.exists(SKILL_CACHE_FILE):
        with open(SKILL_CACHE_FILE, "r") as f:
            return json.load(f)

    all_skills = set()
    
    # Define multiple focused prompts to get comprehensive coverage
    prompt_categories = [
        {
            "category": "Manual Labor & Service",
            "prompt": """List 200+ specific skills for: cleaning staff, janitors, dishwashers, laborers, warehouse workers, 
            packers, stock clerks, maintenance workers, landscapers, groundskeepers, movers, delivery personnel, 
            sanitation workers, custodians, housekeepers, laundry workers, kitchen helpers."""
        },
        {
            "category": "Agriculture & Farming",
            "prompt": """List 200+ specific skills for: farmers, farm workers, crop managers, livestock handlers, 
            agricultural technicians, irrigation specialists, harvesters, dairy workers, poultry workers, 
            farm equipment operators, greenhouse workers, vineyard workers, aquaculture workers, agronomists."""
        },
        {
            "category": "Transportation & Logistics",
            "prompt": """List 200+ specific skills for: truck drivers, taxi drivers, bus drivers, delivery drivers, 
            forklift operators, crane operators, pilots, ship captains, train conductors, dispatchers, 
            logistics coordinators, supply chain managers, freight handlers, route planners, fleet managers."""
        },
        {
            "category": "Construction & Trades",
            "prompt": """List 200+ specific skills for: carpenters, electricians, plumbers, welders, masons, 
            HVAC technicians, roofers, painters, drywall installers, tile setters, glaziers, insulators, 
            heavy equipment operators, pipefitters, ironworkers, sheet metal workers, construction managers."""
        },
        {
            "category": "Food Service & Hospitality",
            "prompt": """List 200+ specific skills for: chefs, cooks, bakers, bartenders, servers, baristas, 
            food prep workers, line cooks, pastry chefs, sous chefs, catering managers, restaurant managers, 
            hotel managers, front desk agents, concierges, housekeeping managers, event coordinators."""
        },
        {
            "category": "Retail & Sales",
            "prompt": """List 200+ specific skills for: retail associates, cashiers, sales representatives, 
            merchandisers, store managers, buyers, inventory specialists, loss prevention, visual merchandisers, 
            account executives, business development, inside sales, outside sales, territory managers."""
        },
        {
            "category": "Healthcare & Medical",
            "prompt": """List 200+ specific skills for: nurses, doctors, surgeons, medical assistants, 
            paramedics, EMTs, pharmacists, pharmacy technicians, radiologists, lab technicians, 
            phlebotomists, dental assistants, physical therapists, occupational therapists, medical coders."""
        },
        {
            "category": "Education & Training",
            "prompt": """List 200+ specific skills for: teachers, professors, tutors, instructional designers, 
            training specialists, curriculum developers, education administrators, school counselors, 
            librarians, teaching assistants, special education teachers, ESL teachers, corporate trainers."""
        },
        {
            "category": "Manufacturing & Production",
            "prompt": """List 200+ specific skills for: machine operators, production workers, assemblers, 
            quality inspectors, manufacturing engineers, production supervisors, CNC operators, fabricators, 
            industrial maintenance, production planners, process engineers, lean specialists, Six Sigma experts."""
        },
        {
            "category": "IT & Software Development",
            "prompt": """List 300+ specific technical skills including: programming languages (Python, Java, C++, C#, 
            JavaScript, TypeScript, Ruby, Go, Rust, PHP, Swift, Kotlin, R, MATLAB, Scala, etc.), frameworks 
            (React, Angular, Vue, Django, Flask, Spring, .NET, Node.js, Express, Laravel, etc.), databases, 
            cloud platforms, DevOps tools, version control, testing frameworks, APIs, microservices."""
        },
        {
            "category": "Cybersecurity & Network",
            "prompt": """List 200+ specific skills for: security analysts, penetration testers, ethical hackers, 
            security engineers, network administrators, firewall specialists, SIEM analysts, SOC analysts, 
            malware analysts, cryptographers, compliance officers, risk assessors, incident responders."""
        },
        {
            "category": "Data Science & Analytics",
            "prompt": """List 200+ specific skills including: data analysis tools, statistical methods, 
            machine learning algorithms, deep learning, NLP, computer vision, big data technologies (Hadoop, Spark), 
            visualization tools (Tableau, Power BI, Looker), SQL variants, Python libraries (pandas, numpy, scikit-learn), 
            R packages, data modeling, ETL processes, data warehousing."""
        },
        {
            "category": "Business & Finance",
            "prompt": """List 200+ specific skills for: accountants, bookkeepers, financial analysts, auditors, 
            tax professionals, investment bankers, wealth managers, controllers, CFOs, budget analysts, 
            credit analysts, financial planners, actuaries, payroll specialists, accounts payable/receivable."""
        },
        {
            "category": "Marketing & Advertising",
            "prompt": """List 200+ specific skills including: SEO, SEM, PPC, social media platforms (Facebook Ads, 
            Google Ads, LinkedIn Ads, TikTok Ads), email marketing, content marketing, copywriting, brand management, 
            market research, analytics tools (Google Analytics, Adobe Analytics), CRM systems, marketing automation, 
            growth hacking, influencer marketing, affiliate marketing, video marketing."""
        },
        {
            "category": "Creative & Design",
            "prompt": """List 200+ specific skills including: Adobe Creative Suite (Photoshop, Illustrator, InDesign, 
            After Effects, Premiere Pro), Figma, Sketch, UI/UX design, graphic design, web design, motion graphics, 
            3D modeling (Blender, Maya, 3ds Max), video editing, photography, illustration, typography, 
            color theory, wireframing, prototyping."""
        },
        {
            "category": "Engineering",
            "prompt": """List 200+ specific skills for: mechanical engineers, electrical engineers, civil engineers, 
            chemical engineers, aerospace engineers, industrial engineers, environmental engineers, software engineers, 
            systems engineers, including CAD tools (AutoCAD, SolidWorks, CATIA, Revit), simulation software, 
            technical drawing, project engineering, quality engineering."""
        },
        {
            "category": "Legal & Compliance",
            "prompt": """List 150+ specific skills for: lawyers, paralegals, legal assistants, compliance officers, 
            contract managers, legal researchers, court reporters, mediators, arbitrators, patent attorneys, 
            corporate counsel, litigation specialists, regulatory experts, legal technology."""
        },
        {
            "category": "HR & Recruitment",
            "prompt": """List 150+ specific skills for: HR managers, recruiters, talent acquisition, HR generalists, 
            compensation specialists, benefits administrators, HR analytics, HRIS systems (Workday, SAP SuccessFactors, 
            Oracle HCM), employee relations, performance management, training coordinators, organizational development."""
        },
        {
            "category": "Executive & Leadership",
            "prompt": """List 200+ specific skills for: CEOs, COOs, CFOs, CIOs, CTOs, VPs, directors, senior managers 
            including: strategic planning, business strategy, P&L management, M&A, stakeholder management, 
            corporate governance, change management, executive communication, board relations, investor relations, 
            crisis management, succession planning, organizational design."""
        },
        {
            "category": "Soft Skills & General",
            "prompt": """List 200+ specific soft skills and general competencies including: communication types 
            (verbal, written, presentation, public speaking, negotiation), leadership styles, emotional intelligence, 
            problem-solving approaches, critical thinking, creativity, adaptability, time management, organization, 
            collaboration, conflict resolution, decision-making, customer service, active listening."""
        }
    ]
    
    print("🔄 Generating comprehensive skill database across all sectors...")
    
    for idx, category_data in enumerate(prompt_categories, 1):
        print(f"📊 Processing category {idx}/{len(prompt_categories)}: {category_data['category']}")
        
        full_prompt = f"""{category_data['prompt']}

Return ONLY a JSON array of individual skill names. Be very specific and comprehensive. 
Include technical skills, tools, software, methodologies, certifications, and specific abilities.
No categories, no explanations, no numbering - just skill names."""

        payload = {
            "model": "meta/llama-3.1-70b-instruct",
            "messages": [
                {"role": "system", "content": "You are a skill taxonomy expert. Return a comprehensive JSON array of specific, actionable skill names."},
                {"role": "user", "content": full_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 8000
        }

        try:
            llm_response = call_llm(payload)
            
            try:
                skills_list = json.loads(llm_response)
            except json.JSONDecodeError:
                # Robust extraction
                cleaned_text = re.sub(r'[0-9]+\.?\s*', '', llm_response)
                cleaned_text = re.sub(r'```json|```', '', cleaned_text)
                skills_list = [
                    skill.strip().strip('"').strip("'").strip(',').strip('[]') 
                    for skill in re.split(r'[\n,•*-]+', cleaned_text) 
                    if skill.strip()
                ]
            
            # Clean and add skills
            excluded_keywords = ["category", "skills:", "example", "e.g.", "etc.", "including", "such as"]
            
            for skill in skills_list:
                skill = skill.strip().strip('"').strip("'").strip(',').strip()
                
                # Skip if contains excluded keywords
                if any(keyword in skill.lower() for keyword in excluded_keywords):
                    continue
                
                # Skip very short or very long entries
                if len(skill) < 2 or len(skill) > 70:
                    continue
                
                # Skip entries with parentheses at the end
                if re.search(r'\([^)]*$', skill):
                    continue
                
                # Skip entries that look like descriptions
                if skill.count(' ') > 6:
                    continue
                
                if skill:
                    all_skills.add(skill.title())
            
            print(f"   ✅ Added skills. Total so far: {len(all_skills)}")
            
        except Exception as e:
            print(f"   ⚠️ Error in category {category_data['category']}: {e}")
            continue
    
    # Add comprehensive baseline skills to ensure coverage
    baseline_skills = [
        # Manual & Service
        "Cleaning", "Janitorial Work", "Floor Cleaning", "Window Cleaning", "Carpet Cleaning",
        "Dishwashing", "Laundry", "Ironing", "Mopping", "Vacuuming", "Sweeping", "Dusting",
        "Waste Management", "Recycling", "Sanitation", "Disinfection", "Pest Control",
        
        # Agriculture
        "Farming", "Crop Management", "Livestock Care", "Tractor Operation", "Harvesting",
        "Planting", "Irrigation", "Soil Testing", "Fertilization", "Crop Rotation",
        "Animal Husbandry", "Dairy Farming", "Poultry Farming", "Beekeeping", "Composting",
        
        # Transportation
        "Driving", "Truck Driving", "Bus Driving", "Taxi Driving", "Forklift Operation",
        "CDL License", "Vehicle Maintenance", "Route Planning", "GPS Navigation", "Loading",
        "Unloading", "Delivery", "Dispatch", "Logistics", "Fleet Management",
        
        # Construction
        "Carpentry", "Plumbing", "Electrical Work", "Welding", "Masonry", "HVAC",
        "Roofing", "Painting", "Drywall", "Tiling", "Flooring", "Concrete Work",
        "Blueprint Reading", "Framing", "Demolition", "Scaffolding",
        
        # Food Service
        "Cooking", "Baking", "Food Preparation", "Food Safety", "Menu Planning",
        "Knife Skills", "Grilling", "Frying", "Sautéing", "Plating", "Bartending",
        "Coffee Making", "Food Handling", "Kitchen Management", "Recipe Development",
        
        # Retail
        "Customer Service", "Cash Handling", "POS Systems", "Inventory Management",
        "Merchandising", "Sales", "Upselling", "Stock Replenishment", "Loss Prevention",
        "Visual Merchandising", "Product Knowledge", "Returns Processing",
        
        # Healthcare
        "Patient Care", "First Aid", "CPR", "BLS", "ACLS", "Vital Signs",
        "Medical Terminology", "Phlebotomy", "IV Insertion", "Wound Care",
        "Medication Administration", "EMR Systems", "HIPAA Compliance",
        
        # IT & Programming
        "Python", "Java", "JavaScript", "C++", "C#", "PHP", "Ruby", "Go", "Rust",
        "TypeScript", "Swift", "Kotlin", "R", "MATLAB", "SQL", "HTML", "CSS",
        "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring Boot",
        "Git", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux", "Windows Server",
        
        # Data & Analytics
        "Data Analysis", "Excel", "Power BI", "Tableau", "SQL", "Python", "R",
        "Statistics", "Data Visualization", "ETL", "Data Modeling", "Machine Learning",
        "Deep Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn",
        
        # Cybersecurity
        "Network Security", "Penetration Testing", "Ethical Hacking", "Firewall Management",
        "SIEM", "IDS/IPS", "Vulnerability Assessment", "Security Auditing", "Cryptography",
        "Incident Response", "Malware Analysis", "Security Compliance",
        
        # Business & Finance
        "Accounting", "Bookkeeping", "Financial Analysis", "Budgeting", "Forecasting",
        "Tax Preparation", "Auditing", "QuickBooks", "SAP", "Oracle Financials",
        "Financial Modeling", "Excel VBA", "Financial Reporting", "AP/AR",
        
        # Marketing
        "SEO", "SEM", "PPC", "Google Ads", "Facebook Ads", "Social Media Marketing",
        "Content Marketing", "Email Marketing", "Copywriting", "Google Analytics",
        "Marketing Automation", "CRM", "Salesforce", "HubSpot", "Mailchimp",
        
        # Design
        "Graphic Design", "UI/UX Design", "Adobe Photoshop", "Adobe Illustrator",
        "Figma", "Sketch", "InDesign", "After Effects", "Premiere Pro", "Video Editing",
        "Photography", "Photo Editing", "Web Design", "Mobile Design", "Wireframing",
        
        # Soft Skills
        "Communication", "Leadership", "Teamwork", "Problem Solving", "Critical Thinking",
        "Time Management", "Organization", "Adaptability", "Creativity", "Collaboration",
        "Negotiation", "Conflict Resolution", "Decision Making", "Public Speaking",
        "Presentation Skills", "Active Listening", "Emotional Intelligence", "Work Ethic",
        "Attention to Detail", "Multitasking", "Stress Management", "Customer Focus",
        
        # Project Management
        "Project Management", "Agile", "Scrum", "Kanban", "Waterfall", "JIRA", "Asana",
        "MS Project", "Risk Management", "Stakeholder Management", "Resource Planning",
        "PMP", "PRINCE2", "Change Management",
        
        # Engineering
        "AutoCAD", "SolidWorks", "CATIA", "Revit", "MATLAB", "Simulink", "ANSYS",
        "CAD", "CAM", "FEA", "CFD", "Technical Drawing", "GD&T", "Quality Control",
        
        # Executive
        "Strategic Planning", "Business Strategy", "P&L Management", "M&A",
        "Corporate Governance", "Stakeholder Management", "Board Relations",
        "Executive Leadership", "Change Management", "Business Development"
    ]
    
    # Add all baseline skills
    all_skills.update([skill.title() for skill in baseline_skills])
    
    # Convert to sorted list
    unique_skills = sorted(list(all_skills))
    
    # Save to cache
    os.makedirs(os.path.dirname(SKILL_CACHE_FILE), exist_ok=True)
    with open(SKILL_CACHE_FILE, "w") as f:
        json.dump(unique_skills, f, indent=2)

    print(f"\n✅ Generated {len(unique_skills)} unique skills covering all job sectors and levels!")
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
    
import docx2txt

def extract_text_from_docx(docx_file):
    try:
        text = docx2txt.process(docx_file)
        return text.strip()
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return ""
""
    

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
    Enhance the existing candidate resume using the JD,
    but DO NOT add new fake roles, skills, or projects that
    are not present in user's resume. Only highlight and optimize.
    """
    rewritten_resume = resume_data.copy()
    rewritten_resume.pop("input_method", None)

    # --- 1. Separate education and certifications (unchanged) ---
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

    # --- 2. Normalize candidate skills (unchanged logic) ---
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

    # --- 3. Experience + Projects (unchanged) ---
    experience = resume_data.get("experience", [])
    projects = resume_data.get("projects", [])

    all_exp_desc = []
    for exp in experience:
        desc = exp.get("description", [])
        if isinstance(desc, str):
            desc = [line.strip() for line in desc.split("\n") if line.strip()]
        all_exp_desc.extend(desc if isinstance(desc, list) else [])

    # --- 4. JD extraction (unchanged) ---
    job_title = jd_data.get("job_title", "")
    job_summary = jd_data.get("job_summary", "")
    responsibilities = jd_data.get("responsibilities", [])
    required_skills = jd_data.get("required_skills", [])

    responsibilities = [str(r) for r in responsibilities if r] if isinstance(responsibilities, list) else []
    required_skills = [str(s) for s in required_skills if s] if isinstance(required_skills, list) else []

    # ==========================================================
    # 🚀 UPDATED PROMPT -> SUMMARY: Highlight only existing skills
    # ==========================================================
    summary_prompt = f"""
Act as a professional resume writer and produce a polished professional summary
for {resume_data.get('name','')} applying for {job_title} at {jd_data.get('company','')}.

RULES (STRICT):
- Mention ONLY skills and experience that ALREADY exist in the user's resume.
- Do NOT invent or assume any new roles, skills, tools, achievements, metrics, or claims.
- Make it aligned with the job by emphasizing only matching elements that truly exist.
- Keep it factual, concise, ATS-friendly, and written in implied first person (no "I", "my", "me").

Use ONLY this content:
- Original summary: {resume_data.get('summary','')}
- Experience points: {all_exp_desc[:10]}
- Skills to highlight ONLY if they exist in resume: {', '.join(required_skills)}

Length: 2–3 sentences maximum.

⚠️ Return ONLY the final professional summary text.
⚠️ Do NOT include titles, labels, comments, explanations, headers, or extra lines.
"""

    rewritten_resume["summary"] = call_llm_api(summary_prompt, 200)
    rewritten_resume["job_title"] = job_title

    # ==========================================================
    # 🚀 UPDATED PROMPT -> EXPERIENCE: No creation, only highlight
    # ==========================================================
    if experience:
        exp_prompt = f"""
        Rewrite the candidate's experience to better align with {job_title} at {jd_data.get('company','')}.

        RULES (VERY IMPORTANT):
        - Do NOT create fake tasks, tools, achievements, or metrics.
        - Only rephrase and highlight what ALREADY exists.
        - If skills match the JD, highlight them clearly.
        - Keep structure the same: JSON with 'position', 'company', 'duration', 'overview', and 'description' (bullet list).

        Original Experience JSON: {json.dumps(experience)}
        JD Responsibilities: {', '.join(responsibilities)}
        Matching Skills to Highlight Only if Present: {', '.join(required_skills)}

        Return ONLY the cleaned JSON array.
        """
        rewritten_exp_text = call_llm_api(exp_prompt, 500)
        try:
            json_start = rewritten_exp_text.find('[')
            json_end = rewritten_exp_text.rfind(']') + 1
            rewritten_experience = json.loads(rewritten_exp_text[json_start:json_end])
            rewritten_resume["experience"] = rewritten_experience
        except:
            rewritten_resume["experience"] = experience

    # ==========================================================
    # 🚀 UPDATED PROMPT -> PROJECTS: Only enhance existing ones
    # ==========================================================
    if projects:
        proj_prompt = f"""
        Rewrite the candidate's project descriptions to align with {job_title}.

        RULES:
        - Do NOT add new technologies, tools, responsibilities or outcomes.
        - Only rephrase and highlight relevant points that ALREADY exist.
        - Highlight only skills already present in project text.

        Original Projects JSON: {json.dumps(projects)}
        Skills to highlight only if they ALREADY exist: {', '.join(required_skills)}

        Return ONLY valid JSON array (same structure).
        """
        rewritten_proj_text = call_llm_api(proj_prompt, 400)
        try:
            json_start = rewritten_proj_text.find('[')
            json_end = rewritten_proj_text.rfind(']') + 1
            rewritten_resume["projects"] = json.loads(rewritten_proj_text[json_start:json_end])
        except:
            rewritten_resume["projects"] = projects

    # ==========================================================
    # 🚀 UPDATED PROMPT -> SKILLS: ONLY enhance, NO new skills
    # ==========================================================
    skills_prompt = f"""
    Categorize ONLY the candidate's existing skills to align with {job_title}.

    RULES:
    - DO NOT add new tools or skills that are NOT already in the resume.
    - If a skill matches the JD, place it at the TOP of its category.
    - Categorize ONLY the user's existing skills into:
      technicalSkills, tools, cloudSkills, softSkills, languages.

    USER SKILLS: {', '.join(candidate_skills[:30])}
    JD SKILLS to highlight only if they exist in USER skills: {', '.join(required_skills)}

    Return ONLY JSON object with the categories.
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

    # Try a few times if the server gives 500 or times out
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

        except requests.exceptions.Timeout:
            print(f"⏳ Timeout on attempt {attempt + 1}, retrying...")
            time.sleep(2 ** attempt)

        except requests.exceptions.HTTPError as e:
            if response.status_code >= 500:
                print(f"⚠️ Server error 500 on attempt {attempt + 1}, retrying...")
                time.sleep(2 ** attempt)
            else:
                # Show more details for debugging
                print("❌ Client error:", response.text)
                break

        except Exception as e:
            print("Unexpected error:", e)
            break

    return "⚠️ Sorry, the AI service is currently unavailable. Please try again later."





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
    Enhance the existing candidate resume using JD guidance,
    without adding any fake skills, tools, achievements or content
    that does not exist in the original resume.
    """
    rewritten_resume = resume_data.copy()
    rewritten_resume.pop("input_method", None)

    # -------------------- Education and Certifications (NO CHANGE) --------------------
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

    # -------------------- Flatten Candidate Skills (NO CHANGE) --------------------
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

    # -------------------- Job Info (NO CHANGE) --------------------
    job_title = jd_data.get("job_title", "")
    responsibilities = jd_data.get("responsibilities", [])
    required_skills = jd_data.get("required_skills", [])
    rewritten_resume["job_title"] = job_title

    responsibilities = [str(r) for r in responsibilities if r] if isinstance(responsibilities, list) else []
    required_skills = [str(s) for s in required_skills if s] if isinstance(required_skills, list) else []

    # -------------------- Merge Experience (NO CHANGE) --------------------
    experience_all = []
    if "experience" in resume_data and isinstance(resume_data["experience"], list):
        experience_all.extend(resume_data["experience"])
    if "professional_experience" in resume_data and isinstance(resume_data["professional_experience"], list):
        experience_all.extend(resume_data["professional_experience"])

    rewritten_resume.pop("experience", None)
    rewritten_resume.pop("professional_experience", None)
    rewritten_resume.pop("input_method", None)

    seen = set()
    merged_experience = []
    for exp in experience_all:
        key = (exp.get("company", ""), exp.get("position", ""))
        if key not in seen:
            merged_experience.append(exp)
            seen.add(key)

    rewritten_resume["experience"] = merged_experience
    rewritten_resume["total_experience_count"] = len(merged_experience)

    # -------------------- Generate Experience (UPDATED LOGIC) --------------------
    rewritten_experience = []
    all_exp_desc = []

    for exp in merged_experience:
        position = exp.get("position", "Professional")
        company = exp.get("company", "A Company")
        start_date = exp.get("start_date", "")
        end_date = exp.get("end_date", "")
        exp_skills = exp.get("exp_skills", [])

        exp_prompt = f"""
        You are a professional resume writer. Rewrite ONLY the existing content for this experience
        to align with the {job_title} role.

        STRICT RULES:
        - DO NOT add new tools, tasks, achievements, metrics or claims.
        - Use only the information already present in the role.
        - You may rephrase content and highlight relevancy using existing skills only.
        - Highlight only if a skill matches BOTH resume and JD.
        - Make description strong but 100% factual.

        USER ROLE: {position} at {company} ({start_date} to {end_date})
        USER EXISTING SKILLS: {', '.join(exp_skills)}
        JD SKILLS TO HIGHLIGHT ONLY IF THEY ALREADY EXIST ABOVE: {', '.join(required_skills)}

        Return ONLY JSON array with one object containing:
        {{"description": ["sentence1", "sentence2", ...]}}
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
            fallback_desc = [f"Worked as a {position} at {company}, using {', '.join(exp_skills)}."]
            new_exp = {
                "company": company,
                "position": position,
                "start_date": start_date,
                "end_date": end_date,
                "description": fallback_desc
            }
            rewritten_experience.append(new_exp)
            all_exp_desc.extend(fallback_desc)

    rewritten_resume["experience"] = rewritten_experience
    rewritten_resume["total_experience_count"] = len(rewritten_experience)

    # -------------------- Professional Summary (UPDATED LOGIC) --------------------
    summary_prompt = f"""
    Rewrite the professional summary for {resume_data.get('name','')} applying for {job_title}.

    STRICT RULES:
    - Do NOT invent new skills, tools, achievements or claims.
    - Only use what exists in resume & experience.
    - Highlight only skills that match both resume and JD.
    - Keep 100% factual but strongly aligned to the job.
    - Write in first person implied (no "I", "me", "my").

    USER SUMMARY: {resume_data.get('summary','')}
    EXPERIENCE POINTS: {all_exp_desc[:10]}
    JD SKILLS (highlight only if they exist in resume): {', '.join(required_skills)}

    Return ONLY the rewritten summary text. 
    Do NOT add titles, headers, labels, notes, explanations, quotes, or extra lines.
    """

    rewritten_resume["summary"] = call_llm_api(summary_prompt, 200)

    # -------------------- Projects (UPDATED LOGIC) --------------------
    if "project" in resume_data:
        projects = resume_data.get("project", [])
        rewritten_projects = []

        for proj in projects:
            project_name = proj.get("projectname", proj.get("name", "Project"))
            tools_used = proj.get("tools", [])
            original_desc = proj.get("description", proj.get("decription", ""))

            proj_prompt = f"""
            Rewrite this project description using ONLY the existing information provided.

            ALLOWED:
            - You may elaborate, expand, and improve clarity.
            - You may make the sentences more descriptive and professional.
            - You may highlight relevant responsibilities already present.
            - You may emphasize important parts using stronger wording.

            STRICT RULES:
            - Do NOT introduce or assume new technologies, tools, achievements, metrics, or responsibilities.
            - If a JD skill matches the project and ALREADY exists in the description or tools, highlight it naturally.
            - The final output must remain factual based only on given content.

            Project Name: {project_name}
            Original Description: {original_desc}
            Tools Already Used: {', '.join(tools_used)}
            JD Skills to highlight ONLY if already present: {', '.join(required_skills)}

            Return ONLY a JSON array in this exact structure:
            [{{ 
                "name": "{project_name}", 
                "description": ["sentence1", "sentence2", ...], 
                "overview": "" 
            }}]

            Do NOT include notes, labels, headers, comments, or explanations.
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

    # -------------------- Skill Categorization (UPDATED LOGIC) --------------------
    skills_prompt = f"""
    Categorize ONLY the candidate's EXISTING skills to align with {job_title}.

    STRICT RULES:
    - DO NOT add or assume any new skills.
    - If a skill matches the JD AND exists in user's list, move it to the top.
    - Categorize only, do not invent.

    USER SKILLS: {', '.join(candidate_skills[:30])}
    JD SKILLS to highlight ONLY if also in user skills: {', '.join(required_skills)}

    Return ONLY JSON with:
    technicalSkills, tools, cloudSkills, softSkills, languages
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

    # -------------------- Handle Custom Sections (NO CHANGE) --------------------
    standard_keys = {
        "name", "email", "phone", "location", "url", "summary", "job_title",
        "education", "experience", "skills", "projects", "certifications", 
        "achievements", "total_experience_count", "professional_experience",
        "certificate", "project", "input_method"
    }

    custom_sections = resume_data.get("custom_sections", {})
    if isinstance(custom_sections, dict):
        for title, description in custom_sections.items():
            clean_title = str(title).strip()
            clean_description = description.strip() if isinstance(description, str) else (
                "\n".join(map(str, description)) if isinstance(description, list) else str(description)
            )
            if clean_title and clean_title not in standard_keys:
                rewritten_resume[clean_title] = clean_description

    for key, value in resume_data.items():
        if key not in standard_keys and isinstance(value, str):
            rewritten_resume[key] = value.strip()

    if "project" in rewritten_resume and "projects" in rewritten_resume:
        del rewritten_resume["project"]
    if "certificate" in rewritten_resume and "certifications" in rewritten_resume:
        del rewritten_resume["certificate"]
    if "custom_sections" in rewritten_resume:
        del rewritten_resume["custom_sections"]

    rewritten_resume["projects"] = rewritten_resume.get("projects", [])
    rewritten_resume["certifications"] = rewritten_resume.get("certifications", [])

    return rewritten_resume


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    pattern = r'^\+?\d{7,15}$'
    return re.match(pattern, phone) is not None


def save_user_resume(email, resume_data, input_method=None):
    """Save or update a user's resume without affecting other users"""
    # user_data_file = "user_resume_data.json"

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
    
def get_user_template_path(user_email):
    """Return the JSON path for the given user's templates."""
    if not user_email:
        raise ValueError("❌ user_email is None — make sure the user is logged in before saving templates.")
    
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    safe_email = user_email.replace("@", "_at_").replace(".", "_dot_")
    return os.path.join(TEMPLATES_DIR, f"{safe_email}.json")





import base64

def get_user_ppt_template_path(user_email):
    """Get the file path for user's PPT templates."""
    return os.path.join("user_data", f"{user_email}_ppt_templates.json")

def load_user_templates(user_email):
    """Load templates from JSON file for the logged-in user."""
    path = get_user_template_path(user_email)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_templates(user_email, templates):
    """Save templates to JSON file for the logged-in user."""
    path = get_user_template_path(user_email)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(templates, f, indent=4, ensure_ascii=False)

def load_user_ppt_templates(user_email):
    """Load PowerPoint templates from JSON file for the logged-in user."""
    path = get_user_ppt_template_path(user_email)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            templates = json.load(f)
            # Convert base64 back to binary for ppt_data and convert lists back to sets
            for key in templates:
                if 'ppt_data' in templates[key]:
                    templates[key]['ppt_data'] = base64.b64decode(templates[key]['ppt_data'])
                # Convert lists back to sets
                if 'heading_shapes' in templates[key]:
                    templates[key]['heading_shapes'] = set(templates[key]['heading_shapes'])
                if 'basic_info_shapes' in templates[key]:
                    templates[key]['basic_info_shapes'] = set(templates[key]['basic_info_shapes'])
            return templates
    return {}

def save_user_ppt_templates(user_email, templates):
    """Save PowerPoint templates to JSON file for the logged-in user."""
    path = get_user_ppt_template_path(user_email)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Create a copy to avoid modifying the original
    templates_copy = {}
    for key, val in templates.items():
        templates_copy[key] = val.copy()
        # Convert binary ppt_data to base64 for JSON storage
        if 'ppt_data' in val and isinstance(val['ppt_data'], bytes):
            templates_copy[key]['ppt_data'] = base64.b64encode(val['ppt_data']).decode('utf-8')
        # Convert sets to lists for JSON serialization
        if 'heading_shapes' in val and isinstance(val['heading_shapes'], set):
            templates_copy[key]['heading_shapes'] = list(val['heading_shapes'])
        if 'basic_info_shapes' in val and isinstance(val['basic_info_shapes'], set):
            templates_copy[key]['basic_info_shapes'] = list(val['basic_info_shapes'])
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(templates_copy, f, indent=4, ensure_ascii=False)



def calculate_ats_score(resume_data, job_description):
    """
    Calculate ATS score based on keyword matching between resume and JD.
    Returns a score out of 100 and breakdown details.
    """
    if not job_description or not resume_data:
        return {"score": 0, "breakdown": {}, "missing_keywords": []}
    
    # FIXED: Handle job_description if it's a dict
    if isinstance(job_description, dict):
        jd_text = extract_jd_text(job_description)
    else:
        jd_text = job_description
    
    # Extract keywords from job description
    jd_keywords = extract_keywords(jd_text)
    
    # Extract all text from resume
    resume_text = extract_resume_text(resume_data)
    resume_keywords = extract_keywords(resume_text)
    
    # Calculate matching
    matched_keywords = jd_keywords.intersection(resume_keywords)
    match_percentage = (len(matched_keywords) / len(jd_keywords) * 100) if jd_keywords else 0
    
    # Calculate breakdown by sections
    breakdown = {
        "skills_match": calculate_skills_match(resume_data.get('skills', {}), jd_text),
        "experience_match": calculate_text_match(
            extract_section_text(resume_data.get('experience', [])), 
            jd_text
        ),
        "keyword_match": match_percentage
    }
    
    # Calculate overall score (weighted)
    overall_score = (
        breakdown["skills_match"] * 0.4 +
        breakdown["experience_match"] * 0.3 +
        breakdown["keyword_match"] * 0.3
    )
    
    # Find missing important keywords
    missing_keywords = list(jd_keywords - resume_keywords)[:10]  # Top 10 missing
    
    return {
        "score": round(overall_score, 1),
        "breakdown": breakdown,
        "matched_keywords": list(matched_keywords)[:15],
        "missing_keywords": missing_keywords
    }


def extract_jd_text(jd_dict):
    """Extract text from job description dictionary."""
    if not isinstance(jd_dict, dict):
        return str(jd_dict)
    
    text_parts = []
    
    # Common JD fields
    jd_fields = [
        'job_title', 'title', 'position', 
        'description', 'job_description',
        'responsibilities', 'requirements', 
        'qualifications', 'skills_required',
        'preferred_skills', 'experience_required',
        'summary', 'overview', 'about_role'
    ]
    
    # Extract text from all fields
    for field in jd_fields:
        if field in jd_dict:
            value = jd_dict[field]
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, list):
                text_parts.extend([str(item) for item in value])
    
    # If no specific fields found, extract all string values
    if not text_parts:
        for key, value in jd_dict.items():
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, list):
                text_parts.extend([str(item) for item in value if item])
    
    return ' '.join(text_parts)


def extract_keywords(text):
    """Extract meaningful keywords from text."""
    if not text:
        return set()
    
    # Ensure text is a string
    if not isinstance(text, str):
        text = str(text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and split into words
    words = re.findall(r'\b[a-z]{3,}\b', text)
    
    # Common stop words to exclude
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was',
        'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may',
        'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'she', 'use', 'way',
        'about', 'after', 'also', 'back', 'been', 'before', 'being', 'both', 'could',
        'each', 'from', 'have', 'here', 'into', 'just', 'like', 'more', 'most', 'only',
        'other', 'over', 'such', 'than', 'that', 'them', 'then', 'there', 'these',
        'they', 'this', 'through', 'time', 'very', 'were', 'what', 'when', 'where',
        'which', 'while', 'will', 'with', 'would', 'your', 'work', 'using', 'able'
    }
    
    # Filter out stop words and keep meaningful keywords
    keywords = {word for word in words if word not in stop_words and len(word) > 3}
    
    return keywords


def extract_resume_text(resume_data):
    """Extract all text content from resume data."""
    text_parts = []
    
    # Add summary
    if resume_data.get('summary'):
        text_parts.append(resume_data['summary'])
    
    # Add skills
    skills = resume_data.get('skills', {})
    for skill_list in skills.values():
        if isinstance(skill_list, list):
            text_parts.extend(skill_list)
    
    # Add experience
    for exp in resume_data.get('experience', []):
        if exp.get('position'):
            text_parts.append(exp['position'])
        if exp.get('title'):
            text_parts.append(exp['title'])
        if exp.get('description'):
            if isinstance(exp['description'], list):
                text_parts.extend(exp['description'])
            else:
                text_parts.append(str(exp['description']))
    
    # Add projects
    for proj in resume_data.get('projects', []):
        if proj.get('name'):
            text_parts.append(proj['name'])
        if proj.get('description'):
            if isinstance(proj['description'], list):
                text_parts.extend(proj['description'])
            else:
                text_parts.append(str(proj['description']))
    
    # Add education
    for edu in resume_data.get('education', []):
        if edu.get('degree'):
            text_parts.append(edu['degree'])
        if edu.get('course'):
            text_parts.append(edu['course'])
    
    # Add certifications
    for cert in resume_data.get('certifications', []):
        # Add certifications
        for cert in resume_data.get('certifications', []):
            if isinstance(cert, dict):
                # cert is a dictionary
                name = cert.get('certificate_name') or cert.get('name')
            else:
                # cert is a string
                name = cert
            
            if name:
                text_parts.append(name)

    
    return ' '.join([str(part) for part in text_parts])


def extract_section_text(section_list):
    """Extract text from a list section."""
    text_parts = []
    for item in section_list:
        if isinstance(item, dict):
            for value in item.values():
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, list):
                    text_parts.extend([str(v) for v in value])
    return ' '.join(text_parts)


def calculate_skills_match(resume_skills, job_description):
    """Calculate how many resume skills match the job description."""
    if not resume_skills or not job_description:
        return 0
    
    # Ensure job_description is a string
    if isinstance(job_description, dict):
        jd_text = extract_jd_text(job_description)
    else:
        jd_text = str(job_description)
    
    jd_lower = jd_text.lower()
    total_skills = 0
    matched_skills = 0
    
    for skill_category, skills_list in resume_skills.items():
        if isinstance(skills_list, list):
            for skill in skills_list:
                total_skills += 1
                if str(skill).lower() in jd_lower:
                    matched_skills += 1
    
    return (matched_skills / total_skills * 100) if total_skills > 0 else 0


def calculate_text_match(text, job_description):
    """Calculate keyword match percentage between text and JD."""
    if not text or not job_description:
        return 0
    
    # Ensure inputs are strings
    if isinstance(job_description, dict):
        jd_text = extract_jd_text(job_description)
    else:
        jd_text = str(job_description)
    
    text_keywords = extract_keywords(text)
    jd_keywords = extract_keywords(jd_text)
    
    if not jd_keywords:
        return 0
    
    matched = text_keywords.intersection(jd_keywords)
    return (len(matched) / len(jd_keywords) * 100)


def get_score_color(score):
    """Return color based on score."""
    if score >= 80:
        return "#00FF7F"  # Green
    elif score >= 60:
        return "#FFD700"  # Gold
    elif score >= 40:
        return "#FFA500"  # Orange
    else:
        return "#FF6347"  # Red


def get_score_label(score):
    """Return label based on score."""
    if score >= 80:
        return "Excellent Match"
    elif score >= 60:
        return "Good Match"
    elif score >= 40:
        return "Fair Match"
    else:
        return "Needs Improvement"
    

# --- Template CSS & HTML Generation Functions (Same as before) ---
def get_css_minimalist(color):
    return f"""
        <style>
        @page {{ margin: 0.3in; size: letter; }}
        body {{ margin: 0; padding: 0; }}
        .ats-page {{ 
            font-family: 'Arial', sans-serif; 
            font-size: 9pt; 
            color: #333; 
            max-width: 100%; 
            margin: 0; 
            padding: 0.3in;
            line-height: 1.2; 
        }}
        .ats-section-title {{ 
            font-size: 10.5pt; 
            font-weight: bold; 
            color: #000;
            border-bottom: 1px solid #333;
            padding-bottom: 1px;
            margin-top: 8px;
            margin-bottom: 3px;
        }}
        .ats-item-header {{ 
            margin-top: 2px; 
            margin-bottom: 0; 
            line-height: 1.1; 
            font-size: 9.5pt;
            display: flex;
            justify-content: space-between;
            align-items: flex-start; 
        }}
        .ats-item-title-group {{ 
            flex-grow: 1; 
            padding-right: 8px; 
        }}
        .ats-item-title {{ 
            font-weight: bold; 
            color: #000; 
            display: inline; 
        }} 
        .ats-item-subtitle {{ 
            font-style: italic; 
            color: #555; 
            display: inline; 
            font-size: 9pt;
        }}
        .ats-item-duration {{ 
            font-size: 9pt; 
            color: #666; 
            white-space: nowrap;
            flex-shrink: 0;
            text-align: right; 
        }}
        .ats-bullet-list {{ 
            list-style-type: disc; 
            margin-left: 18px; 
            padding-left: 0; 
            margin-top: 2px; 
            margin-bottom: 3px; 
        }}
        .ats-bullet-list li {{ 
            margin-bottom: 0px; 
            line-height: 1.2; 
        }}
        .ats-header {{ margin-bottom: 8px; }}
        .ats-header h1 {{ margin: 0; padding: 0; font-size: 16pt; }}
        .ats-job-title-header {{ font-size: 11pt; margin: 2px 0 5px 0; }}
        .ats-contact {{ font-size: 9pt; margin-top: 3px; }}
        .ats-skills-group {{ margin-bottom: 3px; }}
        p {{ margin: 5px 0; }}
        </style>
    """

def get_css_horizontal(color):
    return f"""
        <style>
        @page {{ margin: 0.3in; size: letter; }}
        body {{ margin: 0; padding: 0; }}
        .ats-page {{ 
            font-family: 'Times New Roman', serif; 
            font-size: 9.5pt; 
            color: #333; 
            max-width: 100%; 
            margin: 0; 
            padding: 0.3in;
            line-height: 1.15; 
        }}
        .ats-header {{ text-align: center; padding-bottom: 3px; margin-bottom: 8px; }}
        .ats-header h1 {{ color: #000; font-size: 16pt; margin: 0; text-transform: uppercase; }}
        .ats-job-title-header {{ font-size: 11pt; margin: 2px 0 5px 0; }}
        .ats-contact {{ font-size: 8.5pt; margin-top: 3px; }}
        .ats-contact span:not(:last-child)::after {{ content: " | "; white-space: pre; }}
        .ats-section-title {{ 
            color: {color}; 
            font-size: 10.5pt; 
            font-weight: bold; 
            text-transform: uppercase; 
            border-bottom: 2px solid {color}; 
            padding-bottom: 1px; 
            margin-top: 8px; 
            margin-bottom: 3px; 
        }}
        .ats-item-header {{ margin-top: 2px; margin-bottom: 1px; line-height: 1.1; display: flex; justify-content: space-between; }}
        .ats-item-title {{ font-weight: bold; color: #000; flex-grow: 1; }}
        .ats-item-duration {{ font-size: 9pt; white-space: nowrap; color: #666; }}
        .ats-item-subtitle {{ font-style: italic; color: #555; display: block; font-size: 9pt; }}
        .ats-bullet-list {{ list-style-type: circle; margin-left: 20px; padding-left: 0; margin-top: 2px; margin-bottom: 3px; }}
        .ats-bullet-list li {{ margin-bottom: 0px; line-height: 1.2; }}
        .ats-skills-group {{ margin-bottom: 3px; }}
        p {{ margin: 5px 0; }}
        </style>
    """

def get_css_bold_title(color):
    return f"""
        <style>
        @page {{ margin: 0.3in; size: letter; }}
        body {{ margin: 0; padding: 0; }}
        .ats-page {{ 
            font-family: 'Verdana', sans-serif; 
            font-size: 8.5pt; 
            color: #333; 
            max-width: 100%; 
            margin: 0; 
            padding: 0.3in;
            line-height: 1.2; 
        }}
        .ats-header {{ text-align: center; padding-bottom: 3px; margin-bottom: 8px; }}
        .ats-header h1 {{ color: {color}; font-size: 15pt; margin: 0; text-transform: uppercase; }}
        .ats-job-title-header {{ 
            font-size: 11pt; 
            color: #555; 
            margin: 2px 0 5px 0; 
            text-align: center;
        }}
        .ats-contact {{ font-size: 8pt; margin-top: 3px; }}
        .ats-contact span:not(:last-child)::after {{ content: " • "; white-space: pre; }}
        .ats-section-title {{ 
            color: #000; 
            font-size: 10pt; 
            font-weight: 900; 
            text-transform: uppercase; 
            margin-top: 8px; 
            margin-bottom: 3px; 
            border-bottom: 1.5px solid #CCC; 
        }}
        .ats-item-header {{ 
            margin-top: 2px; 
            margin-bottom: 0px; 
            line-height: 1.1;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}
        .ats-item-title-group {{
            flex-grow: 1;
            padding-right: 8px;
        }}
        .ats-item-title {{ font-weight: bold; color: {color}; display: inline; }}
        .ats-item-subtitle {{ font-style: italic; color: #555; display: inline; font-size: 8.5pt; }}
        .ats-item-duration {{ 
            font-size: 8pt; 
            color: #666;
            white-space: nowrap;
            flex-shrink: 0;
            text-align: right;
        }}
        .ats-bullet-list {{ list-style-type: square; margin-left: 18px; padding-left: 0; margin-top: 2px; margin-bottom: 3px; }}
        .ats-bullet-list li {{ margin-bottom: 0px; line-height: 1.2; }}
        .ats-skills-group {{ margin-bottom: 3px; }}
        p {{ margin: 5px 0; }}
        </style>
    """

def get_css_date_below(color):
    return f"""
        <style>
        @page {{ margin: 0.3in; size: letter; }}
        body {{ margin: 0; padding: 0; }}
        .ats-page {{ 
            font-family: 'Calibri', sans-serif; 
            font-size: 9pt; 
            color: #333; 
            max-width: 100%; 
            margin: 0; 
            padding: 0.3in;
            line-height: 1.2; 
        }}
        .ats-header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 3px; margin-bottom: 8px; }}
        .ats-header h1 {{ color: #000; font-size: 17pt; margin: 0; }}
        .ats-job-title-header {{ font-size: 11pt; margin: 2px 0 5px 0; }}
        .ats-contact {{ font-size: 8.5pt; margin-top: 3px; }}
        .ats-contact span:not(:last-child)::after {{ content: " | "; white-space: pre; }}
        .ats-section-title {{ 
            color: {color}; 
            font-size: 10.5pt; 
            font-weight: bold; 
            text-transform: uppercase; 
            letter-spacing: 0.5px; 
            margin-top: 8px; 
            margin-bottom: 3px; 
        }}
        .ats-item-header {{ margin-top: 2px; margin-bottom: 1px; line-height: 1.1; }}
        .ats-item-title {{ font-weight: bold; color: #000; display: inline-block; }}
        .ats-item-duration {{ font-size: 8.5pt; color: {color}; display: block; font-style: italic; margin-top: 1px; }}
        .ats-item-subtitle {{ font-style: italic; color: #555; display: inline-block; margin-left: 5px; font-size: 8.5pt; }}
        .ats-bullet-list {{ list-style-type: disc; margin-left: 18px; padding-left: 0; margin-top: 2px; margin-bottom: 3px; }}
        .ats-bullet-list li {{ margin-bottom: 0px; line-height: 1.2; }}
        .ats-skills-group {{ margin-bottom: 3px; }}
        p {{ margin: 5px 0; }}
        </style>
    """

def get_css_section_box(color):
    return f"""
        <style>
        @page {{ margin: 0.3in; size: letter; }}
        body {{ margin: 0; padding: 0; }}
        .ats-page {{ 
            font-family: 'Arial', sans-serif; 
            font-size: 9pt; 
            color: #333; 
            max-width: 100%; 
            margin: 0; 
            padding: 0.3in;
            line-height: 1.2; 
        }}
        .ats-header {{ text-align: center; padding-bottom: 3px; margin-bottom: 8px; }}
        .ats-header h1 {{ color: {color}; font-size: 16pt; margin: 0; text-transform: uppercase; }}
        .ats-job-title-header {{ font-size: 11pt; margin: 2px 0 5px 0; }}
        .ats-contact {{ font-size: 8.5pt; margin-top: 3px; }}
        .ats-contact span:not(:last-child)::after {{ content: " | "; white-space: pre; }}
        .ats-section-title {{ 
            background-color: {color}; 
            color: white; 
            font-size: 10pt; 
            font-weight: bold; 
            text-transform: uppercase; 
            padding: 2px 8px; 
            margin-top: 8px; 
            margin-bottom: 3px; 
        }}
        .ats-item-header {{ margin-top: 2px; margin-bottom: 1px; line-height: 1.1; display: flex; justify-content: space-between; }}
        .ats-item-title {{ font-weight: bold; color: #000; flex-grow: 1; }}
        .ats-item-duration {{ font-size: 8.5pt; white-space: nowrap; color: #666; }}
        .ats-item-subtitle {{ font-style: italic; color: #555; display: block; font-size: 8.5pt; }}
        .ats-bullet-list {{ list-style-type: disc; margin-left: 18px; padding-left: 0; margin-top: 2px; margin-bottom: 3px; }}
        .ats-bullet-list li {{ margin-bottom: 0px; line-height: 1.2; }}
        .ats-skills-group {{ margin-bottom: 3px; }}
        p {{ margin: 5px 0; }}
        </style>
    """

def get_css_classic(color):
    return f"""
        <style>
        @page {{ margin: 0.3in; size: letter; }}
        body {{ margin: 0; padding: 0; }}
        .ats-page {{ 
            font-family: 'Times New Roman', serif; 
            font-size: 10pt; 
            color: #000; 
            max-width: 100%; 
            margin: 0; 
            padding: 0.3in;
            line-height: 1.15; 
        }}
        .ats-header {{ text-align: center; padding-bottom: 3px; margin-bottom: 8px; }}
        .ats-header h1 {{ color: #000; font-size: 18pt; margin: 0; }}
        .ats-job-title-header {{ font-size: 11pt; margin: 2px 0 5px 0; }}
        .ats-contact {{ font-size: 9pt; margin-top: 3px; }}
        .ats-contact span:not(:last-child)::after {{ content: " | "; white-space: pre; }}
        .ats-section-title {{ 
            color: #000; 
            font-size: 10.5pt; 
            font-weight: bold; 
            text-transform: uppercase; 
            border-bottom: 1px solid #000; 
            padding-bottom: 1px; 
            margin-top: 8px; 
            margin-bottom: 3px; 
        }}
        .ats-item-header {{ margin-top: 2px; margin-bottom: 1px; line-height: 1.1; display: flex; justify-content: space-between; }}
        .ats-item-title {{ font-weight: bold; color: {color}; flex-grow: 1; }}
        .ats-item-duration {{ font-size: 9.5pt; white-space: nowrap; color: #000; }}
        .ats-item-subtitle {{ font-style: italic; color: #000; display: block; font-size: 9.5pt; }}
        .ats-bullet-list {{ list-style-type: disc; margin-left: 22px; padding-left: 0; margin-top: 2px; margin-bottom: 3px; }}
        .ats-bullet-list li {{ margin-bottom: 0px; line-height: 1.2; }}
        .ats-skills-group {{ margin-bottom: 3px; }}
        p {{ margin: 5px 0; }}
        </style>
    """


def get_css_clean_contemporary(color):
    return f"""
        <style>
        @page {{ margin: 0.35in; size: letter; }}
        body {{ margin: 0; padding: 0; }}
        .ats-page {{ 
            font-family: 'Calibri', 'Arial', sans-serif;
            font-size: 9pt;
            color: #333;
            max-width: 100%;
            margin: 0;
            padding: 0;
            line-height: 1.4;
        }}
        
        /* Colored header box/banner */
        .ats-header {{ 
            background-color: {color};
            padding: 20px 0.5in;
            margin: 0 0 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .ats-header h1 {{ 
            margin: 0 0 5px 0;
            font-size: 26pt;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 0.5px;
        }}
        
        .ats-job-title-header {{ 
            font-size: 12pt;
            color: rgba(255, 255, 255, 0.95);
            font-weight: 500;
            margin: 3px 0 6px 0;
        }}
        
        .ats-contact {{ 
            font-size: 9pt;
            color: rgba(255, 255, 255, 0.95);
            margin-top: 4px;
        }}
        
        .ats-contact span:not(:last-child)::after {{ 
            content: " | "; 
            white-space: pre; 
        }}
        
        .ats-page-content {{
            padding: 0 0.5in;
        }}
        
        .ats-section-title {{ 
            font-size: 10.5pt;
            font-weight: 700;
            color: {color};
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-top: 14px;
            margin-bottom: 8px;
            padding-left: 8px;
            border-left: 3px solid {color};
        }}
        
        .ats-item-header {{ 
            margin-top: 8px;
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            line-height: 1.1;
        }}
        
        .ats-item-title-group {{
            flex-grow: 1;
        }}
        
        .ats-item-title {{ 
            font-weight: 700;
            font-size: 10pt;
            color: {color};
            display: inline;
        }}
        
        .ats-item-subtitle {{ 
            font-size: 9pt;
            color: #666;
            display: inline;
            margin-left: 8px;
        }}
        
        .ats-item-subtitle::before {{
            content: "• ";
        }}
        
        .ats-item-duration {{ 
            font-size: 8.5pt;
            color: #999;
            font-weight: 600;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        
        .ats-bullet-list {{ 
            list-style-type: disc;
            margin-left: 18px;
            padding-left: 0;
            margin-top: 3px;
            margin-bottom: 8px;
        }}
        
        .ats-bullet-list li {{ 
            margin-bottom: 2px;
            line-height: 1.4;
            color: #555;
        }}
        
        .ats-skills-group {{ 
            margin-bottom: 5px;
            font-size: 9pt;
            line-height: 1.4;
        }}
        
        .ats-skills-group strong {{ 
            font-weight: 700;
            color: {color};
        }}
        
        p {{ 
            margin: 5px 0;
            line-height: 1.5;
        }}
        </style>
    """

def get_css_sophisticated_minimal(color):
    return f"""
        <style>
        @page {{ margin: 0.4in; size: letter; }}
        body {{ margin: 0; padding: 0; }}
        .ats-page {{ 
            font-family: 'Helvetica Neue', 'Arial', sans-serif;
            font-size: 9pt;
            color: #2d2d2d;
            max-width: 100%;
            margin: 0;
            padding: 0.4in 0.55in;
            line-height: 1.5;
        }}
        .ats-header {{ 
            margin-bottom: 24px;
        }}
        .ats-header h1 {{ 
            margin: 0 0 2px 0;
            font-size: 30pt;
            font-weight: 300;
            color: #1a1a1a;
            letter-spacing: 2px;
        }}
        .ats-job-title-header {{ 
            font-size: 11pt;
            color: #666;
            font-weight: 400;
            margin: 4px 0 10px 0;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }}
        .ats-contact {{ 
            font-size: 9pt;
            color: #888;
            padding-top: 10px;
            border-top: 1px solid #e0e0e0;
            margin-top: 8px;
        }}
        .ats-contact span:not(:last-child)::after {{ 
            content: " | "; 
            white-space: pre; 
        }}
        .ats-section-title {{ 
            font-size: 10pt;
            font-weight: 600;
            color: #1a1a1a;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-top: 16px;
            margin-bottom: 8px;
        }}
        .ats-item-header {{ 
            margin-top: 10px;
            margin-bottom: 5px;
            line-height: 1.1;
            padding-bottom: 8px;
        }}
        .ats-item-title-row {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 3px;
        }}
        .ats-item-title {{ 
            font-weight: 600;
            font-size: 10pt;
            color: {color};
            letter-spacing: 0.3px;
        }}
        .ats-item-subtitle {{ 
            font-size: 9pt;
            color: #666;
            font-style: italic;
            display: block;
            margin-top: 2px;
        }}
        .ats-item-duration {{ 
            font-size: 8.5pt;
            color: #999;
            font-weight: 400;
            white-space: nowrap;
        }}
        .ats-item-divider {{
            border-bottom: 0.5px solid #f0f0f0;
            margin-top: 8px;
        }}
        .ats-bullet-list {{ 
            list-style-type: disc;
            margin-left: 16px;
            padding-left: 0;
            margin-top: 4px;
            margin-bottom: 0px;
        }}
        .ats-bullet-list li {{ 
            margin-bottom: 3px;
            line-height: 1.5;
            color: #4a4a4a;
        }}
        .ats-skills-group {{ 
            margin-bottom: 6px;
            font-size: 9pt;
            line-height: 1.5;
        }}
        .ats-skills-group strong {{ 
            font-weight: 600;
            color: #1a1a1a;
        }}
        p {{ 
            margin: 5px 0;
            line-height: 1.6;
            text-align: justify;
        }}
        </style>
    """


def get_css_modern_minimal(color):
    return f"""
        <style>
        @page {{ margin: 0.4in; size: letter; }}
        body {{ margin: 0; padding: 0; }}
        .ats-page {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 9pt;
            color: #2c3e50;
            max-width: 100%;
            margin: 0;
            padding: 0.4in 0.5in;
            line-height: 1.4;
        }}
        .ats-header {{ 
            margin-bottom: 25px;
        }}
        .ats-header h1 {{ 
            margin: 0 0 4px 0;
            font-size: 28pt;
            font-weight: 700;
            color: {color};
            letter-spacing: 0.5px;
        }}
        .ats-job-title-header {{ 
            font-size: 12pt;
            color: #4a5568;
            font-weight: 500;
            margin: 3px 0 6px 0;
        }}
        .ats-contact {{ 
            font-size: 9pt;
            color: #718096;
            border-top: 1.5px solid #e2e8f0;
            padding-top: 8px;
            margin-top: 6px;
        }}
        .ats-contact span:not(:last-child)::after {{ 
            content: " | "; 
            white-space: pre; 
        }}
        .ats-section-title {{ 
            font-size: 11pt;
            font-weight: 700;
            color: {color};
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 15px;
            margin-bottom: 8px;
            padding-bottom: 3px;
            border-bottom: 2px solid {color};
        }}
        .ats-item-header {{ 
            margin-top: 8px;
            margin-bottom: 4px;
            line-height: 1.1;
            display: flex;
            justify-content: space-between;
            align-items: baseline;
        }}
        .ats-item-title-group {{
            flex-grow: 1;
            padding-right: 10px;
        }}
        .ats-item-title {{ 
            font-weight: 700;
            font-size: 10pt;
            color: #2d3748;
            display: inline;
        }}
        .ats-item-subtitle {{ 
            font-style: italic;
            font-size: 9pt;
            color: #4a5568;
            display: inline;
            margin-left: 6px;
        }}
        .ats-item-duration {{ 
            font-size: 8.5pt;
            color: #718096;
            font-weight: 500;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        .ats-bullet-list {{ 
            list-style-type: disc;
            margin-left: 18px;
            padding-left: 0;
            margin-top: 3px;
            margin-bottom: 8px;
        }}
        .ats-bullet-list li {{ 
            margin-bottom: 2px;
            line-height: 1.4;
            color: #4a5568;
        }}
        .ats-skills-group {{ 
            margin-bottom: 5px;
            font-size: 9pt;
            line-height: 1.4;
        }}
        .ats-skills-group strong {{ 
            font-weight: 700;
            color: #2d3748;
        }}
        p {{ 
            margin: 5px 0;
            line-height: 1.5;
            text-align: justify;
        }}
        </style>
    """


def get_css_elegant_professional(color):
    return f"""
        <style>
        @page {{ margin: 0.45in; size: letter; }}
        body {{ margin: 0; padding: 0; }}
        .ats-page {{ 
            font-family: 'Georgia', 'Times New Roman', serif;
            font-size: 9pt;
            color: #333333;
            max-width: 100%;
            margin: 0;
            padding: 0.45in 0.55in;
            line-height: 1.45;
        }}
        .ats-header {{ 
            text-align: center;
            margin-bottom: 22px;
            border-bottom: 2.5px double {color};
            padding-bottom: 15px;
        }}
        .ats-header h1 {{ 
            margin: 0 0 6px 0;
            font-size: 30pt;
            font-weight: 400;
            color: {color};
            letter-spacing: 1.5px;
        }}
        .ats-job-title-header {{ 
            font-size: 12pt;
            color: #555;
            font-style: italic;
            margin: 4px 0 8px 0;
        }}
        .ats-contact {{ 
            font-size: 9pt;
            color: #666;
            letter-spacing: 0.3px;
            margin-top: 6px;
        }}
        .ats-contact span:not(:last-child)::after {{ 
            content: " | "; 
            white-space: pre; 
        }}
        .ats-section-title {{ 
            font-size: 10.5pt;
            font-weight: 700;
            color: {color};
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-top: 16px;
            margin-bottom: 8px;
        }}
        .ats-item-header {{ 
            margin-top: 10px;
            margin-bottom: 5px;
            line-height: 1.1;
        }}
        .ats-item-title-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2px;
        }}
        .ats-item-title {{ 
            font-weight: 700;
            font-size: 10pt;
            color: {color};
        }}
        .ats-item-subtitle {{ 
            font-style: italic;
            font-size: 9pt;
            color: #666;
            display: block;
            margin-top: 1px;
        }}
        .ats-item-duration {{ 
            font-size: 8.5pt;
            color: #777;
            font-style: italic;
            white-space: nowrap;
        }}
        .ats-bullet-list {{ 
            list-style-type: disc;
            margin-left: 20px;
            padding-left: 0;
            margin-top: 4px;
            margin-bottom: 10px;
        }}
        .ats-bullet-list li {{ 
            margin-bottom: 3px;
            line-height: 1.45;
            color: #444;
        }}
        .ats-skills-group {{ 
            margin-bottom: 6px;
            font-size: 9pt;
            line-height: 1.5;
        }}
        .ats-skills-group strong {{ 
            font-weight: 700;
            color: {color};
        }}
        p {{ 
            margin: 5px 0;
            line-height: 1.55;
            text-align: justify;
        }}
        </style>
    """




def analyze_slide_structure(slide_texts):
    """Use LLM to find headings, subheadings, and related contents - INCLUDING BASIC INFO"""
    system_prompt = """
You are a presentation content analyzer.

You will receive a list of text boxes per slide, each with coordinates (x, y) and text content.

Your goal:
- Identify **basic information** (name, title, contact info, summary) - these should be marked as editable
- Identify **main headings** (e.g., "Selected Experiences", "Core Competencies", "Profile")
- Identify **subheadings** under a main heading
- Group all descriptive text under the closest subheading

CRITICAL: Basic information like name, job title, contact info, and summary SHOULD be marked as editable content, NOT locked headings.

Return **strictly valid JSON**:
[
  {
    "slide_number": 1,
    "sections": [
      {
        "heading": "Profile",
        "heading_shape_idx": 0,
        "is_basic_info": true,
        "subsections": [
          {
            "subheading": "",
            "subheading_shape_idx": null,
            "content_shape_idx": 1,
            "content_text": "Sudheer Varma\\nOracle Cloud HCM Techno Functional Consultant\\n8+ years of experience",
            "content_type": "basic_info"
          }
        ]
      }
    ]
  }
]
"""
    user_prompt = f"Analyze these slide texts and extract ALL content including basic information:\n{json.dumps(slide_texts, indent=2)}"

    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2500
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        result_text = response.json()["choices"][0]["message"]["content"]
        
        try:
            structured = json.loads(result_text)
        except json.JSONDecodeError:
            match = re.search(r'\[.*\]', result_text, re.DOTALL)
            structured = json.loads(match.group(0)) if match else []
        
        return structured
    except:
        return []
    
def analyze_content_length(text):
    """Analyze content length and return category"""
    word_count = len(text.split())
    char_count = len(text)
    
    if word_count < 30 or char_count < 150:
        return "very_short", word_count, char_count
    elif word_count < 60 or char_count < 400:
        return "short", word_count, char_count
    elif word_count < 100 or char_count < 700:
        return "medium", word_count, char_count
    else:
        return "long", word_count, char_count



def generate_ppt_sections(resume_data, structured_slides):
    """Generate AI content for ALL sections including basic info"""
    sections = []
    for slide in structured_slides:
        for section in slide.get("sections", []):
            # Check if this is basic info section
            is_basic_info = section.get("is_basic_info", False)
            
            entry = {
                "slide_number": slide.get("slide_number"),
                "heading": section.get("heading", ""),
                "heading_shape_idx": section.get("heading_shape_idx"),
                "is_basic_info": is_basic_info,
                "subsections": []
            }

            for subsec in section.get("subsections", []):
                original_text = subsec.get("content_text", "")
                content_type = subsec.get("content_type", "normal")
                
                # For basic info, we need special handling
                if is_basic_info or content_type == "basic_info":
                    # Basic info should be short and concise
                    target_word_count = min(len(original_text.split()), 50)
                    target_char_count = min(len(original_text), 300)
                    length_category = "short"
                else:
                    length_category, word_count, char_count = analyze_content_length(original_text)
                    target_word_count = word_count
                    target_char_count = char_count
                
                entry["subsections"].append({
                    "subheading": subsec.get("subheading", ""),
                    "subheading_shape_idx": subsec.get("subheading_shape_idx"),
                    "content_shape_idx": subsec.get("content_shape_idx"),
                    "original_content": original_text,
                    "target_word_count": target_word_count,
                    "target_char_count": target_char_count,
                    "length_category": length_category,
                    "content_type": content_type,
                    "is_basic_info": is_basic_info
                })

            sections.append(entry)

    system_prompt = """
You are a professional AI assistant that generates polished PowerPoint content from resume data.

CRITICAL REQUIREMENTS:
1. Match the target length specified for each section PRECISELY
2. For BASIC INFORMATION sections (name, title, contact, summary), replace with actual resume data
3. For EXPERIENCE sections, generate professional content that matches the target length

SPECIAL HANDLING FOR BASIC INFORMATION:
- Replace name with: {name}
- Replace title/position with actual experience titles
- Update contact info: {email}, {phone}, {location}
- For profile/summary: use the resume summary

TASK:
- For basic info sections: DIRECTLY REPLACE with actual resume data
- For other sections: Generate professional content that MATCHES target word count
- Always write in a formal, presentation-friendly tone
- Rewrite resume data to sound concise, polished, and visually engaging
- DO NOT use bullet points - write in paragraph form
- IMPORTANT: Respect the target_word_count for each section

OUTPUT FORMAT (strict JSON):
[
  {
    "slide_number": 1,
    "heading": "Profile",
    "is_basic_info": true,
    "subsections": [
      {
        "subheading": "",
        "content_shape_idx": 1,
        "target_word_count": 25,
        "generated_content": "Anaha Joy\\nMagento 2 Developer\\n2+ years of experience\\n+91 8304078233 | anahajoy2022@gmail.com"
      }
    ]
  }
]
"""

    user_prompt = f"""
Resume Data:
{json.dumps(resume_data, indent=2)}

PPT Structure with Target Lengths:
{json.dumps(sections, indent=2)}

Generate content for ALL sections:
- For BASIC INFO: Directly replace with actual resume data
- For EXPERIENCE: Generate professional content matching target length
"""

    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.45,
        "max_tokens": 4000
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        result_text = response.json()["choices"][0]["message"]["content"]
        
        try:
            structured_output = json.loads(result_text)
        except json.JSONDecodeError:
            match = re.search(r'\[.*\]', result_text, re.DOTALL)
            structured_output = json.loads(match.group(0)) if match else []
        
        return structured_output
    except:
        return []
    
def trim_content_to_length(content, target_word_count, target_char_count):
    """Trim content to match target length while maintaining coherence"""
    current_words = len(content.split())
    current_chars = len(content)
    
    # If content is within acceptable range (±20%), return as is
    word_diff = abs(current_words - target_word_count) / max(target_word_count, 1)
    if word_diff < 0.2:
        return content
    
    # If too long, trim sentences
    if current_words > target_word_count * 1.2:
        sentences = content.split('. ')
        trimmed = []
        word_count = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            if word_count + sentence_words <= target_word_count * 1.1:
                trimmed.append(sentence)
                word_count += sentence_words
            else:
                break
        
        result = '. '.join(trimmed)
        if result and not result.endswith('.'):
            result += '.'
        return result
    
    return content
def similarity_score(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def match_generated_to_original(original_elements, generated_sections, prs):
    """
    Smart matching system that maps generated content to original PPT positions
    NOW ALLOWS BASIC INFO TO BE EDITABLE
    """
    content_mapping = {}
    heading_shapes = set()
    basic_info_shapes = set()
    
    for gen_section in generated_sections:
        slide_num = gen_section.get("slide_number", 1)
        is_basic_info = gen_section.get("is_basic_info", False)
        
        # Mark heading as non-editable UNLESS it's basic info
        heading_shape_idx = gen_section.get("heading_shape_idx")
        if heading_shape_idx is not None and not is_basic_info:
            heading_shapes.add(f"{slide_num}_{heading_shape_idx}")
        
        for subsec in gen_section.get("subsections", []):
            # Mark subheading as non-editable
            subheading_shape_idx = subsec.get("subheading_shape_idx")
            if subheading_shape_idx is not None:
                heading_shapes.add(f"{slide_num}_{subheading_shape_idx}")
            
            # Map generated content to content shape
            content_shape_idx = subsec.get("content_shape_idx")
            generated_content = subsec.get("generated_content", "")
            target_word_count = subsec.get("target_word_count", 0)
            target_char_count = subsec.get("target_char_count", 0)
            
            # For basic info, always replace
            if is_basic_info or subsec.get("is_basic_info", False):
                basic_info_shapes.add(f"{slide_num}_{content_shape_idx}")
            
            # Trim content to match target length
            if generated_content and target_word_count:
                generated_content = trim_content_to_length(
                    generated_content, 
                    target_word_count, 
                    target_char_count
                )
            
            if content_shape_idx is not None and generated_content:
                key = f"{slide_num}_{content_shape_idx}"
                content_mapping[key] = generated_content
            elif generated_content:
                # Fallback: find best matching content by similarity
                subheading = subsec.get("subheading", "")
                original_content = subsec.get("original_content", "")
                
                # Find shapes on this slide
                best_match_key = None
                best_score = 0
                
                for elem in original_elements:
                    if elem['slide'] == slide_num:
                        elem_key = f"{elem['slide']}_{elem['shape']}"
                        
                        # Skip if already mapped or is heading
                        if elem_key in content_mapping or elem_key in heading_shapes:
                            continue
                        
                        # Check if this shape contains similar content
                        score = similarity_score(elem['original_text'], original_content)
                        
                        if score > best_score and score > 0.3:
                            best_score = score
                            best_match_key = elem_key
                
                if best_match_key:
                    content_mapping[best_match_key] = generated_content
    
    return content_mapping, heading_shapes, basic_info_shapes

def clear_and_replace_text(shape, new_text):
    """Replace text while preserving formatting"""
    if not shape.has_text_frame:
        return
    
    # Store original formatting
    original_font = None
    if shape.text_frame.paragraphs and shape.text_frame.paragraphs[0].runs:
        first_run = shape.text_frame.paragraphs[0].runs[0]
        original_font = {
            'name': first_run.font.name,
            'size': first_run.font.size,
            'bold': first_run.font.bold,
            'italic': first_run.font.italic,
        }
        try:
            if first_run.font.color.type == 1:
                original_font['color'] = first_run.font.color.rgb
        except:
            pass
    
    # Clear all text
    for paragraph in shape.text_frame.paragraphs:
        for run in paragraph.runs:
            run.text = ""
    
    # Replace with new text
    if shape.text_frame.paragraphs:
        first_paragraph = shape.text_frame.paragraphs[0]
        if first_paragraph.runs:
            first_run = first_paragraph.runs[0]
        else:
            first_run = first_paragraph.add_run()
        
        first_run.text = new_text
        
        # Restore formatting
        if original_font:
            if original_font.get('name'):
                first_run.font.name = original_font['name']
            if original_font.get('size'):
                first_run.font.size = original_font['size']
            if original_font.get('bold') is not None:
                first_run.font.bold = original_font['bold']
            if original_font.get('italic') is not None:
                first_run.font.italic = original_font['italic']
            if original_font.get('color'):
                try:
                    first_run.font.color.rgb = original_font['color']
                except:
                    pass
        
        # Remove extra paragraphs
        while len(shape.text_frame.paragraphs) > 1:
            p = shape.text_frame.paragraphs[-1]
            shape.text_frame._element.remove(p._element)

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import json
import re

# ============= HELPER FUNCTIONS =============

def is_heading(para):
    """Check if paragraph is a heading"""
    if para.style.name.startswith('Heading') or para.style.name == 'Title':
        return True
    
    if para.runs and para.runs[0].bold and len(para.text.strip().split()) <= 10:
        return True
    
    return False

def detect_section(text):
    """Detect which section a paragraph belongs to"""
    text_lower = text.lower().strip()
    
    section_keywords = {
        'experience': ['experience', 'employment', 'work history', 'professional experience'],
        'education': ['education', 'academic', 'qualification'],
        'skills': ['skills', 'technical skills', 'competencies', 'expertise', 'tools', 'languages'],
        'projects': ['projects', 'key projects'],
        'certifications': ['certifications', 'certificates', 'licenses'],
        'achievements': ['achievements', 'accomplishments', 'awards'],
        'summary': ['summary', 'profile', 'about', 'objective', 'professional summary'],
    }
    
    for section, keywords in section_keywords.items():
        if any(keyword == text_lower or keyword in text_lower for keyword in keywords):
            return section
    
    return None

def extract_document_structure(uploaded_file):
    """Extract document structure with sections"""
    doc = Document(uploaded_file)
    structure = []
    current_section = None
    section_content_start = None
    
    for idx, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text:
            continue
        
        # Check if it's a header
        is_header = is_heading(para)
        detected_section = detect_section(text) if is_header else None
        
        # If we found a new section
        if detected_section:
            # Save previous section if exists
            if current_section and section_content_start is not None:
                structure.append({
                    'section': current_section,
                    'header_idx': section_content_start - 1,
                    'content_start': section_content_start,
                    'content_end': idx - 1
                })
            
            current_section = detected_section
            section_content_start = idx + 1
        
        # Handle header content (name, title, contact)
        elif idx <= 3 and not current_section:
            if idx == 0:
                structure.append({'section': 'name', 'para_idx': idx})
            elif idx == 1:
                structure.append({'section': 'job_title', 'para_idx': idx})
            elif idx == 2 or idx == 3:
                structure.append({'section': 'contact', 'para_idx': idx})
    
    # Save last section
    if current_section and section_content_start is not None:
        structure.append({
            'section': current_section,
            'header_idx': section_content_start - 1,
            'content_start': section_content_start,
            'content_end': len(doc.paragraphs) - 1
        })
    
    return doc, structure

def clean_list_representation(data):
    """Clean Python list/dict string representations"""
    if isinstance(data, str):
        # Try to parse as JSON
        try:
            return json.loads(data.replace("'", '"'))
        except:
            pass
        
        # Remove Python dict/list syntax
        data = re.sub(r"^\{|\}$", "", data)  # Remove outer braces
        data = re.sub(r"^\[|\]$", "", data)  # Remove outer brackets
        data = re.sub(r"['\"]", "", data)     # Remove quotes
        
    return data

def format_skills(skills_data):
    """Format skills data properly"""
    if isinstance(skills_data, dict):
        lines = []
        for key, value in skills_data.items():
            key_title = key.replace('_', ' ').title()
            
            if isinstance(value, list):
                # Join list items with commas
                value_str = ", ".join(str(v) for v in value)
                lines.append(f"{key_title}: {value_str}")
            elif isinstance(value, str):
                # Clean string representation
                cleaned = clean_list_representation(value)
                if isinstance(cleaned, list):
                    value_str = ", ".join(str(v) for v in cleaned)
                    lines.append(f"{key_title}: {value_str}")
                else:
                    lines.append(f"{key_title}: {cleaned}")
            else:
                lines.append(f"{key_title}: {value}")
        
        return "\n\n".join(lines)
    
    elif isinstance(skills_data, list):
        return ", ".join(str(s) for s in skills_data)
    
    elif isinstance(skills_data, str):
        # Clean any Python syntax
        cleaned = clean_list_representation(skills_data)
        if isinstance(cleaned, (list, dict)):
            return format_skills(cleaned)
        return cleaned
    
    return str(skills_data)

def format_experience(exp_list):
    """Format experience data with bold subheadings"""
    result = []
    for exp in exp_list:
        job_title = exp.get('job_title', exp.get('position', ''))
        company = exp.get('company', '')
        location = exp.get('location', '')
        start_date = exp.get('start_date', '')
        end_date = exp.get('end_date', '')
        
        # Format date range
        duration = f"{start_date} - {end_date}" if start_date or end_date else ""
        
        # Get responsibilities
        responsibilities = exp.get('responsibilities', exp.get('description', []))
        if isinstance(responsibilities, str):
            # Clean string representation
            cleaned = clean_list_representation(responsibilities)
            if isinstance(cleaned, list):
                responsibilities = cleaned
            else:
                responsibilities = [cleaned]
        
        result.append({
            'job_title': job_title,
            'company': company,
            'duration': duration,
            'location': location,
            'bullets': [str(r).strip() for r in responsibilities if r]
        })
    
    return result

def format_education(edu_list):
    """Format education data"""
    result = []
    for edu in edu_list:
        degree = edu.get('degree', '')
        institution = edu.get('institution', '')
        location = edu.get('location', '')
        year = edu.get('year', '')
        start_date = edu.get('start_date', '')
        end_date = edu.get('end_date', '')
        
        # Use year or date range
        duration = year if year else (f"{start_date} - {end_date}" if start_date or end_date else "")
        
        result.append({
            'degree': degree,
            'institution': institution,
            'year': duration,
            'location': location
        })
    
    return result

def format_projects(proj_list):
    """Format projects data with bold titles"""
    result = []
    for proj in proj_list:
        title = proj.get('title', proj.get('name', ''))
        description = proj.get('description', [])
        
        if isinstance(description, str):
            cleaned = clean_list_representation(description)
            if isinstance(cleaned, list):
                description = cleaned
            else:
                description = [cleaned]
        
        result.append({
            'title': title,
            'bullets': [str(d).strip() for d in description if d]
        })
    
    return result

def format_certifications(cert_list):
    """Format certifications"""
    result = []
    for cert in cert_list:
        if isinstance(cert, str):
            result.append(cert)
        elif isinstance(cert, dict):
            name = cert.get('name', cert.get('title', ''))
            issuer = cert.get('issuer', cert.get('institution', ''))
            if name:
                line = name
                if issuer:
                    line += f" {issuer}"
                result.append(line)
    
    return result

def replace_paragraph_preserving_format(para, new_text, keep_bold=False):
    """Replace paragraph text while preserving all formatting"""
    if not para.runs:
        para.add_run(new_text)
        return
    
    # Store first run's formatting
    first_run = para.runs[0]
    font_name = first_run.font.name
    font_size = first_run.font.size
    bold = first_run.font.bold if keep_bold else False
    italic = first_run.font.italic
    
    try:
        color = first_run.font.color.rgb
    except:
        color = None
    
    # Clear all runs
    for run in para.runs:
        run.text = ""
    
    # Remove extra runs
    while len(para.runs) > 1:
        para._element.remove(para.runs[-1]._element)
    
    # Set new text and restore formatting
    para.runs[0].text = new_text
    if font_name:
        para.runs[0].font.name = font_name
    if font_size:
        para.runs[0].font.size = font_size
    if color:
        try:
            para.runs[0].font.color.rgb = color
        except:
            pass
    para.runs[0].font.bold = bold
    para.runs[0].font.italic = italic

def add_formatted_run(para, text, bold=False, italic=False, ref_run=None):
    """Add a run with specific formatting"""
    run = para.add_run(text)
    
    if ref_run:
        if ref_run.font.name:
            run.font.name = ref_run.font.name
        if ref_run.font.size:
            run.font.size = ref_run.font.size
        try:
            if ref_run.font.color.rgb:
                run.font.color.rgb = ref_run.font.color.rgb
        except:
            pass
    
    run.font.bold = bold
    run.font.italic = italic
    
    return run

def replace_experience_content(doc, start_idx, end_idx, exp_data, ref_para):
    """Replace experience content with bold job titles and italic companies"""
    # Get reference formatting
    ref_run = ref_para.runs[0] if ref_para and ref_para.runs else None
    
    # Build text with proper formatting
    text_parts = []
    
    for exp in exp_data:
        # Format: **Job Title** *Company*
        job_company = f"{exp['job_title']} {exp['company']}".strip()
        
        text_parts.append(job_company)
        
        # Add bullets
        for bullet in exp['bullets']:
            text_parts.append(f"• {bullet}")
        
        text_parts.append("")  # Empty line between experiences
    
    # Join and replace
    full_text = "\n".join(text_parts).strip()
    
    if start_idx < len(doc.paragraphs):
        para = doc.paragraphs[start_idx]
        
        # Clear existing content
        for run in para.runs:
            run.text = ""
        while len(para.runs) > 1:
            para._element.remove(para.runs[-1]._element)
        
        # Add content with mixed formatting
        current_text = ""
        for exp in exp_data:
            # Add job title (bold) and company (italic)
            if exp['job_title']:
                job_run = para.add_run(exp['job_title'] + " ")
                job_run.font.bold = True
                if ref_run:
                    if ref_run.font.name:
                        job_run.font.name = ref_run.font.name
                    if ref_run.font.size:
                        job_run.font.size = ref_run.font.size
            
            if exp['company']:
                company_run = para.add_run(exp['company'])
                company_run.font.italic = True
                if ref_run:
                    if ref_run.font.name:
                        company_run.font.name = ref_run.font.name
                    if ref_run.font.size:
                        company_run.font.size = ref_run.font.size
            
            # Add line break
            para.add_run("\n")
            
            # Add bullets
            for bullet in exp['bullets']:
                bullet_run = para.add_run(f"• {bullet}\n")
                if ref_run:
                    if ref_run.font.name:
                        bullet_run.font.name = ref_run.font.name
                    if ref_run.font.size:
                        bullet_run.font.size = ref_run.font.size
            
            # Add spacing between experiences
            para.add_run("\n")
    
    return list(range(start_idx + 1, end_idx + 1))

def replace_projects_content(doc, start_idx, end_idx, proj_data, ref_para):
    """Replace projects content with bold titles"""
    ref_run = ref_para.runs[0] if ref_para and ref_para.runs else None
    
    if start_idx < len(doc.paragraphs):
        para = doc.paragraphs[start_idx]
        
        # Clear existing content
        for run in para.runs:
            run.text = ""
        while len(para.runs) > 1:
            para._element.remove(para.runs[-1]._element)
        
        # Add content with bold titles
        for proj in proj_data:
            # Add project title (bold)
            if proj['title']:
                title_run = para.add_run(proj['title'])
                title_run.font.bold = True
                if ref_run:
                    if ref_run.font.name:
                        title_run.font.name = ref_run.font.name
                    if ref_run.font.size:
                        title_run.font.size = ref_run.font.size
                
                para.add_run("\n")
            
            # Add bullets
            for bullet in proj['bullets']:
                bullet_run = para.add_run(f"• {bullet}\n")
                if ref_run:
                    if ref_run.font.name:
                        bullet_run.font.name = ref_run.font.name
                    if ref_run.font.size:
                        bullet_run.font.size = ref_run.font.size
            
            # Add spacing
            para.add_run("\n")
    
    return list(range(start_idx + 1, end_idx + 1))

def replace_section_content(doc, start_idx, end_idx, formatted_data, ref_para, section_type):
    """Replace section content with new data"""
    # Handle special formatting for experience and projects
    if section_type == 'experience' and isinstance(formatted_data, list):
        return replace_experience_content(doc, start_idx, end_idx, formatted_data, ref_para)
    
    if section_type == 'projects' and isinstance(formatted_data, list):
        return replace_projects_content(doc, start_idx, end_idx, formatted_data, ref_para)
    
    # Regular content replacement
    ref_run = ref_para.runs[0] if ref_para and ref_para.runs else None
    
    # Build text content
    text_lines = []
    
    if isinstance(formatted_data, list):
        if formatted_data and isinstance(formatted_data[0], dict):
            # Education or other structured data
            for item in formatted_data:
                parts = []
                if item.get('degree'):
                    parts.append(item['degree'])
                if item.get('institution'):
                    parts.append(item['institution'])
                
                header = " ".join(parts)
                if header:
                    text_lines.append(header)
                
                if item.get('year'):
                    text_lines.append(item['year'])
                
                text_lines.append("")
        else:
            # Simple list (certifications)
            for item in formatted_data:
                text_lines.append(f"• {item}")
    
    elif isinstance(formatted_data, str):
        text_lines.append(formatted_data)
    
    # Join text
    full_text = "\n".join(text_lines).strip()
    
    # Replace content
    if start_idx < len(doc.paragraphs):
        para = doc.paragraphs[start_idx]
        replace_paragraph_preserving_format(para, full_text, keep_bold=False)
    
    return list(range(start_idx + 1, end_idx + 1))

def replace_content(doc, structure, final_data):
    """Main function to replace content"""
    paragraphs_to_remove = set()
    replaced_count = 0
    sections_to_remove = set()
    
    # First pass: identify sections not in final_data
    for item in structure:
        section = item['section']
        if section not in ['name', 'job_title', 'contact']:
            if section not in final_data or not final_data[section]:
                # Mark entire section for removal
                if 'header_idx' in item:
                    sections_to_remove.add(item['header_idx'])
                if 'content_start' in item:
                    for idx in range(item['content_start'], item['content_end'] + 1):
                        sections_to_remove.add(idx)
    
    # Second pass: replace content
    for item in structure:
        section = item['section']
        
        # Skip sections marked for removal
        if 'header_idx' in item and item['header_idx'] in sections_to_remove:
            continue
        
        # Handle header sections
        if section == 'name':
            if 'para_idx' in item and 'name' in final_data:
                para_idx = item['para_idx']
                if para_idx < len(doc.paragraphs):
                    replace_paragraph_preserving_format(doc.paragraphs[para_idx], final_data['name'], keep_bold=True)
                    replaced_count += 1
        
        elif section == 'job_title':
            if 'para_idx' in item and 'job_title' in final_data:
                para_idx = item['para_idx']
                if para_idx < len(doc.paragraphs):
                    replace_paragraph_preserving_format(doc.paragraphs[para_idx], final_data['job_title'], keep_bold=False)
                    replaced_count += 1
        
        elif section == 'contact':
            if 'para_idx' in item:
                contact_parts = []
                if final_data.get('phone'):
                    contact_parts.append(final_data['phone'])
                if final_data.get('email'):
                    contact_parts.append(final_data['email'])
                if final_data.get('location'):
                    contact_parts.append(final_data['location'])
                
                if contact_parts:
                    para_idx = item['para_idx']
                    if para_idx < len(doc.paragraphs):
                        replace_paragraph_preserving_format(doc.paragraphs[para_idx], " | ".join(contact_parts), keep_bold=False)
                        replaced_count += 1
        
        # Handle content sections
        else:
            if 'content_start' in item and section in final_data and final_data[section]:
                content_start = item['content_start']
                content_end = item['content_end']
                ref_para = doc.paragraphs[content_start] if content_start < len(doc.paragraphs) else None
                
                # Format data based on section
                formatted_data = None
                
                if section == 'experience':
                    formatted_data = format_experience(final_data['experience'])
                elif section == 'education':
                    formatted_data = format_education(final_data['education'])
                elif section == 'skills':
                    formatted_data = format_skills(final_data['skills'])
                elif section == 'projects':
                    formatted_data = format_projects(final_data['projects'])
                elif section == 'certifications':
                    formatted_data = format_certifications(final_data['certifications'])
                elif section == 'summary':
                    formatted_data = final_data['summary']
                
                if formatted_data:
                    to_remove = replace_section_content(doc, content_start, content_end, formatted_data, ref_para, section)
                    paragraphs_to_remove.update(to_remove)
                    replaced_count += 1
    
    # Combine all paragraphs to remove
    paragraphs_to_remove.update(sections_to_remove)
    
    # Remove marked paragraphs
    for idx in sorted(paragraphs_to_remove, reverse=True):
        if idx < len(doc.paragraphs):
            p = doc.paragraphs[idx]._element
            p.getparent().remove(p)
    
    # Save document
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    
    return output, replaced_count, len(paragraphs_to_remove)

import json
import os
import base64

# ============= DOC TEMPLATE STORAGE FUNCTIONS =============

def get_user_doc_templates_path(username):
    """Get the path for user's document templates JSON file"""
    templates_dir = "user_doc_templates"
    os.makedirs(templates_dir, exist_ok=True)
    return os.path.join(templates_dir, f"{username}_doc_templates.json")

def load_user_doc_templates(username):
    """Load user's saved document templates"""
    filepath = get_user_doc_templates_path(username)
    
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                templates = json.load(f)
                
                # Convert binary data back from base64
                for template_id, template_data in templates.items():
                    if 'doc_data_b64' in template_data:
                        templates[template_id]['doc_data'] = base64.b64decode(template_data['doc_data_b64'])
                        del templates[template_id]['doc_data_b64']
                
                return templates
        except Exception as e:
            print(f"Error loading doc templates: {str(e)}")
            return {}
    
    return {}

def save_user_doc_templates(username, templates):
    """Save user's document templates to JSON"""
    filepath = get_user_doc_templates_path(username)
    
    try:
        # Convert binary data to base64 for JSON serialization
        templates_to_save = {}
        
        for template_id, template_data in templates.items():
            templates_to_save[template_id] = template_data.copy()
            
            # Convert binary doc_data to base64
            if 'doc_data' in template_data:
                templates_to_save[template_id]['doc_data_b64'] = base64.b64encode(template_data['doc_data']).decode('utf-8')
                del templates_to_save[template_id]['doc_data']
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(templates_to_save, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving doc templates: {str(e)}")
        return False

def delete_user_doc_template(username, template_id):
    """Delete a specific doc template"""
    templates = load_user_doc_templates(username)
    
    if template_id in templates:
        del templates[template_id]
        save_user_doc_templates(username, templates)
        return True
    
    return False


# ============= PPT TEMPLATE STORAGE FUNCTIONS =============

def get_user_ppt_templates_path(username):
    """Get the path for user's PPT templates JSON file"""
    templates_dir = "user_ppt_templates"
    os.makedirs(templates_dir, exist_ok=True)
    return os.path.join(templates_dir, f"{username}_ppt_templates.json")

def load_user_ppt_templates(username):
    """Load user's saved PPT templates"""
    filepath = get_user_ppt_templates_path(username)
    
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                templates = json.load(f)
                
                # Convert binary data back from base64
                for template_id, template_data in templates.items():
                    if 'ppt_data_b64' in template_data:
                        templates[template_id]['ppt_data'] = base64.b64decode(template_data['ppt_data_b64'])
                        del templates[template_id]['ppt_data_b64']
                    
                    # Convert sets back from lists
                    if 'heading_shapes' in template_data and isinstance(template_data['heading_shapes'], list):
                        templates[template_id]['heading_shapes'] = set(template_data['heading_shapes'])
                    
                    if 'basic_info_shapes' in template_data and isinstance(template_data['basic_info_shapes'], list):
                        templates[template_id]['basic_info_shapes'] = set(template_data['basic_info_shapes'])
                
                return templates
        except Exception as e:
            print(f"Error loading PPT templates: {str(e)}")
            return {}
    
    return {}

def save_user_ppt_templates(username, templates):
    """Save user's PPT templates to JSON"""
    filepath = get_user_ppt_templates_path(username)
    
    try:
        templates_to_save = {}
        
        for template_id, template_data in templates.items():
            templates_to_save[template_id] = template_data.copy()
            
            # Convert binary ppt_data to base64
            if 'ppt_data' in template_data:
                templates_to_save[template_id]['ppt_data_b64'] = base64.b64encode(template_data['ppt_data']).decode('utf-8')
                del templates_to_save[template_id]['ppt_data']
            
            # Convert sets to lists for JSON
            if 'heading_shapes' in template_data and isinstance(template_data['heading_shapes'], set):
                templates_to_save[template_id]['heading_shapes'] = list(template_data['heading_shapes'])
            
            if 'basic_info_shapes' in template_data and isinstance(template_data['basic_info_shapes'], set):
                templates_to_save[template_id]['basic_info_shapes'] = list(template_data['basic_info_shapes'])
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(templates_to_save, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving PPT templates: {str(e)}")
        return False


def get_resume_hash(resume_data):
    """Generate a hash of resume data to detect changes"""
    resume_str = json.dumps(resume_data, sort_keys=True, default=str)
    return hashlib.md5(resume_str.encode()).hexdigest()

def should_regenerate_resume():
    """Check if we need to regenerate the enhanced resume"""
    current_user = st.session_state.get('logged_in_user')
    resume_data = st.session_state.get('resume_source')
    jd_data = st.session_state.get('job_description')
    
    if 'enhanced_resume' not in st.session_state:
        return True
    
   
    if st.session_state.get('last_resume_user') != current_user:
        return True
    
    
    current_resume_hash = get_resume_hash(resume_data) if resume_data else None
    if st.session_state.get('last_resume_hash') != current_resume_hash:
        return True

    current_jd_hash = get_resume_hash(jd_data) if jd_data else None
    if st.session_state.get('last_jd_hash') != current_jd_hash:
        return True
    
    return False

def generate_enhanced_resume():
    """Generate enhanced resume and store metadata"""
    resume_data = st.session_state.get('resume_source')
    jd_data = st.session_state.get('job_description')
    current_user = st.session_state.get('logged_in_user') or st.query_params.get('user', '')
    
    # If resume_data is None, try to fetch it from user's stored data
    if resume_data is None and current_user:
        try:
            users = load_users()
            user_entry = users.get(current_user)
            
            if isinstance(user_entry, dict):
                user_resume = get_user_resume(current_user)
                
                if user_resume and len(user_resume) > 0:
                    resume_data = user_resume
                    st.session_state['resume_source'] = user_resume
                    st.session_state['input_method'] = user_resume.get("input_method", "Manual Entry")
                    st.session_state['username'] = current_user.split('@')[0]
                else:
                    st.error(f"No resume data found for user: {current_user}. Please create a resume first.")
                    if st.button("Go to Home"):
                        st.query_params["home"] = "true"
                        st.query_params["user"] = current_user
                        st.rerun()
                    st.stop()
            else:
                st.error(f"User not found: {current_user}")
                st.stop()
        except Exception as e:
            st.error(f"Error fetching resume data: {str(e)}")
            st.stop()
    elif resume_data is None:
        st.error("No resume data found and no user logged in. Please go back to the main page.")
        if st.button("Go to Login"):
            st.switch_page("pages/main.py")
        st.stop()
    
    # If jd_data is still None, you might want to handle it
    # if jd_data is None:
    #     st.warning("No job description found. Using default optimization.")
    #     jd_data = {}  # or fetch default JD if you have one
    
    # Safely get input_method with fallback
    input_method = st.session_state.get(
        "input_method", 
        resume_data.get("input_method", "Manual Entry") if isinstance(resume_data, dict) else "Manual Entry"
    )
   
    if input_method == "Manual Entry":
        enhanced_resume = rewrite_resume_for_job_manual(resume_data, jd_data)
    else:
        enhanced_resume = rewrite_resume_for_job(resume_data, jd_data)

    st.session_state['enhanced_resume'] = enhanced_resume
    st.session_state['last_resume_user'] = current_user
    st.session_state['last_resume_hash'] = get_resume_hash(resume_data) if resume_data else None
    st.session_state['last_jd_hash'] = get_resume_hash(jd_data) if jd_data else None
    chatbot(enhanced_resume)
    return enhanced_resume


def format_section_title(key):
    """Converts keys like 'certifications' to 'Certifications'."""
    title = key.replace('_', ' ')
    return ' '.join(word.capitalize() for word in title.split())


def render_basic_details(data, is_edit):
    """Top header section (Name, title, contact info)."""
    if is_edit:
        st.markdown('<h2>Basic Details</h2>', unsafe_allow_html=True)
        data['name'] = st.text_input("Name", data.get('name', ''), key="edit_name")
        data['job_title'] = st.text_input("Job Title", data.get('job_title', ''), key="edit_job_title")

        col1, col2, col3,col4 = st.columns(4)
        with col1:
            data['phone'] = st.text_input("Phone", data.get('phone', ''), key="edit_phone")
        with col2:
            data['email'] = st.text_input("Email", data.get('email', ''), key="edit_email")
        with col3:
            data['location'] = st.text_input("Location", data.get('location', ''), key="edit_location")
        with col4:
            data['url'] = st.text_input("url", data.get('url', ''), key="edit_url")
 

        st.markdown('<div class="resume-section">', unsafe_allow_html=True)
        st.markdown('<h2>Summary</h2>', unsafe_allow_html=True)
        data['summary'] = st.text_area("Summary", data.get('summary', ''), height=150, key="edit_summary")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(f"<h1>{data.get('name', 'Name Not Found')}</h1>", unsafe_allow_html=True)
        if data.get('job_title'):
            st.markdown(f"<h3>{data['job_title']}</h3>", unsafe_allow_html=True)

        contact_html = f"""
        <div class="contact-info">
            {data.get('phone', '')} | {data.get('email', '')} | {data.get('location', '')}
        </div>
        """
        st.markdown(contact_html, unsafe_allow_html=True)

        if data.get('summary'):
            st.markdown('<div class="resume-section">', unsafe_allow_html=True)
            st.markdown('<h2>Summary</h2>', unsafe_allow_html=True)
            st.markdown(f"<p style='color:#E0E0E0;'>{data['summary']}</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


def format_date(date_string):
    """
    Converts date from YYYY-MM-DD to MMM YYYY format.
    Example: "2025-10-14" -> "Oct 2025"
    """
    if not date_string or date_string.strip() == '':
        return ''
    
    try:
        from datetime import datetime
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        return date_obj.strftime('%b %Y')
    except:
        return date_string  # Return original if parsing fails


def render_list_item(item, index, key_prefix, section_title, is_edit=True):
    """Generic list item renderer for both edit and view modes with dynamic field handling."""
    
    # Normalize item to dict
    if isinstance(item, str):
        item = {"title": item}
    
    # Define field priority order for display
    title_keys = ['position', 'title', 'name', 'degree', 'institution', 'company', 'certificate_name']
    subtitle_keys = ['company', 'institution', 'issuer', 'organization', 'provider_name']
    detail_keys_to_skip = ['position', 'title', 'name', 'degree', 'company', 'institution', 
                           'description', 'overview', 'issuer', 'start_date', 'end_date', 
                           'duration', 'certificate_name', 'organization', 'provider_name',
                           'details', 'achievement']

    if not is_edit:
        html_content = "<div>"
        
        # Get main title (first available from title_keys)
        main_title = None
        for key in title_keys:
            if key in item and item[key]:
                main_title = item[key]
                break
        
        if main_title:
            html_content += f'<div class="item-title">{main_title}</div>'
            
            # Get subtitle (first available from subtitle_keys, but not same as title)
            subtitle = None
            for key in subtitle_keys:
                if key in item and item[key] and item[key] != main_title:
                    subtitle = item[key]
                    break
            
            if subtitle:
                html_content += f'<div class="item-subtitle">{subtitle}</div>'

        # Format dates to MMM YYYY
        duration = item.get('duration')
        if not duration:
            start_date = format_date(item.get('start_date', ''))
            end_date = format_date(item.get('end_date', ''))
            if start_date or end_date:
                duration = f"{start_date} - {end_date}"
        
        if duration and duration.strip() != '-':
            html_content += f'<div class="item-details"><em>{duration}</em></div>'

        # Handle description/overview/details/achievement fields
        description_fields = ['description', 'overview', 'details', 'achievement']
        main_description_list = None
        for field in description_fields:
            if field in item:
                main_description_list = item[field]
                break
        
        if main_description_list:
            if isinstance(main_description_list, str):
                main_description_list = [main_description_list]
            if isinstance(main_description_list, list) and main_description_list:
                bullet_html = "".join([f"<li>{line}</li>" for line in main_description_list if line])
                html_content += f'<ul class="bullet-list">{bullet_html}</ul>'
        
        # Display any remaining fields not in skip list
        for k, v in item.items():
            if isinstance(v, str) and v.strip() and k not in detail_keys_to_skip + ['duration']:
                formatted_k = format_section_title(k)
                html_content += f'<div class="item-details">**{formatted_k}:** {v}</div>'

        html_content += "</div>"
        return html_content
    
    else:
        # EDIT MODE
        edited_item = item.copy()
        
        # Get all fields in item
        edit_fields = list(item.keys())
        
        # Priority fields for ordering
        priority_fields = ['position', 'title', 'name', 'company', 'institution', 'degree', 
                          'certificate_name', 'issuer', 'organization', 'provider_name',
                          'duration', 'start_date', 'end_date', 'description', 'overview', 
                          'details', 'achievement']
        
        # Order fields: priority first, then rest
        ordered_fields = []
        for field in priority_fields:
            if field in edit_fields:
                ordered_fields.append(field)
                edit_fields.remove(field)
        ordered_fields.extend(edit_fields)
        
        # Render input fields for each field in order
        for k in ordered_fields:
            v = item[k]
            if isinstance(v, str):
                edited_item[k] = st.text_input(
                    format_section_title(k), 
                    v, 
                    key=f"{key_prefix}_{k}_{index}"
                )
            elif isinstance(v, list):
                text = "\n".join(v)
                edited_text = st.text_area(
                    format_section_title(k), 
                    text, 
                    height=150, 
                    key=f"{key_prefix}_area_{k}_{index}"
                )
                edited_item[k] = [line.strip() for line in edited_text.split('\n') if line.strip()]
        
        return edited_item
    
def render_generic_section(section_key, data_list, is_edit):
    """Renders dynamic list sections with consistent formatting."""
    section_title = format_section_title(section_key)
    if not data_list: 
        return

    st.markdown('<div class="resume-section">', unsafe_allow_html=True)
    st.markdown(f'<h2>{section_title}</h2>', unsafe_allow_html=True)

    for i, item in enumerate(data_list):
        # Normalize all items to dictionaries
        if not isinstance(item, dict):
            if isinstance(item, str):
                item = {"title": item}
            else:
                item = {"title": str(item)}
            data_list[i] = item  # Update the list with normalized item

        with st.container(border=False):
            # Build expander title from available fields
            expander_title_parts = [
                item.get('position'),
                item.get('title'),
                item.get('name'),
                item.get('certificate_name'),
                item.get('company'),
                item.get('institution'),
                item.get('issuer')
            ]
            expander_title = next((t for t in expander_title_parts if t), f"{section_title[:-1]} Item {i+1}")
            
            if is_edit:
                with st.expander(f"📝 Edit: **{expander_title}**", expanded=False):
                    temp_item = deepcopy(item) 
                    edited_item = render_list_item(temp_item, i, f"{section_key}_edit_{i}", section_title, is_edit=True)
                    
                    if edited_item:
                        st.session_state['enhanced_resume'][section_key][i] = edited_item
                    
                    if st.button(f"❌ Remove this {section_title[:-1]}", key=f"{section_key}_remove_{i}"):
                        st.session_state['enhanced_resume'][section_key].pop(i)
                        st.rerun()
                
                # Show view mode preview below edit section
                st.markdown(render_list_item(item, i, f"{section_key}_view_{i}", section_title, is_edit=False), unsafe_allow_html=True)
            else:
                # View mode only
                st.markdown(render_list_item(item, i, f"{section_key}_view_{i}", section_title, is_edit=False), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_skills_section(data, is_edit):
    """Handles the nested dictionary structure of the 'skills' section."""
    skills_data = data.get('skills', {})
    if not skills_data: return

    st.markdown('<div class="resume-section">', unsafe_allow_html=True)
    st.markdown('<h2>Skills</h2>', unsafe_allow_html=True)

    if is_edit:
        with st.expander("📝 Edit Skills (Separate by Line)", expanded=False):
            for skill_type, skill_list in skills_data.items():
                st.subheader(format_section_title(skill_type))
                skill_text = "\n".join(skill_list)
                
                edited_text = st.text_area(f"Edit {skill_type}", skill_text, height=100, key=f"skills_edit_{skill_type}")
                
                st.session_state['enhanced_resume']['skills'][skill_type] = [line.strip() for line in edited_text.split('\n') if line.strip()]
    
    for skill_type, skill_list in skills_data.items():
        if skill_list:
            st.markdown(f"**{format_section_title(skill_type)}:**", unsafe_allow_html=True)
            skills_html = "".join([f'<li class="skill-item">{s}</li>' for s in skill_list])
            st.markdown(f'<ul class="skill-list">{skills_html}</ul>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def add_new_item(section_key, default_item):
    """Generic function to add a new item to any list section."""
    if section_key not in st.session_state['enhanced_resume']:
        st.session_state['enhanced_resume'][section_key] = []
            
    st.session_state['enhanced_resume'][section_key].append(default_item)
    st.rerun()

# MODIFIED: Save and Improve with hash update
def save_and_improve():
    """Calls auto_improve_resume and updates session state."""
    data = deepcopy(st.session_state['enhanced_resume'])
    user_skills_before = deepcopy(data.get('skills', {}))
    job_description = st.session_state.get('job_description', '') 

    
    improved_data = analyze_and_improve_resume(data, job_description)
    
    # Skills merging logic
    llm_skills_after = improved_data.get('skills', {})
    merged_skills = {}
    all_categories = set(user_skills_before.keys()) | set(llm_skills_after.keys())

    for category in all_categories:
        user_list = user_skills_before.get(category, [])
        llm_list = llm_skills_after.get(category, [])
        
        user_set = set(user_list)
        llm_set = set(llm_list)
        final_skills_set = user_set.copy()
        
        for skill in llm_set:
            if skill not in final_skills_set:
                final_skills_set.add(skill)
                
        merged_skills[category] = sorted(list(final_skills_set))

    improved_data['skills'] = merged_skills
    st.session_state['enhanced_resume'] = improved_data
    if 'ats_score_data' in st.session_state:
        del st.session_state['ats_score_data']
    
    # Update hash so it doesn't regenerate
    st.session_state['last_resume_hash'] = get_resume_hash(st.session_state.get('resume_source'))
    
    st.success("Resume content saved and improved! Check the updated details below.")



def image_to_base64_local(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str


def load_users():
    try:
        if users_file.exists():
            with open(users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        return {}
    
def save_users(users):
    try:
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        st.error(f"Error saving users: {e}")


def load_user_resume_data():
    """Load all users' resume data"""
    try:
        if user_data_file.exists():
            with open(user_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        return {}

def get_user_resume(email):
    """Get resume data for a specific user"""
    all_data = load_user_resume_data()
    user_resume = all_data.get(email, None)
    
    if user_resume and isinstance(user_resume, dict) and len(user_resume) > 0:
        return user_resume
    return None

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None




def show_login_modal():
    import streamlit as st
    import time 
    from PIL import Image
    from streamlit_extras.stylable_container import stylable_container
    from utils import load_users, save_users, is_valid_email, get_user_resume

    # Clear cache
    st.cache_data.clear()
    st.cache_resource.clear()
    
    # Session states
    if 'mode' not in st.session_state:
        st.session_state.mode = 'login'

    if 'page_transitioning' not in st.session_state:
        st.session_state.page_transitioning = False

    # -------------------------------------------------------------------------------------------------
    # CSS STYLES - Enhanced with Animation
    # -------------------------------------------------------------------------------------------------
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
        
        /* Overall page background */
        [data-testid="stAppViewContainer"] {
            background: #ffffff !important;
            font-family: 'Montserrat', sans-serif !important;
        }

        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Main container styling */
        .block-container {
            padding: 1.5rem !important;
            max-width: 1200px !important;
        }

        /* Main heading */
        .main-heading {
            font-size: 1.8rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 1.2rem;
            text-align: center;
            font-family: 'Montserrat', sans-serif;
        }

        /* Subtext */
        .form-subtext {
            font-size: 0.85rem;
            color: #666;
            text-align: center;
            margin-bottom: 1rem;
            letter-spacing: 0.3px;
        }

        /* Input fields styling */
        .stTextInput > div > div > input {
            background-color: #eee !important;
            color: #333 !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 13px !important;
            font-size: 13px !important;
            transition: all 0.3s ease !important;
            font-family: 'Montserrat', sans-serif !important;
            width: 100% !important;
            margin: 6px 0 !important;
        }

        .stTextInput > div > div > input:focus {
            background-color: #e8e8e8 !important;
            outline: none !important;
            box-shadow: 0 0 0 2px rgba(241, 39, 17, 0.1) !important;
        }

        .stTextInput > div > div > input::placeholder {
            color: #999 !important;
            font-weight: 400;
        }

        /* Social icons styling */
        .social-icons {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 15px 0;
        }

        .social-icon {
            border: 1px solid #ccc;
            border-radius: 20%;
            display: inline-flex;
            justify-content: center;
            align-items: center;
            width: 36px;
            height: 36px;
            color: #333;
            text-decoration: none;
            transition: all 0.3s ease;
            background: #fff;
        }

        .social-icon:hover {
            border-color: #f12711;
            color: #f12711;
            transform: translateY(-3px);
        }

        /* Sign up text link */
        .signup-text {
            text-align: center;
            color: #333;
            font-size: 13px;
            margin: 12px 0 8px;
        }

        .signup-link {
            color: #e87532;
            text-decoration: none;
            font-weight: 600;
            cursor: pointer;
            transition: color 0.3s ease;
        }

        .signup-link:hover {
            color: #d61f06;
            text-decoration: underline;
        }

        /* Divider */
        .divider-text {
            text-align: center;
            color: #666;
            margin: 1rem 0;
            font-size: 0.875rem;
        }

        /* Welcome panel (right side toggle) */
        .welcome-panel {
            background: linear-gradient(to right, #e87532, #f5af19);
            color: #fff;
            padding: 40px 30px;
            border-radius: 20px;
            text-align: center;
            min-height: 420px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .welcome-heading {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
            font-family: 'Montserrat', sans-serif;
        }

        .welcome-text {
            font-size: 0.95rem;
            line-height: 1.5;
            margin-bottom: 1.5rem;
            opacity: 0.95;
        }
            button:hover {
        background-color: transparent !important;
        background-image: none !important;
        box-shadow: none !important;
    }
    
    /* Specific override for text link buttons */
    [data-testid="stButton"] button[kind="secondary"]:hover {
        background-color: transparent !important;
        background-image: none !important;
        background: transparent !important;
    }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .welcome-panel {
                display: none;
            }
            
            .main-heading {
                font-size: 1.8rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------------------------------
    # PAGE LAYOUT
    # -------------------------------------------------------------------------------------------------
    
    # Create container columns
    col_form, col_welcome = st.columns([1, 1])

    # FORM SECTION (Left side)
    with col_form:
        # Mode-specific heading
        if st.session_state.mode == 'login':
            st.markdown('<h1 class="main-heading">Sign In</h1>', unsafe_allow_html=True)
        else:
            st.markdown('<h1 class="main-heading">Create Account</h1>', unsafe_allow_html=True)
        
        # Social icons
        st.markdown('''
        <div class="social-icons">
            <a href="#" class="social-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
            </a>
            <a href="#" class="social-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
            </a>
            <a href="#" class="social-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
            </a>
            <a href="#" class="social-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
            </a>
        </div>
        ''', unsafe_allow_html=True)
        
        # Subtext
        if st.session_state.mode == 'login':
            st.markdown('<p class="form-subtext">or use your email and password</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="form-subtext">or use your email for registration</p>', unsafe_allow_html=True)
        
        # Name field for registration
        name = ""
        if st.session_state.mode == 'register':
            name = st.text_input("", placeholder="Name", label_visibility="collapsed", key="full_name")
        
        # Email field
        email = st.text_input("", placeholder="Email", label_visibility="collapsed", key="lemail")
        
        # Password field
        password = st.text_input("", placeholder="Password", type="password", label_visibility="collapsed", key="password")
        
        # Sign up / Login text link - moved BEFORE main button
        col_spacer1, col_toggle_text, col_spacer2 = st.columns([2, 8, 2])
        with col_toggle_text:
            if st.session_state.mode == 'login':
                # Show Sign up link
                with stylable_container(
                    key="signup_text_btn",
                    css_styles="""
                    button {
                        background: transparent !important;
                        border: none !important;
                        color: #333 !important;
                        font-size: 13px !important;
                        padding: 8px 0 !important;
                        font-weight: 400 !important;
                        cursor: pointer !important;
                        font-family: 'Montserrat', sans-serif !important;
                        box-shadow: none !important;
                        width: 100% !important;
                    }
                    button:hover {
                        background: transparent !important;
                        box-shadow: none !important;
                        transform: none !important;
                        border: none !important;
                    }
                    button:hover p {
                        background: transparent !important;
                    }
                    button p {
                        margin: 0 !important;
                        text-align: center !important;
                    }
                    """
                ):
                    if st.button("Don't have an account? **Sign up**", key="signup_text_link"):
                        st.session_state.mode = 'register'
                        st.rerun()
            else:
                # Show Back to Login link
                with stylable_container(
                    key="login_text_btn",
                    css_styles="""
                    button {
                        background: transparent !important;
                        border: none !important;
                        color: #333 !important;
                        font-size: 13px !important;
                        padding: 8px 0 !important;
                        font-weight: 400 !important;
                        cursor: pointer !important;
                        font-family: 'Montserrat', sans-serif !important;
                        box-shadow: none !important;
                        width: 100% !important;
                    }
                    button:hover {
                        background: transparent !important;
                        box-shadow: none !important;
                        transform: none !important;
                        border: none !important;
                    }
                    button:hover p {
                        background: transparent !important;
                    }
                    button p {
                        margin: 0 !important;
                        text-align: center !important;
                    }
                    """
                ):
                    if st.button("Already have an account? **Back to Login**", key="login_text_link"):
                        st.session_state.mode = 'login'
                        st.rerun()
        
        # Main action button (Login/Sign Up) - Centered
        button_text = "Sign Up" if st.session_state.mode == 'register' else "Sign In"
        
        col_btn1, col_main_btn, col_btn2 = st.columns([2, 8, 2])
        with col_main_btn:
            with stylable_container(
                key="main_login_btn",
                css_styles="""
                button {
                    background-color: #e87532 !important;
                    color: #fff !important;
                    font-size: 12px !important;
                    padding: 10px 45px !important;
                    border: 1px solid transparent !important;
                    border-radius: 8px !important;
                    font-weight: 600 !important;
                    letter-spacing: 0.5px !important;
                    text-transform: uppercase !important;
                    margin-top: 10px !important;
                    cursor: pointer !important;
                    width: 100% !important;
                    transition: all 0.3s ease !important;
                    font-family: 'Montserrat', sans-serif !important;
                }
                button:hover {
                    background: linear-gradient(to right, #d61f06, #d4941a) !important;
                    transform: translateY(-2px) !important;
                    box-shadow: 0 5px 15px rgba(241, 39, 17, 0.3) !important;
                }
                """
            ):
                if st.button(button_text, key="main_action_btn"):
                    if email and password:
                        if not is_valid_email(email):
                            st.error("Please enter a valid email address")
                        else:
                            users = load_users()

                            if st.session_state.mode == 'login':
                                # LOGIN LOGIC
                                user_entry = users.get(email)
                                stored_pw = user_entry.get("password") if isinstance(user_entry, dict) else user_entry
                                stored_name = user_entry.get("name") if isinstance(user_entry, dict) else None

                                if user_entry is None or stored_pw != password:
                                    st.error("Invalid email or password")
                                else:
                                    st.session_state.logged_in_user = email
                                    st.query_params["user"] = email
                                    st.session_state.username = stored_name or email.split('@')[0]

                                    user_resume = get_user_resume(email)
                                    if user_resume and len(user_resume) > 0:
                                        st.session_state.resume_source = user_resume
                                        st.session_state.input_method = user_resume.get("input_method", "Manual Entry")
                                        st.success(f"Welcome back, {st.session_state.username}!")
                                        time.sleep(0.8)
                                        st.switch_page("app.py")
                                    else:
                                        st.success(f"Welcome, {st.session_state.username}!")
                                        time.sleep(0.8)
                                        st.switch_page("app.py")
                            else:
                                # REGISTRATION LOGIC
                                if email in users:
                                    st.error("Email already registered. Please login.")
                                    st.session_state.mode = 'login'
                                    st.rerun()
                                elif len(password) < 6:
                                    st.error("Password must be at least 6 characters long")
                                elif not name or len(name.strip()) == 0:
                                    st.error("Please enter your full name")
                                else:
                                    users[email] = {"password": password, "name": name.strip()}
                                    save_users(users)
                                    st.session_state.logged_in_user = email
                                    st.query_params["user"] = email
                                    st.session_state.username = name.strip()
                                    st.session_state.mode = 'login'
                                    st.success("Account created successfully!")
                                    time.sleep(0.8)
                                    st.switch_page("app.py")
                    else:
                        st.warning("Please enter both email and password")

    # WELCOME PANEL (Right side)
    with col_welcome:
        if st.session_state.mode == 'login':
            st.markdown('''
            <div class="welcome-panel">
                <h1 class="welcome-heading">Hello, User!</h1>
                <p class="welcome-text">Register with your personal details to use all of site features</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Toggle button
            with stylable_container(
                key="signup_toggle_btn",
                css_styles="""
                button {
                    background-color: transparent !important;
                    color: #fff !important;
                    border: 1px solid #fff !important;
                    border-radius: 8px !important;
                    padding: 10px 45px !important;
                    font-size: 12px !important;
                    font-weight: 600 !important;
                    letter-spacing: 0.5px !important;
                    text-transform: uppercase !important;
                    cursor: pointer !important;
                    width: 60% !important;
                    transition: all 0.3s ease !important;
                    font-family: 'Montserrat', sans-serif !important;
                    margin: 0 auto !important;
                    display: block !important;
                }
                button:hover {
                    background-color: #fff !important;
                    color: #f12711 !important;
                    transform: translateY(-2px) !important;
                }
                """
            ):
                if st.button("Sign Up", key="toggle_signup"):
                    st.session_state.mode = 'register'
                    st.rerun()
        else:
            st.markdown('''
            <div class="welcome-panel">
                <h1 class="welcome-heading">Welcome Back!</h1>
                <p class="welcome-text">Enter your personal details to use all of site features</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Toggle button
            with stylable_container(
                key="login_toggle_btn",
                css_styles="""
                button {
                    background-color: transparent !important;
                    color: #fff !important;
                    border: 1px solid #fff !important;
                    border-radius: 8px !important;
                    padding: 10px 45px !important;
                    font-size: 12px !important;
                    font-weight: 600 !important;
                    letter-spacing: 0.5px !important;
                    text-transform: uppercase !important;
                    cursor: pointer !important;
                    width: 60% !important;
                    transition: all 0.3s ease !important;
                    font-family: 'Montserrat', sans-serif !important;
                    margin: 0 auto !important;
                    display: block !important;
                }
                button:hover {
                    background-color: #fff !important;
                    color: #f12711 !important;
                    transform: translateY(-2px) !important;
                }
                """
            ):
                if st.button("Sign In", key="toggle_login"):
                    st.session_state.mode = 'login'
                    st.rerun()



# =====================================
# 🤖 CHATBOT BEHAVIOR & AI RESPONSE LOGIC
# =====================================

# Enhanced ask_llama function
RESUME_ASSISTANT_PROMPT = """
You are ResumeBot, a professional resume and career assistant. Your role is to provide concise, actionable advice for resume improvement and career guidance.

CORE RESPONSIBILITIES:
- Analyze resume content and provide specific improvement suggestions
- Guide users on relevant content inclusion based on their industry/role
- Offer formatting and structuring advice
- Suggest better ways to phrase accomplishments
- Help tailor resumes for specific job applications
- Provide career development guidance
- Assist with template selection and customization
- Give interview preparation tips

RESPONSE GUIDELINES:
- Be professional, polite, and encouraging
- Keep responses concise but helpful (3-5 sentences or bullet points)
- Use bullet points for actionable advice when appropriate
- Focus on quantifiable achievements and specific examples
- Ask clarifying questions when needed to provide better guidance
- Never request personal sensitive information
- Tailor advice to the user's mentioned industry/experience level

FORMAT PREFERENCE:
- Use bullet points (•) for lists when helpful
- Use emojis sparingly to make responses engaging
- Keep paragraphs short and scannable
- End with a relevant question to continue conversation when appropriate

Example response style:
• **Quantify achievements**: Instead of "managed team" try "Led 5-person team to achieve 15% productivity increase"
• **Add relevant keywords**: Include "project management" and "stakeholder communication" from job description
• **Improve formatting**: Use consistent bullet points and clear section headers

Always be helpful and specific in your advice!"""

import requests
import json


# Recommended models:
FAST_MODEL = "meta/llama3-8b-instruct"
HEAVY_MODEL = "meta/llama3-70b-instruct"

def ask_llama(message, resume_data=None):
    """
    Stream tokens live + fallback model + optional resume context
    """
    context = f"\nHere is the user's resume:\n{resume_data}\n" if resume_data else ""
    prompt = f"{RESUME_ASSISTANT_PROMPT}{context}\nUser: {message}\nAI:"

    payload = {
        "model": HEAVY_MODEL,  # try high-quality model first
        "messages": [
            {"role": "system", "content": RESUME_ASSISTANT_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,     # faster + less hallucinations
        "max_tokens": 200,      # limit output for speed
        "stream": True
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=35)
    except Exception:
        # Fallback to fast 8B model automatically 👍
        payload["model"] = FAST_MODEL
        response = requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=35)

    # Streaming the reply token by token
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode("utf-8").replace("data:", ""))
                token = data["choices"][0]["delta"].get("content", "")
                if token:
                    yield token
            except:
                pass

    
def chatbot(user_resume):
    import streamlit as st

    # Page config
  
    # Initialize session state for messages
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "bot", "content": "Hello! How can I help you today?", "time": "10:30 AM"},
            {"role": "user", "content": "I need help with my resume", "time": "10:31 AM"},
            {"role": "bot", "content": "I'd be happy to help! Could you provide your basic information", "time": "10:31 AM"},
            {"role": "user", "content": "Sure,", "time": "10:32 AM"},
            {"role": "bot", "content": "Thank you! Let me check that for you...", "time": "10:32 AM"}
        ]

    # Custom CSS for the popover and chat styling
    st.html("""
    <style>
        /* Force popover to bottom right with higher specificity */
        [data-testid="stPopover"],
        div[data-testid="stPopover"],
        section[data-testid="stPopover"] {
            position: fixed !important;
            bottom: 20px !important;
            right: 20px !important;
            left: unset !important;
            top: unset !important;
            z-index: 999999 !important;
            margin: 0 !important;
        }
        
        /* Target the parent container */
        [data-testid="stPopover"] > div {
            position: fixed !important;
            bottom: 20px !important;
            right: 20px !important;
            left: unset !important;
        }
        
        /* Style the popover button */
        [data-testid="stPopover"] button,
        [data-testid="stPopover"] > button {
            width: 60px !important;
            height: 60px !important;
            border-radius: 50% !important;
            background: linear-gradient(135deg, #ff6b00 0%, #ff8c42 100%) !important;
            border: none !important;
            box-shadow: 0 5px 20px rgba(255, 107, 0, 0.4) !important;
            font-size: 28px !important;
            padding: 0 !important;
            transition: all 0.3s ease !important;
        }
        
        [data-testid="stPopover"] button:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 7px 25px rgba(255, 107, 0, 0.5) !important;
        }
        
        /* Style the popover content */
        [data-testid="stPopover"] > div > div,
        [data-testid="stPopoverBody"] {
            background: linear-gradient(135deg, #fff5f0 0%, #ffe8db 100%) !important;
            border: 2px solid #ff8c42 !important;
            border-radius: 20px !important;
            box-shadow: 0 10px 40px rgba(255, 107, 0, 0.25) !important;
            padding: 0 !important;
            width: 380px !important;
            max-width: 380px !important;
            position: fixed !important;
            bottom: 90px !important;
            right: 20px !important;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Chat header styling */
        .chat-header {
            background: linear-gradient(135deg, #ff6b00 0%, #ff8c42 100%);
            padding: 18px 20px;
            color: white;
            font-weight: 600;
            font-size: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
            border-radius: 18px 18px 0 0;
            margin: -1rem -1rem 1rem -1rem;
        }
        
        .chat-icon {
            width: 30px;
            height: 30px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }
        
        /* Message styling */
        .chat-message {
            padding: 12px 16px;
            border-radius: 18px;
            margin-bottom: 12px;
            font-size: 14px;
            line-height: 1.4;
            max-width: 75%;
        }
        
        .chat-message.bot {
            background: white;
            color: #333;
            border: 1px solid #ffd4b8;
            box-shadow: 0 2px 5px rgba(255, 107, 0, 0.1);
            margin-right: auto;
        }
        
        .chat-message.user {
            background: linear-gradient(135deg, #ff6b00 0%, #ff8c42 100%);
            color: white;
            box-shadow: 0 2px 8px rgba(255, 107, 0, 0.3);
            margin-left: auto;
        }
        
        .timestamp {
            font-size: 11px;
            margin-top: 4px;
            opacity: 0.7;
        }
        
        .chat-message.bot .timestamp {
            color: #999;
        }
        
        .chat-message.user .timestamp {
            color: rgba(255, 255, 255, 0.8);
        }
        
        /* Chat messages container */
        .chat-messages-container {
            max-height: 350px;
            overflow-y: auto;
            padding: 10px;
            margin-bottom: 15px;
        }
        
        /* Scrollbar styling */
        .chat-messages-container::-webkit-scrollbar {
            width: 6px;
        }
        
        .chat-messages-container::-webkit-scrollbar-track {
            background: #fff5f0;
        }
        
        .chat-messages-container::-webkit-scrollbar-thumb {
            background: #ff8c42;
            border-radius: 10px;
        }
        
        .chat-messages-container::-webkit-scrollbar-thumb:hover {
            background: #ff6b00;
        }
        
        /* Chat input styling */
        [data-testid="stPopover"] .stChatInput {
            margin-top: 10px;
        }
        
        [data-testid="stPopover"] .stChatInput input {
            border: 2px solid #ff8c42 !important;
            border-radius: 25px !important;
            background: #fff9f5 !important;
        }
        
        [data-testid="stPopover"] .stChatInput input:focus {
            border-color: #ff6b00 !important;
            box-shadow: 0 0 0 3px rgba(255, 107, 0, 0.1) !important;
        }
    </style>

    <script>
        // Force position with JavaScript as backup
        function positionPopover() {
            const popover = document.querySelector('[data-testid="stPopover"]');
            if (popover) {
                popover.style.position = 'fixed';
                popover.style.bottom = '20px';
                popover.style.right = '20px';
                popover.style.left = 'auto';
                popover.style.top = 'auto';
            }
        }
        
        // Run on load and with observer
        window.addEventListener('load', positionPopover);
        setTimeout(positionPopover, 100);
        setTimeout(positionPopover, 500);
        setTimeout(positionPopover, 1000);
        
        // Watch for DOM changes
        const observer = new MutationObserver(positionPopover);
        observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """)


    # Chat popover in bottom right
    with st.popover("💬"):
        # Chat header
        st.markdown("""
        <div class="chat-header">
            <div class="chat-icon">💬</div>
            <span>Chat Assistant</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Messages container
        st.markdown('<div class="chat-messages-container">', unsafe_allow_html=True)
        
        # Display messages
        for msg in st.session_state.messages:
            if msg["role"] == "bot":
                st.markdown(f"""
                <div class="chat-message bot">
                    {msg["content"]}
                    <div class="timestamp">{msg["time"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message user">
                    {msg["content"]}
                    <div class="timestamp">{msg["time"]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input
        # Chat input
        prompt = st.chat_input("Type your message here...")
        if prompt:
            from datetime import datetime
            

            # Add user message
            current_time = datetime.now().strftime("%I:%M %p")
            st.session_state.messages.append({
                "role": "user",
                "content": prompt,
                "time": current_time
            })

            # Call ResumeBot (LLaMA)
            with st.chat_message("assistant"):
                placeholder = st.empty()
                reply = ""
                for token in ask_llama(prompt, user_resume):
                    reply += token
                    placeholder.markdown(reply)

            # Add bot response to UI
            st.session_state.messages.append({
                "role": "bot",
                "content": reply,
                "time": current_time
            })

            st.rerun()



def format_section_title(key):
    """Converts keys like 'certifications' to 'Certifications'."""
    title = key.replace('_', ' ').replace('Skills', ' Skills').replace('summary', 'Summary')
    return ' '.join(word.capitalize() for word in title.split())

def get_standard_keys():
    """Return set of standard resume keys that should not be treated as custom sections."""
    return {
        "name", "email", "phone", "location", "url", "summary", "job_title",
        "education", "experience", "skills", "projects", "certifications", 
        "achievements", "total_experience_count"
    }

def format_year_only(date_str):
    """Return only the year from a date string. If already a year, return as-is."""
    if not date_str:
        return ""
    date_str = str(date_str).strip()
    if len(date_str) == 4 and date_str.isdigit(): 
        return date_str
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y")
    except:
        return date_str  


RESUME_ORDER = ["summary", "experience", "education", "skills", "projects", "certifications", "achievements", "publications", "awards"]

# ATS-friendly color palette
ATS_COLORS = {
    "Professional Blue (Default)": "#1F497D",
    "Corporate Gray": "#4D4D4D",
    "Deep Burgundy": "#800020",
    "Navy Blue": "#000080",
    "Black":"#000000"
}


def generate_generic_html(data, date_placement='right'):
    """Generates clean HTML content based on resume data, showing only years for all dates."""
    if not data: 
        return ""

    job_title_for_header = data.get('job_title', '')
    contacts = [data.get('phone'), data.get('email'), data.get('location')]
    contacts_html = " | ".join([c for c in contacts if c])

    html = f'<div class="ats-header">'
    html += f'<h1>{data.get("name", "NAME MISSING")}</h1>'
    if job_title_for_header:
        html += f'<div class="ats-job-title-header">{job_title_for_header}</div>'
    if contacts_html:
        html += f'<div class="ats-contact">{contacts_html}</div>'
    html += '</div>'

    # Standard sections first
    for key in RESUME_ORDER:
        section_data = data.get(key)
        if not section_data or (isinstance(section_data, list) and not section_data):
            continue

        title = format_section_title(key)
        html += f'<div class="ats-section-title">{title}</div>'

        # Summary
        if key == 'summary' and isinstance(section_data, str) and section_data.strip():
            html += f'<p style="margin-top:0;margin-bottom:5px;">{section_data}</p>'

        # Skills
        elif key == 'skills' and isinstance(section_data, dict):
            for skill_type, skill_list in section_data.items():
                if skill_list:
                    html += f'<div class="ats-skills-group"><strong>{format_section_title(skill_type)}:</strong> {", ".join(skill_list)}</div>'

        elif isinstance(section_data, list):
            for item in section_data:
                # Normalize string items to dict
                if isinstance(item, str) and item.strip():
                    item = {"title": item}
                
                if not isinstance(item, dict):
                    continue

                # Define comprehensive field keys for dynamic handling
                title_keys = ['position', 'title', 'name', 'degree', 'certificate_name', 'course']
                subtitle_keys = ['company', 'institution', 'issuer', 'organization', 'provider_name', 'university']
                duration_keys = ['duration', 'date', 'period', 'completed_date', 'start_date', 'end_date']
                description_keys = ['description', 'achievement', 'details', 'overview']

                # Get main title (first available)
                main_title = None
                for k in title_keys:
                    if k in item and item[k]:
                        main_title = item[k]
                        break
                
                # Get subtitle (first available that's not the same as title)
                subtitle = None
                for k in subtitle_keys:
                    if k in item and item[k] and item[k] != main_title:
                        subtitle = item[k]
                        break

                # Get duration with proper date formatting
                start = format_year_only(item.get('start_date', ''))
                end = format_year_only(item.get('end_date', ''))

                if start or end:
                    duration = f"{start} - {end}" if start and end else start or end
                else:
                    # Try other duration fields
                    duration = None
                    for k in duration_keys:
                        if k in item and item[k]:
                            duration = format_year_only(item[k])
                            break
                    duration = duration or ''

                # Skip completely empty items
                if not main_title and not subtitle and not duration:
                    # Check if there's any description content
                    has_description = False
                    for desc_key in description_keys:
                        if desc_key in item and item[desc_key]:
                            has_description = True
                            break
                    if not has_description:
                        continue

                # Build item HTML
                html += '<div class="ats-item-header">'
                if main_title or subtitle:
                    html += '<div class="ats-item-title-group">'
                    if main_title:
                        html += f'<span class="ats-item-title">{main_title}'
                        if subtitle:
                            html += f' <span class="ats-item-subtitle">{subtitle}</span>'
                        html += '</span>'
                    html += '</div>'
                if duration:
                    html += f'<div class="ats-item-duration">{duration}</div>'
                html += '</div>'

                # Description / Achievements - check all possible description fields
                description_list = None
                for desc_key in description_keys:
                    if desc_key in item and item[desc_key]:
                        description_list_raw = item[desc_key]
                        if isinstance(description_list_raw, str):
                            description_list = [description_list_raw]
                        elif isinstance(description_list_raw, list):
                            description_list = description_list_raw
                        break

                if description_list:
                    bullet_html = "".join([f"<li>{line}</li>" for line in description_list if line and str(line).strip()])
                    if bullet_html:
                        html += f'<ul class="ats-bullet-list">{bullet_html}</ul>'

    # ========== ADD CUSTOM SECTIONS HERE ==========
    standard_keys = get_standard_keys()
    

    for key, value in data.items():
        if key not in standard_keys and isinstance(value, str) and value.strip():
            title = format_section_title(key)
            html += f'<div class="ats-section-title">{title}</div>'
   
            formatted_value = value.strip().replace('\n', '<br>')
            html += f'<p style="margin-top:0;margin-bottom:10px;line-height:1.6;">{formatted_value}</p>'

    return html


SYSTEM_TEMPLATES = {
    "Minimalist (ATS Best)": {
        "html_generator": lambda data: generate_generic_html(data, date_placement='right'),
        "css_generator": get_css_minimalist,
    },
    "Horizontal Line": {
        "html_generator": lambda data: generate_generic_html(data, date_placement='right'),
        "css_generator": get_css_horizontal,
    },
    "Bold Title Accent": {
        "html_generator": lambda data: generate_generic_html(data, date_placement='right'),
        "css_generator": get_css_bold_title,
    },
    "Date Below": {
        "html_generator": lambda data: generate_generic_html(data, date_placement='below'),
        "css_generator": get_css_date_below,
    },
    "Section Box Header": {
        "html_generator": lambda data: generate_generic_html(data, date_placement='right'),
        "css_generator": get_css_section_box,
    },
    "Times New Roman Classic": {
        "html_generator": lambda data: generate_generic_html(data, date_placement='right'),
        "css_generator": get_css_classic,
    },
    "Sohisticated_minimal": {
        "html_generator": lambda data: generate_generic_html(data, date_placement='right'),
        "css_generator": get_css_sophisticated_minimal,
    },
        "Clean look": {
        "html_generator": lambda data: generate_generic_html(data, date_placement='right'),
        "css_generator": get_css_clean_contemporary,
    },
            "Elegant": {
        "html_generator": lambda data: generate_generic_html(data, date_placement='right'),
        "css_generator": get_css_elegant_professional,
    },
            "Mordern Minimal": {
        "html_generator": lambda data: generate_generic_html(data, date_placement='right'),
        "css_generator": get_css_modern_minimal,
    },
    
}


def extract_template_from_html(html_content):
    """Extract CSS and structure from uploaded HTML."""

    css_match = re.search(r'<style[^>]*>(.*?)</style>', html_content, re.DOTALL)
    css = css_match.group(1) if css_match else ""
    
    template_id = hashlib.md5(html_content.encode()).hexdigest()[:8]
    
    return {
        'id': template_id,
        'name': f'Uploaded Template {template_id}',
        'css': css,
        'html': html_content,
        'uploaded_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def generate_html_content(data, color, template_generator, css_generator):
    """Generates the full HTML document and returns base64-encoded string."""
    css = css_generator(color)
    html_content = template_generator(data)
    
    title = f"{data.get('name', 'Resume')}"
    full_document_html = f"<html><head><meta charset='UTF-8'>{css}<title>{title}</title></head><body><div class='ats-page'>{html_content}</div></body></html>" 
    return base64.b64encode(full_document_html.encode('utf-8')).decode()

def get_html_download_link(data, color, template_config, filename_suffix=""):
    """Generates a download link for the styled HTML file."""
    if 'html_generator' in template_config and 'css_generator' in template_config:
        b64_data = generate_html_content(
            data, 
            color, 
            template_config['html_generator'], 
            template_config['css_generator']
        )
    else:
        # For uploaded templates
        css = template_config.get('css', '')
        html_body = generate_generic_html(data)
        full_html = f"<html><head><meta charset='UTF-8'><style>{css}</style></head><body><div class='ats-page'>{html_body}</div></body></html>"
        b64_data = base64.b64encode(full_html.encode('utf-8')).decode()
    
    filename = f"Resume_{data.get('name', 'User').replace(' ', '_')}{filename_suffix}.html"
    href = f'<a href="data:text/html;base64,{b64_data}" download="{filename}" style="font-size: 0.95em; text-decoration: none; padding: 10px 15px; background-color: #0077B6; color: white; border-radius: 5px; display: inline-block; margin-top: 10px; width: 100%; text-align: center;"><strong> HTML (.html)</strong></a>'
    return href



# UPDATED generate_doc_html function
def generate_doc_html(data):
    """Generate a simple HTML that can be saved as .doc."""
    html = f"""
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
    <head>
        <meta charset='utf-8'>
        <title>Resume</title>
        <style>
            @page {{
                size: 8.5in 11in;
                margin: 0.5in;
            }}
            body {{ 
                font-family: Calibri, Arial, sans-serif; 
                font-size: 10pt; 
                line-height: 1.1; 
                margin: 0;
                padding: 0;
            }}
            h1 {{ font-size: 16pt; margin: 0 0 3pt 0; text-align: center; }}
            h2 {{ 
                font-size: 11pt; 
                margin-top: 8pt; 
                margin-bottom: 3pt; 
                border-bottom: 1px solid black; 
                padding-bottom: 1pt;
            }}
            p {{ margin: 3pt 0; }}
            ul {{ margin: 3pt 0; padding-left: 18pt; }}
            li {{ margin: 1pt 0; }}
            .header {{ text-align: center; margin-bottom: 8pt; }}
            .contact {{ font-size: 9pt; }}
            .job-title {{ font-size: 11pt; margin: 2pt 0; color: #555; }}
            .item-header {{ margin: 2pt 0; }}
            .item-title {{ font-weight: bold; }}
            .item-subtitle {{ font-style: italic; color: #555; }}
            .skills-group {{ margin: 3pt 0; }}
            .custom-section {{ margin: 8pt 0; line-height: 1.4; }}
        </style>
    </head>
    <body>
        <div class='header'>
            <h1>{data.get('name', 'NAME MISSING')}</h1>
            <p class='job-title'>{data.get('job_title', '')}</p>
            <p class='contact'>{data.get('phone', '')} | {data.get('email', '')} | {data.get('location', '')}</p>
        </div>
    """
    
    # Standard sections
    for key in RESUME_ORDER:
        section_data = data.get(key)
        
        if not section_data or (isinstance(section_data, list) and not section_data) or (key == 'summary' and not section_data):
            continue
            
        title = format_section_title(key)
        html += f'<h2>{title}</h2>'
        
        if key == 'summary' and isinstance(section_data, str):
            html += f'<p>{section_data}</p>'
        
        elif key == 'skills' and isinstance(section_data, dict):
            for skill_type, skill_list in section_data.items():
                if skill_list:
                    html += f'<p class="skills-group"><strong>{format_section_title(skill_type)}:</strong> '
                    html += ", ".join(skill_list)
                    html += '</p>'
        
        elif isinstance(section_data, list):
            for item in section_data:
                if isinstance(item, str):
                    html += f'<ul><li>{item}</li></ul>'
                    continue
                
                if not isinstance(item, dict):
                    continue
                
                title_keys = ['title', 'name', 'degree', 'position', 'course']
                subtitle_keys = ['company', 'institution', 'issuer', 'organization', 'university']
                duration_keys = ['duration', 'date', 'period']
                
                main_title = next((item[k] for k in title_keys if k in item and item[k]), '')
                subtitle = next((item[k] for k in subtitle_keys if k in item and item[k] != main_title and item[k]), '')
                duration = next((item[k] for k in duration_keys if k in item and item[k]), '')

                html += f'<p class="item-header"><span class="item-title">{main_title}</span>'
                if subtitle:
                    html += f' <span class="item-subtitle">({subtitle})</span>'
                if duration:
                    html += f' | {duration}'
                html += '</p>'
                
                description_list_raw = item.get('description') or item.get('achievement') or item.get('details') 

                if description_list_raw:
                    if isinstance(description_list_raw, str):
                        description_list = [description_list_raw]
                    elif isinstance(description_list_raw, list):
                        description_list = description_list_raw
                    else:
                        description_list = None
                        
                    if description_list:
                        html += '<ul>'
                        for line in description_list:
                            html += f'<li>{line}</li>'
                        html += '</ul>'

    # ========== ADD CUSTOM SECTIONS HERE ==========
    standard_keys = get_standard_keys()
    
    for key, value in data.items():
        if key not in standard_keys and isinstance(value, str) and value.strip():
            title = format_section_title(key)
            html += f'<h2>{title}</h2>'
            # Replace newlines with <br> for proper rendering
            formatted_value = value.strip().replace('\n', '<br>')
            html += f'<p class="custom-section">{formatted_value}</p>'

    html += '</body></html>'
    return html


def get_doc_download_link(data, color, template_config, filename_suffix=""):
    """
    Generates a DOC download link using the selected template's HTML/CSS.

    Note: The 'DOC' file generated is an HTML file with a .doc extension and 
    Microsoft Word-specific XML/CSS (like @page rules) added to the beginning, 
    allowing it to open and be formatted correctly in Word.
    """

    if 'html_generator' in template_config and 'css_generator' in template_config:
        css = template_config['css_generator'](color)
        html_body = template_config['html_generator'](data)
    else:
       
        css = template_config.get('css', '')
        html_body = generate_generic_html(data) #
    word_doc_header = f"""
<html xmlns:o='urn:schemas-microsoft-com:office:office'
xmlns:w='urn:schemas-microsoft-com:office:word'
xmlns='http://www.w3.org/TR/REC-html40'>
<head>
    <meta charset='UTF-8'>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data.get('name', 'Resume')}</title>
    <style>
        @page {{ 
            size: 8.5in 11in; 
            margin: 0.5in; 
        }}
        {css}
    </style>
</head>
<body>
    <div class='ats-page'>
        {html_body}
    </div>
</body>
</html>
"""

   
    try:
        b64_data = base64.b64encode(word_doc_header.encode('utf-8')).decode()
    except NameError:
        print("Error: 'base64' module not found. Please import it.")
        return ""

    filename = f"Resume_{data.get('name', 'User').replace(' ', '_')}_Template_DOC{filename_suffix}.doc"

    doc_html = f"""
    <a href="data:application/msword;base64,{b64_data}" download="{filename}"
       style="font-size: 0.95em; text-decoration: none; padding: 10px 15px; 
              background-color: #00B4D8; color: white; border-radius: 5px; 
              display: inline-block; margin-top: 10px; width: 100%; text-align: center;">
        <strong> Word Document(.doc)</strong>
    </a>
    """
    return doc_html





# UPDATED generate_markdown_text function
def generate_markdown_text(data):
    """Generates a plain markdown/text version of the resume."""
    text = ""
    
    text += f"{data.get('name', 'NAME MISSING').upper()}\n"
    if data.get('job_title'):
        text += f"{data.get('job_title')}\n"
    contact_parts = [data.get('phone', ''), data.get('email', ''), data.get('location', '')]
    text += " | ".join(filter(None, contact_parts)) + "\n"
    text += "=" * 50 + "\n\n"
    
    # Standard sections
    for key in RESUME_ORDER:
        section_data = data.get(key)
        
        if not section_data or (isinstance(section_data, list) and not section_data) or (key == 'summary' and not section_data):
            continue
            
        title = format_section_title(key).upper()
        text += f"{title}\n"
        text += "-" * len(title) + "\n"
        
        if key == 'summary' and isinstance(section_data, str):
            text += section_data + "\n\n"

        elif key == 'skills' and isinstance(section_data, dict):
            for skill_type, skill_list in section_data.items():
                if skill_list:
                    text += f"{format_section_title(skill_type)}: "
                    text += ", ".join(skill_list) + "\n"
            text += "\n"
        
        elif isinstance(section_data, list):
            for item in section_data:
                if not isinstance(item, dict):
                    text += f" - {item}\n"
                    continue
                
                title_keys = ['title', 'name', 'degree', 'position', 'course']
                subtitle_keys = ['company', 'institution', 'issuer', 'university']
                duration_keys = ['duration', 'date']
                
                main_title = next((item[k] for k in title_keys if k in item and item[k]), '')
                subtitle = next((item[k] for k in subtitle_keys if k in item and item[k] != main_title and item[k]), '')
                duration = next((item[k] for k in duration_keys if k in item and item[k]), '')

                line = f"{main_title}"
                if subtitle:
                    line += f" ({subtitle})"
                if duration:
                    line += f" | {duration}"
                text += line + "\n"
                
                description_list = item.get('description') or item.get('achievement') or item.get('details')
                if description_list and isinstance(description_list, list):
                    for line in description_list:
                        text += f" - {line}\n"
            text += "\n"

    # ========== ADD CUSTOM SECTIONS HERE ==========
    standard_keys = get_standard_keys()
    
    for key, value in data.items():
        if key not in standard_keys and isinstance(value, str) and value.strip():
            title = format_section_title(key).upper()
            text += f"{title}\n"
            text += "-" * len(title) + "\n"
            text += value.strip() + "\n\n"

    return text

def get_text_download_link(data, filename_suffix=""):
    """Generates a download link for a plain text file."""
    text_content = generate_markdown_text(data)
    b64_data = base64.b64encode(text_content.encode('utf-8')).decode()
    
    filename = f"Resume_{data.get('name', 'User').replace(' ', '_')}_ATS_Plain_Text{filename_suffix}.txt"
    href = f'<a href="data:text/plain;base64,{b64_data}" download="{filename}" style="font-size: 0.95em; text-decoration: none; padding: 10px 15px; background-color: #40E0D0; color: white; border-radius: 5px; display: inline-block; margin-top: 10px; width: 100%; text-align: center;"><strong> Plain Text (.txt)</strong></a>'
    return href
