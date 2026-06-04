import streamlit as st
import plotly.express as px
from src.utils import load_css, render_header, create_uabc_metric_card, render_footer, create_uabc_alert
from src.queries import get_data_analisis_completo        
from src.analisis import normalizar_datos_academicos, identificar_riesgo_academico2, procesar_kardex

load_css()
render_header()

############################# CARGAR DATOS ##############################
if 'df_raw' not in st.session_state or st.session_state.df_raw.empty:
    st.warning("Cargando datos desde la base de datos...")
    st.session_state.df_raw = get_data_analisis_completo()
    df_datos = st.session_state.df_raw
else:
    df_datos = st.session_state.df_raw

# --- SIDEBAR COMPARTIDO ---
with st.sidebar:
    st.image("assets/UABC-logo.png", width=150)
    st.markdown("### Panel de Control")
    st.sidebar.page_link("streamlit_app.py", label="Inicio", icon="🏠")
    st.page_link("pages/carreras.py", label="Carreras", icon="🎓") 
    st.page_link("pages/perfil_alumnos.py", label="Perfil de Alumnos", icon="🧑‍🎓") 
    st.page_link("pages/riesgo_academico.py", label="Riesgo Académico", icon="🚨") 
        
    st.markdown("---")
    st.markdown("### ⚙️ Configuración")
    
      # Filtro de Umbral
    umbral_reprobacion = st.slider("Umbral de promedio critico", 0, 100, 60)
    umbral_eficiencia = st.slider("Creditos promedio por periodo", 0, 100, 40)
    umbral_np_sp = st.slider("Limite de examenes NP y SD", 0, 10, 5)
    tasa = st.slider("Tasa (%) extraordinarios", min_value=0, max_value=100, value=10, step=1)

    # Guardamos en session_state para que otras páginas lo usen
    st.session_state['umbral_reprobacion'] = umbral_reprobacion
    st.session_state['umbral_eficiencia'] = umbral_eficiencia
    st.session_state['umbral_np_sp'] = umbral_np_sp
    st.session_state['tasa'] = tasa


#============================ PROCESAR DATOS ================================

df_limpio = normalizar_datos_academicos(df_datos)

# ============================================CUERPO DEL DASHBOARD ============================================
st.title("📈 Consulta Alumnos")

matricula = st.text_input("Ingresar matrícula:")

if matricula:
    df_alumno =  df_limpio[df_limpio['matricula'] == matricula].sort_values('periodo')
    
    num_carreras = df_alumno['carrera'].nunique()
    num_planes = df_alumno['id_plan_estudio'].nunique() 
    
    if num_carreras > 1:
        st.warning("⚠️ Este alumno tiene registros en múltiples carreras.")
 
        lista_carreras = ["Todas las carreras"] + sorted(df_alumno['carrera'].unique().tolist())
        carrera_sel = st.selectbox("📚 Seleccione carrera", lista_carreras)

        if carrera_sel != "Todas las carreras":
            df_alumno_carrera = df_alumno[df_alumno['carrera'] == carrera_sel]
            df_alumno_resumen = procesar_kardex(df_alumno_carrera, umbral_reprobacion)   # metricas de un solo alumno con 1 0 2 carreras para prediccion de ries
        else:
            df_alumno_carrera = df_alumno
    
    else:
  #      id_carrera = num_carreras['id_carrera'].iloc[0]
        df_alumno_carrera = df_alumno
        df_alumno_resumen = procesar_kardex(df_alumno_carrera, umbral_reprobacion) 

    # materias filtradas por matrícula Y carrera
  #  st.write("id_carrera", id_carrera)
 #   df_alumno_carrera = df_alumno[df_alumno['carrera'] == id_carrera]

    # 3. Código del Análisis por Periodo
  #  st.subheader(f"Análisis de Rendimiento por Periodo")
    
    # Agrupamos para obtener el promedio por periodo
  #  df_stats_periodo = df_periodos.groupby('id_periodo').agg({
 #       'calificacion': 'mean',
 #       'materia': 'count'
 #   }).reset_index()
    
    ####################### INFORMACION GENERAL ############################################333


    if not df_alumno_carrera.empty:
         # 1. INFORMACIÓN GENERAL (Encabezado)
        nombre_alumno = df_alumno_carrera['nombre'].iloc[0] if 'nombre' in df_alumno_carrera.columns else "Estudiante"
        carrera_alumno = df_alumno_carrera['carrera'].iloc[0]
        df_materias_aprobadas = df_alumno_carrera[df_alumno_carrera['calificacion'] > umbral_reprobacion]
        
        st.title(f"📂 Expediente: {nombre_alumno}")
        st.info(f"**Matrícula:** {matricula} | **Carrera:** {carrera_alumno}")

        # 2. MÉTRICAS RESUMIDAS (KPIs)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Promedio General", f"{df_alumno_carrera['calificacion'].mean():.2f}")
        with col2:
            st.metric("Materias Cursadas", len(df_materias_aprobadas))
        with col3:
        # Ejemplo si tienes columna de créditos
            total_creditos = df_materias_aprobadas['creditos_materia'].sum()         
            #if 'creditos' in df_materias_aprobadas.columns else 0
            st.metric("Créditos Totales", total_creditos)
 
        col1, col2, col3= st.columns(3)
        with col1:
            st.markdown(create_uabc_metric_card("Promedio general", f"{df_alumno_carrera['calificacion'].mean():.2f}", " ",icon=" "), unsafe_allow_html=True)
    
        with col2:
            st.markdown(create_uabc_metric_card("Materias cursadas", len(df_materias_aprobadas),  " ",icon=" "), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_uabc_metric_card("Creditos totales", total_creditos,  " ",icon=" "), unsafe_allow_html=True)  
    
        st.markdown("---")

        
        # 3. LISTA COMPLETA DE ASIGNATURAS (El Kardex)
        st.subheader("📚 Historial Académico Completo")
    
        # Seleccionamos solo las columnas que queremos mostrar al usuario
        columnas_mostrar = ['periodo', 'asignatura', 'calificacion', 'estatus_materia']
        # Verificamos que existan en el DF para evitar errores
        columnas_reales = [c for c in columnas_mostrar if c in df_alumno_carrera.columns]
    
        # Mostramos la tabla interactiva
        st.dataframe(
            df_alumno_carrera[columnas_reales],
            use_container_width=True,
            hide_index=True # Para que se vea más limpio
        )

    ################################ riesgo academico 
 #   score_riesgo, nivel = predecir_riesgo(df_alumno)


    # RIESGO
    if carrera_sel != "Todas las carreras":
        resultado_individual = identificar_riesgo_academico2(df_alumno_resumen, umbral_reprobacion, umbral_eficiencia, tasa, umbral_np_sp)
        if not resultado_individual.empty:
            status = resultado_individual.iloc[0] # Extraemos la única fila
    
            st.subheader(f"Análisis de Riesgo: {matricula} ")

            col_info1, col_info2 = st.columns(2)    
            with col_info1:
                st.markdown(create_uabc_alert(f"⚠️ Nivel de riesgo: {status['nivel_riesgo']} ", "metric"), unsafe_allow_html=True)
    
            with col_info2:
                
                st.markdown(create_uabc_alert(f" Motivo detectado: {status['motivo_riesgo']} ", "warning"), unsafe_allow_html=True)

   #         st.metric("Nivel de Riesgo", status['nivel_riesgo'])
   #         st.warning(f"Motivos detectados: {status['motivo_riesgo']}")
            st.info(f"Puntaje de Alerta: {status['alerta_score']}/100")

     

render_footer()