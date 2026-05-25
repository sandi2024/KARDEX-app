import streamlit as st
import plotly.express as px
from src.utils import load_css, render_header, create_uabc_metric_card   
from src.queries import fetch_carreras_alumno, fetch_detalle_por_periodo       

load_css()
render_header()


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
 #   st.session_state['carrera'] = carrera_global
    st.session_state['periodo'] = periodo
    st.session_state['umbral_reprobacion'] = umbral_reprobacion
    st.session_state['mostrar_solo_riesgo'] = mostrar_solo_riesgo
    st.session_state['mostrar_detalles'] = mostrar_detalles

# ============================================CUERPO DEL DASHBOARD ============================================
st.title("📈 Consulta Alumnos")

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