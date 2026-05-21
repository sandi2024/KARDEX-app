import streamlit as st
import pandas as pd
from src.utils import load_css, render_header, render_footer, create_uabc_metric_card
from src.database import get_connection # Tu conexión real a MySQL

st.set_page_config(page_title="Dashboard Académico - FCQI", layout="wide")

load_css()
render_header()

# --- SIDEBAR COMPARTIDO ---
with st.sidebar:
    st.image("assets/UABC-logo.png", width=150)
    st.markdown("### Panel de Control")
    carrera_global = st.selectbox("📚 Carrera", ["Todas", "Ingeniería Química", "..."])
     # Periodo académico
    periodo = st.selectbox(
            "📅 Periodo Académico",
            ["2024-1", "2024-2", "2025-1", "Todos los periodos"])
        
    st.markdown("---")
    st.markdown("### ⚙️ Configuración")
        
    # Filtros adicionales
    umbral_reprobacion = st.slider("Umbral de reprobación", 0, 100, 60)
    mostrar_solo_riesgo = st.checkbox("⚠️ Mostrar solo alumnos en riesgo")
    mostrar_detalles = st.checkbox("📋 Mostrar detalles académicos")


    # Guardamos en session_state para que otras páginas lo usen
    st.session_state['carrera'] = carrera_global
    st.session_state['periodo'] = periodo
    st.session_state['umbral_reprobacion'] = umbral_reprobacion
    st.session_state['mostrar_solo_riesgo'] = mostrar_solo_riesgo
    st.session_state['mostrar_detalles'] = mostrar_detalles

# --- CUERPO DEL DASHBOARD ---
st.title("📊 Visión General")

# Ejemplo de cómo usar las métricas ahora:
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(create_uabc_metric_card("Total Alumnos", "1,200", icon="🎓"), unsafe_allow_html=True)

# ... Aquí van tus gráficas de Plotly ...

render_footer()