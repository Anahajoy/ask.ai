from utils import generate_generic_html, generate_two_column_html
from jinja2 import Environment, FileSystemLoader
from pages.c import ResumeDocxGenerator

# ---------------- JINJA ENV ----------------
env = Environment(loader=FileSystemLoader("templates"))

def load_css_template(template_name: str, color: str) -> str:
    template = env.get_template(f"{template_name}.css.jinja")
    return template.render(color=color)

# ---------------- COLORS ----------------
ATS_COLORS = {
    "Professional Blue (Default)": "#1F497D",
    "Corporate Gray": "#4D4D4D",
    "Deep Burgundy": "#800020",
    "Navy Blue": "#000080",
    "Black": "#000000",
}

# ---------------- DOCX GENERATOR ----------------
def generate_docx_for_template(template_name: str, color: str, resume_data: dict) -> bytes:
    generator = ResumeDocxGenerator(template_name, color)
    return generator.generate(resume_data)

# ---------------- HELPERS ----------------
def generic_html(date_placement="right"):
    return lambda data: generate_generic_html(data, date_placement=date_placement)

def docx(template_name: str):
    return lambda data, color="#1F497D": generate_docx_for_template(template_name, color, data)

# ---------------- SYSTEM TEMPLATES ----------------
SYSTEM_TEMPLATES = {
    "Minimalist (ATS Best)": {
        "html_generator": generic_html("right"),
        "css_template": "minimalist",
        "docx_generator": docx("Minimalist (ATS Best)"),
    },
    "Horizontal Line": {
        "html_generator": generic_html("right"),
        "css_template": "horizontal",
        "docx_generator": docx("Horizontal Line"),
    },
    "Bold Title Accent": {
        "html_generator": generic_html("right"),
        "css_template": "bold_title",
        "docx_generator": docx("Bold Title Accent"),
    },
    "Date Below": {
        "html_generator": generic_html("below"),
        "css_template": "date_below",
        "docx_generator": docx("Date Below"),
    },
    "Section Box Header": {
        "html_generator": generic_html("right"),
        "css_template": "section_box",
        "docx_generator": docx("Section Box Header"),
    },
    "Times New Roman Classic": {
        "html_generator": generic_html("right"),
        "css_template": "classic",
        "docx_generator": docx("Times New Roman Classic"),
    },
    "Sophisticated Minimal": {
        "html_generator": generic_html("right"),
        "css_template": "sophisticated_minimal",
        "docx_generator": docx("Sophisticated Minimal"),
    },
    "Clean Look": {
        "html_generator": generic_html("right"),
        "css_template": "clean_contemporary",
        "docx_generator": docx("Clean Look"),
    },
    "Elegant": {
        "html_generator": generic_html("right"),
        "css_template": "elegant_professional",
        "docx_generator": docx("Elegant"),
    },
    "Modern Minimal": {
        "html_generator": generic_html("right"),
        "css_template": "modern_minimal",
        "docx_generator": docx("Modern Minimal"),
    },
    "Two Coloumn": {
        "html_generator": lambda data: generate_two_column_html(data),
        "css_template": "two_coloumn",
        "docx_generator": docx("Two Coloumn"),
    },
}
