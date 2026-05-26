import streamlit as st
import plotly.express as px
from src.queries import fetch_analisis_reprobacion, fetch_carreras_alumno, get_data_analisis_completo
from src.utils import load_css, create_uabc_metric_card, render_header, render_footer

load_css()
render_header()

# No necesitas volver a llamar a queries.py
if 'df_raw' in st.session_state:
    df = st.session_state.df_raw
    st.write("Datos recuperados de la sesión con éxito.")
    # Aquí ya puedes usar df para tus gráficas de carrera
else:
    st.warning("Por favor, inicia la aplicación en la página principal para cargar los datos.")


with st.sidebar:
    st.image("assets/UABC-logo.png", width=150)
    st.markdown("### Panel de Control")
    st.sidebar.page_link("streamlit_app.py", label="Inicio", icon="🏠")
    st.page_link("pages/carreras.py", label="Carreras", icon="📊") # APARECE DESPUÉS
    st.page_link("pages/perfil_alumnos.py", label="Perfil de Alumnos", icon="🎓") # APARECE DESPUÉS
    st.page_link("pages/riesgo_academico.py", label="Riesgo Académico", icon="🚨") # APARECE DESPUÉS
        
    st.markdown("---")
    st.markdown("### ⚙️ Configuración")
    
     # Filtro de carrera
    lista_carreras = ["Todos las carreras"] + sorted(df['carrera'].unique().tolist())
    carrera_sel = st.selectbox("📚 Seleccione carrera", lista_carreras)
    
     # Filtro de Periodo
    lista_periodos = ["Todos los periodos"] + sorted(df['periodo'].unique().tolist())
    periodo_sel = st.selectbox("📅 Seleccione Periodo Académico", lista_periodos)
    
    # Filtro de Umbral
    umbral = st.slider("Umbral de reprobación (Calificación)", 0, 100, 60)
        
    # Filtros adicionales
    mostrar_solo_riesgo = st.checkbox("⚠️ Mostrar solo alumnos en riesgo")
    mostrar_detalles = st.checkbox("📋 Mostrar detalles académicos")


    # Guardamos en session_state para que otras páginas lo usen
    st.session_state['carrera'] = carrera_sel   
    st.session_state['periodo'] = periodo_sel
    st.session_state['umbral_reprobacion'] = umbral
    st.session_state['mostrar_solo_riesgo'] = mostrar_solo_riesgo
    st.session_state['mostrar_detalles'] = mostrar_detalles



# ============================================== PROCESAMIENTO ============================================
if periodo_sel != "Todos los periodos":
    df_filtrado = df_raw[df_raw['periodo'] == periodo_sel]
else:
    df_filtrado = df_raw

df_final = procesar_academicos(df_filtrado, umbral)   #Segun perido y umbral seleccionado


# ============================================== MÉTRICAS PRINCIPALES ============================================
#st.title(f"Dashboard Académico - {periodo_sel}")
#m1, m2, m3, m4, m5 = st.columns(5)

total_alumnos = len(df_final)
sobresalientes = len(df_final[df_final['promedio_general'] >= 90])
en_riesgo = len(df_final[df_final['estatus'] == 'RIESGO'])

# ============================================CUERPO DEL DASHBOARD ============================================
st.title("📈 Análisis por Carrera")

# Supongamos que traemos los datos de la carrera seleccionada
df_carrera = fetch_analisis_reprobacion(id_carrera=st.session_state.get('id_carrera_sel'))

# --- CARDS DE METRICAS --
col1, col2, col3, col4, col5= st.columns(5)
with col1:
    st.markdown(create_uabc_metric_card("Total Alumnos", "1,200", icon="🎓"), unsafe_allow_html=True)
    
with col2:
 #   promedio = df['promedio_general'].mean()
 #   st.markdown(create_uabc_metric_card("Promedio General", f"{promedio:.1f}", "escala 0-100", "📊"), unsafe_allow_html=True)
    st.markdown(create_uabc_metric_card("Promedio General", "100", "escala 0-100", "📊"), unsafe_allow_html=True)
        
with col3:
  #  avance = df['porcentaje_avance'].mean()
  #  st.markdown(create_uabc_metric_card("Avance Crediticio", f"{avance:.1f}%", "del plan de estudios", "📈"), unsafe_allow_html=True)
    st.markdown(create_uabc_metric_card("Avance Crediticio", "30%", "del plan de estudios", "📈"), unsafe_allow_html=True)  

with col4:
 #   riesgo = len(df[df['estatus'].isin(['RIESGO', 'REZAGADO'])])
 #   porcentaje_riesgo = (riesgo/len(df))*100 if len(df) > 0 else 0
 #   st.markdown(create_uabc_metric_card("En Riesgo", riesgo, f"{porcentaje_riesgo:.0f}% del total", "⚠️"), unsafe_allow_html=True)
   st.markdown(create_uabc_metric_card("En Riesgo", "50", "50% del total", "⚠️"), unsafe_allow_html=True)
        
with col5:
 #   extras = df['examenes_regularizacion'].mean()
   # st.markdown(create_uabc_metric_card("Extraordinarios", f"{extras:.1f}", "promedio por alumno", "📝"), unsafe_allow_html=True)
    st.markdown(create_uabc_metric_card("Extraordinarios", "2", "promedio por alumno", "📝"), unsafe_allow_html=True)
    
st.markdown("---")


if not df_carrera.empty:  # Si hay datos para la carrera seleccionada
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




render_footer()