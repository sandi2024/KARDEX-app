import streamlit as st
import pandas as pd
from src.utils import get_image_base64, load_css, render_header, render_footer, create_uabc_metric_card, create_uabc_alert
from src.database import get_data_completo
from src.analisis import normalizar_datos_academicos, calcular_metricas_generales, obtener_lista_periodos, procesar_kardex_general
import plotly.express as px
import numpy as np
import plotly.graph_objects as go


# --- SIDEBAR  ---
def render_sidebar(lista_periodos: list[str], lista_periodos_base: list[str]):
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

        st.sidebar.page_link("streamlit_app.py", label="<div class='sidebar-link'>Inicio</div>", icon="🏠")
        st.page_link("pages/carreras.py", label="Carreras", icon="🎓") # APARECE DESPUÉS
        st.page_link("pages/perfil_alumnos.py", label="Perfil de Alumnos", icon="🧑‍🎓") # APARECE DESPUÉS
        st.page_link("pages/riesgo_academico.py", label="Riesgo Académico", icon="🚨") # APARECE DESPUÉS
        
        st.markdown("---")
    
    
        st.markdown("### ⚙️ Configuración")
        mostrar_intervalo_periodo = st.checkbox(" Filtra periodo por intervalos ")
        if mostrar_intervalo_periodo:
            rango_periodos = st.select_slider(
                    "Selecciona el intervalo de periodos",
                    options=lista_periodos_base,
                    value=(lista_periodos_base[0], lista_periodos_base[-1])
            )
            # Variable auxiliar interna del formulario para saber qué se seleccionó
            periodo_sel = None 
        else:
            periodo_sel = st.selectbox("📅 Seleccione Periodo Académico", lista_periodos)
            rango_periodos = None
        
        umbral = st.slider("Umbral de reprobación (Calificación)", 0, 100, 60)
        max_extraordinarios = st.slider("No. max extraordinario", 0, 10, 3)
        
        
        if mostrar_intervalo_periodo:
            st.session_state['periodo'] = rango_periodos
        else:
            st.session_state['periodo'] = periodo_sel
        st.session_state['umbral_reprobacion'] = umbral
        st.session_state['max_extraordinarios'] = max_extraordinarios
        return periodo_sel, umbral, max_extraordinarios, mostrar_intervalo_periodo, rango_periodos



st.set_page_config(page_title="Dashboard Académico - FCQI", layout="wide")
load_css()    # Cargamos los estilos personalizados
render_header()   # Renderizamos el header común a todas las páginas


df_datos = get_data_completo()
lista_periodos_base = obtener_lista_periodos(df_datos)
lista_periodos = ["Todos los periodos"] + lista_periodos_base
periodo_sel, umbral, max_extraordinarios, mostrar_intervalo_periodo, rango_periodos = render_sidebar(lista_periodos, lista_periodos_base)

# ============================================== PROCESAMIENTO ============================================
if  mostrar_intervalo_periodo:
    df_filtrado = df_datos[(df_datos['periodo'] >= rango_periodos[0]) & (df_datos['periodo'] <= rango_periodos[1])]
else:
    if periodo_sel != "Todos los periodos":
        df_filtrado = df_datos[df_datos['periodo'] == periodo_sel]
    else:
        df_filtrado = df_datos

df_norm = normalizar_datos_academicos(df_filtrado)
df_final = procesar_kardex_general(df_norm, umbral, max_extraordinarios)

# ============================================== MÉTRICAS PRINCIPALES ============================================

metricas = calcular_metricas_generales(df_final)

# ===================================== CUERPO DEL DASHBOARD ===========================================
st.title(f" Visión General del Rendimiento Académico {periodo_sel if periodo_sel != 'Todos los periodos' else ' ' + rango_periodos[0] + '/' + rango_periodos[1] if mostrar_intervalo_periodo else ''}")

# METRICAS DESTACADAS
col1, col2, col3, col4, col5= st.columns(5)
with col1:
    st.markdown(create_uabc_metric_card("Total Alumnos", metricas["total_alumno"], " ",icon="🎓"), unsafe_allow_html=True)
    
with col2:
    st.markdown(create_uabc_metric_card("Promedio General", f"{metricas["promedio_general"]:.1f}", "escala 0-100", "📊"), unsafe_allow_html=True)
        
with col3:
    st.markdown(create_uabc_metric_card("Avance Crediticio", f"{metricas["avance_porcentaje"]:.1f}", "promedio de avance", "📈"), unsafe_allow_html=True)  

with col4:
   st.markdown(create_uabc_metric_card("En Riesgo",f"{metricas["porcentaje_riesgo"]:.0f}%", "del total", "⚠️"), unsafe_allow_html=True)
        
with col5:
    st.markdown(create_uabc_metric_card("Extraordinarios", f"{metricas["promedio_ext"]:.2f}", "promedio por alumno", "📝"), unsafe_allow_html=True)
    
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

# ========================== GRÁFICAS ===============================================
col_izq, col_der = st.columns(2)

with col_izq:
    # 1. Histograma interactivo
    fig1 = px.histogram(df_final, x="promedio_final", nbins=30,
                        title='📊 Distribución de Calificaciones',
                        color_discrete_sequence=['#003366'])
    st.plotly_chart(fig1, use_container_width=True)

    # 2. Pie Chart: Proporción de Estatus
    color_map = {'EXCELENTE': '#4CAF50', 'REGULAR': '#2196F3', 'RIESGO': '#FF9800', 'REZAGADO': '#F44336'}
    fig2 = px.pie(df_final, names='estatus', title='🎯 Distribución por Estatus Académico',
                  color='estatus', color_discrete_map=color_map)
    st.plotly_chart(fig2, use_container_width=True)

with col_der:
     
     # Avance crediticio
    fig2 = px.scatter(df_final, x='total_creditos_logrados', y='promedio_final',
                         color='estatus', size='conteo_extraordinarios',
                         title='📈 Relación: Créditos vs Promedio',
                         labels={'creditos_cursados': 'Créditos Cursados', 
                                'promedio_final': 'Promedio General'},
                         color_discrete_map={'SOBRESALIENTE': '#4CAF50', 'REGULAR': '#2196F3', 
                                           'RIESGO': '#FF9800', 'REZAGADO': '#F44336'})
    fig2.update_layout(height=400, plot_bgcolor='white')
    st.plotly_chart(fig2, use_container_width=True)
    

    # 4. Bar Chart: Volumen por Plan de Estudios (Escala continua)
    plan_data = df_final['plan_estudio'].value_counts().reset_index()
    fig4 = px.bar(plan_data, x='plan_estudio', y='count',
                  color='count', color_continuous_scale='Blues',
                  title='📚 Volumen por Plan de Estudios')
    fig4.update_layout(xaxis=dict(type='category'))
    st.plotly_chart(fig4, use_container_width=True)


st.markdown("---")

st.markdown("### Rendimiento por Carrera")   
columna1, columna2 = st.columns(2)

with columna1:
     # Gráfico de promedios por carrera 
    carrera_promedio = df_final.groupby('carrera')['promedio_final'].mean().sort_values(ascending=False)
    fig5 = px.bar(x=carrera_promedio.values, y=carrera_promedio.index,
                orientation='h', title='Promedio General por Carrera',
                color=carrera_promedio.values, color_continuous_scale='Blues',
                    labels={'x': 'Promedio General', 'y': 'Carrera'})
    fig5.update_layout(height=400, plot_bgcolor='white')
    st.plotly_chart(fig5, use_container_width=True)

with columna2:
    # Tabla de métricas por carrera
    metrics_table = df_final.groupby('carrera').agg({
        'promedio_final': 'mean',
        'avance_porcentaje': 'mean',
        'conteo_extraordinarios': 'mean'
    }).round(2)
    metrics_table.columns = ['📊 Promedio', '📈 Avance Promedio', '📝 Extraordinarios']
    st.dataframe(metrics_table.style.background_gradient(subset=['📊 Promedio'], cmap='Blues'))
    
    
# Gráfico comparativo 
st.markdown("###  Comparativa de Indicadores")
carrera_metrics = df_final.groupby('carrera').agg({
        'promedio_final': 'mean',
        'avance_porcentaje': 'mean'
    }).reset_index()
    
fig6 = go.Figure()
fig6.add_trace(go.Bar(name='Promedio General', x=carrera_metrics['carrera'], 
                          y=carrera_metrics['promedio_final'], marker_color='#003366'))
fig6.add_trace(go.Bar(name='Avance %', x=carrera_metrics['carrera'], 
                          y=carrera_metrics['avance_porcentaje'], marker_color='#C5A35E'))
fig6.update_layout(title='Comparativa por Carrera', barmode='group', height=400,
                      plot_bgcolor='white')
st.plotly_chart(fig6, use_container_width=True)


render_footer()