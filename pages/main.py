import streamlit as st
from pathlib import Path
import json
import re
import time # Keep time import for page switch delay

# NOTE: The provided imports (utils functions) are assumed to exist.
from utils import extract_text_from_pdf, extract_text_from_docx, extract_details_from_text, get_all_skills_from_llm, save_user_resume,load_skills_from_json

if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None
# Initialize session state variables
if "exp_indices" not in st.session_state:
    st.session_state.exp_indices = [0]
if "edu_indices" not in st.session_state:
    st.session_state.edu_indices = [0]
if "cert_indices" not in st.session_state:
    st.session_state.cert_indices = [0]
if "project_indices" not in st.session_state:
    st.session_state.project_indices = [0]
    
# IMPORTANT: Add this at the very top of your file (after imports, before any other code)
# This ensures user authentication is checked on every page load
def check_authentication():
    """Check if user is authenticated, redirect to login if not"""
    if 'logged_in_user' not in st.session_state or not st.session_state.logged_in_user:
        st.warning("⚠️ Please login to continue")
        # st.switch_page("login.py") # Commented out so the app runs standalone for review
        # st.stop()

# Call this right after your imports and before any UI code
# check_authentication()  # Uncomment this line to enable auth check


st.markdown("""
<style>
/* Hide default Streamlit UI elements */
[data-testid="stSidebar"] {display: none;}
[data-testid="collapsedControl"] {display: none;}
button[kind="header"] {display: none;}
[data-testid="stSidebarNav"] {display: none;}
#MainMenu, footer, header {visibility: hidden;}

/* Import font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

/* =========================================
   🌿 COLOR PALETTE (New Gradient Edition)
   ========================================= */
:root {
    --primary-gradient: -webkit-linear-gradient(45deg, #00BFFF, #00FF7F) !important;
    --accent-gradient: -webkit-linear-gradient(45deg, #00BFFF, #00FF7F) !important;

    --primary-blue-dark: #009acd;
    --accent-light: #00FF7F;
    --accent-color: #00BFFF;

        --bg-dark: #0a0a0a;
        --bg-darker: #121212;
        --bg-gray: #1a1a1a;
        --text-white: #FFFFFF;
        --text-gray: #e0e0e0;
        --border-gray: #333333;
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.6);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.6);
}

/* =========================================
   🌤️ Background & Layout
   ========================================= */
 * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* Background */
    .stApp {
        background: var(--bg-dark);
        min-height: 100vh;
        color: var(--text-white);
    }


.block-container {
    max-width: 1200px;
    padding: 2rem 3rem;
    margin: 0 auto;
}

/* =========================================
   🧭 Header Section
   ========================================= */
.header-container {
    background: var(--bg-white);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    border: 1px solid var(--border-gray);
    box-shadow: var(--shadow-lg);
    position: relative;
    overflow: hidden;
}

.header-container::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: var(--primary-gradient);
}

/* Titles */
h1 {
    color: var(--text-black) !important;
    font-weight: 800 !important;
    font-size: 2.8rem !important;
    margin-bottom: 0.5rem !important;
    letter-spacing: -0.8px;
}

h2 {
    color: var(--text-black) !important;
    font-weight: 700 !important;
    margin-top: 3rem !important;
    margin-bottom: 1.5rem !important;
    font-size: 2rem !important;
    display: flex;
    align-items: center;
}

/* =========================================
   💠 Section Number Badge
   ========================================= */
.section-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: var(--primary-gradient);
    color: white;
    width: 45px;
    height: 45px;
    border-radius: 14px;
    font-weight: 700;
    font-size: 1.2rem;
    margin-right: 18px;
    box-shadow: 0 4px 20px rgba(0,191,255,0.5);
}

/* =========================================
   📦 Input Fields
   ========================================= */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stMultiSelect > div > div,
.stDateInput > div > div > input {
    background: var(--bg-white) !important;
    border: 2px solid var(--border-gray) !important;
    border-radius: 12px !important;
    padding: 1rem 1.2rem !important;
    color: var(--text-black) !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > div:focus-within,
.stMultiSelect > div > div:focus-within {
    border-color: #00BFFF !important;
    box-shadow: 0 0 0 4px rgba(0,191,255,0.2);
}

/* =========================================
   🧊 Experience Card
   ========================================= */
.experience-card {
    background: rgba(255,255,255,0.95);
    border-radius: 20px;
    padding: 2.5rem;
    margin-bottom: 1.5rem;
    border: 2px solid rgba(0,191,255,0.15);
    box-shadow: 0 8px 30px rgba(0,191,255,0.1);
    transition: all 0.3s ease;
}

.experience-card:hover {
    border-color: rgba(0,255,127,0.3);
    box-shadow: 0 12px 40px rgba(0,255,127,0.25);
}

/* =========================================
   🎨 Buttons
   ========================================= */
.stApp .stButton > button {
    background: var(--primary-gradient) !important;
    color: #ffffff !important;
    border: none !important;
    padding: 0.9rem 1.6rem !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    box-shadow: 0 6px 18px rgba(0,191,255,0.28) !important;
    transition: all 0.3s ease !important;
}

.stApp .stButton > button:hover {
    transform: translateY(-2px);
    filter: brightness(1.05);
}

/* Full-width CTA Buttons */
.stApp .stButton > button[key="man-btn"],
.stApp .stButton > button[key="re-btn"] {
    background: var(--primary-gradient) !important;
    color: #ffffff !important;
    width: 100% !important;
    padding: 1.2rem 2rem !important;
    font-size: 1.1rem !important;
}

/* Remove / Add small buttons */
.stApp .stButton > button[key*="add_"] {
    background: #00BFFF !important;
    color: white !important;
}

.stApp .stButton > button[key*="remove_"] {
    background: #ef4444 !important;
    color: white !important;
}

/* =========================================
   📁 File Uploader
   ========================================= */
.stFileUploader {
    background: rgba(255, 255, 255, 0.9);
    border: 3px dashed #00BFFF;
    border-radius: 20px;
    padding: 4rem 3rem;
    box-shadow: 0 8px 30px rgba(0,191,255,0.2);
    transition: all 0.3s ease;
}

.stFileUploader:hover {
    border-color: #00FF7F;
    box-shadow: 0 12px 40px rgba(0,255,127,0.3);
}

/* =========================================
   🔹 Scrollbar
   ========================================= */
::-webkit-scrollbar {
    width: 12px;
}
::-webkit-scrollbar-track {
    background: rgba(0,191,255,0.1);
}
::-webkit-scrollbar-thumb {
    background: var(--primary-gradient);
    border-radius: 6px;
}
::-webkit-scrollbar-thumb:hover {
    background: -webkit-linear-gradient(180deg, #00FF7F, #00BFFF);
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
    
    # UI CHANGE: Wrap Personal Info in a card
    st.markdown('<div class="experience-card">', unsafe_allow_html=True)
    st.markdown(f'<p class="card-badge">BASIC DETAILS</p>', unsafe_allow_html=True) # Added badge
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name *", placeholder="e.g., John Smith", key="name_input")
        experience = st.text_input("Years of Experience *", placeholder="e.g., 5", key="experience_input")
    
    with col2:
        # Placeholder for utility function call
        all_skills_list = load_skills_from_json()

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
        # UI CHANGE: Ensure each experience is wrapped in its card
        st.markdown(f'<div class="experience-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="card-badge">EXPERIENCE {idx + 1}</p>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 3, 1])
        with col1:
            company_name = st.text_input("Company Name", key=f"company_{i}", placeholder="e.g., Google Inc.")
            position_name = st.text_input("Position", key=f"position_{i}", placeholder="e.g., Senior Developer")

            exp_skills_list = load_skills_from_json()     
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
            # Center the remove button
            col_rm = st.columns([1, 1, 1])[1]
            with col_rm:
                if st.button("Remove", key=f"remove_exp_{i}"):
                    remove_index = i
            
        st.markdown('</div>', unsafe_allow_html=True) # End card
            
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
    
    # UI CHANGE: Center the 'Add More' button
    col_add_exp = st.columns([1, 2, 1])
    with col_add_exp[1]:
        if st.button("+ Add More Experience", key="add_exp", use_container_width=True):
            new_idx = max(st.session_state.exp_indices) + 1 if st.session_state.exp_indices else 0
            st.session_state.exp_indices.append(new_idx)
            st.rerun()
    
    st.markdown("---")


    # Education
    st.markdown('<h2><span class="section-number">4</span>Education</h2>', unsafe_allow_html=True)
    
    for idx, i in enumerate(st.session_state.edu_indices):
        # UI CHANGE: Ensure each education is wrapped in its card
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
            # Center the remove button
            col_rm = st.columns([1, 1, 1])[1]
            with col_rm:
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
    
    # UI CHANGE: Center the 'Add More' button
    col_add_edu = st.columns([1, 2, 1])
    with col_add_edu[1]:
        if st.button("+ Add More Education", key="add_edu", use_container_width=True):
            new_idx = max(st.session_state.edu_indices) + 1 if st.session_state.edu_indices else 0
            st.session_state.edu_indices.append(new_idx)
            st.rerun()
    
    st.markdown("---")
    
    # Certifications
    st.markdown('<h2><span class="section-number">5</span>Certifications</h2>', unsafe_allow_html=True)
    
    for idx, i in enumerate(st.session_state.cert_indices):
        # UI CHANGE: Ensure each certification is wrapped in its card
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
            # Center the remove button
            col_rm = st.columns([1, 1, 1])[1]
            with col_rm:
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
    
    # UI CHANGE: Center the 'Add More' button
    col_add_cert = st.columns([1, 2, 1])
    with col_add_cert[1]:
        if st.button("+ Add More Certification", key="add_cert", use_container_width=True):
            new_idx = max(st.session_state.cert_indices) + 1 if st.session_state.cert_indices else 0
            st.session_state.cert_indices.append(new_idx)
            st.rerun()
    
    st.markdown("---")

    # Projects
    st.markdown('<h2><span class="section-number">6</span>Projects</h2>', unsafe_allow_html=True)
    
    for idx, i in enumerate(st.session_state.project_indices):
        # UI CHANGE: Ensure each project is wrapped in its card
        st.markdown(f'<div class="experience-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="card-badge">PROJECT {idx + 1}</p>', unsafe_allow_html=True)
        
        # Changed columns to [2, 4, 1] to give more space for the description text area
        col1, col2, col3 = st.columns([2, 4, 1]) 
        with col1:
            projectname = st.text_input("Project Name", placeholder="e.g., Created An Integration Tool", key=f"projectname_{i}")
            tools = st.text_input("Tools/Languages", placeholder="e.g., PowerBI, SQL, Python", key=f"tools_{i}")
        with col2:
            # Changed to st.text_area for longer descriptions
            decription = st.text_area("Description (Key achievements)", key=f"decription_{i}", height=150) 
        with col3:
            st.markdown("<br><br>", unsafe_allow_html=True)
            # Center the remove button
            col_rm = st.columns([1, 1, 1])[1]
            with col_rm:
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
    
    # UI CHANGE: Center the 'Add More' button
    col_add_proj = st.columns([1, 2, 1])
    with col_add_proj[1]:
        if st.button("+ Add More Projects", key="add_project", use_container_width=True):
            new_idx = max(st.session_state.project_indices) + 1 if st.session_state.project_indices else 0
            st.session_state.project_indices.append(new_idx)
            st.rerun()
    
    st.markdown("---")
    
    
    # Submit Button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Generate Resume", key="man-btn", use_container_width=True): # Ensure submit button is full width
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
        with st.spinner("File processing..."):
            if uploaded_file.type == "application/pdf":
                extracted_text = extract_text_from_pdf(uploaded_file)
            else:
                extracted_text = extract_text_from_docx(uploaded_file)
        
        st.success("File uploaded and text extracted successfully! Review and click 'Process Resume'.")
        
        # UI CHANGE: Wrap preview in a card/container
        st.markdown('<div class="experience-card" style="padding: 1.5rem;">', unsafe_allow_html=True)
        st.markdown('<h3>Extracted Text Preview</h3>', unsafe_allow_html=True)
        st.text_area("Extracted Content", value=extracted_text, height=300, key="extracted_content_preview", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Process Resume", key="re-btn", use_container_width=True): # Ensure process button is full width
                if extracted_text:
                    # Check if user is logged in BEFORE processing (kept for integrity)
                    if 'logged_in_user' not in st.session_state or not st.session_state.logged_in_user:
                        st.error("⚠️ Session expired. Please login again.")
                        # st.switch_page("login.py")
                        # st.stop()
                    
                    with st.spinner("Analyzing your resume and parsing details..."):
                        try:
                            parsed_data = extract_details_from_text(extracted_text)
                        except Exception as e:
                            st.error(f"Error during detail extraction: {e}")
                            parsed_data = None
                    
                    if parsed_data:
                        # Store in session state FIRST
                        st.session_state.resume_source = parsed_data
                        st.session_state.resume_processed = True
                        st.session_state.input_method = "Upload"  # Store input method
                        
                        # Then save to file
                        save_success = save_user_resume(
                            st.session_state.logged_in_user, 
                            parsed_data, 
                            input_method="Upload"
                        )
                        
                        if save_success:
                            st.success("✅ Resume processed and saved successfully! Redirecting...")
                            
                            # Add a small delay to ensure state is saved
                            time.sleep(0.5)
                            
                            # Switch page
                            st.switch_page("pages/job.py")
                        else:
                            st.error("❌ Failed to save resume. Please try again.")
                    else:
                        st.error("Failed to process resume. Please ensure your file is clean or try manual entry.")
                else:
                    st.error("Please upload your resume first")