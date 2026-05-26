import streamlit as st
import pandas as pd
from src.utils import load_css, render_header, render_footer, create_uabc_metric_card, create_uabc_alert
from src.queries import fetch_analisis_reprobacion, get_kardex_alumno, get_data_analisis_completo
from src.analisis import calcular_indice_riesgo, procesar_academicos
import numpy as np
import plotly.express as px


st.set_page_config(page_title="Dashboard Académico - FCQI", layout="wide")
load_css()    # Cargamos los estilos personalizados
render_header()   # Renderizamos el header común a todas las páginas


# ============================================
# CARGA DE DATOS
# ============================================
# Extracción inicial
df_raw = get_data_analisis_completo()

# --- SIDEBAR COMPARTIDO ---
with st.sidebar:
    st.image("assets/UABC-logo.png", width=150)
    st.markdown("### Panel de Control")
    st.sidebar.page_link("streamlit_app.py", label="Inicio", icon="🏠")
    st.page_link("pages/carreras.py", label="Carreras", icon="📊") # APARECE DESPUÉS
    st.page_link("pages/perfil_alumnos.py", label="Perfil de Alumnos", icon="🎓") # APARECE DESPUÉS
    st.page_link("pages/riesgo_academico.py", label="Riesgo Académico", icon="🚨") # APARECE DESPUÉS
        
    st.markdown("---")
    st.markdown("### ⚙️ Configuración")
     # Filtro de Periodo
    lista_periodos = ["Todos los periodos"] + sorted(df_raw['periodo'].unique().tolist())
    periodo_sel = st.selectbox("Seleccione Periodo Académico", lista_periodos)
    
    # Filtro de Umbral
    umbral = st.slider("Umbral de reprobación (Calificación)", 0, 100, 60)

    mostrar_solo_riesgo = st.checkbox("⚠️ Mostrar solo alumnos en riesgo")
    mostrar_detalles = st.checkbox("📋 Mostrar detalles académicos")


    # Guardamos en session_state para que otras páginas lo usen
 #   st.session_state['carrera'] = carrera_global
    st.session_state['periodo'] = periodo_sel
    st.session_state['umbral_reprobacion'] = umbral
    st.session_state['mostrar_solo_riesgo'] = mostrar_solo_riesgo
    st.session_state['mostrar_detalles'] = mostrar_detalles




# --- PROCESAMIENTO ---
if periodo_sel != "Todos los periodos":
    df_filtrado = df_raw[df_raw['periodo'] == periodo_sel]
else:
    df_filtrado = df_raw

df_final = procesar_academicos(df_filtrado, umbral)

# --- MÉTRICAS PRINCIPALES ---
#st.title(f"Dashboard Académico - {periodo_sel}")
#m1, m2, m3, m4, m5 = st.columns(5)

total_alumnos = len(df_final)
sobresalientes = len(df_final[df_final['promedio_general'] >= 90])
en_riesgo = len(df_final[df_final['estatus'] == 'RIESGO'])

#m1.metric("Total Alumnos", total_alumnos)
#m2.metric("Promedio General", f"{df_final['promedio_general'].mean():.1f}")
#m3.metric("Avance Créditos (Avg)", f"{df_final['avance_porcentaje'].mean():.1f}%")
#m4.metric("Sobresalientes", sobresalientes)
#m5.metric("En Riesgo", en_riesgo)



# --- CUERPO DEL DASHBOARD ---
st.title("📊 Visión General")

# Ejemplo de cómo usar las métricas ahora:
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
   st.markdown(create_uabc_metric_card("En Riesgo", en_riesgo, f"{(en_riesgo/total_alumnos)*100:.0f}% del total", "⚠️"), unsafe_allow_html=True)
        
with col5:
 #   extras = df['examenes_regularizacion'].mean()
   # st.markdown(create_uabc_metric_card("Extraordinarios", f"{extras:.1f}", "promedio por alumno", "📝"), unsafe_allow_html=True)
    st.markdown(create_uabc_metric_card("Extraordinarios", f"{df_final['examenes_regularizacion'].mean():.1f}", "promedio por alumno", "📝"), unsafe_allow_html=True)
    
st.markdown("---")

 # Alertas destacadas
col_info1, col_info2 = st.columns(2)
    
with col_info1:
  #  excelentes = len(df[df['promedio_general'] >= 90])
 #   excelentes = 100
  #  if excelentes > 0:
    st.markdown(create_uabc_alert(f"🎉 {sobresalientes} alumnos con promedio sobresaliente (≥90)", "success"), unsafe_allow_html=True)
    
with col_info2:
 #   riesgo_count = len(df[df['estatus'].isin(['RIESGO', 'REZAGADO'])])
 #   riesgo_count = 50
    if en_riesgo > 0:
        st.markdown(create_uabc_alert(f"⚠️ Se han identificado {en_riesgo} alumnos en situación de riesgo académico", "warning"), unsafe_allow_html=True)
    
st.markdown("---")

# ... Aquí van tus gráficas de Plotly ...
# --- GRÁFICAS ---
col_izq, col_der = st.columns(2)

with col_izq:
    # 1. Histograma interactivo
    fig1 = px.histogram(df_final, x="promedio_general", nbins=30,
                        title='📊 Distribución de Calificaciones',
                        color_discrete_sequence=['#003366'])
    st.plotly_chart(fig1, use_container_width=True)

    # 2. Pie Chart: Proporción de Estatus
    color_map = {'ACTIVO': '#4CAF50', 'REGULAR': '#2196F3', 'RIESGO': '#FF9800', 'REZAGADO': '#F44336'}
    fig2 = px.pie(df_final, names='estatus', title='🎯 Distribución por Estatus Académico',
                  color='estatus', color_discrete_map=color_map)
    st.plotly_chart(fig2, use_container_width=True)

with col_der:
    # 3. Scatter Plot 4D
    # X: Créditos, Y: Promedio, Color: Estatus, Size: Extraordinarios
    fig3 = px.scatter(df_final, x='creditos_cursados', y='promedio_general',
                      color='estatus', size='conteo_extraordinarios',
                      title='📈 Relación: Créditos vs Promedio (4D)',
                      color_discrete_map=color_map,
                      hover_data=['carrera'])
    st.plotly_chart(fig3, use_container_width=True)

    # 4. Bar Chart: Volumen por Plan de Estudios (Escala continua)
    plan_data = df_final['id_plan_estudio'].value_counts().reset_index()
    fig4 = px.bar(plan_data, x='id_plan_estudio', y='count',
                  color='count', color_continuous_scale='Blues',
                  title='📚 Volumen por Plan de Estudios')
    st.plotly_chart(fig4, use_container_width=True)





render_footer()