import streamlit as st
from pathlib import Path
import json
import time

from utils import (
    is_valid_email,
    is_valid_phone,
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_details_from_text,
    get_all_skills_from_llm,
    save_user_resume,
    load_skills_from_json
)

from streamlit_extras.stylable_container import stylable_container

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


if "exp_indices" not in st.session_state:
    st.session_state.exp_indices = [0]
if "edu_indices" not in st.session_state:
    st.session_state.edu_indices = [0]
if "cert_indices" not in st.session_state:
    st.session_state.cert_indices = [0]
if "project_indices" not in st.session_state:
    st.session_state.project_indices = [0]

if "saved_personal_info" not in st.session_state:
    st.session_state.saved_personal_info = {}
if "saved_experiences" not in st.session_state:
    st.session_state.saved_experiences = {}
if "saved_education" not in st.session_state:
    st.session_state.saved_education = {}
if "saved_certificates" not in st.session_state:
    st.session_state.saved_certificates = {}
if "saved_projects" not in st.session_state:
    st.session_state.saved_projects = {}

if "custom_indices" not in st.session_state:
    st.session_state.custom_indices = [0]
if "saved_custom_sections" not in st.session_state:
    st.session_state.saved_custom_sections = {}

# ============================
# COMMON BUTTON STYLE
# ============================
BUTTON_STYLE = """
    button {
        background-color: #ffffff !important;
        color: #e87532 !important;
        padding: 12px 28px !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        border: 2px solid #e87532 !important;
    }
    button:hover {
        background-color:#e87532 !important;
        color: #ffffff !important;
    }
"""

SAVE_STYLE = """
    button {
        background-color: #93C47D !important;
        color: #FFFFFF !important;
        padding: 12px 2px !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        border: 2px solid #93C47D !important;
        width: 300px !important;
        margin-left:200px !important;
    }
    button:hover {
        background-color:#FFFFFF !important;
        color: #93C47D !important;
    }
"""
SAVEPER_STYLE = """
    button {
        background-color: #93C47D !important;
        color: #FFFFFF !important;
        padding: 12px 2px !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        border: 2px solid #93C47D !important;
        width: 300px !important;
        margin-left:50px !important;
    }
    button:hover {
        background-color:#FFFFFF !important;
        color: #93C47D !important;
    }
"""
REMOVE_STYLE = """
    button {
        background-color: #FF6A4C !important;
        color: #FFFFFF !important;
        padding: 12px 28px !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        border: 2px solid #FF6A4C !important;
        width: 300px !important; 
        margin-left:00px !important;
        
    }
    button:hover {
        background-color:#FFFFFF !important;
        color: #FF6A4C !important;
    }
"""

ADD_STYLE = """
    button {
        background-color: #9FC0DE !important;
        color: #FFFFFF !important;
        padding: 12px 28px !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        border: 2px solid #9FC0DE !important;
        width: 300px !important; 
        margin-left:100px !important;
    }
    button:hover {
        background-color:#FFFFFF !important;
        color: #9FC0DE !important;
    }
"""

PRIMARY_LARGE_BUTTON_STYLE = """
    button {
        background-color: #e87532 !important;
        color: #ffffff !important;
        padding: 14px 40px !important;
        border-radius: 50px !important;
        font-weight: 700 !important;
        border: 2px solid #e87532 !important;
        font-size: 1rem !important;
    }
    button:hover {
        background-color:#ffffff !important;
        color: #e87532 !important;
    }
"""

# ============================
# PAGE STYLE (NO BUTTON CSS HERE)
# ============================
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
        max-width: 1100px !important;
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
    }

    .nav-link:hover {
        color: var(--primary) !important;
        background: rgba(255, 107, 53, 0.08);
    }

    /* ==================== PAGE HEADER ==================== */
    .page-header {
        text-align: center;
        margin: 120px 0 3rem;
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
        font-size: 42px;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 1rem;
        letter-spacing: -1px;
    }

    .page-subtitle {
        font-size: 17px;
        color: var(--text-secondary);
        line-height: 1.7;
        max-width: 600px;
        margin-left: 200px !important;
    }

    /* ==================== RADIO BUTTONS ==================== */
    .stRadio {
        margin: 2rem 0 !important;
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
        justify-content: center !important;
    }

    .stRadio > div > label {
        background: var(--bg-secondary);
        padding: 1rem 2rem;
        border-radius: 12px;
        border: 2px solid var(--border);
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        margin: 0 !important;
        position: relative;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        min-width: 180px;
    }
    
    .stRadio > div > label:hover {
        border-color: var(--primary);
        background: rgba(255, 107, 53, 0.05);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.15);
    }
    
    .stRadio > div > label > div:first-child {
        display: none !important;
    }
    
    .stRadio > div > label > div:last-child {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        white-space: nowrap !important;
    }
    
    .stRadio > div > label[data-baseweb="radio"]:has(input:checked) {
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.1), rgba(255, 140, 90, 0.1));
        border-color: var(--primary);
        box-shadow: 0 4px 16px rgba(255, 107, 53, 0.2);
    }
    
    .stRadio > div > label[data-baseweb="radio"]:has(input:checked) > div:last-child {
        color: var(--primary) !important;
    }
    
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

    /* ==================== TABS ==================== */
    .tabs-wrapper {
        display: flex;
        gap: 0.5rem;
        margin: 2rem 0;
        overflow-x: auto;
        padding-bottom: 0.5rem;
    }

    [data-testid="column"] {
        padding: 0 !important;
    }

    [data-testid="stButton"] {
        width: 100% !important;
    }

    [data-testid="stButton"] > button {
        width: 100% !important;
        background: var(--bg-secondary) !important;
        color: var(--text-secondary) !important;
        border: 2px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        transition: all 0.3s ease !important;
        white-space: nowrap !important;
    }

    [data-testid="stButton"] > button:hover {
        border-color: var(--primary) !important;
        background: rgba(255, 107, 53, 0.05) !important;
        color: var(--primary) !important;
    }

    [data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
        color: white !important;
        border-color: var(--primary) !important;
        box-shadow: 0 4px 12px var(--shadow) !important;
    }

    [data-testid="stButton"] > button[kind="primary"]:hover {
        background: linear-gradient(135deg, var(--primary-dark), var(--primary)) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px var(--shadow) !important;
    }

    /* ==================== PROGRESS BAR ==================== */
    .progress-bar {
        width: 100%;
        height: 8px;
        background: var(--bg-secondary);
        border-radius: 10px;
        overflow: hidden;
        margin: 2rem 0 1rem;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
        transition: width 0.5s ease;
        border-radius: 10px;
    }

    /* ==================== FORM ELEMENTS ==================== */
    label, .stApp label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        margin-bottom: 0.5rem !important;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--bg-secondary) !important;
        border: 2px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        padding: 0.75rem !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1) !important;
    }

    /* ==================== SECTION HEADERS ==================== */
    .section-header {
        text-align: center;
        color: var(--primary);
        font-size: 20px;
        font-weight: 700;
        margin: 3rem 0 2rem;
        font-family: 'Archivo', sans-serif;
    }

    .section-divider {
        width: 80px;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--primary), transparent);
        margin: 0.5rem auto 2rem;
    }

    /* ==================== FILE UPLOADER ==================== */
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
    /* ==================== ALERTS ==================== */
    .stSuccess, .stError, .stWarning, .stInfo {
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
    }

    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border-left: 4px solid var(--error) !important;
    }

    .stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        border-left: 4px solid var(--warning) !important;
    }

    .stInfo {
        background: rgba(59, 130, 246, 0.1) !important;
        border-left: 4px solid #3b82f6 !important;
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
    }

    /* ==================== RESPONSIVE ==================== */
    @media (max-width: 768px) {
        .nav-container {
            padding: 0 1.5rem;
        }

        .page-title {
            font-size: 32px;
        }

        .stRadio > div {
            flex-direction: column !important;
        }

        .tabs-wrapper {
            overflow-x: scroll;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Build URLs
ats_url = f"ats?user={current_user}"
qu_url = f"qu?user={current_user}"
home_url = f"/?user={current_user}"

# Navigation Bar
st.markdown(f"""
<div class="nav-wrapper">
    <div class="nav-container">
        <div class="logo">ResumeIQ</div>
        <div class="nav-menu">
            <a class="nav-link" href="{home_url}" target="_self">Home</a>
            <a class="nav-link" href="{ats_url}" target="_self">ATS Checker</a>
            <a class="nav-link" href="{qu_url}" target="_self">AI Assistant</a>
            <a class="nav-link" href="?logout=true" target="_self">Logout</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Handle logout
if st.query_params.get("logout") == "true":
    st.session_state.logged_in_user = None
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.switch_page("app.py")


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
    margin-left: 220px !important; */
    line-height: 1.6;
    font-weight: 400;
}
</style>
""", unsafe_allow_html=True)

 
st.markdown("""
<div class="ats-main-wrapper">
    <div class="ats-hero">
        <div class="ats-hero-badge">Step 1 of 3</div>
        <h1 class="ats-main-title">Build Your <span class="highlight">Resume</span></h1>
        <p class="ats-hero-description">
            Choose how you'd like to provide your information - manually enter details or upload an existing resume
        </p>
    </div>
</div>
""", unsafe_allow_html=True)


if st.session_state.logged_in_user:
    input_method = st.radio(
        "How would you like to provide your information?",
        ["Manual Entry", "Upload Resume"],
        horizontal=True,
        key="input_method_radio"
    )
   
    user_data = {}
    professional_experience = []
    education = []
    certificate = []
    project = []

    remove_index_edu = None
    remove_index_cert = None
    remove_index = None
    remove_index_project = None

    # ====================================================================================
    # MANUAL ENTRY
    # ====================================================================================
    if input_method == "Manual Entry":
        st.session_state["input_method"] = input_method
        # Initialize active tab in session state
        if "active_tab" not in st.session_state:
            st.session_state.active_tab = "personal"

        # Tab data structure
        tabs_config = [
            {"id": "personal", "label": "Personal Info", "icon": "1"},
            {"id": "experience", "label": "Experience", "icon": "2"},
            {"id": "education", "label": "Education", "icon": "3"},
            {"id": "certifications", "label": "Certifications", "icon": "4"},
            {"id": "projects", "label": "Projects", "icon": "5"},
            {"id": "custom", "label": "Custom Sections", "icon": "6"},
        ]

        # Function to change tabs
        def change_tab(tab_id):
            st.session_state.active_tab = tab_id

        # Calculate progress
        def calculate_progress():
            completed_sections = 0
            total_sections = 6
            
            if st.session_state.saved_personal_info:
                completed_sections += 1
            if st.session_state.saved_experiences:
                completed_sections += 1
            if st.session_state.saved_education:
                completed_sections += 1
            if st.session_state.saved_certificates:
                completed_sections += 1
            if st.session_state.saved_projects:
                completed_sections += 1
            if st.session_state.saved_custom_sections:
                completed_sections += 1
            
            return (completed_sections / total_sections) * 100
            # Render tabs
        st.markdown('<div class="tab-container">', unsafe_allow_html=True)

        # Progress bar
        progress = calculate_progress()
        st.markdown(f"""
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress}%"></div>
        </div>
        <p style="text-align: center; color: #6b7280; font-size: 0.9rem; margin-bottom: 1.5rem;">
            Progress: {int(progress)}% Complete
        </p>
        """, unsafe_allow_html=True)

        # Render tab buttons
        st.markdown('<div class="tabs-wrapper">', unsafe_allow_html=True)

        col_tabs = st.columns(len(tabs_config))
        for idx, tab in enumerate(tabs_config):
            with col_tabs[idx]:
                active_class = "active" if st.session_state.active_tab == tab["id"] else ""
                if st.button(
                    f"{tab['icon']}  {tab['label']}", 
                    key=f"tab_{tab['id']}",
                    width='stretch',
                    type="secondary" if active_class == "" else "primary"
                ):
                    change_tab(tab["id"])
                    st.rerun()

        st.markdown('</div></div>', unsafe_allow_html=True)

        # Tab content rendering
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)

        # PERSONAL INFO TAB
        if st.session_state.active_tab == "personal":
            st.markdown("""
    <div class="section-header">Personal information</div>
    <div class="section-divider-wave"></div>
    """, unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input(
                    "Full Name *",
                    placeholder="e.g., John Smith",
                    key="name_input",
                    value=st.session_state.saved_personal_info.get("name", "")
                )
                experience = st.text_input(
                    "Years of Experience *",
                    placeholder="e.g., 5",
                    key="experience_input",
                    value=st.session_state.saved_personal_info.get("experience", "")
                )
                phone = st.text_input(
                    "Phone number *",
                    placeholder="e.g., +91 ",
                    key="phone",
                    value=st.session_state.saved_personal_info.get("phone", "")
                )
                email = st.text_input(
                    "Email *",
                    placeholder="e.g., google@gmail.com",
                    key="email",
                    value=st.session_state.saved_personal_info.get("email", "")
                )

            with col2:
                all_skills_list = load_skills_from_json()
                skills = st.multiselect(
                    "Your Core Skills *",
                    options=all_skills_list,
                    help="Select all relevant skills",
                    key="general_skills",
                    default=st.session_state.saved_personal_info.get("skills", [])
                )
                location = st.text_input(
                    "Location *",
                    placeholder="e.g., New York",
                    key="location",
                    value=st.session_state.saved_personal_info.get("location", "")
                )
                url = st.text_input(
                    "LinkedIn/GitHub",
                    placeholder="e.g., user/linkedin.com",
                    key="url",
                    value=st.session_state.saved_personal_info.get("url", "")
                )
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                with stylable_container("save-personal-btn", css_styles=SAVEPER_STYLE):
                    if st.button("Save & Continue", key="save_personal_tab", width='stretch'):
                        if name and skills and experience and phone and email and location:
                            if not is_valid_email(email):
                                st.error("Please enter a valid email address")
                            elif not is_valid_phone(phone):
                                st.error("Please enter a valid phone number")
                            else:
                                st.session_state.saved_personal_info = {
                                    "name": name,
                                    "skills": skills,
                                    "experience": experience,
                                    "phone": phone,
                                    "email": email,
                                    "url": url,
                                    "location": location
                                }
                                st.success("✅ Personal information saved!")
                                change_tab("experience")
                                st.rerun()
                        else:
                            st.error("Please fill in all required fields marked with *")

        # EXPERIENCE TAB
        elif st.session_state.active_tab == "experience":
            
            # Experience section code here (keep your existing experience code)
            for idx, i in enumerate(st.session_state.exp_indices):
                # st.markdown(f'<p class="section-header">EXPERIENCE {idx + 1}</p>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="section-header">Experience {idx + 1}</div>
                <div class="section-divider-wave"></div>
                """, unsafe_allow_html=True)

                saved_exp = st.session_state.saved_experiences.get(i, {})
                
                col1, col2 = st.columns([3, 3])
                with col1:
                    company_name = st.text_input(
                        "Company Name",
                        key=f"company_{i}",
                        placeholder="e.g., Google Inc.",
                        value=saved_exp.get("company", "")
                    )
                    position_name = st.text_input(
                        "Position",
                        key=f"position_{i}",
                        placeholder="e.g., Senior Developer",
                        value=saved_exp.get("position", "")
                    )
                    exp_skills_list = load_skills_from_json()
                    exp_skills = st.multiselect(
                        "Skills Used",
                        options=exp_skills_list,
                        key=f"exp_skills_{i}",
                        default=saved_exp.get("exp_skills", [])
                    )
                with col2:
                    comp_startdate = st.text_input(
                        "Start Date (MM/YYYY)",
                        key=f"comp_startdate_{i}",
                        placeholder="e.g., 01/2020",
                        value=saved_exp.get("start_date", "")
                    )
                    comp_enddate = st.text_input(
                        "End Date (MM/YYYY) or 'Present'",
                        key=f"comp_enddate_{i}",
                        placeholder="e.g., 12/2023 or Present",
                        value=saved_exp.get("end_date", "")
                    )
                
                col_save, col_remove = st.columns(2)
                with col_remove:
                    with stylable_container(f"remove-exp-{i}", css_styles=REMOVE_STYLE):
                        if st.button(f"Remove Experience {idx + 1}", key=f"remove_exp_{i}", width='stretch'):
                            remove_index = i

                with col_save:
                    with stylable_container(f"save-exp-{i}", css_styles=SAVE_STYLE):
                        if st.button(f"Save Experience {idx + 1}", key=f"save_exp_{i}", width='stretch'):
                            if company_name and position_name:
                                st.session_state.saved_experiences[i] = {
                                    "company": company_name,
                                    "position": position_name,
                                    "exp_skills": exp_skills,
                                    "start_date": comp_startdate,
                                    "end_date": comp_enddate
                                }
                                st.success(f"✅ Experience {idx + 1} saved!")
                            else:
                                st.error("Please fill in company name and position")

                professional_experience.append({
                    "company": company_name,
                    "position": position_name,
                    'exp_skills': exp_skills,
                    "start_date": comp_startdate,
                    "end_date": comp_enddate
                })
                st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
            if remove_index is not None:
                st.session_state.exp_indices.remove(remove_index)
                st.rerun()

            col_add_exp = st.columns([1, 2, 1])
            with col_add_exp[1]:
                st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)

                with stylable_container("add-exp-btn", css_styles=ADD_STYLE):
                    st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)

                    if st.button("+ Add More Experience", key="add_exp", width='stretch'):
                        new_idx = max(st.session_state.exp_indices) + 1 if st.session_state.exp_indices else 0
                        st.session_state.exp_indices.append(new_idx)
                        st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Previous", key="exp_prev", width='stretch'):
                    change_tab("personal")
                    st.rerun()
            with col2:
                if st.button("Next →", key="exp_next", width='stretch'):
                    change_tab("education")
                    st.rerun()
        
        # EDUCATION TAB
        elif st.session_state.active_tab == "education":
            
            for idx, i in enumerate(st.session_state.edu_indices):
                st.markdown(f"""
                <div class="section-header">Education {idx + 1}</div>
                <div class="section-divider-wave"></div>
                """, unsafe_allow_html=True)


                saved_edu = st.session_state.saved_education.get(i, {})
                col1, col2 = st.columns(2)
                with col1:
                    course = st.text_input(
                        "Course/Degree",
                        placeholder="e.g., Master of Computer Application",
                        key=f"course_{i}",
                        value=saved_edu.get("course", "")
                    )
                    university = st.text_input(
                        "Institution",
                        placeholder="e.g., Texas University",
                        key=f"university_{i}",
                        value=saved_edu.get("university", "")
                    )
                with col2:
                    edu_startdate = st.text_input(
                        "Start Date (MM/YYYY)",
                        key=f"edu_start_{i}",
                        placeholder="e.g., 08/2018",
                        value=saved_edu.get("start_date", "")
                    )
                    edu_enddate = st.text_input(
                        "End Date (MM/YYYY) or 'Present'",
                        key=f"edu_end_{i}",
                        placeholder="e.g., 05/2022 or Present",
                        value=saved_edu.get("end_date", "")
                    )

                    if edu_startdate and edu_enddate and edu_enddate.lower() != "present":
                        try:
                            from datetime import datetime
                            start = datetime.strptime(edu_startdate, "%m/%Y")
                            end = datetime.strptime(edu_enddate, "%m/%Y")
                            if start > end:
                                st.warning("⚠️ Start date must be before end date")
                        except:
                            st.warning("⚠️ Use MM/YYYY format")

                col_save, col_remove = st.columns(2)
                with col_remove:
                    with stylable_container(f"remove-edu-{i}", css_styles=REMOVE_STYLE):
                        if st.button(f"Remove Education {idx + 1}", key=f"remove_edu_{i}", width='stretch'):
                            remove_index_edu = i

                with col_save:
                    with stylable_container(f"save-edu-{i}", css_styles=SAVE_STYLE):
                        if st.button(f"Save Education {idx + 1}", key=f"save_edu_{i}", width='stretch'):
                            if course and university:
                                st.session_state.saved_education[i] = {
                                    "course": course,
                                    "university": university,
                                    "start_date": edu_startdate,
                                    "end_date": edu_enddate
                                }
                                st.success(f"✅ Education {idx + 1} saved!")
                            else:
                                st.error("Please fill in course and institution")

                education.append({
                    "course": course,
                    "university": university,
                    "start_date": edu_startdate,
                    "end_date": edu_enddate
                })
                st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
            if remove_index_edu is not None:
                st.session_state.edu_indices.remove(remove_index_edu)
                st.rerun()

            col_add_edu = st.columns([1, 2, 1])
            with col_add_edu[1]:
                with stylable_container("add-edu-btn", css_styles=ADD_STYLE):
                    st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)

                    if st.button("+ Add More Education", key="add_edu", width='stretch'):
                        new_idx = max(st.session_state.edu_indices) + 1 if st.session_state.edu_indices else 0
                        st.session_state.edu_indices.append(new_idx)
                        st.rerun()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Previous", key="eud_prev", width='stretch'):
                    change_tab("experience")
                    st.rerun()
            with col2:
                if st.button("Next →", key="eud_next", width='stretch'):
                    change_tab("certifications")
                    st.rerun()
            st.markdown("---")
            
        # CERTIFICATIONS TAB
        elif st.session_state.active_tab == "certifications":
            for idx, i in enumerate(st.session_state.cert_indices):
                st.markdown(f"""
                <div class="section-header">Certification {idx + 1}</div>
                <div class="section-divider-wave"></div>
                """, unsafe_allow_html=True)


                saved_cert = st.session_state.saved_certificates.get(i, {})
                col1, col2 = st.columns(2)
                with col1:
                    certificate_name = st.text_input(
                        "Certificate Name",
                        placeholder="e.g., AWS Solutions Architect",
                        key=f"certificate_{i}",
                        value=saved_cert.get("certificate_name", "")
                    )
                    provider = st.text_input(
                        "Provider",
                        placeholder="e.g., Amazon Web Services",
                        key=f"Provider_{i}",
                        value=saved_cert.get("provider_name", "")
                    )
                with col2:
                    comp_date = st.text_input(
                        "Completion Date (MM/YYYY)",
                        key=f"comp_date_{i}",
                        placeholder="e.g., 06/2023",
                        value=saved_cert.get("completed_date", "")
                    )

                col_save, col_remove = st.columns(2)
                with col_remove:
                    with stylable_container(f"remove-cert-{i}", css_styles=REMOVE_STYLE):
                        if st.button(f"Remove Certification {idx + 1}", key=f"remove_cert_{i}", width='stretch'):
                            remove_index_cert = i

                with col_save:
                    with stylable_container(f"save-cert-{i}", css_styles=SAVE_STYLE):
                        if st.button(f"Save Certification {idx + 1}", key=f"save_cert_{i}", width='stretch'):
                            if certificate_name and provider:
                                st.session_state.saved_certificates[i] = {
                                    "certificate_name": certificate_name,
                                    "provider_name": provider,
                                    "completed_date": comp_date
                                }
                                st.success(f"✅ Certification {idx + 1} saved!")
                            else:
                                st.error("Please fill in certificate name and provider")

                certificate.append({
                    "certificate_name": certificate_name,
                    "provider_name": provider,
                    "completed_date": comp_date
                })
                st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
            if remove_index_cert is not None:
                st.session_state.cert_indices.remove(remove_index_cert)
                st.rerun()

            col_add_cert = st.columns([1, 2, 1])
            with col_add_cert[1]:
                with stylable_container("add-cert-btn", css_styles=ADD_STYLE):
                    st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)

                    if st.button("+ Add More Certification", key="add_cert", width='stretch'):
                        new_idx = max(st.session_state.cert_indices) + 1 if st.session_state.cert_indices else 0
                        st.session_state.cert_indices.append(new_idx)
                        st.rerun()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Previous", key="cert_prev", width='stretch'):
                    change_tab("education")
                    st.rerun()
            with col2:
                if st.button("Next →", key="cert_next", width='stretch'):
                    change_tab("projects")
                    st.rerun()
            st.markdown("---")

        # PROJECTS TAB
        elif st.session_state.active_tab == "projects":
            for idx, i in enumerate(st.session_state.project_indices):
                st.markdown(f"""
                <div class="section-header">Project {idx + 1}</div>
                <div class="section-divider-wave"></div>
                """, unsafe_allow_html=True)


                saved_proj = st.session_state.saved_projects.get(i, {})

                col1, col2 = st.columns(2)
                with col1:
                    projectname = st.text_input(
                        "Project Name",
                        placeholder="e.g., Created An Integration Tool",
                        key=f"projectname_{i}",
                        value=saved_proj.get("projectname", "")
                    )
                    tools = st.text_input(
                        "Tools/Languages",
                        placeholder="e.g., PowerBI, SQL, Python",
                        key=f"tools_{i}",
                        value=saved_proj.get("tools", "")
                    )
                with col2:
                    decription = st.text_area(
                        "Description (Key achievements)",
                        key=f"decription_{i}",
                        height=150,
                        value=saved_proj.get("decription", "")
                    )

                col_save, col_remove = st.columns(2)
                with col_remove:
                    with stylable_container(f"remove-proj-{i}", css_styles=REMOVE_STYLE):
                        if st.button(f"Remove Project {idx + 1}", key=f"remove_project_{i}", width='stretch'):
                            remove_index_project = i

                with col_save:
                    with stylable_container(f"save-proj-{i}", css_styles=SAVE_STYLE):
                        if st.button(f"Save Project {idx + 1}", key=f"save_project_{i}", width='stretch'):
                            if projectname:
                                st.session_state.saved_projects[i] = {
                                    "projectname": projectname,
                                    "tools": tools,
                                    "decription": decription
                                }
                                st.success(f"✅ Project {idx + 1} saved!")
                            else:
                                st.error("Please fill in project name")

                project.append({
                    "projectname": projectname,
                    "tools": tools,
                    "decription": decription
                })
                st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
            if remove_index_project is not None:
                st.session_state.project_indices.remove(remove_index_project)
                st.rerun()

            col_add_proj = st.columns([1, 2, 1])
            with col_add_proj[1]:
                with stylable_container("add-proj-btn", css_styles=ADD_STYLE):
                    st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)

                    if st.button("+ Add More Projects", key="add_project", width='stretch'):
                        new_idx = max(st.session_state.project_indices) + 1 if st.session_state.project_indices else 0
                        st.session_state.project_indices.append(new_idx)
                        st.rerun()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Previous", key="pro_prev", width='stretch'):
                    change_tab("certifications")
                    st.rerun()
            with col2:
                if st.button("Next →", key="pro_next", width='stretch'):
                    change_tab("custom")
                    st.rerun()
            st.markdown("---")


        # CUSTOM SECTIONS TAB
        elif st.session_state.active_tab == "custom":
            remove_index_custom = None
            custom_sections = []

            for idx, i in enumerate(st.session_state.custom_indices):
                st.markdown(f"""
                <div class="section-header">Custom section {idx + 1}</div>
                <div class="section-divider-wave"></div>
                """, unsafe_allow_html=True)


                saved_custom = st.session_state.saved_custom_sections.get(i, {})

                col1, col2 = st.columns([1, 1])
                with col1:
                    section_title = st.text_input(
                        "Section Heading *",
                        placeholder="e.g., Languages, Achievements, Interests",
                        key=f"custom_title_{i}",
                        value=saved_custom.get("title", "")
                    )
                with col2:
                    section_description = st.text_area(
                        "Description / Details *",
                        placeholder="Add details for this section...",
                        key=f"custom_desc_{i}",
                        height=120,
                        value=saved_custom.get("description", "")
                    )
                
                col_save, col_remove = st.columns(2)
                with col_remove:
                    with stylable_container(f"remove-custom-{i}", css_styles=REMOVE_STYLE):
                        if st.button(f"Remove Custom Section {idx + 1}", key=f"remove_custom_{i}", width='stretch'):
                            remove_index_custom = i

                with col_save:
                    with stylable_container(f"save-custom-{i}", css_styles=SAVE_STYLE):
                        if st.button(f"Save Custom Section {idx + 1}", key=f"save_custom_{i}", width='stretch'):
                            if section_title and section_description:
                                st.session_state.saved_custom_sections[i] = {
                                    "title": section_title,
                                    "description": section_description
                                }
                                st.success(f"✅ Custom Section {idx + 1} saved!")
                            else:
                                st.error("Please fill in both the heading and description fields.")

                custom_sections.append({
                    "title": section_title,
                    "description": section_description
                })
                st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
            if remove_index_custom is not None:
                st.session_state.custom_indices.remove(remove_index_custom)
                st.rerun()

            col_add_custom = st.columns([1, 2, 1])
            with col_add_custom[1]:
                with stylable_container("add-custom-btn", css_styles=ADD_STYLE):
                    st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)

                    if st.button("+ Add Custom Section", key="add_custom", width='stretch'):
                        new_idx = max(st.session_state.custom_indices) + 1 if st.session_state.custom_indices else 0
                        st.session_state.custom_indices.append(new_idx)
                        st.rerun()
            if st.button("← Previous", key="cust_prev", width='stretch'):
                    change_tab("projects")
                    st.rerun()
           
            st.markdown("---")
        


        # st.markdown('</div>', unsafe_allow_html=True)

        # Final submit button (show on last tab)
        # if st.session_state.active_tab == "custom":
        #     st.markdown("<br>", unsafe_allow_html=True)
        #     col1, col2, col3 = st.columns([1, 2, 1])
        #     with col2:
        #         with stylable_container("final-submit-btn", css_styles=PRIMARY_LARGE_BUTTON_STYLE):
        #             if st.button("Complete & Generate Resume", key="final_submit", width='stretch'):
        #                 # Your existing submit logic here
        #                 st.balloons()
        #                 st.switch_page("pages/job.py")

        # ---------------- CONTINUE BUTTON (SUBMIT) ----------------
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with stylable_container("continue-btn", css_styles=PRIMARY_LARGE_BUTTON_STYLE):
                if st.button("Complete & Generate Resume", key="final_submit", width='stretch'):
                    # Get values from saved session state
                    name = st.session_state.saved_personal_info.get("name", "")
                    skills = st.session_state.saved_personal_info.get("skills", [])
                    experience = st.session_state.saved_personal_info.get("experience", "")
                    phone = st.session_state.saved_personal_info.get("phone", "")
                    email = st.session_state.saved_personal_info.get("email", "")
                    url = st.session_state.saved_personal_info.get("url", "")
                    location = st.session_state.saved_personal_info.get("location", "")
                    
                    if name and skills and experience:  # ✅ Now it works
                        with st.spinner("Processing your resume..."):
                            # Build experience list from saved data
                            professional_experience = [
                                st.session_state.saved_experiences[i]
                                for i in st.session_state.exp_indices
                                if i in st.session_state.saved_experiences
                            ]
                            
                            # Build education list from saved data
                            education = [
                                st.session_state.saved_education[i]
                                for i in st.session_state.edu_indices
                                if i in st.session_state.saved_education
                            ]
                            
                            # Build certificate list
                            certificate = [
                                st.session_state.saved_certificates[i]
                                for i in st.session_state.cert_indices
                                if i in st.session_state.saved_certificates
                            ]
                            
                            # Build project list
                            project = [
                                st.session_state.saved_projects[i]
                                for i in st.session_state.project_indices
                                if i in st.session_state.saved_projects
                            ]
                            
                            # Build custom sections
                            custom_sections = [
                                st.session_state.saved_custom_sections[i]
                                for i in st.session_state.custom_indices
                                if i in st.session_state.saved_custom_sections
                            ]

                            user_data = {
                                'name': name,
                                'skills': skills,
                                'experience': experience,
                                'phone': phone,
                                'email': email,
                                'url': url,
                                'location': location,
                                'professional_experience': professional_experience,
                                'education': education,
                                'certificate': certificate,
                                'project': project,
                                'custom_sections': {
                                    c["title"]: c["description"]
                                    for c in custom_sections
                                    if c.get("title") and c.get("description")
                                }
                            }

                        st.session_state.resume_source = user_data
                        if 'from_template_button' in st.session_state and st.session_state.from_template_button:
                            # Clear the flag
                            st.session_state.from_template_button = False
                            # Navigate to template.py with the parsed data
                            st.switch_page("pages/job.py")
                        else:
                            if 'logged_in_user' in st.session_state:
                                st.session_state.input_method = "Manual Entry"
                                save_success = save_user_resume(
                                    st.session_state.logged_in_user,
                                    user_data,
                                    input_method="Manual Entry"
                                )
                                if save_success:
                                    st.success("Resume processed and saved to profile!")
                                else:
                                    st.warning("Resume processed but couldn't save to profile")

                            st.switch_page("pages/job.py")
                    else:
                        st.error("Please complete the Personal Info section first (Name, Skills, and Experience are required)")

    # ====================================================================================
    # UPLOAD RESUME
    # ====================================================================================
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
    <style>
        /* File uploader border */
        [data-testid="stFileUploader"] > section {
            border: 2px dashed #8b6f47 !important;
            border-radius: 12px !important;
            background: rgba(232, 117, 50, 0.05) !important;
            padding: 2rem !important;
        }
        
        /* Browse files button */
        [data-testid="stFileUploader"] button {
            background-color: #e87532 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1.5rem !important;
            font-weight: 600 !important;
        }
        
        [data-testid="stFileUploader"] button:hover {
            background-color: #d66429 !important;
            color: white !important;
        }
        
        /* Upload icon */
        [data-testid="stFileUploader"] svg {
            fill: #e87532 !important;
        }
    </style>
""", unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Drop your PDF or DOCX resume here or click to browse",
            type=["pdf", "docx"],
            help="Supported formats: PDF, DOCX",
            key="uploader_widget"
        )


        if uploaded_file:
            with st.spinner("Reading file..."):
                try:
                    if uploaded_file.type == "application/pdf":
                        extracted_text = extract_text_from_pdf(uploaded_file)
                    else:  # DOCX
                        # Reset file pointer to beginning
                        uploaded_file.seek(0)
                        extracted_text = extract_text_from_docx(uploaded_file)
                    
                    if not extracted_text or len(extracted_text.strip()) < 50:
                        st.error("⚠️ Could not extract enough text from the file. Please ensure:")
                        st.markdown("""
                        - The file is not corrupted
                        - The file contains actual text (not just images)
                        - The file is a valid PDF or DOCX format
                        """)
                        st.stop()
                    
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
                    st.info("💡 Try saving your resume as a different format or re-export it from your word processor.")
                    st.stop()

            st.markdown('<h3>Extracted Text Preview</h3>', unsafe_allow_html=True)
            st.text_area(
                "Extracted Content",
                value=extracted_text[:2000] + ("..." if len(extracted_text) > 2000 else ""),  # Preview first 2000 chars
                height=300,
                key="extracted_content_preview",
                label_visibility="collapsed"
            )
            
            # Show full text length
            st.caption(f"📊 Total characters extracted: {len(extracted_text)}")

            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with stylable_container("process-resume-btn", css_styles=PRIMARY_LARGE_BUTTON_STYLE):
                    if st.button("Process Resume", key="re-btn", width='stretch'):
                        if not extracted_text or len(extracted_text.strip()) < 50:
                            st.error("❌ Not enough text to process. Please upload a valid resume.")
                            st.stop()
                        
                        if 'logged_in_user' not in st.session_state or not st.session_state.logged_in_user:
                            st.error("⚠️ Session expired. Please login again.")
                            st.switch_page("app.py")

                        parsed_data = None
                        loading_placeholder = st.empty()
                        loading_placeholder.markdown("""
                            <div id="overlay-loader">
                                <div class="loader-spinner"></div>
                                <p>🤖 Analyzing your resume with AI...</p>
                            </div>
                            <style>
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
                                    color: #e87532 !important;
                                    font-size: 1.2rem;
                                    font-weight: 500;
                                }
                                .loader-spinner {
                                    border: 5px solid rgba(232, 117, 50, 0.2);
                                    border-top: 5px solid #e87532;
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
                            </style>
                        """, unsafe_allow_html=True)

                        try:
                            # Call your AI extraction function
                            parsed_data = extract_details_from_text(extracted_text)
                            
                            if not parsed_data:
                                raise ValueError("AI returned empty data")
                            
                        except Exception as e:
                            loading_placeholder.empty()
                            st.error(f"❌ Error during AI processing: {str(e)}")
                            
                            with st.expander("🔍 Debug Information"):
                                st.code(f"Error type: {type(e).__name__}")
                                st.code(f"Error message: {str(e)}")
                                st.code(f"Text length: {len(extracted_text)} characters")
                                st.code(f"First 500 chars:\n{extracted_text[:500]}")
                            
                            st.warning("💡 Try these solutions:")
                            st.markdown("""
                            1. **Use Manual Entry** - Click the Manual Entry option above
                            2. **Simplify your resume** - Remove complex formatting, tables, or images
                            3. **Try a different format** - Convert to plain text PDF
                            4. **Contact support** - If the issue persists
                            """)
                            parsed_data = None
                        
                        finally:
                            loading_placeholder.empty()
                        
                        if parsed_data:
                            # Store in session state
                            st.session_state.resume_source = parsed_data
                            st.session_state.resume_processed = True
                            st.session_state.input_method = "Upload Entry"
                            
                            # Check if coming from template button
                            if st.session_state.get('from_template_button'):
                                st.session_state.from_template_button = False
                                
                                # Set this so template_preview.py knows to use it
                                st.session_state.final_resume_data = parsed_data
                                
                                # Navigate to template preview
                                st.query_params.clear()
                                st.query_params["user"] = st.session_state.logged_in_user
                                st.success("✅ Resume processed! Redirecting to templates...")
                                time.sleep(0.5)
                                st.switch_page("pages/job.py")
                            else:
                                # Normal flow - save and go to job page
                                save_success = save_user_resume(
                                    st.session_state.logged_in_user,
                                    parsed_data,
                                    input_method="Upload Entry"
                                )

                                if save_success:
                                    st.success("✅ Resume processed and saved successfully!")
                                    st.balloons()
                                    time.sleep(1)
                                    st.query_params["user"] = st.session_state.logged_in_user
                                    st.switch_page("pages/job.py")
                                else:
                                    st.error("❌ Failed to save resume. Please try again.")
        else:
            st.info("👆 Please upload your resume to continue")
else:
    st.error("please login first")

# st.markdown('<div id="jd" style="scroll-margin-top: 100px;"></div>', unsafe_allow_html=True)
# if st.session_state.get("show_job_inside_main", False):
#     job()
#     st.stop() 
# if exsting:
#     job()
# if "show_job_inside_main" in st.session_state and st.session_state.show_job_inside_main:
#         job()
#         st.stop()   # Stop showing other sections