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
st.subheader("📊 1. Cuotas de Referencia (Pre-Partido)")
st.caption("Estas cuotas definen la fuerza inicial y jerarquía teórica de cada equipo antes de que ruede el balón.")

col_ref1, col_ref2, col_ref3 = st.columns(3)
with col_ref1:
    cuota_ref_l = st.number_input("Cuota Inicial - Local", min_value=1.01, value=2.10, step=0.01, key="ref_l")
with col_ref2:
    cuota_ref_e = st.number_input("Cuota Inicial - Empate", min_value=1.01, value=3.30, step=0.01, key="ref_e")
with col_ref3:
    cuota_ref_v = st.number_input("Cuota Inicial - Visitante", min_value=1.01, value=3.50, step=0.01, key="ref_v")

st.markdown("---")
st.subheader("📝 2. Panel de Control (Datos En Vivo)")

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
st.subheader("💰 3. Cuotas Actuales en Vivo (Para buscar Valor)")

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
# --- ALGORITMO MATEMÁTICO NO LINEAL Y DINÁMICO ---
if st.button("📊 Calcular Predicción Avanzada", use_container_width=True, type="primary"):
    tiempo_restante = max(1, 90 - minuto_actual)
    
    # 1. CÁLCULO DE PODER RELATIVO PRE-PARTIDO (Anclaje Estadístico)
    prob_implicita_l = 1 / cuota_ref_l
    prob_implicita_v = 1 / cuota_ref_v
    total_prob = prob_implicita_l + prob_implicita_v + (1 / cuota_ref_e)
    
    fuerza_teorica_l = max(0.1, min(0.9, prob_implicita_l / total_prob))
    fuerza_teorica_v = max(0.1, min(0.9, prob_implicita_v / total_prob))
    
    # 2. DINÁMICA DE TIEMPO REAL (Multiplicador de Intensidad)
    if minuto_actual >= 75:
        factor_frenesi = 1.35  
    elif minuto_actual >= 60:
        factor_frenesi = 1.15  
    else:
        factor_frenesi = 1.00  
        
    # 3. PROYECCIÓN DE GOLES (En vivo 70% + Jerarquía 30%)
    volumen_minuto_l = ((tiros_l * 1.5) + (corners_l * 0.8)) / minuto_actual
    volumen_minuto_v = ((tiros_v * 1.5) + (corners_v * 0.8)) / minuto_actual
    
    indice_empuje_l = volumen_minuto_l * (posesion_l / 100)
    indice_empuje_v = volumen_minuto_v * (posesion_v / 100)
    
    xg_restante_l = max(((indice_empuje_l * 0.7) + (fuerza_teorica_l * 0.3)) * 0.18 * tiempo_restante * factor_frenesi, 0.05)
    xg_restante_v = max(((indice_empuje_v * 0.7) + (fuerza_teorica_v * 0.3)) * 0.18 * tiempo_restante * factor_frenesi, 0.05)
    
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
    
    # 4. PROYECCIÓN DE CÓRNERS 
    corners_minuto_l = ((tiros_l * 0.4) + (corners_l * 0.03)) / minuto_actual
    corners_minuto_v = ((tiros_v * 0.4) + (corners_v * 0.03)) / minuto_actual
    
    corners_restantes_esperados_l = max(0.2, corners_minuto_l * tiempo_restante * factor_frenesi)
    corners_restantes_esperados_v = max(0.2, corners_minuto_v * tiempo_restante * factor_frenesi)
    
    corners_restantes_sim_l = np.random.poisson(corners_restantes_esperados_l, n_simulaciones)
    corners_restantes_sim_v = np.random.poisson(corners_restantes_esperados_v, n_simulaciones)
    
    totales_corners_sim = corners_l + corners_v + corners_restantes_sim_l + corners_restantes_sim_v
    corners_finales_l = corners_l + corners_restantes_esperados_l
    corners_finales_v = corners_v + corners_restantes_esperados_v

    # --- RENDERIZADO DE INTERFAZ ---
    st.subheader(f"🔮 Proyección Avanzada (Minuto {minuto_actual} al 90)")
    if minuto_actual >= 75:
        st.error(f"🔥 **¡Frenesí de Cierre Activado!** Faltan {tiempo_restante} minutos (Aceleración del +35%).")
    else:
        st.info(f"⏳ Faltan jugar **{tiempo_restante} minutos** bajo ritmo regulado.")
    
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

    # --- RECOMENDADOR INTELIGENTE DE APUESTAS ---
    st.markdown("---")
    st.subheader("🎯 Recomendador Inteligente: La Apuesta Más Acertada")
    
    opciones_apuestas = []
    if ventaja_l > 0: opciones_apuestas.append({"Tipo": "1X2 (+EV)", "Pick": "🏠 Gana Local", "Probabilidad": prob_local, "Ventaja": ventaja_l})
    if ventaja_e > 0: opciones_apuestas.append({"Tipo": "1X2 (+EV)", "Pick": "🤝 Empate", "Probabilidad": prob_empate, "Ventaja": ventaja_e})
    if ventaja_v > 0: opciones_apuestas.append({"Tipo": "1X2 (+EV)", "Pick": "🚀 Gana Visitante", "Probabilidad": prob_visitante, "Ventaja": ventaja_v})
        
    for linea in [0.5, 1.5, 2.5, 3.5]:
        p_over = (np.sum(totales_goles_sim > linea) / n_simulaciones) * 100
        p_under = 100.0 - p_over
        if p_over >= 72: opciones_apuestas.append({"Tipo": "Goles", "Pick": f"⚽ Más de {linea} Goles", "Probabilidad": p_over, "Ventaja": 0})
        if p_under >= 72: opciones_apuestas.append({"Tipo": "Goles", "Pick": f"⚽ Menos de {linea} Goles", "Probabilidad": p_under, "Ventaja": 0})
            
    if prob_ambos_anotan >= 72: opciones_apuestas.append({"Tipo": "Goles", "Pick": "GG (Ambos Anotan)", "Probabilidad": prob_ambos_anotan, "Ventaja": 0})
    elif prob_no_anotan >= 72: opciones_apuestas.append({"Tipo": "Goles", "Pick": "NG (Ambos NO Anotan)", "Probabilidad": prob_no_anotan, "Ventaja": 0})

    for linea_c in [7.5, 8.5, 9.5, 10.5, 11.5]:
        p_over_c = (np.sum(totales_corners_sim > linea_c) / n_simulaciones) * 100
        p_under_c = 100.0 - p_over_c
        if p_over_c >= 72: opciones_apuestas.append({"Tipo": "Córners", "Pick": f"🚩 Más de {linea_c} Córners", "Probabilidad": p_over_c, "Ventaja": 0})
        if p_under_c >= 72: opciones_apuestas.append({"Tipo": "Córners", "Pick": f"🚩 Menos de {linea_c} Córners", "Probabilidad": p_under_c, "Ventaja": 0})

    if opciones_apuestas:
        df_opciones = pd.DataFrame(opciones_apuestas)
        df_con_valor = df_opciones[df_opciones["Ventaja"] > 0]
        
        if not df_con_valor.empty:
            mejor_apuesta = df_con_valor.sort_values(by="Ventaja", ascending=False).iloc[0]
            st.success(f"💥 **Recomendación Profesional (+EV):** {mejor_apuesta['Pick']} ({mejor_apuesta['Tipo']})")
            st.write(f"Ventaja matemática detectada: **{mejor_apuesta['Ventaja']:.1f}%**. Probabilidad real: **{mejor_apuesta['Probabilidad']:.1f}%**.")
        else:
            mejor_apuesta = df_opciones.sort_values(by="Probabilidad", ascending=False).iloc[0]
            st.warning(f"🎯 **Recomendación de Seguridad Absoluta:** {mejor_apuesta['Pick']}")
            st.write(f"Opción numéricamente más probable con un **{mejor_apuesta['Probabilidad']:.1f}%** de acierto.")
    else:
        st.info("Partido muy equilibrado. No hay recomendaciones con suficiente respaldo en este minuto.")

    st.markdown("---")
    st.subheader("📈 Evolución de Probabilidades (Línea de Tiempo)")
    if len(st.session_state.historial_predicciones) > 1:
        df_historial = pd.DataFrame(st.session_state.historial_predicciones).sort_values(by="Minuto")
        fig_linea = px.line(df_historial, x="Minuto", y=["Local (%)", "Empate (%)", "Visitante (%)"], markers=True)
        st.plotly_chart(fig_linea, use_container_width=True)
    else:
        st.caption("Efectúa simulaciones en distintos minutos de juego para generar curvas de tendencia.")

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

    # --- MERCADO DE CÓRNERS COMPLETO ---
    st.markdown("---")
    st.subheader("🚩 Mercados de Córners Totales (Proyección Pro)")
    col_corn1, col_corn2 = st.columns(2)
    
    lineas_corners = [7.5, 8.5, 9.5, 10.5, 11.5]
    datos_ou_c = []
    for linea_c in lineas_corners:
        prob_over_c = (np.sum(totales_corners_sim > linea_c) / n_simulaciones) * 100
        prob_under_c = 100.0 - prob_over_c
        datos_ou_c.append({"Línea": f"Córners {linea_c}", "Más de (+)": f"{prob_over_c:.1f}%", "Menos de (-)": f"{prob_under_c:.1f}%"})
        
    with col_corn1:
        st.dataframe(pd.DataFrame(datos_ou_c), use_container_width=True, hide_index=True)
    with col_corn2:
        st.write(f"**Proyección Córners Local:** {corners_finales_l:.1f}")
        st.write(f"**Proyección Córners Visitante:** {corners_finales_v:.1f}")
        st.metric(label="🚩 Total Córners Esperados", value=f"{(corners_finales_l + corners_finales_v):.1f}")

    st.markdown("---")
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.subheader("⚽ Marcador Esperado Final")
        st.markdown(f"### `{goles_finales_l:.1f} - {goles_finales_v:.1f}`")
    with col_info2:
        st.subheader("🎯 Parámetros Dinámicos Calculados")
        st.write(f"Factor de Aceleración: **x{factor_frenesi:.2f}**")
        st.write(f"xG Restante -> Local: **{xg_restante_l:.2f}** | Vis: **{xg_restante_v:.2f}**")
