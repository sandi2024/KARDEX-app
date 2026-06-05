import streamlit as st
import plotly.express as px
from src.database import get_data_completo
from src.utils import get_image_base64, load_css, render_header, create_uabc_metric_card, render_footer, create_uabc_alert     
from src.analisis import existe_matricula, normalizar_datos_academicos, identificar_riesgo_academico2, procesar_kardex


# ------------------------- SIDEBAR COMPARTIDO -------------------------------
def render_sidebar():
    with st.sidebar:
        logo_base64 = get_image_base64("assets/UABC-logo.png")
        logo_html = f'<img src="data:image/jpeg;base64,{logo_base64}" alt="UABC" style="height: 200px;">' if logo_base64 else '<div style="height: 80px;"></div>'
        st.markdown(f"""
               <div class="sidebar-logo">
                   {logo_html}
                   <p style="font-size: 1.2rem; color: #666;">UABC</p>
               </div>
               """, unsafe_allow_html=True)
        st.markdown("<div class='sidebar-title'> Panel de Control</div>", unsafe_allow_html=True)
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
    
        return umbral_reprobacion, umbral_eficiencia, umbral_np_sp, tasa


load_css()
render_header()

df_datos = get_data_completo()
umbral_reprobacion, umbral_eficiencia, umbral_np_sp, tasa = render_sidebar()
#============================ PROCESAR DATOS ================================

df_limpio = normalizar_datos_academicos(df_datos)

# ============================================CUERPO DEL DASHBOARD ============================================
st.title("📈 Consulta Alumnos")

matricula = st.text_input("Ingresar matrícula:")

if matricula:
    if existe_matricula(df_limpio, matricula):

        df_alumno =  df_limpio[df_limpio['matricula'] == matricula].sort_values('periodo')  
        num_carreras = df_alumno['carrera'].nunique()
        num_planes = df_alumno['id_plan_estudio'].nunique() 
    
        if num_carreras > 1:
            st.warning("⚠️ Este alumno tiene registros en múltiples carreras.")
 
            lista_carreras = ["Todas las carreras"] + sorted(df_alumno['carrera'].unique().tolist())
            carrera_sel = st.selectbox("📚 Seleccione carrera", lista_carreras)
        else:
            carrera_sel = df_alumno['carrera'].iloc[0]
        
        #-------------------- INFORMACION GENERAL ----------------------
        if carrera_sel != "Todas las carreras" and num_carreras > 1:
            df_alumno_carrera = df_alumno[df_alumno['carrera'] == carrera_sel]
        else:
            df_alumno_carrera = df_alumno

        df_alumno_resumen = procesar_kardex(df_alumno_carrera, umbral_reprobacion)   # metricas de un solo alumno con 1 0 2 carreras para prediccion de riesgo academico

        if not df_alumno_carrera.empty:
         # 1. INFORMACIÓN GENERAL (Encabezado)
            nombre_alumno = df_alumno_carrera['nombre'].iloc[0] if 'nombre' in df_alumno_carrera.columns else "Estudiante"
            df_materias_aprobadas = df_alumno_carrera[df_alumno_carrera['calificacion'] >= umbral_reprobacion]
            total_creditos = df_materias_aprobadas['creditos_materia'].sum() if 'creditos_materia' in df_alumno_carrera.columns else 0
            plan_estudio = df_alumno_carrera['nombre_plan'].iloc[0] if 'nombre_plan' in df_alumno_carrera.columns else "Desconocido"

            st.subheader(f"📂 Expediente: {nombre_alumno}")
            st.info(f"**Matrícula:** {matricula}  |  **Carrera:** {carrera_sel}")

            # MÉTRICAS RESUMIDAS 
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

    #-------------------------  RIESGO ACADEMICO ---------------------------------
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
    else:
        st.error("❌ La matrícula no existe en el sistema")

render_footer()