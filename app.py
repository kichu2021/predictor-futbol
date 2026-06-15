import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# Configuración de la página web
st.set_page_config(page_title="Predicciones de Fútbol Manual Pro", page_icon="⚽", layout="centered")

# Inicializar el historial en la sesión para la línea de tiempo
if "historial_predicciones" not in st.session_state:
    st.session_state.historial_predicciones = []

st.title("⚽ Predictor Profesional - Modo Manual Pro")
st.write("Ingresa los datos en vivo. Cada simulación guardará un punto en la línea de tiempo histórica.")

st.markdown("---")

st.subheader("📝 Panel de Control (Ingreso manual)")

# Selector de minuto del partido
minuto_actual = st.slider("⏱️ Minuto actual del partido:", min_value=1, max_value=89, value=45, step=1)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**🏠 Equipo Local**")
    goles_l = st.number_input("Goles Local Actuales", min_value=0, value=0, step=1, key="l1")
    tiros_l = st.number_input("Tiros al arco Local", min_value=0, value=5, step=1, key="l2")
    corners_l = st.number_input("Córners Local Totales", min_value=0, value=4, step=1, key="l3")
    posesion_l = st.number_input("Posesión Local (%)", min_value=0, max_value=100, value=70, step=1, key="l4")

with col2:
    st.markdown("**🚀 Equipo Visitante**")
    goles_v = st.number_input("Goles Visitante Actuales", min_value=0, value=0, step=1, key="v1")
    tiros_v = st.number_input("Tiros al arco Visitante", min_value=0, value=0, step=1, key="v2")
    corners_v = st.number_input("Córners Visitante Totales", min_value=0, value=0, step=1, key="v3")
    posesion_v = st.number_input("Posesión Visitante (%)", min_value=0, max_value=100, value=30, step=1, key="v4")

# Botón para reiniciar la línea de tiempo histórica
if st.button("🗑️ Reiniciar Línea de Tiempo Histórica", type="secondary"):
    st.session_state.historial_predicciones = []
    st.toast("Historial reiniciado con éxito")

st.markdown("---")

# --- ALGORITMO MATEMÁTICO DIRECTO ---
if st.button("📊 Calcular Predicción Completa", use_container_width=True, type="primary"):
    # Calcular el tiempo restante del partido
    tiempo_restante = max(1, 90 - minuto_actual)
    
    # 1. Volumen Ofensivo generado POR MINUTO hasta ahora
    volumen_minuto_l = ((tiros_l * 1.5) + (corners_l * 0.8)) / minuto_actual
    volumen_minuto_v = ((tiros_v * 1.5) + (corners_v * 0.8)) / minuto_actual
    
    # 2. Factor de dominio enfocado por posesión
    indice_empuje_l = volumen_minuto_l * (posesion_l / 100)
    indice_empuje_v = volumen_minuto_v * (posesion_v / 100)
    
    # 3. Estimación de xG Ajustado para el tiempo restante (Tasa Lambda dinámico)
    xg_restante_l = max(indice_empuje_l * 0.18 * tiempo_restante, 0.05) 
    xg_restante_v = max(indice_empuje_v * 0.18 * tiempo_restante, 0.05)
    
    goles_finales_l = goles_l + xg_restante_l
    goles_finales_v = goles_v + xg_restante_v
    
    # Montecarlo 10k con Poisson ajustado por minutos
    n_simulaciones = 10000
    goles_restantes_sim_l = np.random.poisson(xg_restante_l, n_simulaciones)
    goles_restantes_sim_v = np.random.poisson(xg_restante_v, n_simulaciones)
    
    marcador_final_sim_l = goles_l + goles_restantes_sim_l
    marcador_final_sim_v = goles_v + goles_restantes_sim_v
    totales_goles_sim = marcador_final_sim_l + marcador_final_sim_v
    
    # Probabilidades Finales
    prob_local = (np.sum(marcador_final_sim_l > marcador_final_sim_v) / n_simulaciones) * 100
    prob_empate = (np.sum(marcador_final_sim_l == marcador_final_sim_v) / n_simulaciones) * 100
    prob_visitante = (np.sum(marcador_final_sim_l < marcador_final_sim_v) / n_simulaciones) * 100
    
    # Guardar en el historial de la línea de tiempo
    st.session_state.historial_predicciones.append({
        "Minuto": minuto_actual,
        "Local (%)": round(prob_local, 1),
        "Empate (%)": round(prob_empate, 1),
        "Visitante (%)": round(prob_visitante, 1)
    })
    
    # Ambos Anotan (en el tiempo restante)
    ambos_anotan_2t = (goles_restantes_sim_l > 0) & (goles_restantes_sim_v > 0)
    prob_ambos_anotan = (np.sum(ambos_anotan_2t) / n_simulaciones) * 100
    prob_no_anotan = 100.0 - prob_ambos_anotan
    
    # Córners dinámicos por tiempo restante
    corners_minuto_l = ((tiros_l * 0.4) + (posesion_l * 0.03)) / minuto_actual
    corners_minuto_v = ((tiros_v * 0.4) + (posesion_v * 0.03)) / minuto_actual
    
    corners_finales_l = corners_l + max(0.5, corners_minuto_l * tiempo_restante)
    corners_finales_v = corners_v + max(0.5, corners_minuto_v * tiempo_restante)
    total_corners_partido = corners_finales_l + corners_finales_v

    # --- SECCIÓN VISUAL DE RESULTADOS OPTIMIZADA ---
    st.subheader(f"🔮 Proyección Matemática (Minuto {minuto_actual} al 90)")
    st.info(f"⏳ Faltan jugar **{tiempo_restante} minutos** de partido.")
    
    # Probabilidades 1X2 con Barras de Progreso Visuales
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric(label="🏠 Victoria Local", value=f"{prob_local:.1f}%")
        st.progress(float(prob_local / 100))
    with col_res2:
        st.metric(label="🤝 Empate", value=f"{prob_empate:.1f}%")
        st.progress(float(prob_empate / 100))
    with col_res3:
        st.metric(label="🚀 Victoria Visitante", value=f"{prob_visitante:.1f}%")
        st.progress(float(prob_visitante / 100))
    
    st.markdown("---")
    
    # NUEVA SECCIÓN: GRÁFICO DE LÍNEA DE TIEMPO EVOLUTIVA
    st.subheader("📈 Evolución de Probabilidades (Línea de Tiempo)")
    if len(st.session_state.historial_predicciones) > 1:
        df_historial = pd.DataFrame(st.session_state.historial_predicciones).sort_values(by="Minuto")
        fig_linea = px.line(
            df_historial, 
            x="Minuto", 
            y=["Local (%)", "Empate (%)", "Visitante (%)"],
            labels={"value": "Probabilidad (%)", "variable": "Resultado"},
            markers=True,
            color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c"]
        )
        fig_linea.update_layout(xaxis_range=[0, 90], height=300, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_linea, use_container_width=True)
    else:
        st.caption("Inserta cálculos en diferentes minutos (ej. Minuto 15, luego 45, luego 70) para ver la tendencia gráfica aquí.")

    st.markdown("---")

    # NUEVA SECCIÓN: MERCADO OVER/UNDER (MÁS/MENOS GOLES)
    st.subheader("📊 Mercados de Goles Totales (Final del Partido)")
    col_ou1, col_ou2 = st.columns(2)
    
    lineas_goles = [0.5, 1.5, 2.5, 3.5]
    datos_ou = []
    for linea in lineas_goles:
        prob_over = (np.sum(totales_goles_sim > linea) / n_simulaciones) * 100
        prob_under = 100.0 - prob_over
        datos_ou.append({"Línea": f"Goles {linea}", "Más de (+)": f"{prob_over:.1f}%", "Menos de (-)": f"{prob_under:.1f}%"})
    
    df_ou = pd.DataFrame(datos_ou)
    
    with col_ou1:
        st.markdown("**Líneas Estadísticas Over/Under**")
        st.dataframe(df_ou, use_container_width=True, hide_index=True)
        
    with col_ou2:
        st.markdown("**Ambos Anotan (Del minuto %d al 90)**" % minuto_actual)
        st.write(f"**Sí (GG):** {prob_ambos_anotan:.1f}%")
        st.progress(float(prob_ambos_anotan / 100))
        st.write(f"**No (NG):** {prob_no_anotan:.1f}%")
        st.progress(float(prob_no_anotan / 100))

    st.markdown("---")

    # Tarjetas de Hitos Clave (Goles y Córners)
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.subheader("⚽ Marcador Esperado")
        st.markdown(f"### `{goles_finales_l:.1f} - {goles_finales_v:.1f}`")
        st.caption("Promedio estimado del resultado final con base en el xG proyectado.")
    with col_info2:
        st.subheader("🚩 Córners Totales")
        st.markdown(f"### `{total_corners_partido:.1f}`")
        st.caption(f"Local: {corners_finales_l:.1f} | Visitante: {corners_finales_v:.1f}")

    st.markdown("---")

    # Gráfico de Marcadores más Probables
    st.markdown("### 📈 Top Marcadores Finales Más Probables")
    marcadores = [f"{l}-{v}" for l, v in zip(marcador_final_sim_l, marcador_final_sim_v)]
    df_marcadores = pd.DataFrame(marcadores, columns=["Marcador"])
    df_top = df_marcadores["Marcador"].value_counts(normalize=True).head(8).reset_index()
    df_top.columns = ["Marcador", "Probabilidad"]
    df_top["Probabilidad"] = df_top["Probabilidad"] * 100

    fig = px.bar(
        df_top, 
        x="Marcador", 
        y="Probabilidad", 
        text=df_top["Probabilidad"].map("{:.1f}%".format),
        labels={"Probabilidad": "Probabilidad (%)", "Marcador": "Marcador Final"},
        color="Probabilidad",
        color_continuous_scale="Viridis"
    )
    fig.update_traces(textposition="outside", marker_line_color="black", marker_line_width=1)
    fig.update_layout(showlegend=False, yaxis_range=[0, df_top["Probabilidad"].max() + 5], height=320)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # NUEVA SECCIÓN: EXPORTACIÓN DE DATOS SIMULADOS
    st.subheader("💾 Exportar Simulación de Montecarlo")
    st.caption("Descarga el desglose matemático completo de las 10,000 iteraciones simuladas por el algoritmo.")
    
    df_simulacion_completa = pd.DataFrame({
        "Simulacion_ID": np.arange(1, n_simulaciones + 1),
        "Goles_Restantes_Local": goles_restantes_sim_l,
        "Goles_Restantes_Visitante": goles_restantes_sim_v,
        "Marcador_Final_Local": marcador_final_sim_l,
        "Marcador_Final_Visitante": marcador_final_sim_v,
        "Total_Goles_Partido": totales_goles_sim
    })
    
    csv_data = df_simulacion_completa.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Descargar datos de simulación (.CSV)",
        data=csv_data,
        file_name=f"simulacion_partido_minuto_{minuto_actual}.csv",
        mime="text/csv",
        use_container_width=True
    )
