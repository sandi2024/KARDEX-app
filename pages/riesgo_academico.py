import streamlit as st
from src.database import get_data_completo
from src.analisis import normalizar_datos_academicos, procesar_kardex, identificar_riesgo_academico2
from src.utils import load_css, render_header, create_uabc_metric_card, render_footer, create_uabc_alert, create_progress_bar
import pandas as pd


load_css()
render_header()

############################# CARGAR DATOS ##############################
# No necesitas volver a llamar a queries.py
if 'df_raw' not in st.session_state or st.session_state.df_raw.empty:
    st.warning("Cargando datos desde la base de datos...")
    st.session_state.df_raw = get_data_completo()
    df_datos = st.session_state.df_raw
else:
    df_datos = st.session_state.df_raw


# ======================== SIDEBAR COMPARTIDO ==================================
with st.sidebar:
    st.image("assets/UABC-logo.png", width=150)
    st.markdown("### Panel de Control")
    st.sidebar.page_link("streamlit_app.py", label="Inicio", icon="🏠")
    st.page_link("pages/carreras.py", label="Carreras", icon="🎓") # APARECE DESPUÉS
    st.page_link("pages/perfil_alumnos.py", label="Perfil de Alumnos", icon="🧑‍🎓") # APARECE DESPUÉS
    st.page_link("pages/riesgo_academico.py", label="Riesgo Académico", icon="🚨") # APARECE DESPUÉS
        
    st.markdown("---")
    st.markdown("### ⚙️ Configuración")
        
    # Filtros adicionales
    lista_carreras = ["Todas las carreras"] + sorted(df_datos['carrera'].unique().tolist())
    carrera_sel = st.selectbox("📚 Seleccione carrera", lista_carreras)
    

    umbral_reprobacion = st.slider("Umbral de promedio critico", 0, 100, 60)
    umbral_eficiencia = st.slider("Creditos promedio por periodo", 0, 100, 40)
    umbral_np_sp = st.slider("Limite de examenes NP ySD", 0, 10, 5)
    tasa = st.slider("Tasa (%) extraordinarios", min_value=0, max_value=100, value=10, step=1)


    mostrar_solo_criticos = st.checkbox("🔴 Mostrar solo alumnos criticos")
    mostrar_solo_moderados = st.checkbox("🟡 Mostrar solo alumnos moderados")
    ocultar_bajos = st.checkbox("🟢 Ocultar solo alumnos de riesgo bajo")

    # Guardamos en session_state para que otras páginas lo usen
    st.session_state['carrera'] = carrera_sel
    st.session_state['umbral_reprobacion'] = umbral_reprobacion
    st.session_state['umbral_eficiencia'] = umbral_eficiencia
    st.session_state['umbral_np_sp'] = umbral_np_sp
    st.session_state['mostrar_solo_criticos'] = mostrar_solo_criticos
    st.session_state['mostrar_solo_moderados'] = mostrar_solo_moderados



# ============================================== PROCESAMIENTO ============================================

if carrera_sel != "Todas las carreras":
    df_filtrado = df_datos[df_datos['carrera'] == carrera_sel]
else:
    df_filtrado = df_datos


df_norm = normalizar_datos_academicos(df_filtrado)
df_resumen = procesar_kardex(df_norm, umbral_reprobacion)
df_con_riesgo = identificar_riesgo_academico2(df_resumen, umbral_reprobacion, umbral_eficiencia, tasa, umbral_np_sp)

#============================================CUERPO DEL DASHBOARD ============================================

st.title("🚨 Sistema de Alerta Temprana")

# Mostrar métricas de resumen
critico = len(df_con_riesgo[df_con_riesgo['nivel_riesgo'] == 'Crítico'])
moderado = len(df_con_riesgo[df_con_riesgo['nivel_riesgo'] == 'Moderado'])

col_info1, col_info2 = st.columns(2)    
with col_info1:
   if moderado > 0:
        st.markdown(create_uabc_alert(f"⚠️ Se han identificado {moderado} alumnos en situación de riesgo académico moderado", "warning"), unsafe_allow_html=True)
   #     st.markdown(create_progress_bar(moderado, type="warning"), unsafe_allow_html=True)
    
with col_info2:
    if critico > 0:
        st.markdown(create_uabc_alert(f"⚠️ Se han identificado {critico} alumnos en situación de riesgo académico critico", "warning"), unsafe_allow_html=True)
   #     st.markdown(create_progress_bar(critico, type="warning"), unsafe_allow_html=True)


st.markdown("---")

# Mostrar tabla filtrada (Solo Críticos y Moderados)
df_mostrar = df_con_riesgo.copy()

if  mostrar_solo_criticos:
    df_mostrar = df_mostrar[df_mostrar['nivel_riesgo'] == 'Crítico']

if  mostrar_solo_moderados:
    df_mostrar = df_mostrar[df_mostrar['nivel_riesgo'] == 'Moderado']

if ocultar_bajos:
    df_mostrar = df_mostrar[df_mostrar['nivel_riesgo'] != 'Bajo']

#  Imprimir el resultado
st.dataframe(
    df_mostrar,
    column_order=("id_estudiante", "nivel_riesgo", "alerta_score", "tasa_extraordinarios", "eficiencia_creditos"),
    use_container_width=True
)

render_footer()