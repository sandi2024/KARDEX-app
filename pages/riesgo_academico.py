import streamlit as st
from src.database import get_data_completo
from src.analisis import normalizar_datos_academicos, obtener_lista_carreras, procesar_kardex, identificar_riesgo_academico2
from src.utils import get_image_base64, load_css, render_header, create_uabc_metric_card, render_footer, create_uabc_alert, create_progress_bar
import pandas as pd

# ======================== SIDEBAR COMPARTIDO ==================================
def render_sidebar(lista_carreras: list[str]):
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
        st.page_link("pages/carreras.py", label="Carreras", icon="🎓") # APARECE DESPUÉS
        st.page_link("pages/perfil_alumnos.py", label="Perfil de Alumnos", icon="🧑‍🎓") # APARECE DESPUÉS
        st.page_link("pages/riesgo_academico.py", label="Riesgo Académico", icon="🚨") # APARECE DESPUÉS
        
        st.markdown("---")
        st.markdown("### ⚙️ Configuración")
        
       # Filtros adicionales
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
        st.session_state['ocultar_bajos'] = ocultar_bajos
        return carrera_sel, umbral_reprobacion, umbral_eficiencia, umbral_np_sp, tasa, mostrar_solo_criticos, mostrar_solo_moderados, ocultar_bajos
    

# ======================== CARGAR DATOS ==================================
load_css()
render_header()

df_datos = get_data_completo()
carrera_sel, umbral_reprobacion, umbral_eficiencia, umbral_np_sp, tasa, mostrar_solo_criticos, mostrar_solo_moderados, ocultar_bajos = render_sidebar(obtener_lista_carreras(df_datos))
lista_carreras = obtener_lista_carreras(df_datos)
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



st.markdown("Indices de riesgo academico")

col_metrica1, col_metrica2, col_metrica3 = st.columns(3)
with col_metrica1:
    peso_promedio = st.number_input(
        label="Define el peso del promedio (porcentaje):",
        min_value=0.0,      # Al usar .0, Streamlit sabe que es decimal
        max_value=100.0,
        value=40.0,
        step=0.50,          # Incrementos de 50 centavos
        format="%.2f",       # Fuerza a mostrar siempre 2 decimales
        key="peso_promedio"
    )

with col_metrica2:
# 2. Ejemplo con número decimal (Float)
    peso_abandono = st.number_input(
        label="Define el peso del abandono (porcentaje):",
        min_value=0.0,      # Al usar .0, Streamlit sabe que es decimal
        max_value=100.0,
        value=30.0,
        step=0.50,          # Incrementos de 50 centavos
        format="%.2f",       # Fuerza a mostrar siempre 2 decimales
        key="peso_abandono"
    )

with col_metrica3:
    peso_extra = st.number_input(
        label="Define el peso de los extraordinarios (porcentaje):",
        min_value=0.0,      # Al usar .0, Streamlit sabe que es decimal
        max_value=100.0,
        value=30.0,
        step=0.50,          # Incrementos de 50 centavos
        format="%.2f",       # Fuerza a mostrar siempre 2 decimales
        key="peso_extra"
    )

st.write(f"Total porcentaje: **{peso_promedio + peso_abandono + peso_extra}%**")

# 2. Crear el botón que ejecutará la suma
if st.button("Nueva prediccion", type="primary"):
    # El código aquí adentro SOLO se ejecuta al hacer clic
    resultado = peso_promedio + peso_abandono + peso_extra
    
    # 3. Mostrar el resultado de forma visual
    st.success(f"¡Cálculo completado! El resultado es: **{resultado}**")







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