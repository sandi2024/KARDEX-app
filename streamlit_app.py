import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- CLASE DE MOTOR DE ANÁLISIS ---
class AnalizadorKardex:
    """Clase encargada de procesar los datos y aplicar lógica de negocio."""
    def __init__(self, dataframe):
        self.df = dataframe

    def obtener_metricas_salud(self, carrera):
        df_c = self.df[self.df['Carrera'] == carrera]
        stats = df_c.groupby('Materia').agg(
            Total=('Alumno_ID', 'count'),
            Reprobados=('Estatus', lambda x: (x == 'Reprobado').sum())
        ).reset_index()
        stats['Porcentaje_Reprobacion'] = (stats['Reprobados'] / stats['Total']) * 100
        return stats

    def obtener_historial_alumno(self, alumno_id):
        return self.df[self.df['Alumno_ID'] == alumno_id]

    def calcular_riesgo(self, alumno_id):
        datos = self.obtener_historial_alumno(alumno_id)
        if datos.empty: return None
        
        promedio = datos['Calificacion'].mean()
        reprobadas = (datos['Estatus'] == 'Reprobado').sum()
        
        # Lógica de riesgo: Alto si promedio < 70 o tiene +2 reprobadas
        nivel = "ALTO" if promedio < 70 or reprobadas >= 2 else "BAJO"
        return {"promedio": promedio, "reprobadas": reprobadas, "nivel": nivel}

    def obtener_datos_comparativos(self):
        # Simulación de métricas complejas por carrera
        carreras = self.df['Carrera'].unique()
        metrics = []
        for c in carreras:
            df_c = self.df[self.df['Carrera'] == c]
            metrics.append({
                "Carrera": c,
                "Promedio": df_c['Calificacion'].mean(),
                "Retencion": np.random.uniform(70, 95), # Simulado
                "Velocidad_Egreso": np.random.uniform(60, 90), # Simulado
                "Titulación": np.random.uniform(50, 85) # Simulado
            })
        return pd.DataFrame(metrics)

# --- CLASES DE INTERFAZ (VISTAS) ---
class VistaDirector:
    @staticmethod
    def render(analizador):
        st.header("📊 Panel de Salud (Director)")
        carrera = st.selectbox("Seleccione Carrera", analizador.df['Carrera'].unique())
        stats = analizador.obtener_metricas_salud(carrera)
        
        umbral = 40
        alertas = stats[stats['Porcentaje_Reprobacion'] > umbral]
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Alertas de Reprobación")
            if not alertas.empty:
                for _, row in alertas.iterrows():
                    st.error(f"🚨 **{row['Materia']}**: {row['Porcentaje_Reprobacion']:.1f}%")
            else:
                st.success("Carrera saludable")
        
        with col2:
            fig = px.bar(stats, x='Materia', y='Porcentaje_Reprobacion', 
                         title=f"Rendimiento en {carrera}",
                         color='Porcentaje_Reprobacion', color_continuous_scale='Reds')
            fig.add_hline(y=umbral, line_dash="dash", line_color="black")
            st.plotly_chart(fig, use_container_width=True)

class VistaTutoria:
    @staticmethod
    def render(analizador):
        st.header("🔍 Buscador de Alumnos (Tutoría)")
        alumno_id = st.text_input("Ingrese ID del Alumno:")
        
        if alumno_id:
            resumen = analizador.calcular_riesgo(alumno_id)
            if resumen:
                c1, c2, c3 = st.columns(3)
                c1.metric("Promedio General", f"{resumen['promedio']:.1f}")
                c2.metric("Materias Reprobadas", resumen['reprobadas'])
                color_riesgo = "inverse" if resumen['nivel'] == "ALTO" else "normal"
                c3.metric("Riesgo Académico", resumen['nivel'], delta_color=color_riesgo)
                
                historial = analizador.obtener_historial_alumno(alumno_id)
                st.dataframe(historial[['Semestre', 'Materia', 'Calificacion', 'Estatus']], use_container_width=True)
            else:
                st.warning("ID no encontrado en la base de datos.")

class VistaComparativa:
    @staticmethod
    def render(analizador):
        st.header("🏎️ Comparativa Inter-Carreras")
        datos = analizador.obtener_datos_comparativos()
        
        categories = ['Promedio', 'Retencion', 'Velocidad_Egreso', 'Titulación']
        fig = go.Figure()

        for _, row in datos.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row[c] for c in categories],
                theta=categories,
                fill='toself',
                name=row['Carrera']
            ))

        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
        st.plotly_chart(fig, use_container_width=True)

# --- MAIN APP ---
def main():
    st.set_page_config(page_title="Kardex Analytics", layout="wide")
    
    # Simulación de carga de datos
    @st.cache_data
    def load_dummy_data():
        data = []
        carreras = [f'Carrera {i+1}' for i in range(6)]
        for c in carreras:
            for a in range(50):
                uid = f"{c[:3]}-{100+a}"
                for s in range(1, 5):
                    data.append({
                        "Carrera": c, "Alumno_ID": uid, "Semestre": s,
                        "Materia": f"Materia {s}A", "Calificacion": np.random.randint(40, 100),
                        "Estatus": "Aprobado" # Se recalcula abajo
                    })
        df = pd.DataFrame(data)
        df['Estatus'] = df['Calificacion'].apply(lambda x: 'Aprobado' if x >= 60 else 'Reprobado')
        return df

    df = load_dummy_data()
    analizador = AnalizadorKardex(df)

    # Sidebar Navigation
    st.sidebar.title("Menú de Análisis")
    opcion = st.sidebar.radio("Ir a:", ["Director", "Tutoría", "Comparativa"])

    if opcion == "Director":
        VistaDirector.render(analizador)
    elif opcion == "Tutoría":
        VistaTutoria.render(analizador)
    else:
        VistaComparativa.render(analizador)

if __name__ == "__main__":
    main()