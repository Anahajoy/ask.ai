import streamlit as st
import os,json
from utils import get_score_color,get_score_label,ai_ats_score,analyze_and_improve_resume, should_regenerate_resume, generate_enhanced_resume, save_and_improve, add_new_item, render_basic_details, render_skills_section, render_generic_section
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(layout="wide", page_title="Dynamic ATS Resume Editor")

# PRESERVE USER SESSION - Get user from query params if not in session state
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


if os.path.exists("persist.json"):
    with open("persist.json", "r") as f:
        stored = json.load(f)
else:
    stored = {}

# ---------- Restore logged user ----------
from utils import get_user_resume  # or your resume fetch function

# ---------- RESUME STATE RESTORE ----------
if "resume_source" not in st.session_state or st.session_state.resume_source is None:
    resume_param = st.query_params.get("resume")
    if resume_param:  # resume passed via URL
        try:
            st.session_state.resume_source = json.loads(resume_param)
        except:
            st.session_state.resume_source = {}
    else:
        # Resume not in URL → try to fetch normally if user is logged in
        email = st.session_state.get("logged_in_user")
        if email:
            st.session_state.resume_source = get_user_resume(email)

# Save back resume to URL if valid
if st.session_state.get("resume_source"):
    st.query_params["resume"] = json.dumps(st.session_state.resume_source)

# ---------- JD STATE RESTORE ----------
if "job_description" not in st.session_state or st.session_state.job_description is None:
    jd_param = st.query_params.get("jd")
    if jd_param:
        try:
            st.session_state.job_description = json.loads(jd_param)
        except:
            st.session_state.job_description = {}
    else:
        st.session_state.job_description = st.session_state.get("job_description", {})



# Save JD back to URL
if st.session_state.get("job_description"):
    st.query_params["jd"] = json.dumps(st.session_state.job_description)

# ---------- ENHANCED RESUME STATE RESTORE ----------
if "enhanced_resume" not in st.session_state or st.session_state.enhanced_resume is None:
    enhanced_param = st.query_params.get("enhanced_resume")
    if enhanced_param:
        try:
            st.session_state.enhanced_resume = json.loads(enhanced_param)
        except:
            st.session_state.enhanced_resume = None

# ---------- RESTORE GENERATION METADATA ----------
if "last_resume_hash" not in st.session_state or st.session_state.last_resume_hash is None:
    st.session_state.last_resume_hash = st.query_params.get("last_resume_hash")

if "last_jd_hash" not in st.session_state or st.session_state.last_jd_hash is None:
    st.session_state.last_jd_hash = st.query_params.get("last_jd_hash")

if "last_resume_user" not in st.session_state or st.session_state.last_resume_user is None:
    st.session_state.last_resume_user = st.query_params.get("last_resume_user")

# ---------- SAVE ALL STATE BACK TO URL (Always sync to URL) ----------
if st.session_state.get("enhanced_resume"):
    st.query_params["enhanced_resume"] = json.dumps(st.session_state.enhanced_resume)

if st.session_state.get("last_resume_hash"):
    st.query_params["last_resume_hash"] = str(st.session_state.last_resume_hash)

if st.session_state.get("last_jd_hash"):
    st.query_params["last_jd_hash"] = str(st.session_state.last_jd_hash)

if st.session_state.get("last_resume_user"):
    st.query_params["last_resume_user"] = str(st.session_state.last_resume_user)



RESUME_ORDER = ["education", "experience", "skills", "projects", "certifications", "achievements"]

def apply_custom_css():
    """Applies improved dark theme with gradient accents."""
    st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarNav"] {display: none;}
    #MainMenu, footer, header, button[kind="header"] {visibility: hidden;}
     
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary-blue: #e87532;
        --primary-blue-hover: #1d4ed8;
        --secondary-blue: #3b82f6;
        --light-blue: #60a5fa;
        --accent-blue: #1e40af;
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --bg-card-hover: #283447;
        --text-white: #ffffff;
        --text-gray: #94a3b8;
        --text-light-gray: #cbd5e1;
        --text-blue: #60a5fa;
        --border-gray: #334155;
        --border-light: #475569;
        --success-green: #10b981;
        --warning-yellow: #f59e0b;
        --danger-red: #ef4444;
    }
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: #f8f9fa;
        min-height: 100vh;
    }
    
    /* Remove default Streamlit padding */
    .main .block-container {
        padding-top: 100px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }
    
    /* Panel Container Styling */
    .panel-container {
        height: calc(100vh - 120px);
        overflow-y: auto;
        overflow-x: hidden;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Left Panel - Narrower */
    .left-panel {
        background: #e87532;
        color: white;
    }
    
    .left-panel h1, .left-panel h2, .left-panel h3, .left-panel p, .left-panel label {
        color: #ffffff !important;
    }
    
    /* Middle Panel - Medium width */
    .middle-panel {
        background: white;
    }
    
    /* Right Panel - Wider */
    .right-panel {
        background: white;
    }
    
    /* Scrollbar Styling */
    .panel-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .panel-container::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.1);
        border-radius: 10px;
    }
    
    .panel-container::-webkit-scrollbar-thumb {
        background: #e87532;
        border-radius: 10px;
    }
    
    .panel-container::-webkit-scrollbar-thumb:hover {
        background: #d66829;
    }
    
    /* SIDEBAR BUTTONS */
    .left-panel .stButton > button {
        background: #ffffff !important;
        color: #e87532 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 1.3rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        margin-bottom: 0.6rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px rgba(255, 255, 255, 0.3) !important;
        text-transform: none !important;
        letter-spacing: 0.3px !important;
    }
    
    .left-panel .stButton > button:hover {
        background: #f8f9fa !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 255, 255, 0.4) !important;
        color: #d66829 !important;
    }
    
    /* Resume Section Styling */
    .resume-section {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .resume-section h2 {
        color: #1f2937 !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.2rem !important;
        padding-bottom: 0.8rem !important;
        border-bottom: 2px solid #e87532 !important;
        letter-spacing: 0.3px !important;
    }
    
    .resume-section h3 {
        color: #e87532 !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.8rem !important;
        letter-spacing: 0.2px !important;
    }
    
    /* Custom Section Header Styling */
    .custom-section-header {
        color: #1f2937 !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        text-transform: capitalize !important;
        letter-spacing: 0.3px !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }
    
    .custom-section-header::before {
        content: '📋';
        font-size: 1.2rem;
    }
    
    /* Item Titles & Subtitles */
    .resume-section .item-title {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: #1f2937 !important;
        margin-bottom: 0.4rem !important;
        display: block !important;
        letter-spacing: 0.2px !important;
    }

    .resume-section .item-subtitle {
        font-size: 1rem !important;
        color: #4b5563 !important;
        margin-bottom: 0.3rem !important;
        font-weight: 500 !important;
        display: block !important;
    }

    .resume-section .item-details {
        color: #6b7280 !important;
        margin-bottom: 0.5rem !important;
        font-size: 0.9rem !important;
        font-style: italic !important;
    }

    /* Bullet Lists */
    .resume-section .bullet-list {
        list-style-type: disc !important;
        margin: 0.6rem 0 !important;
        padding-left: 1.5rem !important;
        color: #374151 !important;
    }

    .resume-section .bullet-list li {
        color: #374151 !important;
        margin-bottom: 0.4rem !important;
        line-height: 1.6 !important;
        list-style-type: disc !important;
    }

    /* Skill Lists */
    .resume-section .skill-list {
        list-style-type: none !important;
        padding-left: 0 !important;
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 0.5rem !important;
    }

    .resume-section .skill-list li.skill-item {
        display: inline-flex !important;
        align-items: center !important;
        background: linear-gradient(135deg, rgba(232, 117, 50, 0.1) 0%, rgba(232, 117, 50, 0.05) 100%) !important;
        padding: 0.5rem 1rem !important;
        margin: 0 !important;
        border-radius: 8px !important;
        border: 1px solid rgba(232, 117, 50, 0.3) !important;
        color: #e87532 !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
    }
    
    .resume-section .skill-list li.skill-item:hover {
        background: linear-gradient(135deg, rgba(232, 117, 50, 0.2) 0%, rgba(232, 117, 50, 0.15) 100%) !important;
        border-color: rgba(232, 117, 50, 0.5) !important;
        transform: translateY(-2px);
    }

    /* Custom Section Content */
    .custom-section-content {
        background: #f9fafb !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 1.2rem !important;
        color: #374151 !important;
        font-size: 0.95rem !important;
        line-height: 1.7 !important;
        white-space: pre-line !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #ffffff !important;
        border: 2px solid #e5e7eb !important;
        border-radius: 8px !important;
        color: #1f2937 !important;
        padding: 0.75rem !important;
        font-size: 0.9rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #e87532 !important;
        box-shadow: 0 0 0 3px rgba(232, 117, 50, 0.1) !important;
        outline: none !important;
    }
    
    .stTextInput > label,
    .stTextArea > label {
        color: #374151 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.4rem !important;
    }
    
    /* Delete button styling */
    .stButton > button[kind="secondary"] {
        background: #9FC0DE !important;
        color: #ffffff !important;
        border: 1px solid #9FC0DE !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #ffffff !important;
        border-color: #9FC0DE !important;
        color : #9FC0DE !important;
    }

    .stButton > button[kind="primary"] {
        background: #e87532 !important;
        color: #ffffff !important;
        border: 1px solid #e87532 !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #ffffff !important;
        border-color: #e87532 !important;
        color: #e87532 !important;
    }

    /* LIVE PREVIEW MOCK UI BOX */
    .preview-box {
        width: 100%;
        height: 100%;
        background: #fff;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 15px;
    }
    
    .preview-header {
        font-size: 1rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 15px;
        text-align: center;
    }
    
    .preview-content {
        background: #fafafa;
        height: calc(100% - 50px);
        border-radius: 8px;
        border: 1px dashed #d1d5db;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #9ca3af;
        font-size: 0.9rem;
    }

    /* Navigation Bar */

    </style>
    """, unsafe_allow_html=True)

# Get current user and ensure it's preserved in session state
current_user = st.session_state.get('logged_in_user', '')
st.markdown("""
    <style>
      .nav-wrapper {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    max-width: 1200px;
    z-index: 99999 !important;
    background-color: white !important;
    padding: 0.8rem 2rem;
    box-shadow: 0 2px 20px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: 50px;
}

.logo {
    font-size: 24px;
    font-weight: 400;
    color: #2c3e50;
    font-family: 'Nunito Sans', sans-serif !important;
    letter-spacing: -0.5px;
}

.nav-menu {
    display: flex;
    gap: 2rem;
    align-items: center;
}

.nav-item { position: relative; }

.nav-link {
    color: #000000 !important;
    text-decoration: none !important;
    font-size: 1rem;
    font-family: 'Nunito Sans', sans-serif;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.nav-link:visited {
    color: #000000 !important;
}

.nav-link:hover {
    background-color: #fff5f0;
    color: #ff8c42 !important;  /* Added !important to override the default color */
}
    </style>
    """, unsafe_allow_html=True)
# Use f-string to properly interpolate the user variable
st.markdown(f"""
<div class="nav-wrapper">
    <div class="logo">Resume Creator</div>
    <div class="nav-menu">
        <div class="nav-item">
            <a class="nav-link" href="?home=true&user={current_user}" target="_self">Home</a>
        </div>
        <div class="nav-item">
             <a class="nav-link" href="?create=true&user={current_user}" target="_self">Create New Resume</a>
        </div>
        <div class="nav-item">
             <a class="nav-link" href="?addjd=true&user={current_user}" target="_self">Add New JD</a>
        </div>
        <div class="nav-item">
            <a class="nav-link" href="?logout=true" target="_self">Logout</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Handle navigation - PRESERVE USER IN SESSION STATE
if st.query_params.get("addjd") == "true":
    st.query_params.clear()
    st.query_params["user"] = current_user
    st.switch_page("pages/job.py")

if st.query_params.get("create") == "true":
    st.query_params.clear()
    st.query_params["user"] = current_user
    st.switch_page("pages/main.py")

if st.query_params.get("home") == "true":
    st.query_params.clear()
    st.query_params["user"] = current_user
    st.switch_page("app.py")

if st.query_params.get("logout") == "true":
    # Only clear session state on logout
    st.session_state.logged_in_user = None
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.switch_page("app.py")


import time

loading_placeholder = st.empty()

if should_regenerate_resume():
    loading_placeholder.markdown("""
        <div id="overlay-loader">
            <div class="loader-spinner"></div>
            <p>Please Wait...</p>
        </div>
        <style>
            #overlay-loader {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(6px);
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                z-index: 9999;
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

            #overlay-loader p {
                color: #1f2937;
                font-size: 1.1rem;
                letter-spacing: 0.5px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Run spinner for 5 seconds
    time.sleep(5)

    # Run your function AFTER the delay
    generate_enhanced_resume()

    # Remove spinner
    loading_placeholder.empty()

resume_data = st.session_state.get('enhanced_resume')
jd_data = st.session_state.get('job_description')

if resume_data and jd_data:
    try:
        st.session_state['ats_result'] = ai_ats_score(resume_data, jd_data)
        # st.write("✅ ATS Analysis Complete:", st.session_state['ats_result'])
    except Exception as e:
        st.error(f"❌ Error analyzing resume: {str(e)}")
        st.session_state['ats_result'] = {}

def get_standard_keys():
    """Return set of standard resume keys that should not be treated as custom sections."""
    return {
        "name", "email", "phone", "location", "url", "summary", "job_title",
        "education", "experience", "skills", "projects", "certifications", 
         "total_experience_count","input_method"
    }

def save_custom_sections():
    """Save custom section edits to session state."""
    data = st.session_state['enhanced_resume']
    standard_keys = get_standard_keys()
    
    # Update custom sections from session state (for edit mode)
    for key in list(data.keys()):
        if key not in standard_keys and isinstance(data.get(key), str):
            edit_key = f"edit_custom_{key}"
            if edit_key in st.session_state:
                data[key] = st.session_state[edit_key].strip()
    
    # Ensure all custom sections are preserved in the data
    st.session_state['enhanced_resume'] = data

def generate_and_switch():
    """Performs final analysis and switches to download page."""
    # Save any pending custom section edits
    save_custom_sections()
    
    data = st.session_state['enhanced_resume']
    
    # Extract custom sections before analysis
    standard_keys = get_standard_keys()
    custom_sections = {k: v for k, v in data.items() 
                      if k not in standard_keys and isinstance(v, str)}
    
    # Perform analysis
    finalized_data = analyze_and_improve_resume(data)
    
    # Re-add custom sections to finalized data
    for key, value in custom_sections.items():
        if key not in finalized_data:
            finalized_data[key] = value

    default_template = "Minimalist (ATS Best)"

    st.session_state.selected_template = default_template
    st.session_state.template_source = 'saved'
    st.session_state['final_resume_data'] = finalized_data

    # Set default template config
    from utils import SYSTEM_TEMPLATES  # make sure this import exists
    st.session_state.selected_template_config = SYSTEM_TEMPLATES.get(default_template)

    st.switch_page("pages/template_preview.py")


def flatten_custom_sections(data):
    """
    Converts nested custom_sections into top-level keys.
    Example: {"custom_sections": {"Languages": "..."}} → {"Languages": "..."}
    """
    if 'custom_sections' in data and isinstance(data['custom_sections'], dict):
        custom_sections = data.pop('custom_sections')
        for key, value in custom_sections.items():
            if key not in data:  # Don't overwrite existing keys
                data[key] = value
    return data

def main():
    apply_custom_css()
    data = st.session_state['enhanced_resume']
    
    # Flatten custom_sections if they exist
    data = flatten_custom_sections(data)
    st.session_state['enhanced_resume'] = data
    
    # Create 3 columns with different widths: narrow, medium, wider
    col1, col3 = st.columns([3.5, 6], gap="large")
    
    # LEFT PANEL - Tools Section
    with col1:
        with st.container():
            # st.markdown("<div class='panel-container left-panel'>", unsafe_allow_html=True)
            st.title("Resume Tools 🛠️")
            loading_placeholder = st.empty()
            # ========= PREMIUM ATS GAUGE ==========
            ats_data = st.session_state.get('ats_result', {})

            if ats_data and ats_data.get("overall_score", 0) > 0:
                score = ats_data.get("overall_score", 0)  # Changed from "score" to "overall_score"
                label = get_score_label(score)
                color = get_score_color(score)
                
                st.markdown(f"### ATS Score: {score}/100")
                st.markdown(f"**{label}**", unsafe_allow_html=True)
                st.markdown(f"""
                <div style="
                    text-align:center;
                    padding:15px;
                    margin-bottom:18px;
                    background:white;
                    border-radius:16px;
                    box-shadow:0 4px 12px rgba(0,0,0,0.08);
                    border:1px solid #e8e8e8;
                ">
                    <div style="position: relative; width:140px; height:140px; margin:auto;">
                        <svg width="140" height="140">
                            <circle cx="70" cy="70" r="60" stroke="#f0f0f0" stroke-width="12" fill="none"/>
                            <circle cx="70" cy="70" r="60"
                                stroke="{color}" stroke-width="12" fill="none"
                                stroke-linecap="round"
                                stroke-dasharray="{round(score*3.6)}, 360"
                                transform="rotate(-90 70 70)"
                            />
                            <text x="70" y="78" text-anchor="middle" font-size="28" font-weight="700" fill="#333">{score}%</text>
                        </svg>
                    </div>
                    <div style="font-size:15px; margin-top:8px; font-weight:600; color:#333;">
                        {label}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ================= Keyword Table Expander ====================
                with st.expander("🔎 View ATS Keyword Analysis"):
                    st.markdown("### 🟢 Matched Keywords")
                    # Changed from matched_keywords to matched_skills
                    matched = ats_data.get("matched_skills", [])
                    if matched:
                        st.write(", ".join(matched))
                    else:
                        st.write("None")
                    
                    st.markdown("### 🔴 Missing Keywords")
                    # Changed from missing_keywords to missing_skills
                    missing = ats_data.get("missing_skills", [])
                    if missing:
                        st.write(", ".join(missing))
                    else:
                        st.write("None")


            if st.button("✨ **Save & Auto-Improve**", type="primary", use_container_width=True):
                loading_placeholder.markdown("""
                    <div id="overlay-loader">
                        <div class="loader-spinner"></div>
                        <p>Performing auto-improvement...</p>
                    </div>
                    <style>
                        #overlay-loader {
                            position: fixed;
                            top: 0;
                            left: 0;
                            width: 100vw;
                            height: 100vh;
                            background: rgba(255, 255, 255, 0.95);
                            backdrop-filter: blur(6px);
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                            align-items: center;
                            z-index: 9999;
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

                        #overlay-loader p {
                            color: #1f2937;
                            font-size: 1.1rem;
                            letter-spacing: 0.5px;
                        }
                    </style>
                    """, unsafe_allow_html=True)

                save_custom_sections()
                save_and_improve()
                loading_placeholder.empty()
                
            if st.button("📄 **GENERATE RESUME**", type="primary", use_container_width=True):
                loading_placeholder.markdown("""
                    <div id="overlay-loader">
                        <div class="loader-spinner"></div>
                        <p>Generating your resume...</p>
                    </div>
                    <style>
                        #overlay-loader {
                            position: fixed;
                            top: 0;
                            left: 0;
                            width: 100vw;
                            height: 100vh;
                            background: rgba(255, 255, 255, 0.95);
                            backdrop-filter: blur(6px);
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                            align-items: center;
                            z-index: 9999;
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

                        #overlay-loader p {
                            color: #1f2937;
                            font-size: 1.1rem;
                            letter-spacing: 0.5px;
                        }
                    </style>
                    """, unsafe_allow_html=True)

                generate_and_switch()
                loading_placeholder.empty()

            st.markdown("---")

            is_edit_mode = st.checkbox("⚙️ **Enable Edit Mode**", key='edit_toggle')

            if not st.session_state.get('edit_toggle', False):
                st.info("⚠️ Enable Edit Mode to add new items.\n\nFor saving newly added content, disable Edit Mode after making changes.")
            else:
                st.markdown("---")
                st.subheader("➕ Add New Section Items")
                st.button(
                    "Add New Experience",
                    on_click=add_new_item,
                    args=('experience', {
                        "position": "New Job Title",
                        "company": "New Company",
                        "start_date": "2025-01-01",
                        "end_date": "2025-12-31",
                        "description": ["New responsibility 1."]
                    }),
                    type="secondary"
                )
                st.button(
                    "Add New Education",
                    on_click=add_new_item,
                    args=('education', {
                        "institution": "New University",
                        "degree": "New Degree",
                        "start_date": "2025-01-01",
                        "end_date": "2025-12-31"
                    }),
                    type="secondary"
                )
                st.button(
                    "Add New Certification",
                    on_click=add_new_item,
                    args=('certifications', {
                        "name": "New Certification Name",
                        "issuer": "Issuing Body",
                        "completed_date": "2025-01-01"
                    }),
                    type="secondary"
                )
                st.button(
                    "Add New Project",
                    on_click=add_new_item,
                    args=('projects', {
                        "name": "New Project Title",
                        "description": ["Project detail"]
                    }),
                    type="secondary"
                )
            st.markdown("</div>", unsafe_allow_html=True)
           
    # RIGHT PANEL - Live Preview
    with col3:
      
        with st.container():
            # st.markdown("<div class='panel-container middle-panel'>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align:center;color:#6b7280;margin-bottom:1.5rem;'>✏️ Content Editor</h3>", unsafe_allow_html=True)
            
            # Render basic details
            render_basic_details(data, is_edit=is_edit_mode)

            # Track rendered keys to avoid duplicates
            rendered_keys = set()
            standard_keys = get_standard_keys()
            
            # Render standard sections in order
            for key in RESUME_ORDER:
                if key in data and data[key]:
                    rendered_keys.add(key)
                    if key == "skills":
                        render_skills_section(data, is_edit=is_edit_mode)
                    else:
                        render_generic_section(key, data[key], is_edit=is_edit_mode)

            # Render other list-type sections that aren't in the standard order
            for key, value in data.items():
                if key not in rendered_keys and key not in standard_keys:
                    if isinstance(value, list) and value:
                        rendered_keys.add(key)
                        render_generic_section(key, value, is_edit=is_edit_mode)

            # Render Custom Text Sections (Languages, Licenses, etc.)
            for key, value in data.items():
                if key not in rendered_keys and key not in standard_keys and isinstance(value, str):
                    st.markdown(f"<div class='resume-section'>", unsafe_allow_html=True)
                    st.markdown(f"<h3 class='custom-section-header'>{key}</h3>", unsafe_allow_html=True)

                    if is_edit_mode:
                        new_val = st.text_area(
                            f"Edit {key}",
                            value=value.strip(),
                            key=f"edit_custom_{key}",
                            height=200,
                            help="Edit your custom section content here"
                        )

                        data[key] = new_val.strip()
                        st.session_state['enhanced_resume'] = data
                        
                        if st.button(f"🗑️ Delete '{key}' Section", key=f"delete_{key}", type="secondary"):
                            del data[key]
                            st.session_state['enhanced_resume'] = data
                            st.rerun()
                    else:
                        st.markdown(
                            f"<div class='custom-section-content'>{value.strip()}</div>",
                            unsafe_allow_html=True
                        )

                    st.markdown("</div>", unsafe_allow_html=True)
            
            

if __name__ == '__main__':
    if 'job_description' not in st.session_state or 'resume_source' not in st.session_state:
        st.error("Missing job description or resume source. Please go back to the main page.")
        if st.button("Go to Home"):
            switch_page("pages/main.py")
    else:
        main()