import streamlit as st
from pathlib import Path
import json
import re
import time 
from utils import image_to_base64
from PIL import Image
import base64
from io import BytesIO

st.set_page_config(page_title="Login Page", layout="wide", initial_sidebar_state="collapsed")

st.cache_data.clear()
st.cache_resource.clear()

if 'mode' not in st.session_state:
    st.session_state.mode = 'login'  
users_file = Path(__file__).parent / "users.json"
user_data_file = Path(__file__).parent/"user_resume_data.json"

def load_users():
    try:
        if users_file.exists():
            with open(users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        return {}

def save_users(users):
    try:
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        st.error(f"Error saving users: {e}")

def load_user_resume_data():
    """Load all users' resume data"""
    try:
        if user_data_file.exists():
            with open(user_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        return {}

def get_user_resume(email):
    """Get resume data for a specific user"""
    all_data = load_user_resume_data()
    user_resume = all_data.get(email, None)
    
    if user_resume and isinstance(user_resume, dict) and len(user_resume) > 0:
        return user_resume
    return None

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def image_to_base64_local(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Hide Streamlit default elements */
    #MainMenu, footer, header, button[kind="header"] {visibility: hidden;}
    [data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarNav"] {display: none;}
    
    /* Remove scrollbar */
    html, body, [data-testid="stAppViewContainer"], .main {
        overflow: hidden !important;
        height: 100vh !important;
    }
    
    /* Full-screen background with modern workspace image */
    .stApp {
        height: 100vh;
        overflow: hidden;
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
    
    /* Remove default padding */
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100vw !important;
        position: relative;
        z-index: 1;
        overflow: hidden !important;
    }
    
    /* Center container */
    .main-container {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        max-width: 500px;
        padding: 1rem;
    }
    
    /* Logo container - minimal spacing */
    .logo-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 0.8rem;
        width: 100%;
    }
    
    .logo-wrapper img {
        display: block;
        max-width: 400px;
        width: 100%;
        height: auto;
        max-height: 100px;
        object-fit: contain;
    }
    
    /* Modern glassmorphism card - reduced padding */
    .stContainer {
        max-width: 450px;
        width: 100%;
        background: rgba(255, 255, 255, 0.08);
        padding: 24px 32px;
        border-radius: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4),
                    0 0 0 1px rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        animation: slideIn 0.6s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .subtitle {
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.95rem;
        margin-bottom: 0.8rem;
        margin-top: 0;
        font-weight: 400;
        letter-spacing: 0.3px;
    }
    
    /* Clean input fields - minimal spacing */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.85);
        color: #000000 !important;
        border: 1.5px solid rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 10px 14px;
        font-size: 0.95rem;
        font-weight: 400;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }

    .stTextInput > div > div > input:focus {
        background: #ffffff;
        border-color: rgba(8, 145, 178, 0.6);
        box-shadow: 0 0 0 3px rgba(8, 145, 178, 0.15);
        outline: none;
    }

    .stTextInput > div > div > input::placeholder {
        color: rgba(0, 0, 0, 0.45);
        font-weight: 300;
    }
    
    /* Solid color button - peacock blue */
    .stButton > button {
        background: #0891b2;
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 10px 24px;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
        margin-top: 0.8rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px 0 rgba(8, 145, 178, 0.35);
        letter-spacing: 0.3px;
        font-family: 'Inter', sans-serif;
    }
    
    .stButton > button:hover {
        background: #0e7490;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(8, 145, 178, 0.45);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }
    
    /* Link buttons - clean text links */
    .stButton[key="create_link"] > button, .stButton[key="help_link"] > button {
        background: transparent !important;
        border: none !important;
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: 0.9rem !important;
        padding: 6px 0 !important;
        box-shadow: none !important;
        text-decoration: none; 
        margin-top: 0.4rem;
        font-weight: 500;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }
    
    .stButton[key="create_link"] > button:hover, .stButton[key="help_link"] > button:hover {
        color: #ffffff !important;
        transform: none !important;
    }

    /* Divider */
    [data-testid="stHorizontalBlock"] > div > div:nth-child(2) > p {
        color: rgba(255, 255, 255, 0.25) !important;
        text-align: center; 
        margin-top: 0.4rem !important;
        font-size: 1rem;
    }
    
    /* Alert styling - minimal spacing */
    .stAlert {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #ffffff;
        margin-top: 0.4rem;
        margin-bottom: 0.4rem;
        padding: 0.6rem;
    }
    
    /* Input label visibility fix */
    .stTextInput label {
        visibility: hidden;
        height: 0;
        margin: 0;
        padding: 0;
    }

    /* Target the column that contains all form elements */
    div[data-testid="column"]:has(.form-wrapper) {
        position: relative;
        width: 100%;
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Create background using ::before pseudo-element */
    div[data-testid="column"]:has(.form-wrapper)::before {
        content: '';
        position: absolute;
        top: -10px;
        left: -20px;
        right: -20px;
        bottom: -10px;
        background: linear-gradient(
            145deg,
            rgba(255, 255, 255, 0.50) 0%,
            rgba(255, 255, 255, 0.35) 35%,
            rgba(8, 145, 178, 0.10) 65%,
            rgba(255, 255, 255, 0.30) 100%
        );
        backdrop-filter: blur(40px) saturate(150%) contrast(120%);
        -webkit-backdrop-filter: blur(40px) saturate(150%) contrast(120%);
        border-radius: 22px;
        box-shadow:
            0 25px 80px rgba(0, 0, 0, 0.1),
            inset 0 2px 1px rgba(255, 255, 255, 0.7),
            inset 0 -1px 1px rgba(255, 255, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.6);
        z-index: 0;
        pointer-events: none;
    }

    /* Ensure form elements are above the background */
    div[data-testid="column"]:has(.form-wrapper) > div {
        position: relative;
        z-index: 1;
    }

    /* Remove the form-wrapper styles since we're using ::before */
    .form-wrapper {
        display: contents;
    }

    /* Minimal spacing between inputs */
    .stTextInput {
        margin-bottom: 0.5rem;
    }
    
    /* First input spacing */
    .stTextInput:first-of-type {
        margin-top: 0rem;
    }

    /* Reduce button top margin */
    .stButton > button {
        margin-top: 0.6rem;
    }
    
    /* Links container spacing */
    [data-testid="stHorizontalBlock"] {
        margin-top: 0.6rem;
    }
</style>
""", unsafe_allow_html=True)

# Main container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Load and display logo
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
        
        if st.button(button_text, key="main_action_btn"):
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
                                time.sleep(1)
                                st.switch_page("pages/job.py")
                            else:
                                st.success(f"Welcome, {st.session_state.username}! Let's create your resume.")
                                time.sleep(1)
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
                            time.sleep(1)
                            st.switch_page("pages/main.py")
            else:
                st.warning("Please enter both email and password")

        col_link1, col_sep, col_link2 = st.columns([1, 0.1, 1])
        
        with col_link1:
            if st.button("Create Account" if st.session_state.mode == 'login' else "Back to Login", 
                        key="create_link", use_container_width=False):
                st.session_state.mode = 'register' if st.session_state.mode == 'login' else 'login'
                st.rerun()
        
        with col_sep:
            st.markdown('<p style="color: rgba(255, 255, 255, 0.25); text-align: center; margin-top: 0.4rem; font-size: 1rem;">|</p>', unsafe_allow_html=True)
        
        with col_link2:
            if st.button("Need Help?", key="help_link", use_container_width=False):
                st.info("Please contact support at support@ask.ai")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)