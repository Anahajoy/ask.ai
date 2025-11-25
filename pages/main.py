import streamlit as st
from pathlib import Path
import json
import time

from utils import (
    is_valid_email,
    is_valid_phone,
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_details_from_text,
    get_all_skills_from_llm,
    save_user_resume,
    load_skills_from_json
)

from streamlit_extras.stylable_container import stylable_container

if 'logged_in_user' not in st.session_state or st.session_state.logged_in_user is None:
    logged_user = st.query_params.get("user")
    if logged_user:
        st.session_state.logged_in_user = logged_user
    else:
        st.warning("Please login first!")
        st.switch_page("app.py")


if st.session_state.logged_in_user:
    st.query_params["user"] = st.session_state.logged_in_user

current_user = st.session_state.get('logged_in_user', '')


if "exp_indices" not in st.session_state:
    st.session_state.exp_indices = [0]
if "edu_indices" not in st.session_state:
    st.session_state.edu_indices = [0]
if "cert_indices" not in st.session_state:
    st.session_state.cert_indices = [0]
if "project_indices" not in st.session_state:
    st.session_state.project_indices = [0]

if "saved_personal_info" not in st.session_state:
    st.session_state.saved_personal_info = {}
if "saved_experiences" not in st.session_state:
    st.session_state.saved_experiences = {}
if "saved_education" not in st.session_state:
    st.session_state.saved_education = {}
if "saved_certificates" not in st.session_state:
    st.session_state.saved_certificates = {}
if "saved_projects" not in st.session_state:
    st.session_state.saved_projects = {}

if "custom_indices" not in st.session_state:
    st.session_state.custom_indices = [0]
if "saved_custom_sections" not in st.session_state:
    st.session_state.saved_custom_sections = {}

# ============================
# COMMON BUTTON STYLE
# ============================
BUTTON_STYLE = """
    button {
        background-color: #ffffff !important;
        color: #e87532 !important;
        padding: 12px 28px !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        border: 2px solid #e87532 !important;
    }
    button:hover {
        background-color:#e87532 !important;
        color: #ffffff !important;
    }
"""

SAVE_STYLE = """
    button {
        background-color: #93C47D !important;
        color: #FFFFFF !important;
        padding: 12px 2px !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        border: 2px solid #93C47D !important;
    }
    button:hover {
        background-color:#FFFFFF !important;
        color: #93C47D !important;
    }
"""
REMOVE_STYLE = """
    button {
        background-color: #FF6A4C !important;
        color: #FFFFFF !important;
        padding: 12px 28px !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        border: 2px solid #FF6A4C !important;
    }
    button:hover {
        background-color:#FFFFFF !important;
        color: #FF6A4C !important;
    }
"""

ADD_STYLE = """
    button {
        background-color: #9FC0DE !important;
        color: #FFFFFF !important;
        padding: 12px 28px !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        border: 2px solid #9FC0DE !important;
    }
    button:hover {
        background-color:#FFFFFF !important;
        color: #9FC0DE !important;
    }
"""

PRIMARY_LARGE_BUTTON_STYLE = """
    button {
        background-color: #e87532 !important;
        color: #ffffff !important;
        padding: 14px 40px !important;
        border-radius: 50px !important;
        font-weight: 700 !important;
        border: 2px solid #e87532 !important;
        font-size: 1rem !important;
    }
    button:hover {
        background-color:#ffffff !important;
        color: #e87532 !important;
    }
"""

# ============================
# PAGE STYLE (NO BUTTON CSS HERE)
# ============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    [data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarNav"] {display: none;}
    #MainMenu, footer, header, button[kind="header"] {visibility: hidden;}

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background: #FFFFFF;
        min-height: 100vh;
        color:#000000;
    }

    .block-container {
        max-width: 1200px;
        padding: 2rem 3rem;
        margin: 0 auto;
    }

    h1 {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 2.4rem !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.5px;
    }

    h2 {
        color: #000000 !important;
        font-weight: 700 !important;
        margin-top: 2.5rem !important;
        margin-bottom: 1.2rem !important;
        font-size: 1.7rem !important;
        display: flex;
        align-items: center;
    }

    .section-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #E87532;
        color: white;
        width: 45px;
        height: 45px;
        border-radius: 14px;
        font-weight: 700;
        margin-right: 18px;
        font-size: 1.1rem;
    }

    .card-badge {
        color: #E87532 !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        letter-spacing: 1.5px;
        margin-bottom: 0.8rem !important;
        text-transform: uppercase;
    }

    .welcome-text {
        color: #555555;
        font-size: 0.95rem;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div,
    .stDateInput > div > div > input {
        background: rgba(0, 0, 0, 0.02) !important;
        border-radius: 10px !important;
        padding: 0.7rem 1rem !important;
    }

    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stMultiSelect label {
        color:#000000 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.3rem !important;
    }

    ::-webkit-scrollbar {
        width: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: #E87532;
        border-radius: 6px;
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
    background-color: #f8fafc;
    color: #e87532;
}

.dropdown {
    position: relative;
    display: inline-block;
}

.dropdown-toggle {
    color: #000000;
    text-decoration: none;
    font-size: 1rem;
    font-family: 'Nunito Sans', sans-serif;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    background: transparent;
    border: none;
    transition: all 0.3s ease;
}

.dropdown-toggle:hover {
    background-color: #f8fafc;
    color: #e87532;
}

.dropdown-content {
    display: none;
    position: absolute;
    background-color: white;
    min-width: 200px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    border-radius: 8px;
    z-index: 100000;
    top: 100%;
    margin-top: 0.5rem;
}

.dropdown:hover .dropdown-content {
    display: block;
}

.dropdown-item {
    color: #000000 !important;
    padding: 12px 16px;
    text-decoration: none !important;
    display: block;
    font-family: 'Nunito Sans', sans-serif;
    cursor: pointer;
    transition: all 0.3s ease;
}

.dropdown-item:visited {
    color: #000000 !important;
}

.dropdown-item:hover {
    background-color: #f8fafc;
    color: #e87532;
}     
.logo {
    font-size: 24px;
    font-weight: 400;
    color: #2c3e50;
    font-family: 'Nunito Sans', sans-serif !important;
    letter-spacing: -0.5px;
}
</style>
""", unsafe_allow_html=True)



st.markdown(f"""
<div class="nav-wrapper">
    <div class="logo">Resume Creator</div>
    <div class="nav-menu">
        <div class="nav-item">
            <a class="nav-link" href="?home=true&user={current_user}" target="_self">Home</a>
        </div>
        <div class="nav-item">
            <a class="nav-link" href="?add_jd=true&user={current_user}" target="_self">Add JD</a>
        </div>
        <div class="nav-item">
            <a class="nav-link" href="?logout=true" target="_self">Logout</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Handle navigation
if st.query_params.get("add_jd") == "true":
    st.query_params.clear()
    if st.session_state.logged_in_user:
        st.query_params["user"] = st.session_state.logged_in_user
    st.switch_page("pages/job.py")

if st.query_params.get("home") == "true":
    st.query_params.clear()
    if st.session_state.logged_in_user:
        st.query_params["user"] = st.session_state.logged_in_user
    st.switch_page("app.py")

if st.query_params.get("logout") == "true":
    # ONLY clear session on explicit logout
    st.session_state.logged_in_user = None
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.switch_page("app.py")




if  st.session_state.logged_in_user :
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 3rem; margin-left: 15rem; padding-right: 100px;">
                <h1> Add Basic Information</h1>
                <p class="welcome-text">Welcome back, <strong>{st.session_state.get("username", "User")}</strong>! Let's add your basic information.</p>
            </div>
            """,
            unsafe_allow_html=True
        )


    

    st.markdown('<h2>Choose Input Method</h2>', unsafe_allow_html=True)
    input_method = st.radio(
        "How would you like to provide your information?",
        ["Manual Entry", "Upload Resume"],
        horizontal=True,
        key="input_method_radio"
    )

    user_data = {}
    professional_experience = []
    education = []
    certificate = []
    project = []

    remove_index_edu = None
    remove_index_cert = None
    remove_index = None
    remove_index_project = None

    # ====================================================================================
    # MANUAL ENTRY
    # ====================================================================================
    if input_method == "Manual Entry":
        st.session_state["input_method"] = input_method

        # ---------------- PERSONAL INFO ----------------
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<h2><span class="section-number">1</span>Personal Information</h2>', unsafe_allow_html=True)
        st.markdown(f'<p class="card-badge">BASIC DETAILS</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(
                "Full Name *",
                placeholder="e.g., John Smith",
                key="name_input",
                value=st.session_state.saved_personal_info.get("name", "")
            )
            experience = st.text_input(
                "Years of Experience *",
                placeholder="e.g., 5",
                key="experience_input",
                value=st.session_state.saved_personal_info.get("experience", "")
            )
            phone = st.text_input(
                "Phone number *",
                placeholder="e.g., +91 ",
                key="phone",
                value=st.session_state.saved_personal_info.get("phone", "")
            )
            email = st.text_input(
                "email *",
                placeholder="e.g., google@gmail.com",
                key="email",
                value=st.session_state.saved_personal_info.get("email", "")
            )
            url = st.text_input(
                "linkedin/github",
                placeholder="e.g., user/linkedin.com",
                key="url",
                value=st.session_state.saved_personal_info.get("url", "")
            )

        with col2:
            all_skills_list = load_skills_from_json()
            skills = st.multiselect(
                "Your Core Skills *",
                options=all_skills_list,
                help="Select all relevant skills",
                key="general_skills",
                default=st.session_state.saved_personal_info.get("skills", [])
            )
            location = st.text_input(
                "location *",
                placeholder="e.g., New York",
                key="location",
                value=st.session_state.saved_personal_info.get("location", "")
            )

        col_save = st.columns([1, 2, 1])
        with col_save[1]:
            with stylable_container("template-btn-save-personal", css_styles=SAVE_STYLE):
                if st.button("Save Personal Information", key="save_personal", use_container_width=True):
                    if name and skills and experience and phone and email:
                        if not is_valid_email(email):
                            st.error("Please enter a valid email address")
                        elif not is_valid_phone(phone):
                            st.error("Please enter a valid phone number")
                        else:
                            st.session_state.saved_personal_info = {
                                "name": name,
                                "skills": skills,
                                "experience": experience,
                                "phone": phone,
                                "email": email,
                                "url": url,
                                "location": location
                            }
                            st.success("✅ Personal information saved!")
                    else:
                        st.error("Please fill in all required fields marked with *")

        st.markdown("---")

        # ---------------- PROFESSIONAL EXPERIENCE ----------------
        st.markdown('<h2><span class="section-number">2</span>Professional Experience</h2>', unsafe_allow_html=True)
        for idx, i in enumerate(st.session_state.exp_indices):
            st.markdown(f'<p class="card-badge">EXPERIENCE {idx + 1}</p>', unsafe_allow_html=True)

            saved_exp = st.session_state.saved_experiences.get(i, {})

            col1, col2 = st.columns([3, 3])
            with col1:
                company_name = st.text_input(
                    "Company Name",
                    key=f"company_{i}",
                    placeholder="e.g., Google Inc.",
                    value=saved_exp.get("company", "")
                )
                position_name = st.text_input(
                    "Position",
                    key=f"position_{i}",
                    placeholder="e.g., Senior Developer",
                    value=saved_exp.get("position", "")
                )

                exp_skills_list = load_skills_from_json()
                exp_skills = st.multiselect(
                    "Skills Used (Experience)",
                    options=exp_skills_list,
                    help="Select skills relevant to this role",
                    key=f"exp_skills_{i}",
                    default=saved_exp.get("exp_skills", [])
                )

            with col2:
                comp_startdate = st.text_input(
                    "Start Date (MM/YYYY)",
                    key=f"comp_startdate_{i}",
                    placeholder="e.g., 01/2020",
                    value=saved_exp.get("start_date", "")
                )
                comp_enddate = st.text_input(
                    "End Date (MM/YYYY) or 'Present'",
                    key=f"comp_enddate_{i}",
                    placeholder="e.g., 12/2023 or Present",
                    value=saved_exp.get("end_date", "")
                )

                if comp_startdate and comp_enddate and comp_enddate.lower() != "present":
                    try:
                        from datetime import datetime
                        start = datetime.strptime(comp_startdate, "%m/%Y")
                        end = datetime.strptime(comp_enddate, "%m/%Y")
                        if start > end:
                            st.warning("⚠️ Start date must be before end date")
                    except:
                        st.warning("⚠️ Use MM/YYYY format")

            col_save, col_remove = st.columns(2)
            with col_remove:
                with stylable_container(f"remove-exp-{i}", css_styles=REMOVE_STYLE):
                    if st.button(f"Remove Experience {idx + 1}", key=f"remove_exp_{i}", use_container_width=True):
                        remove_index = i

            with col_save:
                with stylable_container(f"save-exp-{i}", css_styles=SAVE_STYLE):
                    if st.button(f"Save Experience {idx + 1}", key=f"save_exp_{i}", use_container_width=True):
                        if company_name and position_name:
                            st.session_state.saved_experiences[i] = {
                                "company": company_name,
                                "position": position_name,
                                "exp_skills": exp_skills,
                                "start_date": comp_startdate,
                                "end_date": comp_enddate
                            }
                            st.success(f"✅ Experience {idx + 1} saved!")
                        else:
                            st.error("Please fill in company name and position")

            professional_experience.append({
                "company": company_name,
                "position": position_name,
                'exp_skills': exp_skills,
                "start_date": comp_startdate,
                "end_date": comp_enddate
            })

        if remove_index is not None:
            st.session_state.exp_indices.remove(remove_index)
            st.rerun()

        col_add_exp = st.columns([1, 2, 1])
        with col_add_exp[1]:
            st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)

            with stylable_container("add-exp-btn", css_styles=ADD_STYLE):
                st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)

                if st.button("+ Add More Experience", key="add_exp", use_container_width=True):
                    new_idx = max(st.session_state.exp_indices) + 1 if st.session_state.exp_indices else 0
                    st.session_state.exp_indices.append(new_idx)
                    st.rerun()

        st.markdown("---")

        # ---------------- EDUCATION ----------------
        st.markdown('<h2><span class="section-number">3</span>Education</h2>', unsafe_allow_html=True)

        for idx, i in enumerate(st.session_state.edu_indices):
            st.markdown(f'<p class="card-badge">EDUCATION {idx + 1}</p>', unsafe_allow_html=True)

            saved_edu = st.session_state.saved_education.get(i, {})
            col1, col2 = st.columns(2)
            with col1:
                course = st.text_input(
                    "Course/Degree",
                    placeholder="e.g., Master of Computer Application",
                    key=f"course_{i}",
                    value=saved_edu.get("course", "")
                )
                university = st.text_input(
                    "Institution",
                    placeholder="e.g., Texas University",
                    key=f"university_{i}",
                    value=saved_edu.get("university", "")
                )
            with col2:
                edu_startdate = st.text_input(
                    "Start Date (MM/YYYY)",
                    key=f"edu_start_{i}",
                    placeholder="e.g., 08/2018",
                    value=saved_edu.get("start_date", "")
                )
                edu_enddate = st.text_input(
                    "End Date (MM/YYYY) or 'Present'",
                    key=f"edu_end_{i}",
                    placeholder="e.g., 05/2022 or Present",
                    value=saved_edu.get("end_date", "")
                )

                if edu_startdate and edu_enddate and edu_enddate.lower() != "present":
                    try:
                        from datetime import datetime
                        start = datetime.strptime(edu_startdate, "%m/%Y")
                        end = datetime.strptime(edu_enddate, "%m/%Y")
                        if start > end:
                            st.warning("⚠️ Start date must be before end date")
                    except:
                        st.warning("⚠️ Use MM/YYYY format")

            col_save, col_remove = st.columns(2)
            with col_remove:
                with stylable_container(f"remove-edu-{i}", css_styles=REMOVE_STYLE):
                    if st.button(f"Remove Education {idx + 1}", key=f"remove_edu_{i}", use_container_width=True):
                        remove_index_edu = i

            with col_save:
                with stylable_container(f"save-edu-{i}", css_styles=SAVE_STYLE):
                    if st.button(f"Save Education {idx + 1}", key=f"save_edu_{i}", use_container_width=True):
                        if course and university:
                            st.session_state.saved_education[i] = {
                                "course": course,
                                "university": university,
                                "start_date": edu_startdate,
                                "end_date": edu_enddate
                            }
                            st.success(f"✅ Education {idx + 1} saved!")
                        else:
                            st.error("Please fill in course and institution")

            education.append({
                "course": course,
                "university": university,
                "start_date": edu_startdate,
                "end_date": edu_enddate
            })

        if remove_index_edu is not None:
            st.session_state.edu_indices.remove(remove_index_edu)
            st.rerun()

        col_add_edu = st.columns([1, 2, 1])
        with col_add_edu[1]:
            with stylable_container("add-edu-btn", css_styles=ADD_STYLE):
                st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)

                if st.button("+ Add More Education", key="add_edu", use_container_width=True):
                    new_idx = max(st.session_state.edu_indices) + 1 if st.session_state.edu_indices else 0
                    st.session_state.edu_indices.append(new_idx)
                    st.rerun()

        st.markdown("---")

        # ---------------- CERTIFICATIONS ----------------
        st.markdown('<h2><span class="section-number">4</span>Certifications</h2>', unsafe_allow_html=True)

        for idx, i in enumerate(st.session_state.cert_indices):
            st.markdown(f'<p class="card-badge">CERTIFICATION {idx + 1}</p>', unsafe_allow_html=True)

            saved_cert = st.session_state.saved_certificates.get(i, {})
            col1, col2 = st.columns(2)
            with col1:
                certificate_name = st.text_input(
                    "Certificate Name",
                    placeholder="e.g., AWS Solutions Architect",
                    key=f"certificate_{i}",
                    value=saved_cert.get("certificate_name", "")
                )
                provider = st.text_input(
                    "Provider",
                    placeholder="e.g., Amazon Web Services",
                    key=f"Provider_{i}",
                    value=saved_cert.get("provider_name", "")
                )
            with col2:
                comp_date = st.text_input(
                    "Completion Date (MM/YYYY)",
                    key=f"comp_date_{i}",
                    placeholder="e.g., 06/2023",
                    value=saved_cert.get("completed_date", "")
                )

            col_save, col_remove = st.columns(2)
            with col_remove:
                with stylable_container(f"remove-cert-{i}", css_styles=REMOVE_STYLE):
                    if st.button(f"Remove Certification {idx + 1}", key=f"remove_cert_{i}", use_container_width=True):
                        remove_index_cert = i

            with col_save:
                with stylable_container(f"save-cert-{i}", css_styles=SAVE_STYLE):
                    if st.button(f"Save Certification {idx + 1}", key=f"save_cert_{i}", use_container_width=True):
                        if certificate_name and provider:
                            st.session_state.saved_certificates[i] = {
                                "certificate_name": certificate_name,
                                "provider_name": provider,
                                "completed_date": comp_date
                            }
                            st.success(f"✅ Certification {idx + 1} saved!")
                        else:
                            st.error("Please fill in certificate name and provider")

            certificate.append({
                "certificate_name": certificate_name,
                "provider_name": provider,
                "completed_date": comp_date
            })

        if remove_index_cert is not None:
            st.session_state.cert_indices.remove(remove_index_cert)
            st.rerun()

        col_add_cert = st.columns([1, 2, 1])
        with col_add_cert[1]:
            with stylable_container("add-cert-btn", css_styles=ADD_STYLE):
                st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)

                if st.button("+ Add More Certification", key="add_cert", use_container_width=True):
                    new_idx = max(st.session_state.cert_indices) + 1 if st.session_state.cert_indices else 0
                    st.session_state.cert_indices.append(new_idx)
                    st.rerun()

        st.markdown("---")

        # ---------------- PROJECTS ----------------
        st.markdown('<h2><span class="section-number">5</span>Projects</h2>', unsafe_allow_html=True)

        for idx, i in enumerate(st.session_state.project_indices):
            st.markdown(f'<p class="card-badge">PROJECT {idx + 1}</p>', unsafe_allow_html=True)

            saved_proj = st.session_state.saved_projects.get(i, {})

            col1, col2 = st.columns(2)
            with col1:
                projectname = st.text_input(
                    "Project Name",
                    placeholder="e.g., Created An Integration Tool",
                    key=f"projectname_{i}",
                    value=saved_proj.get("projectname", "")
                )
                tools = st.text_input(
                    "Tools/Languages",
                    placeholder="e.g., PowerBI, SQL, Python",
                    key=f"tools_{i}",
                    value=saved_proj.get("tools", "")
                )
            with col2:
                decription = st.text_area(
                    "Description (Key achievements)",
                    key=f"decription_{i}",
                    height=150,
                    value=saved_proj.get("decription", "")
                )

            col_save, col_remove = st.columns(2)
            with col_remove:
                with stylable_container(f"remove-proj-{i}", css_styles=REMOVE_STYLE):
                    if st.button(f"Remove Project {idx + 1}", key=f"remove_project_{i}", use_container_width=True):
                        remove_index_project = i

            with col_save:
                with stylable_container(f"save-proj-{i}", css_styles=SAVE_STYLE):
                    if st.button(f"Save Project {idx + 1}", key=f"save_project_{i}", use_container_width=True):
                        if projectname:
                            st.session_state.saved_projects[i] = {
                                "projectname": projectname,
                                "tools": tools,
                                "decription": decription
                            }
                            st.success(f"✅ Project {idx + 1} saved!")
                        else:
                            st.error("Please fill in project name")

            project.append({
                "projectname": projectname,
                "tools": tools,
                "decription": decription
            })

        if remove_index_project is not None:
            st.session_state.project_indices.remove(remove_index_project)
            st.rerun()

        col_add_proj = st.columns([1, 2, 1])
        with col_add_proj[1]:
            with stylable_container("add-proj-btn", css_styles=ADD_STYLE):
                st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)

                if st.button("+ Add More Projects", key="add_project", use_container_width=True):
                    new_idx = max(st.session_state.project_indices) + 1 if st.session_state.project_indices else 0
                    st.session_state.project_indices.append(new_idx)
                    st.rerun()

        st.markdown("---")

        # ---------------- CUSTOM SECTIONS ----------------
        st.markdown('<h2><span class="section-number">6</span>Custom Sections</h2>', unsafe_allow_html=True)

        remove_index_custom = None
        custom_sections = []

        for idx, i in enumerate(st.session_state.custom_indices):
            st.markdown(f'<p class="card-badge">CUSTOM SECTION {idx + 1}</p>', unsafe_allow_html=True)

            saved_custom = st.session_state.saved_custom_sections.get(i, {})

            col1, col2 = st.columns([1, 1])
            with col1:
                section_title = st.text_input(
                    "Section Heading *",
                    placeholder="e.g., Languages, Achievements, Interests",
                    key=f"custom_title_{i}",
                    value=saved_custom.get("title", "")
                )
            with col2:
                section_description = st.text_area(
                    "Description / Details *",
                    placeholder="Add details for this section...",
                    key=f"custom_desc_{i}",
                    height=120,
                    value=saved_custom.get("description", "")
                )

            col_save, col_remove = st.columns(2)
            with col_remove:
                with stylable_container(f"remove-custom-{i}", css_styles=REMOVE_STYLE):
                    if st.button(f"Remove Custom Section {idx + 1}", key=f"remove_custom_{i}", use_container_width=True):
                        remove_index_custom = i

            with col_save:
                with stylable_container(f"save-custom-{i}", css_styles=SAVE_STYLE):
                    if st.button(f"Save Custom Section {idx + 1}", key=f"save_custom_{i}", use_container_width=True):
                        if section_title and section_description:
                            st.session_state.saved_custom_sections[i] = {
                                "title": section_title,
                                "description": section_description
                            }
                            st.success(f"✅ Custom Section {idx + 1} saved!")
                        else:
                            st.error("Please fill in both the heading and description fields.")

            custom_sections.append({
                "title": section_title,
                "description": section_description
            })

        if remove_index_custom is not None:
            st.session_state.custom_indices.remove(remove_index_custom)
            st.rerun()

        col_add_custom = st.columns([1, 2, 1])
        with col_add_custom[1]:
            with stylable_container("add-custom-btn", css_styles=ADD_STYLE):
                st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)

                if st.button("+ Add Custom Section", key="add_custom", use_container_width=True):
                    new_idx = max(st.session_state.custom_indices) + 1 if st.session_state.custom_indices else 0
                    st.session_state.custom_indices.append(new_idx)
                    st.rerun()

        st.markdown("---")

        # ---------------- CONTINUE BUTTON (SUBMIT) ----------------
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with stylable_container("continue-btn", css_styles=PRIMARY_LARGE_BUTTON_STYLE):
                if st.button("Continue", key="man-btn", use_container_width=True):
                    st.balloons()
                    if not is_valid_email(email):
                        st.error("Please enter a valid email address")
                    elif not is_valid_phone(phone):
                        st.error("Please enter a valid phone number")
                    else:
                        if name and skills and experience:
                            with st.spinner("Processing your resume..."):
                                filtered_experience = [p for p in professional_experience if p["company"] and p["position"]]
                                filtered_education = [e for e in education if e["course"] and e["university"]]
                                filtered_certificate = [c for c in certificate if c["certificate_name"]]
                                filtered_project = [p for p in project if p["projectname"]]

                                user_data = {
                                    'name': name,
                                    'skills': skills,
                                    'experience': experience,
                                    'phone': phone,
                                    'email': email,
                                    'url': url,
                                    'location': location,
                                    'professional_experience': filtered_experience,
                                    'education': filtered_education,
                                    'certificate': filtered_certificate,
                                    'project': filtered_project,
                                    'custom_sections': {
                                        c["title"]: c["description"]
                                        for c in custom_sections
                                        if c["title"] and c["description"]
                                    }
                                }

                            st.session_state.resume_source = user_data
                            st.write(user_data)  # optional debug

                            if 'logged_in_user' in st.session_state:
                                st.session_state.input_method = "Manual Entry"
                                save_success = save_user_resume(
                                    st.session_state.logged_in_user,
                                    user_data,
                                    input_method="Manual Entry"
                                )
                                if save_success:
                                    st.success("Resume processed and saved to profile!")
                                else:
                                    st.warning("Resume processed but couldn't save to profile")

                            st.switch_page("pages/job.py")
                        else:
                            st.error("Please fill in all required fields marked with *")

    # ====================================================================================
    # UPLOAD RESUME
    # ====================================================================================
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<h2>Upload Your Resume</h2>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Drop your PDF or DOCX resume here or click to browse",
            type=["pdf", "docx"],
            help="Supported formats: PDF, DOCX",
            key="uploader_widget"
        )

        if uploaded_file:
            with st.spinner("File processing..."):
                if uploaded_file.type == "application/pdf":
                    extracted_text = extract_text_from_pdf(uploaded_file)
                else:
                    extracted_text = extract_text_from_docx(uploaded_file)

            st.markdown('<h3>Extracted Text Preview</h3>', unsafe_allow_html=True)
            st.text_area(
                "Extracted Content",
                value=extracted_text,
                height=300,
                key="extracted_content_preview",
                label_visibility="collapsed"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with stylable_container("process-resume-btn", css_styles=PRIMARY_LARGE_BUTTON_STYLE):
                    if st.button("Process Resume", key="re-btn", use_container_width=True):
                        if extracted_text:
                            if 'logged_in_user' not in st.session_state or not st.session_state.logged_in_user:
                                st.error("⚠️ Session expired. Please login again.")
                                st.switch_page("login.py")

                            parsed_data = None
                            loading_placeholder = st.empty()
                            loading_placeholder.markdown("""
                                <div id="overlay-loader">
                                    <div class="loader-spinner"></div>
                                    <p>Analyzing your resume and parsing details</p>
                                </div>
                                <style>
                                    #overlay-loader {
                                        position: fixed;
                                        top: 0;
                                        left: 0;
                                        width: 100vw;
                                        height: 100vh;
                                        background: rgba(255, 255, 255, 0.40);
                                        backdrop-filter: blur(10px);
                                        display: flex;
                                        flex-direction: column;
                                        justify-content: center;
                                        align-items: center;
                                        z-index: 9999;
                                        color: #e87532 !important;
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
                                parsed_data = extract_details_from_text(extracted_text)
                            except Exception as e:
                                st.error(f"Error during detail extraction: {e}")
                                parsed_data = None
                            finally:
                                loading_placeholder.empty()

                            if parsed_data:
                                st.session_state.resume_source = parsed_data
                                st.session_state.resume_processed = True
                                st.session_state.input_method = "Upload Entry"

                                save_success = save_user_resume(
                                    st.session_state.logged_in_user,
                                    parsed_data,
                                    input_method="Upload Entry"
                                )

                                if save_success:
                                    st.success("✅ Resume processed and saved successfully! Redirecting...")
                                    time.sleep(0.5)
                                    st.switch_page("pages/job.py")
                                else:
                                    st.error("❌ Failed to save resume. Please try again.")
                            else:
                                st.error("Failed to process resume. Please ensure your file is clean or try manual entry.")
                        else:
                            st.error("Please upload your resume first")
else:
    st.error("please login first")

# st.markdown('<div id="jd" style="scroll-margin-top: 100px;"></div>', unsafe_allow_html=True)
# if st.session_state.get("show_job_inside_main", False):
#     job()
#     st.stop() 
# if exsting:
#     job()
# if "show_job_inside_main" in st.session_state and st.session_state.show_job_inside_main:
#         job()
#         st.stop()   # Stop showing other sections
