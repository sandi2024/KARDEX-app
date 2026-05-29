import streamlit as st
from src.queries import fetch_analisis_reprobacion, get_data_completo
from src.analisis import calcular_indice_riesgo, normalizar_datos_academicos, procesar_kardex, identificar_riesgo_academico
from src.utils import load_css, render_header, create_uabc_metric_card, render_footer
import pandas as pd


load_css()
render_header()

############################# CARGAR DATOS ##############################
# No necesitas volver a llamar a queries.py
if 'df_raw' not in st.session_state or st.session_state.df_raw.empty:
    st.session_state.df_raw = get_data_completo()
    df_datos = st.session_state.df_raw
    st.warning("VACIO")  
else:
    df_datos = st.session_state.df_raw
    st.write("Datos recuperados de la sesión con éxito.")
    # Aquí ya puedes usar df para tus gráficas de carrera


# ======================== SIDEBAR COMPARTIDO ==================================
with st.sidebar:
    st.image("assets/UABC-logo.png", width=150)
    st.markdown("### Panel de Control")
    st.sidebar.page_link("streamlit_app.py", label="Inicio", icon="🏠")
    st.page_link("pages/carreras.py", label="Carreras", icon="📊") # APARECE DESPUÉS
    st.page_link("pages/perfil_alumnos.py", label="Perfil de Alumnos", icon="🎓") # APARECE DESPUÉS
    st.page_link("pages/riesgo_academico.py", label="Riesgo Académico", icon="🚨") # APARECE DESPUÉS
        
    st.markdown("---")
    st.markdown("### ⚙️ Configuración")
        
    # Filtros adicionales
    lista_carreras = ["Todas las carreras"] + sorted(df_datos['carrera'].unique().tolist())
    carrera_sel = st.selectbox("📚 Seleccione carrera", lista_carreras)
    

    umbral_reprobacion = st.slider("Umbral de promedio critico", 0, 100, 60)
    umbral_eficiencia = st.slider("Creditos promedio por periodo", 0, 100, 60)
    umbral_np_sp = st.slider("Limite de examenes NP ySD", 0, 100, 60)

    mostrar_solo_riesgo = st.checkbox("⚠️ Mostrar solo alumnos en riesgo")
    mostrar_detalles = st.checkbox("📋 Mostrar detalles académicos")


    # Guardamos en session_state para que otras páginas lo usen
    st.session_state['carrera'] = carrera_sel
    st.session_state['umbral_reprobacion'] = umbral_reprobacion
    st.session_state['umbral_eficiencia'] = umbral_eficiencia
    st.session_state['umbral_np_sp'] = umbral_np_sp
    st.session_state['mostrar_solo_riesgo'] = mostrar_solo_riesgo
    st.session_state['mostrar_detalles'] = mostrar_detalles



# ============================================== PROCESAMIENTO ============================================

if carrera_sel != "Todos las carreras":
    df_filtrado = df_datos[df_datos['carrera'] == carrera_sel]
else:
    df_filtrado = df_datos

df_norm = normalizar_datos_academicos(df_filtrado)
df_resumen = procesar_kardex(df_norm, umbral_reprobacion)
df_con_riesgo = identificar_riesgo_academico(df_resumen, umbral_reprobacion, umbral_eficiencia, umbral_np_sp)

#============================================CUERPO DEL DASHBOARD ============================================

st.title("🚨 Sistema de Alerta Temprana")

# Traemos todos los datos de la facultad (o por carrera)
#df_riesgo = fetch_analisis_reprobacion()

# Aplicamos el análisis a cada alumno único
#resumen_riesgo = []
#for matricula in df_riesgo['matricula'].unique():
#    historial = df_riesgo[df_riesgo['matricula'] == matricula]
#    analisis = calcular_indice_riesgo(historial)
#    resumen_riesgo.append({
#        "Matrícula": matricula,
#        "Nivel de Riesgo": analisis['nivel'],
#        "Score": analisis['score']
#    })

#df_final = pd.DataFrame(resumen_riesgo)

# Visualización
#col1, col2 = st.columns([1, 2])

#with col1:
#    st.write("### Distribución de Riesgo")
#    conteo = df_final['Nivel de Riesgo'].value_counts()
#    st.bar_chart(conteo)

#with col2:
#    st.write("### Alumnos que requieren intervención")
#    st.dataframe(df_final.sort_values("Score", ascending=False), use_container_width=True)

# Mostrar métricas de resumen
col1, col2 = st.columns(2)
col1.metric("Alumnos en Riesgo Crítico", len(df_con_riesgo[df_con_riesgo['nivel_riesgo'] == 'Crítico']))
col2.metric("Alumnos en Riesgo Moderado", len(df_con_riesgo[df_con_riesgo['nivel_riesgo'] == 'Moderado']))

# Mostrar tabla filtrada (Solo Críticos y Moderados)
st.dataframe(
    df_con_riesgo[df_con_riesgo['nivel_riesgo'] != 'Bajo'],
    use_container_width=True
)
render_footer()