import streamlit as st

# 1. Inyectar el CSS que ya tienes (revisado)
st.markdown("""
<style>
:root {
    --blue: #003366;
    --gold: #C5A35E;
    --white: #FFFFFF;
    --gray: #F5F5F5;
    --primary-gradient: linear-gradient(135deg, #003366, #004d99);
    --gold-gradient: linear-gradient(135deg, #C5A35E, #D4B47C);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
    --border-radius-md: 12px;
}

/* Aplicar fondo gris claro a la app para que resalten las tarjetas blancas */
[data-testid="stAppViewContainer"] {
    background-color: var(--gray);
}

.uabc-header {
    background: var(--primary-gradient);
    padding: 1.5rem;
    border-radius: var(--border-radius-md);
    color: white;
    margin-bottom: 2rem;
    border-top: 4px solid var(--gold);
    box-shadow: var(--shadow-md);
}

.card-uabc {
    background: var(--white);
    border-radius: var(--border-radius-md);
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow-md);
    border-left: 5px solid var(--blue);
}

.metric-value {
    font-size: 2rem;
    font-weight: bold;
    color: var(--blue);
}
</style>
""", unsafe_allow_html=True)

# 2. Simulación de Base de Datos
alumnos = {
    "123456": {
        "nombre": "Juan Pérez González",
        "carrera": "Ingeniería en Computación",
        "promedio": 92.5,
        "estatus": "Regular",
        "semestre": "6to Semestre"
    },
    "654321": {
        "nombre": "María Rodríguez López",
        "carrera": "Licenciatura en Derecho",
        "promedio": 95.0,
        "estatus": "Excelencia",
        "semestre": "8vo Semestre"
    }
}
########################################################################3
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# 1. Función para conectar y extraer datos (con cache para optimizar)
@st.cache_data
def get_alumnos_data(query):
    # Sustituye con tu cadena de conexión: 
    # 'mysql+pymysql://user:pass@host/dbname'
    engine = create_engine('sqlite:///mi_base_de_datos.db')
    
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

# 2. Uso en la aplicación
st.title("Consulta de Alumnos")

matricula = st.text_input("Buscar por matrícula:")

if matricula:
    # Usamos f-strings para la consulta (en producción usar parámetros seguros)
    query = f"SELECT * FROM alumnos WHERE matricula = '{matricula}'"
    
    try:
        df_alumno = get_alumnos_data(query)

        if not df_alumno.empty:
            st.write("### Información encontrada:")
            st.dataframe(df_alumno) # Aquí se aplicaría tu estilo CSS automático  //
        else:
            st.warning("Alumno no encontrado.")
            
    except Exception as e:
        st.error(f"Error de conexión: {e}")
##############################################################################################################33

# 3. Interfaz de Búsqueda
st.markdown('<div class="uabc-header"><h1>Portal de Consulta de Alumnos</h1><p>Sistema de Gestión Académica</p></div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    matricula = st.text_input("Ingrese la matrícula del alumno:", placeholder="Ej. 123456")

# 4. Lógica de despliegue
if matricula:
    if matricula in alumnos:
        alumno = alumnos[matricula]
        
        # Ficha de Datos Personales
        st.markdown(f"""
        <div class="card-uabc">
            <h3>Información General</h3>
            <p><strong>Nombre:</strong> {alumno['nombre']}</p>
            <p><strong>Carrera:</strong> {alumno['carrera']}</p>
            <p><strong>Ciclo:</strong> {alumno['semestre']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Métricas Rápidas
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="card-uabc">
                <small>PROMEDIO GENERAL</small>
                <div class="metric-value">{alumno['promedio']}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="card-uabc">
                <small>ESTATUS ACADÉMICO</small>
                <div class="metric-value" style="color: #4CAF50;">{alumno['estatus']}</div>
            </div>
            """, unsafe_allow_html=True)
            
    else:
        st.error("Matrícula no encontrada. Por favor, verifique los datos.")
else:
    st.info("Por favor, ingrese una matrícula para comenzar la búsqueda.")