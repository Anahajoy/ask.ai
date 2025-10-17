import streamlit as st
import json
from utils import extract_text_from_pdf, extract_text_from_docx, extract_details_from_jd

# --- Modern Professional Theme CSS ---
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    #MainMenu, footer, header {visibility: hidden;}

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Color Palette Variables */
    :root {
        --primary-blue: #2563eb;
        --primary-blue-dark: #1e40af;
        --primary-blue-light: #3b82f6;
        --accent-cyan: #06b6d4;
        --accent-purple: #8b5cf6;
        --bg-white: #ffffff;
        --bg-gray-50: #f9fafb;
        --bg-gray-100: #f3f4f6;
        --text-black: #111827;
        --text-gray-700: #374151;
        --text-gray-600: #4b5563;
        --text-gray-500: #6b7280;
        --border-gray: #e5e7eb;
        --border-gray-light: #f3f4f6;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* App Background - Clean White */
    .stApp {
        background: linear-gradient(to bottom, #ffffff 0%, #f9fafb 100%);
        background-attachment: fixed;
        min-height: 100vh;
        color: var(--text-black);
    }

    .block-container {
        max-width: 900px;
        padding: 3rem 2rem;
        margin: 0 auto;
    }

    /* Header Section */
    .header-section {
        background: var(--bg-white);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        border: 1px solid var(--border-gray);
        box-shadow: var(--shadow-lg);
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
        background: linear-gradient(90deg, var(--primary-blue), var(--accent-cyan), var(--accent-purple));
    }

    h2 {
        color: var(--text-black) !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 0 !important;
    }

    .step-badge {
        background: linear-gradient(135deg, var(--primary-blue), var(--primary-blue-light));
        color: white;
        width: 48px;
        height: 48px;
        border-radius: 12px;
        text-align: center;
        line-height: 48px;
        font-weight: 700;
        font-size: 1.3rem;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }

    /* Returning User Alert */
    .returning-user-alert {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 1px solid #93c5fd;
        border-left: 4px solid var(--primary-blue);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-md);
    }

    .returning-user-alert h3 {
        color: var(--text-black) !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem;
    }

    .returning-user-alert p {
        color: var(--text-gray-700) !important;
        font-size: 0.95rem;
        line-height: 1.6;
        margin: 0;
    }

    /* Content Container */
    .content-container {
        background: var(--bg-white);
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--border-gray);
    }

    /* Labels - Black Text */
    label, .stApp label, .stRadio label, .stRadio > label, .stTextArea label {
        color: var(--text-black) !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.8rem !important;
        letter-spacing: -0.01em;
    }
    
    /* Radio Button Styling */
    .stRadio > div {
        background: var(--bg-gray-50);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid var(--border-gray);
        gap: 1rem;
    }
    
    .stRadio > div > label {
        background: var(--bg-white);
        border: 2px solid var(--border-gray);
        border-radius: 10px;
        padding: 0.75rem 1.25rem;
        margin: 0.25rem;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .stRadio > div > label:hover {
        border-color: var(--primary-blue);
        background: var(--bg-gray-50);
    }
    
    .stRadio > div > label > div {
        color: var(--text-black) !important;
        font-weight: 500 !important;
    }
    
    .stRadio > div > label > div[data-baseweb="radio"] > div {
        background-color: var(--bg-white) !important;
        border-color: var(--primary-blue) !important;
        border-width: 2px !important;
    }
    
    .stRadio > div > label > div[data-baseweb="radio"] > div:first-child {
        background-color: var(--primary-blue) !important;
    }

    /* Button Styling */
    .stApp .stButton > button,
    .stApp button[class*="stButton"],
    .stApp div.stButton button {
        background: linear-gradient(135deg, var(--primary-blue), var(--primary-blue-light)) !important;
        color: white !important;
        border: none !important;
        box-shadow: var(--shadow-md) !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        min-width: 140px !important;
        transition: all 0.3s ease !important;
        font-size: 0.95rem !important;
    }

    .stApp .stButton > button > div > p,
    .stApp .stButton > button > span,
    .stApp button > div > p {
        color: white !important;
        font-weight: 600 !important;
    }

    .stApp .stButton > button[key="jb-btn"],
    .stApp button[key="jb-btn"] {
        background: linear-gradient(135deg, var(--primary-blue), var(--accent-cyan)) !important;
        width: 100% !important;
        padding: 1rem 2rem !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
    }

    .stApp .stButton > button[key="add-new-resume-btn"],
    .stApp button[key="add-new-resume-btn"] {
        background: var(--bg-white) !important;
        color: var(--primary-blue) !important;
        border: 2px solid var(--primary-blue) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stApp .stButton > button[key="add-new-resume-btn"]:hover,
    .stApp button[key="add-new-resume-btn"]:hover {
        background: var(--bg-gray-50) !important;
        border-color: var(--primary-blue-dark) !important;
    }

    .stApp .stButton > button[key="go-to-main-btn"],
    .stApp button[key="go-to-main-btn"] {
        background: linear-gradient(135deg, var(--primary-blue), var(--primary-blue-light)) !important;
        color: white !important;
    }

    .stApp .stButton > button:hover,
    .stApp button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
    }

    /* Text Areas - White Background with Black Text */
    textarea, .stTextArea > div > div > textarea {
        background: var(--bg-white) !important;
        border: 2px solid var(--border-gray) !important;
        border-radius: 12px !important;
        color: var(--text-black) !important;
        padding: 1rem !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        transition: all 0.2s ease;
        font-weight: 400 !important;
    }
    
    textarea::placeholder {
        color: var(--text-gray-500) !important;
        opacity: 1 !important;
    }

    textarea:focus {
        border-color: var(--primary-blue) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1), var(--shadow-md) !important;
        background: var(--bg-white) !important;
        outline: none !important;
    }
    
    .stTextArea small, .help-text {
        color: var(--text-gray-600) !important;
        font-size: 0.85rem !important;
    }

    /* File Uploader */
    .stFileUploader {
        background: var(--bg-gray-50) !important;
        border: 2px dashed var(--border-gray) !important;
        border-radius: 12px !important;
        padding: 2.5rem !important;
        transition: 0.3s ease;
    }

    .stFileUploader:hover {
        border-color: var(--primary-blue) !important;
        background: var(--bg-white) !important;
        box-shadow: var(--shadow-md);
    }
    
    .stFileUploader label {
        color: var(--text-black) !important;
        font-weight: 600 !important;
    }
    
    .stFileUploader section {
        color: var(--text-gray-600) !important;
    }
    
    .stFileUploader section button {
        background: linear-gradient(135deg, var(--primary-blue), var(--primary-blue-light)) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
    }
    
    .stFileUploader section small {
        color: var(--text-gray-500) !important;
    }

    /* Success/Error Messages */
    .stSuccess, .stError, .stWarning {
        border-radius: 12px !important;
        padding: 1rem 1.2rem !important;
        font-weight: 500;
        border-left: 4px solid;
    }

    .stSuccess {
        background: #f0fdf4 !important;
        border-color: #22c55e !important;
        color: #166534 !important;
    }

    .stError {
        background: #fef2f2 !important;
        border-color: #ef4444 !important;
        color: #991b1b !important;
    }
    
    .stWarning {
        background: #fffbeb !important;
        border-color: #f59e0b !important;
        color: #92400e !important;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--primary-blue) !important;
    }

    /* Help text paragraphs */
    p.help-text {
        color: var(--text-gray-600) !important;
        font-size: 0.875rem;
        margin-top: 0.5rem;
    }

</style>
""", unsafe_allow_html=True)


# Check if user is logged in
if 'logged_in_user' not in st.session_state:
    st.warning("Please login first!")
    st.switch_page("login.py")

# Get resume data from session state
resume_data = st.session_state.get("resume_source", {})
input_method = resume_data.get("input_method", "Manual Entry") 
st.session_state["input_method"] = input_method


# --- Header Section ---
st.markdown('<div class="header-section">', unsafe_allow_html=True)
st.markdown('<h2><span class="step-badge">2</span>Target Job Description</h2>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# --- Returning User Alert ---
resume_source = st.session_state.get("resume_source", None)

if resume_source:
    # st.markdown('<div class="returning-user-alert">', unsafe_allow_html=True)
    st.markdown(f'<p>Your last resume was created. You can proceed with it, or click the button below to start a new resume from scratch.</p>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns([1, 4])
    with col_a: 
        if st.button("Start New Resume", key="add-new-resume-btn"):
            keys_to_delete = ['resume_source', 'enhanced_resume', 'job_description', 
                             'resume_processed', 'exp_indices', 'edu_indices', 'cert_indices', 'project_indices']
            
            for key in keys_to_delete:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.switch_page("../ask.ai/pages/main.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Job Description Input ---
if resume_source is None:
    st.error("No resume data found. Please go back to the main page to upload or enter your data first.")
    if st.button("Go to Resume Builder", key="go-to-main-btn"):
        st.switch_page("../ask.ai/pages/main.py")
else:
    # st.markdown('<div class="content-container">', unsafe_allow_html=True)
    
    jd_method = st.radio(
        "Choose how to provide the job description:",
        ["Type or Paste", "Upload File"],
        horizontal=True,
        key="jd_method_radio"
    )
    
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
            
            if job_description:
                st.text_area(
                    "Extracted Job Description Content (Review before processing)",
                    value=job_description,
                    height=200,
                    help="Preview of the extracted job description"
                )

    else:
        job_description = st.text_area(
            "Paste the Job Description Text *",
            value="",
            height=250,
            placeholder="Paste the complete job description here..."
        )
        
        if job_description:
            word_count = len(job_description.split())
            st.markdown(f'<p class="help-text">Word count: {word_count}</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Continue to Resume Generation ➡️", key="jb-btn"):
            if job_description:
                with st.spinner("Analyzing job description and preparing for tailoring..."):
                    structured_jd = extract_details_from_jd(job_description)
                    
                    if isinstance(structured_jd, str):
                        try:
                            structured_jd = json.loads(structured_jd)
                        except json.JSONDecodeError:
                            structured_jd = {"raw_text": job_description}
                    
                    st.session_state.job_description = structured_jd
                
                st.success("Job description processed successfully!")
                st.switch_page("pages/create.py")
            else:
                st.error("Please provide a job description to continue")
    
    st.markdown('</div>', unsafe_allow_html=True)