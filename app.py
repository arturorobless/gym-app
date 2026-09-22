import json
import random
from datetime import date
import requests
import streamlit as st

st.set_page_config(page_title="Gym Routine", page_icon="🏋️‍♂️", layout="centered")

def cargar_ejercicios():
    with open("exercises.json", "r") as f:
        return json.load(f)

def seleccionar_ejercicios_variados(ejercicios, cantidad):
    """Selecciona ejercicios priorizando que pertenezcan a tipos distintos."""
    por_tipo = {}
    for ej in ejercicios:
        t = ej["tipo"]
        if t not in por_tipo:
            por_tipo[t] = []
        por_tipo[t].append(ej)

    tipos_disponibles = list(por_tipo.keys())
    random.shuffle(tipos_disponibles)

    elegidos = []

    # 1. Extraer un ejercicio de cada tipo distinto primero
    for tipo in tipos_disponibles:
        if len(elegidos) < cantidad and por_tipo[tipo]:
            ej_al_azar = random.choice(por_tipo[tipo])
            elegidos.append(ej_al_azar)
            por_tipo[tipo].remove(ej_al_azar)

    # 2. Rellenar si faltan ejercicios sin repetir
    if len(elegidos) < cantidad:
        sobrantes = [ej for lista in por_tipo.values() for ej in lista]
        faltan = cantidad - len(elegidos)
        if sobrantes:
            elegidos.extend(random.sample(sobrantes, min(faltan, len(sobrantes))))

    elegidos.sort(key=lambda x: x["tipo"])
    return elegidos

# Base de datos
datos = cargar_ejercicios()

# Configuración de los días de entrenamiento
CONFIG_RUTINAS = {
    "Pierna (5 ejercicios)": [
        {"musculo": "pierna", "cantidad": 5}
    ],
    "Espalda y Tríceps (4 espalda + 2 tríceps)": [
        {"musculo": "espalda", "cantidad": 4},
        {"musculo": "triceps", "cantidad": 2}
    ],
    "Pecho, Hombro y Bíceps (2 pecho + 2 hombro + 2 bíceps)": [
        {"musculo": "pecho", "cantidad": 2},
        {"musculo": "hombro", "cantidad": 2},
        {"musculo": "biceps", "cantidad": 2}
    ]
}

# Interfaz principal
st.title("🏋️‍♂️ Rutina de Entrenamiento")
st.caption(f"Fecha: {date.today().strftime('%d/%m/%Y')}")

dia_seleccionado = st.selectbox(
    "Selecciona el día de hoy:",
    options=list(CONFIG_RUTINAS.keys())
)

if st.button("🔥 Generar Rutina del Día", type="primary", use_container_width=True):
    st.divider()
    plan = CONFIG_RUTINAS[dia_seleccionado]

    for bloque in plan:
        nombre_musculo = bloque["musculo"]
        cantidad = bloque["cantidad"]

        ejercicios_musculo = []
        for item in datos:
            if item["musculo"] == nombre_musculo:
                ejercicios_musculo = item["ejercicios"]
                break

        rutina_musculo = seleccionar_ejercicios_variados(ejercicios_musculo, cantidad)

        st.subheader(f"{nombre_musculo.upper()} ({len(rutina_musculo)} ejercicios)")
        ultimo_tipo = ""
        for ej in rutina_musculo:
            if ultimo_tipo != ej["tipo"]:
                st.markdown(f"**— {ej['tipo'].upper()} —**")
                ultimo_tipo = ej["tipo"]
            st.info(f"💪 {ej['nombre'].capitalize()}")

# --- BUZÓN DE SUGERENCIAS VÍA TELEGRAM ---
st.divider()
with st.expander("💬 ¿Tienes sugerencias o mejoras? Déjalas aquí"):
    with st.form("form_sugerencias", clear_on_submit=True):
        nombre = st.text_input("Tu nombre:")
        mensaje = st.text_area("¿Qué añadirías o cambiarías?")
        enviado = st.form_submit_button("Enviar sugerencia", use_container_width=True)

        if enviado:
            if mensaje.strip() != "":
                autor = nombre.strip() if nombre.strip() != "" else "Anónimo"
                texto_telegram = f"🔔 *Nueva sugerencia de la Gym App*\n\n👤 *De:* {autor}\n💬 *Mensaje:* {mensaje}"

                try:
                    token = st.secrets["TELEGRAM_TOKEN"]
                    chat_id = st.secrets["TELEGRAM_CHAT_ID"]
                    url = f"https://api.telegram.org/bot{token}/sendMessage"
                    payload = {
                        "chat_id": chat_id,
                        "text": texto_telegram,
                        "parse_mode": "Markdown"
                    }
                    response = requests.post(url, json=payload, timeout=5)

                    if response.status_code == 200:
                        st.success("¡Mensaje enviado directamente a mi móvil! Gracias por la ayuda 💪")
                    else:
                        st.error("Hubo un error al enviar el mensaje a Telegram.")
                except Exception:
                    st.error("No se pudo conectar con el servicio de avisos.")
            else:
                st.warning("Escribe un mensaje antes de enviar.")
