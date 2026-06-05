import streamlit as st
import plotly.express as px
from src.database import get_data_completo
from src.utils import get_image_base64, load_css, create_uabc_metric_card, render_header, render_footer, create_uabc_alert
from src.analisis import calcular_metricas_reprobacion, normalizar_datos_academicos, distribucion_calificaciones, calcular_evolucion_academica, obtener_lista_carreras, obtener_lista_periodos, procesar_kardex_general, calcular_metricas_generales


def render_sidebar(lista_periodos: list[str], lista_carreras: list[str], lista_periodos_base: list[str]):
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
    
        # Filtro de carrera
        carrera_sel = st.selectbox("📚 Seleccione carrera", lista_carreras)
    
      # Filtro de Periodo
        periodo_sel = st.selectbox("📅 Seleccione Periodo Académico", lista_periodos)

        mostrar_intervalo_periodo = st.checkbox(" Filtra periodo por intervalos ")
        if mostrar_intervalo_periodo:
            rango_periodos = st.select_slider(
                    "Selecciona el intervalo de periodos",
                    options=lista_periodos_base,
                    value=(lista_periodos_base[0], lista_periodos_base[-1])
            )
         # Filtro de Umbral
        umbral = st.slider("Umbral de reprobación (Calificación)", 0, 100, 60)
        max_extraordinarios = st.slider("No. max extraordinario", 0, 10, 3)


        # Guardamos en session_state para que otras páginas lo usen
        st.session_state['carrera'] = carrera_sel   
        st.session_state['periodo'] = periodo_sel
        st.session_state['umbral_reprobacion'] = umbral
        st.session_state['max_extraordinarios'] = max_extraordinarios

        return carrera_sel, periodo_sel, umbral, max_extraordinarios, mostrar_intervalo_periodo, rango_periodos



load_css()
render_header()

df_datos = get_data_completo()
lista_carreras = obtener_lista_carreras(df_datos)
lista_periodos_base = obtener_lista_periodos(df_datos)
lista_periodos = ["Todos los periodos"] + lista_periodos_base
carrera_sel, periodo_sel, umbral, max_extraordinarios, mostrar_intervalo_periodo, rango_periodos = render_sidebar(lista_periodos, lista_carreras, lista_periodos_base)
# ============================================== PROCESAMIENTO ============================================

df_limpio = normalizar_datos_academicos(df_datos)

if carrera_sel != "Todas las carreras":
    df_carrera = df_limpio[df_limpio['carrera'] == carrera_sel]
else:
    df_carrera = df_limpio


if mostrar_intervalo_periodo:
        df_periodo = df_carrera[(df_carrera['periodo'] >= rango_periodos[0]) & (df_carrera['periodo'] <= rango_periodos[1])]
else:
    if periodo_sel != "Todos los periodos":
        df_periodo = df_carrera[df_carrera['periodo'] == periodo_sel]
    else:
        df_periodo = df_carrera



df_final = procesar_kardex_general(df_periodo, umbral, max_extraordinarios)

top_reprobadas = calcular_metricas_reprobacion(df_periodo, umbral)

df_distribucion = distribucion_calificaciones(df_carrera)

#df_procesada = procesar_kardex_general(df_carrera, umbral, max_extraordinarios)
df_evo = calcular_evolucion_academica(df_carrera, umbral)

# ============================================== MÉTRICAS PRINCIPALES ============================================

metricas = calcular_metricas_generales(df_final)

# ============================================CUERPO DEL DASHBOARD ============================================
st.title(f"📈 Análisis por Carrera {carrera_sel if carrera_sel != 'Todas las carreras' else '' + rango_periodos[0] + '/' + rango_periodos[1] if mostrar_intervalo_periodo else ''}")

# --- CARDS DE METRICAS --
col1, col2, col3, col4, col5= st.columns(5)
with col1:
    st.markdown(create_uabc_metric_card("Total Alumnos", metricas["total_alumno"], icon="🎓"), unsafe_allow_html=True)
    
with col2:
    st.markdown(create_uabc_metric_card("Promedio General", f"{metricas["promedio_general"]:.1f}", "escala 0-100", "📊"), unsafe_allow_html=True)
        
with col3:
    st.markdown(create_uabc_metric_card("Avance Crediticio", f"{metricas["avance_porcentaje"]:.1f}%", "del plan de estudios", "📈"), unsafe_allow_html=True)  

with col4:
   st.markdown(create_uabc_metric_card("En Riesgo", f"{metricas["porcentaje_riesgo"]:.0f}%", "del total", "⚠️"), unsafe_allow_html=True)
        
with col5:
    st.markdown(create_uabc_metric_card("Extraordinarios", f"{metricas["promedio_ext"]:.1f}", "promedio por alumno", "📝"), unsafe_allow_html=True)
    
st.markdown("---")

 # Alertas destacadas
col_info1, col_info2 = st.columns(2) 
with col_info1:
    if metricas["sobresalientes"] > 0:
        st.markdown(create_uabc_alert(f"🏆 {metricas["sobresalientes"]} alumnos con promedio sobresaliente (≥90)", "success"), unsafe_allow_html=True)
    
with col_info2:
    if metricas["en_riesgo"] > 0:
        st.markdown(create_uabc_alert(f"⚠️ Se han identificado {metricas["en_riesgo"]} alumnos en situación de riesgo académico", "warning"), unsafe_allow_html=True)
    
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
  #  st.write(df_distribucion['calificacion'].unique())
  #  st.write(df_distribucion.columns)
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


   # df_evo = calcular_evolucion_academica(df_limpio, umbral)
  #  st.dataframe(df_evo)
    if not df_evo.empty:
        fig_evolucion = px.line(
            df_evo,
            x='periodo',
            y=['porcentaje_reprobacion', 'promedio_periodo'], # Graficamos ambas columnas
            title="Evolución: Reprobación vs Promedio General",
            markers=True,
            line_shape="spline", #
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
        fig_evolucion.update_layout(xaxis=dict(type='category'))
        st.plotly_chart(fig_evolucion, use_container_width=True)


else:
    st.warning("ℹ️ No hay datos disponibles para los filtros seleccionados.")

render_footer()