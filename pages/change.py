import streamlit as st
from utils import extract_details_from_text,extract_text_from_pdf,extract_text_from_docx
import time
from templates.templateconfig import SYSTEM_TEMPLATES,ATS_COLORS,load_css_template
# Page config
st.set_page_config(page_title="Resume Upload", layout="wide")




# Replace the entire CSS section in Document 2 with this:

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Archivo:wght@400;500;600;700;800;900&display=swap');
    
    /* ==================== RESET ==================== */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Hide Streamlit default elements */
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
        background: rgba(255, 255, 255, 0.98);
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
    
    /* Main Page Wrapper */
    .ats-main-wrapper {
        min-height: 30vh;
        background: linear-gradient(135deg, #fff9f5 0%, #ffffff 50%, #fff5f0 100%);
        padding: 110px 0 40px;
        position: relative;
        margin-bottom: 3rem;
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
    
    /* Hero Header */
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
        margin-left: 300px !important;
        line-height: 1.6;
        font-weight: 400;
    }
    
    /* Main Content Container */
    .main-container {
        max-width: 900px;
        margin: 0 auto 4rem auto;
        padding: 0 2rem;
    }
    
    /* Upload Section */
    .upload-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #f0f0f0;
        height: 100%;
    }
    
    .upload-icon-large {
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, #ff8c42 0%, #ffa666 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        margin: 0 auto 1.5rem auto;
    }
    
    .upload-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .upload-subtitle {
        font-size: 0.9rem;
        color: #64748b;
        text-align: center;
        line-height: 1.5;
        margin-bottom: 1.5rem;
    }
    
    /* Custom file uploader styling */
    .stFileUploader {
        margin-top: 1rem;
    }
    
    .stFileUploader > div {
        border: 2px dashed #d0d0d0 !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        background: #fafafa !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
    }
    
    .stFileUploader > div:hover {
        border-color: #ff8c42 !important;
        background: #fff5f0 !important;
        box-shadow: 0 4px 15px rgba(255, 140, 66, 0.1) !important;
    }
    
    .stFileUploader label {
        display: none !important;
    }
    
    /* Browse button styling */
    .stFileUploader button {
        background: #ff8c42 !important;
        border: none !important;
        color: white !important;
        padding: 0.5rem 1.5rem !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        margin-top: 0.5rem !important;
    }
    
    .stFileUploader button:hover {
        background: #ff7a29 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(255, 140, 66, 0.3) !important;
    }
    
    /* Panel header */
    .panel-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--border);
    }
    
    /* Preview header */
    .preview-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        text-align: center;
        margin: 3rem 0 2rem 0;
        padding-top: 2rem;
        border-top: 2px solid var(--border);
    }
    
    /* Success messages */
    .stSuccess {
        background: #f0fdf4 !important;
        border: 1px solid #86efac !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: white !important;
        border: 2px solid var(--border) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--primary) !important;
    }
    
    /* Download buttons */
    .stDownloadButton button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stDownloadButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px var(--shadow) !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .nav-container {
            padding: 0 1.5rem;
        }

        .nav-menu {
            gap: 0.5rem;
            flex-wrap: wrap;
            justify-content: center;
        }

        .nav-link {
            padding: 8px 12px;
            font-size: 13px;
        }
        
        .main-content {
            padding: 100px 1.5rem 60px;
        }
        
        .main-container {
            padding: 0 1rem;
        }
        
        .ats-main-title {
            font-size: 2rem;
        }
        
        .ats-hero-description {
            font-size: 0.9rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Update the navigation HTML to match the ResumeAI style:




def generate_resume_preview(parsed_data, template_name, color):
    """Generate CSS and HTML for resume preview"""
    if template_name in SYSTEM_TEMPLATES:
        template_config = SYSTEM_TEMPLATES[template_name]
        css = load_css_template(template_config['css_template'], color)
        html_content = template_config['html_generator'](parsed_data)
        return css, html_content
    return None, None

def update_preview_cache():
    """Update the cached preview HTML in session state"""
    if 'parsed_data' in st.session_state and st.session_state.parsed_data:
        css, html = generate_resume_preview(
            st.session_state.parsed_data,
            st.session_state.selected_template,
            st.session_state.preview_selected_color
        )
        if css and html:
            st.session_state.cached_css = css
            st.session_state.cached_html = html
            st.session_state.cached_full_html = f"""
            {css}
            <div class="ats-page">
                {html}
            </div>
            """

def generate_download_files():
    """Generate all download file formats"""
    if 'parsed_data' not in st.session_state or not st.session_state.parsed_data:
        return None
    
    parsed_data = st.session_state.parsed_data
    css = st.session_state.get('cached_css', '')
    html_content = st.session_state.get('cached_html', '')
    
    user_name = parsed_data.get('name', 'User').replace(' ', '_')
    
    # HTML Download
    html_doc = f"<html><head><meta charset='UTF-8'><style>{css}</style></head><body><div class='ats-page'>{html_content}</div></body></html>"
    
    # DOC Download
    doc_content = f"""
    <html xmlns:o='urn:schemas-microsoft-com:office:office'
    xmlns:w='urn:schemas-microsoft-com:office:word'
    xmlns='http://www.w3.org/TR/REC-html40'>
    <head>
        <meta charset='UTF-8'>
        <style>
            @page {{ size: 8.5in 11in; margin: 0.5in; }}
            {css}
        </style>
    </head>
    <body>
        <div class='ats-page'>{html_content}</div>
    </body>
    </html>
    """
    
    # TXT Download (you'll need to implement this function)
    # txt_content = generate_markdown_text(parsed_data)
    
    return {
        'html': {'data': html_doc, 'filename': f"Resume_{user_name}.html", 'mime': 'text/html'},
        'doc': {'data': doc_content, 'filename': f"Resume_{user_name}.doc", 'mime': 'application/msword'},
        # 'txt': {'data': txt_content, 'filename': f"Resume_{user_name}.txt", 'mime': 'text/plain'}
    }

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None

if "logged_in_user" not in st.session_state or st.session_state.logged_in_user is None:
    logged_user = st.query_params.get("user")
    if logged_user:
        st.session_state.logged_in_user = logged_user

if 'selected_template' not in st.session_state:
    st.session_state.selected_template = "Minimalist (ATS Best)"
    
if 'template_source' not in st.session_state:
    st.session_state.template_source = "system"

if 'preview_selected_color' not in st.session_state:
    st.session_state.preview_selected_color = ATS_COLORS["Professional Blue (Default)"]

# ============================================================================
# NAVIGATION
# ============================================================================

current_user = st.session_state.get('logged_in_user', '')
is_logged_in = bool(current_user)

if is_logged_in and current_user:
    home_url = f"/?user={current_user}"
    ats_url = f"ats?user={current_user}"
    qu_url = f"qu?user={current_user}"
else:
    home_url = "/"
    ats_url = "#ats"
    qu_url = "#qu"

if is_logged_in:
    auth_button = '<div class="nav-item"><a class="nav-link" href="?logout=true" target="_self">⏻</a></div>'
else:
    auth_button = '<div class="nav-item"><a class="nav-link" data-section="Login" href="#Login">Login</a></div>'

st.markdown(f"""
<div class="nav-wrapper">
    <div class="nav-container">
        <div class="logo">CVmate</div>
        <div class="nav-menu">
            <a class="nav-link" href="{home_url}" target="_self">Home</a>
            <a class="nav-link" href="main?&user={current_user}" target="_self">Create New Resume</a>
            <a class="nav-link" href="{ats_url}" target="_self">Check ATS Score</a>
            <a class="nav-link" href="{qu_url}" target="_self">Analysis Assistant</a>
            {auth_button}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


if st.query_params.get("logout") == "true":
    st.session_state.logged_in_user = None
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.rerun()

# ============================================================================
# HERO SECTION
# ============================================================================

st.markdown("""
<div class="ats-main-wrapper">
    <div class="ats-hero">
        <div class="ats-hero-badge">✨ Change your Resume Template</div>
        <h1 class="ats-main-title">ATS Friendly <span class="highlight">Templates</span></h1>
        <p class="ats-hero-description">
            Upload your resume and choose from a variety of professionally designed, ATS-optimized templates to make your application stand out.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.markdown('<div class="main-container">', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

# Add to session state initialization section
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

if 'parsed_data' not in st.session_state:
    st.session_state.parsed_data = None

if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None

# Replace the file upload section in col1:
with col1:
    st.markdown("""
    <div class="upload-card">
        <div class="upload-icon-large">📄</div>
        <h2 class="upload-title">Drag and drop file to upload</h2>
        <p class="upload-subtitle">or browse to choose a file</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload file",
        type=['pdf', 'docx', 'doc'],
        label_visibility="collapsed"
    )
    
    # Only process if file is new or different
    if uploaded_file is not None:
        current_file_name = uploaded_file.name
        
        # Check if this is a new file (different from last uploaded)
        if current_file_name != st.session_state.uploaded_file_name:
            with st.spinner("Processing resume..."):
                try:
                    # Extract text based on file type
                    if uploaded_file.type == "application/pdf":
                        extracted_text = extract_text_from_pdf(uploaded_file)
                    else:
                        uploaded_file.seek(0)
                        extracted_text = extract_text_from_docx(uploaded_file)
                    
                    # Parse the extracted text
                    parsed_data = extract_details_from_text(extracted_text)
                    
                    # Update session state
                    st.session_state.parsed_data = parsed_data
                    st.session_state.resume_text = extracted_text
                    st.session_state.uploaded_file_name = current_file_name
                    
                    if parsed_data:
                        # Check if user is logged in
                        if st.session_state.get('logged_in_user'):
                            st.query_params["user"] = st.session_state.logged_in_user
                            st.success("✅ Resume processed successfully!")
                            
                            # Update the preview cache
                            update_preview_cache()
                            st.rerun()
                        else:
                            st.warning("⚠️ Please login first")
                    else:
                        st.error("❌ Failed to process resume")
                        st.session_state.uploaded_file_name = None
                        
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
                    st.session_state.uploaded_file_name = None
        else:
            # File already processed, show status
            if st.session_state.parsed_data:
                st.success(f"✅ Currently using: {current_file_name}")
    else:
        # No file uploaded, clear the session state
        if st.session_state.uploaded_file_name is not None:
            st.session_state.uploaded_file_name = None
            st.session_state.parsed_data = None
            st.session_state.resume_text = None

with col2:
    # st.markdown('<div class="panel-header">Colors</div>', unsafe_allow_html=True)
    
    # Get current color index
    current_color_list = list(ATS_COLORS.keys())
    try:
        current_color_index = [i for i, (k, v) in enumerate(ATS_COLORS.items()) 
                               if v == st.session_state.preview_selected_color][0]
    except:
        current_color_index = 0
    
    color_name = st.selectbox(
        'Choose Accent Color:',
        current_color_list,
        index=current_color_index,
        key='preview_color_select'
    )
    
    new_color = ATS_COLORS[color_name]
    if new_color != st.session_state.preview_selected_color:
        st.session_state.preview_selected_color = new_color
        update_preview_cache()
        st.rerun()
    
    st.markdown(f"""
    <div style="width: 70px; height: 70px; background: {new_color}; 
        border-radius: 50%; margin: 10px auto;
        border: 3px solid #333;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);"></div>
    """, unsafe_allow_html=True)
    
    st.markdown('<br>', unsafe_allow_html=True)
    # st.markdown('</div>', unsafe_allow_html=True)
    # st.markdown('<div class="panel-header">📋 Template Selection</div>', unsafe_allow_html=True)
    
    # st.markdown(f"""
    # <div class="template-box">
    #     <div class="template-name">{st.session_state.selected_template}</div>
    #     <div style="font-size: 0.8rem; color: #666; margin-top: 0.3rem;">
    #         {st.session_state.template_source.replace('_', ' ').title()}
    #     </div>
    # </div>
    # """, unsafe_allow_html=True)
    
    system_template_names = list(SYSTEM_TEMPLATES.keys())
    
    try:
        current_index = system_template_names.index(st.session_state.selected_template)
    except (ValueError, AttributeError):
        current_index = 0
    
    selected_system_template = st.selectbox(
        "Select a System Template:",
        system_template_names,
        index=current_index,
        key="system_template_dropdown",
        help="Choose a template from our professionally designed collection"
    )
    
    if selected_system_template != st.session_state.selected_template:
        st.session_state.selected_template = selected_system_template
        st.session_state.template_source = 'system'
        st.query_params["template"] = selected_system_template
        st.query_params["source"] = 'system'
        
        # Update the preview cache
        update_preview_cache()
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================================================
    # DOWNLOAD SECTION
    # ============================================================================
    
    if 'parsed_data' in st.session_state and st.session_state.parsed_data:
        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown('<div class="panel-header">📥 Download Resume</div>', unsafe_allow_html=True)
        
        download_files = generate_download_files()
        
        if download_files:
            # HTML Download
            st.download_button(
                label="📄 Download HTML",
                data=download_files['html']['data'].encode('utf-8'),
                file_name=download_files['html']['filename'],
                mime=download_files['html']['mime'],
                width='stretch',
                key="download_html"
            )
            
            # DOC Download
            st.download_button(
                label="📑 Download DOC",
                data=download_files['doc']['data'].encode('utf-8'),
                file_name=download_files['doc']['filename'],
                mime=download_files['doc']['mime'],
                width='stretch',
                key="download_doc"
            )
            
            # Uncomment when you add TXT generation
            # st.download_button(
            #     label="📝 Download TXT",
            #     data=download_files['txt']['data'].encode('utf-8'),
            #     file_name=download_files['txt']['filename'],
            #     mime=download_files['txt']['mime'],
            #     width=True,
            #     key="download_txt"
            # )
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# PREVIEW SECTION
# ============================================================================

st.markdown('<div class="preview-header">Resume Preview</div>', unsafe_allow_html=True)

if 'cached_full_html' in st.session_state and st.session_state.cached_full_html:
    preview_container = st.container()
    with preview_container:
        # Force iframe reload with unique comment
        st.markdown(
            f'<!-- color: {st.session_state.preview_selected_color} template: {st.session_state.selected_template} -->', 
            unsafe_allow_html=True
        )
        st.components.v1.html(st.session_state.cached_full_html, height=1000, scrolling=True)
else:
    st.info("📤 Please upload a resume file to see the preview")