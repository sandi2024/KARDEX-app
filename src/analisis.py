import pandas as pd
import numpy as np

def procesar_kardex(df, umbral_reprobacion):

    df_proc = df.copy()

    grupos = df_proc.groupby('id_estudiante')

    resumen_alumnos = pd.DataFrame()

    # Promedio Final: mean() de pandas ignora los NaN (NP) por defecto, 
    # pero sí promedia los 0 (SD). Es el comportamiento académico estándar.
    resumen_alumnos['promedio_final'] = grupos['calificacion'].mean()

    # Créditos Logrados: Solo sumamos créditos si aprobó (calif >= umbral)
    # NP (NaN) y SD (0) fallarán la condición >= 70, por lo que no sumarán créditos.
    resumen_alumnos['total_creditos_logrados'] = grupos.apply(
        lambda x: x[x['calificacion'] >= umbral_reprobacion]['creditos_materia'].sum()
    )

    # Tasa de Extraordinarios
    resumen_alumnos['tasa_extraordinarios'] = grupos.apply(
        lambda x: (x['tipo_examen'] == 'Ext').mean()
    )

    # Conteo de Casos Especiales (NP y SD)
    # Usamos la columna original o la procesada para identificar los nulos
    resumen_alumnos['conteo_SD'] = grupos.apply(lambda x: (x['calificacion'] == 0).sum())
    resumen_alumnos['conteo_NP'] = grupos.apply(lambda x: x['calificacion'].isna().sum())

    # --- 3. MÉTRICAS DE TRAYECTORIA ---
    resumen_alumnos['periodos_cursados'] = grupos['periodo'].nunique()
    
    resumen_alumnos['eficiencia_creditos'] = (
        resumen_alumnos['total_creditos_logrados'] / resumen_alumnos['periodos_cursados']
    )

    return resumen_alumnos

def procesar_kardex_general(df, umbral_reprobacion, max_extraordinario):
 
    df_proc = df.copy()

    # Agrupamos por el ID único del alumno
    grupos = df_proc.groupby('id_estudiante')

    # CÁLCULO DE MÉTRICAS 
    resumen_alumnos = pd.DataFrame()


    resumen_alumnos['carrera'] = grupos['carrera'].first()
    resumen_alumnos['id_plan_estudio'] = grupos['id_plan_estudio'].first()
    resumen_alumnos['plan_estudio'] = grupos['nombre_plan'].first()
    resumen_alumnos['promedio_final'] = grupos['calificacion'].mean()
    # Créditos Logrados: Solo sumamos créditos si aprobó (calif >= umbral)
    # NP (NaN) y SD (0) 
    
    resumen_alumnos['total_creditos_logrados'] = grupos.apply(
        lambda x: x[x['calificacion'] >= umbral_reprobacion]['creditos_materia'].sum()
    )
   
    resumen_alumnos['creditos_total'] = grupos['creditos_totales_plan'].first()
   
    resumen_alumnos['conteo_extraordinarios'] = grupos.apply(
        lambda x: (x['tipo_examen'] == 'Ext').sum()
    )

    # Tasa de Extraordinarios
    resumen_alumnos['tasa_extraordinarios'] = grupos.apply(
        lambda x: (x['tipo_examen'] == 'Ext').mean()
    )

    # Conteo de Casos Especiales (NP y SD)
    # la columna original o la procesada para identificar los nulos
    resumen_alumnos['conteo_SD'] = grupos.apply(lambda x: (x['calificacion'] == 0).sum())
    resumen_alumnos['conteo_NP'] = grupos.apply(lambda x: x['calificacion'].isna().sum())

    def asignar_estatus(row):
        if row['promedio_final'] < umbral_reprobacion:
            return 'RIESGO'
        if row['conteo_extraordinarios'] >= max_extraordinario:
            return 'REZAGADO'
        if row['promedio_final'] >= 90:
            return 'EXCELENTE'
        return 'REGULAR'
    
    def avance_credito(row):
        return row['total_creditos_logrados']/row['creditos_total']*100

    resumen_alumnos['estatus'] = resumen_alumnos.apply(asignar_estatus, axis=1)
    resumen_alumnos['avance_porcentaje'] = resumen_alumnos.apply(avance_credito, axis=1)

    return resumen_alumnos


def calcular_metricas_generales(df_kardex):
    total_alumnos = len(df_kardex)
    promedio_general = df_kardex['promedio_final'].mean()
    promedio_ext = df_kardex['conteo_extraordinarios'].mean()
    sobresalientes = len(df_kardex[df_kardex['promedio_final'] >= 90])
    en_riesgo = len(df_kardex[df_kardex['estatus'] == 'RIESGO'])
    porcetaje_en_riesgo = (en_riesgo/total_alumnos)*100
    avance_porcentaje = df_kardex['avance_porcentaje'].mean()
   

    return {
        "total_alumno": total_alumnos,
        "promedio_general": promedio_general,
        "avance_porcentaje": avance_porcentaje,
        "porcentaje_riesgo": porcetaje_en_riesgo,
        "promedio_ext": promedio_ext,
        "sobresalientes": sobresalientes,
        "en_riesgo": en_riesgo
    }




def calcular_metricas_alumno(df_kardex):
    total_materias = len(df_kardex)
    aprobadas = len(df_kardex[df_kardex['calificacion'] >= 60])
    promedio = df_kardex['calificacion'].mean()
    
    # Análisis de riesgo
    reprobadas = total_materias - aprobadas
    nivel_riesgo = "Bajo"
    if reprobadas >= 2: nivel_riesgo = "Moderado"
    if reprobadas >= 4 or promedio < 60: nivel_riesgo = "Alto"
    
    return {
        "promedio": promedio,
        "avance": (aprobadas / total_materias) * 100,
        "riesgo": nivel_riesgo
    }

def normalizar_datos_academicos(df):
    """Limpia nulos y genera llaves únicas para el análisis."""
    if df.empty:
        return df
    
    df = df.copy() # Evitamos modificar el dataframe original (SettingWithCopyWarning)
    
    # Limpieza de calificaciones
  #  df['calificacion'] = df['calificacion'].fillna(0)   # esto 
    df['calificacion'] = pd.to_numeric(df['calificacion'], errors='coerce')
    
    # Creación de llave única: Matricula + Carrera
    df['id_estudiante'] = df['matricula'].astype(str) + "_" + df['carrera']
    df = df.sort_values(['id_estudiante', 'orden_prioritario'], ascending=True)

    return df


# Suponiendo que carrera_sel y periodo_sel vienen de un selectbox de Streamlit
def filtrar_datos(df, periodo_sel):
    df_filtrado = df.copy()
    
    # Filtro por Periodo
    if periodo_sel != "Todos los periodos":
        df_filtrado = df_filtrado[df_filtrado['periodo'] == periodo_sel]
    
    return df_filtrado


def calcular_metricas_reprobacion(df_normalizado, calificacion_minima):
 
    if df_normalizado.empty:
        return pd.Series(dtype=int)

    # Identificar registros reprobados
    reprobados = df_normalizado[df_normalizado['calificacion'] < calificacion_minima]

    # Contar alumnos por materia
    conteo_reprobadas = reprobados['asignatura'].value_counts()

    # Retornar el Top 10 (o las que gustes) de forma descendente
    return conteo_reprobadas.head(10).sort_values(ascending=True)


def calcular_evolucion_academica(df_limpio, umbral):
    """Calcula reprobación y promedio por periodo."""
    if df_limpio.empty: return pd.DataFrame()

    df_limpio = df_limpio.copy()
    df_limpio['es_reprobado'] = df_limpio['calificacion'] < umbral
    
    # Agrupamos para obtener ambos datos
    evolucion = df_limpio.groupby('periodo').agg(
        total_alumnos=('id_estudiante', 'nunique'),
        reprobados=('es_reprobado', 'sum'),
        promedio_periodo=('calificacion', 'mean') # Nueva métrica
    ).reset_index()
    
    evolucion['porcentaje_reprobacion'] = (evolucion['reprobados'] / evolucion['total_alumnos']) * 100
    evolucion['periodo'] = evolucion['periodo'].astype(str)
    
    return evolucion.sort_values('periodo')



def distribucion_calificaciones(df_limpio):
    """Prepara los datos para un histograma de frecuencias."""


    # Filtrar solo las columnas necesarias y eliminar valores nulos
    df_distribucion = df_limpio[['calificacion']].dropna()

    # Asegurar que la columna sea numérica (float o int)
    df_distribucion['calificacion'] = pd.to_numeric(df_distribucion['calificacion'], errors='coerce')

    # Eliminar posibles errores tras la conversión
    df_distribucion = df_distribucion.dropna(subset=['calificacion'])

    return df_distribucion


def identificar_riesgo_academico2(df_resumen, promedio_min, eficiencia_min, extras_max, umbral_np_sp):
    """
    Analiza las métricas de desempeño y clasifica a los alumnos por nivel de riesgo,
    detallando la razón principal de la alerta.
    """
    if df_resumen.empty:
        return df_resumen

    df_riesgo = df_resumen.copy()

    # LÓGICA DE MOTIVOS
    def determinar_motivo(row):
        motivos = []
        if row['promedio_final'] < promedio_min: motivos.append("Bajo Promedio")
        if (row['conteo_SD'] + row['conteo_NP']) > umbral_np_sp: motivos.append("Abandono/Inasistencia (NP/SD)")
        if row['tasa_extraordinarios'] > (extras_max/100): motivos.append("Alta Recurrencia (Extras)")
        if row['eficiencia_creditos'] < eficiencia_min: motivos.append("Rezago en Créditos")
        
        return ", ".join(motivos) if motivos else "Ninguno"

    df_riesgo['motivo_riesgo'] = df_riesgo.apply(determinar_motivo, axis=1)

    # Condiciones para Riesgo CRÍTICO
    cond_critico = (
        (df_riesgo['promedio_final'] < promedio_min) | 
        ((df_riesgo['conteo_SD'] + df_riesgo['conteo_NP']) > umbral_np_sp)
    )
    
    # Condiciones para Riesgo MODERADO
    cond_moderado = (
        (df_riesgo['promedio_final'] < 80) |  
        (df_riesgo['tasa_extraordinarios'] > 0.20) |
        (df_riesgo['eficiencia_creditos'] < 15)
    )

    df_riesgo['nivel_riesgo'] = np.select(
        [cond_critico, cond_moderado], 
        ['Crítico', 'Moderado'], 
        default='Bajo'
    )

    
    # Damos peso: 40% al promedio, 30% a NP/SD y 30% a extraordinarios
    df_riesgo['alerta_score'] = (
        (100 - df_riesgo['promedio_final'].fillna(0)) * 0.4 +
        ((df_riesgo['conteo_SD'] + df_riesgo['conteo_NP']) * 15) * 0.3 +
        (df_riesgo['tasa_extraordinarios'] * 100) * 0.3
    ).clip(0, 100).round(2)

    # Ordenar por el score más alto (los más urgentes primero)
    return df_riesgo.sort_values(by='alerta_score', ascending=False)