import streamlit as st
import json
from utils import extract_text_from_pdf, extract_text_from_docx, extract_details_from_jd

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Hide Streamlit elements */
    [data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarNav"] {display: none;}
    #MainMenu, footer, header {visibility: hidden;}

    :root {
        --primary-blue: #0891b2;
        --primary-blue-hover: #0e7490;
        --secondary-blue: #06b6d4;
        --danger-red: #ef4444;
        --bg-dark: #0f172a;
        --bg-card: rgba(255, 255, 255, 0.08);
        --text-white: #ffffff;
        --text-gray: #94a3b8;
        --border-gray: rgba(255, 255, 255, 0.12);
    }

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Smooth page entrance */
    .stApp {
        background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
        min-height: 100vh;
        color: var(--text-white);
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    .block-container {
        max-width: 900px;
        padding: 3rem 2rem;
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

    /* Animated header with shimmer */
    .header-section {
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-blue) 100%);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }

    .header-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }

    h2 {
        color: var(--text-white) !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        text-align: center;
        margin: 1rem 0;
        animation: fadeInUp 0.8s ease-out;
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

    /* Content container with glassmorphism */
    .content-container {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        border: 1px solid var(--border-gray);
        transition: all 0.4s ease;
        animation: scaleIn 0.5s ease-out;
    }
    
    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    .content-container:hover {
        box-shadow: 0 12px 40px rgba(8, 145, 178, 0.2);
    }

    label, .stApp label {
        color: var(--text-white) !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: color 0.3s ease;
    }

    /* Primary buttons with ripple effect */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-blue), var(--secondary-blue)) !important;
        color: var(--text-white) !important;
        border: none !important;
        box-shadow: 0 6px 18px rgba(8, 145, 178, 0.35) !important;
        padding: 0.85rem 1.8rem !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-size: 0.95rem !important;
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
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-blue-hover), var(--primary-blue)) !important;
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(8, 145, 178, 0.5) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }

    /* Danger button */
    div.stButton > button[key="add-new-resume-btn"] {
        background: linear-gradient(135deg, var(--danger-red), #f87171) !important;
        box-shadow: 0 6px 18px rgba(239, 68, 68, 0.35) !important;
    }

    div.stButton > button[key="add-new-resume-btn"]:hover {
        background: linear-gradient(135deg, #dc2626, var(--danger-red)) !important;
        box-shadow: 0 8px 24px rgba(239, 68, 68, 0.5) !important;
    }

    /* File uploader with enhanced animation */
    .stFileUploader {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        border: 3px dashed rgba(8, 145, 178, 0.5);
        border-radius: 20px;
        padding: 3rem 2.5rem;
        transition: all 0.4s ease;
        position: relative;
    }
    
    .stFileUploader::before {
        content: '';
        position: absolute;
        top: -3px;
        left: -3px;
        right: -3px;
        bottom: -3px;
        background: linear-gradient(45deg, var(--primary-blue), transparent, var(--secondary-blue));
        border-radius: 20px;
        opacity: 0;
        transition: opacity 0.4s ease;
        z-index: -1;
    }

    .stFileUploader:hover {
        border-color: var(--secondary-blue);
        transform: scale(1.01);
        box-shadow: 0 0 30px rgba(8, 145, 178, 0.3);
    }
    
    .stFileUploader:hover::before {
        opacity: 0.3;
    }

    .stFileUploader label {
        color: var(--text-white) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }

    .stFileUploader section button {
        background: linear-gradient(135deg, var(--primary-blue), var(--secondary-blue)) !important;
        color: var(--text-white) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 1.4rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(8, 145, 178, 0.35) !important;
        transition: all 0.3s ease !important;
    }

    .stFileUploader section button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(8, 145, 178, 0.5) !important;
    }

    /* Textarea with smooth focus */
    textarea, .stTextArea > div > div > textarea {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 2px solid var(--border-gray) !important;
        border-radius: 12px !important;
        color: var(--text-white) !important;
        padding: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    textarea:focus {
        background: rgba(8, 145, 178, 0.1) !important;
        border-color: var(--primary-blue) !important;
        box-shadow: 0 0 0 4px rgba(8, 145, 178, 0.2) !important;
        transform: translateY(-2px);
    }

    /* Success/Error messages with slide animation */
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
        background: rgba(16, 185, 129, 0.15) !important;
        border-left: 4px solid #10b981 !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.15) !important;
        border-left: 4px solid var(--danger-red) !important;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.15) !important;
        border-left: 4px solid #f59e0b !important;
    }

    /* Radio buttons with smooth transition */
    .stRadio > div {
        color: var(--text-white) !important;
    }

    .stRadio label {
        color: var(--text-white) !important;
        transition: all 0.3s ease;
    }
    
    .stRadio > div > label:hover {
        transform: translateX(5px);
        color: var(--secondary-blue) !important;
    }

    /* Enhanced scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.3);
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--primary-blue), var(--primary-blue-hover));
        border-radius: 6px;
        transition: background 0.3s ease;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, var(--secondary-blue), var(--primary-blue));
    }
</style>
""", unsafe_allow_html=True)


if 'logged_in_user' not in st.session_state:
    st.warning("Please login first!")
    st.switch_page("login.py")

resume_data = st.session_state.get("resume_source", {})
input_method = st.session_state.get(
    "input_method", 
    resume_data.get("input_method", "Manual Entry")
)
st.session_state["input_method"] = input_method

st.markdown('<h2>Target Job Description</h2>', unsafe_allow_html=True)

resume_source = st.session_state.get("resume_source", None)

if resume_source:
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

# --- Job Description Input ---
if resume_source is None:
    st.error("No resume data found. Please go back to the main page to upload or enter your data first.")
    if st.button("Go to Resume Builder", key="go-to-main-btn"):
        st.switch_page("../ask.ai/pages/main.py")
else:
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

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        loading_placeholder = st.empty()

        if st.button("Continue to Resume Generation ➡️", key="jb-btn"):
            if job_description:
                loading_placeholder.markdown("""
                <div id="overlay-loader">
                    <div class="loader-spinner"></div>
                    <p>Analyzing job description...</p>
                </div>
                <style>
                    #overlay-loader {
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100vw;
                        height: 100vh;
                        background: rgba(15, 23, 42, 0.95);
                        backdrop-filter: blur(6px);
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        z-index: 9999;
                        color: white;
                        font-size: 1.2rem;
                        font-weight: 500;
                    }

                    .loader-spinner {
                        border: 5px solid rgba(96, 165, 250, 0.2);
                        border-top: 5px solid #3b82f6;
                        border-radius: 50%;
                        width: 70px;
                        height: 70px;
                        animation: spin 1s linear infinite;
                        margin-bottom: 20px;
                    }

                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }

                    #overlay-loader p {
                        color: #e0f7ff;
                        font-size: 1.1rem;
                        letter-spacing: 0.5px;
                    }
                </style>
                """, unsafe_allow_html=True)

                try:
                    structured_jd = extract_details_from_jd(job_description)
                    if isinstance(structured_jd, str):
                        try:
                            structured_jd = json.loads(structured_jd)
                        except json.JSONDecodeError:
                            structured_jd = {"raw_text": job_description}
                except Exception as e:
                    st.error(f"Error processing JD: {e}")
                    structured_jd = {"raw_text": job_description}

                st.session_state.job_description = structured_jd
                loading_placeholder.empty()
                st.switch_page("pages/create.py")
            else:
                st.error("Please provide a job description to continue")