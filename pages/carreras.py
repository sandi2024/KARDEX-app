import streamlit as st
import plotly.express as px
from src.queries import fetch_analisis_reprobacion, fetch_carreras_alumno, fetch_detalle_por_periodo
from src.utils import load_css, create_uabc_metric_card, render_header

load_css()
render_header()

with st.sidebar:
    st.image("assets/UABC-logo.png", width=150)
    st.markdown("### Panel de Control")
    st.page_link("pages/streamlit_app.py", label="General") # APARECE DESPUÉS
    st.page_link("pages/carreras.py", label="Carreras", icon="📊") # APARECE DESPUÉS
    st.page_link("pages/perfil_alumnos.py", label="Perfil de Alumnos", icon="🎓") # APARECE DESPUÉS
    st.page_link("pages/riesgo_academico.py", label="Riesgo Académico", icon="🚨") # APARECE DESPUÉS
    
    carrera_global = st.selectbox("📚 Carrera", ["Ingeniero en Computación", "Ingeniería Química", "..."])
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


# ============================================CUERPO DEL DASHBOARD ============================================
st.title("📈 Análisis por Carrera")

# Supongamos que traemos los datos de la carrera seleccionada
df_carrera = fetch_analisis_reprobacion(id_carrera=st.session_state.get('id_carrera_sel'))

if not df_carrera.empty:
    # --- Gráfica de Barras: Top Materias Reprobadas ---
    top_reprobadas = df_carrera[df_carrera['es_reprobado'] == 1]['materia'].value_counts().head(10)
    
    fig_bar = px.bar(
        x=top_reprobadas.values, 
        y=top_reprobadas.index,
        orientation='h',
        title="Materias con Mayor Número de Reprobados",
        labels={'x': 'Cantidad de Alumnos', 'y': 'Materia'},
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- Heatmap: Periodo vs Carrera ---
    # Esto responde a tu necesidad de visualizar carreras y periodos juntos
    st.subheader("Análisis Carrera-Periodo")
    
    # Pivotamos los datos para el mapa de calor
    df_pivot = df_carrera.groupby(['id_periodo', 'nombre_carrera'])['calificacion'].mean().unstack()
    
    fig_heat = px.imshow(
        df_pivot,
        labels=dict(x="Carrera", y="Periodo", color="Promedio"),
        color_continuous_scale='RdYlGn', # Rojo a Verde
        title="Rendimiento Promedio por Periodo y Carrera"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

else:
    st.warning("No hay datos disponibles para los filtros seleccionados.")