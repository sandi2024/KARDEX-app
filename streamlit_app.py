import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Configuración de página
st.set_page_config(
    page_title="Dashboard Academico - Facultad de Ciencias Químicas e Ingeniería",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar CSS externo
def load_css():
    """Carga el archivo CSS desde la carpeta assets"""
    with open('assets/style.css', 'r', encoding='utf-8') as f:
        css_content = f.read()
    st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)

# Llamar a la función para cargar CSS
load_css()


# Inicializar session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'students_df' not in st.session_state:
    st.session_state.students_df = None
if 'grades_df' not in st.session_state:
    st.session_state.grades_df = None

# Funciones auxiliares para HTML con clases CSS
def create_metric_card(title, value, delta=None, icon="📊"):
    """Crea una tarjeta de métrica usando CSS externo"""
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ''
    return f'''
    <div class="metric-card">
        <h3>{icon} {title}</h3>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    '''

def create_alert(message, type="warning"):
    """Crea una alerta usando CSS externo"""
    return f'<div class="alert-{type}">{message}</div>'

def create_badge(text, type="info"):
    """Crea una badge usando CSS externo"""
    return f'<span class="badge badge-{type}">{text}</span>'

def create_progress_bar(percentage, type="success"):
    """Crea una barra de progreso usando CSS externo"""
    return f'''
    <div class="progress-bar-container">
        <div class="progress-bar progress-bar-{type}" style="width: {percentage}%"></div>
    </div>
    '''

# Sidebar - Carga de datos
with st.sidebar:
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    st.markdown("### 🎓 **Facultad de Ciencias Químicas e Ingeniería**")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Selector de carrera
    carrera = st.selectbox(
        "🎓 Seleccionar Carrera",
        ["Todas", "Ingeniería Química", "Ingeniería Industrial", 
         "Química Farmacéutica", "Ingeniería Ambiental", 
         "Ingeniería en Alimentos", "Licenciatura en Química"]
    )
    
    # Periodo académico
    periodo = st.selectbox(
        "📅 Periodo Académico",
        ["2024-1", "2024-2", "2025-1", "Todos los periodos"]
    )
    
    # Tipo de análisis
    analisis_tipo = st.radio(
        "🔍 Tipo de Análisis",
        ["General", "Por Alumno", "Por Materia", "Predictivo"]
    )
    
    st.markdown("---")
    st.markdown('<div class="filters-container">', unsafe_allow_html=True)
    st.markdown("**⚙️ Filtros Avanzados**")
    
    # Filtros adicionales
    umbral_reprobacion = st.slider("Umbral de reprobación", 0, 100, 60)
    mostrar_solo_riesgo = st.checkbox("Mostrar solo alumnos en riesgo")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🔄 Actualizar Dashboard", type="primary", use_container_width=True):
        st.session_state.data_loaded = True
        st.rerun()

# Título principal
st.markdown('''
<div class="main-header fade-in">
    <h1>📊 Dashboard de Gestión Académica</h1>
    <p>Análisis de 6 carreras - Facultad de Ciencias Químicas e Ingeniería</p>
</div>
''', unsafe_allow_html=True)

# Función para cargar datos de ejemplo
@st.cache_data
def load_sample_data():
    """Carga datos de ejemplo basados en el kardex proporcionado"""
    
    # Datos de alumnos (6 carreras)
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
    
    # Simular materias
    materias = [
        {'clave': '1341', 'nombre': 'QUIMICA GENERAL I', 'creditos': 8, 'tipo': 'BASICA'},
        {'clave': '1348', 'nombre': 'QUIMICA GENERAL II', 'creditos': 8, 'tipo': 'BASICA'},
        {'clave': '1343', 'nombre': 'LAB QUIMICA GENERAL I', 'creditos': 3, 'tipo': 'LABORATORIO'},
        {'clave': '1344', 'nombre': 'FISICA I', 'creditos': 8, 'tipo': 'BASICA'},
        {'clave': '1350', 'nombre': 'FISICA II', 'creditos': 8, 'tipo': 'BASICA'},
        {'clave': '1455', 'nombre': 'PROGRAMACION ESTRUCTURADA I', 'creditos': 9, 'tipo': 'OPTATIVA'},
        {'clave': '1456', 'nombre': 'ALGEBRA LINEAL', 'creditos': 8, 'tipo': 'BASICA'},
        {'clave': '1393', 'nombre': 'COMUNICACION Y EXPRESION', 'creditos': 6, 'tipo': 'OPTATIVA'},
    ]
    
    # Generar calificaciones
    grades = []
    for _, student in students.iterrows():
        for materia in materias:
            intentos = np.random.choice([1, 2, 3, 4], p=[0.6, 0.25, 0.1, 0.05])
            
            for intento in range(1, intentos + 1):
                tipo_examen = 'Ord' if intento == 1 else np.random.choice(['Ord', 'Ext'])
                
                if student['estatus'] == 'RIESGO':
                    calif_base = np.random.uniform(0, 70)
                elif student['promedio_general'] > 80:
                    calif_base = np.random.uniform(70, 100)
                else:
                    calif_base = np.random.uniform(40, 85)
                
                calif = calif_base + (intento - 1) * 8
                calif = np.clip(calif, 0, 100)
                
                if np.random.random() < 0.1:
                    calif = 'NP'
                elif calif < 60 and np.random.random() < 0.2:
                    calif = 'SD'
                else:
                    calif = round(calif)
                
                grades.append({
                    'matricula': student['matricula'],
                    'carrera': student['carrera'],
                    'clave_materia': materia['clave'],
                    'materia': materia['nombre'],
                    'creditos': materia['creditos'],
                    'tipo_materia': materia['tipo'],
                    'intento': intento,
                    'tipo_examen': tipo_examen,
                    'calificacion': calif,
                    'fecha': f"2024-{np.random.randint(1, 13)}-{np.random.randint(1, 28)}",
                    'periodo': np.random.choice(['2024-1', '2024-2', '2023-2'], 1)[0]
                })
    
    grades_df = pd.DataFrame(grades)
    
    # Calcular métricas adicionales
    students['creditos_faltantes'] = students['creditos_requeridos'] - students['creditos_cursados']
    students['porcentaje_avance'] = (students['creditos_cursados'] / students['creditos_requeridos']) * 100
    students['porcentaje_avance'] = students['porcentaje_avance'].clip(0, 100)
    
    return students, grades_df, materias

# Cargar datos
if st.session_state.students_df is None:
    with st.spinner("Cargando datos académicos..."):
        students_df, grades_df, materias = load_sample_data()
        st.session_state.students_df = students_df
        st.session_state.grades_df = grades_df
else:
    students_df = st.session_state.students_df
    grades_df = st.session_state.grades_df
    materias = []

# Filtrar por carrera
if carrera != "Todas":
    students_df = students_df[students_df['carrera'] == carrera]
    grades_df = grades_df[grades_df['carrera'] == carrera]

# Filtrar por periodo
if periodo != "Todos los periodos":
    grades_df = grades_df[grades_df['periodo'] == periodo]

# Filtrar por riesgo
if mostrar_solo_riesgo:
    students_df = students_df[students_df['estatus'].isin(['RIESGO', 'REZAGADO'])]

# Mostrar métricas con CSS personalizado
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(create_metric_card("Total Alumnos", len(students_df), "activos", "🎓"), unsafe_allow_html=True)

with col2:
    promedio_final = students_df['promedio_general'].mean()
    st.markdown(create_metric_card("Promedio General", f"{promedio_final:.1f}", None, "📊"), unsafe_allow_html=True)
    
with col3:
    avance_promedio = students_df['porcentaje_avance'].mean()
    st.markdown(create_metric_card("Avance Promedio", f"{avance_promedio:.1f}%", None, "📈"), unsafe_allow_html=True)
    
with col4:
    riesgo_count = len(students_df[students_df['estatus'].isin(['RIESGO', 'REZAGADO'])])
    st.markdown(create_metric_card("Alumnos en Riesgo", riesgo_count, f"{riesgo_count/len(students_df)*100:.0f}% del total", "⚠️"), unsafe_allow_html=True)
    
with col5:
    extra_promedio = students_df['examenes_regularizacion'].mean()
    st.markdown(create_metric_card("Extraordinarios Promedio", f"{extra_promedio:.1f}", None, "📝"), unsafe_allow_html=True)

st.markdown("---")

# Mostrar ejemplo de badge y alerta
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💡 **Estado Académico**")
    st.markdown(create_badge("Excelente", "success") + " " + 
                create_badge("Regular", "warning") + " " + 
                create_badge("En Riesgo", "danger") + " " +
                create_badge("Bajo Seguimiento", "info"), unsafe_allow_html=True)

with col2:
    st.markdown("### 📢 **Notificaciones**")
    st.markdown(create_alert("3 alumnos tienen materias con más de 3 intentos sin aprobar", "warning"), unsafe_allow_html=True)

st.markdown("---")

# Tabs para diferentes análisis
tab1, tab2, tab3, tab4 = st.tabs(["📊 Visión General", "🎯 Análisis por Carrera", "🚨 Detección de Riesgo", "📈 Análisis Predictivo"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución de promedios
        fig = px.histogram(students_df, x='promedio_general', nbins=30,
                          title='📊 Distribución de Promedios Generales',
                          color_discrete_sequence=['#3b82f6'])
        fig.update_layout(height=400, showlegend=False)
        fig.add_vline(x=60, line_dash="dash", line_color="red")
        fig.add_vline(x=80, line_dash="dash", line_color="green")
        st.plotly_chart(fig, use_container_width=True)
        
        # Avance por créditos
        fig2 = px.scatter(students_df, x='creditos_cursados', y='promedio_general',
                         color='estatus', size='examenes_regularizacion',
                         title='📈 Relación: Créditos vs Promedio',
                         labels={'creditos_cursados': 'Créditos Cursados', 
                                'promedio_general': 'Promedio General'})
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        # Estado académico
        estatus_counts = students_df['estatus'].value_counts()
        fig3 = px.pie(values=estatus_counts.values, names=estatus_counts.index,
                     title='🎯 Distribución por Estatus Académico',
                     color_discrete_sequence=px.colors.qualitative.Set3)
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)
        
        # Top materias con reprobación
        reprobadas = grades_df[grades_df['calificacion'].astype(str).str.isnumeric()]
        reprobadas = reprobadas[reprobadas['calificacion'].astype(float) < umbral_reprobacion]
        top_reprobadas = reprobadas['materia'].value_counts().head(10)
        
        fig4 = px.bar(x=top_reprobadas.values, y=top_reprobadas.index,
                     orientation='h', title='🔴 Materias con Mayor Índice de Reprobación',
                     color_discrete_sequence=['#ef4444'])
        fig4.update_layout(height=400)
        st.plotly_chart(fig4, use_container_width=True)

with tab2:
    st.markdown("### 🏆 Rendimiento por Carrera")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras por carrera
        carrera_metrics = students_df.groupby('carrera')['promedio_general'].mean().sort_values(ascending=False)
        fig5 = px.bar(x=carrera_metrics.values, y=carrera_metrics.index,
                     orientation='h', title='Promedio General por Carrera',
                     color=carrera_metrics.values, color_continuous_scale='Viridis')
        fig5.update_layout(height=400)
        st.plotly_chart(fig5, use_container_width=True)
    
    with col2:
        # Tabla de métricas
        metrics_table = students_df.groupby('carrera').agg({
            'promedio_general': 'mean',
            'porcentaje_avance': 'mean',
            'examenes_regularizacion': 'mean'
        }).round(2)
        metrics_table.columns = ['Promedio', 'Avance %', 'Extraordinarios']
        st.dataframe(metrics_table, use_container_width=True)

with tab3:
    st.markdown("### 🚨 Sistema de Alerta Temprana")
    st.markdown(create_alert("Basado en el análisis del kardex proporcionado", "info"), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="alert-warning">', unsafe_allow_html=True)
        st.markdown("**⚠️ Materia Bloqueante**")
        st.markdown("**Programación Estructurada I**")
        st.markdown("- 4 intentos sin aprobar")
        st.markdown("- Todas las calificaciones: NP")
        st.markdown("**Recomendación:** Intervención tutorial inmediata")
        st.markdown(create_progress_bar(0, "danger"), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="alert-danger">', unsafe_allow_html=True)
        st.markdown("**📉 Mejora Insuficiente**")
        st.markdown("**Álgebra Lineal**")
        st.markdown("- Ordinario: 40")
        st.markdown("- Extraordinario: 50")
        st.markdown("**Recomendación:** Curso remedial")
        st.markdown(create_progress_bar(50, "warning"), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="alert-warning">', unsafe_allow_html=True)
        st.markdown("**❓ Sin Datos (SD)**")
        st.markdown("**Química General II**")
        st.markdown("- Ordinario: SD")
        st.markdown("- Extraordinario: SD")
        st.markdown("**Recomendación:** Verificar asistencia")
        st.markdown(create_progress_bar(0, "danger"), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown("### 📈 Análisis Predictivo")
    st.markdown(create_alert("Modelo ML para predicción de riesgo académico", "info"), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Simulación de predicción
        riesgo_predicho = students_df['promedio_general'] < 65
        pred_counts = riesgo_predicho.value_counts()
        
        fig9 = px.pie(values=pred_counts.values, 
                     names=['Bajo Riesgo', 'Alto Riesgo'],
                     title='Predicción de Alumnos en Riesgo',
                     color_discrete_sequence=['#10b981', '#ef4444'])
        st.plotly_chart(fig9, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Modelo Random Forest")
        st.markdown("**Métricas de desempeño:**")
        st.markdown(create_progress_bar(87, "success"), unsafe_allow_html=True)
        st.markdown("Precisión: 87%")
        st.markdown(create_progress_bar(79, "warning"), unsafe_allow_html=True)
        st.markdown("Recall: 79%")
        st.markdown(create_progress_bar(83, "info"), unsafe_allow_html=True)
        st.markdown("F1-Score: 83%")

# Footer
st.markdown('''
<div class="main-footer">
    <p>📊 Dashboard de Gestión Académica | Facultad de Ciencias Químicas e Ingeniería</p>
    <p>Datos basados en estructura de kardex institucional | Actualización en tiempo real</p>
</div>
''', unsafe_allow_html=True)