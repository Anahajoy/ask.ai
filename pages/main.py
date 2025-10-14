import streamlit as st
from utils import extract_text_from_pdf, extract_text_from_docx, extract_details_from_text, get_all_skills_from_llm, save_user_resume


# Initialize session state variables
if "exp_indices" not in st.session_state:
    st.session_state.exp_indices = [0]
if "edu_indices" not in st.session_state:
    st.session_state.edu_indices = [0]
if "cert_indices" not in st.session_state:
    st.session_state.cert_indices = [0]
if "project_indices" not in st.session_state:
    st.session_state.project_indices = [0]

# --- Custom CSS for Black/White/Grey Theme with Tangerine Accent ---
# The background image URL provided is a placeholder. You'll need to update 
# the 'url()' in the .stApp selector below to the actual URL you use for your 
# login page's best background, or a similar image for consistency.
st.markdown("""
<style>
            
/* Hide default Streamlit UI elements */
[data-testid="stSidebar"] {display: none;}
[data-testid="collapsedControl"] {display: none;}
button[kind="header"] {display: none;}
[data-testid="stSidebarNav"] {display: none;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
    
/* Import Google Fonts - Inter is clean and modern */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Global Styles */
* {
    font-family: 'Inter', sans-serif;
}

/* Color Palette Variables */
:root {
    --primary-color: #0d0d0d; /* Deep Black/Dark Grey */
    --secondary-color: #f8f9fa; /* Off-White/Light Grey */
    --accent-color: #ff6b35; /* Burnt Orange/Tangerine */
    --accent-light: #f7931e;
    --text-dark: #1a1a1a;
    --text-light: #FFFFFF;
    --card-bg: rgba(255, 255, 255, 0.08); /* Dark Glassmorphism */
    --card-border: rgba(255, 255, 255, 0.15);
}

/* Main App Background - Replace URL with your preferred image (e.g., a professional, moody landscape/abstract) */
.stApp {
    background: linear-gradient(rgba(0,0,0,0.65), rgba(0,0,0,0.85)),
                url('https://images.unsplash.com/photo-1549491418-2e0e4b8686e5?q=80&w=2670&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D') center/cover;
    background-attachment: fixed;
    min-height: 100vh;
}

/* Main Container - Centralized and controlled width */
.block-container {
    max-width: 1200px;
    padding: 2rem 3rem;
    margin: 0 auto;
}

/* Header Section Styling (Dark Card) */
.header-container {
    background: var(--card-bg);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 2.5rem;
    margin-bottom: 2.5rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    border: 1px solid var(--card-border);
}

/* Title Styling */
h1 {
    color: var(--text-light) !important;
    font-weight: 800 !important;
    margin-bottom: 0.5rem !important;
    font-size: 2.8rem !important;
    letter-spacing: -0.8px !important;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
}

/* Subtitle/Welcome Text */
.welcome-text {
    color: var(--secondary-color);
    font-size: 1.1rem;
    margin-bottom: 0;
    font-weight: 400;
    line-height: 1.6;
}

.welcome-text strong {
    color: var(--accent-color);
    font-weight: 600;
}

/* Logout Button - Minimal/Dark Style */
.stButton > button[key="log-outbtn"] {
    background: var(--card-bg) !important;
    color: var(--secondary-color) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    height: auto !important;
    min-width: 100px !important;
}

.stButton > button[key="log-outbtn"]:hover {
    background: var(--accent-color) !important;
    border-color: var(--accent-color) !important;
    transform: translateY(-2px) !important;
    color: var(--text-light) !important;
    box-shadow: 0 6px 15px rgba(255, 107, 53, 0.3) !important;
}

/* Section Headers (Steps) */
h2 {
    color: var(--text-light) !important;
    font-weight: 700 !important;
    margin-top: 3rem !important;
    margin-bottom: 1.5rem !important;
    font-size: 2rem !important;
    letter-spacing: -0.5px !important;
    display: flex;
    align-items: center;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.4);
}

/* Section Number Badge - Accent Color */
.section-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-light) 100%);
    color: white;
    width: 45px;
    height: 45px;
    border-radius: 14px;
    font-weight: 700;
    font-size: 1.2rem;
    margin-right: 18px;
    box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
    border: 2px solid white;
}

/* Sub-section Headers */
h3 {
    color: var(--text-dark) !important;
    font-weight: 600 !important;
    margin-top: 1.5rem !important;
    margin-bottom: 1rem !important;
    font-size: 1.35rem !important;
}

/* Radio Buttons - Clean and Dark/Light Contrast */
.stRadio > label {
    font-weight: 600 !important;
    color: var(--text-light) !important;
    font-size: 1.05rem !important;
    margin-bottom: 1rem !important;
}

.stRadio > div {
    background: var(--card-bg);
    backdrop-filter: blur(15px);
    padding: 1.5rem;
    border-radius: 16px;
    gap: 1.5rem;
    border: 1px solid var(--card-border);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.stRadio > div > label {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 2px solid var(--card-border) !important;
    border-radius: 12px !important;
    padding: 1rem 2rem !important;
    transition: all 0.3s ease !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    cursor: pointer !important;
    color: var(--secondary-color) !important;
}

.stRadio > div > label:hover {
    background: rgba(255, 255, 255, 0.15) !important;
    border-color: var(--accent-color) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(255, 107, 53, 0.1);
}

.stRadio > div > label[data-checked="true"] {
    background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-light) 100%) !important;
    border-color: var(--accent-color) !important;
    color: white !important;
    box-shadow: 0 4px 16px rgba(255, 107, 53, 0.4);
}

/* Input Fields - Clean Light Background on Dark Card */
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stMultiSelect > div > div,
.stDateInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--secondary-color) !important;
    border: 2px solid rgba(26, 26, 26, 0.1) !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
    color: var(--text-dark) !important;
    font-weight: 400 !important;
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > div:focus-within,
.stMultiSelect > div > div:focus-within,
.stDateInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent-color) !important;
    background: white !important;
    box-shadow: 0 0 0 4px rgba(255, 107, 53, 0.2) !important;
    transform: translateY(-1px);
}

.stTextInput > div > div > input::placeholder {
    color: #9ca3af !important;
    opacity: 1 !important;
}

/* Labels - Light Color for Visibility */
.stTextInput > label,
.stSelectbox > label,
.stMultiSelect > label,
.stDateInput > label,
.stRadio > label,
.stTextArea > label {
    font-weight: 500 !important;
    color: var(--secondary-color) !important;
    font-size: 0.95rem !important;
    margin-bottom: 0.6rem !important;
    letter-spacing: 0.2px !important;
}


/* Experience/Education Cards (The main data entry container) */
.experience-card {
    background: rgba(255, 255, 255, 0.98); /* Near-white background for content forms */
    backdrop-filter: blur(5px);
    border-radius: 16px;
    padding: 2.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.experience-card:hover {
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.card-badge {
    color: var(--accent-color);
    font-size: 0.9rem;
    font-weight: 700;
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Add Buttons - Minimal Dark Style */
.stButton > button[key^="add_"] {
    background: var(--primary-color) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25) !important;
    letter-spacing: 0.3px !important;
}

.stButton > button[key^="add_"]:hover {
    background: var(--accent-color) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4) !important;
}

/* Remove Buttons - Subtle Red */
.stButton > button[key^="remove_"] {
    background: transparent !important;
    color: #dc2626 !important;
    border: 1px solid #dc2626 !important;
    border-radius: 10px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
}

.stButton > button[key^="remove_"]:hover {
    background: #dc2626 !important;
    color: white !important;
    transform: scale(1.02);
}

/* Submit/Generate Buttons - Hero Accent Style */
.stButton > button[key$="-btn"] {
    background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-light) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 1.5rem 3rem !important;
    font-size: 1.2rem !important;
    font-weight: 800 !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 10px 30px rgba(255, 107, 53, 0.45) !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
}

.stButton > button[key$="-btn"]:hover {
    background: linear-gradient(135deg, var(--accent-light) 0%, var(--accent-color) 100%) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 15px 40px rgba(255, 107, 53, 0.6) !important;
}

/* File Uploader - Elegant Dashed Border */
.stFileUploader {
    background: var(--card-bg);
    backdrop-filter: blur(15px);
    border: 3px dashed var(--accent-color);
    border-radius: 16px;
    padding: 4rem 3rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.stFileUploader:hover {
    border-color: white;
    box-shadow: 0 8px 24px rgba(255, 107, 53, 0.2);
}

.stFileUploader label {
    color: var(--secondary-color) !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
}

/* Divider - Minimal */
hr {
    border: none !important;
    height: 1px !important;
    background: rgba(255, 255, 255, 0.2) !important;
    margin: 3rem 0 !important;
}

/* Multi-select Tags - Dark & Clean */
.stMultiSelect span[data-baseweb="tag"] {
    background: var(--primary-color) !important;
    border-radius: 8px !important;
    color: white !important;
    padding: 0.4rem 0.8rem !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}

.stMultiSelect button[aria-label*="Remove"] {
    color: rgba(255, 255, 255, 0.8) !important;
}

.stMultiSelect button[aria-label*="Remove"]:hover {
    color: var(--accent-color) !important;
}

/* Success/Error Messages */
.stSuccess {
    background: rgba(16, 185, 129, 0.15) !important; /* Green */
    border: 2px solid #10b981 !important;
    border-radius: 12px !important;
    color: #10b981 !important;
}

.stError {
    background: rgba(239, 68, 68, 0.15) !important; /* Red */
    border: 2px solid #ef4444 !important;
    border-radius: 12px !important;
    color: #ef4444 !important;
}

.stWarning {
    background: rgba(245, 158, 11, 0.15) !important; /* Yellow */
    border: 2px solid #f59e0b !important;
    border-radius: 12px !important;
    color: #f59e0b !important;
}

.stSuccess, .stError, .stWarning {
    padding: 1rem 1.5rem !important;
    font-weight: 500 !important;
}

/* Scrollbar Styling */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
}

::-webkit-scrollbar-thumb {
    background: var(--accent-color);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--accent-light);
}

</style>
""", unsafe_allow_html=True)


# Header Section (Wrapped in a container for glassmorphism effect)
st.markdown('<div class="header-container">', unsafe_allow_html=True)
col1, col2 = st.columns([5, 1])
with col1:
    st.title("Create Your Resume ✍️")
    # Using st.session_state.get() is safer
    st.markdown(f'<p class="welcome-text">Welcome back, <strong>{st.session_state.get("username", "User")}</strong>! Let\'s build your professional resume.</p>', unsafe_allow_html=True)
with col2:
    # Use a small space for better vertical alignment
    st.markdown('<br>', unsafe_allow_html=True) 
    if st.button("Logout", key="log-outbtn"):
        st.switch_page("login.py")
st.markdown('</div>', unsafe_allow_html=True)


# Main Content starts here

# Step 1 Header
st.markdown('<h2><span class="section-number">1</span>Choose Input Method</h2>', unsafe_allow_html=True)
input_method = st.radio(
    "How would you like to provide your information?",
    ["Manual Entry", "Upload Resume"],
    horizontal=True,
    key="input_method_radio"
)

# Initialize data structures
user_data = {}
professional_experience = []
education = []
certificate = []
project = []

# Initialize index removers
remove_index_edu = None
remove_index_cert = None
remove_index = None
remove_index_project = None

# Manual Entry Section
if input_method == "Manual Entry":
    st.session_state["input_method"] = input_method
    
    # Personal Information
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h2><span class="section-number">2</span>Personal Information</h2>', unsafe_allow_html=True)
    
    # Wrap in a card for styling
    st.markdown('<div class="experience-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name *", placeholder="e.g., John Smith", key="name_input")
        experience = st.text_input("Years of Experience *", placeholder="e.g., 5", key="experience_input")
    
    with col2:
        # Placeholder for utility function call
        # roles_list = get_all_roles_from_llm() 
        # role = st.multiselect("Target Role *", options=roles_list, help="Select the job role(s) you're targeting")
        all_skills_list = ["Python", "JavaScript", "SQL", "Cloud Computing", "Project Management", "Data Analysis"] # Placeholder list
        skills = st.multiselect(
            "Your Core Skills *",
            options=all_skills_list,
            help="Select all relevant skills",
            key="general_skills"
        )
    st.markdown('</div>', unsafe_allow_html=True) # End card
    
    st.markdown("---")
    
    # Professional Experience
    st.markdown('<h2><span class="section-number">3</span>Professional Experience</h2>', unsafe_allow_html=True)
    
    for idx, i in enumerate(st.session_state.exp_indices):
        with st.container():
            st.markdown(f'<div class="experience-card">', unsafe_allow_html=True)
            st.markdown(f'<p class="card-badge">EXPERIENCE {idx + 1}</p>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                company_name = st.text_input("Company Name", key=f"company_{i}", placeholder="e.g., Google Inc.")
                position_name = st.text_input("Position", key=f"position_{i}", placeholder="e.g., Senior Developer")
                
                # Placeholder for utility function call
                # exp_skills_list = get_all_skills_from_llm()
                exp_skills_list = ["Team Leadership", "Frontend", "Backend", "Agile", "DevOps"] # Placeholder list
                exp_skills = st.multiselect(
                    "Skills Used (Experience)",
                    options=exp_skills_list,
                    help="Select skills relevant to this role",
                    key=f"exp_skills_{i}" 
                )
            with col2:
                comp_startdate = st.date_input("Start Date", key=f"comp_startdate_{i}")
                comp_enddate = st.date_input("End Date (Current or Final)", key=f"comp_enddate_{i}")
            with col3:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button("Remove", key=f"remove_exp_{i}"):
                    remove_index = i
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            professional_experience.append({
                "company": company_name,
                "position": position_name,
                'exp_skills':exp_skills,
                "start_date": comp_startdate.strftime("%Y-%m-%d") if comp_startdate else None,
                "end_date": comp_enddate.strftime("%Y-%m-%d") if comp_enddate else None
            })
    
    if remove_index is not None:
        st.session_state.exp_indices.remove(remove_index)
        st.rerun()
    
    if st.button("+ Add More Experience", key="add_exp"):
        new_idx = max(st.session_state.exp_indices) + 1 if st.session_state.exp_indices else 0
        st.session_state.exp_indices.append(new_idx)
        st.rerun()
    
    st.markdown("---")


       
    
    # Education
    st.markdown('<h2><span class="section-number">4</span>Education</h2>', unsafe_allow_html=True)
    
    for idx, i in enumerate(st.session_state.edu_indices):
        with st.container():
            st.markdown(f'<div class="experience-card">', unsafe_allow_html=True)
            st.markdown(f'<p class="card-badge">EDUCATION {idx + 1}</p>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                course = st.text_input("Course/Degree", placeholder="e.g., Master of Computer Application", key=f"course_{i}")
                university = st.text_input("Institution", placeholder="e.g., Texas University", key=f"university_{i}")
            with col2:
                edu_startdate = st.date_input("Start Date", key=f"edu_start_{i}")
                edu_enddate = st.date_input("End Date (Expected or Final)", key=f"edu_end_{i}")
            with col3:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button("Remove", key=f"remove_edu_{i}"):
                    remove_index_edu = i
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            education.append({
                "course": course,
                "university": university,
                "start_date": edu_startdate.strftime("%Y-%m-%d") if edu_startdate else None,
                "end_date": edu_enddate.strftime("%Y-%m-%d") if edu_enddate else None
            })
    
    if remove_index_edu is not None:
        st.session_state.edu_indices.remove(remove_index_edu)
        st.rerun()
    
    if st.button("+ Add More Education", key="add_edu"):
        new_idx = max(st.session_state.edu_indices) + 1 if st.session_state.edu_indices else 0
        st.session_state.edu_indices.append(new_idx)
        st.rerun()
    
    st.markdown("---")
    
    # Certifications
    st.markdown('<h2><span class="section-number">5</span>Certifications</h2>', unsafe_allow_html=True)
    
    for idx, i in enumerate(st.session_state.cert_indices):
        with st.container():
            st.markdown(f'<div class="experience-card">', unsafe_allow_html=True)
            st.markdown(f'<p class="card-badge">CERTIFICATION {idx + 1}</p>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                certificate_name = st.text_input("Certificate Name", placeholder="e.g., AWS Solutions Architect", key=f"certificate_{i}")
                provider = st.text_input("Provider", placeholder="e.g., Amazon Web Services", key=f"Provider_{i}")
            with col2:
                comp_date = st.date_input("Completion Date", key=f"comp_date_{i}")
            with col3:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button("Remove", key=f"remove_cert_{i}"):
                    remove_index_cert = i
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            certificate.append({
                "certificate_name": certificate_name,
                "provider_name": provider,
                "completed_date": comp_date.strftime("%Y-%m-%d") if comp_date else None,
            })
    
    if remove_index_cert is not None:
        st.session_state.cert_indices.remove(remove_index_cert)
        st.rerun()
    
    if st.button("+ Add More Certification", key="add_cert"):
        new_idx = max(st.session_state.cert_indices) + 1 if st.session_state.cert_indices else 0
        st.session_state.cert_indices.append(new_idx)
        st.rerun()
    
    st.markdown("---")

     # Projects
    st.markdown('<h2><span class="section-number">6</span>Projects</h2>', unsafe_allow_html=True)
    
    for idx, i in enumerate(st.session_state.project_indices):
        with st.container():
            st.markdown(f'<div class="experience-card">', unsafe_allow_html=True)
            st.markdown(f'<p class="card-badge">PROJECT {idx + 1}</p>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                projectname = st.text_input("Project Name", placeholder="e.g., Created An Integration Tool", key=f"projectname_{i}")
                tools = st.text_input("Tools/Languages", placeholder="e.g., PowerBI, SQL, Python", key=f"tools_{i}")
            with col2:
                # Changed to st.text_area for longer descriptions
                decription = st.text_area("Description (Key achievements)", key=f"decription_{i}", height=150) 
            with col3:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button("Remove", key=f"remove_project_{i}"):
                    remove_index_project = i
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            project.append({
                "projectname": projectname,
                "tools": tools,
                "decription": decription
            })
    
    if remove_index_project is not None:
        st.session_state.project_indices.remove(remove_index_project)
        st.rerun()
    
    if st.button("+ Add More Projects", key="add_project"):
        new_idx = max(st.session_state.project_indices) + 1 if st.session_state.project_indices else 0
        st.session_state.project_indices.append(new_idx)
        st.rerun()
    
    st.markdown("---")
    
    
    # Submit Button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Generate Resume", key="man-btn"):
            if name and skills and experience:
                with st.spinner("Processing your resume..."):
                    # Filtering out empty entries from lists
                    filtered_experience = [p for p in professional_experience if p["company"] and p["position"]]
                    filtered_education = [e for e in education if e["course"] and e["university"]]
                    filtered_certificate = [c for c in certificate if c["certificate_name"]]
                    filtered_project = [p for p in project if p["projectname"]]
                    
                    user_data = {
                        'name': name,
                        'skills': skills,
                        'experience': experience,
                        'professional_experience': filtered_experience,
                        'education': filtered_education,
                        'certificate': filtered_certificate,
                        'project': filtered_project
                    }

                st.session_state.resume_source = user_data
                st.success("Resume data saved successfully!")

                if 'logged_in_user' in st.session_state:
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
    st.markdown('<h2><span class="section-number">2</span>Upload Your Resume</h2>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Drop your PDF or DOCX resume here or click to browse",
        type=["pdf", "docx"],
        help="Supported formats: PDF, DOCX",
        key="uploader_widget"
    )
    
    if uploaded_file:
        with st.spinner("Extracting data from your file..."):
            if uploaded_file.type == "application/pdf":
                extracted_text = extract_text_from_pdf(uploaded_file)
            else:
                extracted_text = extract_text_from_docx(uploaded_file)
        
        st.success("File uploaded and text extracted successfully!")
        st.markdown('<h3>Extracted Text Preview</h3>', unsafe_allow_html=True)
        st.text_area("Extracted Content", value=extracted_text, height=300, key="extracted_content_preview")
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Process Resume", key="re-btn"):
                if extracted_text:
                    with st.spinner("Analyzing your resume and parsing details..."):
                        # Ensure you have a check for the utility function's behavior
                        try:
                            parsed_data = extract_details_from_text(extracted_text)
                        except Exception as e:
                            st.error(f"Error during detail extraction: {e}")
                            parsed_data = None
                    
                    if parsed_data:
                        st.session_state.resume_source = parsed_data
                        st.session_state.resume_processed = True

                        st.success("Resume processed and details captured successfully!")
                        if 'logged_in_user' in st.session_state:
                            save_success = save_user_resume(st.session_state.logged_in_user, parsed_data, input_method="Upload")
                            if save_success:
                                st.success("Resume data saved to profile!")
                            else:
                                st.warning("Resume created but couldn't save to profile")

                        st.switch_page("pages/job.py")

                    else:
                        st.error("Failed to process resume. Please ensure your file is clean or try manual entry.")
                else:
                    st.error("Please upload your resume first")