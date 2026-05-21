import streamlit as st
from src.database import fetch_analisis_reprobacion # La consulta SQL que hicimos antes
from src.analisis import calcular_indice_riesgo
from src.utils import load_css, render_header, create_uabc_metric_card

load_css()
render_header()

st.title("🚨 Sistema de Alerta Temprana")

# Traemos todos los datos de la facultad (o por carrera)
df_riesgo = fetch_analisis_reprobacion()

# Aplicamos el análisis a cada alumno único
resumen_riesgo = []
for matricula in df_riesgo['matricula'].unique():
    historial = df_riesgo[df_riesgo['matricula'] == matricula]
    analisis = calcular_indice_riesgo(historial)
    resumen_riesgo.append({
        "Matrícula": matricula,
        "Nivel de Riesgo": analisis['nivel'],
        "Score": analisis['score']
    })

df_final = pd.DataFrame(resumen_riesgo)

# Visualización
col1, col2 = st.columns([1, 2])

with col1:
    st.write("### Distribución de Riesgo")
    conteo = df_final['Nivel de Riesgo'].value_counts()
    st.bar_chart(conteo)

with col2:
    st.write("### Alumnos que requieren intervención")
    st.dataframe(df_final.sort_values("Score", ascending=False), use_container_width=True)