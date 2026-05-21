import streamlit as st
import plotly.express as px
from src.database import fetch_carreras_alumno, fetch_detalle_por_periodo
from src.utils import load_css, render_header, create_uabc_metric_card          

# 1. Búsqueda de matrícula
matricula = st.text_input("Matrícula")

if matricula:
    carreras = fetch_carreras_alumno(matricula)
    
    if len(carreras) > 1:
        st.warning("⚠️ Este alumno tiene registros en múltiples carreras.")
        seleccion = st.selectbox("Selecciona la carrera para el análisis:", 
                                 carreras['nombre_carrera'])
        id_carrera = carreras[carreras['nombre_carrera'] == seleccion]['id_carrera'].iloc[0]
    else:
        id_carrera = carreras['id_carrera'].iloc[0]

    # 2. Obtener materias filtradas por matrícula Y carrera
    df_periodos = fetch_detalle_por_periodo(matricula, id_carrera)

    # 3. Código del Análisis por Periodo
    st.subheader(f"Análisis de Rendimiento por Periodo")
    
    # Agrupamos para obtener el promedio por periodo
    df_stats_periodo = df_periodos.groupby('id_periodo').agg({
        'calificacion': 'mean',
        'materia': 'count'
    }).reset_index()

    # Gráfica de evolución
    fig = px.line(df_stats_periodo, x='id_periodo', y='calificacion', 
                  title="Evolución del Promedio Académico",
                  markers=True, text="calificacion")
    fig.update_traces(textposition="top center", line_color="#00723F") # Verde UABC
    st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar materias cursadas en ese periodo específico
    st.write("### Detalle Cronológico")
    st.table(df_periodos[['id_periodo', 'materia', 'calificacion']])