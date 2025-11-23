import streamlit as st
from PIL import Image
from utils import show_login_modal, get_user_resume, load_users,load_user_templates,load_user_doc_templates,save_user_templates,replace_content,save_user_doc_templates,load_user_ppt_templates,analyze_slide_structure,generate_ppt_sections,match_generated_to_original,clear_and_replace_text,save_user_ppt_templates
from streamlit_extras.stylable_container import stylable_container
from pages.download import SYSTEM_TEMPLATES,generate_generic_html


# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="Resume Creator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------------
# RESTORE USER FROM QUERY PARAMS FIRST
# ----------------------------------
if "logged_in_user" not in st.session_state or st.session_state.logged_in_user is None:
    logged_user = st.query_params.get("user")
    if logged_user:
        st.session_state.logged_in_user = logged_user
    else:
        st.session_state.logged_in_user = None

# ----------------------------------
# OTHER SESSION STATES
# ----------------------------------
if "show_login_modal" not in st.session_state:
    st.session_state.show_login_modal = False

if "show_template_modal" not in st.session_state:
    st.session_state.show_template_modal = False

if "scroll_to" not in st.session_state:
    st.session_state.scroll_to = None

# ----------------------------------
# CUSTOM CSS
# ----------------------------------
st.markdown("""
<style>
#MainMenu, footer, header, button[kind="header"] {visibility: hidden;}
.stMainBlockContainer, div.block-container, [data-testid="stMainBlockContainer"] {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
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

.dropdown {
    position: relative;
    display: inline-block;
}

.dropdown-toggle {
    color: #000000;
    text-decoration: none;
    font-size: 1rem;
    font-family: 'Nunito Sans', sans-serif;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    background: transparent;
    border: none;
    transition: all 0.3s ease;
}

.dropdown-toggle:hover {
    background-color: #f8fafc;
    color: #e87532;
}

.dropdown-content {
    display: none;
    position: absolute;
    background-color: white;
    min-width: 200px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    border-radius: 8px;
    z-index: 100000;
    top: 100%;
    margin-top: 0.5rem;
}

.dropdown:hover .dropdown-content {
    display: block;
}

.dropdown-item {
    color: #000000 !important;
    padding: 12px 16px;
    text-decoration: none !important;
    display: block;
    font-family: 'Nunito Sans', sans-serif;
    cursor: pointer;
    transition: all 0.3s ease;
}

.dropdown-item:visited {
    color: #000000 !important;
}

.dropdown-item:hover {
    background-color: #f8fafc;
    color: #e87532;
}

.hero-title {
    font-size: 3rem;
    font-weight: 500;
    color: #0a0f14;
    margin-bottom: 1rem;
    margin-top: 1rem !important;
    font-family: 'Nunito Sans', sans-serif !important;
    margin-left: 1rem !important;
}

.hero-subtitle {
    font-size: 1.2rem;
    color: #64748b;
    margin-top: 2rem;
    font-family: 'Nunito Sans', sans-serif !important;
    margin-left: 1rem !important;
}

/* About Section Styling */
.about-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    max-width: 800px;
}

.about-header {
    color: #e87532;
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    font-family: 'Nunito Sans', sans-serif;
    margin-top : -500px !important;
}

.about-title {
    color: #0a0f14;
    font-size: 2rem;
    font-weight: 600;
    margin-bottom: 1rem;
    font-family: 'Nunito Sans', sans-serif;
}

.about-description {
    color: #64748b;
    font-size: 1rem;
    line-height: 1.6;
    margin-bottom: 2rem;
    font-family: 'Nunito Sans', sans-serif;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
    background: #f8fafc;
    padding: 1.5rem;
    border-radius: 12px;
}

.info-item {
    display: flex;
    flex-direction: column;
}

.info-label {
    color: #64748b;
    font-size: 0.9rem;
    margin-bottom: 0.3rem;
    font-family: 'Nunito Sans', sans-serif;
}

.info-value {
    color: #0a0f14;
    font-size: 1.1rem;
    font-weight: 600;
    font-family: 'Nunito Sans', sans-serif;
}

/* Resume Section Styling */
.resume-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
}

.section-header {
    text-align: center;
    color: #8b6f47;
    font-size: 2.5rem;
    font-weight: 400;
    margin-bottom: 0.5rem;
    font-family: 'Nunito Sans', sans-serif;
}

.section-divider {
    width: 100px;
    height: 2px;
    background: linear-gradient(to right, transparent, #e87532, transparent);
    margin: 1rem auto 2rem;
}

.section-subtitle {
    text-align: center;
    color: #64748b;
    font-size: 1rem;
    margin-bottom: 3rem;
    font-family: 'Nunito Sans', sans-serif;
}

.work-experience-section {
    margin-top: 3rem;
}

.work-experience-title {
    color: #1e3a5f;
    font-size: 1.8rem;
    font-weight: 600;
    margin-bottom: 1rem;
    font-family: 'Nunito Sans', sans-serif;
}

.work-experience-subtitle {
    color: #64748b;
    font-size: 1rem;
    margin-bottom: 2rem;
    font-family: 'Nunito Sans', sans-serif;
}

.experience-item {
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid #e2e8f0;
}

.experience-timeline {
    flex-shrink: 0;
}

.company-name {
    color: #1e3a5f;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.3rem;
    font-family: 'Nunito Sans', sans-serif;
}

.experience-date {
    color: #e87532;
    font-size: 0.9rem;
    font-family: 'Nunito Sans', sans-serif;
}

.experience-content {
    flex: 1;
}

.experience-role {
    color: #1e3a5f;
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: 0.8rem;
    font-family: 'Nunito Sans', sans-serif;
}

.experience-description {
    color: #64748b;
    font-size: 0.95rem;
    line-height: 1.6;
    font-family: 'Nunito Sans', sans-serif;
}

.timeline-dot {
    width: 12px;
    height: 12px;
    background: #e87532;
    border-radius: 50%;
    margin-top: 6px;
}

.no-resume-message {
    text-align: center;
    color: #64748b;
    font-size: 1.1rem;
    padding: 3rem;
    background: #f8fafc;
    border-radius: 12px;
    margin: 2rem auto;
    max-width: 600px;
}

div[data-testid="stButton"] button:hover {
    filter: brightness(1.1);
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------
# HANDLE NAVIGATION QUERY PARAMS
# ----------------------------------

# Handle LOGOUT
if st.query_params.get("logout") == "true":
    st.session_state.logged_in_user = None
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.rerun()

# Handle HOME navigation
if st.query_params.get("home") == "true":
    if "home" in st.query_params:
        del st.query_params["home"]
    if st.session_state.logged_in_user:
        st.query_params["user"] = st.session_state.logged_in_user
    st.rerun()

# ----------------------------------
# GET CURRENT USER FOR NAVIGATION LINKS
# ----------------------------------
current_user = st.session_state.get('logged_in_user', '')

# ----------------------------------
# NAVIGATION BAR
# ----------------------------------
st.markdown(f"""
<div class="nav-wrapper">
    <div class="logo">Resume Creator</div>
    <div class="nav-menu">
        <div class="nav-item">
            <a class="nav-link" href="?home=true&user={current_user}" target="_self">Home</a>
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
        <div class="dropdown">
            <button class="dropdown-toggle" type="button">Templates ▾</button>
            <div class="dropdown-content">
                <a class="dropdown-item" data-section="CustomTemplates" href="#CustomTemplates">Custom Templates</a>
                <a class="dropdown-item" data-section="SystemTemplates" href="#SystemTemplates">System Templates</a>
            </div>
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

# Add spacing for fixed navbar
st.markdown('<div style="height: 80px;"></div>', unsafe_allow_html=True)

# ----------------------------------
# HOME SECTION
# ----------------------------------
st.markdown('<div id="Home"></div>', unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("""
        <div style="padding: 2rem 0;">
            <div class="hero-title">Creating Resume with Help of AI</div>
            <div class="hero-subtitle">
                Transforming Data into elegant solutions through creative design and innovative development
            </div>
        </div>
        """, unsafe_allow_html=True)

        btn1, btn2 = st.columns([0.9, 1])

        with btn1:
            with stylable_container(
                "create-resume-btn",
                css_styles="""
                    button {
                        background-color: #e87532 !important;
                        color: white !important;
                        padding: 15px 35px !important;
                        border-radius: 50px !important;
                        font-weight: 600 !important;
                        border: 2px solid #e87532 !important;
                    }
                    button:hover {
                        background-color: white !important;
                        color: #e87532 !important;
                    }
                """
            ):
                create_resume_clicked = st.button("Create Resume")

        with btn2, stylable_container(
            "template-btn",
            css_styles="""
                button {
                    background-color: #ffffff !important;
                    color: #e87532 !important;
                    padding: 15px 35px !important;
                    border-radius: 50px !important;
                    font-weight: 600 !important;
                    border: 1px solid #e87532 !important;
                }
                button:hover {
                    background-color:#e87532 !important;
                    color: #ffffff !important;
                }
            """
        ):
            template_clicked = st.button("Show Template")

    with col2:
        try:
            img = Image.open(r"C:\\ask.ai\\image\\image.png")
            st.image(img, use_container_width=True)
        except:
            st.info("Image not found. Check the path.")

# Handle Create Resume button click
if create_resume_clicked:
    if st.session_state.logged_in_user is None:
        st.warning("🔒 Please login first to create a resume.")
        st.session_state.show_login_modal = True
    else:
        email = st.session_state.logged_in_user
        users = load_users()
        user_entry = users.get(email)
        
        st.query_params["user"] = email
        
        if isinstance(user_entry, dict):
            st.session_state.username = email.split('@')[0]
            user_resume = get_user_resume(email)
            
            if user_resume and len(user_resume) > 0:
                st.session_state.resume_source = user_resume
                st.session_state.input_method = user_resume.get("input_method", "Manual Entry")
                st.switch_page("pages/job.py")
            else:
                st.switch_page("pages/main.py")
        else:
            st.switch_page("pages/main.py")

# -------------------------------
# If NOT logged in: only show Home + Login modal
# -------------------------------
if st.session_state.logged_in_user is None:
    st.markdown(
        "<p style='text-align:center; color:#e87532; font-weight:600; margin-top:1rem;margin-bottom:10rem;'>🔒 Please login to access all sections.</p>",
        unsafe_allow_html=True
    )
    st.markdown('<div id="Login"></div>', unsafe_allow_html=True)
    show_login_modal()   
    st.stop()     

# ----------------------------------
# LOGGED-IN USER CONTENT
# ----------------------------------
email = st.session_state.logged_in_user

# Get user resume data
user_resume = get_user_resume(email)
has_resume = user_resume and len(user_resume) > 0

# ----------------------------------
# ABOUT SECTION
# ----------------------------------
st.markdown('<div id="About"></div>', unsafe_allow_html=True)
st.markdown('<div style="padding: 100px 0; min-height: 100vh;">', unsafe_allow_html=True)

if has_resume:
    st.markdown(f"""
    <div class="about-card">
        <div class="about-header">About Me</div>
        <div class="about-title">{user_resume.get('job_title', 'UI/UX Designer & Web Developer')}</div>
        <div class="about-description">
            {user_resume.get('summary', 'Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.')}
        </div>
        <div class="about-description">
            Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet
        </div>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Name</div>
                <div class="info-value">{user_resume.get('name', 'Not provided')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Phone</div>
                <div class="info-value">{user_resume.get('phone', 'Not provided')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Age</div>
                <div class="info-value">26 Years</div>
            </div>
            <div class="info-item">
                <div class="info-label">Email</div>
                <div class="info-value">{user_resume.get('email', email)}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Occupation</div>
                <div class="info-value">{user_resume.get('job_title', 'Not provided')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Nationality</div>
                <div class="info-value">{user_resume.get('location', 'Not provided')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="no-resume-message">
        <h3 style="color: #e87532; margin-bottom: 1rem;">📄 No Resume Data Available</h3>
        <p>You haven't created a resume yet. Click "Create Resume" to get started!</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------
# RESUME SECTION
# ----------------------------------
st.markdown('<div id="Resume"></div>', unsafe_allow_html=True)
# st.markdown('<div style="padding: 100px 0; min-height: 100vh; background: #f8fafc;">', unsafe_allow_html=True)

if has_resume:
    st.markdown("""
    <div class="resume-container">
        <div class="section-header">Resume</div>
        <div class="section-divider"></div>
       
    """, unsafe_allow_html=True)
    
    # Work Experience Section
    if 'experience' in user_resume and user_resume['experience']:
        st.markdown("""
        <div class="work-experience-section">
            <div class="work-experience-title">Work Experience</div>
            
        """, unsafe_allow_html=True)
        
        for exp in user_resume['experience']:
            company = exp.get('company', 'Company Name')
            position = exp.get('title', 'Position')
            # start_date = exp.get('start_date', '')
            dates = exp.get('duration', 'Current')
            description = exp.get('description', [])
            
            # Join description list into paragraphs
            desc_text = '<br><br>'.join(description) if isinstance(description, list) else description
            
            st.markdown(f"""
            <div class="experience-item">
                <div class="experience-timeline">
                    <div class="timeline-dot"></div>
                    <div class="company-name">{company}</div>
                    <div class="experience-date">{dates}</div>
                </div>
                <div class="experience-content">
                    <div class="experience-role">{position}</div>
                    <div class="experience-description">{desc_text}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        if 'education' in user_resume and user_resume['education']:
            st.markdown("""
            <div class="work-experience-section">
                <div class="work-experience-title">Education</div>
                
            """, unsafe_allow_html=True)
            
            for ed in user_resume['education']:
                inst = ed.get('institution', 'Institution Name')
                degree = ed.get('degree', 'Degree')
                # start_date = exp.get('start_date', '')
                dates = ed.get('duration', 'Duration')
                gpa = ed.get('gpa', 'GPA')
                
                # # Join description list into paragraphs
                # desc_text = '<br><br>'.join(description) if isinstance(description, list) else description
                
                st.markdown(f"""
                <div class="experience-item">
                    <div class="experience-timeline">
                        <div class="timeline-dot"></div>
                        <div class="company-name">{inst}</div>
                        <div class="experience-date">{degree}</div>
                    </div>
                    <div class="experience-content">
                        <div class="experience-role">{dates}</div>
                        <div class="experience-description">{gpa}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)   
    
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="resume-container">
        <div class="no-resume-message">
            <h3 style="color: #e87532; margin-bottom: 1rem;">📄 No Resume Data Available</h3>
            <p>Create your resume to see it displayed here with all your work experience and qualifications.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------
# PORTFOLIO SECTION
# ----------------------------------


# ----------------------------------
# CUSTOM TEMPLATES SECTION
# ----------------------------------
st.markdown('<div id="CustomTemplates"></div>', unsafe_allow_html=True)

st.markdown("""
<div >
    <h2 style="text-align: center; color: #0a0f14;">Templates</h2>
</div>
""", unsafe_allow_html=True)
tab1, tab3 = st.tabs(["🎨 System Templates", "📤 Custom Templates"])
with tab1:
        # System template selection dropdown
        system_template_names = list(SYSTEM_TEMPLATES.keys())
        selected_system_template = st.selectbox(
            "Select a System Template:",
            system_template_names,
            key="system_template_dropdown",
            help="Choose a template from our professionally designed collection"
        )

        # if selected_system_template:
        #     template_config = SYSTEM_TEMPLATES[selected_system_template]
            
        #     # Store the selected template in session state
        #     st.session_state.selected_template = selected_system_template
        #     st.session_state.selected_template_config = template_config
        #     st.session_state.template_source = 'system'
            

        
            
        #     # Color selection in main body
        #     # col1, col2 = st.columns([3, 1])
        #     # with col1:
        #     color_name = st.selectbox(
        #             'Choose Accent Color:',
        #             list(ATS_COLORS.keys()),
        #             key='sys_color_select'
        #         )
        #     primary_color = ATS_COLORS[color_name]
            
        #     # with col2:
        #     #     custom_color = st.color_picker(
        #     #         'Custom Color:',
        #     #         primary_color,
        #     #         key='sys_custom_color'
        #     #     )
        #     #     if custom_color != primary_color:
        #     #         primary_color = custom_color
            
        #     # Store selected color in session state
        #     st.session_state.selected_color = primary_color
            
        #     # Generate preview with selected color
        #     template_config = st.session_state.selected_template_config
        #     css = template_config['css_generator'](primary_color)
        #     html_content = template_config['html_generator'](final_data)
            
        #     full_html = f"""
        #     {css}
        #     <div class="ats-page">
        #         {html_content}
        #     </div>
        #     """
            
        #     st.components.v1.html(full_html, height=1000, scrolling=True)
            

    
with tab3:

        if 'uploaded_templates' not in st.session_state:
            st.session_state.uploaded_templates = load_user_templates(st.session_state.logged_in_user)
        
        if 'doc_templates' not in st.session_state:
            st.session_state.doc_templates = load_user_doc_templates(st.session_state.logged_in_user)

    
        st.markdown("### 🗂️ Your Saved Templates")
        
        template_tab1, template_tab2,template_tab3 = st.tabs(["📄 HTML Templates", "📝 Word Templates","📊 PowerPoint Templates"])
        
        # ========== HTML TEMPLATES TAB ==========
        with template_tab1:
            if st.session_state.uploaded_templates:
                cols = st.columns(3)
                for idx, (template_id, template_data) in enumerate(st.session_state.uploaded_templates.items()):
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div class="template-card" style="border:1px solid #ccc; padding:10px; border-radius:10px; background:#fafafa;">
                            <h4>{template_data['name']}</h4>
                            <p style="font-size:0.85em; color:#555;">File: {template_data['original_filename']}</p>
                            <p style="font-size:0.8em; color:#888;">Uploaded: {template_data['uploaded_at']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Use", key=f"use_html_{template_id}",type="primary", use_container_width=True):
                                if 'temp_upload_config' in st.session_state:
                                    del st.session_state.temp_upload_config
                                
                                st.session_state.selected_template_preview = f"""
                                    <style>{template_data['css']}</style>
                                    <div class="ats-page">{generate_generic_html(user_resume)}</div>
                                """
                                st.session_state.selected_template = template_data['name']
                                st.session_state.selected_template_config = template_data
                                st.session_state.template_source = 'saved'
                                st.session_state.current_upload_id = template_id
                                st.rerun()

                        with col2:
                            if st.button(f"Delete", key=f"delete_html_{template_id}",type="secondary", use_container_width=True):
                                if st.session_state.get('current_upload_id') == template_id:
                                    st.session_state.pop('selected_template_preview', None)
                                    st.session_state.pop('selected_template', None)
                                    st.session_state.pop('selected_template_config', None)
                                    st.session_state.pop('current_upload_id', None)
                                
                                del st.session_state.uploaded_templates[template_id]
                                save_user_templates(st.session_state.logged_in_user, st.session_state.uploaded_templates)
                                st.success(f"✅ Deleted '{template_data['name']}'")
                                st.rerun()
            else:
                st.info("📂 No saved HTML templates yet.")

        # ========== WORD TEMPLATES TAB ==========
        with template_tab2:
            if st.session_state.doc_templates:
                cols = st.columns(3)
                for idx, (template_id, template_data) in enumerate(st.session_state.doc_templates.items()):
                    with cols[idx % 3]:
                        sections_text = ", ".join(template_data.get('sections_detected', [])[:3])
                        if len(template_data.get('sections_detected', [])) > 3:
                            sections_text += "..."
                        
                        st.markdown(f"""
                        <div class="template-card" style="border:1px solid #ccc; padding:10px; border-radius:10px; background:#fafafa;">
                            <h4>{template_data['name']}</h4>
                            <p style="font-size:0.85em; color:#555;">File: {template_data['original_filename']}</p>
                            <p style="font-size:0.8em; color:#888;">Uploaded: {template_data['uploaded_at']}</p>
                            <p style="font-size:0.75em; color:#999;">Sections: {sections_text}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Use", key=f"use_doc_{template_id}",type="primary", use_container_width=True):
                                # Process and display the doc template
                                try:
                                    import io
                                    from docx import Document
                                    
                                    # Load template
                                    doc_stream = io.BytesIO(template_data['doc_data'])
                                    doc = Document(doc_stream)
                                    
                                    # Use stored structure
                                    structure = template_data.get('structure', [])
                                    
                                    # Replace content
                                    output, replaced, removed = replace_content(doc, structure, user_resume)
                                    
                                    # Store results
                                    st.session_state.generated_doc = output.getvalue()
                                    st.session_state.selected_doc_template_id = template_id
                                    st.session_state.selected_doc_template = template_data
                                    st.session_state.doc_template_source = 'saved'
                                    
                                    st.success(f"✅ Using template: {template_data['name']}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error loading template: {str(e)}")

                        with col2:
                            if st.button(f"Delete", key=f"delete_doc_{template_id}",type="secondary", use_container_width=True):
                                # Clear selection if deleting currently selected template
                                if st.session_state.get('selected_doc_template_id') == template_id:
                                    st.session_state.pop('generated_doc', None)
                                    st.session_state.pop('selected_doc_template_id', None)
                                    st.session_state.pop('selected_doc_template', None)
                                    st.session_state.pop('doc_template_source', None)
                                
                                del st.session_state.doc_templates[template_id]
                                save_user_doc_templates(st.session_state.logged_in_user, st.session_state.doc_templates)
                                st.success(f"✅ Deleted '{template_data['name']}'")
                                st.rerun()
            else:
                st.info("📂 No saved Word templates yet.")
        # Add this as a third tab in the "Your Saved Templates" section
# After template_tab1 (HTML) and template_tab2 (Word), add:


        # ========== POWERPOINT TEMPLATES TAB ==========
        with template_tab3:
            if 'ppt_templates' not in st.session_state:
                st.session_state.ppt_templates = load_user_ppt_templates(st.session_state.logged_in_user)
            
            if st.session_state.ppt_templates:
                cols = st.columns(3)
                for idx, (template_id, template_data) in enumerate(st.session_state.ppt_templates.items()):
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div class="template-card" style="border:1px solid #ccc; padding:10px; border-radius:10px; background:#fafafa;">
                            <h4>{template_data['name']}</h4>
                            <p style="font-size:0.85em; color:#555;">File: {template_data['original_filename']}</p>
                            <p style="font-size:0.8em; color:#888;">Uploaded: {template_data['uploaded_at']}</p>
                            <p style="font-size:0.75em; color:#999;">Slides: {len(set([e['slide'] for e in template_data.get('text_elements', [])]))}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Use", key=f"use_ppt_{template_id}",type="primary", use_container_width=True):
                                try:
                                    import io
                                    from pptx import Presentation
                                    
                                    # Load template
                                    working_prs = Presentation(io.BytesIO(template_data['ppt_data']))
                                    
                                    # Regenerate content for current data
                                    prs = Presentation(io.BytesIO(template_data['ppt_data']))
                                    slide_texts = []
                                    for slide_idx, slide in enumerate(prs.slides):
                                        text_blocks = []
                                        for shape_idx, shape in enumerate(slide.shapes):
                                            if shape.has_text_frame and shape.text.strip():
                                                text_blocks.append({
                                                    "index": shape_idx,
                                                    "text": shape.text.strip(),
                                                    "position": {"x": shape.left, "y": shape.top}
                                                })
                                        
                                        if text_blocks:
                                            text_blocks.sort(key=lambda x: (x["position"]["y"], x["position"]["x"]))
                                            slide_texts.append({
                                                "slide_number": slide_idx + 1,
                                                "text_blocks": text_blocks
                                            })
                                    
                                    # Generate new content
                                    structured_slides = analyze_slide_structure(slide_texts)
                                    generated_sections = generate_ppt_sections(user_resume, structured_slides)
                                    
                                    text_elements = template_data['text_elements']
                                    content_mapping, heading_shapes, basic_info_shapes = match_generated_to_original(
                                        text_elements, generated_sections, prs)
                                    
                                    # Create new edits
                                    edits = {}
                                    for element in text_elements:
                                        key = f"{element['slide']}_{element['shape']}"
                                        if key not in heading_shapes:
                                            edits[key] = content_mapping.get(key, element['original_text'])
                                    
                                    # Apply edits
                                    success_count = 0
                                    for element in text_elements:
                                        key = f"{element['slide']}_{element['shape']}"
                                        if key not in heading_shapes and key in edits:
                                            slide_idx = element['slide'] - 1
                                            shape_idx = element['shape']
                                            
                                            if slide_idx < len(working_prs.slides):
                                                slide = working_prs.slides[slide_idx]
                                                if shape_idx < len(slide.shapes):
                                                    shape = slide.shapes[shape_idx]
                                                    if shape.has_text_frame:
                                                        clear_and_replace_text(shape, edits[key])
                                                        success_count += 1
                                    
                                    # Save output
                                    output = io.BytesIO()
                                    working_prs.save(output)
                                    output.seek(0)
                                    
                                    # Store results
                                    st.session_state.generated_ppt = output.getvalue()
                                    st.session_state.selected_ppt_template_id = template_id
                                    st.session_state.selected_ppt_template = template_data
                                    st.session_state.ppt_template_source = 'saved'
                                    
                                    st.success(f"✅ Using template: {template_data['name']}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error loading template: {str(e)}")

                        with col2:
                            if st.button(f"Delete", key=f"delete_ppt_{template_id}",type="secondary", use_container_width=True):
                                # Clear selection if deleting currently selected template
                                if st.session_state.get('selected_ppt_template_id') == template_id:
                                    st.session_state.pop('generated_ppt', None)
                                    st.session_state.pop('selected_ppt_template_id', None)
                                    st.session_state.pop('selected_ppt_template', None)
                                    st.session_state.pop('ppt_template_source', None)
                                
                                del st.session_state.ppt_templates[template_id]
                                save_user_ppt_templates(st.session_state.logged_in_user, st.session_state.ppt_templates)
                                st.success(f"✅ Deleted '{template_data['name']}'")
                                st.rerun()
            else:
                st.info("📂 No saved PowerPoint templates yet.")
                st.markdown("---")

# ----------------------------------
# HANDLE TEMPLATE MODAL
# ----------------------------------
if template_clicked:
    st.session_state.show_template_modal = True

if st.session_state.show_template_modal:
    st.write("🎉 Show Template modal here...")