import streamlit as st
import json
from utils import extract_text_from_pdf, extract_text_from_docx, extract_details_from_jd

# Define the new blue colors
NEW_BLUE = "#1E90FF"  # Dodger Blue
NEW_CYAN = "#00CED1"  # Dark Cyan
NEW_BLUE_SHADOW = "rgba(30, 144, 255, 0.4)" # Shadow for the blue accent

# --- Custom CSS for Black/White/Grey Theme (FIXED FOR ALL TEXT READABILITY) ---
# --- ❄️ Winter Theme UI (New Look, Same Logic) ---
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    #MainMenu, footer, header {visibility: hidden;}

    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    /* Color Palette Variables - Winter Theme */
    :root {
        --primary-color: #1a2332; /* Deep Navy Blue */
        --secondary-color: #e8f4f8; /* Icy White/Light Blue */
        --accent-color: #4a9eff; /* Cool Sky Blue */
        --accent-light: #7bb8ff;
        --accent-ice: #b4e0ff; /* Pale Ice Blue */
        --text-dark: #1a2332;
        --text-light: #ffffff;
        --card-bg: rgba(74, 158, 255, 0.12); /* Frosted Glass */
        --card-border: rgba(180, 224, 255, 0.3);
        --silver: #c5d9e8; /* Silver-Blue accent */
    }

    * {
        font-family: 'Poppins', sans-serif;
    }

    /* App Background - Winter Glacier Scene */
    .stApp {
        background: linear-gradient(135deg, rgba(26,35,50,0.98), rgba(31,56,90,0.95)),
                    url('https://images.unsplash.com/photo-1600132806370-125d63f4f9d3?auto=format&fit=crop&w=1200&q=80') center/cover no-repeat;
        background-attachment: fixed;
        min-height: 100vh;
        color: var(--text-light);
    }

    .block-container {
        max-width: 900px;
        padding: 2rem 3rem;
        margin: 0 auto;
    }

    /* Frosted Header Section */
    .header-section {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(18px);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        border: 1px solid var(--card-border);
        box-shadow: 0 8px 25px rgba(74, 158, 255, 0.2);
        position: relative;
    }

    .header-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-color), var(--accent-light), var(--accent-ice));
        border-radius: 5px;
    }

    h2 {
        color: var(--text-light) !important;
        font-weight: 700 !important;
        font-size: 2.2rem !important;
        display: flex;
        align-items: center;
        gap: 1rem;
        text-shadow: 0 0 12px rgba(74,158,255,0.5);
    }

    .step-badge {
        background: linear-gradient(135deg, var(--accent-color), var(--accent-light));
        color: white;
        width: 45px;
        height: 45px;
        border-radius: 14px;
        text-align: center;
        line-height: 45px;
        font-weight: 700;
        font-size: 1.2rem;
        box-shadow: 0 4px 20px rgba(74,158,255,0.4);
        border: 2px solid var(--silver);
    }

    /* Returning User Frosted Box */
    .returning-user-alert {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--card-border);
        border-radius: 18px;
        padding: 1.8rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 30px rgba(74,158,255,0.15);
    }

    .returning-user-alert h3 {
        color: var(--accent-ice);
        font-size: 1.4rem !important;
        margin-bottom: 0.5rem;
    }

    .returning-user-alert p {
        color: var(--secondary-color);
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Frosted Content Card */
    .content-container {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(25px);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 6px 25px rgba(0,0,0,0.25);
        border: 1px solid var(--card-border);
    }

    /* Label and Text Color Adjustments */
    label, .stApp label {
        color: var(--text-light);
        font-weight: 600;
    }

   
/* Generic fallback for any Streamlit-rendered button */
.stApp .stButton > button,
.stApp button[class*="stButton"],
.stApp div.stButton button {
    background: linear-gradient(135deg, var(--accent-color), var(--accent-light)) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 6px 18px rgba(74,158,255,0.28) !important;
    padding: 0.9rem 1.6rem !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    min-width: 140px !important;
    text-transform: none !important;
}

/* Make sure the internal span/p that holds the text is white too */
.stApp .stButton > button > div > p,
.stApp .stButton > button > span,
.stApp button > div > p {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* Specific keyed buttons (your keys) — explicit overrides */
.stApp .stButton > button[key="jb-btn"],
.stApp button[key="jb-btn"] {
    background: linear-gradient(135deg, var(--accent-color), var(--accent-light)) !important;
    color: #ffffff !important;
    width: 100% !important;           /* keep your full-width CTA */
    padding: 1rem 2rem !important;
}

/* smaller/secondary buttons */
.stApp .stButton > button[key="add-new-resume-btn"],
.stApp button[key="add-new-resume-btn"],
.stApp .stButton > button[key="go-to-main-btn"],
.stApp button[key="go-to-main-btn"] {
    background: var(--accent-ice) !important;
    color: var(--text-dark) !important;
    box-shadow: 0 4px 12px rgba(180,224,255,0.25) !important;
}

/* Hover states (ensure hover reflects primary accent) */
.stApp .stButton > button:hover,
.stApp button:hover {
    transform: translateY(-2px) !important;
    filter: brightness(1.03) !important;
}

/* Defensive rule: remove any Streamlit inline red text backgrounds */
.stApp .stButton > button[style*="background"] {
    background-image: none !important;
    background-color: unset !important;
    color: inherit !important;
}

/* If a button still shows red text because of an error class, override it */
.stApp .stButton > button:where([class*="error"], .css-1y4p8pa) {
    color: #ffffff !important;
    background: linear-gradient(135deg, var(--accent-color), var(--accent-light)) !important;
}


    /* Text Areas & Uploaders */
    textarea, .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 12px !important;
        color: var(--text-light) !important;
        padding: 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease-in-out;
    }

    textarea:focus {
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 0 3px rgba(74,158,255,0.3);
        background: rgba(255, 255, 255, 0.25) !important;
    }

    .stFileUploader {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 2px dashed var(--card-border) !important;
        border-radius: 14px !important;
        padding: 2.5rem !important;
        transition: 0.3s ease-in-out;
    }

    .stFileUploader:hover {
        border-color: var(--accent-color) !important;
        background: rgba(255, 255, 255, 0.15) !important;
    }

    /* Section Divider */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-color), transparent);
        margin: 2rem 0;
    }

    /* Success/Error Messages */
    .stSuccess, .stError {
        border-radius: 12px !important;
        padding: 1rem 1.2rem !important;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(255,255,255,0.1);
    }

    .stSuccess {
        background: rgba(180,255,200,0.1) !important;
        border: 1px solid rgba(180,255,200,0.3) !important;
        color: #aef9c0 !important;
    }

    .stError {
        background: rgba(255,120,120,0.1) !important;
        border: 1px solid rgba(255,120,120,0.3) !important;
        color: #ffb0b0 !important;
    }
    

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
            st.switch_page("../ask.ai/pages/main.py") # Use main.py since it's the home page
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Job Description Input ---
if resume_source is None:
    # This text should now be white due to the .stApp color rule
    st.error("No resume data found. Please go back to the main page to upload or enter your data first.")
    if st.button("Go to Resume Builder", key="go-to-main-btn"):
        st.switch_page("../ask.ai/pages/main.py")
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