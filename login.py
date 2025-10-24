import streamlit as st
from pathlib import Path
import json
import re
import time 

# Page configuration
st.set_page_config(page_title="Login Page", layout="wide", initial_sidebar_state="collapsed")
# Clear caches to ensure new CSS and elements load correctly
st.cache_data.clear()
st.cache_resource.clear()

# Initialize session state
if 'mode' not in st.session_state:
    st.session_state.mode = 'login'  # 'login' or 'register'

users_file = Path(__file__).parent / "users.json"
user_data_file = "ask.ai/user_resume_data.json"

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

# Custom CSS for styling - SOPHISTICATED DARK MODE
st.markdown("""
<style>
    /* 1. Hide Streamlit default elements and remove padding/margins */
    #MainMenu, footer, header, button[kind="header"] {visibility: hidden;}
    [data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarNav"] {display: none;}
    
    /* Crucial: Prevent scrolling and set attractive dark background */
    .stApp {
        height: 100vh;
        overflow: hidden;
        /* Attractive Dark Background: Modern Abstract Texture with Dark Overlay */
        background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)),
                    url('https://images.unsplash.com/photo-1569470451072-68314f596aec?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1031') center/cover;
        background-attachment: fixed;
        color: #e0e0e0; /* Default text color: Light grey for dark mode */
    }
    
    /* Remove default Streamlit content padding */
    .main .block-container {
        padding: 0;
        margin: 0;
        max-width: 100vw;
    }
    
    /* 2. Center container for login form */
    .main-container {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        box-sizing: border-box;
    }
    
    /* Form Container Card - Semi-transparent, dark background for elegance */
    .stContainer {
        max-width: 400px;
        background-color: rgba(30, 30, 30, 0.85); /* Darker transparent background */
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); /* Stronger shadow for depth */
        border: 1px solid rgba(100, 100, 100, 0.3); /* Subtle light border */
        backdrop-filter: blur(5px);
    }

    /* Logo styling - Electric Blue gradient */
    .logo {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-align: center;
        /* Using background-clip for a vibrant gradient logo text */
        background: -webkit-linear-gradient(45deg, #00BFFF, #00FF7F); /* Electric Blue to Neon Green */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 10px rgba(0, 255, 127, 0.3); /* Subtle glow */
    }
    
    /* Input styling - Dark and sleek */
    .stTextInput > div > div > input {
        background-color: #222222; /* Very dark input background */
        color: #e0e0e0; 
        border: 1px solid #444444; /* Dark grey border */
        border-radius: 8px;
        padding: 12px 15px;
        font-size: 1rem;
        transition: border-color 0.3s;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00FF7F; /* Neon green focus border */
        box-shadow: 0 0 5px rgba(0, 255, 127, 0.5);
    }

    .stTextInput > div > div > input::placeholder {
        color: #888888;
    }
    
    /* Button styling - Electric Blue gradient for action */
    .stButton > button {
        background: linear-gradient(135deg, #00BFFF, #00FF7F); /* Vibrant Gradient */
        color: #00000; /* Dark text on light button for contrast */
        border: none;
        border-radius: 8px;
        padding: 12px 60px;
        font-size: 1.1rem;
        font-weight: 700;
        width: 100%;
        text-decoration: bold;
        margin-top: 1.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 255, 127, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 255, 127, 0.6);
    }
    
    /* Link buttons styling - Subtle white text on dark background */
    .stButton[key="create_link"] > button, .stButton[key="help_link"] > button {
        background: transparent !important;
        border: none !important;
        color: #00BFFF !important; /* Electric Blue link color */
        font-size: 0.95rem !important;
        padding: 0 !important;
        box-shadow: none !important;
        text-decoration: none; 
        margin-top: 0;
        font-weight: 400;
    }
    
    .stButton[key="create_link"] > button:hover, .stButton[key="help_link"] > button:hover {
        opacity: 0.8 !important;
        transform: none !important;
        text-decoration: underline;
    }

    /* Column separating line */
    [data-testid="stHorizontalBlock"] > div > div:nth-child(2) > p {
        color: #444444 !important; /* Darker separator */
        text-align: center; 
        margin-top: 0.25rem !important;
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
</style>
""", unsafe_allow_html=True)

# Wrap the main content in the custom container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Use st.container to group the form elements (this now acts as the transparent card)
# Note: st.container must be inside a column block if you want it centered horizontally using the columns trick
with st.container(border=False):
    col1, col2, col3 = st.columns([1, 2, 1]) 

    with col2:
        # Wrap the content in a single div to apply the custom card styling
        # st.markdown('<div class="stContainer">', unsafe_allow_html=True) 

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
                        
                        if isinstance(user_entry, dict):
                            stored_pw = user_entry.get("password")
                            stored_name = user_entry.get("name")
                        else:
                            stored_pw = user_entry
                            stored_name = None

                        if user_entry is None or stored_pw != password:
                            st.error("Invalid email or password")
                        else:
                            # Successful Login
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
        
        # ---------------- Links below button ----------------
        col_link1, col_sep, col_link2 = st.columns([1, 0.1, 1])
        
        with col_link1:
            if st.button("CREATE ACCOUNT" if st.session_state.mode == 'login' else "BACK TO LOGIN", 
                        key="create_link", use_container_width=False):
                st.session_state.mode = 'register' if st.session_state.mode == 'login' else 'login'
                st.rerun()
        
        with col_sep:
            # Use raw markdown text for the separator
            st.markdown('<p style="color: #444444; text-align: center; margin-top: 0.25rem;">|</p>', unsafe_allow_html=True)
        
        with col_link2:
            if st.button("NEED HELP?", key="help_link", use_container_width=False):
                st.info("Please contact support at support@ask.ai")

        # Close the custom card div
        st.markdown('</div>', unsafe_allow_html=True)

# Close the main-container div
st.markdown('</div>', unsafe_allow_html=True)

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