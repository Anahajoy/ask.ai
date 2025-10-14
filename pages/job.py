import streamlit as st
import json
from utils import extract_text_from_pdf, extract_text_from_docx, extract_details_from_jd

# Custom CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
     .stApp {
        background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)),
                    url('https://images.unsplash.com/photo-1702835124686-fd1faac06b8d?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=870') center/cover;
        background-attachment: fixed;
    }
  
    
    /* Header section */
    .header-section {
        background: linear-gradient(145deg, #ffffff 0%, #fafafa 100%);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 
            0 10px 40px rgba(0,0,0,0.08),
            0 2px 8px rgba(0,0,0,0.04),
            inset 0 1px 0 rgba(255,255,255,0.8);
        border: 1px solid rgba(0,0,0,0.06);
        position: relative;
        overflow: hidden;
    }
    
    .header-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #1a1a1a, #4a4a4a, #1a1a1a);
        opacity: 0.6;
    }
    
    /* Title styling */
    h2 {
        color: #1a1a1a !important;
        font-weight: 700 !important;
        margin: 0 !important;
        font-size: 1.8rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 1rem !important;
    }
    
    /* Step number badge */
    .step-badge {
        display: inline-block;
        background: linear-gradient(135deg, #2c2c2c 0%, #1a1a1a 100%);
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 12px;
        text-align: center;
        line-height: 40px;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 
            0 4px 12px rgba(0,0,0,0.2),
            inset 0 1px 0 rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Alert box for returning users */
    .returning-user-alert {
        background: linear-gradient(145deg, #fff8e1 0%, #ffecb3 100%);
        border: 2px solid #ffa726;
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 16px rgba(255, 167, 38, 0.2);
    }
    
    .returning-user-alert h3 {
        color: #e65100 !important;
        margin-top: 0 !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }
    
    .returning-user-alert p {
        color: #5d4037;
        margin: 0.5rem 0 1rem 0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Add New Resume button styling */
    .stButton > button[key="add-new-resume-btn"] {
        background: linear-gradient(145deg, #2c2c2c 0%, #1a1a1a 100%) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.1) !important;
        width: 100% !important;
    }
    
    .stButton > button[key="add-new-resume-btn"]:hover {
        background: linear-gradient(145deg, #3d3d3d 0%, #2c2c2c 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    }
    
    /* Content container */
    .content-container {
        background: linear-gradient(145deg, #ffffff 0%, #fafafa 100%);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 
            0 10px 40px rgba(0,0,0,0.08),
            0 2px 8px rgba(0,0,0,0.04),
            inset 0 1px 0 rgba(255,255,255,0.8);
        border: 1px solid rgba(0,0,0,0.06);
    }
    
    /* Radio buttons */
    .stRadio > label {
        font-weight: 600 !important;
        color: #1a1a1a !important;
        font-size: 1rem !important;
        margin-bottom: 1rem !important;
    }
    
    .stRadio > div {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.2rem;
        border-radius: 16px;
        gap: 1rem;
        border: 1px solid rgba(0,0,0,0.08);
        box-shadow: 0 4px 12px rgba(0,0,0,0.06), inset 0 1px 0 rgba(255,255,255,0.5);
    }
    
    .stRadio > div > label {
        background: linear-gradient(145deg, #fafafa 0%, #f0f0f0 100%) !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        border-radius: 12px !important;
        padding: 0.9rem 1.8rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
        font-weight: 500 !important;
    }
    
    .stRadio > div > label:hover {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%) !important;
        border-color: rgba(0,0,0,0.15) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        transform: translateY(-2px) !important;
    }
    
    /* File uploader */
    .stFileUploader {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%) !important;
        border: 2px dashed rgba(0,0,0,0.15) !important;
        border-radius: 16px !important;
        padding: 2.5rem !important;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.04) !important;
        transition: all 0.3s ease !important;
        margin-top: 1rem !important;
    }
    
    .stFileUploader:hover {
        border-color: #1a1a1a !important;
        background: linear-gradient(145deg, #fafafa 0%, #f0f0f0 100%) !important;
        box-shadow: 
            inset 0 2px 8px rgba(0,0,0,0.06),
            0 4px 12px rgba(0,0,0,0.08) !important;
    }
    
    .stFileUploader label {
        color: #666666 !important;
        font-weight: 500 !important;
    }
    
    /* Text area */
    .stTextArea > label {
        font-weight: 600 !important;
        color: #1a1a1a !important;
        font-size: 1rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    .stTextArea > div > div > textarea {
        background: linear-gradient(145deg, #fafafa 0%, #f5f5f5 100%) !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        border-radius: 12px !important;
        font-family: 'Inter', sans-serif !important;
        color: #1a1a1a !important;
        padding: 1rem !important;
        font-size: 0.9rem !important;
        line-height: 1.6 !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.04) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #1a1a1a !important;
        background: linear-gradient(145deg, #ffffff 0%, #fafafa 100%) !important;
        box-shadow: 
            0 0 0 3px rgba(26, 26, 26, 0.08),
            inset 0 2px 4px rgba(0,0,0,0.02) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Submit button */
    .stButton > button[key="jb-btn"] {
        background: linear-gradient(135deg, #2c2c2c 0%, #1a1a1a 100%) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 14px !important;
        padding: 1.1rem 3rem !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        width: 100% !important;
        margin-top: 2rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 
            0 8px 30px rgba(0,0,0,0.2),
            inset 0 1px 0 rgba(255,255,255,0.15) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button[key="jb-btn"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button[key="jb-btn"]:hover::before {
        left: 100%;
    }
    
    .stButton > button[key="jb-btn"]:hover {
        background: linear-gradient(135deg, #3d3d3d 0%, #2c2c2c 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 
            0 12px 40px rgba(0,0,0,0.3),
            inset 0 1px 0 rgba(255,255,255,0.2) !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(145deg, #f0fdf4 0%, #dcfce7 100%) !important;
        border: 1px solid #86efac !important;
        border-radius: 12px !important;
        color: #166534 !important;
        padding: 1rem !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 12px rgba(134, 239, 172, 0.2) !important;
    }
    
    .stError {
        background: linear-gradient(145deg, #fef2f2 0%, #fee2e2 100%) !important;
        border: 1px solid #fca5a5 !important;
        border-radius: 12px !important;
        color: #991b1b !important;
        padding: 1rem !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 12px rgba(252, 165, 165, 0.2) !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #1a1a1a !important;
    }
    
    /* Helper text */
    .help-text {
        color: #666666;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        font-style: italic;
    }
    
    /* Section divider */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0,0,0,0.1), transparent);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Check if user is logged in
if 'logged_in_user' not in st.session_state:
    st.warning("Please login first!")
    st.switch_page("login.py")

# Get input method from session state
resume_data = st.session_state.get("resume_source", {})
input_method = resume_data.get("input_method", "Manual Entry")  # default if missing
st.session_state["input_method"] = input_method


# Header Section
st.markdown('<div class="header-section">', unsafe_allow_html=True)
st.markdown('<h2><span class="step-badge">2</span>Target Job Description</h2>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Check if user has existing resume data (returning user)
resume_source = st.session_state.get("resume_source", None)

if resume_source:
    # Show alert for users with existing resume data
    st.markdown('<div class="returning-user-alert">', unsafe_allow_html=True)
    st.markdown('<h3>👋 Welcome Back!</h3>', unsafe_allow_html=True)
    st.markdown('<p>We found your saved resume data. You can continue with your existing resume or create a new one from scratch.</p>', unsafe_allow_html=True)
    
    if st.button("🔄 Add New Resume Content", key="add-new-resume-btn"):
        # Clear all resume-related session state
        keys_to_delete = ['resume_source', 'enhanced_resume', 'job_description', 
                         'resume_processed', 'exp_indices', 'edu_indices', 'cert_indices']
        
        for key in keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]
        
        # Reset indices to default
        st.session_state.exp_indices = [0]
        st.session_state.edu_indices = [0]
        st.session_state.cert_indices = [0]
        
        st.success("Resume data cleared! Redirecting to create new resume...")
        st.switch_page("pages/main.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Check for resume data
if resume_source is None:
    st.error("No resume data found. Please upload or enter your data first.")
    if st.button("Go to Resume Builder"):
        st.switch_page("pages/main.py")
else:
    # Main content
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    
    # Job description input method
    jd_method = st.radio(
        "Choose how to provide the job description:",
        ["Type or Paste", "Upload File"],
        horizontal=True
    )
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    job_description = ""

    if jd_method == "Upload File":
        jd_file = st.file_uploader(
            "Upload Job Description",
            type=["pdf", "docx"],
            key="jd_upload",
            help="Upload a PDF or DOCX file containing the job description"
        )
        if jd_file:
            with st.spinner("Reading job description..."):
                if jd_file.type == "application/pdf":
                    job_description = extract_text_from_pdf(jd_file)
                else:
                    job_description = extract_text_from_docx(jd_file)
                st.success("Job description uploaded successfully!")
            
            # Show extracted text in a disabled text area
            if job_description:
                st.text_area(
                    "Extracted Content",
                    value=job_description,
                    height=200,
                    disabled=True,
                    help="Preview of the extracted job description"
                )

    else:  # Type or Paste
        job_description = st.text_area(
            "Job Description",
            value="",
            height=250,
            placeholder="Paste the complete job description here...\n\nExample:\nWe are looking for a Senior Software Engineer with 5+ years of experience...",
            help="The AI will analyze this job description and tailor your resume accordingly"
        )
        
        if job_description:
            word_count = len(job_description.split())
            st.markdown(f'<p class="help-text">Word count: {word_count}</p>', unsafe_allow_html=True)

    # Submit button in centered column
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Continue to Resume", key="jb-btn"):
            if job_description:
                with st.spinner("Analyzing job description..."):
                    structured_jd = extract_details_from_jd(job_description)
                    
                    # Handle JSON parsing
                    if isinstance(structured_jd, str):
                        try:
                            structured_jd = json.loads(structured_jd)
                        except json.JSONDecodeError:
                            structured_jd = {"text": structured_jd}
                    
                    st.session_state.job_description = structured_jd
                
                st.success("Job description processed successfully!")
                st.switch_page("pages/create.py")
            else:
                st.error("Please provide a job description to continue")
    
    st.markdown('</div>', unsafe_allow_html=True)