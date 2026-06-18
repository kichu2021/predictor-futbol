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
    xg_l = st.number_input("Goles Esperados (xG) Local", min_value=0.00, value=0.00, step=0.05, key="lxG")
    tiros_l = st.number_input("Tiros al arco Local", min_value=0, value=5, step=1, key="l2")
    corners_l = st.number_input("Córners Local Totales", min_value=0, value=4, step=1, key="l3")
    posesion_l = st.number_input("Posesión Local (%)", min_value=0, max_value=100, value=70, step=1, key="l4")

with col2:
    st.markdown("**🚀 Equipo Visitante**")
    goles_v = st.number_input("Goles Visitante Actuales", min_value=0, value=0, step=1, key="v1")
    xg_v = st.number_input("Goles Esperados (xG) Visitante", min_value=0.00, value=0.00, step=0.05, key="vxG")
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
    
    prob_implicita_l = 1 / cuota_ref_l
    prob_implicita_v = 1 / cuota_ref_v
    total_prob = prob_implicita_l + prob_implicita_v + (1 / cuota_ref_e)
    fuerza_teorica_l = max(0.1, min(0.9, prob_implicita_l / total_prob))
    fuerza_teorica_v = max(0.1, min(0.9, prob_implicita_v / total_prob))
    
    if minuto_actual >= 75:
        factor_frenesi = 1.35  
    elif minuto_actual >= 60:
        factor_frenesi = 1.15  
    else:
        factor_frenesi = 1.00  
        
    # PROYECCIÓN DE GOLES CON VARIABLE xG INTEGRADA
    volumen_minuto_l = ((tiros_l * 1.0) + (corners_l * 0.5) + (xg_l * 2.5)) / minuto_actual
    volumen_minuto_v = ((tiros_v * 1.0) + (corners_v * 0.5) + (xg_v * 2.5)) / minuto_actual
    
    indice_empuje_l = volumen_minuto_l * (posesion_l / 100)
    indice_empuje_v = volumen_minuto_v * (posesion_v / 100)
    
    eficiencia_l = (xg_l + 0.1) / (goles_l + 0.1)
    eficiencia_v = (xg_v + 0.1) / (goles_v + 0.1)
    modificador_xg_l = max(0.8, min(1.3, eficiencia_l))
    modificador_xg_v = max(0.8, min(1.3, eficiencia_v))
    
    xg_restante_l = max(((indice_empuje_l * 0.7) + (fuerza_teorica_l * 0.3)) * 0.18 * tiempo_restante * factor_frenesi * modificador_xg_l, 0.05)
    xg_restante_v = max(((indice_empuje_v * 0.7) + (fuerza_teorica_v * 0.3)) * 0.18 * tiempo_restante * factor_frenesi * modificador_xg_v, 0.05)
    
    n_simulaciones = 10000
    goles_restantes_sim_l = np.random.poisson(xg_restante_l, n_simulaciones)
    goles_restantes_sim_v = np.random.poisson(xg_restante_v, n_simulaciones)
    
    marcador_final_sim_l = goles_l + goles_restantes_sim_l
    marcador_final_sim_v = goles_v + goles_restantes_sim_v
    
    prob_local = (np.sum(marcador_final_sim_l > marcador_final_sim_v) / n_simulaciones) * 100
    prob_empate = (np.sum(marcador_final_sim_l == marcador_final_sim_v) / n_simulaciones) * 100
    prob_visitante = (np.sum(marcador_final_sim_l < marcador_final_sim_v) / n_simulaciones) * 100
    
    st.session_state.historial_predicciones.append({
        "Minuto": minuto_actual, "Local (%)": round(prob_local, 1),
        "Empate (%)": round(prob_empate, 1), "Visitante (%)": round(prob_visitante, 1)
    })
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
    
    # 1. GANADOR DEL PARTIDO (1X2)
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
        
    # 2. MERCADO DE GOLES EN EL 2T (Ambos Anotan)
    st.markdown("---")
    st.subheader("⚽ Ambos Equipos Anotan en el 2do Tiempo")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.metric(label="✅ SÍ Anotan Ambos", value=f"{prob_ambos_anotan:.1f}%")
    with col_g2:
        st.metric(label="❌ NO Anotan Ambos", value=f"{prob_no_anotan:.1f}%")
        
    # 3. MERCADO DE CÓRNERS PROYECTADOS
    st.markdown("---")
    st.subheader("📐 Proyección Total de Córners")
    col_corn1, col_corn2, col_corn3 = st.columns(3)
    with col_corn1:
        st.metric(label="🚩 Finales Local", value=f"{corners_finales_l:.1f}")
    with col_corn2:
        st.metric(label="🚩 Finales Visitante", value=f"{corners_finales_v:.1f}")
    with col_corn3:
        corners_totales_esperados = corners_finales_l + corners_finales_v
        st.metric(label="📊 Total Partido", value=f"{corners_totales_esperados:.1f}")
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
        {"Resultado": "🚀 Visitante", "Tu Probabilidad": f"{prob_visitante:.1f}%", "Tu Cuota Justa": round(cuota_justa_v, 2) if prob_visitante > 0.1 else 1250.00, "Cuota de tu Casa": cuota_casa_v, "¿Tiene Valor?": "✅ SÍ (+EV)" if ventaja_v > 0 else "❌ NO", "Ventaja (%)": f"{ventaja_v:+.1f}%"},
    ]
    
    df_valor = pd.DataFrame(datos_valor)
    st.dataframe(df_valor, use_container_width=True, hide_index=True)
    
    if len(st.session_state.historial_predicciones) > 1:
        st.markdown("---")
        st.subheader("📈 Evolución de Probabilidades en el Tiempo")
        df_hist = pd.DataFrame(st.session_state.historial_predicciones)
        fig = px.line(df_hist, x="Minuto", y=["Local (%)", "Empate (%)", "Visitante (%)"], 
                      title="Tendencia de Probabilidades según avanza el partido",
                      labels={"value": "Probabilidad (%)", "variable": "Mercado"})
        st.plotly_chart(fig, use_container_width=True)
