from utils import generate_generic_html,generate_two_column_html
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates"))

def load_css_template(template_name, color):
    template = env.get_template(f"{template_name}.css.jinja")
    return template.render(color=color)



ATS_COLORS = {
    "Professional Blue (Default)": "#1F497D",
    "Corporate Gray": "#4D4D4D",
    "Deep Burgundy": "#800020",
    "Navy Blue": "#000080",
    "Black":"#000000"
}



SYSTEM_TEMPLATES = {
    "Minimalist (ATS Best)": {
        "html_generator": lambda data: generate_generic_html(data, date_placement="right"),
        "css_template": "minimalist",
    },
    "Horizontal Line": {
        "html_generator": lambda data: generate_generic_html(data, date_placement="right"),
        "css_template": "horizontal",
    },
    "Bold Title Accent": {
        "html_generator": lambda data: generate_generic_html(data, date_placement="right"),
        "css_template": "bold_title",
    },
    "Date Below": {
        "html_generator": lambda data: generate_generic_html(data, date_placement="below"),
        "css_template": "date_below",
    },
    "Section Box Header": {
        "html_generator": lambda data: generate_generic_html(data, date_placement="right"),
        "css_template": "section_box",
    },
    "Times New Roman Classic": {
        "html_generator": lambda data: generate_generic_html(data, date_placement="right"),
        "css_template": "classic",
    },
    "Sophisticated Minimal": {
        "html_generator": lambda data: generate_generic_html(data, date_placement="right"),
        "css_template": "sophisticated_minimal",
    },
    "Clean Look": {
        "html_generator": lambda data: generate_generic_html(data, date_placement="right"),
        "css_template": "clean_contemporary",
    },
    "Elegant": {
        "html_generator": lambda data: generate_generic_html(data, date_placement="right"),
        "css_template": "elegant_professional",
    },
    "Modern Minimal": {
        "html_generator": lambda data: generate_generic_html(data, date_placement="right"),
        "css_template": "modern_minimal",
    },
    "Two Coloumn": {
    "html_generator": lambda data: generate_two_column_html(data),
    "css_template": "two_coloumn",
},
}
