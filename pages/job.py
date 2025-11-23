import streamlit as st
import json
from utils import extract_text_from_pdf, extract_text_from_docx, extract_details_from_jd
from streamlit_extras.stylable_container import stylable_container


if 'logged_in_user' not in st.session_state or st.session_state.logged_in_user is None:
    logged_user = st.query_params.get("user")
    if logged_user:
        st.session_state.logged_in_user = logged_user
    else:
        st.warning("Please login first!")
        st.switch_page("app.py")
        
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Hide Streamlit elements */
    [data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarNav"] {display: none;}
    #MainMenu, footer, header {visibility: hidden;}

    :root {
        --primary-orange: #e87532;
        --primary-orange-hover: #d66428;
        --secondary-orange: #ff8c50;
        --danger-red: #ef4444;
        --bg-light: #ffffff;
        --bg-card: #f8fafc;
        --text-dark: #1e293b;
        --text-gray: #64748b;
        --border-gray: #e2e8f0;
    }

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Smooth page entrance */
    .stApp {
        background: #ffffff;
        min-height: 100vh;
        color: var(--text-dark);
        animation: fadeIn 0.5s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    .block-container {
        max-width: 900px;
        padding: 3rem 2rem;
        margin: 0 auto;
        padding-top: 100px !important;
        animation: slideUp 0.6s ease-out;
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Animated header with shimmer */
    .header-section {
        background: linear-gradient(135deg, var(--primary-orange) 0%, var(--secondary-orange) 100%);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(232, 117, 50, 0.2);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }

    .header-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent);
        animation: shimmer 3s infinite;
    }

    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }

    h2 {
        color: var(--text-dark) !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        text-align: center;
        margin: 1rem 0;
        animation: fadeInUp 0.8s ease-out;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Content container with light theme */
    .content-container {
        background: var(--bg-card);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        border: 1px solid var(--border-gray);
        transition: all 0.4s ease;
        animation: scaleIn 0.5s ease-out;
    }

    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    .content-container:hover {
        box-shadow: 0 8px 24px rgba(232, 117, 50, 0.15);
    }

    label, .stApp label {
        color: var(--text-dark) !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: color 0.3s ease;
    }


    /* File uploader with enhanced animation */
    .stFileUploader {
        background: var(--bg-card);
        border: 3px dashed rgba(232, 117, 50, 0.4);
        border-radius: 20px;
        padding: 3rem 2.5rem;
        transition: all 0.4s ease;
        position: relative;
    }

    .stFileUploader::before {
        content: '';
        position: absolute;
        top: -3px;
        left: -3px;
        right: -3px;
        bottom: -3px;
        background: linear-gradient(45deg, var(--primary-orange), transparent, var(--secondary-orange));
        border-radius: 20px;
        opacity: 0;
        transition: opacity 0.4s ease;
        z-index: -1;
    }

    .stFileUploader:hover {
        border-color: var(--primary-orange);
        transform: scale(1.01);
        box-shadow: 0 0 30px rgba(232, 117, 50, 0.2);
    }

    .stFileUploader:hover::before {
        opacity: 0.1;
    }

    .stFileUploader label {
        color: var(--text-dark) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }

    .stFileUploader section button {
        background: linear-gradient(135deg, var(--primary-orange), var(--secondary-orange)) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 1.4rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(232, 117, 50, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    .stFileUploader section button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(232, 117, 50, 0.4) !important;
    }

    /* Textarea with smooth focus */
    textarea, .stTextArea > div > div > textarea {
        background: #ffffff !important;
        border: 2px solid var(--border-gray) !important;
        border-radius: 12px !important;
        color: var(--text-dark) !important;
        padding: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    textarea:focus {
        background: #ffffff !important;
        border-color: var(--primary-orange) !important;
        box-shadow: 0 0 0 4px rgba(232, 117, 50, 0.1) !important;
        transform: translateY(-2px);
    }

    /* Success/Error messages with slide animation */
    .stSuccess, .stError, .stWarning {
        animation: slideInRight 0.5s ease-out;
        border-radius: 12px;
    }

    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    .stSuccess {
        background: rgba(16, 185, 129, 0.1) !important;
        border-left: 4px solid #10b981 !important;
    }

    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border-left: 4px solid var(--danger-red) !important;
    }

    .stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        border-left: 4px solid #f59e0b !important;
    }

    /* Radio buttons with smooth transition */
    .stRadio > div {
        color: var(--text-dark) !important;
    }

    .stRadio label {
        color: var(--text-dark) !important;
        transition: all 0.3s ease;
    }

    .stRadio > div > label:hover {
        transform: translateX(5px);
        color: var(--primary-orange) !important;
    }

    /* Enhanced scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-card);
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--primary-orange), var(--primary-orange-hover));
        border-radius: 6px;
        transition: background 0.3s ease;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, var(--secondary-orange), var(--primary-orange));
    }

    .nav-wrapper {
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
    }

    .logo {
        font-size: 24px;
        font-weight: 400;
        color: #2c3e50;
        font-family: 'Nunito Sans', sans-serif !important;
        letter-spacing: -0.5px;
    }

    .nav-menu {
        display: flex;
        gap: 2rem;
        align-items: center;
    }

    .nav-item { position: relative; }

    .nav-link {
        color: #000000 !important;
        text-decoration: none !important;
        font-size: 1rem;
        font-family: 'Nunito Sans', sans-serif;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .nav-link:visited {
        color: #000000 !important;
    }

    .nav-link:hover {
        background-color: #fff5f0;
        color: #e87532;
    }


    </style>
    """, unsafe_allow_html=True)


# ----------------------------------
# RESTORE USER FROM QUERY PARAMS FIRST (CRITICAL!)
# ----------------------------------




# Get current user for navigation
current_user = st.session_state.get('logged_in_user', '')

# Navigation bar with user param
st.markdown(f"""
<div class="nav-wrapper">
    <div class="logo">Resume Creator</div>
    <div class="nav-menu">
        <div class="nav-item">
            <a class="nav-link" href="?home=true&user={current_user}" target="_self">Home</a>
        </div>
        <div class="nav-item">
            <a class="nav-link" href="?create=true&user={current_user}" target="_self">Create New Resume</a>
        </div>
        <div class="nav-item">
            <a class="nav-link" href="?logout=true" target="_self">Logout</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Handle navigation
if st.query_params.get("create") == "true":
    if "create" in st.query_params:
        del st.query_params["create"]
    if st.session_state.logged_in_user:
        st.query_params["user"] = st.session_state.logged_in_user
    st.switch_page("pages/main.py")

if st.query_params.get("logout") == "true":
    st.session_state.logged_in_user = None
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.switch_page("app.py")

if st.query_params.get("home") == "true":
    if "home" in st.query_params:
        del st.query_params["home"]
    if st.session_state.logged_in_user:
        st.query_params["user"] = st.session_state.logged_in_user
    st.switch_page("app.py")

# [REST OF YOUR JOB.PY CODE HERE]


resume_data = st.session_state.get("resume_source", {})
input_method = st.session_state.get(
        "input_method", 
        resume_data.get("input_method", "Manual Entry")
    )
st.session_state["input_method"] = input_method

st.markdown('<h2>Target Job Description</h2>', unsafe_allow_html=True)

resume_source = st.session_state.get("resume_source", None)

if resume_source:
        st.markdown(f'<p>Your last resume was created. You can proceed with it, or click the navigation bar create new resume to start a new resume from scratch.</p>', unsafe_allow_html=True)

if resume_source is None:
        st.error("No resume data found. Please go back to the main page to upload or enter your data first .")
        # if st.button("Go to Resume Builder", key="go-to-main-btn"):
        #     st.switch_page("pages/main.py")
else:
        jd_method = st.radio(
            "Choose how to provide the job description:",
            ["Type or Paste", "Upload File"],
            horizontal=True,
            key="jd_method_radio"
        )
        
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
                
                if job_description:
                    st.text_area(
                        "Extracted Job Description Content (Review before processing)",
                        value=job_description,
                        height=200,
                        help="Preview of the extracted job description"
                    )
        else:
            job_description = st.text_area(
                "Paste the Job Description Text *",
                value="",
                height=250,
                placeholder="Paste the complete job description here..."
            )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            loading_placeholder = st.empty()

            with stylable_container(
                key="continue_button",
                css_styles="""
                    button {
                        background: linear-gradient(135deg, #e87532 0%, #ff8c50 100%) !important;
                        color: white !important;
                        border: none !important;
                        border-radius: 10px !important;
                        padding: 0.7rem 1.4rem !important;
                        font-weight: 600 !important;
                        font-size: 1rem !important;
                        box-shadow: 0 4px 12px rgba(232, 117, 50, 0.3) !important;
                        transition: all 0.3s ease !important;
                        width: 100% !important;
                    }
                    button:hover {
                        transform: translateY(-2px) !important;
                        box-shadow: 0 6px 16px rgba(232, 117, 50, 0.4) !important;
                        background: linear-gradient(135deg, #d66428 0%, #e87532 100%) !important;
                    }
                    button:active {
                        transform: translateY(0) !important;
                    }
                """
            ):
                if st.button("Continue to Resume Generation", key="jb-btn"):
                    if job_description:
                        loading_placeholder.markdown("""
                        <div id="overlay-loader">
                            <div class="loader-spinner"></div>
                            <p>Analyzing job description...</p>
                        </div>
                        <style>
                            #overlay-loader {
                                position: fixed;
                                top: 0;
                                left: 0;
                                width: 100vw;
                                height: 100vh;
                                background: rgba(15, 23, 42, 0.95);
                                backdrop-filter: blur(6px);
                                display: flex;
                                flex-direction: column;
                                justify-content: center;
                                align-items: center;
                                z-index: 9999;
                                color: white;
                                font-size: 1.2rem;
                                font-weight: 500;
                            }

                            .loader-spinner {
                                border: 5px solid rgba(96, 165, 250, 0.2);
                                border-top: 5px solid #3b82f6;
                                border-radius: 50%;
                                width: 70px;
                                height: 70px;
                                animation: spin 1s linear infinite;
                                margin-bottom: 20px;
                            }

                            @keyframes spin {
                                0% { transform: rotate(0deg); }
                                100% { transform: rotate(360deg); }
                            }

                            #overlay-loader p {
                                color: #e0f7ff;
                                font-size: 1.1rem;
                                letter-spacing: 0.5px;
                            }
                        </style>
                        """, unsafe_allow_html=True)

                        try:
                            structured_jd = extract_details_from_jd(job_description)
                            if isinstance(structured_jd, str):
                                try:
                                    structured_jd = json.loads(structured_jd)
                                except json.JSONDecodeError:
                                    structured_jd = {"raw_text": job_description}
                        except Exception as e:
                            st.error(f"Error processing JD: {e}")
                            structured_jd = {"raw_text": job_description}

                        st.session_state.job_description = structured_jd
                        loading_placeholder.empty()
                        st.switch_page("pages/create.py")
                    else:
                        st.error("Please provide a job description to continue")