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
import fitz  # PyMuPDF
import re
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pptx import Presentation
from pptx.util import Pt
from docx import Document
from docx.shared import RGBColor
import fitz  # PyMuPDF




API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
API_KEY = "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"

url = API_URL
    
headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
# TO EXTRACT DATA FROM THE UPLOADED FILE#

TEMPLATES_DIR = "uploaded_templates.json"


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
    Creates concise, one-page optimized content with simple language.
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

    # --- 2. Flatten skills ---
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

    # --- 5. Rewrite professional summary (concise) ---
    summary_prompt = f"""
    Rewrite this professional summary for a {job_title} position at {jd_data.get('company','')}.
    
    Original summary: {resume_data.get('summary','')}
    Candidate's key experience: {all_exp_desc[:5]}
    Job requirements: {', '.join(required_skills[:10])}
    Key responsibilities: {', '.join(responsibilities[:5])}
    
    Requirements:
    - 2-3 sentences maximum (45 words total)
    - Use simple, clear language - avoid complex words like "spearheaded", "leveraged", "facilitated", "orchestrated"
    - Use simple verbs: built, created, developed, led, managed, improved, designed
    - Focus on skills and achievements that match the job requirements
    - Include metrics if available in original
    - Ensure perfect grammar and spelling
    - Make it ATS-friendly with keywords from job description
    
    Return only the rewritten summary text without any description or labels.
    """
    rewritten_resume["summary"] = call_llm_api(summary_prompt, 150)
    rewritten_resume["job_title"] = job_title

    # --- 6. Rewrite experience (concise and impactful) ---
    if experience:
        # Calculate bullet limits based on experience count for one-page optimization
        total_exp = len(experience)
        bullets_per_role = min(4, max(2, 12 // total_exp)) if total_exp > 0 else 3
        
        exp_prompt = f"""
        Rewrite the experience section for a {job_title} role. Simplify the language and align with job requirements.
        
        Original Experience: {json.dumps(experience)}
        Job Title: {job_title}
        Job Responsibilities: {', '.join(responsibilities[:10])}
        Required Skills: {', '.join(required_skills[:10])}
        Job Summary: {job_summary}
        
        CRITICAL REQUIREMENTS:
        - Keep maximum {bullets_per_role} bullet points per role
        - Each bullet: 15-22 words maximum
        - Simplify complex language: Replace words like "spearheaded", "orchestrated", "leveraged", "facilitated", "utilized" with simple verbs: built, created, developed, led, managed, improved, designed, implemented
        - Start each bullet with a strong action verb
        - Use simple, clear English (avoid jargon and buzzwords)
        - Include numbers and metrics when present in original content
        - Align content with job requirements - emphasize relevant skills and achievements
        - Check grammar and spelling carefully
        - Make it ATS-friendly by incorporating keywords from job description naturally
        - Focus on impact and results that match what the job is looking for
        
        Example transformation:
        BAD: "Spearheaded the design and implementation of scalable ETL pipelines leveraging Azure Data Factory, DBT, and SSIS, culminating in a 30% increase in data processing efficiency"
        GOOD: "Built ETL pipelines using Azure Data Factory, DBT, and SSIS that improved data processing efficiency by 30%"
        
        Return ONLY valid JSON array with this exact structure:
        [{{"position": "", "company": "", "duration": "", "description": ["bullet1", "bullet2"], "overview": ""}}]
        """
        
        rewritten_exp_text = call_llm_api(exp_prompt, 700)
        try:
            json_start = rewritten_exp_text.find('[')
            json_end = rewritten_exp_text.rfind(']') + 1
            rewritten_experience = json.loads(rewritten_exp_text[json_start:json_end])
            
            for exp in rewritten_experience:
                desc = exp.get("description", [])
                
                # Enforce bullet point limits
                if isinstance(desc, list):
                    desc = desc[:bullets_per_role]
                    exp["description"] = desc
                
                if not desc or (isinstance(desc, list) and not any(line.strip() for line in desc)):
                    position = exp.get("position", "Professional")
                    company = exp.get("company", "A Company")
                    placeholder_desc = generate_basic_description(position, company, candidate_skills, bullets_per_role, required_skills, call_llm_api)
                    exp["description"] = placeholder_desc
                    desc = placeholder_desc
                    
                if isinstance(desc, str):
                    exp["description"] = [line.strip() for line in desc.split("\n") if line.strip()][:bullets_per_role]
                    
            rewritten_resume["experience"] = rewritten_experience
        except:
            rewritten_resume["experience"] = experience

    # --- 7. Rewrite projects (simplify and align) ---
    if projects:
        proj_prompt = f"""
        Rewrite the project descriptions to align with {job_title} role requirements. Simplify the language.
        
        Original Projects: {json.dumps(projects)}
        Job Title: {job_title}
        Job Responsibilities: {', '.join(responsibilities[:10])}
        Required Skills: {', '.join(required_skills[:10])}
        
        CRITICAL REQUIREMENTS:
        - Simplify complex language - use simple verbs: built, created, developed, designed, implemented
        - Avoid buzzwords: "leveraged", "spearheaded", "orchestrated", "facilitated", "utilized"
        - Each bullet: 15-22 words maximum
        - Use clear, simple English
        - Highlight technologies and skills that match job requirements
        - Include metrics and results when available
        - Check grammar and spelling carefully
        - Make it ATS-friendly with relevant keywords from job description
        - Focus on achievements and technical skills relevant to the target role
        
        Return ONLY valid JSON array with this structure:
        [{{"name": "", "description": ["bullet1", "bullet2"], "overview": ""}}]
        """
        
        rewritten_proj_text = call_llm_api(proj_prompt, 500)
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
    Analyze and categorize the candidate's skills for a {job_title} role at {jd_data.get('company','')}.
    
    Candidate's Current Skills: {', '.join(candidate_skills[:35])}
    Job Required Skills: {', '.join(required_skills)}
    Job Responsibilities: {', '.join(responsibilities[:8])}
    
    Requirements:
    - Prioritize skills that match job requirements
    - Include relevant candidate skills
    - Add required skills from job description if candidate has related experience
    - Remove outdated or irrelevant skills
    - Organize into these categories: technicalSkills, tools, cloudSkills, softSkills, languages
    - Each category should have 5-10 relevant skills
    - Make skills ATS-friendly by using exact terminology from job description when applicable
    
    Return ONLY a valid JSON object with the five categories above.
    Example: {{"technicalSkills": ["Python", "SQL"], "tools": ["Power BI", "Azure Data Factory"], "cloudSkills": ["Azure", "AWS"], "softSkills": ["Communication", "Problem Solving"], "languages": ["English", "Spanish"]}}
    """
    
    skills_text = call_llm_api(skills_prompt, 350)
    try:
        json_start = skills_text.find('{')
        json_end = skills_text.rfind('}') + 1
        parsed_skills = json.loads(skills_text[json_start:json_end])
        
        # Keep skills organized by category
        categorized_skills = {}
        for k in ["technicalSkills", "tools", "cloudSkills", "softSkills", "languages"]:
            skills_list = parsed_skills.get(k, [])
            if skills_list:
                categorized_skills[k] = skills_list[:10]  # Max 10 skills per category
                
        rewritten_resume["skills"] = categorized_skills
    except:
        rewritten_resume["skills"] = candidate_skills

    return rewritten_resume


def generate_basic_description(position: str, company: str, candidate_skills: list, max_bullets: int, required_skills: list, call_llm_api) -> list:
    """Generate concise bullet points for missing experience descriptions"""
    key_skills = candidate_skills[:5]
    prompt = f"""
    Generate {max_bullets} professional bullet points for a '{position}' role at '{company}'.
    
    Candidate's skills: {', '.join(key_skills)}
    Relevant job skills: {', '.join(required_skills[:5])}
    
    Requirements:
    - Exactly {max_bullets} bullet points
    - 15-20 words per bullet
    - Start with action verbs: built, created, developed, managed, improved, designed
    - Use simple, clear language
    - Include what was done and the impact/result
    - Check grammar carefully
    - Make bullets relevant to both position and required skills
    
    Return ONLY a JSON array of strings.
    Example: ["Built data pipelines using Python to process customer data", "Created Power BI dashboards for sales analytics"]
    """
    
    result = call_llm_api(prompt, 150)
    try:
        json_start = result.find('[')
        json_end = result.rfind(']') + 1
        bullets = json.loads(result[json_start:json_end])
        return bullets[:max_bullets]
    except:
        return [f"Worked on {position} responsibilities using {', '.join(key_skills[:3])}"]


# --- Helper function for LLM API ---
def call_llm_api(prompt: str, max_tokens: int = 200) -> str:
    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {"role": "system", "content": "You are an expert resume writer specializing in ATS-friendly resumes with clear, simple language and perfect grammar."},
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
    Automatically improve resume content with better grammar, simple clear language,
    and professional formatting while preserving all information, using an external API.
    Aligns content with job description when provided.
    """
    
    resume_text = json.dumps(resume_data, indent=2)
    
    # Extract job details if available
    jd_context = ""
    if job_description:
        jd_context = f"""
    **Target Job Context:**
    {job_description}
    
    Use this context to:
    - Emphasize relevant skills and experiences
    - Incorporate job-specific keywords naturally
    - Highlight achievements that match job requirements
    """
    
    prompt = f"""
    Improve the following resume content with focus on clarity, simplicity, and impact.
    {jd_context}
    
    CRITICAL IMPROVEMENTS TO MAKE:
    
    1. **Simplify Language:**
       - Replace complex words with simple, clear alternatives
       - AVOID: spearheaded, leveraged, orchestrated, facilitated, utilized, championed, synergized
       - USE: built, created, developed, led, managed, improved, designed, implemented
       - Keep sentences under 22 words
       - Use 8th grade reading level (clear and direct)
    
    2. **Grammar and Clarity:**
       - Fix ALL grammar, spelling, and punctuation errors
       - Ensure consistent verb tense (past for previous roles, present for current)
       - Remove redundant words and phrases
       - Make every sentence clear and easy to understand
    
    3. **Professional Impact:**
       - Start each bullet with a strong, simple action verb
       - Include numbers and metrics when present
       - Focus on achievements and results, not just duties
       - Make descriptions concise but impactful
    
    4. **ATS Optimization:**
       - Use keywords from job description naturally (if provided)
       - Ensure professional terminology is clear
       - Maintain consistent formatting
    
    5. **Formatting Consistency:**
       - Standardize date formats
       - Consistent capitalization
       - Proper punctuation throughout
    
    **Examples of Good Simplification:**
    
    BAD: "Spearheaded the orchestration of cross-functional stakeholders to synergize deliverables leveraging agile methodologies"
    GOOD: "Led cross-functional teams to deliver projects using Agile, completing 15+ initiatives on time"
    
    BAD: "Utilized advanced data analytics to facilitate strategic decision-making processes"
    GOOD: "Used data analytics to support business decisions, improving forecast accuracy by 25%"
    
    BAD: "Championed the implementation of cutting-edge technological solutions"
    GOOD: "Implemented new technology solutions that reduced processing time by 40%"
    
    STRICT REQUIREMENTS:
    - Keep the EXACT SAME JSON structure
    - Do NOT remove or add any sections
    - Do NOT change facts, dates, company names, or truthful information
    - Only improve the language, grammar, and presentation
    - Preserve all original metrics and achievements
    - Maintain all skills, tools, and technologies mentioned
    
    Resume Data:
    {resume_text}

    Return the improved resume in the EXACT SAME JSON structure with only text content improved.
    Return ONLY valid JSON with no additional text, explanations, or markdown formatting.
    """

    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {
                "role": "system", 
                "content": "You are an expert resume writer specializing in clear, simple, ATS-friendly content with perfect grammar. You improve language while preserving all facts and structure. Return only valid JSON."
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,  # Lower temperature for more consistent, accurate output
        "max_tokens": 5000
    }

    try:
        # Perform API call
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Extract response content
        response_text = result['choices'][0]['message']['content']

        # Extract JSON (robustly handle text wrapping)
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start == -1 or json_end <= json_start:
            st.error("Could not find valid JSON in improved resume response. Using original data.")
            return resume_data

        improved_data = json.loads(response_text[json_start:json_end])
        
        # Validate that key sections are preserved
        required_keys = ['name', 'skills', 'experience']
        for key in required_keys:
            if key in resume_data and key not in improved_data:
                st.warning(f"Key section '{key}' was lost during improvement. Using original data.")
                return resume_data
        
        return improved_data

    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}. Check your API configuration and network connectivity.")
        return resume_data
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON response: {str(e)}. The API may have returned invalid JSON. Using original data.")
        return resume_data
    except KeyError as e:
        st.error(f"Unexpected API response structure. Missing key: {str(e)}. Using original data.")
        return resume_data
    except Exception as e:
        st.error(f"Unexpected error during resume improvement: {str(e)}. Using original data.")
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
    Creates concise content with simple language and perfect grammar.
    """
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
    job_summary = jd_data.get("job_summary", "")
    responsibilities = jd_data.get("responsibilities", [])
    required_skills = jd_data.get("required_skills", [])
    company_name = jd_data.get("company", "")

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

    # -------------------- Generate Experience Descriptions --------------------
    rewritten_experience = []
    all_exp_desc = []
    
    # Calculate bullet limits for one-page optimization
    total_exp = len(merged_experience)
    bullets_per_role = min(4, max(2, 12 // total_exp)) if total_exp > 0 else 3

    for exp in merged_experience:
        position = exp.get("position", "Professional")
        company = exp.get("company", "A Company")
        start_date = exp.get("start_date", "")
        end_date = exp.get("end_date", "")
        exp_skills = exp.get("exp_skills", [])

        exp_prompt = f"""
        Rewrite the professional experience for {resume_data.get('name','')} for a {position} position at {company}.
        Align this with the target {job_title} role at {company_name}.
        
        Duration: {start_date} to {end_date}
        Candidate's skills used in this role: {', '.join(exp_skills)}
        Target job requirements: {', '.join(required_skills[:10])}
        Target job responsibilities: {', '.join(responsibilities[:8])}
        Target job summary: {job_summary}
        
        CRITICAL REQUIREMENTS:
        - Generate exactly {bullets_per_role} bullet points
        - Each bullet: 15-22 words maximum
        - Simplify complex language - use simple action verbs: built, created, developed, led, managed, improved, designed, implemented
        - Avoid buzzwords: "spearheaded", "orchestrated", "leveraged", "facilitated", "utilized", "championed"
        - Start each bullet with a strong action verb
        - Use clear, simple English (8th grade reading level)
        - Naturally incorporate the candidate's skills and achievements
        - Include numbers and metrics when possible
        - Align content with target job requirements - emphasize relevant skills
        - Check grammar and spelling carefully
        - Make it ATS-friendly by using keywords from the target job description
        - Focus on achievements and impact that match what the target job requires
        
        Example transformation:
        BAD: "Spearheaded the orchestration of cross-functional teams to deliver strategic initiatives leveraging agile methodologies"
        GOOD: "Led cross-functional teams to deliver projects using Agile methodology, completing 15+ initiatives on time"
        
        Return ONLY a JSON array with one object: {{"description": ["bullet1", "bullet2", "bullet3"]}}
        """

        rewritten_exp_text = call_llm_api(exp_prompt, 600)

        try:
            json_start = rewritten_exp_text.find('[')
            json_end = rewritten_exp_text.rfind(']') + 1
            rewritten_exp_list = json.loads(rewritten_exp_text[json_start:json_end])
            rewritten_exp_obj = rewritten_exp_list[0] if rewritten_exp_list else {}
            desc = rewritten_exp_obj.get("description", [])
            
            if isinstance(desc, str):
                desc = [line.strip() for line in desc.split("\n") if line.strip()]
            
            # Enforce bullet limit
            desc = desc[:bullets_per_role] if isinstance(desc, list) else desc

            new_exp = {
                "company": company,
                "position": position,
                "start_date": start_date,
                "end_date": end_date,
                "description": desc if desc else [f"Worked as a {position} at {company}."]
            }
            rewritten_experience.append(new_exp)
            all_exp_desc.extend(desc if isinstance(desc, list) else [desc])

        except Exception:
            fallback_desc = [f"Worked as a {position} at {company}, using {', '.join(exp_skills[:3])}."]
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
    Rewrite this professional summary for {resume_data.get('name','')} applying for a {job_title} position at {company_name}.
    
    Original summary: {resume_data.get('summary','')}
    Candidate's key experience: {all_exp_desc[:8]}
    Target job title: {job_title}
    Job requirements: {', '.join(required_skills[:10])}
    Key job responsibilities: {', '.join(responsibilities[:5])}
    Job summary: {job_summary}
    
    CRITICAL REQUIREMENTS:
    - 2-3 sentences maximum (45 words total)
    - Use simple, clear language - avoid complex words like "spearheaded", "leveraged", "facilitated", "orchestrated", "championed"
    - Use simple action verbs: built, created, developed, led, managed, improved, designed
    - Focus on skills and achievements that directly match the target job requirements
    - Include metrics if available in original content
    - Ensure perfect grammar and spelling
    - Make it ATS-friendly with keywords from the target job description
    - Highlight experience and skills most relevant to the {job_title} role
    
    Return only the rewritten summary text without any labels, descriptions, or extra formatting.
    """
    rewritten_resume["summary"] = call_llm_api(summary_prompt, 180)

    # -------------------- Generate Project Descriptions --------------------
    if "project" in resume_data:
        projects = resume_data.get("project", [])
        rewritten_projects = []

        for proj in projects:
            project_name = proj.get("projectname", proj.get("name", "Project"))
            tools_used = proj.get("tools", [])
            original_desc = proj.get("description", proj.get("decription", ""))

            proj_prompt = f"""
            Rewrite this project description to align with a {job_title} role at {company_name}.
            
            Project Name: {project_name}
            Original Description: {original_desc}
            Tools used: {', '.join(tools_used)}
            Target job requirements: {', '.join(required_skills[:10])}
            Target job responsibilities: {', '.join(responsibilities[:8])}
            
            CRITICAL REQUIREMENTS:
            - Simplify complex language - use simple verbs: built, created, developed, designed, implemented
            - Avoid buzzwords: "leveraged", "spearheaded", "orchestrated", "facilitated", "utilized"
            - Each bullet: 15-22 words maximum
            - Use clear, simple English
            - Naturally mention the tools used in the description (don't list them separately)
            - Highlight technologies and skills that match the target job requirements
            - Include metrics and results when available
            - Check grammar and spelling carefully
            - Make it ATS-friendly with relevant keywords from job description
            - Focus on achievements and technical skills relevant to {job_title} role
            
            Return ONLY a JSON array with one object:
            {{
                "name": "{project_name}",
                "description": ["bullet1", "bullet2"],
                "overview": ""
            }}
            """

            rewritten_proj_text = call_llm_api(proj_prompt, 350)

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
                    else [f"Developed {project_name} using {', '.join(tools_used[:3])}."]
                )
                rewritten_projects.append({
                    "name": project_name,
                    "description": fallback_desc,
                    "overview": ""
                })

        rewritten_resume["projects"] = rewritten_projects

    # -------------------- Categorize Skills --------------------
    skills_prompt = f"""
    Analyze and categorize the candidate's skills for a {job_title} role at {company_name}.
    
    Candidate's current skills: {', '.join(candidate_skills[:35])}
    Job required skills: {', '.join(required_skills)}
    Job responsibilities: {', '.join(responsibilities[:8])}
    
    REQUIREMENTS:
    - Prioritize skills that directly match the target job requirements
    - Include relevant candidate skills that align with the role
    - Add required skills from job description if candidate has related experience
    - Remove outdated or irrelevant skills
    - Organize into: technicalSkills, tools, cloudSkills, softSkills, languages
    - Each category: 5-10 most relevant skills
    - Make skills ATS-friendly by using exact terminology from job description when applicable
    - Focus on skills that are valuable for a {job_title} position
    
    Return ONLY a valid JSON object with the five categories.
    Example: {{"technicalSkills": ["Python", "SQL"], "tools": ["Power BI", "Azure Data Factory"], "cloudSkills": ["Azure", "AWS"], "softSkills": ["Communication", "Problem Solving"], "languages": ["English"]}}
    """
    
    skills_text = call_llm_api(skills_prompt, 350)
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

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    pattern = r'^\+?\d{7,15}$'
    return re.match(pattern, phone) is not None


def save_user_resume(email, resume_data, input_method=None):
    """Save or update a user's resume without affecting other users"""
    user_data_file = "user_resume_data.json"

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


import re
from collections import Counter

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
        if cert.get('certificate_name') or cert.get('name'):
            text_parts.append(cert.get('certificate_name') or cert.get('name'))
    
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
        .ats-header-banner {{ 
            background-color: {color};
            padding: 18px 0.5in;
            margin: 0 0 20px 0;
        }}
        .ats-header {{ 
            margin: 0;
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
            color: rgba(255, 255, 255, 0.85);
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
            line-height: 1.1;
        }}
        .ats-item-header-box {{
            background-color: #f5f5f5;
            padding: 6px 10px;
            margin-bottom: 5px;
            border-radius: 3px;
            display: flex;
            justify-content: space-between;
            align-items: center;
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