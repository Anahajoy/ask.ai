import streamlit as st
import base64
from datetime import datetime
from utils import get_user_resume
from pages.download import (
    SYSTEM_TEMPLATES, 
    ATS_COLORS, 
    generate_generic_html,
    generate_markdown_text
)

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="Template Preview",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------------
# RESTORE USER FROM QUERY PARAMS
# ----------------------------------
if "logged_in_user" not in st.session_state or st.session_state.logged_in_user is None:
    logged_user = st.query_params.get("user")
    if logged_user:
        st.session_state.logged_in_user = logged_user
        st.query_params["user"] = logged_user
    else:
        st.session_state.logged_in_user = None
else:
    if st.session_state.logged_in_user:
        st.query_params["user"] = st.session_state.logged_in_user

# ----------------------------------
# HANDLE NAVIGATION FIRST
# ----------------------------------
if st.query_params.get("logout") == "true":
    st.session_state.logged_in_user = None
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.switch_page("app.py")

if st.query_params.get("app") == "true":
    if "app" in st.query_params:
        del st.query_params["app"]
    if st.session_state.logged_in_user:
        st.query_params["user"] = st.session_state.logged_in_user
    st.switch_page("app.py")

# ----------------------------------
# CHECK LOGIN
# ----------------------------------
if not st.session_state.get('logged_in_user'):
    st.error("Please login first to view templates")
    st.stop()

# ----------------------------------
# GET USER EMAIL AND RESUME
# ----------------------------------
email = st.session_state.logged_in_user
user_resume = get_user_resume(email)
has_resume = user_resume and len(user_resume) > 0

if not has_resume:
    st.warning("No resume found. Please create a resume first.")
    if st.button("Create Resume"):
        st.query_params["user"] = email
        st.switch_page("pages/main.py")
    st.stop()

# ----------------------------------
# GET SELECTED TEMPLATE INFO
# ----------------------------------
selected_template = st.session_state.get('selected_template')
selected_config = st.session_state.get('selected_template_config')
template_source = st.session_state.get('template_source', 'system')

if not selected_template or not selected_config:
    st.warning("No template selected. Please select a template first.")
    st.stop()

# ----------------------------------
# CUSTOM CSS
# ----------------------------------
st.markdown("""
<style>
#MainMenu, footer, header, button[kind="header"] {visibility: hidden;}

:root {
    --primary-orange: #e87532;
    --primary-dark: #d66629;
    --light-bg: #fff5f2;
    --border-color: #ffe5d9;
}

/* Top Navigation Bar */
.top-nav {
    background: white;
    padding: 1rem 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin-bottom: 2rem;
    border-radius: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--primary-orange);
}

.nav-buttons {
    display: flex;
    gap: 1rem;
}

/* Main Layout */
.main-container {
    display: grid;
    grid-template-columns: 400px 1fr;
    gap: 2rem;
    margin-top: 1rem;
}

/* Left Panel */
.left-panel {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    height: fit-content;
}

.panel-section {
    margin-bottom: 2rem;
}

.section-title {
    color: var(--primary-orange);
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.info-row {
    margin: 0.5rem 0;
    font-size: 0.9rem;
}

.info-label {
    font-weight: 600;
    color: #666;
}

.info-value {
    color: var(--primary-orange);
}

/* Download Panel */
.download-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.8rem;
    margin-top: 1rem;
}

/* Color Selector */
.color-selector-box {
    background: var(--light-bg);
    padding: 1.5rem;
    border-radius: 8px;
    border: 2px solid var(--border-color);
}

/* Right Panel - Preview */
.preview-panel {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    max-height: 85vh;
    overflow-y: auto;
}

.preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--border-color);
}

.preview-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--primary-orange);
}

/* Buttons */
.stButton > button {
    background: var(--primary-orange) !important;
    color: white !important;
    border: none !important;
    padding: 10px 20px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: var(--primary-dark) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(232, 117, 50, 0.3) !important;
}

.stDownloadButton > button {
    background: var(--primary-orange) !important;
    color: white !important;
    border: none !important;
    padding: 10px 20px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
}

.stDownloadButton > button:hover {
    background: var(--primary-dark) !important;
    transform: translateY(-2px);
}

/* Selectbox */
.stSelectbox > div > div {
    border: 2px solid var(--border-color) !important;
    border-radius: 8px !important;
}

.stSelectbox label {
    color: var(--primary-orange) !important;
    font-weight: 600 !important;
}

/* iframe preview */
iframe {
    border: 2px solid var(--border-color);
    border-radius: 8px;
    width: 100%;
}

/* Preview color box */
.color-preview-box {
    width: 100%;
    height: 50px;
    border-radius: 8px;
    border: 2px solid var(--border-color);
    margin-top: 0.5rem;
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
    color: #e87532;
}

    
.logo {
    font-size: 24px;
    font-weight: 400;
    color: #2c3e50;
    font-family: 'Nunito Sans', sans-serif !important;
    letter-spacing: -0.5px;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------
# TOP NAVIGATION
# ----------------------------------
current_user = st.session_state.get('logged_in_user', '') or st.query_params.get('user', '')
st.markdown("""
<div class="nav-wrapper">
    <div class="logo">Resume Creator</div>
    <div class="nav-menu">
        <div class="nav-item">
            <a class="nav-link" href="?app=true&user={current_user}" target="_self">Home</a>
        </div>
        <div class="nav-item">
            <a class="nav-link" href="?logout=true" target="_self">Logout</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)



# ----------------------------------
# MAIN LAYOUT - TWO COLUMNS
# ----------------------------------
left_col, right_col = st.columns([1, 2])

# ----------------------------------
# LEFT PANEL
# ----------------------------------
with left_col:
 
    
    # Template Information
    st.markdown(f"""
    <div class="panel-section">
        <div class="section-title">📋 Template Information</div>
        <div class="info-row"><span class="info-label">Template:</span> <span class="info-value">{selected_template}</span></div>
        <div class="info-row"><span class="info-label">Owner:</span> {user_resume.get('name', 'Not specified')}</div>
        <div class="info-row"><span class="info-label">Last Modified:</span> {datetime.now().strftime('%B %d, %Y')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Color Selection (Only for system templates)
    if template_source == 'system':
        st.markdown('<div class="section-title">🎨 Choose Accent Color</div>', unsafe_allow_html=True)
        
        color_name = st.selectbox(
            'Select Color:',
            list(ATS_COLORS.keys()),
            key='color_select',
            index=0
        )
        primary_color = ATS_COLORS[color_name]
        st.session_state.preview_selected_color = primary_color
        
        st.markdown(f"""
        <div class="color-preview-box" style="background: {primary_color};">
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Download Panel
    st.markdown('<div class="section-title">📥 Template Panel</div>', unsafe_allow_html=True)
    
    if template_source == 'system':
        selected_color = st.session_state.get('preview_selected_color', ATS_COLORS["Professional Blue (Default)"])
        css = selected_config['css_generator'](selected_color)
        html_content = selected_config['html_generator'](user_resume)
        
        col1, col2 = st.columns(2)
        
        # HTML Download
        with col1:
            full_doc = f"<html><head><meta charset='UTF-8'><style>{css}</style></head><body><div class='ats-page'>{html_content}</div></body></html>"
            html_filename = f"Resume_{user_resume.get('name', 'User').replace(' ', '_')}.html"
            st.download_button(
                label="📄 HTML",
                data=full_doc.encode('utf-8'),
                file_name=html_filename,
                mime="text/html",
                use_container_width=True,
                key="download_html"
            )
        
        # DOC Download
        with col2:
            word_doc = f"""
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
            doc_filename = f"Resume_{user_resume.get('name', 'User').replace(' ', '_')}.doc"
            st.download_button(
                label="📑 DOC",
                data=word_doc.encode('utf-8'),
                file_name=doc_filename,
                mime="application/msword",
                use_container_width=True,
                key="download_doc"
            )
        
        # PDF and TXT Download
        col3, col4 = st.columns(2)
        
        with col3:
            txt_content = generate_markdown_text(user_resume)
            txt_filename = f"Resume_{user_resume.get('name', 'User').replace(' ', '_')}.txt"
            st.download_button(
                label="📝 TXT",
                data=txt_content.encode('utf-8'),
                file_name=txt_filename,
                mime="text/plain",
                use_container_width=True,
                key="download_txt"
            )
    
    elif template_source in ['saved', 'temp_upload']:
        css = selected_config.get('css', '')
        html_content = generate_generic_html(user_resume)
        full_doc = f"<html><head><meta charset='UTF-8'><style>{css}</style></head><body><div class='ats-page'>{html_content}</div></body></html>"
        html_filename = f"Resume_{user_resume.get('name', 'User').replace(' ', '_')}.html"
        
        st.download_button(
            label="📄 Download HTML",
            data=full_doc.encode('utf-8'),
            file_name=html_filename,
            mime="text/html",
            use_container_width=True,
            key="download_html_custom"
        )
    
    elif template_source == 'doc_saved' and st.session_state.get('generated_doc'):
        doc_filename = f"Resume_{user_resume.get('name', 'Resume').replace(' ', '_')}.docx"
        st.download_button(
            label="📄 Download DOCX",
            data=st.session_state.generated_doc,
            file_name=doc_filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key="download_docx"
        )
    
    elif template_source == 'ppt_saved' and st.session_state.get('generated_ppt'):
        ppt_filename = f"Resume_{user_resume.get('name', 'Presentation').replace(' ', '_')}.pptx"
        st.download_button(
            label="📊 Download PPTX",
            data=st.session_state.generated_ppt,
            file_name=ppt_filename,
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True,
            key="download_pptx"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------
# RIGHT PANEL - PREVIEW
# ----------------------------------
with right_col:
   
    st.markdown('<div class="preview-title">Resume Preview</div>', unsafe_allow_html=True)
    
    # Generate preview based on template type
    if template_source == 'system':
        selected_color = st.session_state.get('preview_selected_color', ATS_COLORS["Professional Blue (Default)"])
        css = selected_config['css_generator'](selected_color)
        html_content = selected_config['html_generator'](user_resume)
        
        full_html = f"""
        {css}
        <div class="ats-page">
            {html_content}
        </div>
        """
        st.components.v1.html(full_html, height=1000, scrolling=True)
    
    elif template_source in ['saved', 'temp_upload']:
        css = selected_config.get('css', '')
        html_content = generate_generic_html(user_resume)
        
        full_html = f"""
        <style>{css}</style>
        <div class="ats-page">
            {html_content}
        </div>
        """
        st.components.v1.html(full_html, height=1000, scrolling=True)
    
    elif template_source == 'doc_saved' and st.session_state.get('generated_doc'):
        try:
            from docx import Document
            import io
            
            doc_stream = io.BytesIO(st.session_state.generated_doc)
            processed_doc = Document(doc_stream)
            
            html_preview = '<div style="background: white; padding: 40px; font-family: Calibri, Arial; line-height: 1.6;">'
            for para in processed_doc.paragraphs:
                if para.text.strip():
                    html_preview += f'<p style="margin: 8px 0;">{para.text.strip()}</p>'
            html_preview += '</div>'
            
            st.markdown(html_preview, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Preview error: {str(e)}")
    
    elif template_source == 'ppt_saved' and st.session_state.get('generated_ppt'):
        try:
            from pptx import Presentation
            import io
            
            preview_prs = Presentation(io.BytesIO(st.session_state.generated_ppt))
            
            for slide_idx, slide in enumerate(preview_prs.slides):
                st.markdown(f"""
                <div style="background: #f5f7fa; padding: 20px; margin: 15px 0; border-radius: 10px; border: 2px solid #ffe5d9;">
                    <div style="background: #e87532; color: white; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-weight: bold;">
                        Slide {slide_idx + 1}
                    </div>
                """, unsafe_allow_html=True)
                
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        st.markdown(f"""
                        <div style="background: white; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #e87532;">
                            {shape.text.strip().replace(chr(10), '<br>')}
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Preview error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)