import streamlit as st
import pandas as pd
import base64 # Importamos librería necesaria para convertir imágenes a texto (Base64)
import os     # Importamos librería para verificar si existen los archivos
import plotly.express as px

# =========================================================
# CONFIGURACIÓN Y PORTADA
# =========================================================
st.set_page_config(page_title="Circuito Cero | Posadas", page_icon="⚡", layout="wide")

# Inicializar sesión de autenticación si no existe
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# --- FUNCIÓN AUXILIAR PARA CARGAR IMÁGENES LOCALES EN HTML ---
# Esta función es CRUCIAL. Debe estar definida AQUÍ, antes de mostrar_informe
def cargar_imagen_base64(ruta_imagen):
    """Lee una imagen local y la convierte a una cadena Base64 para HTML."""
    if os.path.exists(ruta_imagen): # Verificamos si el archivo existe en la carpeta
        with open(ruta_imagen, "rb") as image_file:
            # Leemos como binario, codificamos y decodificamos a string utf-8
            return base64.b64encode(image_file.read()).decode()
    else:
        # Si no existe, imprimimos una advertencia en la terminal (consola)
        print(f"ADVERTENCIA: No se encontró el archivo de imagen en la ruta: {ruta_imagen}")
    return None # Retorna None si no encuentra el archivo

def mostrar_portada():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; font-size: 80px;'>⭕</h1>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>CIRCUITO CERO</h1>", unsafe_allow_html=True)
        st.write("---")
        clave = st.text_input("Ingrese la clave de acceso:", type="password")
        if st.button("Acceder"):
            if clave == "posadas2026":
                st.session_state.autenticado = True
                # Usamos rerun() para actualizar la página inmediatamente
                st.rerun()
            else:
                st.error("Clave incorrecta.")

# =========================================================
# EL INFORME (EL TABLERO PRINCIPAL)
# =========================================================
def mostrar_informe():
    try:
        # 1. LEEMOS EL EXCEL ORIGINAL
        # Asegúrate de que este archivo también esté en la misma carpeta
        df_original = pd.read_excel('Elecciones_2027_Posadas_SEPTIEMBRE_LIMPIO.xlsx')
        
        # --- BARRA LATERAL: MENÚ Y FILTROS ---
        with st.sidebar:
            st.title("📂 Indice del informe")
            pagina = st.radio("Ir a la sección:", [
                "1. Perfil del Votante", 
                "2. Termómetro Social",
                "3. Economía",
                "4. Evaluación de Gestión",
                "5. Elecciones 2027",
                "6. Ficha Técnica"
            ])
            
            st.write("---")
            st.title("⚙️ Filtros Globales")
            
            # Filtro por Circuito (siempre visible)
            lista_circuitos = ["Todos"] + list(df_original["Circuito"].dropna().unique())
            filtro_circuito = st.selectbox("Seleccionar Circuito:", lista_circuitos)
            
            # Filtros demográficos (visibles desde Página 2)
            filtro_sexo = "Todos"
            filtro_edad = "Todos"
            
            if pagina != "1. Perfil del Votante":
                st.write("---")
                st.title("⚙️ Filtros Demográficos:")
                
                # Filtro por Sexo
                if 'Genero' in df_original.columns:
                    lista_sexo = ["Todos"] + list(df_original["Genero"].dropna().unique())
                    filtro_sexo = st.selectbox("Seleccionar Sexo:", lista_sexo)
                
                # Filtro por Edad
                if 'Rango_Edad' in df_original.columns:
                    lista_edad = ["Todos"] + list(df_original["Rango_Edad"].dropna().unique())
                    filtro_edad = st.selectbox("Seleccionar Rango de Edad:", lista_edad)
            
            st.write("---")
            if st.button("Cerrar Sesión"):
                st.session_state.autenticado = False
                st.rerun()

        # 2. APLICAMOS LOS FILTROS AL DATAFRAME (de forma encadenada)
        df = df_original.copy()
        
        # Filtro de Circuito
        if filtro_circuito != "Todos":
            df = df[df["Circuito"] == filtro_circuito]
            
        # Filtros demográficos (solo si no estamos en la Pág 1)
        if pagina != "1. Perfil del Votante":
            if filtro_sexo != "Todos" and 'Genero' in df.columns:
                df = df[df["Genero"] == filtro_sexo]
            if filtro_edad != "Todos" and 'Rango_Edad' in df.columns:
                df = df[df["Rango_Edad"] == filtro_edad]

        # --- DIBUJAMOS LA CABECERA ---
        # --- DIBUJAMOS LA CABECERA PERSONALIZADA ---
        if pagina == "2. Termómetro Social":
            st.title(f"🌡️ {pagina}")  # Aquí pones el termómetro
        elif pagina == "3. Economía":
            st.title(f"💵 {pagina}")
        elif pagina == "5. Elecciones 2027":
            st.title(f"🗳️ {pagina}")    
        elif pagina == "1. Perfil del Votante":
            st.title(f"👥 {pagina}")
        elif pagina == "6. Ficha Técnica":
            st.title (f"📝 {pagina}")    
        else:
            st.title(f"📊 {pagina}")  # Las demás páginas usan el gráfico de barras
        
        # Mostramos los filtros activos si hay alguno seleccionado
        info_filtros = []
        if filtro_circuito != "Todos": info_filtros.append(f"Circuito: **{filtro_circuito}**")
        if filtro_sexo != "Todos": info_filtros.append(f"Sexo: **{filtro_sexo}**")
        if filtro_edad != "Todos": info_filtros.append(f"Edad: **{filtro_edad}**")
        
        if info_filtros:
            st.info(f"📍 Filtros activos -> {' | '.join(info_filtros)}")
        
        st.write("---")

        # =========================================================
        # PÁGINA 1: PERFIL DEL VOTANTE
        # =========================================================
        if pagina == "1. Perfil del Votante":
            st.write("Composición sociodemográfica de la muestra encuestada.")
            

            # Usamos df_original para el perfil total, a menos que se filtre por circuito
            df_perfil = df_original.copy()
            if filtro_circuito != "Todos":
                df_perfil = df_perfil[df_perfil["Circuito"] == filtro_circuito]

            col_fila1_1, col_fila1_2 = st.columns(2)
            
            with col_fila1_1:
                st.markdown("**Género**")
                df_genero = df_perfil['Genero'].value_counts().reset_index()
                df_genero.columns = ['Genero', 'Cantidad']
                
                fig_genero = px.pie(
                    df_genero, names='Genero', values='Cantidad', hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_genero.update_traces(textinfo='label+value+percent', textposition='outside')
                st.plotly_chart(fig_genero, use_container_width=True)
                
            with col_fila1_2:
                st.markdown("**Edad**")
                if 'Rango_Edad' in df_perfil.columns:
                    conteo_edad = df_perfil['Rango_Edad'].value_counts()
                    st.bar_chart(conteo_edad)
                else:
                    st.info("La columna de Edad no se encuentra en el DataFrame.")

            st.write("---")

            col_fila2_1, col_fila2_2 = st.columns(2)
            
            with col_fila2_1:
                st.markdown("**Ocupación**")
                if 'Ocupaci_n' in df_perfil.columns:
                    conteo_ocup = df_perfil['Ocupaci_n'].value_counts()
                    st.bar_chart(conteo_ocup)
                
            with col_fila2_2:
                st.markdown("**Máximo Nivel de Estudios Alcanzado**")
                columna_estudios = 'M_ximo_nivel_de_estudios_alcanzado'
                if columna_estudios in df_perfil.columns:
                    conteo_estudios = df_perfil[columna_estudios].value_counts()
                    st.bar_chart(conteo_estudios)
                else:
                    st.info(f"Busca el nombre exacto de la columna de estudios en tu base. (Actual: '{columna_estudios}')")

        # =========================================================
        # PÁGINA 2: TERMÓMETRO SOCIAL 
        # =========================================================
        elif pagina == "2. Termómetro Social":
            st.write("Evaluación de demandas y preocupaciones ciudadanas.")
            
            
            # Estilo CSS para botones negros
            st.markdown("""<style>div.stButton > button{background-color:#000000;color:#ffffff;border-radius:6px;border:1px solid #333333;font-weight:bold;}div.stButton > button:hover{background-color:#333333;color:#ffffff;border-color:#000000;}</style>""", unsafe_allow_html=True)
            
            if "pestana_activa" not in st.session_state: st.session_state.pestana_activa = "personal"

            st.markdown("### 📌 Resumen: Principales preocupaciones")
            st.write("Haz clic en el botón de cada tarjeta para desplegar su gráfico detallado:")
            
            col_personal = "_Cu_l_es_su_principal_preocupa"
            col_ciudad = "problema_intendente_recategorizado"
            col_prov = "problema_recategorizado"
            
            top_p, pct_p, df_p = "Sin datos", 0.0, None
            if col_personal in df.columns and not df.empty:
                df_p = (df[col_personal].value_counts(normalize=True) * 100).reset_index()
                df_p.columns = ['Problema', 'Porcentaje']
                if not df_p.empty: top_p = df_p.iloc[0]['Problema']; pct_p = df_p.iloc[0]['Porcentaje']

            top_c, pct_c, df_c = "Sin datos", 0.0, None
            if col_ciudad in df.columns and not df.empty:
                df_c = (df[col_ciudad].value_counts(normalize=True) * 100).reset_index()
                df_c.columns = ['Problema', 'Porcentaje']
                if not df_c.empty: top_c = df_c.iloc[0]['Problema']; pct_c = df_c.iloc[0]['Porcentaje']

            top_pr, pct_pr, df_pr = "Sin datos", 0.0, None
            if col_prov in df.columns and not df.empty:
                df_pr = (df[col_prov].value_counts(normalize=True) * 100).reset_index()
                df_pr.columns = ['Problema', 'Porcentaje']
                if not df_pr.empty: top_pr = df_pr.iloc[0]['Problema']; pct_pr = df_pr.iloc[0]['Porcentaje']

            col_res1, col_res2, col_res3 = st.columns(3)
            with col_res1:
                st.markdown(f"""<div style="background-color:#ffe6e6;padding:12px;border-radius:8px;border:2px solid #ff4d4d;margin-bottom:5px;min-height:105px;"><p style="color:#c0392b;font-weight:bold;margin:0;font-size:12px;">🔴 1. Personal / Familiar</p><p style="color:#900c3f;margin:4px 0;font-size:13px;font-weight:bold;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;" title="{top_p}">{top_p}</p><p style="color:#e74c3c;font-size:20px;font-weight:bold;margin:0;">{pct_p:.1f}%</p></div>""", unsafe_allow_html=True)
                if st.button("Ver gráfico ➔", key="btn_p", use_container_width=True): st.session_state.pestana_activa = "personal"; st.rerun()
            with col_res2:
                st.markdown(f"""<div style="background-color:#f2f4f4;padding:12px;border-radius:8px;border:2px solid #bdc3c7;margin-bottom:5px;min-height:105px;"><p style="color:#2c3e50;font-weight:bold;margin:0;font-size:12px;">🏙️ 2. Ciudad (Posadas)</p><p style="color:#34495e;margin:4px 0;font-size:13px;font-weight:bold;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;" title="{top_c}">{top_c}</p><p style="color:#2980b9;font-size:20px;font-weight:bold;margin:0;">{pct_c:.1f}%</p></div>""", unsafe_allow_html=True)
                if st.button("Ver gráfico ➔", key="btn_c", use_container_width=True): st.session_state.pestana_activa = "ciudad"; st.rerun()
            with col_res3:
                st.markdown(f"""<div style="background-color:#f2f4f4;padding:12px;border-radius:8px;border:2px solid #bdc3c7;margin-bottom:5px;min-height:105px;"><p style="color:#2c3e50;font-weight:bold;margin:0;font-size:12px;">🗺️ 3. Provincia (Misiones)</p><p style="color:#34495e;margin:4px 0;font-size:13px;font-weight:bold;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;" title="{top_pr}">{top_pr}</p><p style="color:#27ae60;font-size:20px;font-weight:bold;margin:0;">{pct_pr:.1f}%</p></div>""", unsafe_allow_html=True)
                if st.button("Ver gráfico ➔", key="btn_pr", use_container_width=True): st.session_state.pestana_activa = "provincia"; st.rerun()

            st.write("---") 

            activa = st.session_state.pestana_activa
            if activa == "personal":
                st.subheader("🔴 Principal Preocupación Personal / Familiar")
                if df_p is not None and not df_p.empty:
                    fig_pers = px.bar(df_p.head(5), x='Problema', y='Porcentaje', text_auto='.1f', color='Porcentaje', color_continuous_scale='Reds')
                    fig_pers.update_layout(xaxis={'categoryorder':'total descending'}, showlegend=False, xaxis_tickfont=dict(size=10), xaxis_tickangle=-20)
                    st.plotly_chart(fig_pers, use_container_width=True)
                    with st.expander("Ver tabla completa (%)"): st.dataframe(df_p.set_index('Problema').round(1))
                else: st.info("No hay datos suficientes.")
            elif activa == "ciudad":
                st.subheader("🏙️ Principal Problema de Posadas")
                if df_c is not None and not df_c.empty:
                    fig_ciu = px.bar(df_c.head(5), x='Problema', y='Porcentaje', text_auto='.1f', color='Porcentaje', color_continuous_scale='Blues')
                    fig_ciu.update_layout(xaxis={'categoryorder':'total descending'}, showlegend=False, xaxis_tickfont=dict(size=10), xaxis_tickangle=-20)
                    st.plotly_chart(fig_ciu, use_container_width=True)
                    with st.expander("Ver tabla completa (%)"): st.dataframe(df_c.set_index('Problema').round(1))
                    if filtro_circuito == "Todos":
                        st.write("---"); st.subheader("Cruce Territorial (Ciudad vs Circuitos)")
                        cruce_territorial = pd.crosstab(df["Circuito"], df[col_ciudad], normalize='index') * 100; st.bar_chart(cruce_territorial)
                else: st.info("No hay datos suficientes.")
            elif activa == "provincia":
                st.subheader("🗺️ Principal Problema de Misiones")
                if df_pr is not None and not df_pr.empty:
                    fig_prov = px.bar(df_pr.head(5), x='Problema', y='Porcentaje', text_auto='.1f', color='Porcentaje', color_continuous_scale='Greens')
                    fig_prov.update_layout(xaxis={'categoryorder':'total descending'}, showlegend=False, xaxis_tickfont=dict(size=10), xaxis_tickangle=-20)
                    st.plotly_chart(fig_prov, use_container_width=True)
                    with st.expander("Ver tabla completa (%)"): st.dataframe(df_pr.set_index('Problema').round(1))
                else: st.info("No hay datos suficientes.")

        # =========================================================
        # PÁGINA 3: ECONOMÍA
        # =========================================================
        elif pagina == "3. Economía":
            st.markdown("""<style>div.stButton > button{background-color:#000000;color:#ffffff;border-radius:6px;border:1px solid #333333;font-weight:bold;}div.stButton > button:hover{background-color:#333333;color:#ffffff;border-color:#000000;}</style>""", unsafe_allow_html=True)
            if "pestana_eco_activa" not in st.session_state: st.session_state.pestana_eco_activa = "personal_eco"

            st.markdown("### 📌 Percepción Económica")
            
            col_eco_pers = "_C_mo_calificar_a_su_situaci_n_econ_mica"
            col_eco_pais = "_Y_la_situaci_n_econ_mica_del_pa_s"
            col_eco_comp = "Cree_que_la_situaci_mica_de_Misiones_es"
            
            top_ep, pct_ep, df_ep = "Sin datos", 0.0, None
            if col_eco_pers in df.columns and not df.empty:
                df_ep = (df[col_eco_pers].value_counts(normalize=True) * 100).reset_index(); df_ep.columns = ['Categoria', 'Porcentaje']
                if not df_ep.empty: top_ep = df_ep.iloc[0]['Categoria']; pct_ep = df_ep.iloc[0]['Porcentaje']

            top_ec, pct_ec, df_ec = "Sin datos", 0.0, None
            if col_eco_pais in df.columns and not df.empty:
                df_ec = (df[col_eco_pais].value_counts(normalize=True) * 100).reset_index(); df_ec.columns = ['Categoria', 'Porcentaje']
                if not df_ec.empty: top_ec = df_ec.iloc[0]['Categoria']; pct_ec = df_ec.iloc[0]['Porcentaje']

            top_co, pct_co, df_co = "Sin datos", 0.0, None
            if col_eco_comp in df.columns and not df.empty:
                df_co = (df[col_eco_comp].value_counts(normalize=True) * 100).reset_index(); df_co.columns = ['Categoria', 'Porcentaje']
                if not df_co.empty: top_co = df_co.iloc[0]['Categoria']; pct_co = df_co.iloc[0]['Porcentaje']

            col_eco1, col_eco2, col_eco3 = st.columns(3)
            with col_eco1:
                st.markdown(f"""<div style="background-color:#ebf5fb;padding:12px;border-radius:8px;border:2px solid #3498db;margin-bottom:5px;min-height:105px;"><p style="color:#2471a3;font-weight:bold;margin:0;font-size:12px;">💳 1. Situación Personal</p><p style="color:#1b4f72;margin:4px 0;font-size:13px;font-weight:bold;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;" title="{top_ep}">{top_ep}</p><p style="color:#2980b9;font-size:20px;font-weight:bold;margin:0;">{pct_ep:.1f}%</p></div>""", unsafe_allow_html=True)
                if st.button("Ver gráfico ➔", key="btn_ep", use_container_width=True): st.session_state.pestana_eco_activa = "personal_eco"; st.rerun()
            with col_eco2:
                st.markdown(f"""<div style="background-color:#e8f8f5;padding:12px;border-radius:8px;border:2px solid #1abc9c;margin-bottom:5px;min-height:105px;"><p style="color:#117a65;font-weight:bold;margin:0;font-size:12px;">📈 2. Situación del País</p><p style="color:#0e6655;margin:4px 0;font-size:13px;font-weight:bold;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;" title="{top_ec}">{top_ec}</p><p style="color:#16a085;font-size:20px;font-weight:bold;margin:0;">{pct_ec:.1f}%</p></div>""", unsafe_allow_html=True)
                if st.button("Ver gráfico ➔", key="btn_ec", use_container_width=True): st.session_state.pestana_eco_activa = "pais_eco"; st.rerun()
            with col_eco3:
                st.markdown(f"""<div style="background-color:#fef9e7;padding:12px;border-radius:8px;border:2px solid #f1c40f;margin-bottom:5px;min-height:105px;"><p style="color:#9a7d0a;font-weight:bold;margin:0;font-size:12px;">⚖️ 3. Comparativa</p><p style="color:#7d6608;margin:4px 0;font-size:13px;font-weight:bold;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;" title="{top_co}">{top_co}</p><p style="color:#d4ac0d;font-size:20px;font-weight:bold;margin:0;">{pct_co:.1f}%</p></div>""", unsafe_allow_html=True)
                if st.button("Ver gráfico ➔", key="btn_co", use_container_width=True): st.session_state.pestana_eco_activa = "comparativa_eco"; st.rerun()

            st.write("---") 

            activa_eco = st.session_state.pestana_eco_activa
            if activa_eco == "personal_eco":
                st.subheader("💳 Desglose: Situación Económica Personal")
                if df_ep is not None and not df_ep.empty:
                    fig_ep = px.bar(df_ep, x='Porcentaje', y='Categoria', orientation='h', text_auto='.1f', color='Porcentaje', color_continuous_scale='Blues')
                    fig_ep.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, yaxis_tickfont=dict(size=11))
                    st.plotly_chart(fig_ep, use_container_width=True)
                    with st.expander("Ver tabla completa (%)"): st.dataframe(df_ep.set_index('Categoria').round(1))
            elif activa_eco == "pais_eco":
                st.subheader("📈 Desglose: Situación Económica del País")
                if df_ec is not None and not df_ec.empty:
                    fig_ec = px.bar(df_ec, x='Porcentaje', y='Categoria', orientation='h', text_auto='.1f', color='Porcentaje', color_continuous_scale='Teal')
                    fig_ec.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, yaxis_tickfont=dict(size=11))
                    st.plotly_chart(fig_ec, use_container_width=True)
                    with st.expander("Ver tabla completa (%)"): st.dataframe(df_ec.set_index('Categoria').round(1))
            elif activa_eco == "comparativa_eco":
                st.subheader("⚖️ Desglose: Comparativa Económica")
                if df_co is not None and not df_co.empty:
                    fig_co = px.bar(df_co, x='Porcentaje', y='Categoria', orientation='h', text_auto='.1f', color='Porcentaje', color_continuous_scale='Cividis')
                    fig_co.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, yaxis_tickfont=dict(size=11))
                    st.plotly_chart(fig_co, use_container_width=True)
                    with st.expander("Ver tabla completa (%)"): st.dataframe(df_co.set_index('Categoria').round(1))

        # =========================================================
        # PÁGINA 4: EVALUACIÓN DE GESTIÓN (CORREGIDA)
        # =========================================================
        elif pagina == "4. Evaluación de Gestión":
            st.write("Evaluación de la imagen y gestión de referentes políticos.")
            
            # Estilo CSS para botones negros
            st.markdown("""<style>div.stButton > button{background-color:#000000;color:#ffffff;border-radius:6px;border:1px solid #333333;font-weight:bold;}div.stButton > button:hover{background-color:#333333;color:#ffffff;border-color:#000000;}</style>""", unsafe_allow_html=True)
            
            if "pestana_ges_activa" not in st.session_state: st.session_state.pestana_ges_activa = "milei"

            st.markdown("### 📌 Resumen: Evaluación de Gestión")
            st.write("Haz clic en el botón de cada tarjeta para ver el desglose:")
            
            # Asegúrate de que estos nombres coincidan con tus columnas en el Excel
            col_ges_milei = "_C_mo_calificar_a_la_ti_n_de_Javier_Milei"
            col_ges_pass = "_C_mo_calificar_a_la_de_Hugo_Passalacqua"
            col_ges_stell = "_y_de_Lalo_Stellato"
            
            # 1. Calculamos los datos
            top_gm, pct_gm, df_gm = "Sin datos", 0.0, None
            if col_ges_milei in df.columns and not df.empty:
                df_gm = (df[col_ges_milei].value_counts(normalize=True) * 100).reset_index(); df_gm.columns = ['Categoria', 'Porcentaje']
                if not df_gm.empty: top_gm = df_gm.iloc[0]['Categoria']; pct_gm = df_gm.iloc[0]['Porcentaje']

            top_gp, pct_gp, df_gp = "Sin datos", 0.0, None
            if col_ges_pass in df.columns and not df.empty:
                df_gp = (df[col_ges_pass].value_counts(normalize=True) * 100).reset_index(); df_gp.columns = ['Categoria', 'Porcentaje']
                if not df_gp.empty: top_gp = df_gp.iloc[0]['Categoria']; pct_gp = df_gp.iloc[0]['Porcentaje']

            top_gs, pct_gs, df_gs = "Sin datos", 0.0, None
            if col_ges_stell in df.columns and not df.empty:
                df_gs = (df[col_ges_stell].value_counts(normalize=True) * 100).reset_index(); df_gs.columns = ['Categoria', 'Porcentaje']
                if not df_gs.empty: top_gs = df_gs.iloc[0]['Categoria']; pct_gs = df_gs.iloc[0]['Porcentaje']

            # --- PREPARAMOS LAS IMÁGENES EN BASE64 PARA HTML ---
            # Aquí es donde se llama a la función auxiliar que definimos arriba[cite: 1.1.2]
            # *IMPORTANTE: Los nombres de archivo deben coincidir EXACTAMENTE (Mayúsculas/minúsculas)
            img_milei_b64 = cargar_imagen_base64("Milei.png")
            img_pass_b64 = cargar_imagen_base64("passalacqua.png")
            img_stell_b64 = cargar_imagen_base64("stellato.png")

            # 2. Creamos las tarjetas con imagen (usando Base64 si existe)
            col_g1, col_g2, col_g3 = st.columns(3)
            
            # Marcador de posición visual por si no encuentra la imagen
            placeholder_img = "https://i.ibb.co/3s83w0q/user-placeholder.png"

            with col_g1:
                # Si se cargó la imagen, creamos el source Base64; si no, el placeholder
                src_gm = f"data:image/png;base64,{img_milei_b64}" if img_milei_b64 else placeholder_img
                
                # Inyectamos el HTML crudo con la imagen Base64[cite: 1.2.5]
                st.markdown(f"""<div style="background-color:#f8f9f9;padding:10px;border-radius:8px;border:2px solid #bdc3c7;margin-bottom:5px;text-align:center;"><img src="{src_gm}" style="width:60px;height:60px;border-radius:50%;object-fit:cover;margin-bottom:5px;box-shadow:0 4px 6px rgba(0,0,0,0.1);" alt="Milei"><p style="color:#2c3e50;font-weight:bold;margin:0;font-size:12px;">Javier Milei</p><p style="color:#34495e;margin:2px 0;font-size:13px;font-weight:bold;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="{top_gm}">{top_gm}</p><p style="color:#2980b9;font-size:18px;font-weight:bold;margin:0;">{pct_gm:.1f}%</p></div>""", unsafe_allow_html=True)
                if st.button("Ver gráfico ➔", key="btn_gm", use_container_width=True): st.session_state.pestana_ges_activa = "milei"; st.rerun()

            with col_g2:
                src_gp = f"data:image/png;base64,{img_pass_b64}" if img_pass_b64 else placeholder_img
                st.markdown(f"""<div style="background-color:#f8f9f9;padding:10px;border-radius:8px;border:2px solid #bdc3c7;margin-bottom:5px;text-align:center;"><img src="{src_gp}" style="width:60px;height:60px;border-radius:50%;object-fit:cover;margin-bottom:5px;box-shadow:0 4px 6px rgba(0,0,0,0.1);" alt="Passalacqua"><p style="color:#2c3e50;font-weight:bold;margin:0;font-size:12px;">Hugo Passalacqua</p><p style="color:#34495e;margin:2px 0;font-size:13px;font-weight:bold;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="{top_gp}">{top_gp}</p><p style="color:#27ae60;font-size:18px;font-weight:bold;margin:0;">{pct_gp:.1f}%</p></div>""", unsafe_allow_html=True)
                if st.button("Ver gráfico ➔", key="btn_gp", use_container_width=True): st.session_state.pestana_ges_activa = "passalacqua"; st.rerun()

            with col_g3:
                # Para JPEG, el source es data:image/jpeg;base64,...
                src_gs = f"data:image/jpeg;base64,{img_stell_b64}" if img_stell_b64 else placeholder_img
                # Corregimos también aquí el corte de sintaxis HTML final que traía tu código original
                st.markdown(f"""<div style="background-color:#f8f9f9;padding:10px;border-radius:8px;border:2px solid #bdc3c7;margin-bottom:5px;text-align:center;"><img src="{src_gs}" style="width:60px;height:60px;border-radius:50%;object-fit:cover;margin-bottom:5px;box-shadow:0 4px 6px rgba(0,0,0,0.1);" alt="Stellato"><p style="color:#2c3e50;font-weight:bold;margin:0;font-size:12px;">Lalo Stellato</p><p style="color:#34495e;margin:2px 0;font-size:13px;font-weight:bold;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="{top_gs}">{top_gs}</p><p style="color:#d35400;font-size:18px;font-weight:bold;margin:0;">{pct_gs:.1f}%</p></div>""", unsafe_allow_html=True)
                if st.button("Ver gráfico ➔", key="btn_gs", use_container_width=True): st.session_state.pestana_ges_activa = "stellato"; st.rerun()

            st.write("---") 

            activa_ges = st.session_state.pestana_ges_activa

            if activa_ges == "milei":
                st.subheader("🔵 Desglose: Gestión Javier Milei")
                if df_gm is not None and not df_gm.empty:
                    fig_gm = px.bar(df_gm, x='Porcentaje', y='Categoria', orientation='h', text_auto='.1f', color='Porcentaje', color_continuous_scale='Blues')
                    fig_gm.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, yaxis_tickfont=dict(size=11))
                    st.plotly_chart(fig_gm, use_container_width=True)
                    with st.expander("Ver tabla completa (%)"): st.dataframe(df_gm.set_index('Categoria').round(1))

            elif activa_ges == "passalacqua":
                st.subheader("🟢 Desglose: Gestión Hugo Passalacqua")
                if df_gp is not None and not df_gp.empty:
                    fig_gp = px.bar(df_gp, x='Porcentaje', y='Categoria', orientation='h', text_auto='.1f', color='Porcentaje', color_continuous_scale='Greens')
                    fig_gp.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, yaxis_tickfont=dict(size=11))
                    st.plotly_chart(fig_gp, use_container_width=True)
                    with st.expander("Ver tabla completa (%)"): st.dataframe(df_gp.set_index('Categoria').round(1))

            elif activa_ges == "stellato":
                st.subheader("🟠 Desglose: Gestión Lalo Stellato")
                if df_gs is not None and not df_gs.empty:
                    fig_gs = px.bar(df_gs, x='Porcentaje', y='Categoria', orientation='h', text_auto='.1f', color='Porcentaje', color_continuous_scale='Oranges')
                    fig_gs.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, yaxis_tickfont=dict(size=11))
                    st.plotly_chart(fig_gs, use_container_width=True)
                    with st.expander("Ver tabla completa (%)"): st.dataframe(df_gs.set_index('Categoria').round(1))
# =========================================================
        # PÁGINA 5: ELECCIONES 2027 (Actualizada con Intención de Voto)
        # =========================================================
        elif pagina == "5. Elecciones 2027":
# --- NUEVA SECCIÓN: Voto Pasado vs Voto Hoy ---
            st.subheader("🗳️ Voto Pasado vs. Intención Actual por Partido")
            
            # *** ATENCIÓN USER ***: Debes reemplazar estos nombres por los exactos y LIMPIOS de tu Excel
            col_voto_pasado = "Voto_anterior" # REEMPLAZAR AQUÍ
            col_voto_hoy = "Voto_futuro"           # REEMPLAZAR AQUÍ
            
# USAMOS 3 COLUMNAS: La del medio (0.05) es para la línea vertical
            col_partido_1, col_linea_1, col_partido_2 = st.columns([0.48, 0.04, 0.48])

            with col_partido_1:
                st.markdown("**¿A qué partido votó en las últimas elecciones?**")
                if col_voto_pasado in df.columns:
                    df_voto_pasado = df[col_voto_pasado].value_counts(normalize=True).reset_index()
                    df_voto_pasado.columns = ['Partido', 'Porcentaje']
                    df_voto_pasado['Porcentaje'] = df_voto_pasado['Porcentaje'] * 100
                    df_voto_pasado = df_voto_pasado.sort_values(by='Porcentaje', ascending=False)

                    fig_pasado = px.bar(df_voto_pasado, x='Porcentaje', y='Partido', orientation='h', text_auto='.1f', color='Porcentaje', color_continuous_scale='Magma')
                    fig_pasado.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, height=400)
                    st.plotly_chart(fig_pasado, use_container_width=True)
                else:
                    st.warning(f"No se encontró '{col_voto_pasado}'. Por favor, edita el código.")

            # === LA LÍNEA VERTICAL ===
            with col_linea_1:
                st.markdown('<div style="border-left: 2px solid #e0e0e0; height: 380px; margin: 40px auto 0 auto;"></div>', unsafe_allow_html=True)

            with col_partido_2:
                st.markdown("**Si las elecciones fueran hoy, ¿a qué partido votaría?**")
                if col_voto_hoy in df.columns:
                    df_voto_hoy = df[col_voto_hoy].value_counts(normalize=True).reset_index()
                    df_voto_hoy.columns = ['Partido', 'Porcentaje']
                    df_voto_hoy['Porcentaje'] = df_voto_hoy['Porcentaje'] * 100
                    df_voto_hoy = df_voto_hoy.sort_values(by='Porcentaje', ascending=False)

                    fig_hoy = px.bar(df_voto_hoy, x='Porcentaje', y='Partido', orientation='h', text_auto='.1f', color='Porcentaje', color_continuous_scale='Viridis')
                    fig_hoy.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, height=400)
                    st.plotly_chart(fig_hoy, use_container_width=True)
                else:
                    st.warning(f"No se encontró '{col_voto_hoy}'. Por favor, edita el código.")


            st.write("---")
            st.subheader("🗳️ Datos preliminares sobre el clima electoral.")

            # --- DEFINICIÓN DE COLUMNAS PARA TARTAS (Originales) ---
            # Basado en el snippet de Excel: Q y R
            col_conocimiento = "_Sab_a_que_el_a_o_qu_ernador_e_intendente" # Asumiendo sanitización de 'ñ'
            col_intencion = "_Tiene_pensado_ir_a_votar"

            # --- NUEVA SECCIÓN: Marcadores para Intención de Voto ---
            # *** ATENCIÓN USER ***: Debes reemplazar estos nombres por los exactos y LIMPIOS de tu Excel
            col_voto_gobernador = "_A_qui_n_votar_a_para_gobernad" # Placeholder para intención Gobernador
            col_voto_intendente = "_y_para_intendente_de_Posadas" # Placeholder para intención Intendente

            # Creamos columnas en Streamlit para poner gráficos de torta lado a lado
            col_p5_1, col_p5_2 = st.columns(2)

            with col_p5_1:
                st.markdown("**¿Sabía que el año que viene hay elecciones a gobernador e intendente?**")
                if col_conocimiento in df.columns:
                    # Cálculo de datos sobre el DataFrame filtrado (df)
                    df_conocimiento = df[col_conocimiento].value_counts(normalize=True).reset_index()
                    df_conocimiento.columns = ['Respuesta', 'Porcentaje']
                    df_conocimiento['Porcentaje'] = df_conocimiento['Porcentaje'] * 100

                    # Gráfico
                    fig_conocimiento = px.pie(
                        df_conocimiento, names='Respuesta', values='Porcentaje', hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Safe
                    )
                    fig_conocimiento.update_traces(textinfo='label+percent', textposition='outside')
                    fig_conocimiento.update_layout(showlegend=False, height=350, margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig_conocimiento, use_container_width=True)
                else:
                    st.warning(f"No se encontró la columna '{col_conocimiento}' en el Excel.")

            with col_p5_2:
                st.markdown("**¿Tiene pensado ir a votar?**")
                if col_intencion in df.columns:
                    # Cálculo de datos sobre el DataFrame filtrado (df)
                    df_intencion = df[col_intencion].value_counts(normalize=True).reset_index()
                    df_intencion.columns = ['Respuesta', 'Porcentaje']
                    df_intencion['Porcentaje'] = df_intencion['Porcentaje'] * 100

                    # Gráfico
                    fig_intencion = px.pie(
                        df_intencion, names='Respuesta', values='Porcentaje', hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_intencion.update_traces(textinfo='label+percent', textposition='outside')
                    fig_intencion.update_layout(showlegend=False, height=350, margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig_intencion, use_container_width=True)
                else:
                    st.warning(f"No se encontró la columna '{col_intencion}' en el Excel.")

            # --- AQUÍ EMPIEZA LA CORRECCIÓN EXACTA ---
            # Separador visual y encabezado
            st.write("---")
            st.subheader("🗳️ Intención de Voto (septiembre 2027)")

            # Creamos nuevas columnas para Gobernador e Intendente (Bar Chart)
            col_voto_1, col_voto_2 = st.columns(2)

            with col_voto_1:
                st.markdown("**Intención de Voto: Gobernador**")
                if col_voto_gobernador in df.columns:
                    # Cálculo de datos (df filtrado)
                    df_v_gob = df[col_voto_gobernador].value_counts(normalize=True).reset_index()
                    df_v_gob.columns = ['Candidato', 'Porcentaje']
                    df_v_gob['Porcentaje'] = df_v_gob['Porcentaje'] * 100
                    df_v_gob = df_v_gob.sort_values(by='Porcentaje', ascending=False) # Ordenar por voto

                    # Gráfico de barras horizontal (mejor para muchos candidatos)
                    fig_v_gob = px.bar(
                        df_v_gob, x='Porcentaje', y='Candidato', 
                        orientation='h', text_auto='.1f', 
                        color='Porcentaje', color_continuous_scale='Viridis'
                    )
                    fig_v_gob.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
                    st.plotly_chart(fig_v_gob, use_container_width=True)
                else:
                    # Advertencia si no encuentra la columna placeholder
                    st.warning(f"No se encontró la columna de placeholder '{col_voto_gobernador}' para Gobernador. Por favor, edita la línea 377 del código con el nombre correcto de tu Excel.")

            with col_voto_2:
                st.markdown("**Intención de Voto: Intendente Posadas**")
                if col_voto_intendente in df.columns:
                    # Cálculo de datos (df filtrado)
                    df_v_int = df[col_voto_intendente].value_counts(normalize=True).reset_index()
                    df_v_int.columns = ['Candidato', 'Porcentaje']
                    df_v_int['Porcentaje'] = df_v_int['Porcentaje'] * 100
                    df_v_int = df_v_int.sort_values(by='Porcentaje', ascending=False) # Ordenar por voto

                    # Gráfico de barras horizontal
                    fig_v_int = px.bar(
                        df_v_int, x='Porcentaje', y='Candidato', 
                        orientation='h', text_auto='.1f', 
                        color='Porcentaje', color_continuous_scale='Plasma'
                    )
                    fig_v_int.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
                    st.plotly_chart(fig_v_int, use_container_width=True)
                else:
                    # Advertencia si no encuentra la columna placeholder
                    st.warning(f"No se encontró la columna de placeholder '{col_voto_intendente}' para Intendente. Por favor, edita la línea 378 del código con el nombre correcto de tu Excel.")

        # =========================================================
        # PÁGINA 6: FICHA TÉCNICA
        # =========================================================
        elif pagina == "6. Ficha Técnica":
            st.write("Especificaciones metodológicas y técnicas de la investigación de opinión pública.")
            st.write("---")

            col_ft1, col_ft2 = st.columns(2)

            with col_ft1:
                st.markdown("""
                * **Ámbito geográfico:** Ciudad de Posadas.
                * **Población objeto / Universo:** Mayores de 16 años habilitados para votar.
                * **Tamaño de la muestra / Casos efectivos:** 626 encuestas.
                * **Tipo de muestreo:** Probabilístico, estratificado por circuitos, sexo y edad.
                """)

            with col_ft2:
                st.markdown("""
                * **Procedimiento de recolección:** Encuestas presenciales en hogares / dispositivos móviles con KoboToolbox.
                * **Fecha de trabajo de campo:** Septiembre de 2026.
                * **Nivel de confianza y Margen de error:** Nivel de confianza del 95%, margen de error aproximado de +/- 3%.
                * **Instrumento de medición:** Cuestionario estructurado.
                """)

    except FileNotFoundError:
        st.error("No se encontró el Excel limpio. Asegúrate de correr primero tu archivo de limpieza.")
    except KeyError as e:
        st.error(f"Ocurrió un error con el nombre de una columna: {e}")

# =========================================================
# CONTROLADOR DE VISTAS
# =========================================================
if not st.session_state.autenticado:
    # Si no está autenticado, mostramos la portada de login
    mostrar_portada()
else:
    # Si está autenticado, mostramos el tablero completo
    mostrar_informe()
