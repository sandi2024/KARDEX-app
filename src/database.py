import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import date
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


class Facultad(SQLModel, table=True):
    id_unidad: int = Field(primary_key=True)
    nombre: Optional[str] = Field(default=None, max_length=100)

    # Relaciones
    programas: List["ProgramaEducativo"] = Relationship(back_populates="facultad")


class ProgramaEducativo(SQLModel, table=True):
    id_programa: int = Field(primary_key=True)
    nombre: Optional[str] = Field(default=None, max_length=100)
    id_unidad: Optional[int] = Field(default=None, foreign_key="facultad.id_unidad")

    # Relaciones
    facultad: Optional[Facultad] = Relationship(back_populates="programas")
    planes_estudio: List["PlanEstudio"] = Relationship(back_populates="programa")


class Alumno(SQLModel, table=True):
    matricula: str = Field(primary_key=True, max_length=50)
    nombre: Optional[str] = Field(default=None, max_length=100)

    # Relaciones
    planes_estudio_vinculos: List["AlumnoPlanEstudio"] = Relationship(back_populates="alumno")
    asignaturas_cursadas: List["AlumnoAsignatura"] = Relationship(back_populates="alumno")


class PlanEstudio(SQLModel, table=True):
    __tablename__ = "Plan_estudio"

    id_plan_estudio: str = Field(primary_key=True, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=80)
    creditos_optativos: Optional[int] = Field(default=None)
    creditos_obligatorios: Optional[int] = Field(default=None)
    creditos_pp: Optional[int] = Field(default=None)
    id_programa: Optional[int] = Field(default=None, foreign_key="programaeducativo.id_programa")

    # Relaciones
    programa: Optional[ProgramaEducativo] = Relationship(back_populates="planes_estudio")
    asignaturas_vinculos: List["AsignaturaPlan"] = Relationship(back_populates="plan_estudio")


class AlumnoPlanEstudio(SQLModel, table=True):
    __tablename__ = "Alumno_plan_estudio"

    # Nota: Como SQLModel requiere una llave primaria por tabla, definimos una compuesta
    id_plan_estudio: str = Field(primary_key=True, max_length=50, foreign_key="Plan_estudio.id_plan_estudio")
    matricula: str = Field(primary_key=True, max_length=50, foreign_key="alumno.matricula")
    orden_prioritario: Optional[int] = Field(default=None)

    # Relaciones
    alumno: Optional[Alumno] = Relationship(back_populates="planes_estudio_vinculos")


class Asignatura(SQLModel, table=True):
    id_asignatura: str = Field(primary_key=True, max_length=50)
    nombre: Optional[str] = Field(default=None, max_length=100)
    creditos: Optional[int] = Field(default=None)

    # Relaciones
    planes_vinculos: List["AsignaturaPlan"] = Relationship(back_populates="asignatura")


class AsignaturaPlan(SQLModel, table=True):
    __tablename__ = "Asignatura_plan"

    id_asignatura_plan: int = Field(primary_key=True)
    id_plan_estudio: Optional[str] = Field(default=None, foreign_key="Plan_estudio.id_plan_estudio")
    id_asignatura: Optional[str] = Field(default=None, foreign_key="asignatura.id_asignatura")

    # Relaciones
    plan_estudio: Optional[PlanEstudio] = Relationship(back_populates="asignaturas_vinculos")
    asignatura: Optional[Asignatura] = Relationship(back_populates="planes_vinculos")
    alumnos_vinculos: List["AlumnoAsignatura"] = Relationship(back_populates="asignatura_plan")


class Periodo(SQLModel, table=True):
    id_periodo: str = Field(primary_key=True, max_length=10)
    anio_periodo: Optional[int] = Field(default=None)
    orden: Optional[int] = Field(default=None)

    # Relaciones
    alumnos_asignaturas: List["AlumnoAsignatura"] = Relationship(back_populates="periodo")


class AlumnoAsignatura(SQLModel, table=True):
    __tablename__ = "Alumno_asignatura"

    # Llave primaria compuesta requerida por SQLModel para tablas relacionales intermedias
    matricula: str = Field(primary_key=True, max_length=50, foreign_key="alumno.matricula")
    id_asignatura_plan: int = Field(primary_key=True, foreign_key="Asignatura_plan.id_asignatura_plan")
    id_periodo: str = Field(primary_key=True, max_length=10, foreign_key="periodo.id_periodo")
    
    tipo_examen: Optional[str] = Field(default=None, max_length=20)
    calificacion: Optional[float] = Field(default=None)  # DECIMAL mapea a float en Python
    fecha_examen: Optional[date] = Field(default=None)
    etapa: Optional[str] = Field(default=None, max_length=20)

    # Relaciones
    alumno: Optional[Alumno] = Relationship(back_populates="asignaturas_cursadas")
    asignatura_plan: Optional[AsignaturaPlan] = Relationship(back_populates="alumnos_vinculos")
    periodo: Optional[Periodo] = Relationship(back_populates="alumnos_asignaturas")



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
