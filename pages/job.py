import streamlit as st
import json
from utils import extract_text_from_pdf, extract_text_from_docx, extract_details_from_jd

st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    #MainMenu, footer, header {visibility: hidden;}

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --peacock-blue: #0891b2;
        --peacock-blue-dark: #0e7490;
        --peacock-blue-light: #06b6d4;
        --peacock-shadow: rgba(8, 145, 178, 0.3);
        
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
        background: var(--peacock-blue);
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
        background: linear-gradient(90deg, var(--peacock-blue-light), var(--peacock-blue-dark));
    }

    h2 {
        color: var(--text-white) !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        text-align: center;
    }

    .step-badge {
        background: rgba(255, 255, 255, 0.2);
        color: var(--text-white);
        width: 48px;
        height: 48px;
        border-radius: 12px;
        text-align: center;
        line-height: 48px;
        font-weight: 700;
        font-size: 1.3rem;
        box-shadow: 0 4px 12px var(--peacock-shadow);
    }

    /* Returning user alert */
    .returning-user-alert {
        background: linear-gradient(135deg, #1b1b1b, #222222);
        border: 1px solid #444444;
        border-left: 4px solid var(--peacock-blue);
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

    /* Main Buttons */
    .stApp .stButton > button {
        background: var(--peacock-blue) !important;
        color: var(--text-white) !important;
        border: none !important;
        box-shadow: 0 6px 18px var(--peacock-shadow) !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        min-width: 140px !important;
        transition: all 0.3s ease !important;
        font-size: 0.95rem !important;
    }

    .stApp .stButton > button:hover {
        background: var(--peacock-blue-dark) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px var(--peacock-shadow) !important;
    }

    /* Start New Resume Button - Red/Dark variant */
    .stApp .stButton > button[key="add-new-resume-btn"] {
        background: #dc2626 !important;
        color: var(--text-white) !important;
        border: 2px solid #ef4444 !important;
        box-shadow: 0 6px 18px rgba(220, 38, 38, 0.3) !important;
    }

    .stApp .stButton > button[key="add-new-resume-btn"]:hover {
        background: #b91c1c !important;
        border-color: #dc2626 !important;
        box-shadow: 0 8px 24px rgba(220, 38, 38, 0.4) !important;
    }

    /* File Uploader Container */
    .stFileUploader {
        background: var(--bg-gray);
        border: 3px dashed var(--peacock-blue);
        border-radius: 16px;
        padding: 3rem 2.5rem;
        transition: all 0.3s ease;
        color: var(--text-white);
        box-shadow: none;
    }

    .stFileUploader:hover {
        border-color: var(--peacock-blue-light);
        box-shadow: none;
        background: rgba(8, 145, 178, 0.05);
    }

    /* File Uploader Label */
    .stFileUploader label {
        color: var(--text-white) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }

    /* File Uploader Browse Button */
    .stFileUploader section button {
        background: var(--peacock-blue) !important;
        color: var(--text-white) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 1.4rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px var(--peacock-shadow) !important;
        transition: all 0.3s ease !important;
    }

    .stFileUploader section button:hover {
        background: var(--peacock-blue-dark) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px var(--peacock-shadow) !important;
    }

    /* File Uploader Instructions */
    .stFileUploader small {
        color: var(--text-gray) !important;
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
        border-color: var(--peacock-blue) !important;
        box-shadow: 0 0 0 3px var(--peacock-shadow) !important;
        background: rgba(8, 145, 178, 0.05) !important;
    }

    /* Success/Error/Warning messages */
    .stSuccess {
        background: rgba(8, 145, 178, 0.1) !important;
        border-left: 4px solid var(--peacock-blue) !important;
        color: var(--text-white) !important;
        border-radius: 8px;
    }
    
    .stError {
        background: #2a0a0a !important;
        border-left: 4px solid #ef4444 !important;
        color: var(--text-white) !important;
        border-radius: 8px;
    }
    
    .stWarning {
        background: #2a1a00 !important;
        border-left: 4px solid #f59e0b !important;
        color: var(--text-white) !important;
        border-radius: 8px;
    }

    /* Radio Buttons */
    .stRadio > div {
        color: var(--text-white) !important;
    }

    .stRadio label {
        color: var(--text-white) !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-darker);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--peacock-blue);
        border-radius: 6px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--peacock-blue-dark);
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
# input_method = resume_data.get("input_method", "Manual Entry") 
st.session_state["input_method"] = input_method
# st.write(input_method)



# st.markdown('<div class="header-section">', unsafe_allow_html=True)
st.markdown('<h2 >Target Job Description</h2>', unsafe_allow_html=True)




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
    
    st.markdown('</div>', unsafe_allow_html=True)

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
                                background: rgba(10,10,10,0.95);
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
                                border: 5px solid rgba(255,255,255,0.2);
                                border-top: 5px solid #00b4d8;
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

                    
                        import time
                        time.sleep(2)

                 
                        structured_jd = extract_details_from_jd(job_description)
                        if isinstance(structured_jd, str):
                            try:
                                structured_jd = json.loads(structured_jd)
                            except json.JSONDecodeError:
                                structured_jd = {"raw_text": job_description}

                        st.session_state.job_description = structured_jd

                 
                        loading_placeholder.empty()

                        # st.success("Job description processed successfully!")
                        st.switch_page("pages/create.py")
                    else:
                        st.error("Please provide a job description to continue")

    st.markdown('</div>', unsafe_allow_html=True)