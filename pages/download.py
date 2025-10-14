import streamlit as st
import json
import base64
from pathlib import Path
from utils import generate_template_from_blocks,extract_ppt_blocks,extract_docx_blocks,extract_html_blocks,refine_final_data_with_template,extract_pdf_blocks,json_to_html,save_user_resume_template
from streamlit_extras.switch_page_button import switch_page 
from datetime import datetime
import re

st.set_page_config(layout="wide", page_title="Download Resume")

# Define the preferred display order for sections (copied from main.py for consistency)
# Note: 'achievements' is now included and dynamically handled.
RESUME_ORDER = ["summary", "experience", "education", "skills", "projects", "certifications", "achievements", "publications", "awards"] 

# --- ATS Template Configuration ---

# ATS-friendly color palette
ATS_COLORS = {
    "Professional Blue (Default)": "#1F497D",
    "Corporate Gray": "#4D4D4D",
    "Deep Burgundy": "#800020",
    "Navy Blue": "#000080"
}

def format_section_title(key):
    """Converts keys like 'certifications' to 'Certifications'."""
    title = key.replace('_', ' ').replace('Skills', ' Skills').replace('summary', 'Summary')
    return ' '.join(word.capitalize() for word in title.split())

# --- Template-Specific CSS & HTML Generation Functions ---
# OPTIMIZED FOR SINGLE PAGE

# Template 1: Minimalist (Most ATS-Friendly) - OPTIMIZED
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

       
        
        /* Highlighted Section Headings */
        .ats-section-title {{ 
            font-size: 10.5pt; 
            font-weight: bold; 
            color: #000;
            border-bottom: 1px solid #333;
            padding-bottom: 1px;
            margin-top: 8px;
            margin-bottom: 3px;
        }}

        /* --- Experience Item Header --- */
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
        
        /* Position/Title */
        .ats-item-title {{ 
            font-weight: bold; 
            color: #000; 
            display: inline; 
        }} 
        
        /* Company Name */
        .ats-item-subtitle {{ 
            font-style: italic; 
            color: #555; 
            display: inline; 
            font-size: 9pt;
        }}
        
        /* Date (Right Aligned) */
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

def generate_html_minimalist(data):
    return generate_generic_html(data, date_placement='right')

# Template 2: Horizontal Line - OPTIMIZED
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

def generate_html_horizontal(data):
    return generate_generic_html(data, date_placement='right')

# Template 3: Bold Title - OPTIMIZED
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
def generate_html_bold_title(data):
    return generate_generic_html(data, date_placement='right')

# Template 4: Date Below - OPTIMIZED
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

def generate_html_date_below(data):
    return generate_generic_html(data, date_placement='below')

# Template 5: Section Box - OPTIMIZED
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

def generate_html_section_box(data):
    return generate_generic_html(data, date_placement='right')

# Template 6: Times New Roman Classic - OPTIMIZED
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

def generate_html_classic(data):
    return generate_generic_html(data, date_placement='right')


# --- Dynamic Universal HTML Generator ---

def generate_generic_html(data, date_placement='right'):
    """Generates the HTML content based on data and template style choices."""
    if not data: return ""
    
    # --- Attempt to find a general job title for the header ---
    job_title_for_header = data.get('job_title', '')

    # --- Header and Contact Info (Updated) ---
    html = f"""
    <div class="ats-header">
        <h1>{data.get('name', 'NAME MISSING')}</h1>
        {f'<div class="ats-job-title-header">{job_title_for_header}</div>' if job_title_for_header else ''}
        <div class="ats-contact">
            <span>{data.get('phone', '')}</span>
            <span>{data.get('email', '')}</span>
            <span>{data.get('location', '')}</span>
        </div>
    </div>
    """
    
    # --- Dynamic Sections ---
    for key in RESUME_ORDER:
        section_data = data.get(key)
        
        if not section_data or (isinstance(section_data, list) and not section_data) or (key == 'summary' and not section_data):
            continue
            
        title = format_section_title(key)
        html += f'<div class="ats-section-title">{title}</div>'
        
        if key == 'summary' and isinstance(section_data, str):
            html += f'<p style="margin-top: 0; margin-bottom: 5px;">{section_data}</p>'
        
        elif key == 'skills' and isinstance(section_data, dict):
            for skill_type, skill_list in section_data.items():
                if skill_list:
                    html += f'<div class="ats-skills-group">'
                    html += f'<strong>{format_section_title(skill_type)}:</strong> '
                    html += ", ".join(skill_list)
                    html += f'</div>'
        
        elif isinstance(section_data, list):
            for item in section_data:
                # FIX: Check if item is a string (like in achievements section)
                if isinstance(item, str):
                    # For simple string items, just add as bullet point
                    html += f'<ul class="ats-bullet-list"><li>{item}</li></ul>'
                    continue
                
                # FIX: Check if item is a dictionary
                if not isinstance(item, dict):
                    continue
                
                title_keys = ['title', 'name', 'degree']
                subtitle_keys = ['company', 'institution', 'issuer', 'organization']
                duration_keys = ['duration', 'date', 'period']
                
                main_title = next((item[k] for k in title_keys if k in item and item[k]), '')
                subtitle = next((item[k] for k in subtitle_keys if k in item and item[k] != main_title and item[k]), '')
                duration = next((item[k] for k in duration_keys if k in item and item[k]), '')

                # 1. Start of Item Header (The container for all main elements)
                html += '<div class="ats-item-header">'
                
                # --- Right Alignment Logic (Title Left, Date Right) ---
                if duration and date_placement == 'right':
                    
                    # 2. Title and Subtitle Group (Flex Item 1 / Block Item 1) - THIS MUST COME FIRST
                    html += '<div class="ats-item-title-group">' 
                    
                    # Title
                    html += f'<span class="ats-item-title">{main_title}'
                    
                    # Subtitle (now always inline via CSS)
                    if subtitle:
                        html += f' <span class="ats-item-subtitle">{subtitle}</span>' 
                    html += '</span>'
                    
                    html += '</div>' # Close ats-item-title-group
                    
                    # Add duration LAST so Flexbox pushes it to the right (Flex Item 2)
                    html += f'<div class="ats-item-duration">{duration}</div>'
                
                
                # --- Date Below Logic (Duration is forced to new line by CSS) ---
                elif duration and date_placement == 'below':
                    # Title and Subtitle Group
                    html += '<div class="ats-item-title-group">' 
                    html += f'<span class="ats-item-title">{main_title}'
                    if subtitle:
                        html += f' <span class="ats-item-subtitle">{subtitle}</span>'
                    html += '</span>'
                    html += '</div>' # Close ats-item-title-group
                    
                    # Duration is placed here, and the 'display: block' CSS for date-below
                    # will force it onto a new line immediately after the title group.
                    html += f'<div class="ats-item-duration">{duration}</div>'
                        
                else: 
                    # Fallback for when date is missing or date_placement isn't 'right'/'below'
                    html += '<div class="ats-item-title-group">' 
                    html += f'<span class="ats-item-title">{main_title}'
                    if subtitle:
                        html += f' <span class="ats-item-subtitle">{subtitle}</span>'
                    html += '</span>'
                    html += '</div>' # Close ats-item-title-group
                        
                html += '</div>' # Close ats-item-header
                
                # Bullet Points (Description or Achievements)
                description_list_raw = item.get('description') or item.get('achievement') or item.get('details') 

                if description_list_raw:
                    if isinstance(description_list_raw, str):
                        description_list = [description_list_raw]
                    elif isinstance(description_list_raw, list):
                        description_list = description_list_raw
                    else:
                        description_list = None
                        
                    if description_list:
                        bullet_html = "".join([f"<li>{line}</li>" for line in description_list])
                        html += f'<ul class="ats-bullet-list">{bullet_html}</ul>'

    return html

# --- Template Configuration Dictionary (6 templates) ---

TEMPLATE_CONFIGS = {
    "Minimalist (ATS Best)": {
        "html_generator": generate_html_minimalist,
        "css_generator": get_css_minimalist,
    },
    "Horizontal Line": {
        "html_generator": generate_html_horizontal,
        "css_generator": get_css_horizontal,
    },
    "Bold Title Accent": {
        "html_generator": generate_html_bold_title,
        "css_generator": get_css_bold_title,
    },
    "Date Below": {
        "html_generator": generate_html_date_below,
        "css_generator": get_css_date_below,
    },
    "Section Box Header": {
        "html_generator": generate_html_section_box,
        "css_generator": get_css_section_box,
    },
    "Times New Roman Classic": {
        "html_generator": generate_html_classic,
        "css_generator": get_css_classic,
    }
}


# --- Download Link Generation ---

def generate_html_content(data, color, template_generator, css_generator):
    """Generates the full HTML document and returns base64-encoded string."""
    css = css_generator(color)
    html_content = template_generator(data)
    
    # ADDED: Title tag based on name and template
    title = f"{data.get('name', 'Resume')} - {template_generator.__name__.replace('generate_html_', '').title()}"
    
    # Use the added title tag here:
    full_document_html = f"<html><head><meta charset='UTF-8'>{css}<title>{title}</title></head><body><div class='ats-page'>{html_content}</div></body></html>" 
    return base64.b64encode(full_document_html.encode('utf-8')).decode()

def get_html_download_link(data, color, template_name):
    """Generates a download link for the styled HTML file."""
    
    config = TEMPLATE_CONFIGS[template_name]
    b64_data = generate_html_content(
        data, 
        color, 
        config['html_generator'], 
        config['css_generator']
    )
    
    mime_type = "text/html"
    filename = f"Resume_{data.get('name', 'User').replace(' ', '_')}_{template_name.replace(' ', '_')}.html"
    link_text = f"⬇️ Download HTML (.html)"
    
    # Styled download link
    href = f'<a href="data:{mime_type};base64,{b64_data}" download="{filename}" style="font-size: 0.95em; text-decoration: none; padding: 10px 15px; background-color: #1E90FF; color: white; border-radius: 5px; display: inline-block; margin-top: 10px; width: 100%; text-align: center;"><strong>{link_text}</strong></a>'
    return href

def get_pdf_download_link(data, color, template_name):
    """Generate PDF download link - creates a properly formatted HTML file."""
    config = TEMPLATE_CONFIGS[template_name]
    
    # Generate the full HTML content
    css = config['css_generator'](color)
    html_body = config['html_generator'](data)
    
    # Create complete HTML document
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset='UTF-8'>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data.get('name', 'Resume')}</title>
    {css}
</head>
<body>
    <div class='ats-page'>
        {html_body}
    </div>
</body>
</html>"""
    
    # Encode to base64
    b64_data = base64.b64encode(full_html.encode('utf-8')).decode()
    
    # Create download link for HTML file that can be opened and printed
    filename = f"Resume_{data.get('name', 'User').replace(' ', '_')}_PDF.html"
    
    pdf_html = f"""
    <a href="data:text/html;charset=utf-8;base64,{b64_data}" download="{filename}"
       style="font-size: 0.95em; text-decoration: none; padding: 10px 15px; 
              background-color: #00BFFF; color: white; border-radius: 5px; 
              display: inline-block; margin-top: 10px; width: 100%; text-align: center;">
        <strong>📄 Download for PDF Export (.html)</strong>
    </a>
    """
    return pdf_html

def get_doc_download_link(data):
    """Generates a download link for a DOC file (HTML format that Word can open)."""
    text_content = generate_doc_html(data)
    b64_data = base64.b64encode(text_content.encode('utf-8')).decode()
    
    filename = f"Resume_{data.get('name', 'User').replace(' ', '_')}.doc"
    link_text = "📝 Download DOC (.doc)"

    # Styled download link
    href = f'<a href="data:application/msword;base64,{b64_data}" download="{filename}" style="font-size: 0.95em; text-decoration: none; padding: 10px 15px; background-color: #007bff; color: white; border-radius: 5px; display: inline-block; margin-top: 10px; width: 100%; text-align: center;"><strong>{link_text}</strong></a>'
    return href

def generate_doc_html(data):
    """Generate a simple HTML that can be saved as .doc and opened in Word - SINGLE PAGE."""
    html = f"""
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
    <head>
        <meta charset='utf-8'>
        <title>Resume</title>
        <style>
            @page {{
                size: 8.5in 11in;
                margin: 0.5in 0.5in 0.5in 0.5in;
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

def get_text_download_link(data):
    """Generates a download link for a plain text/markdown file."""
    text_content = generate_markdown_text(data)
    b64_data = base64.b64encode(text_content.encode('utf-8')).decode()
    
    filename = f"Resume_{data.get('name', 'User').replace(' ', '_')}_ATS_Plain_Text.txt"
    link_text = "📋 Download Plain Text (.txt)"

    # Styled download link
    href = f'<a href="data:text/plain;base64,{b64_data}" download="{filename}" style="font-size: 0.95em; text-decoration: none; padding: 10px 15px; background-color: #1E90FF; color: white; border-radius: 5px; display: inline-block; margin-top: 10px; width: 100%; text-align: center;"><strong>{link_text}</strong></a>'
    return href

# Reuse the existing robust markdown generator for the .txt file
def generate_markdown_text(data):
    """Generates a plain markdown/text version of the resume."""
    text = ""
    
    # Header
    text += f"{data.get('name', 'NAME MISSING').upper()}\n"
    if data.get('job_title'):
        text += f"{data.get('job_title')}\n"
    contact_parts = [data.get('phone', ''), data.get('email', ''), data.get('location', '')]
    text += " | ".join(filter(None, contact_parts)) + "\n"
    text += "=" * 50 + "\n\n"
    
    # Dynamic Sections
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
            # Skills section logic
            for skill_type, skill_list in section_data.items():
                if skill_list:
                    text += f"{format_section_title(skill_type)}: "
                    text += ", ".join(skill_list) + "\n"
            text += "\n"
        
        elif isinstance(section_data, list):
            # Generic list item logic
            for item in section_data:
                # FIX: Check if item is a dictionary before calling .get()
                if not isinstance(item, dict):
                    # If item is a string, just add it as plain text
                    text += f" - {item}\n"
                    continue
                
                title_keys = ['title', 'name', 'degree']
                subtitle_keys = ['company', 'institution', 'issuer']
                duration_keys = ['duration', 'date']
                
                main_title = next((item[k] for k in title_keys if k in item and item[k]), '')
                subtitle = next((item[k] for k in subtitle_keys if k in item and item[k] != main_title and item[k]), '')
                duration = next((item[k] for k in duration_keys if k in item and item[k]), '')

                # Item Header (Title, Subtitle, Duration)
                line = f"{main_title}"
                if subtitle:
                    line += f" ({subtitle})"
                if duration:
                    line += f" | {duration}"
                text += line + "\n"
                
                # Bullet Points
                description_list = item.get('description') or item.get('achievement') or item.get('details')
                if description_list and isinstance(description_list, list):
                    for line in description_list:
                        text += f" - {line}\n"
                    
                # Other simple string fields as key-value pairs
                for k, v in item.items():
                    if isinstance(v, str) and v and k not in title_keys and k not in subtitle_keys and k not in duration_keys and k not in ['description', 'achievement', 'details']:
                        text += f"   {format_section_title(k)}: {v}\n"
            text += "\n" # Add a final newline after the section list

    return text

# --- Streamlit Page Layout ---
def load_user_templates(user_id):
    """
    Load all saved templates for a user
    """
    save_folder = Path("user_templates")
    if not save_folder.exists():
        return []
    
    templates = []
    for file_path in save_folder.glob(f"{user_id}_*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                template_data = json.load(f)
                templates.append({
                    "name": template_data.get("template_name", file_path.stem),
                    "path": file_path,
                    "data": template_data.get("template_data", template_data),
                    "created_at": template_data.get("created_at", "Unknown")
                })
        except Exception as e:
            st.error(f"Error loading template {file_path.name}: {str(e)}")
    
    return templates



def save_user_template_enhanced(user_id, template_json, template_name):
    """
    Save user's custom template with metadata
    """
    save_folder = Path("user_templates")
    save_folder.mkdir(exist_ok=True)
    
    # Create a unique filename
    safe_name = template_name.replace(" ", "_").replace("/", "_")
    save_path = save_folder / f"{user_id}_{safe_name}.json"
    
    # Add metadata
    template_with_metadata = {
        "template_name": template_name,
        "user_id": user_id,
        "created_at": str(datetime.now()),
        "template_data": template_json
    }
    
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(template_with_metadata, f, indent=4)
    
    return save_path

def delete_user_template(template_path):
    """Delete a user's saved template."""
    try:
        Path(template_path).unlink()
        return True
    except Exception as e:
        st.error(f"Error deleting template: {e}")
        return False


def get_all_templates(user_id):
    """
    Get both system templates and user templates.
    Returns a dictionary with two categories.
    """
    # System templates
    system_templates = [
        {
            "name": "Minimalist (ATS Best)",
            "type": "system",
            "description": "Clean, single-column layout optimized for ATS parsing",
            "config": TEMPLATE_CONFIGS["Minimalist (ATS Best)"]
        },
        {
            "name": "Horizontal Line",
            "type": "system",
            "description": "Classic design with horizontal line separators",
            "config": TEMPLATE_CONFIGS["Horizontal Line"]
        },
        {
            "name": "Bold Title Accent",
            "type": "system",
            "description": "Modern template with bold colored accents",
            "config": TEMPLATE_CONFIGS["Bold Title Accent"]
        },
        {
            "name": "Date Below",
            "type": "system",
            "description": "Dates positioned below job titles",
            "config": TEMPLATE_CONFIGS["Date Below"]
        },
        {
            "name": "Section Box Header",
            "type": "system",
            "description": "Colored box headers for each section",
            "config": TEMPLATE_CONFIGS["Section Box Header"]
        },
        {
            "name": "Times New Roman Classic",
            "type": "system",
            "description": "Traditional serif font with classic styling",
            "config": TEMPLATE_CONFIGS["Times New Roman Classic"]
        }
    ]
    
    # User templates
    user_templates = load_user_templates(user_id)
    
    return {
        "system": system_templates,
        "custom": user_templates
    }


# --- Streamlit App with Template Gallery ---

def app_download():
    st.markdown("""
        <style>
        [data-testid="collapsedControl"] {
            display: none;
        }
        .stApp {
            background: linear-gradient(135deg, rgba(100, 181, 246, 0.15) 0%, rgba(224, 247, 250, 0.25) 50%, rgba(179, 229, 252, 0.15) 100%),
                        linear-gradient(rgba(255, 255, 255, 0.85), rgba(240, 248, 255, 0.85)),
                        url('https://images.unsplash.com/photo-1491002052546-bf38f186af56?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80') center/cover;
            background-attachment: fixed;
        }
        
        .template-card {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 2px solid rgba(66, 165, 245, 0.2);
            transition: all 0.3s ease;
        }
        
        .template-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(66, 153, 225, 0.2);
            border-color: #42A5F5;
        }
        
        .template-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-right: 0.5rem;
        }
        
        .badge-system {
            background: linear-gradient(135deg, #42A5F5 0%, #1E88E5 100%);
            color: white;
        }
        
        .badge-custom {
            background: linear-gradient(135deg, #66BB6A 0%, #43A047 100%);
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    final_data = st.session_state.get('final_resume_data')

    if final_data is None:
        st.error("❌ Resume data not found. Please return to the editor to finalize your resume.")
        if st.button("⬅️ Go Back to Editor"):
            switch_page("main")
        return

    # Safely load the data
    if isinstance(final_data, str):
        try:
            final_data = json.loads(final_data)
        except json.JSONDecodeError:
            st.error("❌ Error: Could not parse resume data.")
            return

    user_id = st.session_state.get('logged_in_user', 'default_user')
    
    # Get all templates
    all_templates = get_all_templates(user_id)
    
    # --- Main Header ---
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: #0D47A1; font-size: 2.5rem; margin-bottom: 0.5rem;">📄 Download Your Resume</h1>
            <p style="color: #1565C0; font-size: 1.1rem;">Choose from our templates or use your custom uploaded templates</p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- Template Selection Tabs ---
    tab1, tab2, tab3 = st.tabs(["🎨 System Templates", "📁 My Custom Templates", "⬆️ Upload New Template"])
    
    # TAB 1: System Templates
    with tab1:
        st.markdown("### 🎨 Professional System Templates")
        st.markdown("Choose from our carefully designed ATS-optimized templates")
        
        cols = st.columns(2)
        for idx, template in enumerate(all_templates["system"]):
            with cols[idx % 2]:
                st.markdown(f"""
                    <div class="template-card">
                        <span class="template-badge badge-system">SYSTEM</span>
                        <h3 style="color: #0D47A1; margin: 0.5rem 0;">{template['name']}</h3>
                        <p style="color: #666; font-size: 0.9rem;">{template['description']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Use {template['name']}", key=f"sys_{idx}"):
                    st.session_state['selected_template'] = template['name']
                    st.session_state['selected_template_type'] = 'system'
                    st.success(f"✅ Selected: {template['name']}")
                    st.rerun()
    
    # TAB 2: Custom Templates
    with tab2:
        st.markdown("### 📚 My Saved Templates")
        
        # Load user's saved templates
        saved_templates = load_user_templates(user_id)
        
        if not saved_templates:
            st.info("📭 You haven't saved any custom templates yet. Upload a template in Tab 3 to get started!")
        else:
            st.markdown(f"**Found {len(saved_templates)} saved template(s)**")
            
            # Display templates in a grid
            cols_per_row = 3
            for i in range(0, len(saved_templates), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx < len(saved_templates):
                        template = saved_templates[idx]
                        
                        with col:
                            st.markdown(f"""
                                <div style="border: 2px solid #42A5F5; border-radius: 12px; 
                                            padding: 1rem; background: white; height: 200px;
                                            display: flex; flex-direction: column; justify-content: space-between;">
                                    <div>
                                        <h4 style="margin: 0; color: #1E88E5;">📄 {template['name']}</h4>
                                        <p style="font-size: 0.85rem; color: #666; margin: 0.5rem 0;">
                                            Created: {template['created_at'][:10] if isinstance(template['created_at'], str) else 'Unknown'}
                                        </p>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button("✨ Use", key=f"use_{idx}", use_container_width=True):
                                    st.session_state['selected_template'] = template['name']
                                    st.session_state['selected_template_type'] = 'custom'
                                    st.session_state['selected_template_data'] = template['data']
                                    st.success(f"✅ Selected: {template['name']}")
                                    st.rerun()
                            
                            with col2:
                                if st.button("🗑️ Delete", key=f"del_{idx}", use_container_width=True):
                                    try:
                                        template['path'].unlink()
                                        st.success(f"✅ Deleted: {template['name']}")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error: {str(e)}")
    # ==================== IMPROVED SELECTED TEMPLATE PREVIEW ====================

    st.markdown("---")

    if 'selected_template' in st.session_state:
        selected_template_name = st.session_state['selected_template']
        selected_type = st.session_state['selected_template_type']
        
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #42A5F5 0%, #1E88E5 100%); 
                        padding: 1.5rem; border-radius: 16px; color: white; text-align: center; margin: 2rem 0;">
                <h2 style="margin: 0;">✨ Currently Selected: {selected_template_name}</h2>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Type: {selected_type.upper()}</p>
            </div>
        """, unsafe_allow_html=True)
        
        if selected_type == 'custom':
            template_data = st.session_state.get('selected_template_data')
            if template_data:
                # Map data to template
                with st.spinner("🔄 Generating preview..."):
                    refined_data = refine_final_data_with_template(final_data, template_data)
                    html_template = json_to_html(refined_data, final_data)
                
                st.markdown("### 📋 Live Preview")
                st.components.v1.html(html_template, height=1000, scrolling=True)
                
                # Download custom template
                st.sidebar.markdown("---")
                st.sidebar.markdown("### 💾 Download Custom Template")
                
                b64 = base64.b64encode(html_template.encode()).decode()
                href = f'<a href="data:text/html;base64,{b64}" download="Resume_{selected_template_name}.html" style="background-color: #42A5F5; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none; display: inline-block; width: 100%; text-align: center;"><strong>⬇️ Download HTML</strong></a>'
                st.sidebar.markdown(href, unsafe_allow_html=True)
                
                # JSON download
                json_b64 = base64.b64encode(json.dumps(refined_data, indent=2).encode()).decode()
                json_href = f'<a href="data:application/json;base64,{json_b64}" download="Template_{selected_template_name}.json" style="background-color: #66BB6A; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none; display: inline-block; width: 100%; text-align: center; margin-top: 10px;"><strong>📋 Download JSON</strong></a>'
                st.sidebar.markdown(json_href, unsafe_allow_html=True)
        
        else:  # System template
            # Your existing system template code
            pass

    else:
        st.info("👆 Please select a template from the tabs above to preview and download your resume")

    # Back button
    if st.sidebar.button("⬅️ Go Back to Editor", use_container_width=True):
        switch_page("job")

    st.markdown("---")
    # TAB 3: Upload New Template
    # Replace the TAB 3 section in your download.py with this improved version

    with tab3:
        st.markdown("### ⬆️ Upload Your Own Resume Template")
        st.markdown("Upload a PDF, DOC, DOCX, PPT, PPTX, or HTML file to create a custom template")
        
        # Add helpful tips
        with st.expander("💡 Tips for Best Results"):
            st.markdown("""
            **For best template extraction:**
            - Use well-formatted documents with clear sections
            - Ensure text is selectable (not scanned images)
            - Files with consistent styling work best
            - PDF and DOCX formats typically give best results
            """)
        
        uploaded_file = st.file_uploader(
            "Upload template file", 
            type=["pdf", "doc", "docx", "html", "htm", "ppt", "pptx"], 
            help="Upload your custom resume template file.",
            key="template_uploader"
        )

        if uploaded_file is not None:
            st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
            
            file_ext = uploaded_file.name.split(".")[-1].lower()
            
            # Show processing status
            status_container = st.empty()
            progress_bar = st.progress(0)
            
            try:
                # Step 1: Extract blocks
                status_container.info(f"🔄 Step 1/3: Extracting content from {file_ext.upper()} file...")
                progress_bar.progress(33)
                
                if file_ext == "pdf":
                    blocks_data = extract_pdf_blocks(uploaded_file)
                elif file_ext in ["ppt", "pptx"]:
                    blocks_data = extract_ppt_blocks(uploaded_file)
                elif file_ext in ["doc", "docx"]:
                    blocks_data = extract_docx_blocks(uploaded_file)
                elif file_ext in ["html", "htm"]:
                    blocks_data = extract_html_blocks(uploaded_file)
                else:
                    st.error(f"❌ Unsupported file type: {file_ext}")
                    st.stop()
                
                if not blocks_data:
                    st.error("❌ No content could be extracted from the file. Please check the file format.")
                    st.stop()
                
                st.success(f"✅ Extracted {len(blocks_data)} text blocks from the document")
                
                # Step 2: Generate template
                status_container.info("🔄 Step 2/3: Analyzing document structure with AI...")
                progress_bar.progress(66)
                
                template_json = generate_template_from_blocks(blocks_data, file_type=file_ext)
                
                # Check for errors in template generation
                if "error" in template_json:
                    st.error(f"❌ Error extracting template: {template_json.get('error')}")
                    
                    with st.expander("🔍 Debug Information - Click to expand"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Error Details:**")
                            st.json({
                                "error": template_json.get("error"),
                                "help": template_json.get("help", "No additional help available")
                            })
                        
                        with col2:
                            st.markdown("**Sample Extracted Content:**")
                            st.json(template_json.get("blocks_sample", [])[:3])
                        
                        # Show raw AI response if available
                        if "raw" in template_json:
                            st.markdown("---")
                            st.markdown("**Raw AI Response (first 1000 chars):**")
                            st.code(template_json["raw"][:1000], language="text")
                            
                            # Try manual extraction
                            st.markdown("---")
                            if st.button("🔧 Try Manual JSON Extraction"):
                                raw_text = template_json["raw"]
                                extracted = None
                                
                                # Try different extraction methods
                                patterns = [
                                    (r'```json\s*(.*?)\s*```', "```json block"),
                                    (r'```\s*(.*?)\s*```', "``` block"),
                                    (r'(\{[\s\S]*\})', "JSON object")
                                ]
                                
                                for pattern, name in patterns:
                                    match = re.search(pattern, raw_text, re.DOTALL)
                                    if match:
                                        try:
                                            extracted = json.loads(match.group(1).strip())
                                            st.success(f"✅ Successfully extracted JSON from {name}!")
                                            template_json = extracted
                                            break
                                        except json.JSONDecodeError as e:
                                            st.warning(f"Found {name} but failed to parse: {str(e)}")
                                
                                if extracted is None:
                                    st.error("❌ Could not automatically extract JSON. Please try a different file.")
                                    st.stop()
                    
                    if "error" in template_json:  # Still has error after manual fix attempt
                        st.info("💡 **Suggestions:**\n- Try a different file format (PDF or DOCX recommended)\n- Ensure the document has clear text content\n- Check that the file isn't corrupted")
                        st.stop()
                
                status_container.success("✅ Step 2/3: Template structure extracted successfully!")
                progress_bar.progress(100)
                
                # Preview extracted structure
                with st.expander("📋 Preview Extracted Template Structure"):
                    st.json(template_json)
                
                # Step 3: Map user data to template
                st.markdown("---")
                st.markdown("### 🎨 Preview with Your Data")
                
                with st.spinner("🔄 Step 3/3: Mapping your resume data to template..."):
                    refined_data = refine_final_data_with_template(final_data, template_json)
                    
                    # Check for errors in mapping
                    if "error" in refined_data:
                        st.warning(f"⚠️ Warning during data mapping: {refined_data.get('error')}")
                        
                        if "fallback" in refined_data:
                            st.info("ℹ️ Using original template structure with your data")
                            refined_data = refined_data["fallback"]
                        else:
                            st.info("ℹ️ Showing template structure without data mapping")
                            refined_data = template_json
                    
                    # Generate HTML preview
                    html_template = json_to_html(refined_data, final_data)
                
                # Show live preview
                st.markdown("### 📄 Live Preview")
                st.components.v1.html(html_template, height=800, scrolling=True)
                
                # Save template section
                st.markdown("---")
                st.markdown("### 💾 Save This Template")
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    default_name = uploaded_file.name.rsplit('.', 1)[0]
                    template_name = st.text_input(
                        "Template Name", 
                        value=default_name,
                        placeholder="e.g., My Professional Template",
                        key="custom_template_name",
                        help="Give your template a memorable name"
                    )
                
                with col2:
                    st.write("")  # Spacing
                    st.write("")  # Spacing
                    save_enabled = bool(template_name and "error" not in template_json)
                    
                    if st.button("💾 Save Template", 
                            type="primary", 
                            use_container_width=True,
                            disabled=not save_enabled):
                        try:
                            save_path = save_user_template_enhanced(
                                user_id, 
                                template_json, 
                                template_name
                            )
                            st.success(f"✅ Template '{template_name}' saved successfully!")
                            st.balloons()
                            
                            # Update session state
                            st.session_state['selected_template'] = template_name
                            st.session_state['selected_template_type'] = 'custom'
                            st.session_state['selected_template_data'] = template_json
                            
                            # Show success message with next steps
                            st.info("💡 Your template is now available in the 'My Custom Templates' tab!")
                            
                        except Exception as e:
                            st.error(f"❌ Error saving template: {str(e)}")
                
                if not template_name:
                    st.warning("⚠️ Please enter a template name to save")
                
                # Download options
                st.markdown("---")
                st.markdown("### ⬇️ Download Options")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Download HTML
                    html_bytes = html_template.encode()
                    b64 = base64.b64encode(html_bytes).decode()
                    href = f'''
                    <a href="data:text/html;base64,{b64}" 
                    download="Resume_{template_name if template_name else 'Custom'}.html" 
                    style="background-color: #42A5F5; color: white; padding: 12px 20px; 
                            border-radius: 8px; text-decoration: none; display: inline-block; 
                            width: 100%; text-align: center; font-weight: bold;">
                        📄 Download HTML
                    </a>
                    '''
                    st.markdown(href, unsafe_allow_html=True)
                
                with col2:
                    # Download JSON template
                    json_str = json.dumps(template_json, indent=2)
                    b64_json = base64.b64encode(json_str.encode()).decode()
                    href_json = f'''
                    <a href="data:application/json;base64,{b64_json}" 
                    download="Template_{template_name if template_name else 'Custom'}.json" 
                    style="background-color: #66BB6A; color: white; padding: 12px 20px; 
                            border-radius: 8px; text-decoration: none; display: inline-block; 
                            width: 100%; text-align: center; font-weight: bold;">
                        📋 Download JSON
                    </a>
                    '''
                    st.markdown(href_json, unsafe_allow_html=True)
                
                with col3:
                    # Info about PDF conversion
                    st.info("💡 Use 'Print to PDF' in your browser after downloading HTML for PDF version")
            
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                with st.expander("🔍 Full Error Details"):
                    st.exception(e)
                
                st.info("💡 **Troubleshooting:**\n"
                    "1. Try a different file format\n"
                    "2. Ensure the file isn't corrupted\n"
                    "3. Check file size (very large files may timeout)")
            
            finally:
                # Clean up progress indicators
                status_container.empty()
                progress_bar.empty()

if __name__ == '__main__':
    app_download()