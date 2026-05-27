import streamlit as st
import plotly.express as px
from src.utils import load_css, render_header, create_uabc_metric_card, render_footer
from src.queries import fetch_carreras_alumno, fetch_detalle_por_periodo, get_data_analisis_completo        
from analisis import normalizar_datos_academicos
load_css()
render_header()

############################# CARGAR DATOS ##############################
# No necesitas volver a llamar a queries.py
if 'df_raw' not in st.session_state or st.session_state.df_raw.empty:
    st.session_state.df_raw = get_data_analisis_completo()
    df_datos = st.session_state.df_raw
    st.warning("VACIO")  
else:
    df_datos = st.session_state.df_raw
    st.write("Datos recuperados de la sesión con éxito.")
    # Aquí ya puedes usar df para tus gráficas de carrera

# --- SIDEBAR COMPARTIDO ---
with st.sidebar:
    st.image("assets/UABC-logo.png", width=150)
    st.markdown("### Panel de Control")
    st.sidebar.page_link("streamlit_app.py", label="Inicio", icon="🏠")
    st.page_link("pages/carreras.py", label="Carreras", icon="📊") 
    st.page_link("pages/perfil_alumnos.py", label="Perfil de Alumnos", icon="🎓") 
    st.page_link("pages/riesgo_academico.py", label="Riesgo Académico", icon="🚨") 
        
    st.markdown("---")
    st.markdown("### ⚙️ Configuración")
    
    # Filtro de carrera
    lista_carreras = ["Todas las carreras"] + sorted(df_datos['carrera'].unique().tolist())
    carrera_sel = st.selectbox("📚 Seleccione carrera", lista_carreras)
    
     # Filtro de Periodo
    lista_periodos = ["Todos los periodos"] + sorted(df_datos['periodo'].unique().tolist())
    periodo_sel = st.selectbox("📅 Seleccione Periodo Académico", lista_periodos)
    
    # Filtros adicionales
    mostrar_detalles = st.checkbox("📋 Mostrar detalles académicos")

    # Guardamos en session_state para que otras páginas lo usen
    st.session_state['carrera'] = carrera_sel
    st.session_state['periodo'] = periodo_sel
    st.session_state['mostrar_detalles'] = mostrar_detalles

#============================ PROCESAR DATOS ================================

df_limpio = normalizar_datos_academicos(df_datos)

# ============================================CUERPO DEL DASHBOARD ============================================
st.title("📈 Consulta Alumnos")

matricula = st.text_input("Matrícula")

if matricula:
    df_alumno =  df_limpio[df_limpio['matricula'] == matricula]
    carreras = df_alumno[]
    
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



render_footer()