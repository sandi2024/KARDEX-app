import streamlit as st
import plotly.express as px
from src.utils import load_css, render_header, create_uabc_metric_card, render_footer
from src.queries import get_data_analisis_completo        
from src.analisis import normalizar_datos_academicos, predecir_riesgo

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
    df_alumno =  df_limpio[df_limpio['matricula'] == matricula].sort_values('periodo')
    num_carreras = df_alumno['carrera'].nunique()
    num_planes = df_alumno['id_plan_estudio'].nunique() 
    
    if num_carreras > 1:
        st.warning("⚠️ Este alumno tiene registros en múltiples carreras.")
        seleccion = st.selectbox("Selecciona la carrera para el análisis:", 
                                 num_carreras['nombre_carrera'])
        id_carrera = num_carreras[num_carreras['nombre_carrera'] == seleccion]['id_carrera'].iloc[0]
    else:
        id_carrera = num_carreras['id_carrera'].iloc[0]

    # 2. Obtener materias filtradas por matrícula Y carrera
 #   df_periodos = fetch_detalle_por_periodo(matricula, id_carrera)

    # 3. Código del Análisis por Periodo
  #  st.subheader(f"Análisis de Rendimiento por Periodo")
    
    # Agrupamos para obtener el promedio por periodo
  #  df_stats_periodo = df_periodos.groupby('id_periodo').agg({
 #       'calificacion': 'mean',
 #       'materia': 'count'
 #   }).reset_index()
    
    ####################### INFORMACION GENERAL ############################################333


    if not df_alumno.empty:
         # 1. INFORMACIÓN GENERAL (Encabezado)
        nombre_alumno = df_alumno['nombre'].iloc[0] if 'nombre' in df_alumno.columns else "Estudiante"
        carrera_alumno = df_alumno['carrera'].iloc[0]
    
        st.title(f"📂 Expediente: {nombre_alumno}")
        st.info(f"**Matrícula:** {matricula} | **Carrera:** {carrera_alumno}")

        # 2. MÉTRICAS RESUMIDAS (KPIs)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Promedio General", f"{df_alumno['calificacion'].mean():.2f}")
        with col2:
            st.metric("Materias Cursadas", len(df_alumno))
        with col3:
        # Ejemplo si tienes columna de créditos
            total_creditos = df_alumno['creditos'].sum() if 'creditos' in df_alumno.columns else 0
            st.metric("Créditos Totales", total_creditos)

        # 3. LISTA COMPLETA DE ASIGNATURAS (El Kardex)
        st.subheader("📚 Historial Académico Completo")
    
        # Seleccionamos solo las columnas que queremos mostrar al usuario
        columnas_mostrar = ['periodo', 'asignatura', 'calificacion', 'estatus_materia']
        # Verificamos que existan en el DF para evitar errores
        columnas_reales = [c for c in columnas_mostrar if c in df_alumno.columns]
    
        # Mostramos la tabla interactiva
        st.dataframe(
            df_alumno[columnas_reales],
            use_container_width=True,
            hide_index=True # Para que se vea más limpio
        )

    ################################ riesgo academico 
    score_riesgo, nivel = predecir_riesgo(df_alumno)

    # Mostrar con un indicador visual
    st.subheader("🔮 Predicción de Riesgo Académico")

    col1, col2 = st.columns(2)
    with col1:
        color = "red" if score_riesgo >= 70 else "orange" if score_riesgo >= 40 else "green"
        st.markdown(f"### Nivel: :{color}[{nivel}]")

    with col2:
        st.metric("Índice de Riesgo", f"{score_riesgo}%", delta_color="inverse")

    # Explicación del riesgo
    if score_riesgo >= 40:
        st.warning("🚨 **Factores detectados:**")
        if df_alumno['calificacion'].mean() < 75:
            st.write("- El promedio general es muy bajo.")
        if (df_alumno['calificacion'] < 70).sum() > 0:
            st.write("- Existen materias reprobadas en el historial.")


    ###############################  GRAFICA
    # Gráfica de evolución
#    fig = px.line(df_stats_periodo, x='id_periodo', y='calificacion', 
 #                 title="Evolución del Promedio Académico",
 #                 markers=True, text="calificacion")
 #   fig.update_traces(textposition="top center", line_color="#00723F") # Verde UABC
 #   st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar materias cursadas en ese periodo específico
 #   st.write("### Detalle Cronológico")
 #   st.table(df_periodos[['id_periodo', 'materia', 'calificacion']])



render_footer()