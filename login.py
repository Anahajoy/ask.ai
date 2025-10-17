import streamlit as st
from pathlib import Path
import json
import re

# Page configuration
st.set_page_config(page_title="Loging Page", layout="wide", initial_sidebar_state="collapsed")
st.cache_data.clear()  # ✅ Clears Streamlit's memory cache
st.cache_resource.clear()  # ✅ Clears resource cache

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
    user_resume = all_data.get(email, None)
    
    # Debug print (remove after testing)
    print(f"Checking resume for {email}: {user_resume is not None}")
    
    # Check if resume exists and has actual data
    if user_resume and isinstance(user_resume, dict) and len(user_resume) > 0:
        return user_resume
    return None


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
            
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    button[kind="header"] {display: none;}
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Adjust main content to use full width */
    .main .block-container {
        max-width: 100%;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    
    /* Main container styling */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)),
                    url('https://cdn.pixabay.com/photo/2016/01/22/20/42/man-1156619_1280.jpg') center/cover;
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

    # Ensure name always exists (avoid NameError). Show input only for register mode.
    name = ""
    if st.session_state.mode == 'register':
        name = st.text_input("Full Name", placeholder="Full Name...", label_visibility="collapsed", key="full_name")

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
                    user_entry = users.get(email)
                    # support old-style (password string) and new-style (dict)
                    if isinstance(user_entry, dict):
                        stored_pw = user_entry.get("password")
                        stored_name = user_entry.get("name")
                    else:
                        stored_pw = user_entry
                        stored_name = None

                    if user_entry is None:
                        st.error("Invalid email or password")
                    elif stored_pw == password:
                        st.session_state.logged_in_user = email
                        # prefer stored name if available; fallback to email prefix
                        st.session_state.username = stored_name or email.split('@')[0]

                        # Load existing resume safely
                        user_resume = get_user_resume(email)
                        
                        # Debug info (remove after testing)
                        st.info(f"Debug: Resume data found: {user_resume is not None}")
                        
                        if user_resume and len(user_resume) > 0:
                            st.session_state.resume_source = user_resume
                            st.success(f"Welcome back, {st.session_state.username}! Loading your saved resume...")
                            # Add a small delay to see the message
                            import time
                            time.sleep(1)
                            st.switch_page("pages/job.py")
                        else:
                            st.success(f"Welcome, {st.session_state.username}! Let's create your resume.")
                            import time
                            time.sleep(1)
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
                    elif not name or len(name.strip()) == 0:
                        st.error("Please enter your full name")
                    else:
                        # Save new user with name included
                        users[email] = {"password": password, "name": name.strip()}
                        save_users(users)
                        st.session_state.logged_in_user = email
                        st.session_state.username = name.strip()
                        st.session_state.mode = 'login'
                        st.success(f"Account created successfully, {name.strip()}! Let's create your resume.")
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
