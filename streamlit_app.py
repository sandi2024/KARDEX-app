import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import base64
from pathlib import Path

# Configuración de página
st.set_page_config(
    page_title="Dashboard Académico - FCQI | UABC",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ============================================
# FUNCIONES AUXILIARES
# ============================================

def load_css():
    """Carga el archivo CSS externo"""
    css_file = Path("assets/style.css")
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ No se encontró el archivo CSS. Verifica que 'assets/style.css' esté en el directorio.")

def get_image_base64(image_path):
    """Convierte una imagen a base64 para incrustar en HTML"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def create_uabc_metric_card(title, value, subtitle=None, icon="📊"):
    """Crea una tarjeta de métrica con estilos UABC"""
    return f'''
    <div class="metric-card-uabc">
        <h3>{icon} {title}</h3>
        <div class="metric-value">{value}</div>
        {f'<div class="metric-sub">{subtitle}</div>' if subtitle else ''}
    </div>
    '''

def create_uabc_alert(message, type="info"):
    """Crea una alerta con estilos UABC"""
    return f'<div class="alert-uabc alert-uabc-{type}">{message}</div>'

def create_uabc_badge(text, type="regular"):
    """Crea una badge con estilos UABC"""
    return f'<span class="badge-uabc badge-{type}">{text}</span>'

def create_progress_bar(percentage, type="success"):
    """Crea una barra de progreso"""
    return f'''
    <div class="progress-container">
        <div class="progress-bar-uabc progress-{type}" style="width: {percentage}%"></div>
    </div>
    '''

# ============================================
# CARGA DE DATOS
# ============================================

@st.cache_data
def load_sample_data():
    """Carga datos de ejemplo para el dashboard"""
    
    np.random.seed(42)  # Para reproducibilidad
    
    # Datos de alumnos
    students = pd.DataFrame({
        'matricula': [f'00{i}/46609' for i in range(1, 101)],
        'nombre': [f'Alumno_{i}' for i in range(1, 101)],
        'carrera': np.random.choice([
            'Ingeniería Química', 'Ingeniería Industrial', 
            'Química Farmacéutica', 'Ingeniería Ambiental',
            'Ingeniería en Alimentos', 'Licenciatura en Química'
        ], 100),
        'plan_estudios': np.random.choice(['1994-2', '2005-1', '2010-1', '2015-2', '2020-1'], 100),
        'promedio_general': np.random.normal(75, 12, 100).clip(0, 100),
        'creditos_cursados': np.random.randint(0, 400, 100),
        'creditos_requeridos': 326,
        'examenes_regularizacion': np.random.randint(0, 5, 100),
        'estatus': np.random.choice(['ACTIVO', 'REZAGADO', 'RIESGO', 'REGULAR'], 100, p=[0.5, 0.2, 0.2, 0.1])
    })
    
    # Calcular métricas adicionales
    students['creditos_faltantes'] = students['creditos_requeridos'] - students['creditos_cursados']
    students['porcentaje_avance'] = (students['creditos_cursados'] / students['creditos_requeridos']) * 100
    students['porcentaje_avance'] = students['porcentaje_avance'].clip(0, 100)
    
    return students

# ============================================
# FUNCIONES DE VISUALIZACIÓN
# ============================================

def render_header():
    """Renderiza el header institucional con el logo UABC"""
    
    # Intentar cargar el logo
    logo_base64 = get_image_base64("assets/UABC-logo.png")
    logo_html = f'<img src="data:image/jpeg;base64,{logo_base64}" alt="Logo UABC">' if logo_base64 else '<div style="width: 70px; height: 70px; background: #C5A35E; border-radius: 8px;"></div>'
    
    st.markdown(f"""
    <div class="uabc-header fade-in-up">
        <div class="header-content"> 
                
            <div class="logo-container">
                {logo_html} 
            </div>

            <div class="title-container">
                <h1>📊 Dashboard de Gestión Académica</h1>
                <p>Facultad de Ciencias Químicas e Ingeniería | Universidad Autónoma de Baja California</p>
            </div>
            <div class="uabc-badge">
                🎓 <strong>Excelencia Académica</strong>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renderiza el sidebar con controles de filtrado"""
    
    with st.sidebar:
        # Logo en sidebar
        logo_base64 = get_image_base64("assets/UABC-logo.png")
        logo_html = f'<img src="data:image/jpeg;base64,{logo_base64}" alt="UABC" style="height: 80px;">' if logo_base64 else '<div style="height: 80px;"></div>'
        st.markdown(logo_html, unsafe_allow_html=True)
        st.markdown("<div class='sidebar-title'> Panel de Control</div>", unsafe_allow_html=True)
        
        # Selector de carrera
        carrera = st.selectbox(
            "📚 Seleccionar Carrera",
            ["Todas", "Ingeniería Química", "Ingeniería Industrial", 
             "Química Farmacéutica", "Ingeniería Ambiental", 
             "Ingeniería en Alimentos", "Licenciatura en Química"]
        )
        
        # Periodo académico
        periodo = st.selectbox(
            "📅 Periodo Académico",
            ["2024-1", "2024-2", "2025-1", "Todos los periodos"]
        )
        
        st.markdown("---")
        st.markdown("### ⚙️ Configuración")
        
        # Filtros adicionales
        umbral_reprobacion = st.slider("Umbral de reprobación", 0, 100, 60)
        mostrar_solo_riesgo = st.checkbox("⚠️ Mostrar solo alumnos en riesgo")
        mostrar_detalles = st.checkbox("📋 Mostrar detalles académicos")
        
        st.markdown("---")
        st.markdown("### 📊 Información Institucional")
        st.markdown("""
        <div style="background: #E3F2FD; padding: 0.75rem; border-radius: 8px; font-size: 0.8rem;">
            <strong>📈 Datos actualizados:</strong><br>
            • 6 carreras en análisis<br>
            • Seguimiento académico<br>
            • Alertas tempranas<br>
            • Sistema de riesgo
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("🔄 Actualizar Dashboard", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        return carrera, periodo, umbral_reprobacion, mostrar_solo_riesgo, mostrar_detalles

def render_metrics(df):
    """Renderiza las tarjetas de métricas"""
    
    st.markdown("### 📊 Indicadores Académicos")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(create_uabc_metric_card("Total Alumnos", len(df), "matriculados", "🎓"), unsafe_allow_html=True)
    
    with col2:
        promedio = df['promedio_general'].mean()
        st.markdown(create_uabc_metric_card("Promedio General", f"{promedio:.1f}", "escala 0-100", "📊"), unsafe_allow_html=True)
        
    with col3:
        avance = df['porcentaje_avance'].mean()
        st.markdown(create_uabc_metric_card("Avance Crediticio", f"{avance:.1f}%", "del plan de estudios", "📈"), unsafe_allow_html=True)
        
    with col4:
        riesgo = len(df[df['estatus'].isin(['RIESGO', 'REZAGADO'])])
        porcentaje_riesgo = (riesgo/len(df))*100 if len(df) > 0 else 0
        st.markdown(create_uabc_metric_card("En Riesgo", riesgo, f"{porcentaje_riesgo:.0f}% del total", "⚠️"), unsafe_allow_html=True)
        
    with col5:
        extras = df['examenes_regularizacion'].mean()
        st.markdown(create_uabc_metric_card("Extraordinarios", f"{extras:.1f}", "promedio por alumno", "📝"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Alertas destacadas
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        excelentes = len(df[df['promedio_general'] >= 90])
        st.markdown(create_uabc_alert(f"🎉 {excelentes} alumnos con promedio sobresaliente (≥90)", "success"), unsafe_allow_html=True)
    
    with col_info2:
        riesgo_count = len(df[df['estatus'].isin(['RIESGO', 'REZAGADO'])])
        if riesgo_count > 0:
            st.markdown(create_uabc_alert(f"⚠️ Se han identificado {riesgo_count} alumnos en situación de riesgo académico", "warning"), unsafe_allow_html=True)
    
    st.markdown("---")

def render_tab_general(df):
    """Renderiza la pestaña de visión general"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución de promedios
        fig = px.histogram(df, x='promedio_general', nbins=30,
                          title='📊 Distribución de Promedios Generales',
                          color_discrete_sequence=['#003366'])
        fig.update_layout(
            height=400,
            plot_bgcolor='white',
            title_font_color='#003366',
            xaxis_title="Promedio General",
            yaxis_title="Frecuencia"
        )
        fig.add_vline(x=60, line_dash="dash", line_color="#FF9800", annotation_text="Mínimo aprobatorio")
        fig.add_vline(x=90, line_dash="dash", line_color="#4CAF50", annotation_text="Excelencia")
        st.plotly_chart(fig, use_container_width=True)
        
        # Avance crediticio
        fig2 = px.scatter(df, x='creditos_cursados', y='promedio_general',
                         color='estatus', size='examenes_regularizacion',
                         title='📈 Relación: Créditos vs Promedio',
                         labels={'creditos_cursados': 'Créditos Cursados', 
                                'promedio_general': 'Promedio General'},
                         color_discrete_map={'ACTIVO': '#4CAF50', 'REGULAR': '#2196F3', 
                                           'RIESGO': '#FF9800', 'REZAGADO': '#F44336'})
        fig2.update_layout(height=400, plot_bgcolor='white')
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        # Estado académico
        estatus_counts = df['estatus'].value_counts()
        fig3 = px.pie(values=estatus_counts.values, names=estatus_counts.index,
                     title='🎯 Distribución por Estatus Académico',
                     color_discrete_sequence=['#4CAF50', '#2196F3', '#FF9800', '#F44336'])
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)
        
        # Planes de estudio
        plan_counts = df['plan_estudios'].value_counts()
        fig4 = px.bar(x=plan_counts.index, y=plan_counts.values,
                     title='📚 Distribución por Plan de Estudios',
                     color=plan_counts.values, color_continuous_scale='Blues')
        fig4.update_layout(height=400, plot_bgcolor='white')
        st.plotly_chart(fig4, use_container_width=True)

def render_tab_carreras(df):
    """Renderiza la pestaña de análisis por carrera"""
    
    st.markdown("### 🏆 Rendimiento por Carrera")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de promedios por carrera
        carrera_promedio = df.groupby('carrera')['promedio_general'].mean().sort_values(ascending=False)
        fig5 = px.bar(x=carrera_promedio.values, y=carrera_promedio.index,
                     orientation='h', title='Promedio General por Carrera',
                     color=carrera_promedio.values, color_continuous_scale='Blues',
                     labels={'x': 'Promedio General', 'y': 'Carrera'})
        fig5.update_layout(height=400, plot_bgcolor='white')
        st.plotly_chart(fig5, use_container_width=True)
    
    with col2:
        # Tabla de métricas por carrera
        metrics_table = df.groupby('carrera').agg({
            'promedio_general': 'mean',
            'porcentaje_avance': 'mean',
            'examenes_regularizacion': 'mean'
        }).round(2)
        metrics_table.columns = ['📊 Promedio', '📈 Avance %', '📝 Extraordinarios']
        st.dataframe(metrics_table, use_container_width=True)
    
    # Gráfico comparativo
    st.markdown("### 📊 Comparativa de Indicadores")
    carrera_metrics = df.groupby('carrera').agg({
        'promedio_general': 'mean',
        'porcentaje_avance': 'mean'
    }).reset_index()
    
    fig6 = go.Figure()
    fig6.add_trace(go.Bar(name='Promedio General', x=carrera_metrics['carrera'], 
                          y=carrera_metrics['promedio_general'], marker_color='#003366'))
    fig6.add_trace(go.Bar(name='Avance %', x=carrera_metrics['carrera'], 
                          y=carrera_metrics['porcentaje_avance'], marker_color='#C5A35E'))
    fig6.update_layout(title='Comparativa por Carrera', barmode='group', height=400,
                      plot_bgcolor='white')
    st.plotly_chart(fig6, use_container_width=True)

def render_tab_riesgo(df):
    """Renderiza la pestaña de detección de riesgo"""
    
    st.markdown("### 🚨 Sistema de Alerta Temprana UABC")
    st.markdown(create_uabc_alert("Detección de patrones de riesgo basada en análisis académico", "info"), unsafe_allow_html=True)
    
    # Identificar alumnos en riesgo
    alumnos_riesgo = df[df['estatus'].isin(['RIESGO', 'REZAGADO'])]
    
    if len(alumnos_riesgo) > 0:
        st.markdown(f"#### ⚠️ {len(alumnos_riesgo)} alumnos requieren atención prioritaria")
        
        for _, alumno in alumnos_riesgo.head(5).iterrows():
            with st.expander(f"🎓 {alumno['nombre']} - {alumno['matricula']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Promedio", f"{alumno['promedio_general']:.1f}")
                with col2:
                    st.metric("Avance", f"{alumno['porcentaje_avance']:.1f}%")
                with col3:
                    st.metric("Extraordinarios", alumno['examenes_regularizacion'])
                
                # Recomendaciones
                st.markdown("**📋 Recomendaciones:**")
                if alumno['promedio_general'] < 60:
                    st.markdown(create_uabc_alert("• Programa de regularización académica inmediato", "danger"), unsafe_allow_html=True)
                if alumno['porcentaje_avance'] < 50:
                    st.markdown(create_uabc_alert("• Asesoría para planificación de créditos", "warning"), unsafe_allow_html=True)
                if alumno['examenes_regularizacion'] > 3:
                    st.markdown(create_uabc_alert("• Intervención tutorial especializada", "warning"), unsafe_allow_html=True)
    else:
        st.markdown(create_uabc_alert("✅ No se encontraron alumnos en situación de riesgo", "success"), unsafe_allow_html=True)
    
    # Métricas de riesgo
    st.markdown("### 📊 Análisis de Riesgo")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        bajo_riesgo = len(df[df['promedio_general'] >= 80])
        st.markdown(create_uabc_metric_card("Bajo Riesgo", bajo_riesgo, "promedio ≥ 80", "🟢"), unsafe_allow_html=True)
    
    with col2:
        riesgo_medio = len(df[(df['promedio_general'] >= 60) & (df['promedio_general'] < 80)])
        st.markdown(create_uabc_metric_card("Riesgo Moderado", riesgo_medio, "promedio 60-80", "🟡"), unsafe_allow_html=True)
    
    with col3:
        alto_riesgo = len(df[df['promedio_general'] < 60])
        st.markdown(create_uabc_metric_card("Alto Riesgo", alto_riesgo, "promedio < 60", "🔴"), unsafe_allow_html=True)

def render_tab_detalle(df, mostrar_detalles):
    """Renderiza la pestaña de detalle de alumnos"""
    
    if mostrar_detalles:
        st.markdown("### 📋 Listado Detallado de Alumnos")
        
        # Selector de columna para ordenar
        ordenar_por = st.selectbox("Ordenar por:", ["matricula", "promedio_general", "porcentaje_avance"])
        ascending = st.checkbox("Ascendente", True)
        
        display_df = df[['matricula', 'nombre', 'carrera', 'promedio_general', 
                        'porcentaje_avance', 'examenes_regularizacion', 'estatus']].copy()
        display_df = display_df.sort_values(ordenar_por, ascending=ascending)
        
        # Formatear para mejor visualización
        display_df['promedio_general'] = display_df['promedio_general'].round(1)
        display_df['porcentaje_avance'] = display_df['porcentaje_avance'].round(1)
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Exportar datos
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar datos (CSV)", csv, "datos_academicos.csv", "text/csv")
    else:
        st.info("ℹ️ Activa 'Mostrar detalles académicos' en el panel lateral para ver el listado completo")

def render_footer():
    """Renderiza el footer institucional"""
    
    st.markdown("""
    <div class="uabc-footer">
        <p><strong>Universidad Autónoma de Baja California</strong> | Facultad de Ciencias Químicas e Ingeniería</p>
        <p>"Por la realización plena del ser"</p>
        <small>📊 Dashboard de Gestión Académica | Datos actualizados al periodo actual</small>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# MAIN
# ============================================

def main():
    """Función principal del dashboard"""
    
    # Cargar CSS
    load_css()
    
    # Renderizar header
    render_header()
    
    # Renderizar sidebar y obtener filtros
    carrera, periodo, umbral_reprobacion, mostrar_solo_riesgo, mostrar_detalles = render_sidebar()
    
    # Cargar datos
    with st.spinner("🔄 Cargando datos académicos..."):
        students_df = load_sample_data()
    
    # Aplicar filtros
    df_filtered = students_df.copy()
    if carrera != "Todas":
        df_filtered = df_filtered[df_filtered['carrera'] == carrera]
    if mostrar_solo_riesgo:
        df_filtered = df_filtered[df_filtered['estatus'].isin(['RIESGO', 'REZAGADO'])]
    
    # Renderizar métricas
    render_metrics(df_filtered)
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Visión General", "🎯 Rendimiento por Carrera", "🚨 Detección de Riesgo", "📋 Detalle de Alumnos"])
    
    with tab1:
        render_tab_general(df_filtered)
    
    with tab2:
        render_tab_carreras(df_filtered)
    
    with tab3:
        render_tab_riesgo(df_filtered)
    
    with tab4:
        render_tab_detalle(df_filtered, mostrar_detalles)
    
    # Renderizar footer
    render_footer()

# Ejecutar la aplicación
if __name__ == "__main__":
    main()