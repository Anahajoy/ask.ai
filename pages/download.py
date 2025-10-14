import streamlit as st
import json
import base64
import textwrap
from streamlit_extras.switch_page_button import switch_page 

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

def app_download():
    st.set_page_config(layout="wide", page_title="Download Resume")
    st.markdown("""
        <style>
        /* Hide entire sidebar */

    [data-testid="collapsedControl"] {
        display: none;
    }
        .stApp {
    background: linear-gradient(rgba(255,255,255,0.4), rgba(255,255,255,0.4)),
                url('https://plus.unsplash.com/premium_photo-1674331863328-78a318c57447?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=872') center/cover;
    background-attachment: fixed;
}

        </style>
    """, unsafe_allow_html=True)

    
    final_data = st.session_state.get('final_resume_data')

    if final_data is None:
        st.error("❌ Resume data not found. Please return to the editor to finalize your resume.")
        if st.button("⬅️ Go Back to Editor"):
            switch_page("main")
        return

    # Safely load the data in case it was stored as a JSON string
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


    # --- Sidebar: Settings & Downloads ---
    st.sidebar.subheader("⚙️ Template Settings")

    # Template Selection
    selected_template_name = st.sidebar.selectbox(
        "Choose Template Style:",
        list(TEMPLATE_CONFIGS.keys()),
        key='template_select'
    )
    selected_template = TEMPLATE_CONFIGS[selected_template_name]

    # Accent Color Selection
    color_name = st.sidebar.selectbox(
        'Choose Accent Color:',
        list(ATS_COLORS.keys()),
        key='color_name_select'
    )
    primary_color = ATS_COLORS[color_name]

    # Optional: Show color picker for custom color
    custom_color = st.sidebar.color_picker(
        'Custom Color (Advanced):',
        primary_color, 
        key='color_picker_custom'
    )

    if custom_color != primary_color:
        primary_color = custom_color

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💾 Download Options")

    # HTML Download
    st.sidebar.markdown(get_html_download_link(final_data, primary_color, selected_template_name), unsafe_allow_html=True)

    # PDF Download
    st.sidebar.markdown(get_pdf_download_link(final_data, primary_color, selected_template_name), unsafe_allow_html=True)
    st.sidebar.caption("↑ Downloads HTML → Open it in browser → Ctrl+P → Save as PDF")

    # DOC Download
    st.sidebar.markdown(get_doc_download_link(final_data), unsafe_allow_html=True)

    # Plain Text Download
    st.sidebar.markdown(get_text_download_link(final_data), unsafe_allow_html=True)

    # Instructions
    st.sidebar.markdown("---")
    st.sidebar.caption("### 💡 Download Tips:")
    st.sidebar.caption("**HTML:** Best for web viewing and customization")
    st.sidebar.caption("**PDF:** Downloads HTML file → Open in Chrome/Edge → Ctrl+P (Cmd+P) → Destination: Save as PDF → Save")
    st.sidebar.caption("**DOC:** Opens in Microsoft Word for editing (single-page optimized)")
    st.sidebar.caption("**TXT:** Maximum ATS compatibility (plain text format)")

    st.sidebar.markdown(f'<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)

    if st.sidebar.button("⬅️ Go Back to Editor", use_container_width=True):
        switch_page("job")

    st.markdown(
        """
        <div style="text-align: center;">
            <h1>📄 Download Your Resume</h1>
            <p style="color: gray; font-size: 16px;">
                <b>All templates optimized for single-page format.</b> Choose your template and download in multiple formats.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- File uploader ---
    uploaded_file = st.file_uploader(
        "Upload PDF, PPT, DOC, or HTML template file", 
        type=["pdf", "ppt", "pptx", "doc", "docx", "html"], 
        help="Upload your custom resume template file.",
        key="template_uploader"
    )

    if uploaded_file is not None:
        # Show only upload success
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        st.info("Processing / preview logic is skipped because a file was uploaded.")
    else:
        # Show default content if no file uploaded
        st.markdown(
            f"""
            <div style="text-align: center;">
                <h3>📋 Live Preview: {selected_template_name}</h3>
                <p style="color: gray;">This preview shows how your resume will look when printed to PDF (optimized for single page)</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        ats_css = selected_template['css_generator'](primary_color)
        ats_html = selected_template['html_generator'](final_data) 

        full_html = f"""
        {ats_css}
        <div class="ats-page">
            {ats_html}
        </div>
        """

        st.components.v1.html(
            full_html,
            height=1000, 
            scrolling=True
        )

if __name__ == '__main__':
    app_download()