import streamlit as st
from utils import extract_text_from_pdf, extract_text_from_docx, extract_details_from_text, get_all_skills_from_llm, get_all_roles_from_llm

# Initialize session state
if "exp_indices" not in st.session_state:
    st.session_state.exp_indices = [0]
if "edu_indices" not in st.session_state:
    st.session_state.edu_indices = [0]
if "cert_indices" not in st.session_state:
    st.session_state.cert_indices = [0]
if "project_indices" not in st.session_state:
    st.session_state.project_indices = [0]

# Custom CSS for improved UI with black, white, grey theme
st.markdown("""
<style>
    /* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Global Styles */
* {
    font-family: 'Inter', sans-serif;
}

/* Main App Background */
.stApp {
    background: linear-gradient(135deg, rgba(0,0,0,0.85) 0%, rgba(26,26,26,0.9) 100%),
                url('https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?q=80&w=1920&auto=format&fit=crop') center/cover fixed;
    min-height: 100vh;
}

/* Main Container - Centralized */
.main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
}

.block-container {
    max-width: 1200px;
    padding: 2rem 3rem;
    margin: 0 auto;
}

/* Header Section - Glassmorphism */
.header-container {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 2.5rem;
    margin-bottom: 2.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.18);
}

/* Title Styling */
h1 {
    color: #FFFFFF !important;
    font-weight: 800 !important;
    margin-bottom: 0.5rem !important;
    font-size: 2.5rem !important;
    letter-spacing: -0.5px !important;
}

/* Subtitle/Welcome Text */
.welcome-text {
    color: #FFFFFF;
    font-size: 1.05rem;
    margin-bottom: 0;
    font-weight: 400;
    line-height: 1.6;
}

.welcome-text strong {
    color: #1a1a1a;
    font-weight: 600;
}

/* Logout Button - Premium Style */
.stButton > button[key="log-outbtn"] {
    background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.1) !important;
    height: auto !important;
    min-width: 120px !important;
    letter-spacing: 0.3px !important;
}

.stButton > button[key="log-outbtn"]:hover {
    background: linear-gradient(135deg, #333333 0%, #1a1a1a 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.15) !important;
}

/* Content Cards - Glassmorphism */
.content-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 2.5rem;
    margin-bottom: 2.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.18);
}

/* Section Headers */
h2 {
    color: #ffffff !important;
    font-weight: 700 !important;
    margin-top: 2.5rem !important;
    margin-bottom: 1.5rem !important;
    font-size: 1.75rem !important;
    letter-spacing: -0.3px !important;
    display: flex;
    align-items: center;
}

h3 {
    color: #1a1a1a !important;
    font-weight: 600 !important;
    margin-top: 1.5rem !important;
    margin-bottom: 1rem !important;
    font-size: 1.25rem !important;
}

/* Section Number Badge */
.section-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
    color: white;
    width: 40px;
    height: 40px;
    border-radius: 12px;
    font-weight: 700;
    font-size: 1.1rem;
    margin-right: 15px;
    box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
}

/* Radio Buttons - Enhanced */
.stRadio > label {
    font-weight: 600 !important;
    color: #ffffff !important;
    font-size: 1.05rem !important;
    margin-bottom: 1rem !important;
}

.stRadio > div {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    padding: 1.5rem;
    border-radius: 16px;
    gap: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.18);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.stRadio > div > label {
    background: rgba(255, 255, 255, 0.5) !important;
    border: 2px solid rgba(26, 26, 26, 0.1) !important;
    border-radius: 12px !important;
    padding: 1rem 2rem !important;
    transition: all 0.3s ease !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    cursor: pointer !important;
}

.stRadio > div > label:hover {
    background: rgba(255, 255, 255, 0.9) !important;
    border-color: #ff6b35 !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(255, 107, 53, 0.15);
}

.stRadio > div > label[data-checked="true"] {
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%) !important;
    border-color: #ff6b35 !important;
    color: white !important;
    box-shadow: 0 4px 16px rgba(255, 107, 53, 0.3);
}

/* Input Fields - Modern & Larger */
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stMultiSelect > div > div,
.stDateInput > div > div > input {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 2px solid rgba(26, 26, 26, 0.1) !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
    color: #1a1a1a !important;
    font-weight: 400 !important;
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > div:focus-within,
.stMultiSelect > div > div:focus-within,
.stDateInput > div > div > input:focus {
    border-color: #ff6b35 !important;
    background: white !important;
    box-shadow: 0 0 0 4px rgba(255, 107, 53, 0.1) !important;
    transform: translateY(-1px);
}

.stTextInput > div > div > input::placeholder {
    color: #9ca3af !important;
    opacity: 1 !important;
}

/* Labels - Enhanced */
.stTextInput > label,
.stSelectbox > label,
.stMultiSelect > label,
.stDateInput > label,
.stRadio > label {
    font-weight: 600 !important;
    color: #ffffff !important;
    font-size: 0.95rem !important;
    margin-bottom: 0.6rem !important;
    letter-spacing: 0.2px !important;
}

/* Experience/Education Cards */
.experience-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(249, 250, 251, 0.95) 100%);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    border: 2px solid rgba(255, 107, 53, 0.1);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    transition: all 0.3s ease;
}

.experience-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    border-color: rgba(255, 107, 53, 0.2);
}

.card-badge {
    color: #ff6b35;
    font-size: 0.9rem;
    font-weight: 700;
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Add Buttons - Eye-catching */
.stButton > button[key^="add_"] {
    background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 1rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2) !important;
    letter-spacing: 0.3px !important;
}

.stButton > button[key^="add_"]:hover {
    background: linear-gradient(135deg, #333333 0%, #1a1a1a 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3) !important;
}

/* Remove Buttons */
.stButton > button[key^="remove_"] {
    background: rgba(255, 68, 68, 0.1) !important;
    color: #dc2626 !important;
    border: 2px solid rgba(220, 38, 38, 0.2) !important;
    border-radius: 10px !important;
    padding: 0.6rem 1rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
}

.stButton > button[key^="remove_"]:hover {
    background: #dc2626 !important;
    color: white !important;
    border-color: #dc2626 !important;
    transform: scale(1.05);
}

/* Submit/Generate Buttons - Hero Style */
.stButton > button[key$="-btn"] {
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 1.25rem 3rem !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 8px 24px rgba(255, 107, 53, 0.35) !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

.stButton > button[key$="-btn"]:hover {
    background: linear-gradient(135deg, #f7931e 0%, #ff6b35 100%) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 32px rgba(255, 107, 53, 0.45) !important;
}

.stButton > button[key$="-btn"]:active {
    transform: translateY(-1px) !important;
}

/* File Uploader - Attractive */
.stFileUploader {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border: 3px dashed rgba(255, 107, 53, 0.3);
    border-radius: 16px;
    padding: 3rem;
    transition: all 0.3s ease;
}

.stFileUploader:hover {
    border-color: #ff6b35;
    background: white;
    box-shadow: 0 8px 24px rgba(255, 107, 53, 0.15);
}

.stFileUploader label {
    color: #1a1a1a !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
}

/* Text Area */
.stTextArea > div > div > textarea {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 2px solid rgba(26, 26, 26, 0.1) !important;
    border-radius: 12px !important;
    font-family: 'Courier New', monospace !important;
    color: #1a1a1a !important;
    font-size: 0.95rem !important;
    padding: 1rem !important;
}

.stTextArea > div > div > textarea:focus {
    border-color: #ff6b35 !important;
    box-shadow: 0 0 0 4px rgba(255, 107, 53, 0.1) !important;
}

/* Divider */
hr {
    border: none !important;
    height: 2px !important;
    background: linear-gradient(90deg, transparent, rgba(255, 107, 53, 0.3), transparent) !important;
    margin: 3rem 0 !important;
}

/* Success/Error Messages */
.stSuccess {
    background: rgba(16, 185, 129, 0.1) !important;
    border: 2px solid #10b981 !important;
    border-radius: 12px !important;
    color: #065f46 !important;
    padding: 1rem 1.5rem !important;
    font-weight: 500 !important;
}

.stError {
    background: rgba(239, 68, 68, 0.1) !important;
    border: 2px solid #ef4444 !important;
    border-radius: 12px !important;
    color: #991b1b !important;
    padding: 1rem 1.5rem !important;
    font-weight: 500 !important;
}

.stWarning {
    background: rgba(245, 158, 11, 0.1) !important;
    border: 2px solid #f59e0b !important;
    border-radius: 12px !important;
    color: #92400e !important;
    padding: 1rem 1.5rem !important;
    font-weight: 500 !important;
}

/* Spinner */
.stSpinner > div {
    border-color: #ff6b35 transparent transparent transparent !important;
}

/* Multi-select Tags */
.stMultiSelect span[data-baseweb="tag"] {
    background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%) !important;
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
    color: white !important;
}

/* Columns Equal Height */
[data-testid="column"] {
    display: flex;
    flex-direction: column;
}

/* Responsive Design */
@media (max-width: 768px) {
    .block-container {
        padding: 1.5rem 1rem;
    }
    
    h1 {
        font-size: 2rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
    }
    
    .section-number {
        width: 35px;
        height: 35px;
        font-size: 1rem;
    }
    
    .experience-card {
        padding: 1.5rem;
    }
}

/* Hide Streamlit Branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Scrollbar Styling */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.1);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #f7931e 0%, #ff6b35 100%);
}
</style>
""", unsafe_allow_html=True)


# Header Section
col1, col2 = st.columns([5, 1])
with col1:
    st.title("Create Your Resume")
    st.markdown(f'<p class="welcome-text">Welcome back, <strong>{st.session_state.get("username", "User")}</strong>! Let\'s build your professional resume.</p>', unsafe_allow_html=True)
with col2:
    if st.button("Logout", key="log-outbtn"):
        st.switch_page("login.py")

st.markdown("<br>", unsafe_allow_html=True)

# Step 1 Header
st.markdown('<h2><span class="section-number">1</span>Choose Input Method</h2>', unsafe_allow_html=True)
input_method = st.radio(
    "How would you like to provide your information?",
    ["Manual Entry", "Upload Resume"],
    horizontal=True
)

user_data = {}
remove_index_edu = None
remove_index_cert = None
remove_index = None
remove_index_project = None
professional_experience = []
education = []
certificate = []
project = []

# Manual Entry Section
if input_method == "Manual Entry":
    st.session_state["input_method"] = input_method
    
    # Personal Information
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h2><span class="section-number">2</span>Personal Information</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name *", placeholder="e.g., John Smith")
        # roles_list = get_all_roles_from_llm()
        # role = st.multiselect(
        #     "Target Role *",
        #     options=roles_list,
        #     help="Select the job role(s) you're targeting"
        # )
        experience = st.text_input("Years of Experience *", placeholder="e.g., 5")
    
    with col2:
        all_skills_list = get_all_skills_from_llm()
        skills = st.multiselect(
            "Your Skills *",
            options=all_skills_list,
            help="Select all relevant skills",
            key="general_skills"
        )
    
    st.markdown("---")
    
    # Professional Experience
    st.markdown('<h2><span class="section-number">3</span>Professional Experience</h2>', unsafe_allow_html=True)
    
    for idx, i in enumerate(st.session_state.exp_indices):
        with st.container():
            st.markdown(f'<div class="experience-card">', unsafe_allow_html=True)
            st.markdown(f'<p class="card-badge">Experience {idx + 1}</p>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                company_name = st.text_input("Company Name", key=f"company_{i}", placeholder="e.g., Google Inc.")
                position_name = st.text_input("Position", key=f"position_{i}", placeholder="e.g., Senior Developer")
                all_skills_list = get_all_skills_from_llm()
                exp_skills = st.multiselect(
                      "Your Skills * (Experience)",
                    options=all_skills_list,
                    help="Select all relevant skills",
                    key="exp_skills" 
                )
            with col2:
                comp_startdate = st.date_input("Start Date", key=f"comp_startdate_{i}")
                comp_enddate = st.date_input("End Date", key=f"comp_enddate_{i}")
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Remove", key=f"remove_exp_{i}"):
                    remove_index = i
            
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
            st.markdown(f'<p class="card-badge">Education {idx + 1}</p>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                course = st.text_input("Course/Degree", placeholder="e.g., Master of Computer Application", key=f"course_{i}")
                university = st.text_input("Institution", placeholder="e.g., Texas University", key=f"university_{i}")
            with col2:
                edu_startdate = st.date_input("Start Date", key=f"edu_start_{i}")
                edu_enddate = st.date_input("End Date", key=f"edu_end_{i}")
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Remove", key=f"remove_edu_{i}"):
                    remove_index_edu = i
            
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
            st.markdown(f'<p class="card-badge">Certification {idx + 1}</p>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                certificate_name = st.text_input("Certificate Name", placeholder="e.g., AWS Solutions Architect", key=f"certificate_{i}")
                provider = st.text_input("Provider", placeholder="e.g., Amazon Web Services", key=f"Provider_{i}")
            with col2:
                comp_date = st.date_input("Completion Date", key=f"comp_date_{i}")
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Remove", key=f"remove_cert_{i}"):
                    remove_index_cert = i
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            certificate.append({
                "certificate_name": certificate_name,
                "provider_name": provider,
                "completed_date": comp_date,
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
            st.markdown(f'<p class="card-badge">Projects {idx + 1}</p>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                projectname = st.text_input("Project Name", placeholder="e.g., Created An Integaration Toll", key=f"projectname_{i}")
                tools = st.text_input("Tools/Languages", placeholder="e.g., PowerBI,SQL", key=f"tools_{i}")
            with col2:
                decription = st.text_input("Description", key=f"decription_{i}")
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
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
            if name and  skills and experience:
                with st.spinner("Processing your resume..."):
                    user_data = {
                        'name': name,
                        'skills': skills,
                        'experience': experience,
                        'professional_experience': professional_experience,
                        'education': education,
                        'certificate': certificate,
                        'project':project
                    }
                    st.session_state.resume_source = user_data
                
                st.success("Resume data saved successfully!")
                st.switch_page("pages/job.py")
            else:
                st.error("Please fill in all required fields marked with *")

# Upload Resume Section
else:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h2><span class="section-number">2</span>Upload Your Resume</h2>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Drop your resume here or click to browse",
        type=["pdf", "docx"],
        help="Supported formats: PDF, DOCX"
    )
    
    if uploaded_file:
        with st.spinner("Extracting data from your file..."):
            if uploaded_file.type == "application/pdf":
                extracted_text = extract_text_from_pdf(uploaded_file)
                # st.json(extracted_text)
            else:
                extracted_text = extract_text_from_docx(uploaded_file)
        
        st.success("File uploaded successfully!")
        st.text_area("Extracted Content", value=extracted_text, height=300)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Process Resume", key="re-btn"):
                if extracted_text:
                    with st.spinner("Analyzing your resume..."):
                        parsed_data = extract_details_from_text(extracted_text)
                    
                    if parsed_data:
                        st.session_state.resume_source = parsed_data
                        st.session_state.resume_processed = True
                        
                        st.success("Resume processed successfully!")
                        st.switch_page("pages/job.py")
                    else:
                        st.error("Failed to process resume. Please try manual entry or upload a different file.")
                else:
                    st.error("Please upload your resume first")