import streamlit as st
import json
import base64
from utils import get_user_resume, extract_text_from_pdf, extract_text_from_docx, extract_details_from_jd
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(
    page_title="Job Description - Resume Creator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session state management
if 'logged_in_user' not in st.session_state or st.session_state.logged_in_user is None:
    logged_user = st.query_params.get("user")
    if logged_user:
        st.session_state.logged_in_user = logged_user
    else:
        st.warning("Please login first!")
        st.switch_page("app.py")

if st.session_state.logged_in_user:
    st.query_params["user"] = st.session_state.logged_in_user

current_user = st.session_state.get('logged_in_user', '')

# Load existing resume if available
if current_user and 'resume_source' not in st.session_state:
    try:
        stored_resume = get_user_resume(current_user)
        if stored_resume:
            st.session_state.resume_source = stored_resume
    except Exception as e:
        pass

# CSS Styling - Aligned with homepage design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Archivo:wght@400;500;600;700;800;900&display=swap');

    /* ==================== RESET ==================== */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    [data-testid="stSidebar"], 
    [data-testid="collapsedControl"], 
    [data-testid="stSidebarNav"],
    #MainMenu, footer, header {
        display: none !important;
        visibility: hidden !important;
    }

    .stMainBlockContainer, div.block-container, [data-testid="stMainBlockContainer"] {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
        max-width: 900px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* ==================== VARIABLES ==================== */
    :root {
        --primary: #FF6B35;
        --primary-dark: #E85A28;
        --primary-light: #FF8C5A;
        --accent: #FFA500;
        --bg-primary: #FAFAFA;
        --bg-secondary: #FFFFFF;
        --text-primary: #1A1A1A;
        --text-secondary: #666666;
        --text-light: #999999;
        --border: #E5E5E5;
        --shadow: rgba(255, 107, 53, 0.12);
        --success: #10b981;
        --error: #ef4444;
        --warning: #f59e0b;
    }

    /* ==================== BASE ==================== */
    html, body, .stApp {
        font-family: 'Inter', sans-serif;
        background: var(--bg-primary);
        color: var(--text-primary);
        scroll-behavior: smooth;
    }

    /* ==================== NAVIGATION ==================== */
    .nav-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid var(--border);
        animation: slideDown 0.6s ease-out;
    }

    @keyframes slideDown {
        from {
            transform: translateY(-100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    .nav-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 3rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 80px;
    }

    .logo {
        font-family: 'Archivo', sans-serif;
        font-size: 28px;
        font-weight: 900;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -1px;
    }

    .nav-menu {
        display: flex;
        gap: 2rem;
        align-items: center;
    }

    .nav-link {
        color: var(--text-secondary) !important;
        text-decoration: none !important;
        font-size: 15px;
        font-weight: 500;
        padding: 10px 20px;
        border-radius: 8px;
        transition: all 0.3s ease;
        position: relative;
    }

    .nav-link:hover {
        color: var(--primary) !important;
        background: rgba(255, 107, 53, 0.08);
    }

    /* ==================== MAIN CONTENT ==================== */
    .main-content {
        max-width: 900px;
        margin: 0 auto;
        padding: 120px 2rem 80px;
        animation: fadeInUp 0.8s ease-out;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* ==================== PAGE HEADER ==================== */
    .page-header {
        text-align: center;
        margin-bottom: 3rem;
    }

    .page-badge {
        display: inline-block;
        background: rgba(255, 107, 53, 0.1);
        padding: 8px 20px;
        border-radius: 50px;
        font-size: 13px;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 107, 53, 0.2);
    }

    .page-title {
        font-family: 'Archivo', sans-serif;
        font-size: 48px;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 1rem;
        letter-spacing: -1px;
    }

    .page-subtitle {
        font-size: 18px;
        color: var(--text-secondary);
        line-height: 1.7;
    }

    /* ==================== CONTENT CARD ==================== */
    .content-card {
        background: var(--bg-secondary);
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        border: 1px solid var(--border);
        transition: all 0.4s ease;
        animation: scaleIn 0.5s ease-out;
        margin-bottom: 2rem;
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

    .content-card:hover {
        box-shadow: 0 8px 24px rgba(255, 107, 53, 0.15);
    }

    /* ==================== FORM CONTAINER ==================== */
    .form-container {
        background: var(--bg-secondary);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        border: 1px solid var(--border);
        margin: 2rem 0;
    }
    
    /* Add space above form elements when inside container */
    .element-container:has(.stRadio),
    .element-container:has(.stFileUploader), 
    .element-container:has(.stTextArea) {
        margin-top: 1.5rem !important;
    }

    /* ==================== FORM ELEMENTS ==================== */
    
    /* Streamlit element spacing */
    [data-testid="stVerticalBlock"] > div {
        gap: 1.5rem;
    }
    
    .stRadio, .stFileUploader, .stTextArea {
        margin-bottom: 1.5rem;
    }
    
    label, .stApp label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        margin-bottom: 0.8rem !important;
        display: block !important;
    }

    /* Radio buttons */
    .stRadio {
        margin-bottom: 2rem !important;
    }
    
    .stRadio > label {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: 1rem !important;
    }
    
    .stRadio > div {
        display: flex !important;
        gap: 1.5rem !important;
    }

    .stRadio > div > label {
        background: var(--bg-secondary);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border: 2px solid var(--border);
        cursor: pointer;
        transition: all 0.3s ease;
        flex: 1;
        text-align: center;
        margin: 0 !important;
        position: relative;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        max-width: 180px;
        min-width: 150px;
    }
    
    .stRadio > div > label:hover {
        border-color: var(--primary);
        background: rgba(255, 107, 53, 0.05);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.15);
    }
    
    /* Hide default radio circle */
    .stRadio > div > label > div:first-child {
        display: none !important;
    }
    
    /* Style the text */
    .stRadio > div > label > div:last-child {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        white-space: nowrap !important;
    }
    
    /* Selected state */
    .stRadio > div > label[data-baseweb="radio"]:has(input:checked) {
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.1), rgba(255, 140, 90, 0.1));
        border-color: var(--primary);
        box-shadow: 0 4px 16px rgba(255, 107, 53, 0.2);
    }
    
    .stRadio > div > label[data-baseweb="radio"]:has(input:checked) > div:last-child {
        color: var(--primary) !important;
    }
    
    /* Add checkmark icon for selected */
    .stRadio > div > label[data-baseweb="radio"]:has(input:checked)::before {
        content: '✓';
        position: absolute;
        top: 8px;
        right: 8px;
        width: 20px;
        height: 20px;
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
    }

    /* File uploader */
    .stFileUploader {
        background: var(--bg-primary);
        border: 3px dashed var(--border);
        border-radius: 20px;
        padding: 3rem 2rem;
        transition: all 0.4s ease;
        text-align: center;
        margin: 2rem 0 !important;
    }

    .stFileUploader:hover {
        border-color: var(--primary);
        background: rgba(255, 107, 53, 0.03);
        box-shadow: 0 8px 24px rgba(255, 107, 53, 0.1);
    }

    .stFileUploader section button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-shadow: 0 4px 12px var(--shadow) !important;
        transition: all 0.3s ease !important;
    }

    .stFileUploader section button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px var(--shadow) !important;
    }

    /* Text area */
    .stTextArea {
        margin: 1.5rem 0 !important;
    }
    
    textarea, .stTextArea > div > div > textarea {
        background: var(--bg-secondary) !important;
        border: 2px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        padding: 1.2rem !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }

    textarea:focus, .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(255, 107, 53, 0.1) !important;
        outline: none !important;
    }

    /* ==================== ALERTS ==================== */
    .stSuccess, .stError, .stWarning {
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        animation: slideInRight 0.5s ease-out;
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
        background: rgba(16, 185, 129, 0.1) !important;
        border-left: 4px solid var(--success) !important;
        color: var(--success) !important;
    }

    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border-left: 4px solid var(--error) !important;
        color: var(--error) !important;
    }

    .stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        border-left: 4px solid var(--warning) !important;
        color: var(--warning) !important;
    }

    /* ==================== BUTTONS ==================== */
    .btn {
        padding: 12px 28px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 14px;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
        font-family: 'Inter', sans-serif;
        white-space: nowrap;
    }

    .btn-primary {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white !important;
        box-shadow: 0 6px 20px var(--shadow);
        border: 2px solid var(--primary);
    }

    .btn-primary:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px var(--shadow);
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%);
    }

    [data-testid="stButton"] > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border: 2px solid var(--primary) !important;
        border-radius: 10px !important;
        padding: 14px 32px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: 0 4px 16px var(--shadow) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin-top: 2rem !important;
    }

    [data-testid="stButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px var(--shadow) !important;
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%) !important;
    }

    /* ==================== LOADER ==================== */
    #overlay-loader {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }

    .loader-spinner {
        border: 5px solid rgba(255, 107, 53, 0.2);
        border-top: 5px solid var(--primary);
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
        color: var(--text-primary);
        font-size: 18px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* ==================== RESPONSIVE ==================== */
    @media (max-width: 768px) {
        .nav-container {
            padding: 0 1.5rem;
        }

        .nav-menu {
            gap: 0.5rem;
        }

        .nav-link {
            padding: 8px 12px;
            font-size: 13px;
        }

        .main-content {
            padding: 100px 1.5rem 60px;
        }

        .page-title {
            font-size: 36px;
        }

        .content-card {
            padding: 2rem;
        }

        .stRadio > div {
            flex-direction: column !important;
        }
            

    }
    </style>
""", unsafe_allow_html=True)

# Build URLs
ats_url = f"ats?user={current_user}"
qu_url = f"qu?user={current_user}"

# Navigation Bar
st.markdown(f"""
<div class="nav-wrapper">
    <div class="nav-container">
        <div class="logo">ResumeIQ</div>
        <div class="nav-menu">
            <a class="nav-link" href="?home=true&user={current_user}" target="_self">Home</a>
            <a class="nav-link" href="?create=true&user={current_user}" target="_self">Create Resume</a>
            <a class="nav-link" href="{ats_url}" target="_self">ATS Checker</a>
            <a class="nav-link" href="{qu_url}" target="_self">AI Assistant</a>
            <a class="nav-link" href="?logout=true" target="_self">Logout</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Handle navigation
if st.query_params.get("create") == "true":
    if "create" in st.query_params:
        del st.query_params["create"]
    if st.session_state.logged_in_user:
        st.query_params["user"] = st.session_state.logged_in_user
    st.switch_page("pages/main.py")

if st.query_params.get("logout") == "true":
    st.session_state.logged_in_user = None
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.switch_page("app.py")

if st.query_params.get("home") == "true":
    if "home" in st.query_params:
        del st.query_params["home"]
    if st.session_state.logged_in_user:
        st.query_params["user"] = st.session_state.logged_in_user
    st.switch_page("app.py")

# Main Content
resume_data = st.session_state.get("resume_source", {})
input_method = st.session_state.get(
    "input_method", 
    resume_data.get("input_method", "Manual Entry")
)
st.session_state["input_method"] = input_method

resume_source = st.session_state.get("resume_source", None)

# ✅ CORRECT - Wrapped in <style> tags
st.markdown("""
<style>
/* ==================== MAIN WRAPPER ==================== */
.ats-main-wrapper {
    min-height: 30vh;
    background: linear-gradient(135deg, #fff9f5 0%, #ffffff 50%, #fff5f0 100%);
    padding: 110px 0 40px;
    position: relative;
}

.ats-main-wrapper::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 200px;
    background: radial-gradient(ellipse at top, rgba(232, 117, 50, 0.06) 0%, transparent 70%);
    pointer-events: none;
}

.ats-hero {
    text-align: center;
    margin-bottom: 2.5rem;
    position: relative;
    z-index: 1;
}

.ats-hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, #fff5f0 0%, #ffe8d6 100%);
    color: #e87532;
    padding: 6px 20px;
    border-radius: 50px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-bottom: 1rem;
    border: 1px solid rgba(232, 117, 50, 0.2);
}

.ats-main-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #0a0f14;
    margin-bottom: 0.5rem;
    line-height: 1.2;
    letter-spacing: -1px;
}

.ats-main-title .highlight {
    background: linear-gradient(135deg, #e87532 0%, #ff8c42 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.ats-hero-description {
    font-size: 1rem;
    color: #64748b;
    max-width: 600px;
    margin-left: 120px !important;  
    line-height: 1.6;
    font-weight: 400;
}
</style>
""", unsafe_allow_html=True)

# Then your HTML (separate markdown call)
st.markdown("""
<div class="ats-main-wrapper">
    <div class="ats-hero">
        <div class="ats-hero-badge">Step 2 of 3</div>
        <h1 class="ats-main-title">Target <span class="highlight">Job Description</span></h1>
        <p class="ats-hero-description">
           Provide the job description to tailor your resume for maximum impact
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

if resume_source is None:
    st.error("❌ No resume data found. Please go back to the main page to upload or enter your data first.")
else:
    jd_method = st.radio(
        "Choose how to provide the job description:",
        ["Paste Text", "Upload File"],
        horizontal=True,
        key="jd_method_radio"
    )
    
    job_description = ""

    if jd_method == "Upload File":
        jd_file = st.file_uploader(
            "Upload Job Description (PDF or DOCX)",
            type=["pdf", "docx"],
            key="jd_upload",
            help="Upload a file containing the complete job description"
        )
        if jd_file:
            with st.spinner("📄 Reading job description..."):
                if jd_file.type == "application/pdf":
                    job_description = extract_text_from_pdf(jd_file)
                else:
                    job_description = extract_text_from_docx(jd_file)
                st.success("✅ Job description uploaded successfully!")
            
            if job_description:
                st.text_area(
                    "Extracted Content (Review before processing)",
                    value=job_description,
                    height=200,
                    help="Preview of the extracted job description"
                )
    else:
        job_description = st.text_area(
            "Paste the Job Description *",
            value="",
            height=300,
            placeholder="Paste the complete job description here, including responsibilities, requirements, and qualifications..."
        )
    
    # Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        loading_placeholder = st.empty()
        
        if st.button("Continue to Resume Generation →", key="jb-btn"):
            if job_description:
                loading_placeholder.markdown("""
                    <div id="overlay-loader">
                        <div class="loader-spinner"></div>
                        <p>Analyzing Job Description...</p>
                    </div>
                """, unsafe_allow_html=True)

                try:
                    structured_jd = extract_details_from_jd(job_description)
                    if isinstance(structured_jd, str):
                        try:
                            structured_jd = json.loads(structured_jd)
                        except json.JSONDecodeError:
                            structured_jd = {"raw_text": job_description}
                except Exception as e:
                    st.error(f"❌ Error processing job description: {e}")
                    structured_jd = {"raw_text": job_description}

                # Store in session state
                st.session_state.job_description = structured_jd

                # ============= CRITICAL: ENCODE JD TO URL =============
                try:
                    # Encode to base64 for safe URL transmission
                    jd_json = json.dumps(structured_jd)
                    encoded_bytes = base64.b64encode(jd_json.encode('utf-8'))
                    encoded_str = encoded_bytes.decode('utf-8')
                    st.query_params["jd"] = encoded_str
                except Exception as e:
                    st.warning(f"Could not encode JD to URL: {e}")
                # ============= END ENCODE =============

                loading_placeholder.empty()
                st.switch_page("pages/create.py")
            else:
                st.error("⚠️ Please provide a job description to continue")