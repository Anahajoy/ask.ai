import streamlit as st
from utils import analyze_and_improve_resume, should_regenerate_resume, generate_enhanced_resume, save_and_improve, add_new_item, render_basic_details, render_skills_section, render_generic_section
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(layout="centered", page_title="Dynamic ATS Resume Editor")

if should_regenerate_resume():
    # loading_placeholder = st.empty()
    
    # loading_placeholder.markdown("""
    #     <div class="fullscreen-loader">
    #         <div class="loader-content">
    #             <div class="loader-spinner"></div>
    #             <h2>Generating Optimized Resume</h2>
    #             <p>Please wait while we optimize your content...</p>
    #         </div>
    #     </div>
        
    #     <style>
    #         /* Full-screen overlay covering everything including sidebar */
    #         .fullscreen-loader {
    #             position: fixed;
    #             top: 0;
    #             left: 0;
    #             width: 100vw;
    #             height: 100vh;
    #             background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
    #             display: flex;
    #             justify-content: center;
    #             align-items: center;
    #             z-index: 999999 !important;
    #             animation: fadeIn 0.3s ease-in;
    #         }
            
    #         @keyframes fadeIn {
    #             from { opacity: 0; }
    #             to { opacity: 1; }
    #         }
            
    #         .loader-content {
    #             text-align: center;
    #             animation: slideUp 0.5s ease-out;
    #         }
            
    #         @keyframes slideUp {
    #             from {
    #                 opacity: 0;
    #                 transform: translateY(30px);
    #             }
    #             to {
    #                 opacity: 1;
    #                 transform: translateY(0);
    #             }
    #         }
            
    #         /* Spinner */
    #         .loader-spinner {
    #             width: 80px;
    #             height: 80px;
    #             margin: 0 auto 30px;
    #             border: 6px solid rgba(96, 165, 250, 0.2);
    #             border-top: 6px solid #3b82f6;
    #             border-radius: 50%;
    #             animation: spin 1s linear infinite;
    #         }
            
    #         @keyframes spin {
    #             0% { transform: rotate(0deg); }
    #             100% { transform: rotate(360deg); }
    #         }
            
    #         /* Text styling */
    #         .fullscreen-loader h2 {
    #             color: #ffffff;
    #             font-size: 2rem;
    #             font-weight: 700;
    #             margin: 0 0 15px 0;
    #             font-family: 'Inter', sans-serif;
    #             letter-spacing: -0.5px;
    #         }
            
    #         .fullscreen-loader p {
    #             color: #94a3b8;
    #             font-size: 1.1rem;
    #             font-weight: 400;
    #             margin: 0;
    #             font-family: 'Inter', sans-serif;
    #         }
    #     </style>
    # """, unsafe_allow_html=True)
    generate_enhanced_resume()
    # loading_placeholder.empty()

RESUME_ORDER = ["education", "experience", "skills", "projects", "certifications", "achievements"]

def apply_custom_css():
    """Applies improved dark theme with gradient accents."""
    st.markdown("""
    <style>
     
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary-blue:  #e87532;
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
        background: #ffffff;
        min-height: 100vh;
       
    }
    [data-testid="stSidebarNav"] {
            display: none !important;
        }
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid var(--border-gray);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #000000 !important;
    }
    
    /* SIDEBAR BUTTONS */
    [data-testid="stSidebar"] .stButton > button {
        background:  #e87532 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 1.3rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        margin-bottom: 0.6rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4) !important;
        text-transform: none !important;
        letter-spacing: 0.3px !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #ffffff !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5) !important;
        color: #e87532 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:active {
        transform: translateY(0px);
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3) !important;
    }
    
    [data-testid="stSidebar"] .stCheckbox {
        color: var(--text-white) !important;
        margin: 0.8rem 0 !important;
    }
    
    [data-testid="stSidebar"] .stCheckbox label {
        color: var(--text-white) !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: var(--border-gray) !important;
        opacity: 0.4;
        margin: 1.5rem 0 !important;
    }
    
    /* Sidebar Subheaders */
    [data-testid="stSidebar"] .stMarkdown h3 {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: var(--text-blue) !important;
        margin-bottom: 1rem !important;
        margin-top: 0.5rem !important;
    }
    
    /* Main Content Area */
    .main-content {
        max-width: 950px;
        margin: 0 auto;
        padding: 2.5rem 2rem;
    }
    
    
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    .resume-section h2 {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.8rem !important;
        border-bottom: 2px solid var(--border-gray) !important;
        letter-spacing: 0.5px !important;
    }
    
    .resume-section h3 {
        color:  #e87532 !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
        letter-spacing: 0.3px !important;
    }
    
    /* Custom Section Header Styling */
    .custom-section-header {
        color: var(--text-white) !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.2rem !important;
        text-transform: capitalize !important;
        letter-spacing: 0.5px !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }
    
    .custom-section-header::before {
        content: '📋';
        font-size: 1.3rem;
    }
    
    /* Item Titles & Subtitles */
    .resume-section .item-title {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        margin-bottom: 0.5rem !important;
        display: block !important;
        letter-spacing: 0.3px !important;
    }

    .resume-section .item-subtitle {
        font-size: 1.15rem !important;
        color:#ffffff !important;
        margin-bottom: 0.4rem !important;
        font-weight: 500 !important;
        display: block !important;
    }

    .resume-section .item-details {
        color: var(--text-gray) !important;
        margin-bottom: 0.6rem !important;
        font-size: 0.95rem !important;
        font-style: italic !important;
    }

    /* Bullet Lists */
    .resume-section .bullet-list {
        list-style-type: disc !important;
        margin: 0.8rem 0 !important;
        padding-left: 1.8rem !important;
        color: var(--text-light-gray) !important;
    }

    .resume-section .bullet-list li {
        color: var(--text-light-gray) !important;
        margin-bottom: 0.5rem !important;
        line-height: 1.7 !important;
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
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.15) 0%, rgba(59, 130, 246, 0.1) 100%) !important;
        padding: 0.5rem 1rem !important;
        margin: 0 !important;
        border-radius: 8px !important;
        border: 1px solid rgba(96, 165, 250, 0.3) !important;
        color: var(--text-blue) !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
    }
    
    .resume-section .skill-list li.skill-item:hover {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.25) 0%, rgba(59, 130, 246, 0.2) 100%) !important;
        border-color: rgba(96, 165, 250, 0.5) !important;
        transform: translateY(-2px);
    }

    /* Custom Section Content */
    .custom-section-content {
        background: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid var(--border-gray) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        color: var(--text-light-gray) !important;
        font-size: 1rem !important;
        line-height: 1.8 !important;
        white-space: pre-line !important;
    }

    /* Higher specificity for Streamlit containers */
    [data-testid="stHorizontalBlock"] .item-subtitle,
    div.element-container .item-subtitle,
    .stMarkdown .item-subtitle {
        font-size: 1.15rem !important;
        color: var(--secondary-blue) !important;
        margin-bottom: 0.4rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stHorizontalBlock"] .bullet-list,
    div.element-container .bullet-list,
    .stMarkdown .bullet-list {
        list-style-type: disc !important;
        padding-left: 1.8rem !important;
    }

    [data-testid="stHorizontalBlock"] .bullet-list li,
    div.element-container .bullet-list li,
    .stMarkdown .bullet-list li {
        color: var(--text-light-gray) !important;
        line-height: 1.7 !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg-dark) !important;
        border: 2px solid var(--border-gray) !important;
        border-radius: 12px !important;
        color: var(--text-white) !important;
        padding: 0.9rem !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-blue) !important;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.15) !important;
        outline: none !important;
    }
    
    .stTextInput > label,
    .stTextArea > label {
        color: var(--text-blue) !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Info/Warning/Error Messages */
    .stAlert {
        border-radius: 12px !important;
        border-left: 4px solid var(--primary-blue) !important;
        background: rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-gray);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--border-light);
    }
    
    /* Delete button styling */
    .stButton > button[kind="secondary"] {
        background: rgba(239, 68, 68, 0.1) !important;
        color: var(--danger-red) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(239, 68, 68, 0.2) !important;
        border-color: var(--danger-red) !important;
    }
    
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
    background-color: #f8fafc;
    color:  #e87532;
}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class="nav-wrapper">
    <div class="logo">Resume Creator</div>
    <div class="nav-menu">
        <div class="nav-item">
            <a class="nav-link" href="?home=true" target="_self">Home</a>
        </div>
        <div class="nav-item">
            <a class="nav-link" data-section="About" href="#About">About</a>
        </div>
        <div class="nav-item">
            <a class="nav-link" data-section="Resume" href="#Resume">Resume</a>
        </div>
        <div class="nav-item">
            <a class="nav-link" data-section="Portfolio" href="#Portfolio">Portfolio</a>
        </div>
        <div class="nav-item">
            <a class="nav-link" data-section="Login" href="#Login">Login</a>
        </div>
        <div class="nav-item">
            <a class="nav-link" href="?logout=true" target="_self">Logout</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

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
    
    st.session_state['final_resume_data'] = finalized_data
    st.switch_page("pages/download.py")

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

    st.sidebar.title("Resume Tools 🛠️")
    loading_placeholder = st.empty()

    if st.sidebar.button("✨ **Save & Auto-Improve**",type="primary", use_container_width=True):
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
                    background: #ffffff;
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

        # Save custom sections before auto-improve
        save_custom_sections()
        save_and_improve()
        loading_placeholder.empty()
        
    if st.sidebar.button("📄 **GENERATE RESUME**", type="primary", use_container_width=True):
        loading_placeholder.markdown("""
            <div id="overlay-loader">
                <div class="loader-spinner"></div>
                <p>Performing final analysis and generating download data...</p>
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

        generate_and_switch()
        loading_placeholder.empty()

    st.sidebar.markdown("---")

    is_edit_mode = st.sidebar.checkbox("⚙️ **Enable Edit Mode**", key='edit_toggle')

    if not st.session_state.get('edit_toggle', False):
        st.sidebar.info("⚠️ Enable Edit Mode to add new items.\n\nFor saving newly added content, disable Edit Mode after making changes.")
    else:
        st.sidebar.markdown("---")
        st.sidebar.subheader("➕ Add New Section Items")
        st.sidebar.button(
            "Add New Experience",
            on_click=add_new_item,
            args=('experience', {
                "position": "New Job Title",
                "company": "New Company",
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
                "description": ["New responsibility 1."]
            }),
            type="primary"
        )
        st.sidebar.button(
            "Add New Education",
            on_click=add_new_item,
            args=('education', {
                "institution": "New University",
                "degree": "New Degree",
                "start_date": "2025-01-01",
                "end_date": "2025-12-31"
            }),
            type="primary"
        )
        st.sidebar.button(
            "Add New Certification",
            on_click=add_new_item,
            args=('certifications', {
                "name": "New Certification Name",
                "issuer": "Issuing Body",
                "completed_date": "2025-01-01"
            }),
            type="primary"
        )
        st.sidebar.button(
            "Add New Project",
            on_click=add_new_item,
            args=('projects', {
                "name": "New Project Title",
                "description": ["Project detail"]
            }),
            type="primary"
        )

        st.sidebar.markdown("---")
        # st.sidebar.subheader("📝 Custom Section Management")
        # new_section_key = st.sidebar.text_input("Add a New Section (e.g., 'Languages', 'Licenses')")
        # if st.sidebar.button("➕ Add Custom Section", use_container_width=True):
        #     if new_section_key and new_section_key.strip():
        #         clean_key = new_section_key.strip()
                
        #         if clean_key not in data:
        #             data[clean_key] = "Enter your content here..."
        #             st.session_state['enhanced_resume'] = data
        #             st.sidebar.success(f"✅ Added '{clean_key}' section!")
        #             st.rerun()
        #         else:
        #             st.sidebar.warning(f"⚠️ Section '{clean_key}' already exists")
        #     else:
        #         st.sidebar.error("❌ Please enter a section name")

    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Regenerate from Source", use_container_width=True):
        if 'enhanced_resume' in st.session_state:
            del st.session_state['enhanced_resume']
        if 'last_resume_hash' in st.session_state:
            del st.session_state['last_resume_hash']
        if 'ats_score_data' in st.session_state:
            del st.session_state['ats_score_data']
        st.switch_page("pages/main.py")

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

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

    # Render Custom Text Sections (Languages, Licenses, etc.) - These are top-level string keys
    for key, value in data.items():
        if key not in rendered_keys and key not in standard_keys and isinstance(value, str):
            st.markdown(f"<div class='resume-section'>", unsafe_allow_html=True)
            st.markdown(f"<h3 class='custom-section-header'>{key}</h3>", unsafe_allow_html=True)

            if is_edit_mode:
                # Editable text area for custom section
                new_val = st.text_area(
                    f"Edit {key}",
                    value=value.strip(),
                    key=f"edit_custom_{key}",
                    height=200,
                    help="Edit your custom section content here"
                )

                # Real-time update
                data[key] = new_val.strip()
                st.session_state['enhanced_resume'] = data
                
                # Delete button for custom sections
                if st.button(f"🗑️ Delete '{key}' Section", key=f"delete_{key}", type="secondary"):
                    del data[key]
                    st.session_state['enhanced_resume'] = data
                    st.rerun()
            else:
                # Display static view mode with improved styling
                st.markdown(
                    f"<div class='custom-section-content'>{value.strip()}</div>",
                    unsafe_allow_html=True
                )

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    if 'job_description' not in st.session_state or 'resume_source' not in st.session_state:
        st.error("Missing job description or resume source. Please go back to the main page.")
        if st.button("Go to Home"):
            switch_page("main")
    else:
        main()