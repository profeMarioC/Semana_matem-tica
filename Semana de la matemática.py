import streamlit as st
import pandas as pd
import plotly.express as px
import re
from fpdf import FPDF
import os

# Configuración inicial de la página
st.set_page_config(page_title="Semana de la Matemática LCC", page_icon="🧮", layout="wide")

# Cabecera con imágenes ajustadas
col_ib, col_logo, col_tit, col_iconos, col_carmelin = st.columns([0.8, 0.8, 3.5, 1.5, 1])

with col_ib:
    if os.path.exists("ib.png"): 
        st.image("ib.png", width=80) 
with col_logo:
    if os.path.exists("logo.png"): 
        st.image("logo.png", width=80) 
with col_tit:
    st.title("🏆Semana de la Matemática Liceo Carmela Carvajal")
    st.subheader("Departamento de matemática")
with col_iconos:
    st.write("") 
    c_pi, c_e, c_phi = st.columns(3)
    with c_pi:
        if os.path.exists("pi.png"): st.image("pi.png", width=75) 
    with c_e:
        if os.path.exists("e.png"): st.image("e.png", width=75)
    with c_phi:
        if os.path.exists("phi.png"): st.image("phi.png", width=75)
with col_carmelin:
    if os.path.exists("carmelin.png"): 
        st.image("carmelin.png", width=130) 

st.divider()

# Función para crear el PDF con diseño e imágenes corregido
def crear_pdf_ranking(df_top):
    pdf = FPDF()
    pdf.add_page()
    
    # Insertar logos en el PDF si existen
    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=10, y=8, w=22)
    if os.path.exists("ib.png"):
        pdf.image("ib.png", x=35, y=8, w=22) 
    if os.path.exists("carmelin.png"):
        pdf.image("carmelin.png", x=175, y=8, w=22)
        
    # Empujar el cursor hacia abajo para no tapar los logos
    pdf.set_y(35)
        
    # Título PDF
    pdf.set_fill_color(75, 75, 255) 
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 16)
    # Codificar a latin-1 para que reconozca tildes en el PDF
    titulo = "Cuadro de Honor - Semana de la Matemática".encode('latin-1', 'replace').decode('latin-1')
    pdf.cell(0, 15, titulo, ln=True, align='C', fill=True)
    pdf.ln(5)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(0, 10, "Liceo Carmela Carvajal", ln=True, align='C')
    pdf.ln(8)
    
    # Tabla PDF
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(230, 230, 230) 
    pdf.cell(100, 10, "Estudiante", border=1, fill=True)
    pdf.cell(40, 10, "Curso", border=1, align='C', fill=True)
    pdf.cell(40, 10, "Puntaje", border=1, align='C', fill=True)
    pdf.ln()
    
    pdf.set_font("Arial", '', 11)
    for _, row in df_top.iterrows():
        # Limpiador optimizado para FPDF que respeta los símbolos (como el ° del curso)
        def limpiar(texto):
            return str(texto).encode('latin-1', 'replace').decode('latin-1')
        
        nombre = limpiar(row['Estudiante'])[:35] 
        curso = limpiar(row['Curso'])
        puntaje = str(row['Puntaje'])
        
        pdf.cell(100, 10, nombre, border=1)
        pdf.cell(40, 10, curso, border=1, align='C')
        pdf.cell(40, 10, puntaje, border=1, align='C')
        pdf.ln()
    
    archivo_temp = "Ranking_Temp.pdf"
    pdf.output(archivo_temp)
    with open(archivo_temp, "rb") as f:
        pdf_bytes = f.read()
    os.remove(archivo_temp) 
    return pdf_bytes

# 1. Carga de Datos y Validación
@st.cache_data(ttl=60)
def cargar_datos():
    ruta_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR_5qT4v-kTR2fXzMOmXWvj2glDtw_kKahKyK2dLxFZk6SeVDqG8ZWz_xaM1L5BT4vi713ClqkanJm4/pub?output=csv" 
    try:
        df = pd.read_csv(ruta_csv)
        df.columns = df.columns.str.strip()
        
        col_codigo = [col for col in df.columns if 'Código del reto' in col][0]
        df['Día de la semana'] = df[col_codigo].astype(str).str.split(' ').str[0]
        idx_codigo = list(df.columns).index(col_codigo)
        
        respuestas_correctas = {
            "Lunes 7° y 8°": "60", "Lunes I° y II°": "17", "Lunes III° y IV°": "29",
            "Martes 7° y 8°": "2", "Martes I° y II°": "750", "Martes III° y IV°": "12",
            "Miércoles 7° y 8°": "d", "Miércoles I° y II°": "13112221", "Miércoles III° y IV°": "10",
            "Jueves 7° y 8°": "20", "Jueves I° y II°": "204", "Jueves III° y IV°": "10",
            "Viernes 7° y 8°": "9", "Viernes I° y II°": "5", "Viernes III° y IV°": "512"
        }
        
        def evaluar_respuesta(fila):
            reto_elegido = str(fila[col_codigo]).strip()
            if reto_elegido in respuestas_correctas:
                esperada = str(respuestas_correctas[reto_elegido]).strip().lower()
                valores_respuestas = fila.values[idx_codigo + 1:]
                texto_respuestas = " ".join([str(val).lower() for val in valores_respuestas])
                
                elementos = re.findall(r'\d+|[a-zñáéíóú]+', texto_respuestas)
                if esperada in elementos:
                    return 10 
            return 0 
            
        df['Puntaje_Obtenido'] = df.apply(evaluar_respuesta, axis=1)
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

df = cargar_datos()

if not df.empty:
    # 2. Métricas Generales
    total_participantes = df['Nombre completo'].nunique()
    total_respuestas = len(df)
    
    if df['Puntaje_Obtenido'].sum() > 0:
        curso_top = df.groupby('Curso')['Puntaje_Obtenido'].sum().idxmax()
    else:
        curso_top = "Aún sin puntos"
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Estudiantes Participantes", total_participantes)
    col2.metric("Total de Retos Resueltos", total_respuestas)
    col3.metric("Curso Líder Actual", curso_top)
    
    st.divider()

    # 3. Gráficos y Rankings Colectivos
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        st.header("📊 Puntaje por Curso")
        puntaje_curso = df.groupby('Curso')['Puntaje_Obtenido'].sum().reset_index()
        puntaje_curso = puntaje_curso.sort_values(by='Puntaje_Obtenido', ascending=True)
        
        fig_cursos = px.bar(
            puntaje_curso, x='Puntaje_Obtenido', y='Curso', orientation='h',
            text='Puntaje_Obtenido', color='Puntaje_Obtenido', color_continuous_scale='Blues'
        )
        fig_cursos.update_layout(xaxis_title="Puntaje Total", yaxis_title="")
        st.plotly_chart(fig_cursos, use_container_width=True)

    with col_der:
        st.header("🥇 Top 10 Estudiantes Destacados")
        top_estudiantes = df.groupby(['Nombre completo', 'Curso'])['Puntaje_Obtenido'].sum().reset_index()
        top_estudiantes = top_estudiantes.sort_values(by='Puntaje_Obtenido', ascending=False).head(10)
        df_top_mostrar = top_estudiantes.rename(columns={'Nombre completo': 'Estudiante', 'Puntaje_Obtenido': 'Puntaje'})
        
        st.dataframe(df_top_mostrar, hide_index=True, use_container_width=True)
        
        if not df_top_mostrar.empty:
            pdf_data = crear_pdf_ranking(df_top_mostrar)
            st.download_button(
                label="📄 Descargar Ranking en PDF",
                data=pdf_data,
                file_name="Ranking_Matematica_LCC.pdf",
                mime="application/pdf"
            )

    st.divider()
    
    # 4. Buscador de Logros Individuales
    st.header("👤 Buscador de Logros Individuales")
    lista_estudiantes = sorted(df['Nombre completo'].dropna().unique())
    estudiante_seleccionado = st.selectbox("Selecciona o escribe el nombre de la estudiante:", [""] + lista_estudiantes)
    
    if estudiante_seleccionado:
        df_estudiante = df[df['Nombre completo'] == estudiante_seleccionado]
        puntaje_total_est = df_estudiante['Puntaje_Obtenido'].sum()
        retos_intentados = len(df_estudiante)
        retos_correctos = len(df_estudiante[df_estudiante['Puntaje_Obtenido'] == 10])
        curso_est = df_estudiante['Curso'].iloc[0]
        
        st.markdown(f"### Perfil de {estudiante_seleccionado} ({curso_est})")
        if retos_correctos >= 5:
            st.success("🌟 ¡Racha Perfecta! Ha resuelto exitosamente los 5 retos de la semana.")
            
        c_est1, c_est2, c_est3 = st.columns(3)
        c_est1.metric("Puntaje Acumulado", f"{puntaje_total_est} pts")
        c_est2.metric("Retos Intentados", retos_intentados)
        c_est3.metric("Respuestas Correctas", retos_correctos)
        
        st.write("📅 Historial de envíos:")
        historial = df_estudiante[['Día de la semana', 'Puntaje_Obtenido']].rename(columns={'Puntaje_Obtenido': 'Puntaje Logrado'})
        st.dataframe(historial, hide_index=True, use_container_width=True)

    st.divider()

    # 5. Participación por Día
    st.header("📈 Nivel de Participación por Día")
    participacion_dia = df['Día de la semana'].value_counts().reindex(['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'], fill_value=0).reset_index()
    participacion_dia.columns = ['Día', 'Cantidad de Respuestas']
    
    fig_dias = px.line(participacion_dia, x='Día', y='Cantidad de Respuestas', markers=True, line_shape='spline')
    fig_dias.update_traces(line_color='#FF4B4B', marker=dict(size=10))
    st.plotly_chart(fig_dias, use_container_width=True)

else:
    st.info("Esperando a que ingresen los primeros datos desde el formulario...")