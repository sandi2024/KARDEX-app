import streamlit as st
from src.queries import fetch_analisis_reprobacion, fetch_carreras_alumno   
from src.analisis import calcular_indice_riesgo
from src.utils import load_css, render_header, create_uabc_metric_card
import pandas as pd


load_css()
render_header()

# --- SIDEBAR COMPARTIDO ---
with st.sidebar:
    st.image("assets/UABC-logo.png", width=150)
    st.markdown("### Panel de Control")
    st.page_link("pages/streamlit_app.py", label="General") # APARECE DESPUÉS
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



#============================================CUERPO DEL DASHBOARD ============================================

st.title("🚨 Sistema de Alerta Temprana")

# Traemos todos los datos de la facultad (o por carrera)
df_riesgo = fetch_analisis_reprobacion()

# Aplicamos el análisis a cada alumno único
resumen_riesgo = []
for matricula in df_riesgo['matricula'].unique():
    historial = df_riesgo[df_riesgo['matricula'] == matricula]
    analisis = calcular_indice_riesgo(historial)
    resumen_riesgo.append({
        "Matrícula": matricula,
        "Nivel de Riesgo": analisis['nivel'],
        "Score": analisis['score']
    })

df_final = pd.DataFrame(resumen_riesgo)

# Visualización
col1, col2 = st.columns([1, 2])

with col1:
    st.write("### Distribución de Riesgo")
    conteo = df_final['Nivel de Riesgo'].value_counts()
    st.bar_chart(conteo)

with col2:
    st.write("### Alumnos que requieren intervención")
    st.dataframe(df_final.sort_values("Score", ascending=False), use_container_width=True)