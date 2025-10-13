import streamlit as st
import json, bcrypt, os
from pathlib import Path
from utils import set_image_as_bg



# # LOGIN PAGE#



# Example usage: pass any file from your image folder
set_image_as_bg("image/data.jpg")   # JPG
# set_image_as_bg("image/images.png") # PNG

# st.title("Streamlit App with Background Image")
st.set_page_config(layout="centered")

with open("../ask.ai/style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if 'clicked_btn' not in st.session_state:
    st.session_state.clicked_btn = None
if 'logged_in'not in st.session_state:
    st.session_state.logged_in = False
if 'name' not in st.session_state:
    st.session_state.name = None


if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

with open("users.json", "r") as f:
    users = json.load(f)




