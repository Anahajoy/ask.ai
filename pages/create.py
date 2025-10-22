import streamlit as st
from utils import rewrite_resume_for_job, analyze_and_improve_resume, rewrite_resume_for_job_manual,calculate_ats_score, get_score_color, get_score_label
from streamlit_extras.switch_page_button import switch_page 
from copy import deepcopy
import hashlib
import json

st.set_page_config(layout="centered", page_title="Dynamic ATS Resume Editor")

def display_ats_score():
    """Display ATS score card with breakdown."""
    resume_data = st.session_state.get('enhanced_resume')
    job_description = st.session_state.get('job_description', '')
    
    if not resume_data or not job_description:
        return
    
    # Calculate score
    if 'ats_score_data' not in st.session_state:
        with st.spinner("Calculating ATS Score..."):
            from utils import calculate_ats_score, get_score_color, get_score_label
            score_data = calculate_ats_score(resume_data, job_description)
            st.session_state['ats_score_data'] = score_data
    else:
        score_data = st.session_state['ats_score_data']
    
    from utils import get_score_color, get_score_label
    
    score = score_data['score']
    breakdown = score_data['breakdown']
    matched_kw = score_data.get('matched_keywords', [])
    missing_kw = score_data.get('missing_keywords', [])
    
    color = get_score_color(score)
    label = get_score_label(score)
    
    # Main score display - more compact
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0; border-top: 2px solid; border-bottom: 2px solid; border-image: linear-gradient(90deg, transparent, #00BFFF, #00FF7F, transparent) 1; margin: 1rem 0;">
        <h3 style="margin-bottom: 0.5rem;">ATS Match Score</h3>
        <h1 style="font-size: 2.5rem; color: {color}; margin: 0.3rem 0;">{score}%</h1>
        <p style="font-size: 1rem; color: {color}; margin-top: 0.3rem; font-weight: 600;">{label}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Breakdown in columns with lines instead of boxes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center; padding: 0.5rem; border-left: 2px solid rgba(0,191,255,0.3); transition: all 0.3s ease;">
            <div style="font-size: 1.5rem; font-weight: 900; background: linear-gradient(45deg, #00BFFF, #00FF7F); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{round(breakdown['skills_match'])}%</div>
            <div style="font-size: 0.8rem; color: #AAA; margin-top: 0.3rem; font-weight: 500;">Skills Match</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 0.5rem; border-left: 2px solid rgba(0,191,255,0.3); transition: all 0.3s ease;">
            <div style="font-size: 1.5rem; font-weight: 900; background: linear-gradient(45deg, #00BFFF, #00FF7F); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{round(breakdown['experience_match'])}%</div>
            <div style="font-size: 0.8rem; color: #AAA; margin-top: 0.3rem; font-weight: 500;">Experience Match</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="text-align: center; padding: 0.5rem; border-left: 2px solid rgba(0,191,255,0.3); transition: all 0.3s ease;">
            <div style="font-size: 1.5rem; font-weight: 900; background: linear-gradient(45deg, #00BFFF, #00FF7F); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{round(breakdown['keyword_match'])}%</div>
            <div style="font-size: 0.8rem; color: #AAA; margin-top: 0.3rem; font-weight: 500;">Keyword Match</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Keywords section - more compact
    with st.expander("📊 View Keywords", expanded=False):
        if matched_kw:
            st.markdown("**✅ Matched Keywords:**")
            keywords_html = " ".join([f'<span style="display: inline-block; padding: 0.3rem 0.6rem; margin: 0.2rem; background: linear-gradient(45deg, #00BFFF, #00FF7F); color: #000; border-radius: 15px; font-size: 0.8rem; font-weight: 700;">{kw}</span>' for kw in matched_kw[:15]])
            st.markdown(f'<div style="margin-top: 0.5rem;">{keywords_html}</div>', unsafe_allow_html=True)
        
        if missing_kw:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**❌ Missing Keywords:**")
            missing_html = " ".join([f'<span style="display: inline-block; padding: 0.3rem 0.6rem; margin: 0.2rem; background: linear-gradient(45deg, #FF6347, #FF4500); color: #FFF; border-radius: 15px; font-size: 0.8rem; font-weight: 700;">{kw}</span>' for kw in missing_kw[:10]])
            st.markdown(f'<div style="margin-top: 0.5rem;">{missing_html}</div>', unsafe_allow_html=True)
def get_resume_hash(resume_data):
    """Generate a hash of resume data to detect changes"""
    resume_str = json.dumps(resume_data, sort_keys=True, default=str)
    return hashlib.md5(resume_str.encode()).hexdigest()

def should_regenerate_resume():
    """Check if we need to regenerate the enhanced resume"""
    current_user = st.session_state.get('logged_in_user')
    resume_data = st.session_state.get('resume_source')
    jd_data = st.session_state.get('job_description')
    
    # Check 1: No enhanced resume exists
    if 'enhanced_resume' not in st.session_state:
        return True
    
    # Check 2: User changed
    if st.session_state.get('last_resume_user') != current_user:
        return True
    
    # Check 3: Resume source data changed
    current_resume_hash = get_resume_hash(resume_data) if resume_data else None
    if st.session_state.get('last_resume_hash') != current_resume_hash:
        return True
    
    # Check 4: Job description changed
    current_jd_hash = get_resume_hash(jd_data) if jd_data else None
    if st.session_state.get('last_jd_hash') != current_jd_hash:
        return True
    
    return False

def generate_enhanced_resume():
    """Generate enhanced resume and store metadata"""
    resume_data = st.session_state.get('resume_source')
    jd_data = st.session_state.get('job_description')
    input_method = st.session_state.get("input_method", "Manual Entry")
    current_user = st.session_state.get('logged_in_user')
    
    # Generate enhanced resume based on input method
    if input_method == "Manual Entry":
        enhanced_resume = rewrite_resume_for_job_manual(resume_data, jd_data)
    else:
        enhanced_resume = rewrite_resume_for_job(resume_data, jd_data)

    # st.write(enhanced_resume)
    
    # Store the enhanced resume and metadata
    st.session_state['enhanced_resume'] = enhanced_resume
    st.session_state['last_resume_user'] = current_user
    st.session_state['last_resume_hash'] = get_resume_hash(resume_data) if resume_data else None
    st.session_state['last_jd_hash'] = get_resume_hash(jd_data) if jd_data else None
    
    return enhanced_resume

# # --- Configuration & Data Retrieval ---
# resume_data = st.session_state.get('resume_source')
# jd_data = st.session_state.get('job_description')
# input_method = st.session_state.get("input_method", "Manual Entry")

# MODIFIED: Smart regeneration logic
if should_regenerate_resume():
    with st.spinner("Generating optimized resume..."):
        generate_enhanced_resume()

RESUME_ORDER = ["education", "experience", "skills", "projects", "certifications", "achievements"]


def apply_custom_css():
    """Applies improved dark theme with gradient accents."""
    st.markdown("""
    <style>
    /* ============================
    🌑 Enhanced Dark Theme with Gradient
    ============================ */

    /* --- App Background --- */
    body, [data-testid="stAppViewContainer"], .main-content {
        background-color: #0a0a0a !important;
        color: #FFFFFF !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* --- Header --- */
    [data-testid="stHeader"] {
        background: linear-gradient(45deg, #00BFFF, #00FF7F) !important;
        color: #000000 !important;
        font-weight: 600 !important;
        box-shadow: 0 3px 10px rgba(0,255,255,0.3);
    }

    /* --- Sidebar --- */
    [data-testid="stSidebar"] {
        background-color: #0f0f0f !important;
        color: #FFFFFF !important;
        padding: 1rem;
        border-right: 2px solid #00BFFF;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4, 
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] .stSelectbox, 
    [data-testid="stSidebar"] .stColorPicker, 
    [data-testid="stSidebar"] input {
        background-color: #1a1a1a !important;
        color: #FFFFFF !important;
        border: 1px solid #00BFFF !important;
    }

    [data-testid="stSidebar"] button {
        background: linear-gradient(45deg, #00BFFF, #00FF7F) !important;
        color: #000000 !important;
        border-radius: 10px;
        font-weight: 700;
        padding: 0.65rem;
        border: none;
        width: 100%;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,191,255,0.3);
    }

    [data-testid="stSidebar"] button:hover {
        background: linear-gradient(45deg, #00FF7F, #00BFFF) !important;
        color: #000000 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,255,127,0.5);
    }

    /* --- Headings with Gradient --- */
    h1, h2, h3, h4, h5, h6 {
        background: linear-gradient(45deg, #00BFFF, #00FF7F) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-weight: 700 !important;
        text-shadow: 0 0 30px rgba(0,191,255,0.5);
    }

    h1 {
        font-size: 2.5rem !important;
    }

    h2 {
        font-size: 1.8rem !important;
    }

    /* --- Buttons --- */
    div.stButton > button {
        background: linear-gradient(45deg, #00BFFF, #00FF7F) !important;
        color: #000000 !important;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 15px rgba(0,191,255,0.3);
    }

    div.stButton > button:hover {
        background: linear-gradient(45deg, #00FF7F, #00BFFF) !important;
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,255,127,0.5);
    }

    /* --- Inputs --- */
    input, textarea, select {
        background-color: #1a1a1a !important;
        color: #FFFFFF !important;
        border: 2px solid #00BFFF !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
        transition: all 0.3s ease;
    }

    input:focus, textarea:focus, select:focus {
        outline: none !important;
        border: 2px solid #00FF7F !important;
        box-shadow: 0 0 15px rgba(0,255,127,0.5) !important;
        background-color: #0f0f0f !important;
    }

    /* --- Cards / Containers --- */
    div[data-testid="stHorizontalBlock"], .template-card, .resume-section {
        background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%) !important;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,191,255,0.15);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        color: #FFFFFF !important;
        border: 1px solid rgba(0,191,255,0.3);
    }

    /* --- Expanders --- */
    [data-testid="stExpander"] {
        background-color: #1a1a1a !important;
        border: 1px solid #00BFFF !important;
        border-radius: 10px;
        margin-bottom: 1rem;
    }

    [data-testid="stExpander"] summary {
        color: #FFFFFF !important;
        font-weight: 600;
    }

    /* --- Contact Info --- */
    .contact-info {
        text-align: center;
        color: #FFFFFF !important;
        font-size: 1.1rem;
        margin: 1rem 0;
        padding: 0.5rem;
        background: linear-gradient(90deg, transparent, rgba(0,191,255,0.1), transparent);
    }

    /* --- Item Titles --- */
    .item-title {
        font-size: 1.3rem;
        font-weight: 700;
        background: linear-gradient(45deg, #00BFFF, #00FF7F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }

    .item-subtitle {
        font-size: 1.1rem;
        color: #FFFFFF;
        margin-bottom: 0.3rem;
        font-weight: 500;
    }

    .item-details {
        color: #CCCCCC;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }

    /* --- Bullet Lists --- */
    .bullet-list, .skill-list {
        color: #FFFFFF !important;
        padding-left: 1.5rem;
    }

    .bullet-list li, .skill-list li {
        color: #FFFFFF !important;
        margin-bottom: 0.5rem;
        line-height: 1.6;
    }

    .skill-item {
        color: #FFFFFF !important;
        padding: 0.3rem 0;
    }

    /* --- ATS Score Card --- */
    .ats-score-card {
        background: transparent;
        padding: 1rem 0;
        margin: 1rem 0;
        border-top: 2px solid;
        border-bottom: 2px solid;
        border-image: linear-gradient(90deg, transparent, #00BFFF, #00FF7F, transparent) 1;
    }
    
    .score-main {
        text-align: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(0,191,255,0.2);
    }
    
    .score-number {
        font-size: 2.5rem;
        font-weight: 900;
        margin: 0.3rem 0;
        text-shadow: 0 0 20px currentColor;
    }
    
    .score-label {
        font-size: 1rem;
        margin-top: 0.3rem;
        font-weight: 600;
    }
    
    .score-breakdown {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin-top: 1rem;
        padding: 0.5rem 0;
    }
    
    .score-item {
        text-align: center;
        padding: 0.5rem;
        background: transparent;
        border-left: 2px solid rgba(0,191,255,0.3);
        transition: all 0.3s ease;
    }

    .score-item:hover {
        border-left-color: #00BFFF;
        padding-left: 0.8rem;
    }
    
    .score-item-value {
        font-size: 1.5rem;
        font-weight: 900;
        background: linear-gradient(45deg, #00BFFF, #00FF7F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .score-item-label {
        font-size: 0.8rem;
        color: #AAAAAA;
        margin-top: 0.3rem;
        font-weight: 500;
    }
    
    .keywords-section {
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(0,191,255,0.3);
    }
    
    .keyword-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        margin: 0.3rem;
        background: linear-gradient(45deg, #00BFFF, #00FF7F);
        color: #000000;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(0,191,255,0.3);
    }

    .keyword-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,191,255,0.5);
    }
    
    .missing-keyword-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        margin: 0.3rem;
        background: linear-gradient(45deg, #FF6347, #FF4500);
        color: #FFFFFF;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(255,99,71,0.3);
    }

    .missing-keyword-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255,99,71,0.5);
    }

    /* --- Checkbox --- */
    [data-testid="stCheckbox"] {
        color: #FFFFFF !important;
    }

    /* --- Info/Warning/Success Messages --- */
    [data-testid="stAlert"] {
        background-color: #1a1a1a !important;
        border-left: 4px solid #00BFFF !important;
        color: #FFFFFF !important;
    }

    /* --- Footer & Header --- */
    footer, header { 
        visibility: hidden !important; 
    }

    /* --- Scrollbar --- */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #00BFFF, #00FF7F);
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #00FF7F, #00BFFF);
    }

    </style>
    """, unsafe_allow_html=True)



def format_section_title(key):
    """Converts keys like 'certifications' to 'Certifications'."""
    title = key.replace('_', ' ')
    return ' '.join(word.capitalize() for word in title.split())


def render_basic_details(data, is_edit):
    """Top header section (Name, title, contact info)."""
    if is_edit:
        st.markdown('<h2>Basic Details</h2>', unsafe_allow_html=True)
        data['name'] = st.text_input("Name", data.get('name', ''), key="edit_name")
        data['job_title'] = st.text_input("Job Title", data.get('job_title', ''), key="edit_job_title")

        col1, col2, col3 = st.columns(3)
        with col1:
            data['phone'] = st.text_input("Phone", data.get('phone', ''), key="edit_phone")
        with col2:
            data['email'] = st.text_input("Email", data.get('email', ''), key="edit_email")
        with col3:
            data['location'] = st.text_input("Location", data.get('location', ''), key="edit_location")

        st.markdown('<div class="resume-section">', unsafe_allow_html=True)
        st.markdown('<h2>Summary</h2>', unsafe_allow_html=True)
        data['summary'] = st.text_area("Summary", data.get('summary', ''), height=150, key="edit_summary")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(f"<h1>{data.get('name', 'Name Not Found')}</h1>", unsafe_allow_html=True)
        if data.get('job_title'):
            st.markdown(f"<h3>{data['job_title']}</h3>", unsafe_allow_html=True)

        contact_html = f"""
        <div class="contact-info">
            {data.get('phone', '')} | {data.get('email', '')} | {data.get('location', '')}
        </div>
        """
        st.markdown(contact_html, unsafe_allow_html=True)

        if data.get('summary'):
            st.markdown('<div class="resume-section">', unsafe_allow_html=True)
            st.markdown('<h2>Summary</h2>', unsafe_allow_html=True)
            st.markdown(f"<p style='color:#E0E0E0;'>{data['summary']}</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


def format_date(date_string):
    """
    Converts date from YYYY-MM-DD to MMM YYYY format.
    Example: "2025-10-14" -> "Oct 2025"
    """
    if not date_string or date_string.strip() == '':
        return ''
    
    try:
        from datetime import datetime
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        return date_obj.strftime('%b %Y')
    except:
        return date_string  # Return original if parsing fails


def render_list_item(item, index, key_prefix, section_title, is_edit=True):
    """Generic list item renderer for both edit and view modes."""
    title_keys = ['name', 'title', 'degree', 'institution', 'company', 'position']  # ADDED 'position'
    detail_keys_to_skip = ['name', 'title', 'degree', 'company', 'institution', 'description', 'overview', 'issuer', 'position', 'start_date', 'end_date']  # ADDED 'position'

    if not is_edit:
        html_content = "<div>"
        
        # MODIFIED: Check for position field first
        main_title = None
        if 'position' in item and item['position']:
            main_title = item['position']
        else:
            main_title = next((item[k] for k in title_keys if k in item and item[k]), None)
        
        if main_title:
            html_content += f'<div class="item-title">{main_title}</div>'
            subtitle_keys = ['institution', 'company', 'issuer']
            subtitle = next((item[k] for k in subtitle_keys if k in item and item[k]), None)
            if subtitle:
                html_content += f'<div class="item-subtitle">{subtitle}</div>'

        # MODIFIED: Format dates to MMM YYYY
        duration = item.get('duration')
        if not duration:
            start_date = format_date(item.get('start_date', ''))
            end_date = format_date(item.get('end_date', ''))
            if start_date or end_date:
                duration = f"{start_date} - {end_date}"
        
        if duration and duration.strip() != '-':
            html_content += f'<div class="item-details"><em>{duration}</em></div>'

        main_description_list = item.get('description') or item.get('overview')
        if isinstance(main_description_list, list) and main_description_list:
            bullet_html = "".join([f"<li>{line}</li>" for line in main_description_list])
            html_content += f'<ul class="bullet-list">{bullet_html}</ul>'
        
        for k, v in item.items():
            if isinstance(v, str) and v.strip() and k not in detail_keys_to_skip + ['duration', 'start_date', 'end_date']:
                formatted_k = format_section_title(k)
                html_content += f'<div class="item-details">**{formatted_k}:** {v}</div>'

        html_content += "</div>"
        return html_content
    else:
        edited_item = item.copy()
        
        edit_fields = list(item.keys())
        # MODIFIED: Added 'position' to priority fields
        priority_fields = ['position', 'title', 'name', 'company', 'institution', 'degree', 'issuer', 'duration', 'start_date', 'end_date', 'description', 'overview']
        
        ordered_fields = []
        for field in priority_fields:
            if field in edit_fields:
                ordered_fields.append(field)
                edit_fields.remove(field)
        ordered_fields.extend(edit_fields)
        
        for k in ordered_fields:
            v = item[k]
            if isinstance(v, str):
                edited_item[k] = st.text_input(format_section_title(k), v, key=f"{key_prefix}_{k}_{index}")
            elif isinstance(v, list):
                text = "\n".join(v)
                edited_text = st.text_area(format_section_title(k), text, height=150, key=f"{key_prefix}_area_{k}_{index}")
                edited_item[k] = [line.strip() for line in edited_text.split('\n') if line.strip()]
        return edited_item

def render_generic_section(section_key, data_list, is_edit):
    """Renders dynamic list sections."""
    section_title = format_section_title(section_key)
    if not data_list: return

    st.markdown('<div class="resume-section">', unsafe_allow_html=True)
    st.markdown(f'<h2>{section_title}</h2>', unsafe_allow_html=True)

    for i, item in enumerate(data_list):
        if i >= len(st.session_state['enhanced_resume'].get(section_key, [])):
             continue 

        with st.container(border=False):
            
            expander_title_parts = [
                item.get('title'),
                item.get('name'),
                item.get('company'),
                item.get('institution'),
                f"{section_title[:-1]} Item {i+1}"
            ]
            expander_title = next((t for t in expander_title_parts if t), f"{section_title[:-1]} Item {i+1}")

            if is_edit:
                with st.expander(f"📝 Edit: **{expander_title}**", expanded=False):
                    temp_item = deepcopy(item) 
                    edited_item = render_list_item(temp_item, i, f"{section_key}_edit_{i}", section_title, is_edit=True)
                    
                    if edited_item:
                        st.session_state['enhanced_resume'][section_key][i] = edited_item
                    
                    if st.button(f"❌ Remove this {section_title[:-1]}", key=f"{section_key}_remove_{i}"):
                        st.session_state['enhanced_resume'][section_key].pop(i)
                        st.rerun()
                
                st.markdown(render_list_item(item, i, f"{section_key}_view_{i}", section_title, is_edit=False), unsafe_allow_html=True)
            else:
                st.markdown(render_list_item(item, i, f"{section_key}_view_{i}", section_title, is_edit=False), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_skills_section(data, is_edit):
    """Handles the nested dictionary structure of the 'skills' section."""
    skills_data = data.get('skills', {})
    if not skills_data: return

    st.markdown('<div class="resume-section">', unsafe_allow_html=True)
    st.markdown('<h2>Skills</h2>', unsafe_allow_html=True)

    if is_edit:
        with st.expander("📝 Edit Skills (Separate by Line)", expanded=False):
            for skill_type, skill_list in skills_data.items():
                st.subheader(format_section_title(skill_type))
                skill_text = "\n".join(skill_list)
                
                edited_text = st.text_area(f"Edit {skill_type}", skill_text, height=100, key=f"skills_edit_{skill_type}")
                
                st.session_state['enhanced_resume']['skills'][skill_type] = [line.strip() for line in edited_text.split('\n') if line.strip()]
    
    for skill_type, skill_list in skills_data.items():
        if skill_list:
            st.markdown(f"**{format_section_title(skill_type)}:**", unsafe_allow_html=True)
            skills_html = "".join([f'<li class="skill-item">{s}</li>' for s in skill_list])
            st.markdown(f'<ul class="skill-list">{skills_html}</ul>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def add_new_item(section_key, default_item):
    """Generic function to add a new item to any list section."""
    if section_key not in st.session_state['enhanced_resume']:
        st.session_state['enhanced_resume'][section_key] = []
            
    st.session_state['enhanced_resume'][section_key].append(default_item)
    st.rerun()

# MODIFIED: Save and Improve with hash update
def save_and_improve():
    """Calls auto_improve_resume and updates session state."""
    data = deepcopy(st.session_state['enhanced_resume'])
    user_skills_before = deepcopy(data.get('skills', {}))
    job_description = st.session_state.get('job_description', '') 

    with st.spinner('performing auto-improvement...'):
        improved_data = analyze_and_improve_resume(data, job_description)
    
    # Skills merging logic
    llm_skills_after = improved_data.get('skills', {})
    merged_skills = {}
    all_categories = set(user_skills_before.keys()) | set(llm_skills_after.keys())

    for category in all_categories:
        user_list = user_skills_before.get(category, [])
        llm_list = llm_skills_after.get(category, [])
        
        user_set = set(user_list)
        llm_set = set(llm_list)
        final_skills_set = user_set.copy()
        
        for skill in llm_set:
            if skill not in final_skills_set:
                final_skills_set.add(skill)
                
        merged_skills[category] = sorted(list(final_skills_set))

    improved_data['skills'] = merged_skills
    st.session_state['enhanced_resume'] = improved_data
    if 'ats_score_data' in st.session_state:
        del st.session_state['ats_score_data']
    
    # Update hash so it doesn't regenerate
    st.session_state['last_resume_hash'] = get_resume_hash(st.session_state.get('resume_source'))
    
    st.success("Resume content saved and improved! Check the updated details below.")

def generate_and_switch():
    """Performs final analysis and switches to download page."""
    data = st.session_state['enhanced_resume']
    
    with st.spinner('Performing final analysis and generating download data...'):
        finalized_data = analyze_and_improve_resume(data) 
    
    st.session_state['final_resume_data'] = finalized_data
    switch_page("download")

# --- Main Streamlit App Layout ---

def main():
    apply_custom_css()
    data = st.session_state['enhanced_resume']

    st.sidebar.title("Resume Tools 🛠️")

    with st.sidebar.expander("ℹ️ Resume Status", expanded=False):
        st.caption(f"**User:** {st.session_state.get('logged_in_user', 'Unknown')}")
        st.caption(f"**Last Updated:** {st.session_state.get('last_resume_user', 'Never')}")

    st.sidebar.markdown("---")

    if st.sidebar.button("✨ **Save & Auto-Improve**", use_container_width=True):
        save_and_improve()
        
    if st.sidebar.button("📄 **GENERATE RESUME**", type="primary", use_container_width=True):
        generate_and_switch()

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
                "position": "New Job Title",  # Changed 'title' to 'position'
                "company": "New Company", 
                "start_date": "2025-01-01",  # Changed to proper date format
                "end_date": "2025-12-31",
                "description": ["New responsibility 1."]
            })
        )
        st.sidebar.button(
            "Add New Education", 
            on_click=add_new_item, 
            args=('education', {
                "institution": "New University", 
                "degree": "New Degree", 
                "start_date": "2025-01-01",
                "end_date": "2025-12-31"
            })
        )
        st.sidebar.button(
            "Add New Certification", 
            on_click=add_new_item, 
            args=('certifications', {
                "name": "New Certification Name", 
                "issuer": "Issuing Body",
                "completed_date": "2025-01-01"
            })
        )
        st.sidebar.button(
            "Add New Project", 
            on_click=add_new_item, 
            args=('projects', {
                "name": "New Project Title", 
                "description": ["Project detail 1.", "Project detail 2."]
            })
        )

        st.sidebar.markdown("---")
        st.sidebar.subheader("Custom Section Management")
        new_section_key = st.sidebar.text_input("Add a New Section Key (e.g., 'awards')")
        if st.sidebar.button("Add Custom List Section"):
            if new_section_key and new_section_key.lower() not in data:
                data[new_section_key.lower()] = []
                st.rerun()
            elif not new_section_key:
                st.sidebar.error("Please enter a section name")
            else:
                st.sidebar.warning(f"Section '{new_section_key}' already exists")

    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Regenerate from Source"):
        # Force regeneration
        if 'enhanced_resume' in st.session_state:
            del st.session_state['enhanced_resume']
        if 'last_resume_hash' in st.session_state:
            del st.session_state['last_resume_hash']
        if 'ats_score_data' in st.session_state:
            del st.session_state['ats_score_data']
        st.rerun()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    # is_edit_mode = st.checkbox("⚙️ **Enable Edit Mode**", key='edit_toggle')
    st.markdown("---")
    display_ats_score()
    st.markdown("---")
    render_basic_details(data, is_edit=is_edit_mode)

    rendered_keys = set()
    for key in RESUME_ORDER:
        if key in data and data[key]:
            rendered_keys.add(key)
            if key == "skills":
                render_skills_section(data, is_edit=is_edit_mode)
            else:
                render_generic_section(key, data[key], is_edit=is_edit_mode)

    for key, value in data.items():
        if key not in rendered_keys and key not in ["name", "email", "phone", "location", "summary", "job_title"]:
            if isinstance(value, list):
                render_generic_section(key, value, is_edit=is_edit_mode)

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    if 'job_description' not in st.session_state or 'resume_source' not in st.session_state:
        st.error("Missing job description or resume source. Please go back to the main page.")
        if st.button("Go to Home"):
            switch_page("main")
    else:
        main()