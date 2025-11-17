import streamlit as st
from pathlib import Path
import json
from utils import is_valid_email,is_valid_phone
import time

from utils import extract_text_from_pdf, extract_text_from_docx, extract_details_from_text, get_all_skills_from_llm, save_user_resume,load_skills_from_json

if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None

if "exp_indices" not in st.session_state:
    st.session_state.exp_indices = [0]
if "edu_indices" not in st.session_state:
    st.session_state.edu_indices = [0]
if "cert_indices" not in st.session_state:
    st.session_state.cert_indices = [0]
if "project_indices" not in st.session_state:
    st.session_state.project_indices = [0]

if "saved_personal_info" not in st.session_state:
    st.session_state.saved_personal_info = {}
if "saved_experiences" not in st.session_state:
    st.session_state.saved_experiences = {}
if "saved_education" not in st.session_state:
    st.session_state.saved_education = {}
if "saved_certificates" not in st.session_state:
    st.session_state.saved_certificates = {}
if "saved_projects" not in st.session_state:
    st.session_state.saved_projects = {}

def check_authentication():
    if 'logged_in_user' not in st.session_state or not st.session_state.logged_in_user:
        st.warning("⚠️ Please login to continue")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Hide Streamlit elements */
    [data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarNav"] {display: none;}
    #MainMenu, footer, header, button[kind="header"] {visibility: hidden;}
    
    /* Variables */
    :root {
        --peacock-blue: #0891b2;
        --peacock-blue-dark: #0e7490;
        --peacock-blue-light: #06b6d4;
        --bg-dark: #0a0a0a;
        --text-white: #ffffff;
        --text-gray: #a0a0a0;
        --border-gray: #2a2a2a;
    }
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Smooth page transitions */
    .stApp {
        background: #FFFFFF;
        min-height: 100vh;
        color:#000000;
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .block-container {
        max-width: 1200px;
        padding: 2rem 3rem;
        margin: 0 auto;
        animation: slideUp 0.6s ease-out;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Header with gradient shine effect */
    .header-container {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--peacock-blue), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    h1 {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 2.8rem !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.8px;
        text-shadow: 0 2px 10px rgba(8, 145, 178, 0.3);
    }
    
    h2 {
        color: #000000 !important;
        font-weight: 700 !important;
        margin-top: 3rem !important;
        margin-bottom: 1.5rem !important;
        font-size: 2rem !important;
        display: flex;
        align-items: center;
        transition: all 0.3s ease;
    }
    
    h2:hover {
        transform: translateX(5px);
    }
    
    /* Animated section badges */
    .section-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, var(--peacock-blue), var(--peacock-blue-light));
        color: var(--text-white);
        width: 45px;
        height: 45px;
        border-radius: 14px;
        font-weight: 700;
        font-size: 1.2rem;
        margin-right: 18px;
        box-shadow: 0 4px 20px rgba(8, 145, 178, 0.5);
        transition: all 0.3s ease;
    }
    
    h2:hover .section-number {
        transform: scale(1.1) rotate(5deg);
    }
    
    /* Experience cards with hover effects */
    .experience-card {
        background:linear-gradient(135deg, rgba(8, 145, 178, 0.1) 0%, transparent 50%);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 0.03rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .experience-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 50%;
        background: linear-gradient(135deg, rgba(8, 145, 178, 0.1) 0%, transparent 50%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .experience-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 32px rgba(8, 145, 178, 0.25);
        border-color: rgba(8, 145, 178, 0.3);
    }
    
    .experience-card:hover::before {
        opacity: 1;
    }
    
    .card-badge {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        letter-spacing: 1.5px;
        margin-bottom: 1rem !important;
        text-transform: uppercase;
        display: block !important;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Input fields with smooth transitions */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div,
    .stDateInput > div > div > input {
        background: rgba(0, 0, 0, 0.03) !important;
        border: 2px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 1rem 1.2rem !important;
        color: #000000 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > div:focus-within,
    .stMultiSelect > div > div:focus-within {
        background: rgba(8, 145, 178, 0.1) !important;
        border-color: var(--peacock-blue) !important;
        box-shadow: 0 0 0 4px rgba(8, 145, 178, 0.2) !important;
        transform: translateY(-2px);
    }
    
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stMultiSelect label {
        color:#000000 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
        transition: color 0.3s ease;
    }
    
    /* Enhanced button styles */
    .stButton > button {
        background: linear-gradient(135deg, #5390d9, #4ea8de) !important;
        color: var(--text-white) !important;
        border: none !important;
        padding: 0.9rem 1.6rem !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 6px 18px rgba(83, 144, 217, 0.3) !important;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #014f86, #01497c) !important;
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(83, 144, 217, 0.5) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* Remove buttons - distinctive color */
    div[data-testid="stHorizontalBlock"] > div:first-child .stButton > button {
        background: linear-gradient(135deg, #38bdf8, #0ea5e9) !important;
        box-shadow: 0 6px 18px rgba(56, 189, 248, 0.3) !important;
    }
    
    div[data-testid="stHorizontalBlock"] > div:first-child .stButton > button:hover {
        background: linear-gradient(135deg, #4895ef, #4361ee) !important;
        box-shadow: 0 8px 24px rgba(72, 149, 239, 0.5) !important;
    }
    
    /* Save buttons - accent color */
    div[data-testid="stHorizontalBlock"] > div:last-child .stButton > button {
        background: linear-gradient(135deg, #fb7185, #f43f5e) !important;
        box-shadow: 0 6px 18px rgba(251, 113, 133, 0.3) !important;
    }
    
    div[data-testid="stHorizontalBlock"] > div:last-child .stButton > button:hover {
        background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
        box-shadow: 0 8px 24px rgba(220, 38, 38, 0.5) !important;
    }
    
    /* File uploader with animation */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 3px dashed rgba(8, 145, 178, 0.5);
        border-radius: 20px;
        padding: 4rem 3rem;
        transition: all 0.4s ease;
        position: relative;
    }
    
    .stFileUploader::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, var(--peacock-blue), transparent, var(--peacock-blue-light));
        border-radius: 20px;
        opacity: 0;
        transition: opacity 0.4s ease;
        z-index: -1;
    }
    
    .stFileUploader:hover {
        border-color: var(--peacock-blue-light);
        transform: scale(1.02);
    }
    
    .stFileUploader:hover::before {
        opacity: 0.5;
        animation: rotate 3s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Radio buttons */
    .stRadio label {
        color: var(--text-white) !important;
        transition: all 0.3s ease;
    }
    
    .stRadio > div > label:hover {
        transform: translateX(5px);
    }
    
    /* Success/Error messages with animations */
    .stSuccess, .stError, .stWarning {
        animation: slideInRight 0.5s ease-out;
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .stSuccess {
        background: rgba(8, 145, 178, 0.15) !important;
        border-left: 4px solid var(--peacock-blue) !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.15) !important;
        border-left: 4px solid #ef4444 !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.3);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--peacock-blue), var(--peacock-blue-dark));
        border-radius: 6px;
        transition: background 0.3s ease;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, var(--peacock-blue-light), var(--peacock-blue));
    }
    
    /* Loading animation */
    .stSpinner > div {
        border-color: var(--peacock-blue) !important;
        border-top-color: transparent !important;
    }
    
    /* Welcome text animation */
    .welcome-text {
        color: var(--text-gray);
        font-size: 1rem;
        margin: 0;
        animation: fadeInUp 0.8s ease-out 0.2s both;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Logout button */
    div[data-testid="stBaseButton-secondary"] .stButton > button {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 2px solid rgba(239, 68, 68, 0.3) !important;
        color: #ef4444 !important;
    }
    
    div[data-testid="stBaseButton-secondary"] .stButton > button:hover {
        background: rgba(239, 68, 68, 0.2) !important;
        border-color: #ef4444 !important;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)



# st.markdown('<div class="header-container">', unsafe_allow_html=True)
col1, col2 = st.columns([5, 1])
with col1:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem; padding-right: 100px;">
        <h1 style="margin-bottom: 0.5rem;">👤 Add Basic Information </h1>
        <p class="welcome-text" style="text-align: center;">Welcome back, <strong>{}</strong>! Let's add your basic information.</p>
    </div>
""".format(st.session_state.get("username", "User")), unsafe_allow_html=True)
with col2:
    st.markdown('<br>', unsafe_allow_html=True) 
    if st.button("Logout", key="log-outbtn"):
        st.switch_page("login.py")
st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<h2>Choose Input Method</h2>', unsafe_allow_html=True)
input_method = st.radio(
    "How would you like to provide your information?",
    ["Manual Entry", "Upload Resume"],
    horizontal=True,
    key="input_method_radio"
)


user_data = {}
professional_experience = []
education = []
certificate = []
project = []


remove_index_edu = None
remove_index_cert = None
remove_index = None
remove_index_project = None

# Manual Entry Section
if input_method == "Manual Entry":
    st.session_state["input_method"] = input_method
    
    # Personal Information
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h2><span class="section-number">1</span>Personal Information</h2>', unsafe_allow_html=True)
    
    # st.markdown('<div class="experience-card">', unsafe_allow_html=True)
    st.markdown(f'<p class="card-badge">BASIC DETAILS</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name *", placeholder="e.g., John Smith", key="name_input", 
                           value=st.session_state.saved_personal_info.get("name", ""))
        experience = st.text_input("Years of Experience *", placeholder="e.g., 5", key="experience_input",
                                   value=st.session_state.saved_personal_info.get("experience", ""))
        phone = st.text_input("Phone number *", placeholder="e.g., +91 ", key="phone",
                             value=st.session_state.saved_personal_info.get("phone", ""))
        email = st.text_input("email *", placeholder="e.g., google@gmail.com", key="email",
                             value=st.session_state.saved_personal_info.get("email", ""))
        url = st.text_input("linkedin/github", placeholder="e.g., user/linkedin.com", key="url",
                             value=st.session_state.saved_personal_info.get("url", ""))
       
    with col2:
        all_skills_list = load_skills_from_json()
        skills = st.multiselect(
            "Your Core Skills *",
            options=all_skills_list,
            help="Select all relevant skills",
            key="general_skills",
            default=st.session_state.saved_personal_info.get("skills", [])
        )
        location = st.text_input("location *", placeholder="e.g.,New York", key="location",
                             value=st.session_state.saved_personal_info.get("location", ""))
    
  
    col_save = st.columns([1, 2, 1])
    with col_save[1]:
        if st.button("Save Personal Information", key="save_personal", use_container_width=True):
            if name and skills and experience and phone and email:
                if not is_valid_email(email):
                    st.error("Please enter a valid email address")
                elif not is_valid_phone(phone):
                    st.error("Please enter a valid phone number")
                else:
                    st.session_state.saved_personal_info = {
                        "name": name,
                        "skills": skills,
                        "experience": experience,
                        "phone": phone,
                        "email": email,
                        "url":url,
                        "location":location
                    }
                    st.success("✅ Personal information saved!")
            else:
                st.error("Please fill in all required fields marked with *")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Professional Experience
    st.markdown('<h2><span class="section-number">2</span>Professional Experience</h2>', unsafe_allow_html=True)
    
    for idx, i in enumerate(st.session_state.exp_indices):
        # st.markdown(f'<div class="experience-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="card-badge">EXPERIENCE {idx + 1}</p>', unsafe_allow_html=True)
        
        saved_exp = st.session_state.saved_experiences.get(i, {})
        
        col1, col2 = st.columns([3, 3])
        with col1:
            company_name = st.text_input("Company Name", key=f"company_{i}", placeholder="e.g., Google Inc.",
                                        value=saved_exp.get("company", ""))
            position_name = st.text_input("Position", key=f"position_{i}", placeholder="e.g., Senior Developer",
                                         value=saved_exp.get("position", ""))

            exp_skills_list = load_skills_from_json()     
            exp_skills = st.multiselect(
                "Skills Used (Experience)",
                options=exp_skills_list,
                help="Select skills relevant to this role",
                key=f"exp_skills_{i}",
                default=saved_exp.get("exp_skills", [])
            )
        with col2:
            comp_startdate = st.text_input("Start Date (MM/YYYY)", key=f"comp_startdate_{i}", 
                                          placeholder="e.g., 01/2020",
                                          value=saved_exp.get("start_date", ""))
            comp_enddate = st.text_input("End Date (MM/YYYY) or 'Present'", key=f"comp_enddate_{i}", 
                                        placeholder="e.g., 12/2023 or Present",
                                        value=saved_exp.get("end_date", ""))
       
            if comp_startdate and comp_enddate and comp_enddate.lower() != "present":
                try:
                    from datetime import datetime
                    start = datetime.strptime(comp_startdate, "%m/%Y")
                    end = datetime.strptime(comp_enddate, "%m/%Y")
                    if start > end:
                        st.markdown('<p class="date-error">⚠️ Start date must be before end date</p>', unsafe_allow_html=True)
                except:
                    st.markdown('<p class="date-error">⚠️ Use MM/YYYY format</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="button-row">', unsafe_allow_html=True)
        col_save,col_remove = st.columns(2)
        
        with col_remove:
            if st.button(f"Remove Experience {idx + 1}", key=f"remove_exp_{i}", use_container_width=True):
                remove_index = i
                
        with col_save:
            if st.button(f"Save Experience {idx + 1}", key=f"save_exp_{i}", use_container_width=True):
                if company_name and position_name:
                    st.session_state.saved_experiences[i] = {
                        "company": company_name,
                        "position": position_name,
                        "exp_skills": exp_skills,
                        "start_date": comp_startdate,
                        "end_date": comp_enddate
                    }
                    st.success(f"✅ Experience {idx + 1} saved!")
                else:
                    st.error("Please fill in company name and position")
                    
        st.markdown('</div>', unsafe_allow_html=True)
 
        professional_experience.append({
            "company": company_name,
            "position": position_name,
            'exp_skills':exp_skills,
            "start_date": comp_startdate,
            "end_date": comp_enddate
        })
    
    if remove_index is not None:
        st.session_state.exp_indices.remove(remove_index)
        st.rerun()
    
    col_add_exp = st.columns([1, 2, 1])
    with col_add_exp[1]:
        if st.button("+ Add More Experience", key="add_exp", use_container_width=True):
            new_idx = max(st.session_state.exp_indices) + 1 if st.session_state.exp_indices else 0
            st.session_state.exp_indices.append(new_idx)
            st.rerun()
    
    st.markdown("---")

    # Education
    st.markdown('<h2><span class="section-number">3</span>Education</h2>', unsafe_allow_html=True)
    
    for idx, i in enumerate(st.session_state.edu_indices):
        # st.markdown(f'<div class="experience-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="card-badge">EDUCATION {idx + 1}</p>', unsafe_allow_html=True)
        
        saved_edu = st.session_state.saved_education.get(i, {})
        
        col1, col2 = st.columns(2)
        with col1:
            course = st.text_input("Course/Degree", placeholder="e.g., Master of Computer Application", key=f"course_{i}",
                                  value=saved_edu.get("course", ""))
            university = st.text_input("Institution", placeholder="e.g., Texas University", key=f"university_{i}",
                                      value=saved_edu.get("university", ""))
        with col2:
            edu_startdate = st.text_input("Start Date (MM/YYYY)", key=f"edu_start_{i}", 
                                         placeholder="e.g., 08/2018",
                                         value=saved_edu.get("start_date", ""))
            edu_enddate = st.text_input("End Date (MM/YYYY) or 'Present'", key=f"edu_end_{i}", 
                                       placeholder="e.g., 05/2022 or Present",
                                       value=saved_edu.get("end_date", ""))
            
    
            if edu_startdate and edu_enddate and edu_enddate.lower() != "present":
                try:
                    from datetime import datetime
                    start = datetime.strptime(edu_startdate, "%m/%Y")
                    end = datetime.strptime(edu_enddate, "%m/%Y")
                    if start > end:
                        st.markdown('<p class="date-error">⚠️ Start date must be before end date</p>', unsafe_allow_html=True)
                except:
                    st.markdown('<p class="date-error">⚠️ Use MM/YYYY format</p>', unsafe_allow_html=True)
        
     
        st.markdown('<div class="button-row">', unsafe_allow_html=True)
        col_save,col_remove  = st.columns(2)
        
        with col_remove:
            if st.button(f"Remove Education {idx + 1}", key=f"remove_edu_{i}", use_container_width=True):
                remove_index_edu = i
                
        with col_save:
            if st.button(f"Save Education {idx + 1}", key=f"save_edu_{i}", use_container_width=True):
                if course and university:
                    st.session_state.saved_education[i] = {
                        "course": course,
                        "university": university,
                        "start_date": edu_startdate,
                        "end_date": edu_enddate
                    }
                    st.success(f"✅ Education {idx + 1} saved!")
                else:
                    st.error("Please fill in course and institution")
                    
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
            
        education.append({
            "course": course,
            "university": university,
            "start_date": edu_startdate,
            "end_date": edu_enddate
        })
    
    if remove_index_edu is not None:
        st.session_state.edu_indices.remove(remove_index_edu)
        st.rerun()
    
    col_add_edu = st.columns([1, 2, 1])
    with col_add_edu[1]:
        if st.button("+ Add More Education", key="add_edu", use_container_width=True):
            new_idx = max(st.session_state.edu_indices) + 1 if st.session_state.edu_indices else 0
            st.session_state.edu_indices.append(new_idx)
            st.rerun()
    
    st.markdown("---")
    
    # Certifications
    st.markdown('<h2><span class="section-number">4</span>Certifications</h2>', unsafe_allow_html=True)
    
    for idx, i in enumerate(st.session_state.cert_indices):
        # st.markdown(f'<div class="experience-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="card-badge">CERTIFICATION {idx + 1}</p>', unsafe_allow_html=True)
        
        saved_cert = st.session_state.saved_certificates.get(i, {})
        
        col1, col2 = st.columns(2)
        with col1:
            certificate_name = st.text_input("Certificate Name", placeholder="e.g., AWS Solutions Architect", key=f"certificate_{i}",
                                            value=saved_cert.get("certificate_name", ""))
            provider = st.text_input("Provider", placeholder="e.g., Amazon Web Services", key=f"Provider_{i}",
                                    value=saved_cert.get("provider_name", ""))
        with col2:
            comp_date = st.text_input("Completion Date (MM/YYYY)", key=f"comp_date_{i}", 
                                     placeholder="e.g., 06/2023",
                                     value=saved_cert.get("completed_date", ""))
     
        st.markdown('<div class="button-row">', unsafe_allow_html=True)
        col_save,col_remove = st.columns(2)
        
        with col_remove:
            if st.button(f"Remove Certification {idx + 1}", key=f"remove_cert_{i}", use_container_width=True):
                remove_index_cert = i
                
        with col_save:
            if st.button(f"Save Certification {idx + 1}", key=f"save_cert_{i}", use_container_width=True):
                if certificate_name and provider:
                    st.session_state.saved_certificates[i] = {
                        "certificate_name": certificate_name,
                        "provider_name": provider,
                        "completed_date": comp_date
                    }
                    st.success(f"✅ Certification {idx + 1} saved!")
                else:
                    st.error("Please fill in certificate name and provider")
                    
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
            
        certificate.append({
            "certificate_name": certificate_name,
            "provider_name": provider,
            "completed_date": comp_date
        })
    
    if remove_index_cert is not None:
        st.session_state.cert_indices.remove(remove_index_cert)
        st.rerun()
    
    col_add_cert = st.columns([1, 2, 1])
    with col_add_cert[1]:
        if st.button("+ Add More Certification", key="add_cert", use_container_width=True):
            new_idx = max(st.session_state.cert_indices) + 1 if st.session_state.cert_indices else 0
            st.session_state.cert_indices.append(new_idx)
            st.rerun()
    
    st.markdown("---")

    # Projects
    st.markdown('<h2><span class="section-number">5</span>Projects</h2>', unsafe_allow_html=True)
    
    for idx, i in enumerate(st.session_state.project_indices):
        # st.markdown(f'<div class="experience-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="card-badge">PROJECT {idx + 1}</p>', unsafe_allow_html=True)
        
        saved_proj = st.session_state.saved_projects.get(i, {})
        
        col1, col2 = st.columns(2)
        with col1:
            projectname = st.text_input("Project Name", placeholder="e.g., Created An Integration Tool", key=f"projectname_{i}",
                                       value=saved_proj.get("projectname", ""))
            tools = st.text_input("Tools/Languages", placeholder="e.g., PowerBI, SQL, Python", key=f"tools_{i}",
                                 value=saved_proj.get("tools", ""))
        with col2:
            decription = st.text_area("Description (Key achievements)", key=f"decription_{i}", height=150,
                                     value=saved_proj.get("decription", ""))
     
        st.markdown('<div class="button-row">', unsafe_allow_html=True)
        col_save,col_remove = st.columns(2)
        
        with col_remove:
            if st.button(f"Remove Project {idx + 1}", key=f"remove_project_{i}", use_container_width=True):
                remove_index_project = i
                
        with col_save:
            if st.button(f"Save Project {idx + 1}", key=f"save_project_{i}", use_container_width=True):
                if projectname:
                    st.session_state.saved_projects[i] = {
                        "projectname": projectname,
                        "tools": tools,
                        "decription": decription
                    }
                    st.success(f"✅ Project {idx + 1} saved!")
                else:
                    st.error("Please fill in project name")
                    
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
            
        project.append({
            "projectname": projectname,
            "tools": tools,
            "decription": decription
        })
    
    if remove_index_project is not None:
        st.session_state.project_indices.remove(remove_index_project)
        st.rerun()
    
    col_add_proj = st.columns([1, 2, 1])
    with col_add_proj[1]:
        if st.button("+ Add More Projects", key="add_project", use_container_width=True):
            new_idx = max(st.session_state.project_indices) + 1 if st.session_state.project_indices else 0
            st.session_state.project_indices.append(new_idx)
            st.rerun()
    
    st.markdown("---")

    # -------------------------------
    # 6. Custom / Additional Sections
    # -------------------------------
    st.markdown('<h2><span class="section-number">6</span>Custom Sections</h2>', unsafe_allow_html=True)

    # Initialize session variables
    if "custom_indices" not in st.session_state:
        st.session_state.custom_indices = [0]
    if "saved_custom_sections" not in st.session_state:
        st.session_state.saved_custom_sections = {}

    remove_index_custom = None
    custom_sections = []

    for idx, i in enumerate(st.session_state.custom_indices):
        # st.markdown(f'<div class="experience-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="card-badge">CUSTOM SECTION {idx + 1}</p>', unsafe_allow_html=True)

        saved_custom = st.session_state.saved_custom_sections.get(i, {})
        
        col1, col2 = st.columns([1, 1])
        with col1:
            section_title = st.text_input("Section Heading *", placeholder="e.g., Languages, Achievements, Interests", 
                                        key=f"custom_title_{i}", value=saved_custom.get("title", ""))
        with col2:
            section_description = st.text_area("Description / Details *", placeholder="Add details for this section...", 
                                            key=f"custom_desc_{i}", height=120,
                                            value=saved_custom.get("description", ""))

        # Save/Remove Buttons
        st.markdown('<div class="button-row">', unsafe_allow_html=True)
        col_save ,col_remove= st.columns(2)
        with col_remove:
            if st.button(f"Remove Custom Section {idx + 1}", key=f"remove_custom_{i}", use_container_width=True):
                remove_index_custom = i

        with col_save:
            if st.button(f"Save Custom Section {idx + 1}", key=f"save_custom_{i}", use_container_width=True):
                if section_title and section_description:
                    st.session_state.saved_custom_sections[i] = {
                        "title": section_title,
                        "description": section_description
                    }
                    st.success(f"✅ Custom Section {idx + 1} saved!")
                else:
                    st.error("Please fill in both the heading and description fields.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        custom_sections.append({
            "title": section_title,
            "description": section_description
        })

    # Remove section if needed
    if remove_index_custom is not None:
        st.session_state.custom_indices.remove(remove_index_custom)
        st.rerun()

    # Add more custom sections
    col_add_custom = st.columns([1, 2, 1])
    with col_add_custom[1]:
        if st.button("+ Add Custom Section", key="add_custom", use_container_width=True):
            new_idx = max(st.session_state.custom_indices) + 1 if st.session_state.custom_indices else 0
            st.session_state.custom_indices.append(new_idx)
            st.rerun()

    st.markdown("---")

    
    # Submit Button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Continue", key="man-btn", use_container_width=True):
            st.balloons()
            if not is_valid_email(email):
                st.error("Please enter a valid email address")
            elif not is_valid_phone(phone):
                st.error("Please enter a valid phone number")
            else:
                if name and skills and experience:
                    with st.spinner("Processing your resume..."):
                        filtered_experience = [p for p in professional_experience if p["company"] and p["position"]]
                        filtered_education = [e for e in education if e["course"] and e["university"]]
                        filtered_certificate = [c for c in certificate if c["certificate_name"]]
                        filtered_project = [p for p in project if p["projectname"]]
                        
                        user_data = {
                            'name': name,
                            'skills': skills,
                            'experience': experience,
                            'phone':phone,
                            'email': email,
                            'url':url,
                            'location':location,
                            'professional_experience': filtered_experience,
                            'education': filtered_education,
                            'certificate': filtered_certificate,
                            'project': filtered_project,
                            'custom_sections': {
                                c["title"]: c["description"]
                                for c in custom_sections
                                if c["title"] and c["description"]
                            }
     
                        }

                    st.session_state.resume_source = user_data
                    # st.success("Resume data saved successfully!")
                    st.write(user_data)

                    if 'logged_in_user' in st.session_state:
                        st.session_state.input_method = "Manual Entry" 
                        save_success = save_user_resume(st.session_state.logged_in_user, user_data, input_method="Manual Entry")
                        if save_success:
                            st.success("Resume processed and saved to profile!")
                        else:
                            st.warning("Resume processed but couldn't save to profile")

                    st.switch_page("pages/job.py")
                else:
                    st.error("Please fill in all required fields marked with *")

# Upload Resume Section
else:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h2>Upload Your Resume</h2>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Drop your PDF or DOCX resume here or click to browse",
        type=["pdf", "docx"],
        help="Supported formats: PDF, DOCX",
        key="uploader_widget"
    )
    
    if uploaded_file:
        with st.spinner("File processing..."):
            if uploaded_file.type == "application/pdf":
                extracted_text = extract_text_from_pdf(uploaded_file)
            else:
                extracted_text = extract_text_from_docx(uploaded_file)
        
        # st.markdown('<div class="experience-card" style="padding: 1.5rem;">', unsafe_allow_html=True)
        st.markdown('<h3>Extracted Text Preview</h3>', unsafe_allow_html=True)
        st.text_area("Extracted Content", value=extracted_text, height=300, key="extracted_content_preview", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Process Resume", key="re-btn", use_container_width=True):
                if extracted_text:
                    if 'logged_in_user' not in st.session_state or not st.session_state.logged_in_user:
                        st.error("⚠️ Session expired. Please login again.")
                        
                        st.switch_page("login.py")
                    
                    with st.spinner("Analyzing your resume and parsing details..."):
                        try:
                            parsed_data = extract_details_from_text(extracted_text)
                        except Exception as e:
                            st.error(f"Error during detail extraction: {e}")
                            parsed_data = None
                    
                    if parsed_data:
                        st.session_state.resume_source = parsed_data
                        st.session_state.resume_processed = True
                        st.session_state.input_method = "Upload Entry"
                        
                        save_success = save_user_resume(
                            st.session_state.logged_in_user, 
                            parsed_data, 
                            input_method="Upload Entry"
                        )
                        
                        if save_success:
                            st.success("✅ Resume processed and saved successfully! Redirecting...")
                            time.sleep(0.5)
                            st.switch_page("pages/job.py")
                        else:
                            st.error("❌ Failed to save resume. Please try again.")
                    else:
                        st.error("Failed to process resume. Please ensure your file is clean or try manual entry.")
                else:
                    st.error("Please upload your resume first")