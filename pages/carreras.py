import streamlit as st
import plotly.express as px
from src.queries import fetch_analisis_reprobacion, fetch_carreras_alumno, get_data_analisis_completo
from src.utils import load_css, create_uabc_metric_card, render_header, render_footer, create_uabc_alert
from src.analisis import calcular_metricas_reprobacion, filtrar_datos, normalizar_datos_academicos, calcular_metricas_academicas, distribucion_calificaciones, calcular_evolucion_academica

load_css()
render_header()

# No necesitas volver a llamar a queries.py
if 'df_raw' not in st.session_state or st.session_state.df_raw.empty:
    st.session_state.df_raw = get_data_analisis_completo()
    df_datos = st.session_state.df_raw
    st.warning("VACIO")  
else:
    df_datos = st.session_state.df_raw
    st.write("Datos recuperados de la sesión con éxito.")
    # Aquí ya puedes usar df para tus gráficas de carrera

if st.session_state.df_raw.empty:
    st.warning("No se han encontrado datos para los filtros seleccionados.")

if df_datos.empty:
    st.warning("No se han encontrado datos df_datos.")

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
    lista_carreras = ["Todas las carreras"] + sorted(df_datos['carrera'].unique().tolist())
    carrera_sel = st.selectbox("📚 Seleccione carrera", lista_carreras)
    
     # Filtro de Periodo
    lista_periodos = ["Todos los periodos"] + sorted(df_datos['periodo'].unique().tolist())
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

df_limpio = normalizar_datos_academicos(df_datos)

if carrera_sel != "Todas las carreras":
    df_carrera = df_limpio[df_datos['carrera'] == carrera_sel]
else:
    df_carrera = df_limpio

df_filtrados = filtrar_datos(df_carrera, periodo_sel)
df_final = calcular_metricas_academicas(df_filtrados, umbral)   # Según periodo y umbral seleccionado

top_reprobadas = calcular_metricas_reprobacion(df_filtrados, umbral)

df_distribucion = distribucion_calificaciones(df_carrera)

# ============================================== MÉTRICAS PRINCIPALES ============================================

total_alumnos = len(df_final)
sobresalientes = len(df_final[df_final['promedio_general'] >= 90])
en_riesgo = len(df_final[df_final['estatus'] == 'RIESGO'])
extras = df_final['conteo_extraordinarios'].mean()

# ============================================CUERPO DEL DASHBOARD ============================================
st.title(f"📈 Análisis por Carrera - {carrera_sel}")

# --- CARDS DE METRICAS --
col1, col2, col3, col4, col5= st.columns(5)
with col1:
    st.markdown(create_uabc_metric_card("Total Alumnos", total_alumnos, icon="🎓"), unsafe_allow_html=True)
    
with col2:
 #   promedio = df['promedio_general'].mean()
 #   st.markdown(create_uabc_metric_card("Promedio General", f"{promedio:.1f}", "escala 0-100", "📊"), unsafe_allow_html=True)
    st.markdown(create_uabc_metric_card("Promedio General", f"{df_final['promedio_general'].mean():.1f}", "escala 0-100", "📊"), unsafe_allow_html=True)
        
with col3:
  #  avance = df['porcentaje_avance'].mean()
  #  st.markdown(create_uabc_metric_card("Avance Crediticio", f"{avance:.1f}%", "del plan de estudios", "📈"), unsafe_allow_html=True)
    st.markdown(create_uabc_metric_card("Avance Crediticio", f"{df_final['avance_porcentaje'].mean():.1f}%", "del plan de estudios", "📈"), unsafe_allow_html=True)  

with col4:
 #   riesgo = len(df[df['estatus'].isin(['RIESGO', 'REZAGADO'])])
 #   porcentaje_riesgo = (riesgo/len(df))*100 if len(df) > 0 else 0
 #   st.markdown(create_uabc_metric_card("En Riesgo", riesgo, f"{porcentaje_riesgo:.0f}% del total", "⚠️"), unsafe_allow_html=True)
   st.markdown(create_uabc_metric_card("En Riesgo", f"{(en_riesgo/total_alumnos)*100:.0f}%", "del total", "⚠️"), unsafe_allow_html=True)
        
with col5:
 #   extras = df['examenes_regularizacion'].mean()
   # st.markdown(create_uabc_metric_card("Extraordinarios", f"{extras:.1f}", "promedio por alumno", "📝"), unsafe_allow_html=True)
    st.markdown(create_uabc_metric_card("Extraordinarios", f"{extras:.1f}", "promedio por alumno", "📝"), unsafe_allow_html=True)
    
st.markdown("---")

 # Alertas destacadas
col_info1, col_info2 = st.columns(2) 
with col_info1:
    if sobresalientes > 0:
        st.markdown(create_uabc_alert(f"🎉 {sobresalientes} alumnos con promedio sobresaliente (≥90)", "success"), unsafe_allow_html=True)
    
with col_info2:
    if en_riesgo > 0:
        st.markdown(create_uabc_alert(f"⚠️ Se han identificado {en_riesgo} alumnos en situación de riesgo académico", "warning"), unsafe_allow_html=True)
    
st.markdown("---")

if not df_final.empty:  # Si hay datos para la carrera seleccionada
    
    if top_reprobadas.sum() < 2:
        st.info("ℹ️ Solo se registra 1 alumno reprobado en este periodo/carrera.")
    else:
        # --- Gráfica de Barras: Top Materias Reprobadas ---
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
    st.subheader("Análisis Carrera-Periodo")  
    # Pivotamos los datos para el mapa de calor
    df_pivot = df_carrera.groupby(['periodo', 'carrera'])['calificacion'].mean().unstack()
    fig_heat = px.imshow(
        df_pivot,
        labels=dict(x="Carrera", y="Periodo", color="Promedio"),
        color_continuous_scale='RdYlGn', # Rojo a Verde
        title="Rendimiento Promedio por Periodo y Carrera"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # ---------- DISTRIBUCION CALIFICACION
    st.subheader("📊 Distribución de Calificaciones")
    if not df_distribucion.empty:
        fig_hist = px.histogram(
            df_distribucion,
            x="calificacion",
            nbins=20,
            title="Frecuencia de Calificaciones",
            labels={'calificacion': 'Calificación', 'count': 'Cantidad de Registros'},
            color_discrete_sequence=['#636EFA']
        )
        # Añadir una línea vertical en el umbral de aprobación
        fig_hist.add_vline(x=umbral, line_dash="dash", line_color="red", 
                          annotation_text=f"Umbral: {umbral}")
        
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("ℹ️ No hay calificaciones para mostrar.")


    df_evo = calcular_evolucion_academica(df_limpio, umbral)

    if not df_evo.empty:
        fig_evolucion = px.line(
            df_evo,
            x='periodo',
            y=['porcentaje_reprobacion', 'promedio_periodo'], # Graficamos ambas columnas
            title="Evolución: Reprobación vs Promedio General",
            markers=True,
            line_shape="linear", #
            labels={
                'value': 'Escala 0-100',
                'periodo': 'Periodo',
                'variable': 'Métrica'
            },
            color_discrete_map={
                'porcentaje_reprobacion': 'red',
                'promedio_periodo': 'blue'
            }
        )

        # Mejoramos la estética
        fig_evolucion.update_layout(
            yaxis_range=[0, 105],
            legend_title="Indicadores",
           hovermode="x unified" # Muestra ambos valores al pasar el mouse
        )

        st.plotly_chart(fig_evolucion, use_container_width=True)


else:
    st.warning("ℹ️ No hay datos disponibles para los filtros seleccionados.")

render_footer()