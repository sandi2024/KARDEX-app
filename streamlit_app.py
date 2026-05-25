import streamlit as st
import pandas as pd
from src.utils import load_css, render_header, render_footer, create_uabc_metric_card
from src.queries import fetch_analisis_reprobacion, get_kardex_alumno 
from src.analisis import calcular_indice_riesgo
import numpy as np

st.set_page_config(page_title="Dashboard Académico - FCQI", layout="wide")

st.logo("assets/UABC-logo.png", layout="wide") # Esto lo posiciona arriba de 'carreras', etc.
load_css()    # Cargamos los estilos personalizados
render_header()   # Renderizamos el header común a todas las páginas


# ============================================
# CARGA DE DATOS
# ============================================

df = calcular_indice_riesgo(get_kardex_alumno("001/32146"))

# --- SIDEBAR COMPARTIDO ---
with st.sidebar:
    st.image("assets/UABC-logo.png", width=150)
    st.markdown("### Panel de Control")

    st.page_link("pages/carreras.py", label="Carreras", icon="📊") # APARECE DESPUÉS
    st.page_link("pages/perfil_alumnos.py", label="Perfil de Alumnos", icon="🎓") # APARECE DESPUÉS
    st.page_link("pages/riesgo_academico.py", label="Riesgo Académico", icon="🚨") # APARECE DESPUÉS

#    carrera_global = st.selectbox("📚 Carrera", ["Todas", "Ingeniería Química", "..."])
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
 #   st.session_state['carrera'] = carrera_global
    st.session_state['periodo'] = periodo
    st.session_state['umbral_reprobacion'] = umbral_reprobacion
    st.session_state['mostrar_solo_riesgo'] = mostrar_solo_riesgo
    st.session_state['mostrar_detalles'] = mostrar_detalles


# --- CUERPO DEL DASHBOARD ---
st.title("📊 Visión General")

# Ejemplo de cómo usar las métricas ahora:
col1, col2, col3, col4, col5= st.columns(5)
with col1:
    st.markdown(create_uabc_metric_card("Total Alumnos", "1,200", icon="🎓"), unsafe_allow_html=True)
    
with col2:
 #   promedio = df['promedio_general'].mean()
 #   st.markdown(create_uabc_metric_card("Promedio General", f"{promedio:.1f}", "escala 0-100", "📊"), unsafe_allow_html=True)
    st.markdown(create_uabc_metric_card("Promedio General", "100", "escala 0-100", "📊"), unsafe_allow_html=True)
        
with col3:
  #  avance = df['porcentaje_avance'].mean()
  #  st.markdown(create_uabc_metric_card("Avance Crediticio", f"{avance:.1f}%", "del plan de estudios", "📈"), unsafe_allow_html=True)
    st.markdown(create_uabc_metric_card("Avance Crediticio", "30%", "del plan de estudios", "📈"), unsafe_allow_html=True)  

with col4:
 #   riesgo = len(df[df['estatus'].isin(['RIESGO', 'REZAGADO'])])
 #   porcentaje_riesgo = (riesgo/len(df))*100 if len(df) > 0 else 0
 #   st.markdown(create_uabc_metric_card("En Riesgo", riesgo, f"{porcentaje_riesgo:.0f}% del total", "⚠️"), unsafe_allow_html=True)
   st.markdown(create_uabc_metric_card("En Riesgo", "50", "50% del total", "⚠️"), unsafe_allow_html=True)
        
with col5:
 #   extras = df['examenes_regularizacion'].mean()
   # st.markdown(create_uabc_metric_card("Extraordinarios", f"{extras:.1f}", "promedio por alumno", "📝"), unsafe_allow_html=True)
    st.markdown(create_uabc_metric_card("Extraordinarios", "2", "promedio por alumno", "📝"), unsafe_allow_html=True)
    
st.markdown("---")

# ... Aquí van tus gráficas de Plotly ...

render_footer()