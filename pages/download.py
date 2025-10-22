import streamlit as st
import base64
from datetime import datetime
from pathlib import Path
import hashlib
import re
from streamlit_extras.switch_page_button import switch_page
from io import BytesIO
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import streamlit as st
import json, os
from datetime import datetime
from utils import load_user_templates,save_user_templates

# Define the preferred display order for sections
RESUME_ORDER = ["summary", "experience", "education", "skills", "projects", "certifications", "achievements", "publications", "awards"]

# ATS-friendly color palette
ATS_COLORS = {
    "Professional Blue (Default)": "#1F497D",
    "Corporate Gray": "#4D4D4D",
    "Deep Burgundy": "#800020",
    "Navy Blue": "#000080"
}



if 'uploaded_templates' not in st.session_state:
    st.session_state.uploaded_templates = {}

if "selected_template_config" not in st.session_state:
    st.session_state.selected_template_config = None

def format_section_title(key):
    """Converts keys like 'certifications' to 'Certifications'."""
    title = key.replace('_', ' ').replace('Skills', ' Skills').replace('summary', 'Summary')
    return ' '.join(word.capitalize() for word in title.split())

# --- Template CSS & HTML Generation Functions (Same as before) ---
def get_css_minimalist(color):
    return f"""
        <style>
        @page {{ margin: 0.3in; size: letter; }}
        body {{ margin: 0; padding: 0; }}
        .ats-page {{ 
            font-family: 'Arial', sans-serif; 
            font-size: 9pt; 
            color: #333; 
            max-width: 100%; 
            margin: 0; 
            padding: 0.3in;
            line-height: 1.2; 
        }}
        .ats-section-title {{ 
            font-size: 10.5pt; 
            font-weight: bold; 
            color: #000;
            border-bottom: 1px solid #333;
            padding-bottom: 1px;
            margin-top: 8px;
            margin-bottom: 3px;
        }}
        .ats-item-header {{ 
            margin-top: 2px; 
            margin-bottom: 0; 
            line-height: 1.1; 
            font-size: 9.5pt;
            display: flex;
            justify-content: space-between;
            align-items: flex-start; 
        }}
        .ats-item-title-group {{ 
            flex-grow: 1; 
            padding-right: 8px; 
        }}
        .ats-item-title {{ 
            font-weight: bold; 
            color: #000; 
            display: inline; 
        }} 
        .ats-item-subtitle {{ 
            font-style: italic; 
            color: #555; 
            display: inline; 
            font-size: 9pt;
        }}
        .ats-item-duration {{ 
            font-size: 9pt; 
            color: #666; 
            white-space: nowrap;
            flex-shrink: 0;
            text-align: right; 
        }}
        .ats-bullet-list {{ 
            list-style-type: disc; 
            margin-left: 18px; 
            padding-left: 0; 
            margin-top: 2px; 
            margin-bottom: 3px; 
        }}
        .ats-bullet-list li {{ 
            margin-bottom: 0px; 
            line-height: 1.2; 
        }}
        .ats-header {{ margin-bottom: 8px; }}
        .ats-header h1 {{ margin: 0; padding: 0; font-size: 16pt; }}
        .ats-job-title-header {{ font-size: 11pt; margin: 2px 0 5px 0; }}
        .ats-contact {{ font-size: 9pt; margin-top: 3px; }}
        .ats-skills-group {{ margin-bottom: 3px; }}
        p {{ margin: 5px 0; }}
        </style>
    """

def get_css_horizontal(color):
    return f"""
        <style>
        @page {{ margin: 0.3in; size: letter; }}
        body {{ margin: 0; padding: 0; }}
        .ats-page {{ 
            font-family: 'Times New Roman', serif; 
            font-size: 9.5pt; 
            color: #333; 
            max-width: 100%; 
            margin: 0; 
            padding: 0.3in;
            line-height: 1.15; 
        }}
        .ats-header {{ text-align: center; padding-bottom: 3px; margin-bottom: 8px; }}
        .ats-header h1 {{ color: #000; font-size: 16pt; margin: 0; text-transform: uppercase; }}
        .ats-job-title-header {{ font-size: 11pt; margin: 2px 0 5px 0; }}
        .ats-contact {{ font-size: 8.5pt; margin-top: 3px; }}
        .ats-contact span:not(:last-child)::after {{ content: " | "; white-space: pre; }}
        .ats-section-title {{ 
            color: {color}; 
            font-size: 10.5pt; 
            font-weight: bold; 
            text-transform: uppercase; 
            border-bottom: 2px solid {color}; 
            padding-bottom: 1px; 
            margin-top: 8px; 
            margin-bottom: 3px; 
        }}
        .ats-item-header {{ margin-top: 2px; margin-bottom: 1px; line-height: 1.1; display: flex; justify-content: space-between; }}
        .ats-item-title {{ font-weight: bold; color: #000; flex-grow: 1; }}
        .ats-item-duration {{ font-size: 9pt; white-space: nowrap; color: #666; }}
        .ats-item-subtitle {{ font-style: italic; color: #555; display: block; font-size: 9pt; }}
        .ats-bullet-list {{ list-style-type: circle; margin-left: 20px; padding-left: 0; margin-top: 2px; margin-bottom: 3px; }}
        .ats-bullet-list li {{ margin-bottom: 0px; line-height: 1.2; }}
        .ats-skills-group {{ margin-bottom: 3px; }}
        p {{ margin: 5px 0; }}
        </style>
    """

def get_css_bold_title(color):
    return f"""
        <style>
        @page {{ margin: 0.3in; size: letter; }}
        body {{ margin: 0; padding: 0; }}
        .ats-page {{ 
            font-family: 'Verdana', sans-serif; 
            font-size: 8.5pt; 
            color: #333; 
            max-width: 100%; 
            margin: 0; 
            padding: 0.3in;
            line-height: 1.2; 
        }}
        .ats-header {{ text-align: center; padding-bottom: 3px; margin-bottom: 8px; }}
        .ats-header h1 {{ color: {color}; font-size: 15pt; margin: 0; text-transform: uppercase; }}
        .ats-job-title-header {{ 
            font-size: 11pt; 
            color: #555; 
            margin: 2px 0 5px 0; 
            text-align: center;
        }}
        .ats-contact {{ font-size: 8pt; margin-top: 3px; }}
        .ats-contact span:not(:last-child)::after {{ content: " • "; white-space: pre; }}
        .ats-section-title {{ 
            color: #000; 
            font-size: 10pt; 
            font-weight: 900; 
            text-transform: uppercase; 
            margin-top: 8px; 
            margin-bottom: 3px; 
            border-bottom: 1.5px solid #CCC; 
        }}
        .ats-item-header {{ 
            margin-top: 2px; 
            margin-bottom: 0px; 
            line-height: 1.1;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}
        .ats-item-title-group {{
            flex-grow: 1;
            padding-right: 8px;
        }}
        .ats-item-title {{ font-weight: bold; color: {color}; display: inline; }}
        .ats-item-subtitle {{ font-style: italic; color: #555; display: inline; font-size: 8.5pt; }}
        .ats-item-duration {{ 
            font-size: 8pt; 
            color: #666;
            white-space: nowrap;
            flex-shrink: 0;
            text-align: right;
        }}
        .ats-bullet-list {{ list-style-type: square; margin-left: 18px; padding-left: 0; margin-top: 2px; margin-bottom: 3px; }}
        .ats-bullet-list li {{ margin-bottom: 0px; line-height: 1.2; }}
        .ats-skills-group {{ margin-bottom: 3px; }}
        p {{ margin: 5px 0; }}
        </style>
    """

def get_css_date_below(color):
    return f"""
        <style>
        @page {{ margin: 0.3in; size: letter; }}
        body {{ margin: 0; padding: 0; }}
        .ats-page {{ 
            font-family: 'Calibri', sans-serif; 
            font-size: 9pt; 
            color: #333; 
            max-width: 100%; 
            margin: 0; 
            padding: 0.3in;
            line-height: 1.2; 
        }}
        .ats-header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 3px; margin-bottom: 8px; }}
        .ats-header h1 {{ color: #000; font-size: 17pt; margin: 0; }}
        .ats-job-title-header {{ font-size: 11pt; margin: 2px 0 5px 0; }}
        .ats-contact {{ font-size: 8.5pt; margin-top: 3px; }}
        .ats-contact span:not(:last-child)::after {{ content: " | "; white-space: pre; }}
        .ats-section-title {{ 
            color: {color}; 
            font-size: 10.5pt; 
            font-weight: bold; 
            text-transform: uppercase; 
            letter-spacing: 0.5px; 
            margin-top: 8px; 
            margin-bottom: 3px; 
        }}
        .ats-item-header {{ margin-top: 2px; margin-bottom: 1px; line-height: 1.1; }}
        .ats-item-title {{ font-weight: bold; color: #000; display: inline-block; }}
        .ats-item-duration {{ font-size: 8.5pt; color: {color}; display: block; font-style: italic; margin-top: 1px; }}
        .ats-item-subtitle {{ font-style: italic; color: #555; display: inline-block; margin-left: 5px; font-size: 8.5pt; }}
        .ats-bullet-list {{ list-style-type: disc; margin-left: 18px; padding-left: 0; margin-top: 2px; margin-bottom: 3px; }}
        .ats-bullet-list li {{ margin-bottom: 0px; line-height: 1.2; }}
        .ats-skills-group {{ margin-bottom: 3px; }}
        p {{ margin: 5px 0; }}
        </style>
    """

def get_css_section_box(color):
    return f"""
        <style>
        @page {{ margin: 0.3in; size: letter; }}
        body {{ margin: 0; padding: 0; }}
        .ats-page {{ 
            font-family: 'Arial', sans-serif; 
            font-size: 9pt; 
            color: #333; 
            max-width: 100%; 
            margin: 0; 
            padding: 0.3in;
            line-height: 1.2; 
        }}
        .ats-header {{ text-align: center; padding-bottom: 3px; margin-bottom: 8px; }}
        .ats-header h1 {{ color: {color}; font-size: 16pt; margin: 0; text-transform: uppercase; }}
        .ats-job-title-header {{ font-size: 11pt; margin: 2px 0 5px 0; }}
        .ats-contact {{ font-size: 8.5pt; margin-top: 3px; }}
        .ats-contact span:not(:last-child)::after {{ content: " | "; white-space: pre; }}
        .ats-section-title {{ 
            background-color: {color}; 
            color: white; 
            font-size: 10pt; 
            font-weight: bold; 
            text-transform: uppercase; 
            padding: 2px 8px; 
            margin-top: 8px; 
            margin-bottom: 3px; 
        }}
        .ats-item-header {{ margin-top: 2px; margin-bottom: 1px; line-height: 1.1; display: flex; justify-content: space-between; }}
        .ats-item-title {{ font-weight: bold; color: #000; flex-grow: 1; }}
        .ats-item-duration {{ font-size: 8.5pt; white-space: nowrap; color: #666; }}
        .ats-item-subtitle {{ font-style: italic; color: #555; display: block; font-size: 8.5pt; }}
        .ats-bullet-list {{ list-style-type: disc; margin-left: 18px; padding-left: 0; margin-top: 2px; margin-bottom: 3px; }}
        .ats-bullet-list li {{ margin-bottom: 0px; line-height: 1.2; }}
        .ats-skills-group {{ margin-bottom: 3px; }}
        p {{ margin: 5px 0; }}
        </style>
    """

def get_css_classic(color):
    return f"""
        <style>
        @page {{ margin: 0.3in; size: letter; }}
        body {{ margin: 0; padding: 0; }}
        .ats-page {{ 
            font-family: 'Times New Roman', serif; 
            font-size: 10pt; 
            color: #000; 
            max-width: 100%; 
            margin: 0; 
            padding: 0.3in;
            line-height: 1.15; 
        }}
        .ats-header {{ text-align: center; padding-bottom: 3px; margin-bottom: 8px; }}
        .ats-header h1 {{ color: #000; font-size: 18pt; margin: 0; }}
        .ats-job-title-header {{ font-size: 11pt; margin: 2px 0 5px 0; }}
        .ats-contact {{ font-size: 9pt; margin-top: 3px; }}
        .ats-contact span:not(:last-child)::after {{ content: " | "; white-space: pre; }}
        .ats-section-title {{ 
            color: #000; 
            font-size: 10.5pt; 
            font-weight: bold; 
            text-transform: uppercase; 
            border-bottom: 1px solid #000; 
            padding-bottom: 1px; 
            margin-top: 8px; 
            margin-bottom: 3px; 
        }}
        .ats-item-header {{ margin-top: 2px; margin-bottom: 1px; line-height: 1.1; display: flex; justify-content: space-between; }}
        .ats-item-title {{ font-weight: bold; color: {color}; flex-grow: 1; }}
        .ats-item-duration {{ font-size: 9.5pt; white-space: nowrap; color: #000; }}
        .ats-item-subtitle {{ font-style: italic; color: #000; display: block; font-size: 9.5pt; }}
        .ats-bullet-list {{ list-style-type: disc; margin-left: 22px; padding-left: 0; margin-top: 2px; margin-bottom: 3px; }}
        .ats-bullet-list li {{ margin-bottom: 0px; line-height: 1.2; }}
        .ats-skills-group {{ margin-bottom: 3px; }}
        p {{ margin: 5px 0; }}
        </style>
    """

from datetime import datetime

def format_year_only(date_str):
    """Return only the year from a date string. If already a year, return as-is."""
    if not date_str:
        return ""
    date_str = str(date_str).strip()
    if len(date_str) == 4 and date_str.isdigit(): 
        return date_str
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y")
    except:
        return date_str  

def generate_generic_html(data, date_placement='right'):
    """Generates clean HTML content based on resume data, showing only years for all dates."""
    if not data: 
        return ""

    # Header
    job_title_for_header = data.get('job_title', '')
    contacts = [data.get('phone'), data.get('email'), data.get('location')]
    contacts_html = " | ".join([c for c in contacts if c])

    html = f'<div class="ats-header">'
    html += f'<h1>{data.get("name", "NAME MISSING")}</h1>'
    if job_title_for_header:
        html += f'<div class="ats-job-title-header">{job_title_for_header}</div>'
    if contacts_html:
        html += f'<div class="ats-contact">{contacts_html}</div>'
    html += '</div>'

    for key in RESUME_ORDER:
        section_data = data.get(key)
        if not section_data or (isinstance(section_data, list) and not section_data):
            continue

        title = format_section_title(key)
        html += f'<div class="ats-section-title">{title}</div>'

        # Summary
        if key == 'summary' and isinstance(section_data, str) and section_data.strip():
            html += f'<p style="margin-top:0;margin-bottom:5px;">{section_data}</p>'

        # Skills
        elif key == 'skills' and isinstance(section_data, dict):
            for skill_type, skill_list in section_data.items():
                if skill_list:
                    html += f'<div class="ats-skills-group"><strong>{format_section_title(skill_type)}:</strong> {", ".join(skill_list)}</div>'

        elif isinstance(section_data, list):
            for item in section_data:
                if isinstance(item, str) and item.strip():
                    html += f'<ul class="ats-bullet-list"><li>{item}</li></ul>'
                    continue

                if not isinstance(item, dict):
                    continue

      
                title_keys = ['title', 'name', 'degree', 'certificate_name', 'course', 'position']
                subtitle_keys = ['company', 'institution', 'issuer', 'organization', 'provider_name', 'university']
                duration_keys = ['duration', 'date', 'period', 'completed_date', 'start_date', 'end_date']

                main_title = next((item[k] for k in title_keys if k in item and item[k]), '')
                subtitle = next((item[k] for k in subtitle_keys if k in item and item[k] != main_title and item[k]), '')

              
                start = format_year_only(item.get('start_date', ''))
                end = format_year_only(item.get('end_date', ''))

                if start or end:
                    duration = f"{start} - {end}" if start and end else start or end
                else:
                    duration = next((format_year_only(item[k]) for k in duration_keys if k in item and item[k]), '')

             
                if not main_title and not subtitle and not duration:
                    continue

                html += '<div class="ats-item-header">'
                if main_title or subtitle:
                    html += '<div class="ats-item-title-group">'
                    if main_title:
                        html += f'<span class="ats-item-title">{main_title}'
                        if subtitle:
                            html += f' <span class="ats-item-subtitle">{subtitle}</span>'
                        html += '</span>'
                    html += '</div>'
                if duration:
                    html += f'<div class="ats-item-duration">{duration}</div>'
                html += '</div>'

                # Description / Achievements
                description_list_raw = item.get('description') or item.get('achievement') or item.get('details')
                if description_list_raw:
                    if isinstance(description_list_raw, str):
                        description_list = [description_list_raw]
                    elif isinstance(description_list_raw, list):
                        description_list = description_list_raw
                    else:
                        description_list = None

                    if description_list:
                        bullet_html = "".join([f"<li>{line}</li>" for line in description_list if line.strip()])
                        if bullet_html:
                            html += f'<ul class="ats-bullet-list">{bullet_html}</ul>'

    return html


SYSTEM_TEMPLATES = {
    "Minimalist (ATS Best)": {
        "html_generator": lambda data: generate_generic_html(data, date_placement='right'),
        "css_generator": get_css_minimalist,
    },
    "Horizontal Line": {
        "html_generator": lambda data: generate_generic_html(data, date_placement='right'),
        "css_generator": get_css_horizontal,
    },
    "Bold Title Accent": {
        "html_generator": lambda data: generate_generic_html(data, date_placement='right'),
        "css_generator": get_css_bold_title,
    },
    "Date Below": {
        "html_generator": lambda data: generate_generic_html(data, date_placement='below'),
        "css_generator": get_css_date_below,
    },
    "Section Box Header": {
        "html_generator": lambda data: generate_generic_html(data, date_placement='right'),
        "css_generator": get_css_section_box,
    },
    "Times New Roman Classic": {
        "html_generator": lambda data: generate_generic_html(data, date_placement='right'),
        "css_generator": get_css_classic,
    }
}

def parse_uploaded_file(uploaded_file):
    """Parse uploaded resume file and extract template styling."""
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_type == 'html':
            content = uploaded_file.read().decode('utf-8')
            return extract_template_from_html(content)
        elif file_type in ['doc', 'docx']:
            st.warning("DOC/DOCX parsing coming soon. Using default template for now.")
            return None
        elif file_type == 'pdf':
            st.warning("PDF parsing coming soon. Using default template for now.")
            return None
        elif file_type in ['ppt', 'pptx']:
            st.warning("PPT/PPTX parsing coming soon. Using default template for now.")
            return None
        else:
            st.error(f"Unsupported file type: {file_type}")
            return None
    except Exception as e:
        st.error(f"Error parsing file: {str(e)}")
        return None

def extract_template_from_html(html_content):
    """Extract CSS and structure from uploaded HTML."""

    css_match = re.search(r'<style[^>]*>(.*?)</style>', html_content, re.DOTALL)
    css = css_match.group(1) if css_match else ""
    
    template_id = hashlib.md5(html_content.encode()).hexdigest()[:8]
    
    return {
        'id': template_id,
        'name': f'Uploaded Template {template_id}',
        'css': css,
        'html': html_content,
        'uploaded_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def generate_html_content(data, color, template_generator, css_generator):
    """Generates the full HTML document and returns base64-encoded string."""
    css = css_generator(color)
    html_content = template_generator(data)
    
    title = f"{data.get('name', 'Resume')}"
    full_document_html = f"<html><head><meta charset='UTF-8'>{css}<title>{title}</title></head><body><div class='ats-page'>{html_content}</div></body></html>" 
    return base64.b64encode(full_document_html.encode('utf-8')).decode()

def get_html_download_link(data, color, template_config, filename_suffix=""):
    """Generates a download link for the styled HTML file."""
    if 'html_generator' in template_config and 'css_generator' in template_config:
        b64_data = generate_html_content(
            data, 
            color, 
            template_config['html_generator'], 
            template_config['css_generator']
        )
    else:
        # For uploaded templates
        css = template_config.get('css', '')
        html_body = generate_generic_html(data)
        full_html = f"<html><head><meta charset='UTF-8'><style>{css}</style></head><body><div class='ats-page'>{html_body}</div></body></html>"
        b64_data = base64.b64encode(full_html.encode('utf-8')).decode()
    
    filename = f"Resume_{data.get('name', 'User').replace(' ', '_')}{filename_suffix}.html"
    href = f'<a href="data:text/html;base64,{b64_data}" download="{filename}" style="font-size: 0.95em; text-decoration: none; padding: 10px 15px; background-color: #00FA9A; color: white; border-radius: 5px; display: inline-block; margin-top: 10px; width: 100%; text-align: center;"><strong>⬇️ Download HTML (.html)</strong></a>'
    return href



def generate_doc_html(data):
    """Generate a simple HTML that can be saved as .doc."""
    html = f"""
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
    <head>
        <meta charset='utf-8'>
        <title>Resume</title>
        <style>
            @page {{
                size: 8.5in 11in;
                margin: 0.5in;
            }}
            body {{ 
                font-family: Calibri, Arial, sans-serif; 
                font-size: 10pt; 
                line-height: 1.1; 
                margin: 0;
                padding: 0;
            }}
            h1 {{ font-size: 16pt; margin: 0 0 3pt 0; text-align: center; }}
            h2 {{ 
                font-size: 11pt; 
                margin-top: 8pt; 
                margin-bottom: 3pt; 
                border-bottom: 1px solid black; 
                padding-bottom: 1pt;
            }}
            p {{ margin: 3pt 0; }}
            ul {{ margin: 3pt 0; padding-left: 18pt; }}
            li {{ margin: 1pt 0; }}
            .header {{ text-align: center; margin-bottom: 8pt; }}
            .contact {{ font-size: 9pt; }}
            .job-title {{ font-size: 11pt; margin: 2pt 0; color: #555; }}
            .item-header {{ margin: 2pt 0; }}
            .item-title {{ font-weight: bold; }}
            .item-subtitle {{ font-style: italic; color: #555; }}
            .skills-group {{ margin: 3pt 0; }}
        </style>
    </head>
    <body>
        <div class='header'>
            <h1>{data.get('name', 'NAME MISSING')}</h1>
            <p class='job-title'>{data.get('job_title', '')}</p>
            <p class='contact'>{data.get('phone', '')} | {data.get('email', '')} | {data.get('location', '')}</p>
        </div>
    """
    
    for key in RESUME_ORDER:
        section_data = data.get(key)
        
        if not section_data or (isinstance(section_data, list) and not section_data) or (key == 'summary' and not section_data):
            continue
            
        title = format_section_title(key)
        html += f'<h2>{title}</h2>'
        
        if key == 'summary' and isinstance(section_data, str):
            html += f'<p>{section_data}</p>'
        
        elif key == 'skills' and isinstance(section_data, dict):
            for skill_type, skill_list in section_data.items():
                if skill_list:
                    html += f'<p class="skills-group"><strong>{format_section_title(skill_type)}:</strong> '
                    html += ", ".join(skill_list)
                    html += '</p>'
        
        elif isinstance(section_data, list):
            for item in section_data:
                if isinstance(item, str):
                    html += f'<ul><li>{item}</li></ul>'
                    continue
                
                if not isinstance(item, dict):
                    continue
                
                title_keys = ['title', 'name', 'degree']
                subtitle_keys = ['company', 'institution', 'issuer', 'organization']
                duration_keys = ['duration', 'date', 'period']
                
                main_title = next((item[k] for k in title_keys if k in item and item[k]), '')
                subtitle = next((item[k] for k in subtitle_keys if k in item and item[k] != main_title and item[k]), '')
                duration = next((item[k] for k in duration_keys if k in item and item[k]), '')

                html += f'<p class="item-header"><span class="item-title">{main_title}</span>'
                if subtitle:
                    html += f' <span class="item-subtitle">({subtitle})</span>'
                if duration:
                    html += f' | {duration}'
                html += '</p>'
                
                description_list_raw = item.get('description') or item.get('achievement') or item.get('details') 

                if description_list_raw:
                    if isinstance(description_list_raw, str):
                        description_list = [description_list_raw]
                    elif isinstance(description_list_raw, list):
                        description_list = description_list_raw
                    else:
                        description_list = None
                        
                    if description_list:
                        html += '<ul>'
                        for line in description_list:
                            html += f'<li>{line}</li>'
                        html += '</ul>'

    html += '</body></html>'
    return html

def get_doc_download_link(data, color, template_config, filename_suffix=""):
    """
    Generates a DOC download link using the selected template's HTML/CSS.

    Note: The 'DOC' file generated is an HTML file with a .doc extension and 
    Microsoft Word-specific XML/CSS (like @page rules) added to the beginning, 
    allowing it to open and be formatted correctly in Word.
    """

    if 'html_generator' in template_config and 'css_generator' in template_config:
        css = template_config['css_generator'](color)
        html_body = template_config['html_generator'](data)
    else:
       
        css = template_config.get('css', '')
        html_body = generate_generic_html(data) #
    word_doc_header = f"""
<html xmlns:o='urn:schemas-microsoft-com:office:office'
xmlns:w='urn:schemas-microsoft-com:office:word'
xmlns='http://www.w3.org/TR/REC-html40'>
<head>
    <meta charset='UTF-8'>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data.get('name', 'Resume')}</title>
    <style>
        @page {{ 
            size: 8.5in 11in; 
            margin: 0.5in; 
        }}
        {css}
    </style>
</head>
<body>
    <div class='ats-page'>
        {html_body}
    </div>
</body>
</html>
"""

   
    try:
        b64_data = base64.b64encode(word_doc_header.encode('utf-8')).decode()
    except NameError:
        print("Error: 'base64' module not found. Please import it.")
        return ""

    filename = f"Resume_{data.get('name', 'User').replace(' ', '_')}_Template_DOC{filename_suffix}.doc"

    doc_html = f"""
    <a href="data:application/msword;base64,{b64_data}" download="{filename}"
       style="font-size: 0.95em; text-decoration: none; padding: 10px 15px; 
              background-color: #00FFFF; color: white; border-radius: 5px; 
              display: inline-block; margin-top: 10px; width: 100%; text-align: center;">
        <strong>📄 Download Template DOC (.doc)</strong>
    </a>
    """
    return doc_html


def generate_markdown_text(data):
    """Generates a plain markdown/text version of the resume."""
    text = ""
    
    text += f"{data.get('name', 'NAME MISSING').upper()}\n"
    if data.get('job_title'):
        text += f"{data.get('job_title')}\n"
    contact_parts = [data.get('phone', ''), data.get('email', ''), data.get('location', '')]
    text += " | ".join(filter(None, contact_parts)) + "\n"
    text += "=" * 50 + "\n\n"
    
    for key in RESUME_ORDER:
        section_data = data.get(key)
        
        if not section_data or (isinstance(section_data, list) and not section_data) or (key == 'summary' and not section_data):
            continue
            
        title = format_section_title(key).upper()
        text += f"{title}\n"
        text += "-" * len(title) + "\n"
        
        if key == 'summary' and isinstance(section_data, str):
            text += section_data + "\n\n"

        elif key == 'skills' and isinstance(section_data, dict):
            for skill_type, skill_list in section_data.items():
                if skill_list:
                    text += f"{format_section_title(skill_type)}: "
                    text += ", ".join(skill_list) + "\n"
            text += "\n"
        
        elif isinstance(section_data, list):
            for item in section_data:
                if not isinstance(item, dict):
                    text += f" - {item}\n"
                    continue
                
                title_keys = ['title', 'name', 'degree']
                subtitle_keys = ['company', 'institution', 'issuer']
                duration_keys = ['duration', 'date']
                
                main_title = next((item[k] for k in title_keys if k in item and item[k]), '')
                subtitle = next((item[k] for k in subtitle_keys if k in item and item[k] != main_title and item[k]), '')
                duration = next((item[k] for k in duration_keys if k in item and item[k]), '')

                line = f"{main_title}"
                if subtitle:
                    line += f" ({subtitle})"
                if duration:
                    line += f" | {duration}"
                text += line + "\n"
                
                description_list = item.get('description') or item.get('achievement') or item.get('details')
                if description_list and isinstance(description_list, list):
                    for line in description_list:
                        text += f" - {line}\n"
            text += "\n"

    return text

def get_text_download_link(data, filename_suffix=""):
    """Generates a download link for a plain text file."""
    text_content = generate_markdown_text(data)
    b64_data = base64.b64encode(text_content.encode('utf-8')).decode()
    
    filename = f"Resume_{data.get('name', 'User').replace(' ', '_')}_ATS_Plain_Text{filename_suffix}.txt"
    href = f'<a href="data:text/plain;base64,{b64_data}" download="{filename}" style="font-size: 0.95em; text-decoration: none; padding: 10px 15px; background-color: #40E0D0; color: white; border-radius: 5px; display: inline-block; margin-top: 10px; width: 100%; text-align: center;"><strong>📋 Download Plain Text (.txt)</strong></a>'
    return href

# def generate_pptx_file(data):
#     """Generate a proper PPTX file with resume data."""
#     prs = Presentation()
#     prs.slide_width = Inches(10)
#     prs.slide_height = Inches(7.5)
    
#     # Slide 1: Title slide with header info
#     slide1 = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
    
#     # Add name (title)
#     name_box = slide1.shapes.add_textbox(Inches(0.5), Inches(1), Inches(9), Inches(1))
#     name_frame = name_box.text_frame
#     name_frame.text = data.get('name', 'NAME MISSING')
#     name_para = name_frame.paragraphs[0]
#     name_para.font.size = Pt(44)
#     name_para.font.bold = True
#     name_para.font.color.rgb = RGBColor(31, 73, 125)  # Professional blue
#     name_para.alignment = PP_ALIGN.CENTER
    
#     # Add job title
#     if data.get('job_title'):
#         job_box = slide1.shapes.add_textbox(Inches(0.5), Inches(2), Inches(9), Inches(0.6))
#         job_frame = job_box.text_frame
#         job_frame.text = data.get('job_title', '')
#         job_para = job_frame.paragraphs[0]
#         job_para.font.size = Pt(24)
#         job_para.font.color.rgb = RGBColor(100, 100, 100)
#         job_para.alignment = PP_ALIGN.CENTER
    
#     # Add contact info
#     contact_parts = []
#     if data.get('phone'):
#         contact_parts.append(f"📱 {data.get('phone')}")
#     if data.get('email'):
#         contact_parts.append(f"✉️ {data.get('email')}")
#     if data.get('location'):
#         contact_parts.append(f"📍 {data.get('location')}")
    
#     contact_text = " • ".join(contact_parts)
#     contact_box = slide1.shapes.add_textbox(Inches(0.5), Inches(3), Inches(9), Inches(0.5))
#     contact_frame = contact_box.text_frame
#     contact_frame.text = contact_text
#     contact_para = contact_frame.paragraphs[0]
#     contact_para.font.size = Pt(14)
#     contact_para.alignment = PP_ALIGN.CENTER
    
#     # Add summary if exists
#     if data.get('summary'):
#         summary_box = slide1.shapes.add_textbox(Inches(1), Inches(4), Inches(8), Inches(2.5))
#         summary_frame = summary_box.text_frame
#         summary_frame.word_wrap = True
#         summary_frame.text = data.get('summary')
#         summary_para = summary_frame.paragraphs[0]
#         summary_para.font.size = Pt(14)
#         summary_para.line_spacing = 1.2
    
#     # Process other sections
#     for key in RESUME_ORDER:
#         if key == 'summary':  # Already handled
#             continue
            
#         section_data = data.get(key)
        
#         if not section_data or (isinstance(section_data, list) and not section_data):
#             continue
        
#         # Create new slide for each section
#         slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
        
#         # Section title
#         title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.6))
#         title_frame = title_box.text_frame
#         title_frame.text = format_section_title(key)
#         title_para = title_frame.paragraphs[0]
#         title_para.font.size = Pt(32)
#         title_para.font.bold = True
#         title_para.font.color.rgb = RGBColor(31, 73, 125)
        
#         # Add horizontal line under title
#         line = slide.shapes.add_shape(
#             1,  # Line shape
#             Inches(0.5), Inches(0.95),
#             Inches(9), Inches(0)
#         )
#         line.line.color.rgb = RGBColor(31, 73, 125)
#         line.line.width = Pt(2)
        
#         # Content box
#         content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(9), Inches(5.8))
#         content_frame = content_box.text_frame
#         content_frame.word_wrap = True
        
#         if key == 'skills' and isinstance(section_data, dict):
#             for skill_type, skill_list in section_data.items():
#                 if skill_list:
#                     p = content_frame.add_paragraph()
#                     p.text = f"{format_section_title(skill_type)}: {', '.join(skill_list)}"
#                     p.font.size = Pt(14)
#                     p.space_after = Pt(8)
#                     p.level = 0
                    
#                     # Make skill type bold
#                     run = p.runs[0]
#                     run.font.bold = True
        
#         elif isinstance(section_data, list):
#             for item in section_data:
#                 if isinstance(item, str):
#                     p = content_frame.add_paragraph()
#                     p.text = item
#                     p.font.size = Pt(14)
#                     p.space_after = Pt(6)
#                     p.level = 0
#                     continue
                
#                 if not isinstance(item, dict):
#                     continue
                
#                 # Extract item details
#                 title_keys = ['title', 'name', 'degree']
#                 subtitle_keys = ['company', 'institution', 'issuer', 'organization']
#                 duration_keys = ['duration', 'date', 'period']
                
#                 main_title = next((item[k] for k in title_keys if k in item and item[k]), '')
#                 subtitle = next((item[k] for k in subtitle_keys if k in item and item[k] != main_title and item[k]), '')
#                 duration = next((item[k] for k in duration_keys if k in item and item[k]), '')
                
#                 # Add title paragraph
#                 p = content_frame.add_paragraph()
#                 title_text = main_title
#                 if subtitle:
#                     title_text += f" • {subtitle}"
#                 if duration:
#                     title_text += f" • {duration}"
#                 p.text = title_text
#                 p.font.size = Pt(16)
#                 p.font.bold = True
#                 p.font.color.rgb = RGBColor(31, 73, 125)
#                 p.space_after = Pt(4)
#                 p.level = 0
                
#                 # Add description bullets
#                 description_list_raw = item.get('description') or item.get('achievement') or item.get('details')
                
#                 if description_list_raw:
#                     if isinstance(description_list_raw, str):
#                         description_list = [description_list_raw]
#                     elif isinstance(description_list_raw, list):
#                         description_list = description_list_raw
#                     else:
#                         description_list = None
                    
#                     if description_list:
#                         for desc in description_list:
#                             p = content_frame.add_paragraph()
#                             p.text = desc
#                             p.font.size = Pt(13)
#                             p.space_after = Pt(3)
#                             p.level = 1  # Indent for bullet points
                
#                 # Add spacing between items
#                 p = content_frame.add_paragraph()
#                 p.space_after = Pt(8)
    
#     # Save to BytesIO
#     pptx_io = BytesIO()
#     prs.save(pptx_io)
#     pptx_io.seek(0)
#     return pptx_io.getvalue()

# def get_pptx_download_link(data, filename_suffix=""):
#     """Generates a download link for a PPTX file."""
#     try:
#         pptx_data = generate_pptx_file(data)
#         b64_data = base64.b64encode(pptx_data).decode()
        
#         filename = f"Resume_{data.get('name', 'User').replace(' ', '_')}{filename_suffix}.pptx"
#         href = f'<a href="data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,{b64_data}" download="{filename}" style="font-size: 0.95em; text-decoration: none; padding: 10px 15px; background-color: #00CED1; color: white; border-radius: 5px; display: inline-block; margin-top: 10px; width: 100%; text-align: center;"><strong>📊 Download PPTX (.pptx)</strong></a>'
#         return href
#     except Exception as e:
#         st.error(f"Error generating PPTX: {str(e)}")
#         return f'<p style="color: red;">Error generating PPTX file. Please try again.</p>'

# --- Main Application ---

def app_download():
    st.set_page_config(layout="wide", page_title="Download Resume")
    ACCENT_COLOR = "#6ea8fe" # Softer, bright blue

    st.markdown(f"""
    <style>
        /* ============================
        🌟 Dark Blue-Green Theme
        ============================ */
        :root {{
            --primary-color: #00BFFF; /* Deep sky blue */
            --secondary-color: #000000; /* Black background */
            --accent-color: #00FF7F; /* Spring green */
            --accent-light: #66FFB2; /* Lighter green-blue */
            --accent-ice: #0a0a0a; /* Dark icy color for borders */
            --text-dark: #FFFFFF; /* Text on dark background */
            --text-light: #FFFFFF;
            --card-bg: rgba(20, 20, 20, 0.9); /* Dark card background */
            --card-border: rgba(0, 255, 127, 0.5); /* Soft green border */
            --soft-shadow: rgba(0, 255, 127, 0.15); /* Soft shadow for depth */
            --button-gradient: -webkit-linear-gradient(45deg, #00BFFF, #00FF7F);
        }}

        /* HIDE NAVIGATION */
        [data-testid="stSidebarNav"] {{
            display: none !important;
        }}

        .stApp {{
            background-color: var(--secondary-color);
            background-attachment: fixed;
            min-height: 100vh;
            color: var(--text-dark);
            font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }}

        /* PREVIEW IFRAME BACKGROUND FIX */
        iframe {{
            background: linear-gradient(135deg, #e6f9ff 0%, #f0fff4 100%) !important;
            border-radius: 12px;
            border: 2px solid var(--accent-color);
            box-shadow: 0 8px 25px var(--soft-shadow);
        }}
        /* TEMPLATE CARDS */
        .template-card {{
            background: var(--card-bg);
            backdrop-filter: blur(5px);
            border: 1px solid var(--card-border);
            padding: 25px;
            border-radius: 18px;
            box-shadow: 0 8px 25px var(--soft-shadow);
            margin-bottom: 25px;
            transition: all 0.3s ease;
            text-align: center;
            min-height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            color: var(--text-dark);
        }}

        .template-card:hover {{
            box-shadow: 0 12px 35px rgba(0, 255, 127, 0.4);
            transform: translateY(-5px);
            border-color: var(--accent-color);
        }}

        /* HEADINGS */
        h1, h2, h3, h4 {{
            color: var(--primary-color);
            font-weight: 700;
        }}

        .template-card h3 {{
            color: var(--primary-color);
            font-weight: 600;
            margin-bottom: 5px;
            font-size: 1.4em;
        }}

        /* BADGE */
        .saved-badge {{
            background: var(--accent-light);
            color: var(--primary-color);
            padding: 5px 12px;
            border-radius: 15px;
            font-weight: 700;
            box-shadow: 0 2px 10px rgba(102, 255, 178, 0.5);
        }}

        /* BUTTONS */
        .stButton>button {{
            background: var(--button-gradient);
            color: var(--text-light);
            border: none;
            border-radius: 12px;
            padding: 0.8rem 1.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            box-shadow: 0 5px 18px rgba(0, 255, 127, 0.4);
            transition: all 0.3s ease;
            width: 100%;
            max-width: 280px;
            margin-top: auto;
            margin-left: auto;
            margin-right: auto;
            display: block;
        }}

        .stButton>button:hover {{
            background: -webkit-linear-gradient(45deg, #00FF7F, #00BFFF);
            box-shadow: 0 8px 25px rgba(0, 255, 127, 0.8);
            transform: translateY(-4px) scale(1.02);
            color: var(--text-dark);
        }}

        /* INPUT FIELDS */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {{
            background-color: #1a1a1a; /* Dark input background */
            color: var(--text-light);
            border: 1px solid var(--accent-ice);
            border-radius: 10px;
            padding: 14px;
            box-shadow: inset 0 1px 4px rgba(0, 0, 0, 0.2);
        }}

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px rgba(0, 255, 127, 0.4);
        }}
                
                /* ============================
        Dark Sidebar Styling
        ============================ */
        /* Sidebar background */
        [data-testid="stSidebar"] {{
            background-color: #000000 !important; /* Black background */
            color: #FFFFFF; /* White text by default */
            padding: 1rem;
        }}

        /* Sidebar headings, subheaders */
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] .css-1d391kg p {{
            color: #FFFFFF !important;
        }}

        /* Sidebar selectbox and color picker */
        [data-testid="stSidebar"] .stSelectbox, 
        [data-testid="stSidebar"] .stColorPicker {{
            background-color: #1a1a1a !important; /* Dark input background */
            color: #FFFFFF !important; /* White text */
        }}

        /* Sidebar buttons */
        [data-testid="stSidebar"] button {{
            background: linear-gradient(45deg, #00BFFF, #00FF7F);
            color: #FFFFFF;
            border-radius: 10px;
            padding: 10px 15px;
            margin-bottom: 10px;
            font-weight: 600;
            border: none;
            width: 100%;
            transition: all 0.3s ease;
        }}

        [data-testid="stSidebar"] button:hover {{
            background: linear-gradient(45deg, #00FF7F, #00BFFF);
            color: #000000;
            transform: scale(1.02);
        }}

        /* Sidebar horizontal lines */
        [data-testid="stSidebar"] hr {{
            border-top: 1px solid rgba(255, 255, 255, 0.2);
        }}

        /* Sidebar captions */
        [data-testid="stSidebar"] .stCaption {{
            color: #FFFFFF !important;
        }}
                    /* Make selectbox label text white in sidebar */
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] .stSelectbox label {{
            color: #FFFFFF !important;
        }}

        /* Make selectbox options text dark (optional) if using dark dropdown) */
        [data-testid="stSidebar"] .stSelectbox div[role="listbox"] div {{
            color: #000000;
        }}
        


    </style>
""", unsafe_allow_html=True)




    final_data = st.session_state.get('final_resume_data')
    # st.json(final_data)

    if final_data is None:
        st.error("❌ Resume data not found. Please return to the editor to finalize your resume.")
        if st.button("⬅️ Go Back to Editor"):
            switch_page("main")
        return

    if isinstance(final_data, str):
        try:
            final_data = json.loads(final_data)
        except json.JSONDecodeError:
            st.error("❌ Error: Could not parse resume data.")
            if st.button("⬅️ Go Back to Editor"):
                switch_page("main")
            return
            
    if not isinstance(final_data, dict):
        st.error("❌ Resume data is in an unusable format.")
        if st.button("⬅️ Go Back to Editor"):
            switch_page("main")
        return

    st.markdown("""
    <div style="text-align: center;">
        <h1>📄 Resume Template Manager</h1>
        <p style="color: white; font-size: 16px;">
            <b>System Templates • Saved Templates • Upload Custom Templates</b>
        </p>
    </div>
    """, unsafe_allow_html=True)
#     
    tab1, tab3 = st.tabs(["🎨 System Templates", "📤 Upload New Template"])

    # --- TAB 1: SYSTEM TEMPLATES ---
    with tab1:
        st.markdown("### Available System Templates")
        st.caption("Choose from professionally designed ATS-friendly templates")
        
        # Template selection
        cols = st.columns(3)
        for idx, (template_name, template_config) in enumerate(SYSTEM_TEMPLATES.items()):
            with cols[idx % 3]:
                with st.container():
                    st.markdown(f"""
                    <div class="template-card">
                        <h4>{template_name}</h4>
                        <p style="font-size: 0.9em; color: #666;">Click to preview and customize</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Select {template_name}", key=f"sys_template_{idx}", use_container_width=True):
                        st.session_state.selected_template = template_name
                        st.session_state.selected_template_config = template_config
                        st.session_state.template_source = 'system'
                        st.rerun()
        

        if st.session_state.get('selected_template') and st.session_state.get('template_source') == 'system':
            st.markdown("---")
            st.markdown(f"### Preview: {st.session_state.selected_template}")
            template_config = st.session_state.selected_template_config
            color_name = st.selectbox(
                        'Choose Accent Color:',
                        list(ATS_COLORS.keys()),
                        key='sys_color_select'
                    )
            primary_color = ATS_COLORS[color_name]
            css = template_config['css_generator'](primary_color)
            html_content = template_config['html_generator'](final_data)
            
            full_html = f"""
            {css}
            <div class="ats-page">
                {html_content}
            </div>
            """
            
            st.components.v1.html(full_html, height=1000, scrolling=True)
            

    
    # --- TAB 3: UPLOAD NEW TEMPLATE ---
   # --- TAB 3: UPLOAD NEW TEMPLATE ---
    with tab3:
        # st.markdown("## 📤 Upload or Manage Templates")

        # Initialize uploaded_templates early
        if 'uploaded_templates' not in st.session_state:
            st.session_state.uploaded_templates = load_user_templates(st.session_state.logged_in_user)

        # 1️⃣ Load Saved Templates First
        if st.session_state.uploaded_templates:
            st.markdown("### 🗂️ Your Saved Templates")
            cols = st.columns(3)
            for idx, (template_id, template_data) in enumerate(st.session_state.uploaded_templates.items()):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="template-card" style="border:1px solid #ccc; padding:10px; border-radius:10px; background:#fafafa;">
                        <h4>{template_data['name']}</h4>
                        <p style="font-size:0.85em; color:#555;">File: {template_data['original_filename']}</p>
                        <p style="font-size:0.8em; color:#888;">Uploaded: {template_data['uploaded_at']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Use", key=f"use_{template_id}", use_container_width=True):
                            # Clear temp upload config when using a saved template
                            if 'temp_upload_config' in st.session_state:
                                del st.session_state.temp_upload_config
                            
                            st.session_state.selected_template_preview = f"""
                                <style>{template_data['css']}</style>
                                <div class="ats-page">{generate_generic_html(final_data)}</div>
                            """
                            st.session_state.selected_template = template_data['name']
                            st.session_state.selected_template_config = template_data
                            st.session_state.template_source = 'saved'
                            st.session_state.current_upload_id = template_id
                            st.rerun()  # Added rerun

                    with col2:
                        if st.button(f"Delete", key=f"delete_{template_id}", use_container_width=True):
                            # Clear selection if deleting currently selected template
                            if st.session_state.get('current_upload_id') == template_id:
                                st.session_state.pop('selected_template_preview', None)
                                st.session_state.pop('selected_template', None)
                                st.session_state.pop('selected_template_config', None)
                                st.session_state.pop('current_upload_id', None)
                            
                            del st.session_state.uploaded_templates[template_id]
                            save_user_templates(st.session_state.logged_in_user, st.session_state.uploaded_templates)
                            st.success(f"✅ Deleted '{template_data['name']}'")
                            st.rerun()

            st.markdown("---")
        else:
            st.info("📂 No saved templates yet. Upload a template below to get started!")
            st.markdown("---")

        # 2️⃣ Upload Section
        st.markdown("### 📤 Upload New Template")
        uploaded_file = st.file_uploader(
            "Upload an HTML file",
            type=['html'],
            key="template_upload"
        )

        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")

            with st.spinner("Parsing template..."):
                parsed_template = parse_uploaded_file(uploaded_file)

            # Store parsed template for preview and download (before saving)
            st.session_state.temp_upload_config = {
                'name': f"Uploaded_{uploaded_file.name.split('.')[0]}",
                'css': parsed_template.get('css', ''),
                'html': parsed_template.get('html', ''),
                'original_filename': uploaded_file.name
            }

            # Template name input and save button
            col1, col2 = st.columns([2, 1])
            with col1:
                template_name = st.text_input(
                    "Template Name:",
                    value=f"Uploaded_{uploaded_file.name.split('.')[0]}",
                    key="upload_template_name"
                )

            with col2:
                if st.button("💾 Save Template", use_container_width=True):
                    template_id = f"upload_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    st.session_state.uploaded_templates[template_id] = {
                        'name': template_name,
                        'css': parsed_template.get('css', ''),
                        'html': parsed_template.get('html', ''),
                        'uploaded_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'original_filename': uploaded_file.name
                    }

                    # Save to JSON
                    save_user_templates(st.session_state.logged_in_user, st.session_state.uploaded_templates)
                    st.success(f"✅ Template '{template_name}' saved!")

                    # Set the saved template as selected
                    st.session_state.selected_template_config = st.session_state.uploaded_templates[template_id]
                    st.session_state.selected_template = template_name
                    st.session_state.template_source = 'saved'
                    st.session_state.current_upload_id = template_id
                    
                    # Update preview to show saved template
                    st.session_state.selected_template_preview = f"""
                        <style>{parsed_template.get('css', '')}</style>
                        <div class="ats-page">{generate_generic_html(final_data)}</div>
                    """
                    
                    # Clear temp upload config since it's now saved
                    if 'temp_upload_config' in st.session_state:
                        del st.session_state.temp_upload_config
                    
                    st.rerun()

            # Show preview for uploaded file (before saving) - Always show when file is uploaded
            preview_html = f"""
                <style>{parsed_template.get('css', '')}</style>
                <div class="ats-page">{generate_generic_html(final_data)}</div>
            """
            st.markdown("### 🔍 Template Preview (Not Saved Yet)")
            st.components.v1.html(preview_html, height=1000, scrolling=True)
            
            # Enable downloads for unsaved upload
            st.session_state.selected_template_config = st.session_state.temp_upload_config
            st.session_state.template_source = 'temp_upload'

        st.markdown("---")

        # 3️⃣ Preview Section
        # Show uploaded file preview (before or after saving)
        if uploaded_file is not None:
            # Preview is already shown above in the upload section
            pass
        # Show saved template preview (after clicking Use) ONLY if no upload is active
        elif st.session_state.get("selected_template_preview") and st.session_state.get("template_source") == 'saved':
            st.markdown(f"### 🔍 Template Preview — **{st.session_state.selected_template}**")
            st.components.v1.html(st.session_state.selected_template_preview, height=1000, scrolling=True)

        st.markdown("---")
        if st.button("⬅️ Go Back to Editor", use_container_width=True):
            switch_page("create")

    # --- Sidebar ---
    with st.sidebar:
        st.subheader("⚙️ Template Settings")
        
        color_name = st.selectbox(
            'Choose Accent Color:',
            list(ATS_COLORS.keys()),
            key='download_sys_color_select'
        )
        primary_color = ATS_COLORS[color_name]
        
        custom_color = st.color_picker(
            'Custom Color (Advanced):',
            primary_color,
            key='download_sys_color_picker'
        )
        
        if custom_color != primary_color:
            primary_color = custom_color
        
        st.markdown("---")
        st.markdown("### 💾 Download Options")
        
        # Download buttons
        if st.session_state.get("selected_template_config"):
            current_template = st.session_state.selected_template_config
            
            # Safely get CSS and HTML with defaults
            template_css = current_template.get('css', '')
            template_html = current_template.get('html', '')
            
            # Update preview with selected color
            if st.session_state.get("selected_template_preview") or st.session_state.get("template_source") == 'temp_upload':
                preview_html = f"""
                    <style>{template_css.replace('{primary_color}', primary_color) if template_css else ''}</style>
                    <div class="ats-page">{generate_generic_html(final_data)}</div>
                """
                # Update preview to reflect color change
                if st.session_state.get("template_source") != 'temp_upload':
                    st.session_state.selected_template_preview = preview_html

            st.markdown(get_html_download_link(
                final_data, 
                primary_color, 
                st.session_state.selected_template_config
            ), unsafe_allow_html=True)
            
            st.markdown(get_doc_download_link(
                final_data, 
                primary_color, 
                st.session_state.selected_template_config
            ), unsafe_allow_html=True)
            
            st.markdown(get_text_download_link(final_data), unsafe_allow_html=True)
        else:
            st.info("👆 Please select a template first to enable download links.")

        st.markdown("---")
        st.caption("### 💡 Download Tips:")
        st.caption("**HTML:** Best for web viewing")
        st.caption("**PDF:** Open HTML → Print → Save as PDF")
        st.caption("**DOC:** Edit in Microsoft Word")
        st.caption("**TXT:** Maximum ATS compatibility")

if __name__ == '__main__':
    app_download()