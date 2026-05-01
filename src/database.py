import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# 1. Configuración de la conexión (Centralizada)
def get_engine():
    """
    Crea el motor de conexión. 
    Usa st.secrets para no exponer contraseñas en el código.
    """
    # Ejemplo para SQLite (Local)
    db_url = "sqlite:///data/gestion_academica.db"
    
    # Ejemplo para MySQL/Postgres (Nube) - Descomenta si lo usas:
    # db_conf = st.secrets["mysql"]
    # db_url = f"mysql+pymysql://{db_conf.user}:{db_conf.password}@{db_conf.host}/{db_conf.database}"
    
    return create_engine(db_url)

# 2. Función genérica para extraer datos con Caché
@st.cache_data(show_spinner="Cargando datos académicos...")
def fetch_data(query, params=None):
    """
    Ejecuta una consulta SQL y devuelve un DataFrame de Pandas.
    """
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # Usamos text() para mayor seguridad contra inyección SQL
            df = pd.read_sql(text(query), conn, params=params)
        return df
    except Exception as e:
        st.error(f"Error al consultar la base de datos: {e}")
        return pd.DataFrame()

# 3. Funciones específicas para el Dashboard
def buscar_alumno_por_matricula(matricula):
    """Obtiene toda la info de un alumno específico."""
    query = "SELECT * FROM alumnos WHERE matricula = :m"
    return fetch_data(query, params={"m": matricula})

def obtener_kardex(matricula):
    """Obtiene las materias y calificaciones del alumno."""
    query = """
        SELECT materia, calificacion, semestre, estatus 
        FROM kardex 
        WHERE matricula = :m 
        ORDER BY semestre ASC
    """
    return fetch_data(query, params={"m": matricula})

def obtener_metricas_globales():
    """Obtiene promedios generales para el análisis de datos."""
    query = "SELECT carrera, AVG(promedio) as promedio_grupal FROM alumnos GROUP BY carrera"
    return fetch_data(query)

# Cargar datos originales para procesar
df_original = pd.read_csv("data/raw/inscripciones.csv")

# ... realizar limpieza y cálculos estadísticos ...

# Guardar resultado para que el Dashboard lo use rápido
df_final.to_csv("data/processed/dashboard_ready.csv")
