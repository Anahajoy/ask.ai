import streamlit as st
from utils import rewrite_resume_for_job, analyze_and_improve_resume ,rewrite_resume_for_job_manual
from streamlit_extras.switch_page_button import switch_page 
from copy import deepcopy

st.set_page_config(layout="centered", page_title="Dynamic ATS Resume Editor")

resume_data = st.session_state.get('resume_source')
jd_data  = st.session_state.get('job_description')
# st.json(resume_data)

input_method = st.session_state["input_method"]

if input_method == "Manual Entry":
    sample_enhanced_resume_data = rewrite_resume_for_job_manual(resume_data, jd_data)
else:
    sample_enhanced_resume_data = rewrite_resume_for_job(resume_data, jd_data)

st.json(sample_enhanced_resume_data)

if 'enhanced_resume' not in st.session_state:
    st.session_state['enhanced_resume'] = sample_enhanced_resume_data

RESUME_ORDER = ["education", "experience", "skills", "projects", "certifications", "achievements"]


def apply_custom_css():
    """Applies custom CSS for a modern dark theme with white text."""
    st.markdown("""
        <style>
                
        [data-testid="stSidebarNav"] {
        display: none !important;
    }
        /* Background */
        .stApp {
            background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)),
                        url('https://images.unsplash.com/photo-1702835124686-fd1faac06b8d?ixlib=rb-4.1.0&auto=format&fit=crop&q=80&w=870') center/cover;
            background-attachment: fixed;
            color: #FFFFFF;
        }

        /* Main content box */
        .main-content {
            background-color: rgba(0, 0, 0, 0.55);
            padding: 30px;
            box-shadow: 0 8px 20px rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            max-width: 900px;
            margin: 40px auto;
            backdrop-filter: blur(10px);
            color: #FFFFFF;
        }

        /* Section headers */
        .resume-section h2 {
            color: #FFD700;
            text-transform: uppercase;
            letter-spacing: 2px;
            border-bottom: 1px solid #888;
            margin-bottom: 10px;
        }

        h1 {
            color: #FFFFFF;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        /* Contact info */
        .contact-info {
            color: #DDDDDD;
            font-size: 1em;
            margin-bottom: 20px;
        }

        /* Item styles */
        .item-title { font-weight: bold; color: #FFFFFF; font-size: 1.15em; margin-top: 12px; margin-bottom: 3px; }
        .item-subtitle { font-style: italic; color: #CCCCCC; font-size: 1em; margin-bottom: 5px; }
        .item-details { color: #DDDDDD; font-size: 0.95em; margin-bottom: 6px; }
        .bullet-list li { margin-bottom: 6px; line-height: 1.5; color: #EEEEEE; }
        .skill-item { background-color: #333333; color: #FFD700; padding: 6px 12px; border-radius: 6px; font-size: 0.9em; }

        /* Sidebar Buttons */
        [data-testid="stSidebar"] button {
            background-color: #5c2e0e;
            color: white;
            font-weight: bold;
            border-radius: 6px;
            padding: 8px 12px;
            margin-bottom: 8px;
        }
        [data-testid="stSidebar"] button:hover {
            background-color: #693926;
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
        # ✅ Ensure name & job title show
        st.markdown(f"<h1>{data.get('name', 'Name Not Found')}</h1>", unsafe_allow_html=True)
        if data.get('job_title'):
            st.markdown(f"<h3 style='color:#FFD700;'>{data['job_title']}</h3>", unsafe_allow_html=True)

        contact_html = f"""
        <div class="contact-info">
            {data.get('phone', '')} | {data.get('email', '')} | {data.get('location', '')}
        </div>
        """
        st.markdown(contact_html, unsafe_allow_html=True)

        if data.get('summary'):
            st.markdown('<div class="resume-section">', unsafe_allow_html=True)
            st.markdown('<h2>Summary</h2>', unsafe_allow_html=True)
            st.markdown(f"<p>{data['summary']}</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


def render_list_item(item, index, key_prefix, section_title, is_edit=True):
    """Generic list item renderer for both edit and view modes."""
    title_keys = ['name', 'title', 'degree', 'institution', 'company'] 
    detail_keys_to_skip = ['name', 'title', 'degree', 'company', 'institution', 'description', 'overview']

    if not is_edit:
        html_content = "<div>"
        main_title = next((item[k] for k in title_keys if k in item and item[k]), None)
        if main_title:
            html_content += f'<div class="item-title">{main_title}</div>'
            subtitle_keys = ['institution', 'company', 'issuer']
            subtitle = next((item[k] for k in subtitle_keys if k in item and item[k]), None)
            if subtitle:
                html_content += f'<div class="item-subtitle">{subtitle}</div>'

        # ✅ Include duration/date
        duration = item.get('duration') or f"{item.get('start_date', '')} - {item.get('end_date', '')}"
        if duration.strip() != '-':
            html_content += f'<div class="item-details"><em>{duration}</em></div>'

        # ✅ Rest content
        for k, v in item.items():
            if isinstance(v, str) and v.strip() and k not in title_keys + detail_keys_to_skip + ['duration', 'start_date', 'end_date']:
                html_content += f'<p>{v}</p>'

        for k, v in item.items():
            if isinstance(v, list) and v:
                bullet_html = "".join([f"<li>{line}</li>" for line in v])
                html_content += f'<ul class="bullet-list">{bullet_html}</ul>'

        html_content += "</div>"
        return html_content
    else:
        edited_item = item.copy()
        for k, v in item.items():
            if isinstance(v, str):
                edited_item[k] = st.text_input(format_section_title(k), v, key=f"{key_prefix}_{k}_{index}")
            elif isinstance(v, list):
                text = "\n".join(v)
                edited_text = st.text_area(format_section_title(k), text, key=f"{key_prefix}_area_{k}_{index}")
                edited_item[k] = [line.strip() for line in edited_text.split('\n') if line.strip()]
        return edited_item

def render_generic_section(section_key, data_list, is_edit):
    """Renders dynamic list sections."""
    section_title = format_section_title(section_key)
    if not data_list: return

    st.markdown('<div class="resume-section">', unsafe_allow_html=True)
    st.markdown(f'<h2>{section_title}</h2>', unsafe_allow_html=True)

    for i, item in enumerate(data_list):
        with st.container(border=False):
            if is_edit:
                expander_title = item.get('title') or item.get('name') or item.get(list(item.keys())[0]) or f"{section_title[:-1]} Item {i+1}"

                
                with st.expander(f"**Edit/Remove:** {expander_title}", expanded=False):
                    edited_item = render_list_item(item, i, f"{section_key}_edit_{i}", section_title, is_edit=True)
                    
                    if edited_item:
                        data_list[i] = edited_item
                    
                    if st.button(f"❌ Remove this {section_title[:-1]}", key=f"{section_key}_remove_{i}"):
                        data_list.pop(i)
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
        with st.expander("📝 Edit Skills", expanded=False):
            for skill_type, skill_list in skills_data.items():
                st.subheader(format_section_title(skill_type))
                skill_text = "\n".join(skill_list)
                # Key must be unique across reruns. 'skills_edit_' is unique per type.
                edited_text = st.text_area(f"Edit {skill_type}", skill_text, height=100, key=f"skills_edit_{skill_type}")
                
                # Update the data list in session state directly
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

# --- MODIFIED FUNCTION: Save and Improve (with Skills Preservation) ---

def save_and_improve():
    """
    Calls auto_improve_resume on the current session state data and updates 
    the session state, preserving user's manual edits/deletions in the skills section.
    """
    # Use deepcopy to ensure we are working with a copy of the data
    data = deepcopy(st.session_state['enhanced_resume'])
    
    # 1. Capture the user's current, manually edited skills before improvement
    user_skills_before = deepcopy(data.get('skills', {}))
    
    # Retrieve job description for context-aware improvement
    job_description = st.session_state.get('job_description', '') 

    with st.spinner('Calling LLM to perform auto-improvement...'):
        # 2. Call the auto_improve_resume function from utils.py
        # Assume this returns a new dictionary with LLM suggestions
        improved_data = analyze_and_improve_resume(data, job_description)
    
    # --- 3. SKILLS MERGING LOGIC: Preserve user deletions/edits ---
    llm_skills_after = improved_data.get('skills', {})
    merged_skills = {}

    # Identify all skill categories present in EITHER the user's data OR the LLM's data
    all_categories = set(user_skills_before.keys()) | set(llm_skills_after.keys())

    for category in all_categories:
        user_list = user_skills_before.get(category, [])
        llm_list = llm_skills_after.get(category, [])
        
        user_set = set(user_list)
        llm_set = set(llm_list)
        
        # Start with the user's current skills for this category (preserving deletions)
        final_skills_set = user_set.copy()
        
        # Add any skills from the LLM's response that the user doesn't currently have.
        # This ensures new, relevant skills are added without re-introducing deleted ones.
        for skill in llm_set:
            if skill not in final_skills_set:
                final_skills_set.add(skill)
                
        merged_skills[category] = sorted(list(final_skills_set))

    # Update the improved data with the merged skills
    improved_data['skills'] = merged_skills
    
    # --- END SKILLS MERGING LOGIC ---
    
    # Update the editor content with the final, merged improved data
    st.session_state['enhanced_resume'] = improved_data
    st.success("Resume content saved and improved! Check the updated details below.")

# --- Generate and Switch Function ---

def generate_and_switch():
    """
    Performs final analysis (if any remaining) or just saves the current state 
    as the final resume data and switches to the download page.
    """
    data = st.session_state['enhanced_resume']
    
    # 1. Call final analysis/quality check (using the function defined in utils)
    with st.spinner('Performing final analysis and generating download data...'):
        finalized_data = analyze_and_improve_resume(data) 
        # st.json(finalized_data)
    
    # 2. Save the finalized data to be retrieved by download.py
    st.session_state['final_resume_data'] = finalized_data
    
    # 3. Switch the page
    switch_page("download")

# --- Main Streamlit App Layout ---

def main():
    apply_custom_css()
    data = st.session_state['enhanced_resume']

    st.sidebar.title("Resume Tools 🛠️")
    if st.sidebar.button("✨ **Save & Auto-Improve**", use_container_width=True):
        save_and_improve()
    if st.sidebar.button("📄 **GENERATE RESUME**", type="primary", use_container_width=True):
        generate_and_switch()

    st.sidebar.markdown("---")
    st.sidebar.subheader("➕ Add New Section Items")
    st.sidebar.button("Add New Experience", on_click=add_new_item, args=('experience', {"title": "New Job Title", "company": "New Company", "duration": "YYYY - YYYY", "description": ["New responsibility 1."]}))
    st.sidebar.button("Add New Education", on_click=add_new_item, args=('education', {"institution": "New University", "degree": "New Degree", "duration": "YYYY - YYYY"}))
    st.sidebar.button("Add New Certification", on_click=add_new_item, args=('certifications', {"name": "New Certification Name", "issuer": "Issuing Body"}))
    st.sidebar.button("Add New Project", on_click=add_new_item, args=('projects', {"name": "New Project Title", "description": ["Project detail 1.", "Project detail 2."]}))

    st.sidebar.markdown("---")
    st.sidebar.subheader("Custom Section Management")
    new_section_key = st.sidebar.text_input("Add a New Section Key (e.g., 'awards')")
    if st.sidebar.button("Add Custom List Section"):
        if new_section_key and new_section_key.lower() not in data:
            data[new_section_key.lower()] = []
            st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("Reset Resume (Use with Caution!)"):
        del st.session_state['enhanced_resume']
        st.rerun()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    is_edit_mode = st.checkbox("⚙️ **Enable Edit Mode**", key='edit_toggle')
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

    # Prevent duplicates
    for key, value in data.items():
        if key not in rendered_keys and key not in ["name", "email", "phone", "location", "summary", "job_title"]:
            if isinstance(value, list):
                render_generic_section(key, value, is_edit=is_edit_mode)

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()