import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# Configuración de la página web
st.set_page_config(page_title="Predicciones de Fútbol Manual Pro", page_icon="⚽", layout="centered")

# Inicializar el historial en la sesión para la línea de tiempo
if "historial_predicciones" not in st.session_state:
    st.session_state.historial_predicciones = []

st.title("⚽ Predictor Profesional + Comparador de Cuotas")
st.write("Ingresa los datos en vivo para calcular probabilidades, cuotas justas y detectar valor frente a las casas de apuestas.")

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

st.markdown("---")
st.subheader("💰 Cuotas de tu Casa de Apuestas (Opcional para buscar Valor)")

col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    cuota_casa_l = st.number_input("Cuota Casa - Local", min_value=1.01, value=1.80, step=0.01)
with col_c2:
    cuota_casa_e = st.number_input("Cuota Casa - Empate", min_value=1.01, value=3.40, step=0.01)
with col_c3:
    cuota_casa_v = st.number_input("Cuota Casa - Visitante", min_value=1.01, value=4.50, step=0.01)

if st.button("🗑️ Reiniciar Línea de Tiempo Histórica", type="secondary"):
    st.session_state.historial_predicciones = []
    st.toast("Historial reiniciado con éxito")

st.markdown("---")
# --- ALGORITMO MATEMÁTICO DIRECTO ---
if st.button("📊 Calcular Predicción Completa", use_container_width=True, type="primary"):
    tiempo_restante = max(1, 90 - minuto_actual)
    
    volumen_minuto_l = ((tiros_l * 1.5) + (corners_l * 0.8)) / minuto_actual
    volumen_minuto_v = ((tiros_v * 1.5) + (corners_v * 0.8)) / minuto_actual
    
    indice_empuje_l = volumen_minuto_l * (posesion_l / 100)
    indice_empuje_v = volumen_minuto_v * (posesion_v / 100)
    
    xg_restante_l = max(indice_empuje_l * 0.18 * tiempo_restante, 0.05) 
    xg_restante_v = max(indice_empuje_v * 0.18 * tiempo_restante, 0.05)
    
    goles_finales_l = goles_l + xg_restante_l
    goles_finales_v = goles_v + xg_restante_v
    
    n_simulaciones = 10000
    goles_restantes_sim_l = np.random.poisson(xg_restante_l, n_simulaciones)
    goles_restantes_sim_v = np.random.poisson(xg_restante_v, n_simulaciones)
    
    marcador_final_sim_l = goles_l + goles_restantes_sim_l
    marcador_final_sim_v = goles_v + goles_restantes_sim_v
    totales_goles_sim = marcador_final_sim_l + marcador_final_sim_v
    
    prob_local = (np.sum(marcador_final_sim_l > marcador_final_sim_v) / n_simulaciones) * 100
    prob_empate = (np.sum(marcador_final_sim_l == marcador_final_sim_v) / n_simulaciones) * 100
    prob_visitante = (np.sum(marcador_final_sim_l < marcador_final_sim_v) / n_simulaciones) * 100
    
    st.session_state.historial_predicciones.append({
        "Minuto": minuto_actual, "Local (%)": round(prob_local, 1),
        "Empate (%)": round(prob_empate, 1), "Visitante (%)": round(prob_visitante, 1)
    })
    
    ambos_anotan_2t = (goles_restantes_sim_l > 0) & (goles_restantes_sim_v > 0)
    prob_ambos_anotan = (np.sum(ambos_anotan_2t) / n_simulaciones) * 100
    prob_no_anotan = 100.0 - prob_ambos_anotan
    
    corners_minuto_l = ((tiros_l * 0.4) + (corners_l * 0.03)) / minuto_actual
    corners_minuto_v = ((tiros_v * 0.4) + (corners_v * 0.03)) / minuto_actual
    
    corners_finales_l = corners_l + max(0.5, corners_minuto_l * tiempo_restante)
    corners_finales_v = corners_v + max(0.5, corners_minuto_v * tiempo_restante)
    total_corners_partido = corners_finales_l + corners_finales_v

    st.subheader(f"🔮 Proyección Matemática (Minuto {minuto_actual} al 90)")
    st.info(f"⏳ Faltan jugar **{tiempo_restante} minutos** de partido.")
    
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
    st.subheader("📊 Analizador de Valor en Apuestas (1X2)")
    
    cuota_justa_l = 100 / max(0.01, prob_local)
    cuota_justa_e = 100 / max(0.01, prob_empate)
    cuota_justa_v = 100 / max(0.01, prob_visitante)
    
    ventaja_l = ((cuota_casa_l / cuota_justa_l) - 1) * 100
    ventaja_e = ((cuota_casa_e / cuota_justa_e) - 1) * 100
    ventaja_v = ((cuota_casa_v / cuota_justa_v) - 1) * 100
    
    datos_valor = [
        {"Resultado": "🏠 Local", "Tu Probabilidad": f"{prob_local:.1f}%", "Tu Cuota Justa": round(cuota_justa_l, 2) if prob_local > 0.1 else 1250.00, "Cuota de tu Casa": cuota_casa_l, "¿Tiene Valor?": "✅ SÍ (+EV)" if ventaja_l > 0 else "❌ NO", "Ventaja (%)": f"{ventaja_l:+.1f}%"},
        {"Resultado": "🤝 Empate", "Tu Probabilidad": f"{prob_empate:.1f}%", "Tu Cuota Justa": round(cuota_justa_e, 2) if prob_empate > 0.1 else 1250.00, "Cuota de tu Casa": cuota_casa_e, "¿Tiene Valor?": "✅ SÍ (+EV)" if ventaja_e > 0 else "❌ NO", "Ventaja (%)": f"{ventaja_e:+.1f}%"},
        {"Resultado": "🚀 Visitante", "Tu Probabilidad": f"{prob_visitante:.1f}%", "Tu Cuota Justa": round(cuota_justa_v, 2) if prob_visitante > 0.1 else 1250.00, "Cuota de tu Casa": cuota_casa_v, "¿Tiene Valor?": "✅ SÍ (+EV)" if ventaja_v > 0 else "❌ NO", "Ventaja (%)": f"{ventaja_v:+.1f}%"}
    ]
    st.dataframe(pd.DataFrame(datos_valor), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("📈 Evolución de Probabilidades (Línea de Tiempo)")
    if len(st.session_state.historial_predicciones) > 1:
        df_historial = pd.DataFrame(st.session_state.historial_predicciones).sort_values(by="Minuto")
        fig_linea = px.line(df_historial, x="Minuto", y=["Local (%)", "Empate (%)", "Visitante (%)"], markers=True)
        st.plotly_chart(fig_linea, use_container_width=True)
    else:
        st.caption("Inserta cálculos en diferentes minutos para ver la tendencia gráfica aquí.")

    st.markdown("---")
    st.subheader("📊 Mercados de Goles Totales (Final del Partido)")
    col_ou1, col_ou2 = st.columns(2)
    
    lineas_goles = [0.5, 1.5, 2.5, 3.5]
    datos_ou = []
    for linea in lineas_goles:
        prob_over = (np.sum(totales_goles_sim > linea) / n_simulaciones) * 100
        prob_under = 100.0 - prob_over
        datos_ou.append({"Línea": f"Goles {linea}", "Más de (+)": f"{prob_over:.1f}%", "Menos de (-)": f"{prob_under:.1f}%"})
    
    with col_ou1:
        st.dataframe(pd.DataFrame(datos_ou), use_container_width=True, hide_index=True)
    with col_ou2:
        st.write(f"**Sí (GG):** {prob_ambos_anotan:.1f}%")
        st.progress(float(prob_ambos_anotan / 100))
        st.write(f"**No (NG):** {prob_no_anotan:.1f}%")
        st.progress(float(prob_no_anotan / 100))

    st.markdown("---")
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.subheader("⚽ Marcador Esperado")
        st.markdown(f"### `{goles_finales_l:.1f} - {goles_finales_v:.1f}`")
    with col_info2:
        st.subheader("🚩 Córners Proyectados")
        st.markdown(f"### `{total_corners_partido:.1f}`")
        st.caption(f"L: {corners_finales_l:.1f} | V: {corners_finales_v:.1f}")

    st.markdown("---")
    st.subheader("📈 Top Marcadores Finales")
    marcadores = [f"{l}-{v}" for l, v in zip(marcador_final_sim_l, marcador_final_sim_v)]
    df_top = pd.DataFrame(marcadores, columns=["Marcador"])["Marcador"].value_counts(normalize=True).head(8).reset_index()
    df_top.columns = ["Marcador", "Probabilidad"]
    df_top["Probabilidad"] = df_top["Probabilidad"] * 100

    fig = px.bar(df_top, x="Marcador", y="Probabilidad", text=df_top["Probabilidad"].map("{:.1f}%".format), color="Probabilidad", color_continuous_scale="Viridis")
    st.plotly_chart(fig, use_container_width=True)
