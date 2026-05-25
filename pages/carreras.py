import streamlit as st
import plotly.express as px
from src.queries import fetch_analisis_reprobacion, fetch_carreras_alumno, fetch_detalle_por_periodo
from src.utils import load_css, create_uabc_metric_card, render_header

load_css()
render_header()

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