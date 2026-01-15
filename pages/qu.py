import streamlit as st
from utils import ask_llama,extract_text_from_pdf,extract_text_from_docx

# Page config
st.set_page_config(page_title="Resume Upload", layout="wide")

# Modern CSS styling
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
    
    /* Hero Header - Compact */
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
    
    /* Features List */
    .features-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #f0f0f0;
    }
    
    .features-title {
        font-size: 1rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #f5f5f5;
    }
    
    .feature-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        border-radius: 8px;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .feature-item:hover {
        background: #fff5f0;
        transform: translateX(3px);
    }
    
    .feature-icon {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #fff5f0 0%, #ffe8dc 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
    }
    
    .feature-text {
        font-size: 0.9rem;
        color: #2c3e50;
        font-weight: 500;
    }
    
    .feature-arrow {
        margin-left: auto;
        color: #cbd5e0;
        font-size: 1.2rem;
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
    
    /* Button styling for chat options */
    .stButton > button {
        background: white;
        color: #2c3e50;
        border: 1.5px solid #e2e8f0;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        font-weight: 500;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 0.5rem;
        width: 100%;
        text-align: left;
    }
    
    .stButton > button:hover {
        background: #fff5f0;
        border-color: #ff8c42;
        color: #ff8c42;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 140, 66, 0.2);
    }
    
    /* Chat container with fixed height and scroll */
    .chat-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        height: 400px;
        overflow-y: auto;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        scroll-behavior: smooth;
    }
    
    /* Custom scrollbar */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: #ff8c42;
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: #ff7a29;
    }
    
    /* Quick actions section - always visible */
    .quick-actions-section {
        margin-bottom: 1.5rem;
    }
    
    .quick-actions-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #64748b;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: #f0fdf4 !important;
        border: 1px solid #86efac !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
    }
    
    /* Text input styling */
    .stTextInput input {
        border-radius: 10px !important;
        border: 1.5px solid #e2e8f0 !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.9rem !important;
    }
    
    .stTextInput input:focus {
        border-color: #ff8c42 !important;
        box-shadow: 0 0 0 2px rgba(255, 140, 66, 0.1) !important;
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
        
        .chat-container {
            height: 300px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None

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
    change_url = f"change?user={current_user}"
else:
    home_url = "/"
    ats_url = "#ats"
    change_url = "#change"

if is_logged_in:
    auth_button = '<a class="nav-link" href="?logout=true" target="_self">Logout</a>'
else:
    auth_button = '<a class="nav-link" href="#Login" target="_self">Login</a>'

# Navigation Bar - Updated to match ResumeAI style
st.markdown(f"""
<div class="nav-wrapper">
    <div class="nav-container">
        <div class="logo">ResumeAI</div>
        <div class="nav-menu">
            <a class="nav-link" href="{home_url}" target="_self">Home</a>
            <a class="nav-link" href="main?&user={current_user}" target="_self">Create Resume</a>
            <a class="nav-link" href="{ats_url}" target="_self">ATS Checker</a>
            <a class="nav-link" href="{change_url}" target="_self">Change Template</a>
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

st.markdown("""
<div class="ats-main-wrapper">
    <div class="ats-hero">
        <div class="ats-hero-badge">✨ AI-Resume Intelligence Hub</div>
        <h1 class="ats-main-title">Resume Analysis <span class="highlight">Assistant</span></h1>
        <p class="ats-hero-description">
            Upload your resume and chat with our AI to get personalized interview questions, strength analysis, resume tips and more.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Content
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Two column layout using Streamlit columns
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="upload-card">
        <div class="upload-icon-large">📄</div>
        <h2 class="upload-title">Drag and drop file to upload</h2>
        <p class="upload-subtitle">or browse to choose a file</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload file",
        type=['pdf', 'docx', 'doc'],
        label_visibility="collapsed"
    )

with col2:
    # st.markdown('<div class="features-card">', unsafe_allow_html=True)
    st.markdown('<div class="features-title">What you\'ll get</div>', unsafe_allow_html=True)
    
    # Feature items
    features = [
        ("❓", "Interview Questions"),
        ("💪", "My Strengths"),
        ("💡", "Resume Tips"),
        ("📈", "How to Improve"),
        ("🎯", "Points to Focus")
    ]
    
    for icon, text in features:
        st.markdown(f"""
        <div class="feature-item">
            <div class="feature-icon">{icon}</div>
            <div class="feature-text">{text}</div>
            <div class="feature-arrow">›</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    # Extract text from file
    if uploaded_file.type == "application/pdf":
        extracted_text = extract_text_from_pdf(uploaded_file)
    else:  # DOCX
        uploaded_file.seek(0)
        extracted_text = extract_text_from_docx(uploaded_file)
    
    # Store resume text in session state
    st.session_state.resume_text = extracted_text
    
    # Hide the upload section and show chat interface
    st.markdown("""
    <style>
    .main-container {
        max-width: 800px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Chat header
    st.markdown(f"""
    <div style="background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 10px rgba(0,0,0,0.08);">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #ff8c42 0%, #ffa666 100%); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">
                    🤖
                </div>
                <div>
                    <div style="font-weight: 600; color: #2c3e50;">Resume Analysis</div>
                    <div style="font-size: 0.85rem; color: #64748b;">Analyzing {uploaded_file.name}</div>
                </div>
            </div>
            <div style="font-size: 0.85rem; color: #94a3b8;">
                {uploaded_file.size / 1024:.1f} KB • {uploaded_file.type.split('/')[-1].upper()}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Actions Section - Always visible
    st.markdown('<div class="quick-actions-section">', unsafe_allow_html=True)
    st.markdown('<div class="quick-actions-title">Quick Actions</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("❓ Generate Interview Questions", key="btn_questions"):
            st.session_state.pending_query = "Generate interview questions based on my resume"
            st.rerun()
        if st.button("💡 Get Resume Tips", key="btn_tips"):
            st.session_state.pending_query = "Give me tips to improve my resume"
            st.rerun()
        if st.button("🎯 Points to Focus", key="btn_focus"):
            st.session_state.pending_query = "What are the key points I should focus on in my resume?"
            st.rerun()
    
    with col2:
        if st.button("💪 Analyze My Strengths", key="btn_strengths"):
            st.session_state.pending_query = "Analyze the strengths shown in my resume"
            st.rerun()
        if st.button("📈 How to Improve", key="btn_improve"):
            st.session_state.pending_query = "How can I improve my resume?"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display welcome message only if chat history is empty
    if len(st.session_state.chat_history) == 0:
        st.markdown("""
        <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
            <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #ff8c42 0%, #ffa666 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                🤖
            </div>
            <div style="background: #f8fafc; padding: 1rem; border-radius: 12px; flex: 1; border-left: 3px solid #ff8c42;">
                <div style="color: #2c3e50; line-height: 1.6;">
                    Great! I've received your resume. Use the quick actions above or type your question below to get started.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat history
    for chat in st.session_state.chat_history:
        # User message
        st.markdown(f"""
        <div style="display: flex; gap: 1rem; margin: 1.5rem 0; justify-content: flex-end;">
            <div style="background: linear-gradient(135deg, #ff8c42 0%, #ffa666 100%); color: white; padding: 1rem; border-radius: 12px; max-width: 70%;">
                <div style="line-height: 1.6;">
                    {chat['user']}
                </div>
            </div>
            <div style="width: 32px; height: 32px; background: #e2e8f0; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                👤
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Bot response
        st.markdown(f"""
        <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
            <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #ff8c42 0%, #ffa666 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                🤖
            </div>
            <div style="background: #f8fafc; padding: 1rem; border-radius: 12px; flex: 1; border-left: 3px solid #ff8c42;">
                <div style="color: #2c3e50; line-height: 1.8;">{chat['bot']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process pending query from button clicks
    if 'pending_query' in st.session_state:
        query = st.session_state.pending_query
        
        # Create a container for new message
        new_message_container = st.container()
        
        with new_message_container:
            # Show user message
            st.markdown(f"""
            <div style="display: flex; gap: 1rem; margin: 1.5rem 0; justify-content: flex-end;">
                <div style="background: linear-gradient(135deg, #ff8c42 0%, #ffa666 100%); color: white; padding: 1rem; border-radius: 12px; max-width: 70%;">
                    <div style="line-height: 1.6;">
                        {query}
                    </div>
                </div>
                <div style="width: 32px; height: 32px; background: #e2e8f0; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    👤
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Bot response with streaming
            st.markdown("""
            <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
                <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #ff8c42 0%, #ffa666 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    🤖
                </div>
                <div style="background: #f8fafc; padding: 1rem; border-radius: 12px; flex: 1; border-left: 3px solid #ff8c42;">
            """, unsafe_allow_html=True)
            
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                for token in ask_llama(query, st.session_state.resume_text):
                    full_response += token
                    response_placeholder.markdown(f'<div style="color: #2c3e50; line-height: 1.8;">{full_response}</div>', unsafe_allow_html=True)
                
                # Add to chat history
                st.session_state.chat_history.append({
                    'user': query,
                    'bot': full_response
                })
                
            except Exception as e:
                response_placeholder.error(f"Error: {str(e)}")
            
            st.markdown("""
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Clear pending query
        del st.session_state.pending_query
    
    # Input area at bottom
    with st.form(key='chat_form', clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input("Ask me anything about your resume...", key="chat_input", label_visibility="collapsed", placeholder="Type your question here...")
        with col2:
            submit_button = st.form_submit_button("Send")
        
        if submit_button and user_input:
            st.session_state.pending_query = user_input
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)