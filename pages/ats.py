import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from utils import get_score_color,get_score_label,extract_text_from_pdf,extract_text_from_docx,extract_details_from_text,extract_details_from_jd,ai_ats_score

st.set_page_config(
    page_title="Cvmate ATS Score",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "logged_in_user" not in st.session_state or st.session_state.logged_in_user is None:
    logged_user = st.query_params.get("user")
    if logged_user:
        st.session_state.logged_in_user = logged_user

# Get user info for navigation
current_user = st.session_state.get('logged_in_user', '')
is_logged_in = bool(current_user)

# Build URLs
if is_logged_in and current_user:
    home_url = f"/?user={current_user}"
    change_url = f"change?user={current_user}"
    qu_url = f"qu?user={current_user}"
else:
    home_url = "/"
    change_url = "#change"
    qu_url = "#qu"

if is_logged_in:
    auth_button = '<a class="nav-link" href="?logout=true" target="_self">⏻</a>'
else:
    auth_button = '<a class="nav-link" href="#Login" target="_self">Login</a>'

# COMPLETE CSS Styling with Navigation
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Archivo:wght@400;500;600;700;800;900&display=swap');

/* ==================== RESET ==================== */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

[data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarNav"],
#MainMenu, footer, header {{
    display: none !important;
    visibility: hidden !important;
}}

.stMainBlockContainer, div.block-container, [data-testid="stMainBlockContainer"] {{
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}}

/* ==================== VARIABLES ==================== */
:root {{
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
}}

html, body, .stApp {{
    font-family: 'Inter', sans-serif !important;
    background: var(--bg-primary);
    color: var(--text-primary);
    scroll-behavior: smooth;
}}

/* ==================== NAVIGATION ==================== */
.nav-wrapper {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border);
    animation: slideDown 0.6s ease-out;
}}

@keyframes slideDown {{
    from {{ transform: translateY(-100%); opacity: 0; }}
    to {{ transform: translateY(0); opacity: 1; }}
}}

.nav-container {{
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 3rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 80px;
}}

.logo {{
    font-family: 'Archivo', sans-serif;
    font-size: 28px;
    font-weight: 900;
    background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
}}

.nav-menu {{
    display: flex;
    gap: 2rem;
    align-items: center;
}}

.nav-link {{
    color: var(--text-secondary) !important;
    text-decoration: none !important;
    font-size: 15px;
    font-weight: 500;
    padding: 10px 20px;
    border-radius: 8px;
    transition: all 0.3s ease;
    position: relative;
}}

.nav-link:hover {{
    color: var(--primary) !important;
    background: rgba(255, 107, 53, 0.08);
}}

/* ==================== MAIN WRAPPER ==================== */
.ats-main-wrapper {{
    min-height: 30vh;
    background: linear-gradient(135deg, #fff9f5 0%, #ffffff 50%, #fff5f0 100%);
    padding: 110px 0 40px;
    position: relative;
}}

.ats-main-wrapper::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 200px;
    background: radial-gradient(ellipse at top, rgba(232, 117, 50, 0.06) 0%, transparent 70%);
    pointer-events: none;
}}

.ats-hero {{
    text-align: center;
    margin-bottom: 2.5rem;
    position: relative;
    z-index: 1;
}}

.ats-hero-badge {{
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
}}

.ats-main-title {{
    font-size: 2.5rem;
    font-weight: 800;
    color: #0a0f14;
    margin-bottom: 0.5rem;
    line-height: 1.2;
    letter-spacing: -1px;
}}

.ats-main-title .highlight {{
    background: linear-gradient(135deg, #e87532 0%, #ff8c42 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.ats-hero-description {{
    font-size: 1rem;
    color: #64748b;
    max-width: 600px;
    margin-left: 300px !important;
    line-height: 1.6;
    font-weight: 400;
}}

/* ==================== UPLOAD SECTIONS ==================== */
.upload-sections-wrapper {{
    max-width: 1300px;
    margin: 0 auto;
    padding: 0 2rem;
}}

.upload-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-bottom: 2rem;
}}

.upload-section-card {{
    background: white;
    border-radius: 24px;
    padding: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.04);
    border: 1px solid rgba(232, 117, 50, 0.08);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}}

.upload-section-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #e87532 0%, #ff8c42 50%, #e87532 100%);
    background-size: 200% 100%;
    animation: shimmer 3s infinite;
    opacity: 0;
    transition: opacity 0.3s;
}}

@keyframes shimmer {{
    0% {{ background-position: -200% 0; }}
    100% {{ background-position: 200% 0; }}
}}

.upload-section-card:hover::before {{
    opacity: 1;
}}

.upload-section-card:hover {{
    transform: translateY(-8px);
    box-shadow: 0 16px 48px rgba(232, 117, 50, 0.12);
    border-color: rgba(232, 117, 50, 0.2);
}}

.section-header-wrapper {{
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1.5rem;
}}

.section-icon-box {{
    width: 50px;
    height: 50px;
    background: linear-gradient(135deg, #e87532 0%, #ff8c42 100%);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
    box-shadow: 0 6px 20px rgba(232, 117, 50, 0.25);
}}

.section-header-content {{
    flex: 1;
}}

.section-number {{
    display: inline-block;
    background: #fff5f0;
    color: #e87532;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
}}

.section-title {{
    font-size: 1.35rem;
    font-weight: 700;
    color: #0a0f14;
    margin-bottom: 0.3rem;
    letter-spacing: -0.5px;
}}

.section-subtitle {{
    font-size: 0.85rem;
    color: #64748b;
    line-height: 1.5;
}}

/* ==================== FILE UPLOAD SUCCESS ==================== */
.file-uploaded {{
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    border: 2px solid #10b981;
    border-radius: 16px;
    padding: 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-top: 1rem;
    animation: slideIn 0.4s ease-out;
}}

@keyframes slideIn {{
    from {{ opacity: 0; transform: translateY(-10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.file-check-icon {{
    width: 40px;
    height: 40px;
    background: #10b981;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: white;
    flex-shrink: 0;
}}

.file-details {{ flex: 1; }}

.file-name-text {{
    font-size: 0.9rem;
    font-weight: 600;
    color: #065f46;
    margin-bottom: 0.2rem;
}}

.file-meta {{
    font-size: 0.75rem;
    color: #059669;
    display: flex;
    gap: 0.75rem;
}}

/* ==================== ACTION BUTTONS ==================== */
.action-section {{
    max-width: 1300px;
    margin: 0 auto;
    padding: 0 2rem;
}}

.button-group {{
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    margin-bottom: 2rem;
}}

/* ==================== INFO CARDS ==================== */
.info-cards-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.25rem;
    max-width: 1300px;
    margin: 2rem auto 0;
    padding: 0 2rem;
}}

.info-card {{
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    border: 1px solid rgba(232, 117, 50, 0.1);
    transition: all 0.3s ease;
}}

.info-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 10px 32px rgba(232, 117, 50, 0.12);
    border-color: rgba(232, 117, 50, 0.3);
}}

.info-card-icon {{
    font-size: 2rem;
    margin-bottom: 0.75rem;
}}

.info-card-title {{
    font-size: 1rem;
    font-weight: 700;
    color: #0a0f14;
    margin-bottom: 0.4rem;
}}

.info-card-text {{
    font-size: 0.85rem;
    color: #64748b;
    line-height: 1.5;
}}

/* ==================== TEXT AREA ==================== */
textarea {{
    background: white !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 1.25rem !important;
    font-size: 0.9rem !important;
    color: #0a0f14 !important;
    line-height: 1.6 !important;
    transition: all 0.3s ease !important;
    min-height: 200px !important;
}}

textarea:focus {{
    border-color: #e87532 !important;
    box-shadow: 0 0 0 3px rgba(232, 117, 50, 0.1) !important;
    outline: none !important;
    background: #fff9f5 !important;
}}

textarea::placeholder {{
    color: #94a3b8 !important;
}}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 1200px) {{
    .upload-grid {{ gap: 1.5rem; }}
    .info-cards-grid {{ grid-template-columns: 1fr; }}
}}

@media (max-width: 968px) {{
    .upload-grid {{ grid-template-columns: 1fr; }}
    .ats-main-title {{ font-size: 2rem; }}
    .button-group {{ flex-direction: column; }}
    .nav-container {{ padding: 0 1.5rem; }}
    .nav-menu {{ gap: 0.5rem; flex-wrap: wrap; justify-content: center; }}
    .nav-link {{ padding: 8px 12px; font-size: 13px; }}
}}

@media (max-width: 640px) {{
    .upload-section-card {{ padding: 1.5rem; }}
    .section-header-wrapper {{ gap: 0.75rem; }}
    .section-icon-box {{ width: 45px; height: 45px; font-size: 20px; }}
}}
</style>
""", unsafe_allow_html=True)

# Navigation Bar
st.markdown(f"""
<div class="nav-wrapper">
    <div class="nav-container">
        <div class="logo">CVmate</div>
        <div class="nav-menu">
            <a class="nav-link" href="{home_url}" target="_self">Home</a>
            <a class="nav-link" href="main?&user={current_user}" target="_self">Create Resume</a>
            <a class="nav-link" href="{change_url}" target="_self">Change Template</a>
            <a class="nav-link" href="{qu_url}" target="_self">AI Assistant</a>
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

# Page Content
st.markdown("""
<div class="ats-main-wrapper">
    <div class="ats-hero">
        <div class="ats-hero-badge">✨ AI-POWERED ATS ANALYSIS</div>
        <h1 class="ats-main-title">Check Your <span class="highlight">ATS Score</span></h1>
        <p class="ats-hero-description">
            Upload your resume and paste the job description to get an instant ATS compatibility score with detailed insights
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Upload Sections
st.markdown('<div class="upload-sections-wrapper"><div class="upload-grid">', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="upload-section-card">
        <div class="section-header-wrapper">
            <div class="section-icon-box">📄</div>
            <div class="section-header-content">
                <span class="section-number">STEP 1</span>
                <h2 class="section-title">Upload Your Resume</h2>
                <p class="section-subtitle">PDF or DOCX format for analysis</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx"],
        key="resume_file"
    )
    
    if uploaded_file:
        st.markdown(f"""
        <div class="file-uploaded">
            <div class="file-check-icon">✓</div>
            <div class="file-details">
                <div class="file-name-text">{uploaded_file.name}</div>
                <div class="file-meta">
                    <span>📊 {uploaded_file.size / 1024:.1f} KB</span>
                    <span>✅ Ready for analysis</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="upload-section-card">
        <div class="section-header-wrapper">
            <div class="section-icon-box">📋</div>
            <div class="section-header-content">
                <span class="section-number">STEP 2</span>
                <h2 class="section-title">Paste Job Description</h2>
                <p class="section-subtitle">Complete job posting for matching</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    job_description = st.text_area(
        "Job Description",
        placeholder="""Paste the complete job description here...

• Job title and company
• Required skills and qualifications  
• Responsibilities and duties
• Experience requirements
• Technical skills and tools""",
        height=240,
        key="job_desc"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# Action Buttons
st.markdown('<div class="action-section">', unsafe_allow_html=True)
st.markdown('<div class="button-group">', unsafe_allow_html=True)

btn_col1, btn_col2 = st.columns([1, 1])

with btn_col1:
    with stylable_container(
        "analyze-btn",
        css_styles="""
            button {
                width: 100%;
                padding: 16px 40px !important;
                background: linear-gradient(135deg, #e87532 0%, #ff8c42 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: 50px !important;
                font-size: 1.05rem !important;
                font-weight: 700 !important;
                letter-spacing: 0.3px !important;
                box-shadow: 0 6px 20px rgba(232, 117, 50, 0.3) !important;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 10px 28px rgba(232, 117, 50, 0.4) !important;
            }
        """
    ):
        analyze_btn = st.button("🎯 Analyze ATS Score")

with btn_col2:
    with stylable_container(
        "clear-btn",
        css_styles="""
            button {
                width: 100%;
                padding: 16px 40px !important;
                background: white !important;
                color: #e87532 !important;
                border: 2px solid #e87532 !important;
                border-radius: 50px !important;
                font-size: 1.05rem !important;
                font-weight: 700 !important;
                transition: all 0.3s ease !important;
            }
            button:hover {
                background: #e87532 !important;
                color: white !important;
                transform: translateY(-2px) !important;
            }
        """
    ):
        clear_btn = st.button("🗑️ Clear All")

st.markdown('</div></div>', unsafe_allow_html=True)

# Info Cards
st.markdown("""
<div class="info-cards-grid">
    <div class="info-card">
        <div class="info-card-icon">⚡</div>
        <h3 class="info-card-title">Instant Analysis</h3>
        <p class="info-card-text">Get your ATS score in seconds with AI analysis</p>
    </div>
    <div class="info-card">
        <div class="info-card-icon">🎯</div>
        <h3 class="info-card-title">Keyword Matching</h3>
        <p class="info-card-text">See which keywords match and are missing</p>
    </div>
    <div class="info-card">
        <div class="info-card-icon">📊</div>
        <h3 class="info-card-title">Detailed Insights</h3>
        <p class="info-card-text">Get actionable recommendations to improve</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Handle Actions
if analyze_btn:
    if uploaded_file and job_description:
        with st.spinner('🔍 Analyzing your resume...'):
            try:
                if uploaded_file.type == "application/pdf":
                    extracted_text = extract_text_from_pdf(uploaded_file)
                else:
                    uploaded_file.seek(0)
                    extracted_text = extract_text_from_docx(uploaded_file)
                
                if not extracted_text or len(extracted_text.strip()) < 50:
                    st.error("⚠️ Could not extract enough text from the file.")
                    st.stop()
                
                parsed_data = extract_details_from_text(extracted_text)
                structured_jd = extract_details_from_jd(job_description)
                ats_data = ai_ats_score(parsed_data, structured_jd)
                # st.write(ats_data)  # For debugging purposes
                # Replace the results display section in your main Streamlit file
                # Find the section after: if uploaded_file and job_description:
                # Replace everything inside the try block after getting ats_data

                # After you get ats_data from: ats_data = ai_ats_score(parsed_data, structured_jd)
                # Use this complete display code:

                if isinstance(ats_data, dict) and "overall_score" in ats_data:
                    score = ats_data.get("overall_score", 0)
                    label = get_score_label(score)
                    color = get_score_color(score)
                    
                    # ============================================================================
                    # MAIN SCORE DISPLAY
                    # ============================================================================
                    st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
                    st.markdown("""
                    <div style="text-align: center; margin: 2rem 0;">
                        <h2 style="font-size: 2rem; font-weight: 800; color: #0a0f14;">
                            📊 Your ATS Analysis Results
                        </h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Score Circle with Label
                    st.markdown(f"""
                    <div style="max-width: 500px; margin: 0 auto 3rem; text-align: center; padding: 2.5rem; background: white; border-radius: 24px; box-shadow: 0 10px 40px rgba(0,0,0,0.08); border: 2px solid {color}20;">
                        <div style="position: relative; width: 160px; height: 160px; margin: auto;">
                            <svg width="160" height="160">
                                <circle cx="80" cy="80" r="70" stroke="#f0f0f0" stroke-width="14" fill="none"/>
                                <circle cx="80" cy="80" r="70" stroke="{color}" stroke-width="14" fill="none" stroke-linecap="round" stroke-dasharray="{round(score*4.4)}, 440" transform="rotate(-90 80 80)"/>
                                <text x="80" y="90" text-anchor="middle" font-size="36" font-weight="800" fill="#0a0f14">{score}</text>
                                <text x="80" y="110" text-anchor="middle" font-size="14" font-weight="600" fill="#64748b">out of 100</text>
                            </svg>
                        </div>
                        <div style="margin-top: 1.5rem;">
                            <div style="display: inline-block; padding: 8px 24px; background: {color}15; color: {color}; border-radius: 50px; font-size: 1.1rem; font-weight: 700; border: 2px solid {color}40;">{label}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # ============================================================================
                    # SCORE BREAKDOWN CARDS
                    # ============================================================================
                    st.markdown("""
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; max-width: 1200px; margin: 0 auto 3rem;">
                    """, unsafe_allow_html=True)
                    
                    scores_data = [
                        ("🎯", "Skill Match", ats_data.get("skill_match_score", 0)),
                        ("💼", "Experience Match", ats_data.get("experience_match_score", 0)),
                        ("🧠", "Semantic Alignment", ats_data.get("semantic_alignment_score", 0))
                    ]
                    
                    for icon, title, subscore in scores_data:
                        subscore_color = get_score_color(subscore)
                        st.markdown(f"""
                        <div style="background: white; padding: 1.5rem; border-radius: 16px; text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.06); border: 2px solid {subscore_color}20;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                            <div style="font-size: 0.85rem; color: #64748b; font-weight: 600; margin-bottom: 0.5rem;">{title}</div>
                            <div style="font-size: 2rem; font-weight: 800; color: {subscore_color};">{subscore}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # ============================================================================
                    # TECHNICAL SKILLS COMPARISON
                    # ============================================================================
                    tech_skills = ats_data.get("technical_skills", {})
                    tech_matched = tech_skills.get("matched", [])
                    tech_missing = tech_skills.get("missing", [])
                    tech_percentage = tech_skills.get("match_percentage", 0)
                    
                    st.markdown(f"""
                    <div style="max-width: 1200px; margin: 0 auto 2rem;">
                        <div style="background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.06);">
                            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                                <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">💻</div>
                                <div style="flex: 1;">
                                    <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700; color: #0a0f14;">Technical Skills Analysis</h3>
                                    <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Match Rate: <strong style="color: #3b82f6;">{tech_percentage}%</strong></p>
                                </div>
                            </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("""
                        <div style="background: #ecfdf5; padding: 1.25rem; border-radius: 12px; border-left: 4px solid #10b981;">
                            <h4 style="margin: 0 0 1rem 0; color: #065f46; font-size: 1.1rem; font-weight: 700;">✅ Matched Skills</h4>
                        """, unsafe_allow_html=True)
                        
                        if tech_matched:
                            for skill in tech_matched:
                                st.markdown(f"""
                                <div style="background: white; padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-radius: 8px; color: #065f46; font-weight: 500; box-shadow: 0 2px 4px rgba(16, 185, 129, 0.1);">
                                    ✓ {skill}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown('<p style="color: #6b7280; font-style: italic; margin: 0;">No matched technical skills identified</p>', unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("""
                        <div style="background: #fef2f2; padding: 1.25rem; border-radius: 12px; border-left: 4px solid #ef4444;">
                            <h4 style="margin: 0 0 1rem 0; color: #991b1b; font-size: 1.1rem; font-weight: 700;">⚠️ Missing Skills</h4>
                        """, unsafe_allow_html=True)
                        
                        if tech_missing:
                            for skill in tech_missing:
                                st.markdown(f"""
                                <div style="background: white; padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-radius: 8px; color: #991b1b; font-weight: 500; box-shadow: 0 2px 4px rgba(239, 68, 68, 0.1);">
                                    ✗ {skill}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown('<p style="color: #6b7280; font-style: italic; margin: 0;">All required technical skills present</p>', unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
                    
                    # ============================================================================
                    # SOFT SKILLS COMPARISON
                    # ============================================================================
                    soft_skills = ats_data.get("soft_skills", {})
                    soft_matched = soft_skills.get("matched", [])
                    soft_missing = soft_skills.get("missing", [])
                    soft_percentage = soft_skills.get("match_percentage", 0)
                    
                    st.markdown(f"""
                    <div style="max-width: 1200px; margin: 0 auto 2rem;">
                        <div style="background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.06);">
                            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                                <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">🤝</div>
                                <div style="flex: 1;">
                                    <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700; color: #0a0f14;">Soft Skills Analysis</h3>
                                    <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Match Rate: <strong style="color: #8b5cf6;">{soft_percentage}%</strong></p>
                                </div>
                            </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("""
                        <div style="background: #f0fdf4; padding: 1.25rem; border-radius: 12px; border-left: 4px solid #22c55e;">
                            <h4 style="margin: 0 0 1rem 0; color: #166534; font-size: 1.1rem; font-weight: 700;">✅ Demonstrated</h4>
                        """, unsafe_allow_html=True)
                        
                        if soft_matched:
                            for skill in soft_matched:
                                st.markdown(f"""
                                <div style="background: white; padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-radius: 8px; color: #166534; font-weight: 500; box-shadow: 0 2px 4px rgba(34, 197, 94, 0.1);">
                                    ✓ {skill}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown('<p style="color: #6b7280; font-style: italic; margin: 0;">No soft skills identified in resume</p>', unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("""
                        <div style="background: #fff7ed; padding: 1.25rem; border-radius: 12px; border-left: 4px solid #f59e0b;">
                            <h4 style="margin: 0 0 1rem 0; color: #92400e; font-size: 1.1rem; font-weight: 700;">⚠️ Could Improve</h4>
                        """, unsafe_allow_html=True)
                        
                        if soft_missing:
                            for skill in soft_missing:
                                st.markdown(f"""
                                <div style="background: white; padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-radius: 8px; color: #92400e; font-weight: 500; box-shadow: 0 2px 4px rgba(245, 158, 11, 0.1);">
                                    ⚡ {skill}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown('<p style="color: #6b7280; font-style: italic; margin: 0;">All soft skills adequately demonstrated</p>', unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
                    
                    # ============================================================================
                    # EXPERIENCE ANALYSIS
                    # ============================================================================
                    exp_analysis = ats_data.get("experience_analysis", {})
                    
                    st.markdown(f"""
                    <div style="max-width: 1200px; margin: 0 auto 2rem;">
                        <div style="background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.06);">
                            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                                <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">📊</div>
                                <div>
                                    <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700; color: #0a0f14;">Experience Analysis</h3>
                                </div>
                            </div>
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
                                <div style="background: #f0f9ff; padding: 1rem; border-radius: 10px;">
                                    <div style="color: #0369a1; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.5rem;">REQUIRED</div>
                                    <div style="color: #0c4a6e; font-size: 1.1rem; font-weight: 700;">{exp_analysis.get('years_required', 'N/A')}</div>
                                </div>
                                <div style="background: #f0f9ff; padding: 1rem; border-radius: 10px;">
                                    <div style="color: #0369a1; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.5rem;">YOUR EXPERIENCE</div>
                                    <div style="color: #0c4a6e; font-size: 1.1rem; font-weight: 700;">{exp_analysis.get('years_present', 'N/A')}</div>
                                </div>
                                <div style="background: #f0f9ff; padding: 1rem; border-radius: 10px;">
                                    <div style="color: #0369a1; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.5rem;">LEVEL MATCH</div>
                                    <div style="color: #0c4a6e; font-size: 1.1rem; font-weight: 700;">{exp_analysis.get('level_match', 'N/A')}</div>
                                </div>
                            </div>
                    """, unsafe_allow_html=True)
                    
                    relevant_exp = exp_analysis.get('relevant_experience', [])
                    if relevant_exp:
                        st.markdown("""
                        <div style="background: #f8fafc; padding: 1rem; border-radius: 10px; border-left: 3px solid #0891b2;">
                            <h4 style="margin: 0 0 0.75rem 0; color: #0c4a6e; font-size: 0.9rem; font-weight: 700;">RELEVANT EXPERIENCE HIGHLIGHTS</h4>
                        """, unsafe_allow_html=True)
                        
                        for exp in relevant_exp:
                            st.markdown(f"""
                            <div style="color: #475569; font-size: 0.85rem; margin-bottom: 0.5rem; padding-left: 1rem; position: relative;">
                                <span style="position: absolute; left: 0; color: #0891b2;">•</span> {exp}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
                    
                    # ============================================================================
                    # STRENGTHS & WEAKNESSES
                    # ============================================================================
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("""
                        <div style="background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.06); height: 100%;">
                            <h3 style="margin: 0 0 1.5rem 0; font-size: 1.3rem; font-weight: 700; color: #0a0f14; display: flex; align-items: center; gap: 0.5rem;">
                                <span style="font-size: 1.5rem;">✅</span> Key Strengths
                            </h3>
                        """, unsafe_allow_html=True)
                        
                        strengths = ats_data.get("strengths", [])
                        if strengths:
                            for strength in strengths:
                                st.markdown(f"""
                                <div style="background: #ecfdf5; padding: 1rem; margin-bottom: 0.75rem; border-radius: 10px; border-left: 3px solid #10b981;">
                                    <p style="margin: 0; color: #065f46; font-weight: 500; line-height: 1.5;">{strength}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown('<p style="color: #6b7280; font-style: italic;">No strengths identified</p>', unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("""
                        <div style="background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.06); height: 100%;">
                            <h3 style="margin: 0 0 1.5rem 0; font-size: 1.3rem; font-weight: 700; color: #0a0f14; display: flex; align-items: center; gap: 0.5rem;">
                                <span style="font-size: 1.5rem;">⚠️</span> Areas for Improvement
                            </h3>
                        """, unsafe_allow_html=True)
                        
                        weaknesses = ats_data.get("weaknesses", [])
                        if weaknesses:
                            for weakness in weaknesses:
                                st.markdown(f"""
                                <div style="background: #fef2f2; padding: 1rem; margin-bottom: 0.75rem; border-radius: 10px; border-left: 3px solid #ef4444;">
                                    <p style="margin: 0; color: #991b1b; font-weight: 500; line-height: 1.5;">{weakness}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown('<p style="color: #6b7280; font-style: italic;">No significant weaknesses identified</p>', unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # ============================================================================
                    # RECOMMENDATIONS
                    # ============================================================================
                    recommendations = ats_data.get("recommendations", [])
                    if recommendations:
                        st.markdown("""
                        <div style="max-width: 1200px; margin: 2rem auto;">
                            <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 20px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 2px solid #f59e0b;">
                                <h3 style="margin: 0 0 1.5rem 0; font-size: 1.3rem; font-weight: 700; color: #78350f; display: flex; align-items: center; gap: 0.5rem;">
                                    <span style="font-size: 1.5rem;">💡</span> Actionable Recommendations
                                </h3>
                        """, unsafe_allow_html=True)
                        
                        for i, rec in enumerate(recommendations, 1):
                            st.markdown(f"""
                            <div style="background: white; padding: 1rem 1.25rem; margin-bottom: 0.75rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(245, 158, 11, 0.1);">
                                <p style="margin: 0; color: #78350f; font-weight: 500; line-height: 1.6;"><strong style="color: #f59e0b; font-size: 1.1rem;">{i}.</strong> {rec}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("</div></div>", unsafe_allow_html=True)
                    
                    # ============================================================================
                    # DETAILED EXPLANATION
                    # ============================================================================
                    explanation = ats_data.get("explanation")
                    if explanation:
                        st.markdown(f"""
                        <div style="max-width: 1200px; margin: 2rem auto;">
                            <div style="background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.06);">
                                <h3 style="margin: 0 0 1rem 0; font-size: 1.3rem; font-weight: 700; color: #0a0f14; display: flex; align-items: center; gap: 0.5rem;">
                                    <span style="font-size: 1.5rem;">🧠</span> Detailed Analysis
                                </h3>
                                <div style="color: #475569; line-height: 1.8; font-size: 0.95rem;">
                                    {explanation}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Success message
                    st.success("✅ Analysis complete! Review your results above.")
                    
                else:
                    st.error("❌ Unable to analyze resume. Please try again.")

            except Exception as e:
                st.error(f"An error occurrd during analysis: {str(e)}")