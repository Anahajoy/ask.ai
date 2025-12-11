import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from utils import get_score_color,get_score_label,extract_text_from_pdf,extract_text_from_docx,extract_details_from_text,extract_details_from_jd,ai_ats_score

st.set_page_config(
    page_title="ATS Score Checker",
    page_icon="📊",
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
    ats_url = f"ats?user={current_user}"
    qu_url = f"qu?user={current_user}"
else:
    home_url = "/"
    ats_url = "#ats"
    qu_url = "#qu"


if is_logged_in:
    auth_button = '<div class="nav-item"><a class="nav-link" href="?logout=true" target="_self">Logout</a></div>'
else:
    auth_button = '<div class="nav-item"><a class="nav-link" data-section="Login" href="#Login">Login</a></div>'


# Enhanced CSS Styling
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

#MainMenu, footer, header, button[kind="header"] {{visibility: hidden;}}
.stMainBlockContainer, div.block-container, [data-testid="stMainBlockContainer"] {{
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}}

* {{
    font-family: 'Inter', sans-serif !important;
}}

/* Fixed Navigation Bar */
.nav-wrapper {{
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
}}

.logo {{
    font-size: 24px;
    font-weight: 400;
    color: #2c3e50;
    font-family: 'Nunito Sans', sans-serif !important;
    letter-spacing: -0.5px;
}}

.nav-menu {{
    display: flex;
    gap: 2rem;
    align-items: center;
}}

.nav-item {{ position: relative; }}

.nav-link {{
    color: #000000 !important;
    text-decoration: none !important;
    font-size: 1rem;
    font-family: 'Nunito Sans', sans-serif;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
}}

.nav-link:visited {{
    color: #000000 !important;
}}

.nav-link:hover {{
    background-color: #fff5f0;
    color: #ff8c42 !important;
}}

/* Main Page Wrapper */
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

/* Hero Header - Compact */
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

/* Upload Sections Container */
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

/* Upload Section Card - Compact */
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

/* Section Header - Compact */
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

/* File Upload Success - Compact */
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
    from {{
        opacity: 0;
        transform: translateY(-10px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
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

.file-details {{
    flex: 1;
}}

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

/* Action Buttons Section - Compact */
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

/* Info Cards - Compact */
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

/* Streamlit Text Area */
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

/* Responsive Design */
@media (max-width: 1200px) {{
    .upload-grid {{
        gap: 1.5rem;
    }}
    
    .info-cards-grid {{
        grid-template-columns: 1fr;
    }}
}}

@media (max-width: 968px) {{
    .upload-grid {{
        grid-template-columns: 1fr;
    }}
    
    .ats-main-title {{
        font-size: 2rem;
    }}
    
    .button-group {{
        flex-direction: column;
    }}
    
    .nav-wrapper {{
        padding: 0.6rem 1.5rem;
    }}
    
    .nav-menu {{
        gap: 1rem;
    }}
}}

@media (max-width: 640px) {{
    .upload-section-card {{
        padding: 1.5rem;
    }}
    
    .section-header-wrapper {{
        gap: 0.75rem;
    }}
    
    .section-icon-box {{
        width: 45px;
        height: 45px;
        font-size: 20px;
    }}
}}
</style>
""", unsafe_allow_html=True)

# Navigation Bar
st.markdown(f"""
<div class="nav-wrapper">
    <div class="logo">Resume Creator</div>
    <div class="nav-menu">
        <div class="nav-item">
            <a class="nav-link" href="{home_url}" target="_self">Home</a>
        </div>
        <div class="nav-item">
            <a class="nav-link" href="main?&user={current_user}" target="_self">Create New Resume</a>
        </div>
        <div class="nav-item">
            <a class="nav-link" data-section="qu" href="{qu_url}" target="_self">Analysis Assistant</a>
        </div>
        {auth_button}
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

# Column 1 - Resume Upload
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
    
    # File uploader - now fully visible and functional
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

# Column 2 - Job Description
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
                background: linear-gradient(135deg, #d66629 0%, #e87532 100%) !important;
            }
            button:active {
                transform: translateY(0px) !important;
            }
        """
    ):
        analyze_btn = st.button("🎯 Analyze ATS Score", width='stretch')

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
                letter-spacing: 0.3px !important;
                transition: all 0.3s ease !important;
            }
            button:hover {
                background: #e87532 !important;
                color: white !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(232, 117, 50, 0.25) !important;
            }
            button:active {
                transform: translateY(0px) !important;
            }
        """
    ):
        clear_btn = st.button("🗑️ Clear All", width='stretch')

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
# Replace the "Handle Actions" section in your ats.py file with this code:

# Handle Actions
if analyze_btn:
    if uploaded_file and job_description:
        with st.spinner('🔍 Analyzing your resume against the job description... This may take a moment.'):
            try:
                # Extract text from uploaded file
                if uploaded_file.type == "application/pdf":
                    extracted_text = extract_text_from_pdf(uploaded_file)
                else:  # DOCX
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
                
                # Parse resume and JD
                parsed_data = extract_details_from_text(extracted_text)
                structured_jd = extract_details_from_jd(job_description)
                
                # Get ATS score
                ats_data = ai_ats_score(parsed_data, structured_jd)
                
                if ats_data and ats_data.get("overall_score", 0) > 0:
                    score = ats_data.get("overall_score", 0)
                    label = get_score_label(score)
                    color = get_score_color(score)
                    
                    # Results Section
                    st.markdown('<div style="height: 3rem;"></div>', unsafe_allow_html=True)
                    st.markdown("""
                    <div style="text-align: center; margin: 2rem 0;">
                        <h2 style="font-size: 2rem; font-weight: 800; color: #0a0f14; margin-bottom: 0.5rem;">
                            📊 Your ATS Analysis Results
                        </h2>
                        <p style="color: #64748b; font-size: 1rem;">Here's how your resume matches the job description</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Score Display Card
                    st.markdown(f"""
                    <div style="
                        max-width: 500px;
                        margin: 0 auto 3rem;
                        text-align: center;
                        padding: 2.5rem;
                        background: white;
                        border-radius: 24px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
                        border: 2px solid {color}20;
                    ">
                        <div style="position: relative; width: 160px; height: 160px; margin: auto;">
                            <svg width="160" height="160">
                                <circle cx="80" cy="80" r="70" stroke="#f0f0f0" stroke-width="14" fill="none"/>
                                <circle cx="80" cy="80" r="70"
                                    stroke="{color}" stroke-width="14" fill="none"
                                    stroke-linecap="round"
                                    stroke-dasharray="{round(score*4.4)}, 440"
                                    transform="rotate(-90 80 80)"
                                    style="transition: stroke-dasharray 1s ease-out;"
                                />
                                <text x="80" y="90" text-anchor="middle" font-size="36" font-weight="800" fill="#0a0f14">{score}</text>
                                <text x="80" y="110" text-anchor="middle" font-size="14" font-weight="600" fill="#64748b">out of 100</text>
                            </svg>
                        </div>
                        <div style="margin-top: 1.5rem;">
                            <div style="
                                display: inline-block;
                                padding: 8px 24px;
                                background: {color}15;
                                color: {color};
                                border-radius: 50px;
                                font-size: 1.1rem;
                                font-weight: 700;
                                border: 2px solid {color}40;
                            ">
                                {label}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Keywords Analysis Section
                    st.markdown("""
                    <div style="max-width: 1000px; margin: 0 auto;">
                        <h3 style="
                            text-align: center;
                            font-size: 1.8rem;
                            font-weight: 700;
                            color: #0a0f14;
                            margin-bottom: 2rem;
                        ">
                            🔍 Keyword Analysis
                        </h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Matched and Missing Keywords in Two Columns
                    kw_col1, kw_col2 = st.columns(2, gap="large")
                    
                    with kw_col1:
                        matched = ats_data.get("matched_skills", [])
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                            border-radius: 20px;
                            padding: 2rem;
                            border: 2px solid #10b981;
                            min-height: 250px;
                        ">
                            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                                <div style="
                                    width: 48px;
                                    height: 48px;
                                    background: #10b981;
                                    border-radius: 12px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-size: 24px;
                                ">✓</div>
                                <div>
                                    <h4 style="
                                        font-size: 1.3rem;
                                        font-weight: 700;
                                        color: #065f46;
                                        margin: 0;
                                    ">Matched Keywords</h4>
                                    <p style="
                                        font-size: 0.85rem;
                                        color: #059669;
                                        margin: 0;
                                    ">{len(matched)} keywords found</p>
                                </div>
                            </div>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        """, unsafe_allow_html=True)
                        
                        if matched:
                            for keyword in matched:
                                st.markdown(f"""
                                <span style="
                                    display: inline-block;
                                    padding: 6px 14px;
                                    background: white;
                                    color: #065f46;
                                    border-radius: 8px;
                                    font-size: 0.85rem;
                                    font-weight: 600;
                                    border: 1px solid #10b98140;
                                ">✓ {keyword}</span>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <p style="color: #059669; font-size: 0.9rem; font-style: italic;">
                                No matched keywords found. Consider adding relevant skills from the job description.
                            </p>
                            """, unsafe_allow_html=True)
                        
                        st.markdown('</div></div>', unsafe_allow_html=True)
                    
                    with kw_col2:
                        missing = ats_data.get("missing_skills", [])
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
                            border-radius: 20px;
                            padding: 2rem;
                            border: 2px solid #ef4444;
                            min-height: 250px;
                        ">
                            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                                <div style="
                                    width: 48px;
                                    height: 48px;
                                    background: #ef4444;
                                    border-radius: 12px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-size: 24px;
                                    color: white;
                                ">!</div>
                                <div>
                                    <h4 style="
                                        font-size: 1.3rem;
                                        font-weight: 700;
                                        color: #991b1b;
                                        margin: 0;
                                    ">Missing Keywords</h4>
                                    <p style="
                                        font-size: 0.85rem;
                                        color: #dc2626;
                                        margin: 0;
                                    ">{len(missing)} keywords to add</p>
                                </div>
                            </div>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        """, unsafe_allow_html=True)
                        
                        if missing:
                            for keyword in missing:
                                st.markdown(f"""
                                <span style="
                                    display: inline-block;
                                    padding: 6px 14px;
                                    background: white;
                                    color: #991b1b;
                                    border-radius: 8px;
                                    font-size: 0.85rem;
                                    font-weight: 600;
                                    border: 1px solid #ef444440;
                                ">✗ {keyword}</span>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <p style="color: #dc2626; font-size: 0.9rem; font-style: italic;">
                                Great! All important keywords are present in your resume.
                            </p>
                            """, unsafe_allow_html=True)
                        
                        st.markdown('</div></div>', unsafe_allow_html=True)
                    
                    # Recommendations Section
                    if missing:
                        st.markdown('<div style="height: 2.5rem;"></div>', unsafe_allow_html=True)
                        st.markdown("""
                        <div style="
                            max-width: 1200px;
                            margin: 0 auto;
                            background: linear-gradient(135deg, #fff9f5 0%, #ffe8d6 100%);
                            border-radius: 24px;
                            padding: 2.5rem;
                            box-shadow: 0 8px 32px rgba(232, 117, 50, 0.12);
                            border: 1px solid #e8753220;
                        ">
                            <div style="text-align: center; margin-bottom: 2rem;">
                                <div style="
                                    width: 64px;
                                    height: 64px;
                                    background: linear-gradient(135deg, #e87532, #ff8c42);
                                    border-radius: 20px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    margin: 0 auto 1rem;
                                    box-shadow: 0 8px 24px rgba(232, 117, 50, 0.3);
                                ">
                                    <span style="font-size: 32px;">💡</span>
                                </div>
                                <h3 style="
                                    font-size: 1.75rem;
                                    font-weight: 700;
                                    color: #e87532;
                                    margin: 0;
                                ">How to Improve Your Score</h3>
                            </div>
                            <div style="
                                display: grid;
                                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                                gap: 1.25rem;
                            ">
                        """, unsafe_allow_html=True)
                        
                        tips = [
                            ("📝", "Update Resume", "Incorporate missing keywords naturally into your experience"),
                            ("🎯", "Be Specific", "Use both acronyms and full terms (ML & Machine Learning)"),
                            ("📊", "Add Metrics", "Quantify achievements with numbers and percentages"),
                            ("🔄", "Re-analyze", "Upload updated resume to see your improved score")
                        ]
                        
                        for icon, title, desc in tips:
                            st.markdown(f"""
                            <div style="
                                background: white;
                                border-radius: 16px;
                                padding: 1.5rem;
                                box-shadow: 0 4px 16px rgba(0,0,0,0.04);
                                text-align: center;
                            ">
                                <div style="
                                    font-size: 2.5rem;
                                    margin-bottom: 0.75rem;
                                ">{icon}</div>
                                <h4 style="
                                    font-size: 1.1rem;
                                    font-weight: 700;
                                    color: #0a0f14;
                                    margin: 0 0 0.5rem 0;
                                ">{title}</h4>
                                <p style="
                                    font-size: 0.9rem;
                                    color: #64748b;
                                    margin: 0;
                                    line-height: 1.5;
                                ">{desc}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown('</div></div>', unsafe_allow_html=True)
                    
                    st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
                    st.success("✅ Your ATS analysis is complete! Use these insights to optimize your resume.")
            except:
                st.markdown("please upload a valid resume file and job description.")
    elif not uploaded_file and not job_description:
        st.error("⚠️ Please upload your resume and paste the job description")
    elif not uploaded_file:
        st.warning("⚠️ Please upload your resume")
    else:
        st.warning("⚠️ Please paste the job description")

if clear_btn:
    st.rerun()