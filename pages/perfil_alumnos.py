import streamlit as st
from src.utils import load_css, render_header, render_footer, create_uabc_metric_card
from src.database import get_connection

# Mismo diseño que la principal
load_css()
render_header()

st.title("🔍 Análisis Individual por Alumno")

matricula = st.text_input("Ingresa la matrícula:")

if matricula:
    # 1. Llamar a database.py para traer datos de MySQL
    # 2. Calcular métricas
    # 3. Mostrar el Kardex
    st.success(f"Mostrando datos para: {matricula}")
    
    # Ejemplo de tarjeta de métrica reusada
    st.markdown(create_uabc_metric_card("Promedio de Alumno", "85.2"), unsafe_allow_html=True)

render_footer()