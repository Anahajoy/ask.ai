import streamlit as st
# from PIL import Image
from utils import chatbot, show_login_modal, get_user_resume, load_users
from db.db_init import initialize_database
# /, load_user_templates, load_user_doc_templates, save_user_templates, replace_content, save_user_doc_templates, load_user_ppt_templates, analyze_slide_structure, generate_ppt_sections, match_generated_to_original, clear_and_replace_text, save_user_ppt_templates
# from streamlit_extras.stylable_container import stylable_container
# from templates.templateconfig import SYSTEM_TEMPLATES, ATS_COLORS, load_css_template


if 'db_initialized' not in st.session_state:
    try:
        initialize_database()
        st.session_state.db_initialized = True
        print("✅ Database initialized successfully")
    except Exception as e:
        st.error(f"❌ Database initialization failed: {e}")
        st.stop()
        
st.set_page_config(
    page_title="Cvmate",
    layout="wide",
    initial_sidebar_state="collapsed"
)



        
st.set_page_config(
    page_title="Cvmate",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session State Initialization
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

if "show_login_modal" not in st.session_state:
    st.session_state.show_login_modal = False

if "show_template_modal" not in st.session_state:
    st.session_state.show_template_modal = False

if "scroll_to" not in st.session_state:
    st.session_state.scroll_to = None

if "template_view_mode" not in st.session_state:
    st.session_state.template_view_mode = "custom"

if 'current_template_type' not in st.session_state:
    st.session_state.current_template_type = "html"

# CSS Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Archivo:wght@400;500;600;700;800;900&display=swap');

    /* ==================== RESET ==================== */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

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
        max-width: 100% !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
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
        background: rgba(255, 255, 255, 0.95);
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

    .nav-link.btn-primary {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white !important;
        font-weight: 600;
        padding: 12px 28px;
        box-shadow: 0 4px 12px var(--shadow);
    }

    .nav-link.btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px var(--shadow);
    }

    /* ==================== HERO SECTION ==================== */
    .hero-section {
        min-height: 100vh;
        display: flex;
        align-items: center;
        padding: 120px 3rem 80px;
        background: linear-gradient(180deg, #FAFAFA 0%, #FFFFFF 100%);
        position: relative;
        overflow: hidden;
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 800px;
        height: 800px;
        background: radial-gradient(circle, rgba(255, 107, 53, 0.08) 0%, transparent 70%);
        border-radius: 50%;
        animation: float 20s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% { transform: translate(0, 0); }
        50% { transform: translate(-50px, -50px); }
    }

    .hero-container {
        max-width: 1400px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 4rem;
        align-items: center;
        position: relative;
        z-index: 1;
    }

    .hero-content {
        animation: fadeInLeft 1s ease-out;
    }

    @keyframes fadeInLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(255, 107, 53, 0.1);
        padding: 8px 20px;
        border-radius: 50px;
        font-size: 13px;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 107, 53, 0.2);
    }

    .hero-badge::before {
        content: '✨';
        font-size: 16px;
    }

    .hero-title {
        font-family: 'Archivo', sans-serif;
        font-size: 64px;
        font-weight: 900;
        line-height: 1.1;
        color: var(--text-primary);
        margin-bottom: 1.5rem;
        letter-spacing: -2px;
    }

    .hero-title .gradient-text {
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-subtitle {
        font-size: 20px;
        line-height: 1.7;
        color: var(--text-secondary);
        margin-bottom: 3rem;
        max-width: 500px;
    }

    .hero-buttons {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin-top: 1rem;
        align-items: center;
    }

    .hero-buttons .btn,
    .hero-buttons button {
        min-width: 200px !important;
        flex: 0 1 auto;
    }

    /* Ensure hero buttons container is centered when empty */
    #hero-btn-container {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        align-items: center;
        justify-content: flex-start;
        min-height: 60px;
    }

    .hero-image {
        position: relative;
        animation: fadeInRight 1s ease-out;
    }

    @keyframes fadeInRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    .hero-image img {
        width: 100%;
        height: auto;
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
    }

    /* ==================== FEATURES SECTION ==================== */
    .features-section {
        padding: 120px 3rem;
        background: var(--bg-secondary);
    }

    .features-container {
        max-width: 1400px;
        margin: 0 auto;
    }

    .section-header {
        text-align: center;
        margin-bottom: 4rem;
    }

    .section-badge {
        display: inline-block;
        background: rgba(255, 107, 53, 0.1);
        padding: 8px 20px;
        border-radius: 50px;
        font-size: 13px;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 107, 53, 0.2);
    }

    .section-title {
        font-family: 'Archivo', sans-serif;
        font-size: 48px;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 1rem;
        letter-spacing: -1px;
    }

    .section-subtitle {
        font-size: 18px;
        color: var(--text-secondary);
        max-width: 600px;
        margin-left: 300px !important;
        line-height: 1.7;
    }

    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 2rem;
    }

    .feature-card {
        background: var(--bg-primary);
        padding: 3rem;
        border-radius: 20px;
        border: 1px solid var(--border);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }

    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.4s ease;
    }

    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        border-color: var(--primary);
    }

    .feature-card:hover::before {
        transform: scaleX(1);
    }

    .feature-icon {
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px var(--shadow);
    }

    .feature-title {
        font-family: 'Archivo', sans-serif;
        font-size: 24px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }

    .feature-description {
        font-size: 15px;
        line-height: 1.7;
        color: var(--text-secondary);
    }

    /* ==================== HOW IT WORKS ==================== */
    .steps-section {
        padding: 120px 3rem;
        background: var(--bg-primary);
    }

    .steps-container {
        max-width: 1400px;
        margin: 0 auto;
    }

    .steps-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 3rem;
        margin-top: 4rem;
    }

    .step-card {
        text-align: center;
        position: relative;
    }

    .step-number {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Archivo', sans-serif;
        font-size: 32px;
        font-weight: 900;
        color: white;
        margin: 0 auto 1.5rem;
        box-shadow: 0 8px 24px var(--shadow);
    }

    .step-title {
        font-family: 'Archivo', sans-serif;
        font-size: 22px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }

    .step-description {
        font-size: 15px;
        line-height: 1.7;
        color: var(--text-secondary);
    }

    /* ==================== CTA SECTION ==================== */
    .cta-section {
        padding: 120px 3rem;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        position: relative;
        overflow: hidden;
    }

    .cta-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -20%;
        width: 600px;
        height: 600px;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        border-radius: 50%;
    }

    .cta-container {
        max-width: 800px;
        margin: 0 auto;
        text-align: center;
        position: relative;
        z-index: 1;
    }

    .cta-title {
        font-family: 'Archivo', sans-serif;
        font-size: 48px;
        font-weight: 900;
        color: white;
        margin-bottom: 1.5rem;
        letter-spacing: -1px;
    }

    .cta-subtitle {
        font-size: 20px;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 3rem;
        line-height: 1.7;
    }

    .cta-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
    }

        /* Button styling - FIXED */
        [data-testid="stButton"] button {
            background: linear-gradient(135deg, #FF6B35 0%, #E85A28 100%) !important;
            color: #FFFFFF !important;
            font-size: 15px !important;
            padding: 16px 40px !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px !important;
            text-transform: uppercase !important;
            cursor: pointer !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            font-family: 'Inter', sans-serif !important;
            box-shadow: 0 6px 20px rgba(255, 107, 53, 0.3) !important;
            margin-top: 1rem !important;
            margin-left: 150px !important;
        }
        
        [data-testid="stButton"] button:hover {
            background: linear-gradient(135deg, #E85A28 0%, #D84315 100%) !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 30px rgba(255, 107, 53, 0.4) !important;
        }

        [data-testid="stButton"] button:active {
            transform: translateY(-1px) !important;
        }

        /* Ensure buttons are visible */
        .stButton {
            display: block !important;
            visibility: visible !important;
            max-width: 400px !important;  /* ADDED: Constrain button container */
            margin-left: 200px !important; 
        }
    /* ==================== FOOTER ==================== */
    .footer {
        background: var(--text-primary);
        color: white;
        padding: 3rem 3rem 2rem;
    }

    .footer-container {
        max-width: 1400px;
        margin: 0 auto;
        text-align: center;
    }

    .footer-logo {
        font-family: 'Archivo', sans-serif;
        font-size: 24px;
        font-weight: 900;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
    }

    .footer-text {
        color: rgba(255, 255, 255, 0.6);
        font-size: 14px;
        margin-top: 2rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Hide Streamlit Buttons */
    .stButton {
        display: block !important;
        visibility: visible !important;
        margin: 0.5rem 0 !important;
    }
    
    /* Ensure buttons show in columns before JavaScript moves them */
    [data-testid="column"] .stButton {
        margin: 0.5rem auto !important;
        text-align: center !important;
    }

    /* ==================== RESPONSIVE ==================== */
    @media (max-width: 1024px) {
        .hero-container {
            grid-template-columns: 1fr;
            text-align: center;
        }

        .hero-content {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .hero-title {
            font-size: 48px;
        }

        .hero-subtitle {
            max-width: 100%;
        }

        .features-grid {
            grid-template-columns: 1fr;
        }

        .steps-grid {
            grid-template-columns: 1fr;
        }
    }

    @media (max-width: 768px) {
        .nav-container {
            padding: 0 1.5rem;
        }

        .nav-menu {
            gap: 0.5rem;
        }

        .nav-link {
            padding: 8px 12px;
            font-size: 13px;
        }

        .hero-section {
            padding: 100px 1.5rem 60px;
        }

        .hero-title {
            font-size: 36px;
        }

        .section-title {
            font-size: 36px;
        }

        .cta-title {
            font-size: 36px;
        }

        .hero-buttons,
        .cta-buttons {
            flex-direction: column;
        }

        .btn {
            width: 100%;
            justify-content: center;
        }
            

            /* Pull Streamlit hero buttons into hero section */
.hero-btn-streamlit {
    max-width: 520px;
    margin-top: -260px;   /* THIS is the key line */
    position: relative;
    z-index: 20;
}

/* Button sizing consistency */
.hero-btn-streamlit [data-testid="stButton"] > button {
    min-width: 220px;
    height: 56px;
    font-size: 16px;
    font-weight: 700;
}

    }
    </style>
""", unsafe_allow_html=True)

# Handle Logout
if st.query_params.get("logout") == "true":
    st.session_state.logged_in_user = None
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.rerun()

# Handle Home Navigation
if st.query_params.get("home") == "true":
    if "home" in st.query_params:
        del st.query_params["home"]
    if st.session_state.logged_in_user:
        st.query_params["user"] = st.session_state.logged_in_user
    st.rerun()

# Get Current User
current_user = st.session_state.get('logged_in_user', '')
is_logged_in = bool(current_user)

# Build URLs
if is_logged_in and current_user:
    ats_url = f"ats?user={current_user}"
    qu_url = f"qu?user={current_user}"
    change_url = f"change?user={current_user}"
    auth_link = '<a class="nav-link" href="?logout=true" title="Logout" target="_self">⏻</a>'
else:
    ats_url = "#features"
    qu_url = "#how-it-works"
    change_url = "#change"
    auth_link = '<a class="nav-link btn-primary" href="#Login" target="_self">Get Started</a>'

# Navigation Bar
st.markdown(f"""
<div class="nav-wrapper">
    <div class="nav-container">
        <div class="logo">CVmate</div>
        <div class="nav-menu">
            <a class="nav-link" href="#features">Features</a>
            <a class="nav-link" href="#how-it-works">How It Works</a>
            <a class="nav-link" href="{ats_url}" target="_self">ATS Checker</a>
            <a class="nav-link" href="{qu_url}" target="_self">AI Assistant</a>
            <a class="nav-link" href="{change_url}" target="_self">Change Template</a>
            {auth_link}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# Hero Section
st.markdown("""
<div class="hero-section" id="Home">
    <div class="hero-container">
        <div class="hero-content">
            <div class="hero-badge">AI-Powered Resume Builder</div>
            <h1 class="hero-title">
                Create <span class="gradient-text">ATS-Optimized</span> Resumes in Minutes
            </h1>
            <p class="hero-subtitle">
                Transform your career with AI-powered resume generation, ATS score checking, and intelligent assistant that helps you land your dream job.
            </p>
            <div class="hero-buttons" id="hero-btn-container">
                <!-- Buttons will be inserted here by JavaScript -->
            </div>
        </div>
        <div class="hero-image">
            <img src="https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=800&h=600&fit=crop" alt="Resume Creation">
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Create Streamlit Buttons (Hidden with CSS)
# Hero Buttons (Streamlit layer)
with st.container():
    st.markdown('<div class="hero-btn-streamlit">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        create_resume_clicked = st.button(
            "Create Resume Now →",
            key="hero-create",
            use_container_width=True
        )

    with col2:
        change_template_clicked = st.button(
            "Change Template",
            key="hero-template",
            use_container_width=True
        )

    st.markdown('</div>', unsafe_allow_html=True)


# JavaScript to Move Buttons into Hero Section
st.markdown("""
<script>
    // Function to move buttons with better styling
    function moveHeroButtons() {
        const container = document.getElementById('hero-btn-container');
        if (!container) {
            console.log('Hero container not found');
            return false;
        }
        
        // Find all buttons in the first set of columns
        const allButtons = document.querySelectorAll('[data-testid="stButton"] button');
        
        if (allButtons.length < 3) {
            console.log('Not enough buttons found:', allButtons.length);
            return false;
        }
        
        // Get the first 3 buttons (hero buttons)
        const createBtn = allButtons[0];
        const templateBtn = allButtons[2];
        
        // Check if buttons already moved
        if (container.querySelector('button')) {
            console.log('Buttons already in container');
            return true;
        }
        
        if (createBtn && learnBtn && templateBtn) {
            // Apply classes
            createBtn.className = 'btn btn-primary';
            templateBtn.className = 'btn btn-secondary';
            
            // Ensure proper display
            [createBtn, learnBtn, templateBtn].forEach(btn => {
                btn.style.display = 'inline-flex';
                btn.style.alignItems = 'center';
                btn.style.justifyContent = 'center';
                btn.style.minWidth = '200px';
            });
            
            // Move to container
            container.appendChild(createBtn);
            container.appendChild(templateBtn);
            
            console.log('Hero buttons moved successfully!');
            return true;
        }
        
        console.log('Buttons found but not moved');
        return false;
    }
    
    // Try multiple times with increasing delays
    let attempts = 0;
    const maxAttempts = 10;
    
    function tryMoveButtons() {
        attempts++;
        const success = moveHeroButtons();
        
        if (!success && attempts < maxAttempts) {
            setTimeout(tryMoveButtons, 100 * attempts);
        }
    }
    
    // Start trying
    tryMoveButtons();
    
    // Also try when Streamlit finishes rendering
    window.addEventListener('load', moveHeroButtons);
    
    // Smooth scroll for Learn More
    document.addEventListener('click', (e) => {
        const btnText = e.target.textContent.trim();
        if (btnText === 'Learn More') {
            e.preventDefault();
            const features = document.getElementById('features');
            if (features) {
                features.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });
</script>
""", unsafe_allow_html=True)

# Features Section
st.markdown("""
<div class="features-section" id="features">
    <div class="features-container">
        <div class="section-header">
            <div class="section-badge">Features</div>
            <h2 class="section-title">Everything You Need to Stand Out</h2>
            <p class="section-subtitle">
                Powerful tools designed to help you create professional, ATS-optimized resumes that get you noticed.
            </p>
        </div>
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <h3 class="feature-title">AI-Powered Generation</h3>
                <p class="feature-description">
                    Our AI analyzes job descriptions and automatically tailors your resume to match the requirements, increasing your chances of getting hired.
                </p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3 class="feature-title">ATS Score Checker</h3>
                <p class="feature-description">
                    Check your resume's ATS compatibility score and get instant feedback on how to improve it for better visibility to recruiters.
                </p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💬</div>
                <h3 class="feature-title">AI Chat Assistant</h3>
                <p class="feature-description">
                    Get personalized advice and suggestions from our AI assistant to enhance your resume content and presentation.
                </p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📄</div>
                <h3 class="feature-title">Multiple Export Formats</h3>
                <p class="feature-description">
                    Download your resume in HTML, DOCX, or PDF formats - perfectly formatted and ready to send to employers.
                </p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎨</div>
                <h3 class="feature-title">Professional Templates</h3>
                <p class="feature-description">
                    Choose from a variety of professionally designed templates that are both visually appealing and ATS-friendly.
                </p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h3 class="feature-title">Job-Specific Optimization</h3>
                <p class="feature-description">
                    Upload a job description and let our AI optimize your resume to match the specific role you're applying for.
                </p>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# How It Works Section
st.markdown("""
<div class="steps-section" id="how-it-works">
    <div class="steps-container">
        <div class="section-header">
            <div class="section-badge">How It Works</div>
            <h2 class="section-title">Create Your Perfect Resume in 3 Steps</h2>
            <p class="section-subtitle">
                Our streamlined process makes it easy to create a professional, job-winning resume.
            </p>
        </div>
        <div class="steps-grid">
            <div class="step-card">
                <div class="step-number">1</div>
                <h3 class="step-title">Input Your Information</h3>
                <p class="step-description">
                    Upload your existing resume or enter your details manually. Add your experience, skills, and education.
                </p>
            </div>
            <div class="step-card">
                <div class="step-number">2</div>
                <h3 class="step-title">Add Job Description</h3>
                <p class="step-description">
                    Paste the job description you're targeting. Our AI analyzes it to tailor your resume perfectly.
                </p>
            </div>
            <div class="step-card">
                <div class="step-number">3</div>
                <h3 class="step-title">Generate & Download</h3>
                <p class="step-description">
                    Get your ATS-optimized resume instantly. Download in your preferred format and apply with confidence.
                </p>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


col3,  col5 = st.columns(2)
with col3:
    cta_start_clicked = st.button("Start Building Now →", key="cta-start-btn", use_container_width=True)
with col5:
    template_clicked = st.button("Change Template", key="template-btn", use_container_width=True)

# CTA Buttons
st.markdown("---")  # Spacer
# CTA Section
# st.markdown("""
# <div class="cta-section">
#     <div class="cta-container">
#         <h2 class="cta-title">Ready to Land Your Dream Job?</h2>
#         <p class="cta-subtitle">
#             Join thousands of professionals who have successfully created ATS-optimized resumes with our AI-powered platform.
#         </p>
#         <div class="cta-buttons" id="cta-btn-container"></div>
#     </div>
# </div>
# """, unsafe_allow_html=True)



# JavaScript to Move CTA Buttons
st.markdown("""
<script>
    // Function to move CTA buttons
    function moveCTAButtons() {
        const ctaContainer = document.getElementById('cta-btn-container');
        if (!ctaContainer) {
            console.log('CTA container not found');
            return false;
        }
        
        // Get all buttons
        const allButtons = document.querySelectorAll('[data-testid="stButton"] button');
        
        if (allButtons.length < 6) {
            console.log('Not enough buttons for CTA:', allButtons.length);
            return false;
        }
        
        // Check if CTA buttons already moved
        if (ctaContainer.querySelector('button')) {
            console.log('CTA buttons already in container');
            return true;
        }
        
        // Get buttons 4, 5, 6 (CTA section)
        const ctaStartBtn = allButtons[3];
        const ctaTemplateBtn = allButtons[5];
        
        if (ctaStartBtn && ctaExploreBtn && ctaTemplateBtn) {
            // Apply classes
            ctaStartBtn.className = 'btn btn-white';
            ctaTemplateBtn.className = 'btn btn-outline';
            
            // Ensure proper display
            [ctaStartBtn, ctaTemplateBtn].forEach(btn => {
                btn.style.display = 'inline-flex';
                btn.style.alignItems = 'center';
                btn.style.justifyContent = 'center';
                btn.style.minWidth = '200px';
            });
            
            // Move to container
            ctaContainer.appendChild(ctaStartBtn);
            ctaContainer.appendChild(ctaTemplateBtn);
            
            console.log('CTA buttons moved successfully!');
            return true;
        }
        
        return false;
    }
    
    // Try multiple times
    let ctaAttempts = 0;
    const maxCtaAttempts = 10;
    
    function tryMoveCTAButtons() {
        ctaAttempts++;
        const success = moveCTAButtons();
        
        if (!success && ctaAttempts < maxCtaAttempts) {
            setTimeout(tryMoveCTAButtons, 100 * ctaAttempts);
        }
    }
    
    // Start trying after a delay (to ensure hero buttons are done first)
    setTimeout(tryMoveCTAButtons, 500);
    
    // Also try on load
    window.addEventListener('load', () => {
        setTimeout(moveCTAButtons, 100);
    });
</script>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <div class="footer-container">
        <div class="footer-logo">CVmate</div>
        <p class="footer-text">
            © 2024 ResumeAI. AI-Powered Resume Builder. All rights reserved.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Handle Button Clicks
if create_resume_clicked or cta_start_clicked:
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

# Handle Change Template Button
if change_template_clicked or template_clicked:
    if st.session_state.logged_in_user is None:
        st.warning("🔒 Please login first to view templates.")
        st.session_state.show_login_modal = True
    else:
        st.session_state.from_template_button = True
        st.switch_page("pages/change.py")

# Show Login Modal if Not Logged In
if st.session_state.logged_in_user is None:
    st.markdown('<div id="Login"></div>', unsafe_allow_html=True)
    show_login_modal()
    st.stop()

# Show Chatbot for Logged In Users
if is_logged_in:
    email = st.session_state.logged_in_user
    if not st.query_params.get("user"):
        st.query_params["user"] = email
    
    user_resume = get_user_resume(email)
    has_resume = user_resume and len(user_resume) > 0
    
    # You can uncomment this to show chatbot
    chatbot(user_resume)