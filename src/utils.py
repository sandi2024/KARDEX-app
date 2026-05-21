import streamlit as st
import base64
from pathlib import Path

def load_css():
    css_file = Path("assets/style.css")
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def render_header():
    st.markdown("""
    <div class="uabc-header fade-in-up">
        <div class="header-content"> 
            <div class="title-container">
                <h1> Dashboard de Gestión Académica</h1>
                <p>Facultad de Ciencias Químicas e Ingeniería | UABC</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_uabc_metric_card(title, value, subtitle=None, icon="📊"):
    return f'''
    <div class="metric-card-uabc">
        <h3>{icon} {title}</h3>
        <div class="metric-value">{value}</div>
        {f'<div class="metric-sub">{subtitle}</div>' if subtitle else ''}
    </div>
    '''

def render_footer():
    st.markdown("""
    <div class="uabc-footer">
        <p><strong>UABC</strong> | Facultad de Ciencias Químicas e Ingeniería</p>
    </div>
    """, unsafe_allow_html=True)