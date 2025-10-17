import streamlit as st
import json
from utils import extract_text_from_pdf, extract_text_from_docx, extract_details_from_jd

# Define the new blue colors
NEW_BLUE = "#1E90FF"  # Dodger Blue
NEW_CYAN = "#00CED1"  # Dark Cyan
NEW_BLUE_SHADOW = "rgba(30, 144, 255, 0.4)" # Shadow for the blue accent

# --- Enhanced Winter Theme CSS ---
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    #MainMenu, footer, header {visibility: hidden;}

    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    /* Color Palette Variables - Winter Theme */
    :root {
        --primary-color: #1a2332;
        --secondary-color: #e8f4f8;
        --accent-color: #4a9eff;
        --accent-light: #7bb8ff;
        --accent-ice: #b4e0ff;
        --text-dark: #1a2332;
        --text-light: #ffffff;
        --card-bg: rgba(74, 158, 255, 0.12);
        --card-border: rgba(180, 224, 255, 0.3);
        --silver: #c5d9e8;
    }

    * {
        font-family: 'Poppins', sans-serif;
    }

    /* App Background - Elegant Dark Winter */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a2332 50%, #243447 100%);
        background-attachment: fixed;
        min-height: 100vh;
        color: var(--text-light);
        position: relative;
    }
    
    /* Subtle animated snowflakes effect */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(2px 2px at 20% 30%, rgba(255,255,255,0.15), transparent),
            radial-gradient(2px 2px at 60% 70%, rgba(255,255,255,0.1), transparent),
            radial-gradient(1px 1px at 50% 50%, rgba(255,255,255,0.1), transparent);
        background-size: 200px 200px, 300px 300px, 150px 150px;
        background-position: 0 0, 40px 60px, 130px 270px;
        pointer-events: none;
        z-index: 0;
    }

    .block-container {
        max-width: 900px;
        padding: 2rem 3rem;
        margin: 0 auto;
        position: relative;
        z-index: 1;
    }

    /* Frosted Header Section */
    .header-section {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(18px);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        border: 1px solid var(--card-border);
        box-shadow: 0 8px 25px rgba(74, 158, 255, 0.2);
        position: relative;
    }

    .header-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-color), var(--accent-light), var(--accent-ice));
        border-radius: 5px;
    }

    h2 {
        color: var(--text-light) !important;
        font-weight: 700 !important;
        font-size: 2.2rem !important;
        display: flex;
        align-items: center;
        gap: 1rem;
        text-shadow: 0 0 12px rgba(74,158,255,0.5);
    }

    .step-badge {
        background: linear-gradient(135deg, var(--accent-color), var(--accent-light));
        color: white;
        width: 45px;
        height: 45px;
        border-radius: 14px;
        text-align: center;
        line-height: 45px;
        font-weight: 700;
        font-size: 1.2rem;
        box-shadow: 0 4px 20px rgba(74,158,255,0.4);
        border: 2px solid var(--silver);
    }

    /* Returning User Frosted Box */
    .returning-user-alert {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--card-border);
        border-radius: 18px;
        padding: 1.8rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 30px rgba(74,158,255,0.15);
    }

    .returning-user-alert h3 {
        color: #ffffff;
        font-size: 1.4rem !important;
        margin-bottom: 0.5rem;
    }

    .returning-user-alert p {
        color: var(--secondary-color);
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Frosted Content Card */
    .content-container {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(25px);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 6px 25px rgba(0,0,0,0.25);
        border: 1px solid var(--card-border);
    }

    /* Label and Text Color Adjustments */
    label, .stApp label, .stRadio label, .stRadio > label {
        color: var(--text-light) !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    /* Radio Button Styling */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.2rem;
        border-radius: 14px;
        border: 1px solid var(--card-border);
    }
    
    .stRadio > div > label > div {
        color: var(--text-light) !important;
    }
    
    .stRadio > div > label > div[data-baseweb="radio"] > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-color: var(--accent-color) !important;
    }
    
    .stRadio > div > label > div[data-baseweb="radio"] > div:first-child {
        background-color: var(--accent-color) !important;
    }
    
    /* Radio button text */
    .stRadio label span {
        color: var(--text-light) !important;
        font-weight: 500 !important;
    }

   
/* Button Styling */
.stApp .stButton > button,
.stApp button[class*="stButton"],
.stApp div.stButton button {
    background: linear-gradient(135deg, var(--accent-color), var(--accent-light)) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 6px 18px rgba(74,158,255,0.28) !important;
    padding: 0.9rem 1.6rem !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    min-width: 140px !important;
    text-transform: none !important;
    transition: all 0.3s ease !important;
}

.stApp .stButton > button > div > p,
.stApp .stButton > button > span,
.stApp button > div > p {
    color: #ffffff !important;
    font-weight: 700 !important;
}

.stApp .stButton > button[key="jb-btn"],
.stApp button[key="jb-btn"] {
    background: linear-gradient(135deg, var(--accent-color), var(--accent-light)) !important;
    color: #ffffff !important;
    width: 100% !important;
    padding: 1rem 2rem !important;
}

.stApp .stButton > button[key="add-new-resume-btn"],
.stApp button[key="add-new-resume-btn"],
.stApp .stButton > button[key="go-to-main-btn"],
.stApp button[key="go-to-main-btn"] {
    background: var(--accent-ice) !important;
    color: var(--text-dark) !important;
    box-shadow: 0 4px 12px rgba(180,224,255,0.25) !important;
}

.stApp .stButton > button:hover,
.stApp button:hover {
    transform: translateY(-2px) !important;
    filter: brightness(1.1) !important;
    box-shadow: 0 8px 25px rgba(74,158,255,0.35) !important;
}


    /* Text Areas & Uploaders */
    textarea, .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 2px solid var(--card-border) !important;
        border-radius: 14px !important;
        color: #000000 !important;
        padding: 1.2rem !important;
        font-size: 0.98rem !important;
        line-height: 1.6 !important;
        transition: all 0.3s ease-in-out;
        font-weight: 400 !important;
    }
    
    /* Placeholder text styling */
    textarea::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
        opacity: 1 !important;
    }

    textarea:focus {
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 0 3px rgba(74,158,255,0.25), 0 8px 25px rgba(74,158,255,0.15) !important;
        background: rgba(255, 255, 255, 0.12) !important;
        outline: none !important;
    }
    
    /* Text area label */
    .stTextArea label {
        color: var(--text-light) !important;
        font-weight: 600 !important;
        margin-bottom: 0.8rem !important;
    }
    
    /* Help text under text area */
    .stTextArea small, .help-text {
        color: var(--accent-ice) !important;
        font-size: 0.88rem !important;
    }

    .stFileUploader {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px dashed var(--card-border) !important;
        border-radius: 16px !important;
        padding: 2.8rem !important;
        transition: 0.3s ease-in-out;
    }

    .stFileUploader:hover {
        border-color: var(--accent-color) !important;
        background: rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 25px rgba(74,158,255,0.15);
    }
    
    .stFileUploader label {
        color: var(--text-light) !important;
        font-weight: 600 !important;
    }
    
    .stFileUploader section {
        color: var(--accent-ice) !important;
    }
    
    .stFileUploader section button {
        background: linear-gradient(135deg, var(--accent-color), var(--accent-light)) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 1.4rem !important;
        font-weight: 600 !important;
    }
    
    .stFileUploader section small {
        color: var(--secondary-color) !important;
    }

    /* Section Divider */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-color), transparent);
        margin: 2rem 0;
        opacity: 0.5;
    }

    /* Success/Error Messages */
    .stSuccess, .stError, .stWarning {
        border-radius: 12px !important;
        padding: 1rem 1.2rem !important;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(255,255,255,0.1);
    }

    .stSuccess {
        background: rgba(180,255,200,0.15) !important;
        border: 1px solid rgba(180,255,200,0.4) !important;
        color: #aef9c0 !important;
    }

    .stError {
        background: rgba(255,120,120,0.15) !important;
        border: 1px solid rgba(255,120,120,0.4) !important;
        color: #ffb0b0 !important;
    }
    
    .stWarning {
        background: rgba(255,200,100,0.15) !important;
        border: 1px solid rgba(255,200,100,0.4) !important;
        color: #ffd699 !important;
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
    # Show alert for users with existing resume data
    st.markdown('<div class="returning-user-alert">', unsafe_allow_html=True)
    # st.markdown('<h3>👋 Resume Found!</h3>', unsafe_allow_html=True)
    
    # Display method used to create resume
    # method_display = "from your Uploaded File" if st.session_state.get("input_method") == "Upload" else "by Manual Entry"

    st.markdown(f'<p>Your last resume was created, You can proceed with it, or click the button below to start a new resume from scratch.</p>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns([1, 4])
    # Button is placed inside a column for better layout control
    with col_a: 
        if st.button("Start New Resume", key="add-new-resume-btn"):
            # Clear all resume-related session state
            keys_to_delete = ['resume_source', 'enhanced_resume', 'job_description', 
                             'resume_processed', 'exp_indices', 'edu_indices', 'cert_indices', 'project_indices']
            
            for key in keys_to_delete:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Redirect to the main resume building page
            st.switch_page("../ask.ai/pages/main.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Job Description Input ---
if resume_source is None:
    st.error("No resume data found. Please go back to the main page to upload or enter your data first.")
    if st.button("Go to Resume Builder", key="go-to-main-btn"):
        st.switch_page("../ask.ai/pages/main.py")
else:
    # Main content
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    
    # Job description input method
    jd_method = st.radio(
        "Choose how to provide the job description:",
        ["Type or Paste", "Upload File"],
        horizontal=True,
        key="jd_method_radio"
    )
    
    # st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
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
            
            # Show extracted text
            if job_description:
                st.text_area(
                    "Extracted Job Description Content (Review before processing)",
                    value=job_description,
                    height=200,
                    help="Preview of the extracted job description"
                )

    else:  # Type or Paste
        job_description = st.text_area(
            "Paste the Job Description Text *",
            value="",
            height=250
        )
        
        if job_description:
            word_count = len(job_description.split())
            st.markdown(f'<p class="help-text">Word count: {word_count}</p>', unsafe_allow_html=True)

    # Submit button in centered column
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Continue to Resume Generation ➡️", key="jb-btn"):
            if job_description:
                with st.spinner("Analyzing job description and preparing for tailoring..."):
                    structured_jd = extract_details_from_jd(job_description)
                    
                    # Handle JSON parsing
                    if isinstance(structured_jd, str):
                        try:
                            structured_jd = json.loads(structured_jd)
                        except json.JSONDecodeError:
                            # If LLM returns non-JSON or fails, save the raw text
                            structured_jd = {"raw_text": job_description}
                    
                    st.session_state.job_description = structured_jd
                
                st.success("Job description processed successfully!")
                st.switch_page("pages/create.py")
            else:
                st.error("Please provide a job description to continue")
    
    st.markdown('</div>', unsafe_allow_html=True)