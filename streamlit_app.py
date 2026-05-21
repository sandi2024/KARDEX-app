import streamlit as st
import pandas as pd
from src.utils import load_css, render_header, render_footer, create_uabc_metric_card
from src.database import get_connection # Tu conexión real a MySQL

import numpy as np

st.set_page_config(page_title="Dashboard Académico - FCQI", layout="wide")

load_css()
render_header()


# ============================================
# CARGA DE DATOS
# ============================================

@st.cache_data
def load_sample_data():
    """Carga datos de ejemplo para el dashboard"""
    
    np.random.seed(42)  # Para reproducibilidad
    
    # Datos de alumnos
    students = pd.DataFrame({
        'matricula': [f'00{i}/46609' for i in range(1, 101)],
        'nombre': [f'Alumno_{i}' for i in range(1, 101)],
        'carrera': np.random.choice([
            'Ingeniería Química', 'Ingeniería Industrial', 
            'Química Farmacéutica', 'Ingeniería Ambiental',
            'Ingeniería en Alimentos', 'Licenciatura en Química'
        ], 100),
        'plan_estudios': np.random.choice(['1994-2', '2005-1', '2010-1', '2015-2', '2020-1'], 100),
        'promedio_general': np.random.normal(75, 12, 100).clip(0, 100),
        'creditos_cursados': np.random.randint(0, 400, 100),
        'creditos_requeridos': 326,
        'examenes_regularizacion': np.random.randint(0, 5, 100),
        'estatus': np.random.choice(['ACTIVO', 'REZAGADO', 'RIESGO', 'REGULAR'], 100, p=[0.5, 0.2, 0.2, 0.1])
    })
    
    # Calcular métricas adicionales
    students['creditos_faltantes'] = students['creditos_requeridos'] - students['creditos_cursados']
    students['porcentaje_avance'] = (students['creditos_cursados'] / students['creditos_requeridos']) * 100
    students['porcentaje_avance'] = students['porcentaje_avance'].clip(0, 100)
    
    return students




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
col1, col2, col3, col4, col5= st.columns(5)
with col1:
    st.markdown(create_uabc_metric_card("Total Alumnos", "1,200", icon="🎓"), unsafe_allow_html=True)
    
with col2:
    promedio = df['promedio_general'].mean()
    st.markdown(create_uabc_metric_card("Promedio General", f"{promedio:.1f}", "escala 0-100", "📊"), unsafe_allow_html=True)
        
with col3:
    avance = df['porcentaje_avance'].mean()
    st.markdown(create_uabc_metric_card("Avance Crediticio", f"{avance:.1f}%", "del plan de estudios", "📈"), unsafe_allow_html=True)
        
with col4:
    riesgo = len(df[df['estatus'].isin(['RIESGO', 'REZAGADO'])])
    porcentaje_riesgo = (riesgo/len(df))*100 if len(df) > 0 else 0
    st.markdown(create_uabc_metric_card("En Riesgo", riesgo, f"{porcentaje_riesgo:.0f}% del total", "⚠️"), unsafe_allow_html=True)
        
with col5:
    extras = df['examenes_regularizacion'].mean()
    st.markdown(create_uabc_metric_card("Extraordinarios", f"{extras:.1f}", "promedio por alumno", "📝"), unsafe_allow_html=True)
    
st.markdown("---")

# ... Aquí van tus gráficas de Plotly ...

render_footer()