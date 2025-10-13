import streamlit as st
from pathlib import Path
import json
import re

# Page configuration
st.set_page_config(page_title="Landing Page", layout="wide")

# Initialize session state
if 'mode' not in st.session_state:
    st.session_state.mode = 'login'  # 'login' or 'register'

users_file = Path(__file__).parent / "users.json"
user_data_file = Path(__file__).parent / "user_resume_data.json"

def load_users():
    try:
        if users_file.exists():
            with open(users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"Error loading users: {e}")
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
        st.error(f"Error loading user data: {e}")
        return {}

def get_user_resume(email):
    """Get resume data for a specific user"""
    all_data = load_user_resume_data()
    return all_data.get(email, None)

def save_user_resume(email, resume_data):
    """Save or update a user's resume without affecting other users"""
    all_data = load_user_resume_data()  # load existing data
    all_data[email] = resume_data       # update only this user
    try:
        with open(user_data_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving resume data: {e}")

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Custom CSS for styling
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)),
                    url('https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?q=80&w=465&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D') center/cover;
        background-attachment: fixed;
    }
    
    /* Center container */
    .main-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 2rem;
    }
    
    /* Logo styling */
    .logo {
        font-size: 4rem;
        color: white;
        font-weight: bold;
        margin-bottom: 3rem;
        text-align: center;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.2);
        color: black;
        border: none;
        border-radius: 25px;
        padding: 15px 20px;
        font-size: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(0, 0, 0, 0.8);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #ff7b54, #ff6b3d);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 15px 60px;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
        margin-top: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(255, 107, 61, 0.3);
    }
    
    /* Links styling */
    .links-container {
        display: flex;
        gap: 2rem;
        margin-top: 2rem;
        justify-content: center;
    }
    
    .link-text {
        color: white;
        text-decoration: none;
        font-size: 0.95rem;
        cursor: pointer;
        transition: opacity 0.3s;
    }
    
    .link-text:hover {
        opacity: 0.8;
    }
    
    /* Footer styling */
    .footer-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        display: flex;
        justify-content: space-between;
        padding: 2rem 3rem;
        color: white;
        font-size: 0.9rem;
    }
    
    .footer-links {
        display: flex;
        gap: 2rem;
    }
    
    /* Hide default streamlit padding */
    .block-container {
        padding: 0;
        max-width: 100%;
    }
    
    /* Style the link buttons to look like text links */
    button[kind="secondary"] {
        background: transparent !important;
        border: none !important;
        color: white !important;
        font-size: 0.95rem !important;
        padding: 0 !important;
        box-shadow: none !important;
        text-decoration: none !important;
    }
    
    button[kind="secondary"]:hover {
        opacity: 0.8 !important;
        transform: none !important;
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)


col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Logo
    st.markdown('<div class="logo">ASK.AI</div>', unsafe_allow_html=True)

    # Email / Password input
    email = st.text_input("Email", placeholder="Email...", label_visibility="collapsed", key="email")
    password = st.text_input("Password", placeholder="Password...", type="password", label_visibility="collapsed", key="password")
    
    # Dynamic button text
    button_text = "Create Account" if st.session_state.mode == 'register' else "Get Started"
    
    if st.button(button_text, key="main_action_btn"):
        if email and password:
            if not is_valid_email(email):
                st.error("Please enter a valid email address")
            else:
                users = load_users()
                
                if st.session_state.mode == 'login':
                    # ---------------- LOGIN MODE ----------------
                    if email in users and users[email] == password:
                        st.session_state.logged_in_user = email
                        st.session_state.username = email.split('@')[0]

                        # Load existing resume safely
                        user_resume = get_user_resume(email)
                        if user_resume:
                            st.session_state.resume_source = user_resume
                            st.session_state.is_returning_user = True
                            st.success(f"Welcome back, {email}!")
                            st.switch_page("pages/job.py")
                        else:
                            st.session_state.is_returning_user = False
                            st.success(f"Welcome back, {email}! Let's create your resume.")
                            st.switch_page("pages/main.py")
                    else:
                        st.error("Invalid email or password")
                
                else:
                    # ---------------- REGISTER MODE ----------------
                    if email in users:
                        st.error("Email already registered. Please login.")
                        st.session_state.mode = 'login'
                        st.rerun()
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters long")
                    else:
                        # Save new user
                        users[email] = password
                        save_users(users)
                        st.session_state.logged_in_user = email
                        st.session_state.username = email.split('@')[0]
                        st.session_state.mode = 'login'
                        st.session_state.is_returning_user = False
                        st.success("Account created successfully! Logging you in...")
                        st.switch_page("pages/main.py")
        else:
            st.warning("Please enter both email and password")
    
    # ---------------- Links below button ----------------
    col_link1, col_sep, col_link2 = st.columns([1, 0.1, 1])
    
    with col_link1:
        if st.button("CREATE ACCOUNT" if st.session_state.mode == 'login' else "BACK TO LOGIN", 
                     key="create_link", use_container_width=True):
            st.session_state.mode = 'register' if st.session_state.mode == 'login' else 'login'
            st.rerun()
    
    with col_sep:
        st.markdown('<p style="color: rgba(255,255,255,0.5); text-align: center; margin-top: 0.5rem;">|</p>', unsafe_allow_html=True)
    
    with col_link2:
        if st.button("NEED HELP?", key="help_link", use_container_width=True):
            st.info("Please contact support at support@ask.ai")

# ---------------- Footer ----------------
st.markdown("""
<div class="footer-container">
    <div class="footer-links">
        <span class="link-text">CREATIVE TIM</span>
        <span class="link-text">ABOUT US</span>
        <span class="link-text">BLOG</span>
    </div>
    <div>
        <span style="opacity: 0.8;">Made with <span style="color: #ff6b3d;">Now AI Resume</span> by Anaha Joy</span>
    </div>
</div>
""", unsafe_allow_html=True)