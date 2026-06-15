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

# --- NUEVA SECCIÓN: INGRESO DE CUOTAS DE LA CASA DE APUESTAS ---
st.markdown("---")
st.subheader("💰 Cuotas de tu Casa de Apuestas (Opcional para buscar Valor)")
st.caption("Ingresa las cuotas que ofrece tu casa de apuestas en este momento para comparar.")
col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    cuota_casa_l = st.number_input("Cuota Casa - Local", min_value=1.01, value=1.80, step=0.01)
with col_c2:
    cuota_casa_e = st.number_input("Cuota Casa - Empate", min_value=1.01, value=3.40, step=0.01)
with col_c3:
    cuota_casa_v = st.number_input("Cuota Casa - Visitante", min_value=1.01, value=4.50, step=0.01)

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
    
    # NUEVA SECCIÓN: TABLA COMPARATIVA DE CUOTAS Y VALOR (+EV)
    st.subheader("📊 Analizador de Valor en Apuestas (1X2)")
    
    # Cálculo de Cuotas Justas (evitando división por cero)
    cuota_justa_l = 100 / prob_local if prob_local > 0 else 999.0
    cuota_justa_e = 100 / prob_empate if prob_empate > 0 else 999.0
    cuota_justa_v = 100 / prob_visitante if prob_visitante > 0 else 999.0
    
    # Cálculo de Ventaja/Valor: (Cuota Casa / Cuota Justa) - 1
    valor_l = (cuota_casa_l / cuota_justa_l) - 1
    valor_e = (cuota_casa_e / cuota_justa_e) - 1
    valor_v = (cuota_casa_v / cuota_justa_v) - 1
    
    datos_cuotas = [
        {
            "Resultado": "🏠 Local",
            "Tu Probabilidad": f"{prob_local:.1f}%",
            "Tu Cuota Justa": f"{cuota_justa_l:.2f}",
            "Cuota de tu Casa": f"{cuota_casa_l:.2f}",
            "¿Tiene Valor?": "✅ SÍ (+EV)" if valor_l > 0 else "❌ NO",
            "Ventaja (%)": f"+{valor_l*100:.1f}%" if valor_l > 0 else f"{valor_l*100:.1f}%"
        },
        {
            "Resultado": "🤝 Empate",
            "Tu Probabilidad": f"{prob_empate:.1f}%",
            "Tu Cuota Justa": f"{cuota_justa_e:.2f}",
            "Cuota de tu Casa": f"{cuota_casa_e:.2f}",
            "¿Tiene Valor?": "✅ SÍ (+EV)" if valor_e > 0 else "❌ NO",
            "Ventaja (%)": f"+{valor_e*100:.1f}%" if valor_e > 0 else f"{valor_e*100:.1f}%"
        },
        {
            "Resultado": "🚀 Visitante",
            "Tu Probabilidad": f"{prob_visitante:.1f}%",
            "Tu Cuota Justa": f"{cuota_justa_v:.2f}",
            "Cuota de tu Casa": f"{cuota_casa_v:.2f}",
            "¿Tiene Valor?": "✅ SÍ (+EV)" if valor_v > 0 else "❌ NO",
            "Ventaja (%)": f"+{valor_v*100:.1f}%" if valor_v > 0 else f"{valor_v*100:.1f}%"
        }
    ]
    
    df_cuotas = pd.DataFrame(datos_cuotas)
    st.dataframe(df_cuotas, use_container_width=True, hide_index=True)
    st.caption("💡 Tip: Si dice '✅ SÍ (+EV)', significa que la casa paga más de lo que la matemática sugiere. Es una apuesta rentable a largo plazo.")
    
    st.markdown("---")
    
    # GRÁFICO DE LÍNEA DE TIEMPO EVOLUTIVA
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
        st.caption("Inserta cálculos en diferentes minutos para ver la tendencia gráfica aquí.")

    st.markdown("---")

    # MERCADO OVER/UNDER (MÁS/MENOS GOLES)
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
