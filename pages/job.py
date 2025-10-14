import streamlit as st
import json
from utils import extract_text_from_pdf, extract_text_from_docx, extract_details_from_jd

# Define the new blue colors
NEW_BLUE = "#1E90FF"  # Dodger Blue
NEW_CYAN = "#00CED1"  # Dark Cyan
NEW_BLUE_SHADOW = "rgba(30, 144, 255, 0.4)" # Shadow for the blue accent

# --- Custom CSS for Black/White/Grey Theme (FIXED FOR ALL TEXT READABILITY) ---
st.markdown(f"""
<style>
    
    [data-testid="stSidebar"] {{display: none;}}
    [data-testid="collapsedControl"] {{display: none;}}
    button[kind="header"] {{display: none;}}
    [data-testid="stSidebarNav"] {{display: none;}}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Import Google Fonts - Inter is used for the entire app */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Color Palette Variables (Cohesive with main.py) */
    :root {{
        --primary-dark: #1a1a1a;
        --secondary-light: #ffffff;
        --accent-color: {NEW_BLUE}; /* CHANGED: New Blue Accent */
        --text-dark: #1a1a1a;
        --text-light: #FFFFFF;
        --card-bg-light: #ffffff;
        --card-shadow: 0 10px 40px rgba(0,0,0,0.08);
        --card-border: 1px solid rgba(0,0,0,0.06);
    }}

    /* Global Styles */
    * {{
        font-family: 'Inter', sans-serif;
    }}

    /* Main App Background & Default Text Color (FIXED) */
    .stApp {{
        /* UPDATED BACKGROUND URL and gradient for darker effect */
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.9)),
                        url('https://images.unsplash.com/photo-1702835124686-fd1faac06b8d?ixlib=rb-4.1.0&auto=format&fit=crop&q=80&w=870') center/cover;
        background-attachment: fixed;
        min-height: 100vh;
        color: var(--text-light); /* IMPORTANT: Sets default text to white */
    }}
    
    /* Streamlit Widget Labels (FIXED - Ensures all labels outside cards are white) */
    .stApp label {{
        color: var(--text-light);
        font-weight: 600;
    }}

    /* Centralizing Content */
    .block-container {{
        max-width: 900px;
        padding: 2rem 3rem;
        margin: 0 auto;
    }}

    
    /* Header section - Dark/Glassmorphism to stand out */
    .header-section {{
        background: rgba(0, 0, 0, 0.6); /* Dark Glassmorphism */
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }}
    
    .header-section::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, {NEW_BLUE}, {NEW_CYAN}, {NEW_BLUE}); 
        opacity: 0.8;
    }}
    
    /* Title styling */
    h2 {{
        color: var(--text-light) !important;
        font-weight: 800 !important;
        margin: 0 !important;
        font-size: 2.2rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 1rem !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }}
    
    /* Step number badge - Using Accent Color */
    .step-badge {{
        display: inline-block;
        background: linear-gradient(135deg, {NEW_BLUE} 0%, {NEW_CYAN} 100%);
        color: white;
        width: 45px;
        height: 45px;
        border-radius: 14px;
        text-align: center;
        line-height: 45px;
        font-weight: 700;
        font-size: 1.2rem;
        box-shadow: 
            0 4px 15px {NEW_BLUE_SHADOW};
        border: 2px solid white;
    }}
    
    /* Alert box for returning users - Dark Glassmorphism */
    .returning-user-alert {{
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(10px);
        border: 2px solid var(--accent-color);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 16px {NEW_BLUE_SHADOW};
    }}
    
    .returning-user-alert h3 {{
        color: var(--text-light) !important;
        margin-top: 0 !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }}
    
    .returning-user-alert p {{
        color: #FFFFFF;
        margin: 0.5rem 0 1rem 0;
        font-size: 1rem;
        line-height: 1.6;
    }}
    
    /* Add New Resume button styling - Accent Dark */
    .stButton > button[key="add-new-resume-btn"] {{
        background: linear-gradient(135deg, var(--accent-color) 0%, {NEW_CYAN} 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px {NEW_BLUE_SHADOW} !important;
        width: auto !important;
        min-width: 250px !important;
        /* FIX 1: Ensure the outer button has white text */
        color: white !important; 
    }}

    /* FIX 2: Target the internal span for maximum text visibility override */
    .stButton > button[key="add-new-resume-btn"] > div > p {{
        color: white !important; 
        font-weight: 600 !important;
    }}
    
    .stButton > button[key="add-new-resume-btn"]:hover {{
        background: linear-gradient(135deg, {NEW_CYAN} 0%, var(--accent-color) 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px {NEW_BLUE_SHADOW} !important;
    }}
    
    /* Button for 'Go to Resume Builder' (appears when no data is found) */
    .stButton > button[key="go-to-main-btn"] {{
        /* This button appears outside the white content container, on the dark background. 
           It should be styled like a bright accent button to be visible. */
        background: var(--accent-color) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }}
    
    .stButton > button[key="go-to-main-btn"] > div > p {{
        color: white !important;
        font-weight: 600 !important;
    }}

    /* Content container - White card for form elements (No change needed) */
    .content-container {{
        background: var(--card-bg-light);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: var(--card-shadow);
        border: var(--card-border);
    }}

    /* FIX: Ensure default button text inside the white container is visible (dark)
       (This primarily targets default, non-styled buttons within the white container. 
       The jb-btn rule below overrides this for the dark submit button.) */
    .content-container .stButton > button {{
        color: var(--text-dark) !important; 
        font-weight: 600 !important;
    }}

    
    /* Radio buttons *label* inside the content container (No change needed) */
    .content-container .stRadio > label {{
        font-weight: 600 !important;
        color: var(--text-dark) !important;
        font-size: 1rem !important;
        margin-bottom: 1rem !important;
    }}

    /* Text Area/Input Labels inside the content container (No change needed) */
    .content-container .stTextArea > label,
    .content-container .stFileUploader > label {{
        color: var(--text-dark) !important;
    }}
    
    .stRadio > div {{
        background: #f8f9fa;
        padding: 1.2rem;
        border-radius: 16px;
        gap: 1.5rem;
        border: 1px solid rgba(0,0,0,0.08);
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.04);
    }}
    
    .stRadio > div > label {{
        background: #f0f0f0 !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        border-radius: 12px !important;
        padding: 0.9rem 1.8rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
        font-weight: 500 !important;
        color: var(--text-dark) !important;
    }}
    
    /* Checked radio button uses the primary dark color for contrast (No change needed) */
    .stRadio > div > label[data-checked="true"] {{
        background: var(--primary-dark) !important;
        border-color: var(--primary-dark) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }}

    .stRadio > div > label:hover {{
        background: #ffffff !important;
        border-color: rgba(0,0,0,0.15) !important;
        transform: translateY(-2px) !important;
    }}
    
    /* File uploader - Dark dashed border for focus (No change needed) */
    .stFileUploader {{
        background: #ffffff !important;
        border: 2px dashed rgba(0,0,0,0.2) !important;
        border-radius: 16px !important;
        padding: 2.5rem !important;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.04) !important;
        transition: all 0.3s ease !important;
        margin-top: 1rem !important;
    }}
    
    .stFileUploader:hover {{
        border-color: var(--primary-dark) !important;
        background: #f8f9fa !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
    }}
    
    .stFileUploader label {{
        color: #666666 !important;
        font-weight: 500 !important;
    }}
    
    /* Text area - Clean and readable */
    .stTextArea > label {{
        font-weight: 600 !important;
        color: var(--text-dark) !important;
        font-size: 1rem !important;
        margin-bottom: 0.8rem !important;
    }}
    
    .stTextArea > div > div > textarea {{
        background: #f5f5f5 !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        border-radius: 12px !important;
        color: var(--text-dark) !important;
        padding: 1rem !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.04) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    
    .stTextArea > div > div > textarea:focus {{
        border-color: var(--accent-color) !important;
        background: #ffffff !important;
        box-shadow: 
            0 0 0 3px rgba(30, 144, 255, 0.2),
            inset 0 2px 4px rgba(0,0,0,0.02) !important;
        transform: translateY(-1px) !important;
    }}
    
    /* Submit button - Dark/Accent Hero Style */
    .stButton > button[key="jb-btn"] {{
        background: linear-gradient(135deg, var(--primary-dark) 0%, #333333 100%) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 14px !important;
        padding: 1.1rem 3rem !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        width: 100% !important;
        margin-top: 2rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 
            0 8px 30px rgba(0,0,0,0.3),
            inset 0 1px 0 rgba(255,255,255,0.15) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        /* FIX 3: Ensure the outer button has white text */
        color: white !important; 
    }}

    /* FIX 4: Target the internal span for maximum text visibility override */
    .stButton > button[key="jb-btn"] > div > p {{
        color: white !important; 
        font-weight: 700 !important;
    }}
    
    .stButton > button[key="jb-btn"]:hover {{
        background: linear-gradient(135deg, var(--accent-color) 0%, {NEW_CYAN} 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 
            0 12px 40px {NEW_BLUE_SHADOW},
            inset 0 1px 0 rgba(255,255,255,0.2) !important;
    }}
    
    /* Success/Error/Warning messages (No change needed for success/error) */
    .stSuccess {{
        background: #f0fdf4 !important;
        border: 1px solid #86efac !important;
        border-radius: 12px !important;
        color: #166534 !important;
        padding: 1rem !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 12px rgba(134, 239, 172, 0.2) !important;
    }}
    
    .stError {{
        background: #fef2f2 !important;
        border: 1px solid #fca5a5 !important;
        border-radius: 12px !important;
        color: #991b1b !important;
        padding: 1rem !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 12px rgba(252, 165, 165, 0.2) !important;
    }}

    /* Streamlit Warning box color (FIXED - so the text isn't black on black) */
    .stWarning {{
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid var(--accent-color) !important;
        border-radius: 12px !important;
        color: var(--text-light) !important; /* White text on dark warning box */
        font-weight: 500 !important;
    }}
    
    /* Spinner */
    .stSpinner > div {{
        border-color: var(--accent-color) transparent transparent transparent !important;
    }}
    
    /* Helper text (No change needed) */
    .help-text {{
        color: #666666;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        font-style: italic;
    }}
    
    /* Section divider (No change needed) */
    .section-divider {{
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0,0,0,0.15), transparent);
        margin: 2rem 0;
    }}
</style>
""", unsafe_allow_html=True)


# Check if user is logged in
if 'logged_in_user' not in st.session_state:
    st.warning("Please login first!")
    st.switch_page("login.py")

# Get resume data from session state
resume_data = st.session_state.get("resume_source", {})
input_method = resume_data.get("input_method", "Manual Entry") 
st.session_state["input_method"] = input_method


# --- Header Section ---
st.markdown('<div class="header-section">', unsafe_allow_html=True)
st.markdown('<h2><span class="step-badge">2</span>Target Job Description</h2>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# --- Returning User Alert ---
resume_source = st.session_state.get("resume_source", None)

if resume_source:
    # Show alert for users with existing resume data
    st.markdown('<div class="returning-user-alert">', unsafe_allow_html=True)
    st.markdown('<h3>👋 Resume Found!</h3>', unsafe_allow_html=True)
    
    # Display method used to create resume
    method_display = "from your Uploaded File" if st.session_state.get("input_method") == "Upload" else "by Manual Entry"

    st.markdown(f'<p>Your last resume was created **{method_display}**. You can proceed with it, or click the button below to start a new resume from scratch.</p>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns([1, 4])
    # Button is placed inside a column for better layout control
    with col_a: 
        if st.button("Start New Resume", key="add-new-resume-btn"):
            # Clear all resume-related session state
            keys_to_delete = ['resume_source', 'enhanced_resume', 'job_description', 
                             'resume_processed', 'exp_indices', 'edu_indices', 'cert_indices', 'project_indices']
            
            for key in keys_to_delete:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Redirect to the main resume building page
            st.switch_page("main.py") # Use main.py since it's the home page
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Job Description Input ---
if resume_source is None:
    # This text should now be white due to the .stApp color rule
    st.error("No resume data found. Please go back to the main page to upload or enter your data first.")
    if st.button("Go to Resume Builder", key="go-to-main-btn"):
        st.switch_page("main.py")
else:
    # Main content
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    
    # Job description input method
    # The label for this radio button will now be dark because it is inside the .content-container,
    # and the specific .content-container label rule overrides the general .stApp rule for good contrast.
    jd_method = st.radio(
        "Choose how to provide the job description:",
        ["Type or Paste", "Upload File"],
        horizontal=True,
        key="jd_method_radio"
    )
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    job_description = ""

    if jd_method == "Upload File":
        jd_file = st.file_uploader(
            "Upload Job Description",
            type=["pdf", "docx"],
            key="jd_upload",
            help="Upload a PDF or DOCX file containing the job description"
        )
        if jd_file:
            with st.spinner("Reading job description..."):
                if jd_file.type == "application/pdf":
                    job_description = extract_text_from_pdf(jd_file)
                else:
                    job_description = extract_text_from_docx(jd_file)
                st.success("Job description uploaded successfully!")
            
            # Show extracted text
            if job_description:
                st.text_area(
                    "Extracted Job Description Content (Review before processing)",
                    value=job_description,
                    height=200,
                    help="Preview of the extracted job description"
                )

    else:  # Type or Paste
        job_description = st.text_area(
            "Paste the Job Description Text *",
            value="",
            height=250,
            placeholder="Paste the complete job description here...\n\nExample:\nWe are looking for a Senior Software Engineer with 5+ years of experience...",
            help="The AI will analyze this job description and tailor your resume accordingly"
        )
        
        if job_description:
            word_count = len(job_description.split())
            st.markdown(f'<p class="help-text">Word count: {word_count}</p>', unsafe_allow_html=True)

    # Submit button in centered column
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Continue to Resume Generation ➡️", key="jb-btn"):
            if job_description:
                with st.spinner("Analyzing job description and preparing for tailoring..."):
                    structured_jd = extract_details_from_jd(job_description)
                    
                    # Handle JSON parsing
                    if isinstance(structured_jd, str):
                        try:
                            structured_jd = json.loads(structured_jd)
                        except json.JSONDecodeError:
                            # If LLM returns non-JSON or fails, save the raw text
                            structured_jd = {"raw_text": job_description}
                    
                    st.session_state.job_description = structured_jd
                
                st.success("Job description processed successfully!")
                st.switch_page("pages/create.py")
            else:
                st.error("Please provide a job description to continue")
    
    st.markdown('</div>', unsafe_allow_html=True)