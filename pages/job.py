import streamlit as st
import json
from utils import extract_text_from_pdf, extract_text_from_docx, extract_details_from_jd

# --- Modern Dark Professional Theme CSS ---
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    #MainMenu, footer, header {visibility: hidden;}

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --accent-gradient: -webkit-linear-gradient(45deg, #00BFFF, #00FF7F);
        --accent-solid1: #00BFFF;
        --accent-solid2: #00FF7F;

        --bg-dark: #0a0a0a;
        --bg-darker: #121212;
        --bg-gray: #1a1a1a;
        --text-white: #FFFFFF;
        --text-gray: #e0e0e0;
        --border-gray: #333333;
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.6);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.6);
    }

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
        max-width: 900px;
        padding: 3rem 2rem;
        margin: 0 auto;
        color: var(--text-white);
    }

    /* Header */
    .header-section {
        background: #0891b2;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        border: 1px solid var(--border-gray);
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
        color: var(--text-white);
    }

    .header-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--accent-gradient);
    }

    h2 {
        color: var(--accent-solid1) !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .step-badge {
        background: #0891b2;
        color: var(--text-white);
        width: 48px;
        height: 48px;
        border-radius: 12px;
        text-align: center;
        line-height: 48px;
        font-weight: 700;
        font-size: 1.3rem;
        box-shadow: 0 4px 12px rgba(0, 191, 255, 0.3);
    }

    /* Returning user alert */
    .returning-user-alert {
        background: linear-gradient(135deg, #1b1b1b, #222222);
        border: 1px solid #444444;
        border-left: 4px solid var(--accent-solid1);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-md);
        color: var(--text-white);
    }

    /* Container */
    .content-container {
        background: var(--bg-darker);
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--border-gray);
        color: var(--text-white);
    }

    /* Labels */
    label, .stApp label {
        color: var(--text-white) !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* Buttons */
    .stApp .stButton > button {
        background: #0891b2 ;
        color: var(--text-white) !important;
        border: none !important;
        box-shadow: var(--shadow-md);
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        min-width: 140px !important;
        transition: all 0.3s ease !important;
        font-size: 0.95rem !important;
    }

    .stApp .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        opacity: 0.9;
    }

    /* Special buttons */
    .stApp .stButton > button[key="add-new-resume-btn"] {
        background: #780000 !important;
        color: var(--accent-solid1) !important;
        border: 2px solid var(--accent-solid1) !important;
    }

    .stApp .stButton > button[key="add-new-resume-btn"]:hover {
        background: #222222 !important;
    }

    /* File Uploader */
    .stFileUploader {
        background: var(--bg-gray);
        border: 2px dashed var(--border-gray);
        border-radius: 12px;
        padding: 2.5rem;
        transition: 0.3s ease;
        color: var(--text-white);
    }

    .stFileUploader:hover {
        border-color: var(--accent-solid1);
        box-shadow: var(--shadow-md);
    }

    .stFileUploader section button {
        background: var(--accent-gradient) !important;
        color: var(--text-white) !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600;
    }

    /* Textarea */
    textarea, .stTextArea > div > div > textarea {
        background: var(--bg-gray) !important;
        border: 2px solid var(--border-gray) !important;
        border-radius: 12px !important;
        color: var(--text-white) !important;
        padding: 1rem !important;
        transition: all 0.2s ease;
    }

    textarea:focus {
        border-color: var(--accent-solid1) !important;
        box-shadow: 0 0 0 3px rgba(0,191,255,0.15);
    }

    /* Success/Error/Warning messages */
    .stSuccess {background: #0f2d0f !important; border-left: 4px solid #22c55e; color: var(--text-white);}
    .stError {background: #2a0a0a !important; border-left: 4px solid #ef4444; color: var(--text-white);}
    .stWarning {background: #2a1a00 !important; border-left: 4px solid #f59e0b; color: var(--text-white);}

</style>
""", unsafe_allow_html=True)



# Check if user is logged in
if 'logged_in_user' not in st.session_state:
    st.warning("Please login first!")
    st.switch_page("login.py")

# Get resume data from session state
resume_data = st.session_state.get("resume_source", {})
input_method = st.session_state.get(
    "input_method", 
    resume_data.get("input_method", "Manual Entry")
)
# input_method = resume_data.get("input_method", "Manual Entry") 
st.session_state["input_method"] = input_method
# st.write(input_method)


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