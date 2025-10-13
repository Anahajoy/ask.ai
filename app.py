import streamlit as st
import json
import bcrypt
import os
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
import pdfplumber
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import requests
import time

# =============================================================================
# FAST AI MODEL INTEGRATION (FREE)
# =============================================================================

def generate_content_with_huggingface(prompt, max_length=200):
    """Use Hugging Face Inference API - Free and Fast"""
    
    # Multiple free models to try (no API key needed for some)
    models = [
        "microsoft/DialoGPT-medium",
        "gpt2",
        "distilgpt2"
    ]
    
    for model in models:
        try:
            API_URL = f"https://api-inference.huggingface.co/models/{model}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_length,
                    "temperature": 0.7,
                    "return_full_text": False,
                    "do_sample": True
                }
            }
            
            response = requests.post(API_URL, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    if generated_text and len(generated_text) > 20:
                        return clean_generated_text(generated_text)
            
            # Wait a bit before trying next model
            time.sleep(1)
            
        except Exception as e:
            continue
    
    # Fallback to template-based generation
    return generate_template_content(prompt)

def clean_generated_text(text):
    """Clean and format AI-generated text"""
    # Remove incomplete sentences
    sentences = text.split('.')
    complete_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10 and sentence[0].isupper():
            complete_sentences.append(sentence)
    
    result = '. '.join(complete_sentences[:3])  # Max 3 sentences
    if result and not result.endswith('.'):
        result += '.'
    
    return result

def generate_template_content(prompt):
    """Fallback template-based content generation"""
    
    # Extract key information from prompt
    prompt_lower = prompt.lower()
    
    if "professional summary" in prompt_lower:
        if "software" in prompt_lower or "developer" in prompt_lower:
            return "Experienced software developer with proven expertise in full-stack development and modern programming languages. Demonstrated ability to deliver high-quality solutions and collaborate effectively with cross-functional teams."
        elif "marketing" in prompt_lower:
            return "Results-driven marketing professional with strong analytical skills and creative problem-solving abilities. Proven track record in developing and executing successful marketing campaigns that drive business growth."
        elif "data" in prompt_lower or "analyst" in prompt_lower:
            return "Detail-oriented data professional with expertise in data analysis, statistical modeling, and insights generation. Skilled in transforming complex datasets into actionable business recommendations."
        elif "manager" in prompt_lower or "management" in prompt_lower:
            return "Strategic leader with proven track record in team management and project execution. Strong background in process optimization, stakeholder communication, and driving organizational success."
        else:
            return "Dedicated professional with strong technical skills and proven ability to contribute to team success. Committed to continuous learning and delivering high-quality results in dynamic environments."
    
    elif "key achievement" in prompt_lower or "accomplishment" in prompt_lower:
        achievements = [
            "Successfully delivered projects ahead of schedule while maintaining high quality standards",
            "Improved team efficiency through implementation of best practices and process optimization",
            "Collaborated with cross-functional teams to achieve organizational objectives",
            "Contributed to positive team culture and knowledge sharing initiatives"
        ]
        return " • ".join(achievements[:2])
    
    else:
        return "Professional with relevant experience and skills aligned with position requirements."

# =============================================================================
# ATS RESUME TEMPLATES
# =============================================================================

class ATSResumeBuilder:
    def __init__(self):
        self.color_themes = {
            "Professional Blue": {"primary": RGBColor(54, 96, 146), "secondary": RGBColor(79, 129, 189)},
            "Corporate Black": {"primary": RGBColor(64, 64, 64), "secondary": RGBColor(128, 128, 128)},
            "Modern Green": {"primary": RGBColor(76, 132, 73), "secondary": RGBColor(106, 168, 79)},
            "Creative Purple": {"primary": RGBColor(112, 79, 161), "secondary": RGBColor(142, 124, 195)},
            "Executive Navy": {"primary": RGBColor(31, 73, 125), "secondary": RGBColor(68, 114, 196)}
        }
    
    def create_ats_resume(self, data, color_theme="Professional Blue", template_style="modern"):
        """Create ATS-friendly resume with selected theme"""
        
        doc = Document()
        
        # Set document margins
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(0.7)
            section.bottom_margin = Inches(0.7)
            section.left_margin = Inches(0.7)
            section.right_margin = Inches(0.7)
        
        theme_colors = self.color_themes.get(color_theme, self.color_themes["Professional Blue"])
        
        # Header Section
        self._add_header(doc, data, theme_colors)
        
        # Professional Summary
        if data.get('ai_summary'):
            self._add_section(doc, "PROFESSIONAL SUMMARY", data['ai_summary'], theme_colors)
        
        # Core Competencies/Skills
        if data.get('skills'):
            self._add_skills_section(doc, data['skills'], theme_colors)
        
        # Professional Experience
        if data.get('experience'):
            self._add_experience_section(doc, data, theme_colors)
        
        # Education
        if data.get('education'):
            self._add_section(doc, "EDUCATION", data['education'], theme_colors)
        
        # Key Achievements (AI Generated)
        if data.get('ai_achievements'):
            self._add_section(doc, "KEY ACHIEVEMENTS", data['ai_achievements'], theme_colors)
        
        return doc
    
    def _add_header(self, doc, data, theme_colors):
        """Add professional header"""
        
        # Name
        name_para = doc.add_paragraph()
        name_run = name_para.add_run(data.get('name', '').upper())
        name_run.font.size = Pt(18)
        name_run.font.color.rgb = theme_colors['primary']
        name_run.bold = True
        name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Role
        role_para = doc.add_paragraph()
        role_run = role_para.add_run(data.get('role', ''))
        role_run.font.size = Pt(12)
        role_run.font.color.rgb = theme_colors['secondary']
        role_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Contact (if provided)
        contact_para = doc.add_paragraph()
        contact_run = contact_para.add_run("Email: professional@email.com | Phone: (555) 123-4567")
        contact_run.font.size = Pt(10)
        contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph()  # Space
    
    def _add_section(self, doc, title, content, theme_colors):
        """Add a section with title and content"""
        
        # Section title
        title_para = doc.add_paragraph()
        title_run = title_para.add_run(title)
        title_run.font.size = Pt(12)
        title_run.font.color.rgb = theme_colors['primary']
        title_run.bold = True
        
        # Add underline effect with border
        title_para.paragraph_format.border_bottom.width = Pt(1)
        title_para.paragraph_format.border_bottom.color.rgb = theme_colors['primary']
        
        # Content
        content_para = doc.add_paragraph(content)
        content_para.paragraph_format.space_after = Pt(12)
        
        doc.add_paragraph()  # Space
    
    def _add_skills_section(self, doc, skills, theme_colors):
        """Add skills section with ATS-friendly formatting"""
        
        # Title
        title_para = doc.add_paragraph()
        title_run = title_para.add_run("CORE COMPETENCIES")
        title_run.font.size = Pt(12)
        title_run.font.color.rgb = theme_colors['primary']
        title_run.bold = True
        title_para.paragraph_format.border_bottom.width = Pt(1)
        title_para.paragraph_format.border_bottom.color.rgb = theme_colors['primary']
        
        # Skills in ATS-friendly format
        skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
        
        # Group skills in rows of 3 for better ATS parsing
        for i in range(0, len(skills_list), 3):
            skill_group = skills_list[i:i+3]
            skill_para = doc.add_paragraph()
            skill_text = " • ".join(skill_group)
            skill_run = skill_para.add_run(skill_text)
            skill_run.font.size = Pt(10)
        
        doc.add_paragraph()  # Space
    
    def _add_experience_section(self, doc, data, theme_colors):
        """Add professional experience with AI enhancements"""
        
        # Title
        title_para = doc.add_paragraph()
        title_run = title_para.add_run("PROFESSIONAL EXPERIENCE")
        title_run.font.size = Pt(12)
        title_run.font.color.rgb = theme_colors['primary']
        title_run.bold = True
        title_para.paragraph_format.border_bottom.width = Pt(1)
        title_para.paragraph_format.border_bottom.color.rgb = theme_colors['primary']
        
        # Experience content (AI enhanced)
        exp_para = doc.add_paragraph()
        
        # Add role and company (if extractable)
        role_company = f"{data.get('role', 'Professional')} | Company Name"
        role_run = exp_para.add_run(role_company)
        role_run.bold = True
        role_run.font.size = Pt(11)
        
        exp_para.add_run("\n")
        
        # AI-enhanced experience description
        experience_text = data.get('experience', '')
        if data.get('ai_experience_enhancement'):
            experience_text = data['ai_experience_enhancement']
        
        exp_para.add_run(experience_text)
        
        doc.add_paragraph()  # Space

def create_pdf_resume(data, color_theme="Professional Blue"):
    """Create PDF version of resume"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.7*inch, bottomMargin=0.7*inch)
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Color mapping for PDF
    color_map = {
        "Professional Blue": colors.HexColor('#36609B'),
        "Corporate Black": colors.HexColor('#404040'),
        "Modern Green": colors.HexColor('#4C8449'),
        "Creative Purple": colors.HexColor('#704FA1'),
        "Executive Navy": colors.HexColor('#1F497D')
    }
    
    primary_color = color_map.get(color_theme, colors.HexColor('#36609B'))
    
    # Custom styles
    name_style = ParagraphStyle(
        'CustomName',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=primary_color,
        alignment=1,  # Center
        spaceAfter=6
    )
    
    role_style = ParagraphStyle(
        'CustomRole',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        alignment=1,  # Center
        spaceAfter=12
    )
    
    section_style = ParagraphStyle(
        'CustomSection',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=primary_color,
        spaceAfter=6,
        borderWidth=1,
        borderColor=primary_color,
        borderPadding=2
    )
    
    content_style = ParagraphStyle(
        'CustomContent',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=12
    )
    
    # Build PDF content
    story = []
    
    # Header
    story.append(Paragraph(data.get('name', '').upper(), name_style))
    story.append(Paragraph(data.get('role', ''), role_style))
    story.append(Paragraph("Email: professional@email.com | Phone: (555) 123-4567", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Professional Summary
    if data.get('ai_summary'):
        story.append(Paragraph("PROFESSIONAL SUMMARY", section_style))
        story.append(Paragraph(data['ai_summary'], content_style))
    
    # Skills
    if data.get('skills'):
        story.append(Paragraph("CORE COMPETENCIES", section_style))
        skills_list = [skill.strip() for skill in data['skills'].split(',') if skill.strip()]
        skills_text = " • ".join(skills_list)
        story.append(Paragraph(skills_text, content_style))
    
    # Experience
    if data.get('experience'):
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", section_style))
        story.append(Paragraph(data.get('ai_experience_enhancement', data['experience']), content_style))
    
    # Education
    if data.get('education'):
        story.append(Paragraph("EDUCATION", section_style))
        story.append(Paragraph(data['education'], content_style))
    
    # Key Achievements
    if data.get('ai_achievements'):
        story.append(Paragraph("KEY ACHIEVEMENTS", section_style))
        story.append(Paragraph(data['ai_achievements'], content_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# =============================================================================
# FILE PROCESSING FUNCTIONS
# =============================================================================

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def extract_text_from_docx(docx_file):
    """Extract text from DOCX file"""
    try:
        doc = Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return ""

def parse_resume_content(text):
    """Parse resume content into structured data"""
    
    data = {}
    text_lower = text.lower()
    
    # Try to extract name (first line usually)
    lines = text.strip().split('\n')
    if lines:
        potential_name = lines[0].strip()
        if len(potential_name) < 50 and not any(char.isdigit() for char in potential_name):
            data['name'] = potential_name
    
    # Extract skills
    skills_pattern = r'(?:skills?|competencies|technical skills?)[:\s]*([^\n]*(?:\n[^\n]*)*?)(?=\n\s*\n|\n[A-Z]|\Z)'
    skills_match = re.search(skills_pattern, text, re.IGNORECASE | re.MULTILINE)
    if skills_match:
        data['skills'] = skills_match.group(1).strip()
    
    # Extract experience
    exp_pattern = r'(?:experience|employment|work history)[:\s]*([^\n]*(?:\n[^\n]*)*?)(?=\n\s*\n|\n(?:education|skills)|$)'
    exp_match = re.search(exp_pattern, text, re.IGNORECASE | re.MULTILINE)
    if exp_match:
        data['experience'] = exp_match.group(1).strip()
    
    # Extract education
    edu_pattern = r'(?:education|qualifications?)[:\s]*([^\n]*(?:\n[^\n]*)*?)(?=\n\s*\n|\n[A-Z]|$)'
    edu_match = re.search(edu_pattern, text, re.IGNORECASE | re.MULTILINE)
    if edu_match:
        data['education'] = edu_match.group(1).strip()
    
    return data

# =============================================================================
# AI CONTENT ENHANCEMENT FUNCTIONS
# =============================================================================

def enhance_resume_with_ai(user_data, job_description=""):
    """Enhance resume content using AI based on job description"""
    
    enhanced_data = user_data.copy()
    
    # Generate Professional Summary
    summary_prompt = f"""
    Create a professional summary for a {user_data.get('role', 'professional')} position.
    Skills: {user_data.get('skills', '')}
    Experience: {user_data.get('experience', '')[:200]}
    Job Requirements: {job_description[:300]}
    
    Write a 2-3 sentence professional summary:
    """
    
    enhanced_data['ai_summary'] = generate_content_with_huggingface(summary_prompt, 150)
    
    # Enhance Experience Description
    if user_data.get('experience'):
        exp_prompt = f"""
        Enhance this work experience for a {user_data.get('role', 'professional')} applying for:
        Job Description: {job_description[:200]}
        
        Original Experience: {user_data.get('experience')[:300]}
        
        Rewrite with measurable achievements and relevant keywords:
        """
        
        enhanced_data['ai_experience_enhancement'] = generate_content_with_huggingface(exp_prompt, 200)
    
    # Generate Key Achievements
    achievements_prompt = f"""
    Create 3-4 key achievements for a {user_data.get('role', 'professional')} with these skills:
    Skills: {user_data.get('skills', '')}
    Target Role: {job_description[:200]}
    
    List measurable achievements with bullet points:
    """
    
    enhanced_data['ai_achievements'] = generate_content_with_huggingface(achievements_prompt, 200)
    
    return enhanced_data

# =============================================================================
# MAIN STREAMLIT APPLICATION
# =============================================================================

# Load CSS
try:
    with open("style.css") as f:
        st.markdown('<style>' + f.read() + '</style>', unsafe_allow_html=True)
except FileNotFoundError:
    st.markdown("""
    <style>
    .center-logo { text-align: center; }
    .stButton > button { width: 100%; }
    .download-btn { 
        background: linear-gradient(90deg, #36609B, #4C8449);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 25px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
session_keys = ['clicked_btn', 'logged_in', 'name', 'username', 'user_data', 'resume_data', 'job_description']
for key in session_keys:
    if key not in st.session_state:
        st.session_state[key] = None if key in ['name', 'username', 'user_data', 'resume_data', 'job_description'] else False

# Load users
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

with open("users.json", "r") as f:
    users = json.load(f)

# =============================================================================
# LOGIN/SIGNUP INTERFACE
# =============================================================================

if not st.session_state.get('logged_in', False):
    fcol1, scol2 = st.columns([1, 1])
    
    with fcol1: 
        st.markdown('<div class="center-logo">', unsafe_allow_html=True)
        try:
            st.image("ask.jpg", use_container_width=True)
        except:
            st.markdown("### 🤖 ASK.AI")
        st.markdown('</div>', unsafe_allow_html=True)

    with scol2:
        st.title("ASK.AI Resume Builder")
        st.markdown("*Create ATS-friendly resumes with AI*")

        col1, col2 = st.columns(2)
        with col1:
            if st.button('🔑 Sign in', key='sign-inbtn'):
                st.session_state.clicked_btn = 'signin'
        with col2:
            if st.button('📝 Sign up', key='sign-upbtn'):
                st.session_state.clicked_btn = 'signup'

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.session_state.clicked_btn == "signup":
            if st.button("Create Account", key='create-btn'):
                if not username or not password:
                    st.error("Please enter both username and password")
                elif username in users:
                    st.error("Username already exists")
                else:
                    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                    users[username] = hashed.decode()
                    with open("users.json", "w") as f:
                        json.dump(users, f)
                    st.success("Account created! Please sign in.")

        elif st.session_state.clicked_btn == "signin":
            if st.button("Login", key='log-inbtn'):
                if not username or not password:
                    st.error("Please enter both username and password")
                elif username in users and bcrypt.checkpw(password.encode(), users[username].encode()):
                    st.success(f"Welcome {username}!")
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")

# =============================================================================
# MAIN APPLICATION INTERFACE
# =============================================================================

else:
    # Header with logout
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🚀 AI Resume Builder")
        st.markdown(f"*Welcome back, {st.session_state.get('username', 'User')}!*")
    with col2:
        if st.button("🚪 Logout"):
            for key in session_keys:
                st.session_state[key] = False if key == 'logged_in' else None
            st.rerun()

    # Step 1: Resume Data Input
    st.header("📄 Step 1: Resume Information")
    
    input_method = st.radio("Choose input method:", ["✍️ Manual Entry", "📁 Upload Resume File"], horizontal=True)
    
    user_data = {}
    
    if input_method == "✍️ Manual Entry":
        with st.form("manual_entry"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name *", placeholder="John Smith")
                role = st.text_input("Target Role *", placeholder="Software Developer")
                skills = st.text_area("Skills (comma separated) *", 
                                    placeholder="Python, JavaScript, React, SQL, AWS")
            
            with col2:
                experience = st.text_area("Professional Experience *", 
                                        placeholder="5+ years of experience in software development...")
                education = st.text_area("Education", 
                                        placeholder="Bachelor's in Computer Science, XYZ University")
                
            submitted = st.form_submit_button("✅ Save Resume Data")
            
            if submitted:
                if name and role and skills and experience:
                    user_data = {
                        'name': name,
                        'role': role,
                        'skills': skills,
                        'experience': experience,
                        'education': education
                    }
                    st.session_state.user_data = user_data
                    st.success("✅ Resume data saved successfully!")
                else:
                    st.error("Please fill in all required fields (*)")
    
    else:  # File Upload
        uploaded_file = st.file_uploader("Upload your resume (PDF/DOCX)", 
                                       type=["pdf", "docx"],
                                       help="Upload your existing resume to extract information")
        
        if uploaded_file:
            with st.spinner("📖 Extracting information from your resume..."):
                if uploaded_file.type == "application/pdf":
                    extracted_text = extract_text_from_pdf(uploaded_file)
                else:
                    extracted_text = extract_text_from_docx(uploaded_file)
                
                if extracted_text:
                    # Parse the extracted content
                    parsed_data = parse_resume_content(extracted_text)
                    
                    # Allow user to edit extracted data
                    st.subheader("📝 Review and Edit Extracted Information")
                    
                    with st.form("edit_extracted"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            name = st.text_input("Full Name", value=parsed_data.get('name', ''))
                            role = st.text_input("Target Role", value=parsed_data.get('role', ''))
                            skills = st.text_area("Skills", value=parsed_data.get('skills', ''))
                        
                        with col2:
                            experience = st.text_area("Experience", value=parsed_data.get('experience', ''))
                            education = st.text_area("Education", value=parsed_data.get('education', ''))
                        
                        if st.form_submit_button("✅ Confirm Resume Data"):
                            user_data = {
                                'name': name,
                                'role': role, 
                                'skills': skills,
                                'experience': experience,
                                'education': education
                            }
                            st.session_state.user_data = user_data
                            st.success("✅ Resume data confirmed!")
                else:
                    st.error("Could not extract text from the file. Please try manual entry.")
    
    # Show current resume data if available
    if st.session_state.user_data:
        st.info("✅ Resume data loaded successfully!")
    
    # Step 2: Job Description
    st.header("💼 Step 2: Target Job Description")
    
    jd_method = st.radio("Job description input:", ["✍️ Type/Paste", "📁 Upload JD File"], horizontal=True)
    
    job_description = ""
    
    if jd_method == "📁 Upload JD File":
        jd_file = st.file_uploader("Upload Job Description (PDF/DOCX)", 
                                  type=["pdf", "docx"],
                                  key="jd_upload")
        
        if jd_file:
            with st.spinner("📖 Reading job description..."):
                if jd_file.type == "application/pdf":
                    job_description = extract_text_from_pdf(jd_file)
                else:
                    job_description = extract_text_from_docx(jd_file)
                
                st.success("✅ Job description uploaded!")
    
    # Text area for job description (for typing or showing uploaded content)
    job_description = st.text_area(
        "Job Description",
        value=job_description,
        height=200,
        placeholder="Paste the job description here or upload a file above...",
        help="The AI will tailor your resume based on this job description"
    )
    
    if job_description:
        st.session_state.job_description = job_description
        st.success("📋 Job description ready!")
    
    # Step 3: Resume Generation
    st.header("🤖 Step 3: Generate AI-Enhanced Resume")
    
    if st.session_state.user_data and job_description:
        
        # Template and color selection
        col1, col2 = st.columns(2)
        
        with col1:
            color_theme = st.selectbox(
                "🎨 Choose Color Theme:",
                ["Professional Blue", "Corporate Black", "Modern Green", "Creative Purple", "Executive Navy"]
            )
        
        with col2:
            template_style = st.selectbox(
                "📋 Template Style:",
                ["Modern ATS", "Executive", "Creative", "Technical"]
            )
        
        # Generation buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Generate AI Resume", type="primary"):
                with st.spinner("🤖 AI is creating your tailored resume..."):
                    
                    # Enhance resume with AI
                    enhanced_data = enhance_resume_with_ai(st.session_state.user_data, job_description)
                    st.session_state.resume_data = enhanced_data
                    
                    # Show preview
                    st.success("✅ AI-enhanced resume generated!")
                    
                    # Display AI-generated content
                    st.subheader("🤖 AI-Generated Content Preview")
                    
                    with st.expander("📝 Professional Summary", expanded=True):
                        st.write(enhanced_data.get('ai_summary', 'Not generated'))
                    
                    with st.expander("🎯 Enhanced Experience"):
                        st.write(enhanced_data.get('ai_experience_enhancement', 'Using original'))
                    
                    with st.expander("🏆 Key Achievements"):
                        st.write(enhanced_data.get('ai_achievements', 'Not generated'))
        
        with col2:
            if st.session_state.resume_data:
                # Create resume builder instance
                resume_builder = ATSResumeBuilder()
                
                # Generate DOCX
                if st.button("📄 Download DOCX", type="secondary"):
                    with st.spinner("📝 Creating DOCX resume..."):
                        doc = resume_builder.create_ats_resume(
                            st.session_state.resume_data, 
                            color_theme, 
                            template_style
                        )
                        
                        # Save to bytes
                        docx_buffer = BytesIO()
                        doc.save(docx_buffer)
                        docx_buffer.seek(0)
                        
                        # Create download button
                        st.download_button(
                            label="📥 Download Resume.docx",
                            data=docx_buffer.getvalue(),
                            file_name=f"{st.session_state.resume_data.get('name', 'Resume').replace(' ', '_')}_ATS_Resume.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                
                # Generate PDF
                if st.button("📄 Download PDF", type="secondary"):
                    with st.spinner("📝 Creating PDF resume..."):
                        pdf_buffer = create_pdf_resume(st.session_state.resume_data, color_theme)
                        
                        st.download_button(
                            label="📥 Download Resume.pdf",
                            data=pdf_buffer.getvalue(),
                            file_name=f"{st.session_state.resume_data.get('name', 'Resume').replace(' ', '_')}_ATS_Resume.pdf",
                            mime="application/pdf"
                        )
    
    else:
        st.warning("⚠️ Please complete Steps 1 and 2 before generating your resume.")
        
        if not st.session_state.user_data:
            st.error("❌ Resume information missing")
        if not job_description:
            st.error("❌ Job description missing")
    
    # Step 4: Resume Preview (if generated)
    if st.session_state.resume_data:
        st.header("👀 Step 4: Resume Preview")
        
        preview_data = st.session_state.resume_data
        
        # Create preview container
        with st.container():
            st.markdown("### 📋 Your ATS-Optimized Resume Preview")
            
            # Header preview
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; border: 2px solid #ddd; border-radius: 10px; margin: 10px 0;'>
                <h2 style='color: #36609B; margin: 0;'>{preview_data.get('name', '').upper()}</h2>
                <h4 style='color: #666; margin: 5px 0;'>{preview_data.get('role', '')}</h4>
                <p style='margin: 5px 0;'>📧 professional@email.com | 📞 (555) 123-4567</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Content sections
            sections = [
                ("PROFESSIONAL SUMMARY", preview_data.get('ai_summary', '')),
                ("CORE COMPETENCIES", preview_data.get('skills', '')),
                ("PROFESSIONAL EXPERIENCE", preview_data.get('ai_experience_enhancement', preview_data.get('experience', ''))),
                ("EDUCATION", preview_data.get('education', '')),
                ("KEY ACHIEVEMENTS", preview_data.get('ai_achievements', ''))
            ]
            
            for title, content in sections:
                if content:
                    st.markdown(f"""
                    <div style='margin: 15px 0;'>
                        <h4 style='color: #36609B; border-bottom: 2px solid #36609B; padding-bottom: 5px;'>{title}</h4>
                        <p style='margin: 10px 0; line-height: 1.6;'>{content}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Sidebar with tips and info
    with st.sidebar:
        st.markdown("### 💡 Resume Tips")
        st.info("""
        **ATS-Friendly Features:**
        - ✅ Clean formatting
        - ✅ Standard fonts
        - ✅ Keyword optimization
        - ✅ Proper section headers
        - ✅ No complex layouts
        """)
        
        st.markdown("### 🤖 AI Features")
        st.success("""
        **AI Enhancements:**
        - 📝 Tailored summaries
        - 🎯 Job-specific keywords
        - 🏆 Achievement generation
        - 📊 Content optimization
        - ⚡ Lightning fast
        """)
        
        st.markdown("### 🎨 Customization")
        st.warning("""
        **Available Options:**
        - 5 color themes
        - Multiple templates
        - DOCX & PDF formats
        - Mobile responsive
        - Professional layouts
        """)
        
        if st.session_state.resume_data:
            st.markdown("### 📊 Resume Stats")
            data = st.session_state.resume_data
            
            # Calculate some basic stats
            word_count = len(data.get('ai_summary', '').split()) + len(data.get('experience', '').split())
            skill_count = len([s.strip() for s in data.get('skills', '').split(',') if s.strip()])
            
            st.metric("Total Words", word_count)
            st.metric("Skills Listed", skill_count)
            st.metric("Sections", len([s for s in [data.get('ai_summary'), data.get('skills'), data.get('experience'), data.get('education')] if s]))
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <h4>🚀 ASK.AI Resume Builder</h4>
        <p>Create professional, ATS-friendly resumes with AI assistance</p>
        <p><strong>Features:</strong> AI Content Generation • ATS Optimization • Multiple Formats • Custom Themes</p>
    </div>
    """, unsafe_allow_html=True)