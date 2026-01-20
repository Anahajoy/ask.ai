import streamlit as st
import streamlit.components.v1 as components
import json
import os
from templates.templateconfig import SYSTEM_TEMPLATES, ATS_COLORS, load_css_template
from utils import (
    generate_generic_html, get_user_resume, get_score_color, render_skills_section,
    get_score_label, ai_ats_score, analyze_and_improve_resume,render_generic_section,
    should_regenerate_resume, generate_enhanced_resume, 
    save_and_improve, add_new_item,generate_and_switch,render_basic_details
)

# Page config
st.set_page_config(
    page_title="Resume Creator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session states
if 'selected_template' not in st.session_state:
    st.session_state.selected_template = None
if 'template_preview_html' not in st.session_state:
    st.session_state.template_preview_html = None
if 'template_preview_css' not in st.session_state:
    st.session_state.template_preview_css = None
if 'show_template_selector' not in st.session_state:
    st.session_state.show_template_selector = True
if 'show_visual_editor' not in st.session_state:
    st.session_state.show_visual_editor = False
if 'enhanced_resume' not in st.session_state:
    st.session_state.enhanced_resume = None
if 'final_resume_data' not in st.session_state:
    st.session_state.final_resume_data = None
if 'editor_content' not in st.session_state:
    st.session_state.editor_content = ""
if 'ats_result' not in st.session_state:
    st.session_state.ats_result = {}
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'current_edit_section' not in st.session_state:
    st.session_state.current_edit_section = None

# Get user data
if 'logged_in_user' not in st.session_state:
    st.warning("Please login first!")
    st.switch_page("app.py")

email = st.session_state.logged_in_user
user_resume = st.session_state.get("final_resume_data") or get_user_resume(email)

# Orange and White Theme CSS
st.markdown("""
<style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"], 
    [data-testid="stSidebarNav"] {display: none;}
    #MainMenu, footer, header, button[kind="header"] {visibility: hidden;}
    
    /* Orange and White Theme */
    :root {
        --primary-orange: #FF6B35;
        --primary-orange-light: #FF8B5C;
        --primary-orange-dark: #D45A2B;
        --white: #FFFFFF;
        --light-gray: #F8F9FA;
        --medium-gray: #E9ECEF;
        --dark-gray: #495057;
        --text-dark: #212529;
        --success-green: #28A745;
    }
    
    .stApp {
        background: var(--white) !important;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Template Gallery - Orange Theme */
    .template-header {
        margin-bottom: 1.5rem;
    }
    
    .template-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--text-dark);
        margin-bottom: 0.3rem;
    }
    
    .template-subtitle {
        font-size: 1rem;
        color: var(--dark-gray);
        margin-bottom: 1.5rem;
    }
    
    .template-card {
        background: var(--white);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.1);
        transition: all 0.3s ease;
        border: 1px solid var(--medium-gray);
        height: 100%;
        cursor: pointer;
        margin-bottom: 1rem;
    }
    
    .template-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(255, 107, 53, 0.2);
        border-color: var(--primary-orange);
    }
    
    .create-blank-card {
        background: var(--white);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.1);
        transition: all 0.3s ease;
        border: 2px dashed var(--primary-orange);
        height: 380px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        margin-bottom: 1rem;
    }
    
    .create-blank-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(255, 107, 53, 0.2);
        border-color: var(--primary-orange-dark);
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.05) 0%, rgba(255, 107, 53, 0.02) 100%);
    }
    
    .plus-icon {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--primary-orange) 0%, var(--primary-orange-light) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        color: var(--white);
        margin-bottom: 1rem;
    }
    
    .template-preview {
        width: 100%;
        height: 200px;
        background: linear-gradient(135deg, var(--light-gray) 0%, var(--medium-gray) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        overflow: hidden;
    }
    
    .template-badge {
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        background: var(--primary-orange);
        color: var(--white);
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    
    /* Visual Editor Container */
    .visual-editor-container {
        width: 100%;
        height: calc(100vh - 120px);
        border: none;
        overflow: hidden;
        margin-top: 0.5rem;
        background: var(--light-gray);
        border-radius: 12px;
        border: 1px solid var(--medium-gray);
    }
    
    /* Resume Tools Panel - Orange Theme */
    .resume-tools-panel {
        background: var(--white);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.1);
        height: fit-content;
        margin-top: 0;
        border: 1px solid var(--medium-gray);
    }
    
    .ats-score-display {
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.1) 0%, rgba(255, 107, 53, 0.05) 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 107, 53, 0.2);
    }
    
    .ats-score-number {
        font-size: 3rem;
        font-weight: 800;
        color: var(--primary-orange);
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .ats-score-label {
        font-size: 1.1rem;
        color: var(--text-dark);
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    
    .ats-score-subtext {
        font-size: 0.9rem;
        color: var(--dark-gray);
    }
    
    /* Button Styling - Orange Theme */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin-bottom: 0.8rem !important;
        font-size: 0.95rem !important;
        padding: 0.8rem 1rem !important;
        border: none !important;
    }
    
    .primary-button {
        background: linear-gradient(135deg, var(--primary-orange) 0%, var(--primary-orange-light) 100%) !important;
        color: var(--white) !important;
    }
    
    .primary-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255, 107, 53, 0.3) !important;
        background: linear-gradient(135deg, var(--primary-orange-dark) 0%, var(--primary-orange) 100%) !important;
    }
    
    .secondary-button {
        background: var(--white) !important;
        color: var(--primary-orange) !important;
        border: 2px solid var(--primary-orange) !important;
    }
    
    .secondary-button:hover {
        background: var(--primary-orange) !important;
        color: var(--white) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.2) !important;
    }
    
    /* Header styling */
    .editor-header {
        background: var(--white);
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(255, 107, 53, 0.1);
        border: 1px solid var(--medium-gray);
    }
    
    /* Inline Editor */
    .inline-editor {
        position: absolute;
        background: var(--white);
        border: 2px solid var(--primary-orange);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        min-width: 300px;
        max-width: 500px;
    }
    
    .inline-editor-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--medium-gray);
    }
    
    .inline-editor-title {
        font-weight: 600;
        color: var(--primary-orange);
        font-size: 1.1rem;
    }
    
    .inline-editor-close {
        background: none;
        border: none;
        color: var(--dark-gray);
        cursor: pointer;
        font-size: 1.2rem;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
    }
    
    .inline-editor-close:hover {
        background: var(--light-gray);
        color: var(--primary-orange);
    }
    
    /* Template grid */
    [data-testid="column"] {
        padding: 0.5rem;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: rgba(255, 107, 53, 0.05) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 107, 53, 0.1) !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: rgba(255, 107, 53, 0.1) !important;
    }
    
    /* Hide empty sections */
    .empty-section {
        display: none !important;
    }
    
    /* Make text areas look better */
    .stTextArea textarea {
        border-radius: 8px !important;
        border: 2px solid var(--medium-gray) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary-orange) !important;
        box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1) !important;
    }
    
    .stTextInput input {
        border-radius: 8px !important;
        border: 2px solid var(--medium-gray) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus {
        border-color: var(--primary-orange) !important;
        box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

def get_standard_keys():
    """Return set of standard resume keys."""
    return {
        "name", "email", "phone", "location", "url", "summary", "job_title",
        "education", "experience", "skills", "projects", "certifications", 
        "total_experience_count", "input_method", "achievements", "languages"
    }

def clean_resume_data(data):
    """Clean and prepare resume data for templates."""
    if not data:
        return {}
    
    cleaned = data.copy()
    
    # Remove empty values
    for key in list(cleaned.keys()):
        if cleaned[key] is None or cleaned[key] == "":
            del cleaned[key]
        elif isinstance(cleaned[key], list) and len(cleaned[key]) == 0:
            del cleaned[key]
        elif isinstance(cleaned[key], dict) and len(cleaned[key]) == 0:
            del cleaned[key]
    
    # Ensure required sections exist
    if 'experience' not in cleaned:
        cleaned['experience'] = []
    if 'education' not in cleaned:
        cleaned['education'] = []
    if 'skills' not in cleaned:
        cleaned['skills'] = []
    
    return cleaned

def generate_resume_for_template():
    """Generate enhanced resume data for template."""
    if st.session_state.enhanced_resume:
        return clean_resume_data(st.session_state.enhanced_resume)
    
    if should_regenerate_resume() and not st.session_state.get('edit_toggle', False):
        generate_enhanced_resume()
    
    resume_data = st.session_state.get('enhanced_resume') or user_resume
    resume_data = clean_resume_data(resume_data)
    
    # Calculate ATS score if job description exists
    jd_data = st.session_state.get('job_description')
    if resume_data and jd_data:
        try:
            st.session_state.ats_result = ai_ats_score(resume_data, jd_data)
        except Exception as e:
            st.error(f"Error analyzing resume: {str(e)}")
            st.session_state.ats_result = {}
    
    return resume_data

def save_custom_sections():
    """Save custom section edits."""
    if 'enhanced_resume' in st.session_state:
        data = st.session_state.enhanced_resume
        standard_keys = get_standard_keys()
        
        for key in list(data.keys()):
            if key not in standard_keys and isinstance(data.get(key), str):
                edit_key = f"edit_custom_{key}"
                if edit_key in st.session_state:
                    data[key] = st.session_state[edit_key].strip()
        
        st.session_state.enhanced_resume = data

# IN-PLACE EDITING VISUAL EDITOR HTML
VISUAL_EDITOR_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #F8F9FA;
            overflow: hidden;
            height: 100vh;
            width: 100vw;
        }

        .header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 50px;
            background: white;
            border-bottom: 2px solid #E9ECEF;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 1.5rem;
            z-index: 1000;
            box-shadow: 0 2px 8px rgba(255, 107, 53, 0.1);
        }

        .header-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #212529;
        }

        .close-btn {
            background: #FF6B35;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }

        .close-btn:hover {
            background: #D45A2B;
            transform: translateY(-1px);
        }

        .canvas-container {
            position: fixed;
            left: 0;
            right: 0;
            top: 50px;
            bottom: 0;
            background: #F8F9FA;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            overflow: auto;
            padding: 1rem;
        }

        .canvas {
            width: 8.5in;
            min-height: 11in;
            background: white;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: visible !important;
            margin: 0 auto;
        }

        /* Make elements editable */
        .editable {
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
        }

        .editable:hover {
            background: rgba(255, 107, 53, 0.05) !important;
            outline: 2px dashed rgba(255, 107, 53, 0.3) !important;
            outline-offset: 2px;
        }

        .editable:active {
            background: rgba(255, 107, 53, 0.1) !important;
        }

        .editable-section {
            border-radius: 4px;
            padding: 4px;
        }

        /* Inline Editor Modal */
        .inline-editor-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 10000;
            justify-content: center;
            align-items: center;
        }

        .inline-editor-content {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
            border: 2px solid #FF6B35;
        }

        .inline-editor-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #F8F9FA;
        }

        .inline-editor-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: #FF6B35;
        }

        .inline-editor-close {
            background: none;
            border: none;
            font-size: 1.5rem;
            color: #495057;
            cursor: pointer;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            transition: all 0.2s ease;
        }

        .inline-editor-close:hover {
            background: #F8F9FA;
            color: #FF6B35;
        }

        .inline-editor-body {
            margin-bottom: 1.5rem;
        }

        .inline-editor-textarea {
            width: 100%;
            min-height: 200px;
            padding: 1rem;
            border: 2px solid #E9ECEF;
            border-radius: 8px;
            font-family: inherit;
            font-size: 1rem;
            line-height: 1.5;
            resize: vertical;
            transition: all 0.3s ease;
        }

        .inline-editor-textarea:focus {
            outline: none;
            border-color: #FF6B35;
            box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
        }

        .inline-editor-actions {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
        }

        .inline-editor-btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .inline-editor-save {
            background: linear-gradient(135deg, #FF6B35 0%, #FF8B5C 100%);
            color: white;
        }

        .inline-editor-save:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 107, 53, 0.3);
        }

        .inline-editor-cancel {
            background: #F8F9FA;
            color: #495057;
            border: 2px solid #E9ECEF;
        }

        .inline-editor-cancel:hover {
            background: #E9ECEF;
        }

        /* Remove any hidden elements */
        [style*="display: none"],
        [style*="visibility: hidden"],
        .empty-section {
            display: none !important;
        }
        
        /* Ensure content is visible */
        .ats-page {
            width: 100% !important;
            height: auto !important;
            min-height: 11in !important;
            padding: 1in !important;
            overflow: visible !important;
        }
        
        /* Make sure all content shows */
        div, p, h1, h2, h3, h4, li, span {
            overflow: visible !important;
            white-space: normal !important;
        }
    </style>
    <style id="template-css"></style>
</head>
<body>
    <div class="header">
        <div class="header-title">📄 Resume Visual Editor - <span id="template-title">Template Preview</span></div>
        <button class="close-btn" onclick="window.parent.postMessage({type: 'close_editor'}, '*')">← Back</button>
    </div>

    <!-- Inline Editor Modal -->
    <div class="inline-editor-modal" id="inlineEditor">
        <div class="inline-editor-content">
            <div class="inline-editor-header">
                <div class="inline-editor-title" id="editorTitle">Edit Section</div>
                <button class="inline-editor-close" onclick="closeEditor()">×</button>
            </div>
            <div class="inline-editor-body">
                <textarea class="inline-editor-textarea" id="editorTextarea" placeholder="Enter your content here..."></textarea>
            </div>
            <div class="inline-editor-actions">
                <button class="inline-editor-btn inline-editor-cancel" onclick="closeEditor()">Cancel</button>
                <button class="inline-editor-btn inline-editor-save" onclick="saveContent()">Save Changes</button>
            </div>
        </div>
    </div>

    <div class="canvas-container">
        <div class="canvas" id="canvas">
            <!-- Template content will be injected here -->
        </div>
    </div>

    <script>
        let currentEditElement = null;
        let currentEditPath = '';
        
        // Load template content
        function loadTemplateContent() {
            const templateData = window.templateContent || '';
            const templateCss = window.templateCss || '';
            
            if (templateData) {
                document.getElementById('canvas').innerHTML = templateData;
            }
            
            if (templateCss) {
                document.getElementById('template-css').innerHTML = templateCss;
            }
            
            if (window.templateName) {
                document.getElementById('template-title').textContent = window.templateName;
            }
            
            // Make all text elements editable
            setTimeout(() => {
                makeElementsEditable();
                removeEmptySections();
            }, 100);
        }
        
        function makeElementsEditable() {
            // Select elements that should be editable
            const editableSelectors = [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'p', 'span', 'li', 'div[class*="name"]',
                'div[class*="title"]', 'div[class*="summary"]',
                'div[class*="description"]', 'div[class*="skill"]'
            ];
            
            editableSelectors.forEach(selector => {
                document.querySelectorAll(`#canvas ${selector}`).forEach(el => {
                    if (el.textContent.trim() && !el.hasAttribute('data-non-editable')) {
                        el.classList.add('editable', 'editable-section');
                        el.setAttribute('title', 'Click to edit');
                        el.addEventListener('click', (e) => {
                            e.stopPropagation();
                            openEditor(el);
                        });
                    }
                });
            });
        }
        
        function removeEmptySections() {
            // Remove completely empty sections
            const sections = document.querySelectorAll('#canvas > div, #canvas section, #canvas .section');
            sections.forEach(section => {
                if (section.textContent.trim() === '' || section.innerHTML.trim() === '<br>') {
                    section.style.display = 'none';
                }
            });
        }
        
        function openEditor(element) {
            currentEditElement = element;
            currentEditPath = getElementPath(element);
            
            // Get current content
            let content = element.textContent || '';
            
            // For list items, get all items in the list
            if (element.tagName === 'LI') {
                const list = element.closest('ul, ol');
                if (list) {
                    content = Array.from(list.querySelectorAll('li')).map(li => li.textContent).join('\\n');
                    currentEditElement = list;
                }
            }
            
            document.getElementById('editorTitle').textContent = 'Edit Content';
            document.getElementById('editorTextarea').value = content;
            document.getElementById('inlineEditor').style.display = 'flex';
        }
        
        function closeEditor() {
            document.getElementById('inlineEditor').style.display = 'none';
            currentEditElement = null;
            currentEditPath = '';
        }
        
        function saveContent() {
            if (!currentEditElement) return;
            
            const newContent = document.getElementById('editorTextarea').value.trim();
            
            if (newContent) {
                if (currentEditElement.tagName === 'LI' || currentEditElement.tagName === 'UL' || currentEditElement.tagName === 'OL') {
                    // Handle list content
                    const list = currentEditElement.tagName === 'LI' ? currentEditElement.closest('ul, ol') : currentEditElement;
                    if (list) {
                        const items = newContent.split('\\n').filter(item => item.trim());
                        list.innerHTML = items.map(item => `<li>${item.trim()}</li>`).join('');
                        
                        // Make new items editable
                        list.querySelectorAll('li').forEach(li => {
                            li.classList.add('editable', 'editable-section');
                            li.setAttribute('title', 'Click to edit');
                            li.addEventListener('click', (e) => {
                                e.stopPropagation();
                                openEditor(li);
                            });
                        });
                    }
                } else {
                    // Handle regular text content
                    currentEditElement.textContent = newContent;
                }
                
                // Notify parent about the change
                window.parent.postMessage({
                    type: 'content_updated',
                    path: currentEditPath,
                    content: newContent
                }, '*');
            }
            
            closeEditor();
        }
        
        function getElementPath(element) {
            const path = [];
            let current = element;
            
            while (current && current !== document.body) {
                let selector = current.tagName.toLowerCase();
                
                if (current.id) {
                    selector += `#${current.id}`;
                } else if (current.className && typeof current.className === 'string') {
                    const classes = current.className.split(' ').filter(c => c).join('.');
                    if (classes) selector += `.${classes}`;
                }
                
                path.unshift(selector);
                current = current.parentElement;
            }
            
            return path.join(' > ');
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', loadTemplateContent);
        
        // Also load on window load
        window.addEventListener('load', loadTemplateContent);
        
        // Listen for messages from parent
        window.addEventListener('message', (event) => {
            if (event.data.type === 'update_content') {
                document.getElementById('canvas').innerHTML = event.data.content;
                const styleEl = document.getElementById('template-css');
                if (styleEl && event.data.css) {
                    styleEl.innerHTML = event.data.css;
                }
                setTimeout(() => {
                    makeElementsEditable();
                    removeEmptySections();
                }, 100);
            }
            
            if (event.data.type === 'refresh_editor') {
                loadTemplateContent();
            }
        });
        
        // Close editor on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeEditor();
            }
        });
        
        // Close editor when clicking outside
        document.getElementById('inlineEditor').addEventListener('click', (e) => {
            if (e.target.classList.contains('inline-editor-modal')) {
                closeEditor();
            }
        });
    </script>
</body>
</html>
"""

def show_template_selector():
    """Show template selection gallery."""
    st.markdown("""
    <div class="template-header">
        <h1 class="template-title">Resume Templates</h1>
        <p class="template-subtitle">Choose from our professionally designed templates or create your own</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search bar
    search_term = st.text_input("🔍 Search templates...", 
                               placeholder="Search templates...",
                               label_visibility="collapsed",
                               key="template_search")
    
    # Template categories
    template_categories = {
        "Minimalist (ATS Best)": "ATS",
        "Horizontal Line": "Modern",
        "Bold Title Accent": "Bold",
        "Date Below": "Clean",
        "Section Box Header": "Boxed",
        "Times New Roman Classic": "Classic",
        "Sophisticated Minimal": "Minimal",
        "Clean Look": "Modern",
        "Elegant": "Elegant",
        "Modern Minimal": "Minimal",
        "Two Coloumn": "Layout",
    }
    
    # Filter templates
    filtered_templates = {
        name: config for name, config in SYSTEM_TEMPLATES.items()
        if search_term.lower() in name.lower() or 
        search_term.lower() in template_categories.get(name, "").lower()
    }
    
    # Display templates in grid
    templates_list = list(filtered_templates.items())
    
    for i in range(0, len(templates_list), 3):
        cols = st.columns(3)
        row_templates = templates_list[i:i + 3]
        
        for col_idx, (template_name, template_config) in enumerate(row_templates):
            with cols[col_idx]:
                template_type = template_categories.get(template_name, "Template")
                
                # Template card
                st.markdown(f"""
                <div class="template-card">
                    <div class="template-preview">
                        <div style="width: 85%; height: 90%; background: white; 
                             border-radius: 4px; padding: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <div style="width: 60%; height: 10px; background: #FF6B35; 
                                 border-radius: 2px; margin-bottom: 0.5rem;"></div>
                            <div style="width: 40%; height: 6px; background: #E9ECEF; 
                                 border-radius: 2px; margin-bottom: 1rem;"></div>
                            <div style="width: 80%; height: 6px; background: #E9ECEF; 
                                 border-radius: 2px; margin-bottom: 0.5rem;"></div>
                        </div>
                        <div class="template-badge">{template_type}</div>
                    </div>
                    <div style="padding: 1rem;">
                        <div style="font-size: 1rem; font-weight: 600; color: #212529; 
                             margin-bottom: 0.5rem;">📄 {template_name}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Use Template", 
                           key=f"use_{template_name}",
                           type="primary",
                           use_container_width=True):
                    # Generate resume data
                    resume_data = generate_resume_for_template()
                    
                    # Generate template HTML
                    selected_color = ATS_COLORS["Professional Blue (Default)"]
                    css = load_css_template(
                        template_config['css_template'],
                        selected_color
                    )
                    html_content = template_config['html_generator'](resume_data)
                    
                    # Create full HTML
                    full_html = f"""
                    <div class="ats-page">
                        {html_content}
                    </div>
                    """
                    
                    # Store in session state
                    st.session_state.selected_template = template_name
                    st.session_state.template_preview_html = full_html
                    st.session_state.template_preview_css = css
                    st.session_state.final_resume_data = resume_data
                    st.session_state.show_template_selector = False
                    st.session_state.show_visual_editor = True
                    st.rerun()

def show_visual_editor_with_tools():
    """Show the visual editor with resume tools on the side."""
    if not st.session_state.selected_template:
        st.session_state.show_template_selector = True
        st.session_state.show_visual_editor = False
        st.rerun()
        return
    
    # Header
    st.markdown('<div class="editor-header">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back to Templates", type="secondary", use_container_width=True):
            st.session_state.show_template_selector = True
            st.session_state.show_visual_editor = False
            st.rerun()
    with col2:
        st.markdown(f"<h3 style='margin: 0; color: #212529;'>📄 Resume Visual Editor - {st.session_state.selected_template}</h3>", 
                   unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main layout: Visual Editor on left (75%), Resume Tools on right (25%)
    editor_col, tools_col = st.columns([7.5, 2.5], gap="medium")
    
    with editor_col:
        # Visual Editor Container
        st.markdown('<div class="visual-editor-container">', unsafe_allow_html=True)
        
        # Get resume data
        resume_data = st.session_state.final_resume_data or {}
        
        # Prepare HTML content
        html_content = st.session_state.template_preview_html or ""
        css_content = st.session_state.template_preview_css or ""
        
        # Inject data into editor
        editor_html_with_data = VISUAL_EDITOR_HTML
        
        inject_script = f"""
        <script>
            window.templateContent = `{html_content}`;
            window.templateCss = `{css_content}`;
            window.templateName = `{st.session_state.selected_template}`;
        </script>
        """
        
        editor_html_with_data = editor_html_with_data.replace('<body>', f'<body>\n{inject_script}')
        
        # Display the visual editor
        components.html(editor_html_with_data, height=700, scrolling=False)
        
        # Listen for content updates from iframe
        if 'content_updated' in st.session_state:
            if st.session_state.content_updated:
                # Here you would process the updated content
                # For now, just clear the flag
                st.session_state.content_updated = False
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tools_col:
        with st.container():
            RESUME_ORDER = ["education", "experience", "skills", "projects", "certifications", "achievements"]

            # st.markdown("<div class='panel-container left-panel'>", unsafe_allow_html=True)
            st.title("Resume Tools 🛠️")
            loading_placeholder = st.empty()
            # ========= PREMIUM ATS GAUGE ==========
            ats_data = st.session_state.get('ats_result', {})

            if ats_data and ats_data.get("overall_score", 0) > 0:
                score = ats_data.get("overall_score", 0)  # Changed from "score" to "overall_score"
                label = get_score_label(score)
                color = get_score_color(score)
                
                st.markdown(f"### ATS Score: {score}/100")
                st.markdown(f"**{label}**", unsafe_allow_html=True)
                st.markdown(f"""
                <div style="
                    text-align:center;
                    padding:15px;
                    margin-bottom:18px;
                    background:white;
                    border-radius:16px;
                    box-shadow:0 4px 12px rgba(0,0,0,0.08);
                    border:1px solid #e8e8e8;
                ">
                    <div style="position: relative; width:140px; height:140px; margin:auto;">
                        <svg width="140" height="140">
                            <circle cx="70" cy="70" r="60" stroke="#f0f0f0" stroke-width="12" fill="none"/>
                            <circle cx="70" cy="70" r="60"
                                stroke="{color}" stroke-width="12" fill="none"
                                stroke-linecap="round"
                                stroke-dasharray="{round(score*3.6)}, 360"
                                transform="rotate(-90 70 70)"
                            />
                            <text x="70" y="78" text-anchor="middle" font-size="28" font-weight="700" fill="#333">{score}%</text>
                        </svg>
                    </div>
                    <div style="font-size:15px; margin-top:8px; font-weight:600; color:#333;">
                        {label}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ================= Keyword Table Expander ====================
                with st.expander("🔎 View ATS Keyword Analysis"):
                    st.markdown("### 🟢 Matched Keywords")
                    # Changed from matched_keywords to matched_skills
                    matched = ats_data.get("matched_skills", [])
                    if matched:
                        st.write(", ".join(matched))
                    else:
                        st.write("None")
                    
                    st.markdown("### 🔴 Missing Keywords")
                    # Changed from missing_keywords to missing_skills
                    missing = ats_data.get("missing_skills", [])
                    if missing:
                        st.write(", ".join(missing))
                    else:
                        st.write("None")


            if st.button("✨ **Save & Auto-Improve**", type="primary", width='stretch'):
                loading_placeholder.markdown("""
                    <div id="overlay-loader">
                        <div class="loader-spinner"></div>
                        <p>Performing auto-improvement...</p>
                    </div>
                    <style>
                        #overlay-loader {
                            position: fixed;
                            top: 0;
                            left: 0;
                            width: 100vw;
                            height: 100vh;
                            background: rgba(255, 255, 255, 0.95);
                            backdrop-filter: blur(6px);
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                            align-items: center;
                            z-index: 9999;
                            font-size: 1.2rem;
                            font-weight: 500;
                        }

                        .loader-spinner {
                            border: 5px solid rgba(232, 117, 50, 0.2);
                            border-top: 5px solid #e87532;
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
                            color: #1f2937;
                            font-size: 1.1rem;
                            letter-spacing: 0.5px;
                        }
                    </style>
                    """, unsafe_allow_html=True)

                save_custom_sections()
                save_and_improve()
                loading_placeholder.empty()
                
            if st.button("📄 **GENERATE RESUME**", type="primary", width='stretch'):
                loading_placeholder.markdown("""
                    <div id="overlay-loader">
                        <div class="loader-spinner"></div>
                        <p>Generating your resume...</p>
                    </div>
                    <style>
                        #overlay-loader {
                            position: fixed;
                            top: 0;
                            left: 0;
                            width: 100vw;
                            height: 100vh;
                            background: rgba(255, 255, 255, 0.95);
                            backdrop-filter: blur(6px);
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                            align-items: center;
                            z-index: 9999;
                            font-size: 1.2rem;
                            font-weight: 500;
                        }

                        .loader-spinner {
                            border: 5px solid rgba(232, 117, 50, 0.2);
                            border-top: 5px solid #e87532;
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
                            color: #1f2937;
                            font-size: 1.1rem;
                            letter-spacing: 0.5px;
                        }
                    </style>
                    """, unsafe_allow_html=True)

                generate_and_switch()
                loading_placeholder.empty()

            st.markdown("---")

            is_edit_mode = st.checkbox("⚙️ **Enable Edit Mode**", key='edit_toggle')

            if not st.session_state.get('edit_toggle', False):
                st.info("⚠️ Enable Edit Mode to add new items.\n\nFor saving newly added content, disable Edit Mode after making changes.")
            else:
                st.markdown("---")
                st.subheader("➕ Add New Section Items")
                st.button(
                    "Add New Experience",
                    on_click=add_new_item,
                    args=('experience', {
                        "position": "New Job Title",
                        "company": "New Company",
                        "start_date": "2025-01-01",
                        "end_date": "2025-12-31",
                        "description": ["New responsibility 1."]
                    }),
                    type="secondary"
                )
                st.button(
                    "Add New Education",
                    on_click=add_new_item,
                    args=('education', {
                        "institution": "New University",
                        "degree": "New Degree",
                        "start_date": "2025-01-01",
                        "end_date": "2025-12-31"
                    }),
                    type="secondary"
                )
                st.button(
                    "Add New Certification",
                    on_click=add_new_item,
                    args=('certifications', {
                        "name": "New Certification Name",
                        "issuer": "Issuing Body",
                        "completed_date": "2025-01-01"
                    }),
                    type="secondary"
                )
                st.button(
                    "Add New Project",
                    on_click=add_new_item,
                    args=('projects', {
                        "name": "New Project Title",
                        "description": ["Project detail"]
                    }),
                    type="secondary"
                )
            st.markdown("</div>", unsafe_allow_html=True)
           
    # RIGHT PANEL - Live Preview
    # with col3:
      
        with st.container():
            # st.markdown("<div class='panel-container middle-panel'>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align:center;color:#6b7280;margin-bottom:1.5rem;'>✏️ Content Editor</h3>", unsafe_allow_html=True)
            
            # Render basic details
            render_basic_details(resume_data, is_edit=is_edit_mode)

            # Track rendered keys to avoid duplicates
            rendered_keys = set()
            standard_keys = get_standard_keys()
            
            # Render standard sections in order
            for key in RESUME_ORDER:
                if key in resume_data and resume_data[key]:
                    rendered_keys.add(key)
                    if key == "skills":
                        render_skills_section(resume_data, is_edit=is_edit_mode)
                    else:
                        render_generic_section(key, resume_data[key], is_edit=is_edit_mode)

            # Render other list-type sections that aren't in the standard order
            for key, value in resume_data.items():
                if key not in rendered_keys and key not in standard_keys:
                    if isinstance(value, list) and value:
                        rendered_keys.add(key)
                        render_generic_section(key, value, is_edit=is_edit_mode)

            # Render Custom Text Sections (Languages, Licenses, etc.)
            for key, value in resume_data.items():
                if key not in rendered_keys and key not in standard_keys and isinstance(value, str):
                    st.markdown(f"<div class='resume-section'>", unsafe_allow_html=True)
                    st.markdown(f"<h3 class='custom-section-header'>{key}</h3>", unsafe_allow_html=True)

                    if is_edit_mode:
                        new_val = st.text_area(
                            f"Edit {key}",
                            value=value.strip(),
                            key=f"edit_custom_{key}",
                            height=200,
                            help="Edit your custom section content here"
                        )

                        resume_data[key] = new_val.strip()
                        st.session_state['enhanced_resume'] = resume_data
                        
                        if st.button(f"🗑️ Delete '{key}' Section", key=f"delete_{key}", type="secondary"):
                            del resume_data[key]
                            st.session_state['enhanced_resume'] = resume_data
                            st.rerun()
                    else:
                        st.markdown(
                            f"<div class='custom-section-content'>{value.strip()}</div>",
                            unsafe_allow_html=True
                        )

                    st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("⬇️ **Download PDF**", type="secondary", use_container_width=True):
            st.info("PDF download functionality coming soon!")
        
        if st.button("📄 **Download HTML**", type="secondary", use_container_width=True):
            # Create downloadable HTML
            download_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Resume - {st.session_state.selected_template}</title>
                <style>{css_content}</style>
            </head>
            <body style="margin: 0; padding: 0; background: #fff;">
                <div style="width: 8.5in; min-height: 11in; margin: 0 auto; padding: 1in; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                    {html_content}
                </div>
            </body>
            </html>
            """
            
            st.download_button(
                label="⬇️ Download HTML",
                data=download_html,
                file_name=f"resume_{st.session_state.selected_template.replace(' ', '_')}.html",
                mime="text/html",
                use_container_width=True,
                type="secondary"
            )
        
        st.markdown("---")
        
        # Quick ATS Analysis
        with st.expander("🔍 ATS Analysis", expanded=False):
            if ats_data and score > 0:
                matched = ats_data.get("matched_skills", []) or ats_data.get("matched_keywords", []) or []
                missing = ats_data.get("missing_skills", []) or ats_data.get("missing_keywords", []) or []
                
                if matched:
                    st.markdown("**✅ Matched Keywords:**")
                    for i, keyword in enumerate(matched[:3]):
                        st.markdown(f"- {keyword}")
                    if len(matched) > 3:
                        st.markdown(f"*... and {len(matched) - 3} more*")
                else:
                    st.markdown("*No matched keywords*")
                
                if missing:
                    st.markdown("**❌ Missing Keywords:**")
                    for i, keyword in enumerate(missing[:3]):
                        st.markdown(f"- {keyword}")
                    if len(missing) > 3:
                        st.markdown(f"*... and {len(missing) - 3} more*")
                else:
                    st.markdown("*No missing keywords*")
            else:
                st.markdown("*No ATS analysis available*")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Main app flow
def main():
    # Check if user needs to be redirected to resume creation first
    if not user_resume or len(user_resume) == 0:
        st.warning("Please create a resume first!")
        if st.button("Go to Resume Creator"):
            st.switch_page("pages/main.py")
        return
    
    # Determine what to show based on session state
    if st.session_state.show_visual_editor:
        show_visual_editor_with_tools()
    else:
        show_template_selector()

if __name__ == "__main__":
    main()