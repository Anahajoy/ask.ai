import streamlit as st
import time 
from utils import load_users,save_users,is_valid_email,get_user_resume,image_to_base64_local
from PIL import Image

st.set_page_config(page_title="Login Page", layout="wide", initial_sidebar_state="collapsed")

st.cache_data.clear()
st.cache_resource.clear()

if 'mode' not in st.session_state:
    st.session_state.mode = 'login'

# Initialize page transition state
if 'page_transitioning' not in st.session_state:
    st.session_state.page_transitioning = False

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family/Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Hide Streamlit default elements */
    #MainMenu, footer, header, button[kind="header"] {visibility: hidden;}
    [data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarNav"] {display: none;}
    
    /* CRITICAL: Remove ALL scrollbars and prevent scrolling */
    * {
        scrollbar-width: none !important;
        -ms-overflow-style: none !important;
    }
    *::-webkit-scrollbar {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
    }
    
    html, body {
        overflow: hidden !important;
        height: 100vh !important;
        margin: 0 !important;
        padding: 0 !important;
        position: fixed !important;
        width: 100% !important;
    }
    
    /* Full-screen background with modern workspace image */
    .stApp {
        height: 100vh !important;
        max-height: 100vh !important;
        overflow: hidden !important;
        background: url('https://plus.unsplash.com/premium_photo-1666820202651-314501c88358?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=870') center/cover fixed no-repeat;
        font-family: 'Inter', sans-serif;
        position: relative;
    }
    
    /* Modern dark overlay for better contrast */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.21) 0%, rgba(30, 41, 59, 0.88) 100%);
        z-index: 0;
    }
    
    /* Remove default padding but keep relative positioning */
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100vw !important;
        position: relative;
        z-index: 1;
        height: 100vh !important;
        overflow: hidden !important;
    }
    
    [data-testid="stAppViewContainer"], .main {
        overflow: hidden !important;
        height: 100vh !important;
        max-height: 100vh !important;
        position: fixed !important;
        width: 100% !important;
        top: 0 !important;
        left: 0 !important;
    }
    
    /* Additional overflow prevention */
    [data-testid="stAppViewContainer"] > section,
    [data-testid="stMainBlockContainer"] {
        overflow: hidden !important;
        height: 100vh !important;
        max-height: 100vh !important;
    }
    
/* Center container - positioned at top with scroll capability */
 .main-container {
    position: fixed;
    top: 2vh;  /* Small top margin */
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    width: 100%;
    max-width: 480px;
    max-height: 96vh;  /* Allow almost full height */
    padding: 0.5rem 1rem;
    z-index: 10;
    overflow-y: auto;  /* Enable vertical scrolling */
    overflow-x: hidden;
    transition: opacity 0.5s ease-out, transform 0.5s ease-out;
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}

.main-container::-webkit-scrollbar {
    width: 6px;
    display: block !important;
}

.main-container::-webkit-scrollbar-track {
    background: transparent;
}

.main-container::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 3px;
}
    /* Container for form elements with scroll if needed */
    .form-container {
        width: 100%;
        max-height: 85vh; /* Limit height to allow scrolling if needed */
        overflow-y: auto; /* Enable scrolling if content overflows */
        padding: 0.5rem 0;
    }
    
    .main-container.fade-out {
        opacity: 0;
        transform: translate(-50%, -5%);
    }
    
    /* Logo container - reduced spacing */
    .logo-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 0.5rem;
        margin-top: -100px;
        width: 100%;
    }

    
    .subtitle {
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
        margin-top: 0.2rem;
        font-weight: 400;
        letter-spacing: 0.3px;
    }
    
    /* Clean input fields - minimal spacing */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.85) !important;
        color: #000000 !important;
        border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        font-size: 0.95rem !important;
        font-weight: 400 !important;
        transition: all 0.3s ease !important;
        font-family: 'Inter', sans-serif !important;
    }

    .stTextInput > div > div > input:focus {
        background: #ffffff !important;
        border-color: rgba(8, 145, 178, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(8, 145, 178, 0.15) !important;
        outline: none !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: rgba(0, 0, 0, 0.45) !important;
        font-weight: 300 !important;
    }
    
    /* Solid color button - peacock blue - REDUCED WIDTH */
    .stButton > button {
        background: #0891b2 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        max-width: 200px !important;
        margin: 0.8rem auto 0 auto !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 14px 0 rgba(8, 145, 178, 0.35) !important;
        letter-spacing: 0.3px !important;
        font-family: 'Inter', sans-serif !important;
        text-align: center !important;
        display: block !important;
    }
    
    .stButton > button:hover {
        background: #0e7490 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px 0 rgba(8, 145, 178, 0.45) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Link buttons - clean text links */
    .stButton[key="create_link"] > button, 
    .stButton[key="help_link"] > button {
        background: transparent !important;
        border: none !important;
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: 0.9rem !important;
        padding: 6px 0 !important;
        box-shadow: none !important;
        text-decoration: none !important; 
        margin-top: 0.4rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.3px !important;
        text-transform: uppercase !important;
    }
    
    .stButton[key="create_link"] > button:hover, 
    .stButton[key="help_link"] > button:hover {
        color: #ffffff !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* Divider */
    [data-testid="stHorizontalBlock"] > div > div:nth-child(2) > p {
        color: rgba(255, 255, 255, 0.25) !important;
        text-align: center !important; 
        margin-top: 0.4rem !important;
        font-size: 1rem !important;
    }
    
    /* Alert styling - minimal spacing */
    .stAlert {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        margin-top: 0.4rem !important;
        margin-bottom: 0.4rem !important;
        padding: 0.6rem !important;
        max-width: 100% !important;
    }
    
    /* Input label visibility fix */
    .stTextInput label {
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Target the column that contains all form elements - NO BACKGROUND */
    div[data-testid="column"]:has(.form-wrapper) {
        position: relative;
        width: 100%;
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
        padding: 0 !important;
    }

    /* Ensure form elements are above the background */
    div[data-testid="column"]:has(.form-wrapper) > div {
        position: relative;
        z-index: 1;
    }

    /* Form wrapper */
    .form-wrapper {
        display: contents;
    }

    /* Minimal spacing between inputs */
    .stTextInput {
        margin-bottom: 0.4rem !important;
    }
    
    /* First input spacing */
    .stTextInput:first-of-type {
        margin-top: 0rem !important;
    }

    /* Reduce button top margin */
    .stButton > button {
        margin-top: 0.5rem !important;
    }
    
    /* Links container spacing */
    [data-testid="stHorizontalBlock"] {
        margin-top: 0.5rem !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    /* Center the columns inside horizontal block */
    [data-testid="stHorizontalBlock"] > div {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="main-container" id="main-container">', unsafe_allow_html=True)

try:
    logo = Image.open("image/11.png")
    st.markdown(
        f"""
        <div class="logo-wrapper">
            <img src="data:image/png;base64,{image_to_base64_local(logo)}" alt="Logo">
        </div>
        """,
        unsafe_allow_html=True
    )
except Exception as e:
    st.error(f"Logo could not be loaded: {e}")

with st.container(border=False):
    col1, col2, col3 = st.columns([0.5, 2, 0.5]) 
    
    with col2:
        subtitle_text = "Create your account to get started" if st.session_state.mode == 'register' else "Welcome back! Please login to continue"
        st.markdown(f'<div class="subtitle">{subtitle_text}</div>', unsafe_allow_html=True)

        st.markdown('<div class="form-wrapper">', unsafe_allow_html=True)
        name = ""
        if st.session_state.mode == 'register':
            name = st.text_input("Full Name", placeholder="Enter your full name", label_visibility="collapsed", key="full_name")

        email = st.text_input("Email", placeholder="Enter your email address", label_visibility="collapsed", key="email")
        password = st.text_input("Password", placeholder="Enter your password", type="password", label_visibility="collapsed", key="password")
        
        button_text = "Sign-Up" if st.session_state.mode == 'register' else "Sign-In"
        
        if st.button(button_text, key="main_action_btn", use_container_width=True):
            if email and password:
                if not is_valid_email(email):
                    st.error("Please enter a valid email address")
                else:
                    users = load_users()
                    
                    if st.session_state.mode == 'login':
                        # LOGIN MODE
                        user_entry = users.get(email)
                        
                        if isinstance(user_entry, dict):
                            stored_pw = user_entry.get("password")
                            stored_name = user_entry.get("name")
                        else:
                            stored_pw = user_entry
                            stored_name = None

                        if user_entry is None or stored_pw != password:
                            st.error("Invalid email or password")
                        else:
                            st.session_state.logged_in_user = email
                            st.session_state.username = stored_name or email.split('@')[0]

                            user_resume = get_user_resume(email)
                            
                            if user_resume and len(user_resume) > 0:
                                st.session_state.resume_source = user_resume
                                st.session_state.input_method = user_resume.get("input_method", "Manual Entry")
                                st.success(f"Welcome back, {st.session_state.username}! Loading your saved resume...")
                                time.sleep(0.8)
                                st.switch_page("pages/job.py")
                            else:
                                st.success(f"Welcome, {st.session_state.username}! Let's create your resume.")
                                time.sleep(0.8)
                                st.switch_page("pages/main.py")
                    else:
                        if email in users:
                            st.error("Email already registered. Please login.")
                            st.session_state.mode = 'login'
                            st.rerun()
                        elif len(password) < 6:
                            st.error("Password must be at least 6 characters long")
                        elif not name or len(name.strip()) == 0:
                            st.error("Please enter your full name")
                        else:
                            # Successful Registration
                            users[email] = {"password": password, "name": name.strip()}
                            save_users(users)
                            st.session_state.logged_in_user = email
                            st.session_state.username = name.strip()
                            st.session_state.mode = 'login'
                            st.success(f"Account created successfully, {name.strip()}! Redirecting...")
                            time.sleep(0.8)
                            st.switch_page("pages/main.py")
            else:
                st.warning("Please enter both email and password")

        col_link1, col_sep, col_link2 = st.columns([1, 0.05, 1])
        
        with col_link1:
            col_a, col_b = st.columns([1, 2])
            with col_b:
                if st.button("Create Account" if st.session_state.mode == 'login' else "Back to Login", 
                            key="create_link", use_container_width=True):
                    st.session_state.mode = 'register' if st.session_state.mode == 'login' else 'login'
                    st.rerun()
        
        with col_sep:
            st.markdown('<p style="color: rgba(255, 255, 255, 0.25); text-align: center; margin-top: 0.4rem; font-size: 1rem;">|</p>', unsafe_allow_html=True)
        
        with col_link2:
            col_c, col_d = st.columns([2, 1])
            with col_c:
                if st.button("Need Help?", key="help_link", use_container_width=True):
                    st.info("Please contact support at support@ask.ai")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)