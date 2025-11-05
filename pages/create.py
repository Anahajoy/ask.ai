import streamlit as st
from utils import  analyze_and_improve_resume,should_regenerate_resume,generate_enhanced_resume,save_and_improve,add_new_item,render_basic_details,render_skills_section,render_generic_section
from streamlit_extras.switch_page_button import switch_page 
import json

st.set_page_config(layout="centered", page_title="Dynamic ATS Resume Editor")



if should_regenerate_resume():
    with st.spinner("Generating optimized resume..."):
        generate_enhanced_resume()

RESUME_ORDER = ["education", "experience", "skills", "projects", "certifications", "achievements"]


def apply_custom_css():
    """Applies improved dark theme with gradient accents."""
    st.markdown("""
    <style>
    /* [Previous CSS remains the same until the item classes...] */
                  /* Background */
    .stApp {
        background: var(--bg-dark);
        min-height: 100vh;
        color: var(--text-white);
    }
     [data-testid="stSidebarNav"] {
            display: none !important;
        }            
    
    .stApp .stButton > button {
    background: -webkit-linear-gradient(45deg, #00BFFF, #00FF7F) !important;
    color: #ffffff !important;
    border: none !important;
    padding: 0.9rem 1.6rem !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    box-shadow: 0 6px 18px rgba(0,191,255,0.28) !important;
    transition: all 0.3s ease !important;
}

.stApp .stButton > button:hover {
    transform: translateY(-2px);
    filter: brightness(1.05);
}






    /* --- Item Titles & Subtitles --- */
    .resume-section .item-title {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        background: linear-gradient(45deg, #00BFFF, #00FF7F) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin-bottom: 0.5rem !important;
        display: block !important;
    }

    .resume-section .item-subtitle {
        font-size: 1.1rem !important;
        color: #00BFFF !important;
        margin-bottom: 0.3rem !important;
        font-weight: 500 !important;
        display: block !important;
    }

    .resume-section .item-details {
        color: #AAAAAA !important;  /* Lighter gray for better visibility on dark bg */
        margin-bottom: 0.5rem !important;
        font-size: 0.95rem !important;
        font-style: italic !important;  /* For dates */
    }

    /* --- Bullet Lists (Fixed with explicit bullet styling) --- */
    .resume-section .bullet-list {
        list-style-type: disc !important;
        margin: 0.5rem 0 !important;
        padding-left: 1.5rem !important;
        color: #FFFFFF !important;
    }

    .resume-section .bullet-list li {
        color: #FFFFFF !important;
        margin-bottom: 0.3rem !important;
        line-height: 1.5 !important;
        list-style-type: inherit !important;  /* Ensure bullets propagate */
    }

    /* Also apply to skill lists for consistency */
    .resume-section .skill-list {
        list-style-type: none !important;  /* No bullets for skills if preferred */
        padding-left: 0 !important;
    }

    .resume-section .skill-list li.skill-item {
        display: inline-block !important;
        background: rgba(0, 191, 255, 0.1) !important;
        padding: 0.3rem 0.8rem !important;
        margin: 0.2rem !important;
        border-radius: 5px !important;
        border: 1px solid rgba(0, 191, 255, 0.3) !important;
    }

    /* Higher specificity for Streamlit containers */
    [data-testid="stHorizontalBlock"] .item-subtitle,
    div.element-container .item-subtitle,
    .stMarkdown .item-subtitle {
        font-size: 1.1rem !important;
        color: #00BFFF !important;
        margin-bottom: 0.3rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stHorizontalBlock"] .bullet-list,
    div.element-container .bullet-list,
    .stMarkdown .bullet-list {
        list-style-type: disc !important;
        padding-left: 1.5rem !important;
    }

    [data-testid="stHorizontalBlock"] .bullet-list li,
    div.element-container .bullet-list li,
    .stMarkdown .bullet-list li {
        color: #FFFFFF !important;
    }

    /* [Rest of the CSS remains the same...] */
    </style>
    """, unsafe_allow_html=True)



def generate_and_switch():
    """Performs final analysis and switches to download page."""
    data = st.session_state['enhanced_resume']
    
    with st.spinner('Performing final analysis and generating download data...'):
        finalized_data = analyze_and_improve_resume(data) 
    
    st.session_state['final_resume_data'] = finalized_data
    switch_page("download")



def main():
    apply_custom_css()
    data = st.session_state['enhanced_resume']

    st.sidebar.title("Resume Tools 🛠️")

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
                "position": "New Job Title",  
                "company": "New Company", 
                "start_date": "2025-01-01",  
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

        if 'enhanced_resume' in st.session_state:
            del st.session_state['enhanced_resume']
        if 'last_resume_hash' in st.session_state:
            del st.session_state['last_resume_hash']
        if 'ats_score_data' in st.session_state:
            del st.session_state['ats_score_data']
        st.rerun()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

   
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