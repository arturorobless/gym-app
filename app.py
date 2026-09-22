import json
import random
from datetime import date
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Gym Routine", page_icon="🏋️‍♂️", layout="centered")

def cargar_ejercicios():
    with open("exercises.json", "r") as f:
        return json.load(f)

def seleccionar_ejercicios_variados(ejercicios, cantidad):
    """Selecciona ejercicios priorizando tipos distintos."""
    por_tipo = {}
    for ej in ejercicios:
        t = ej["tipo"]
        if t not in por_tipo:
            por_tipo[t] = []
        por_tipo[t].append(ej)

    tipos_disponibles = list(por_tipo.keys())
    random.shuffle(tipos_disponibles)

    elegidos = []

    # 1. Uno de cada tipo
    for tipo in tipos_disponibles:
        if len(elegidos) < cantidad and por_tipo[tipo]:
            ej_al_azar = random.choice(por_tipo[tipo])
            elegidos.append(ej_al_azar)
            por_tipo[tipo].remove(ej_al_azar)

    # 2. Rellenar si faltan
    if len(elegidos) < cantidad:
        sobrantes = [ej for lista in por_tipo.values() for ej in lista]
        faltan = cantidad - len(elegidos)
        if sobrantes:
            elegidos.extend(random.sample(sobrantes, min(faltan, len(sobrantes))))

    elegidos.sort(key=lambda x: x["tipo"])
    return elegidos

# Carga de datos
datos = cargar_ejercicios()

# Configuración de rutinas
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

# --- TÍTULO ---
st.title("🏋️‍♂️ Rutina de Entrenamiento")
st.caption(f"Fecha: {date.today().strftime('%d/%m/%Y')}")

# --- TEMPORIZADOR DE DESCANSO (HTML/JS ultraligero) ---
with st.expander("⏱️ Temporizador de Descanso", expanded=True):
    temporizador_html = """
    <div style="text-align: center; font-family: -apple-system, BlinkMacSystemFont, sans-serif; background-color: #1a1c24; padding: 15px; border-radius: 12px; color: white;">
        <div id="display" style="font-size: 42px; font-weight: bold; margin-bottom: 10px; font-variant-numeric: tabular-nums;">01:30</div>
        
        <div style="display: flex; gap: 8px; justify-content: center; margin-bottom: 12px; flex-wrap: wrap;">
            <button onclick="fijar(60)" style="padding: 6px 12px; border-radius: 8px; border: 1px solid #444; background: #2b2e3b; color: #eee; font-weight: 600; cursor: pointer;">60s</button>
            <button onclick="fijar(90)" style="padding: 6px 12px; border-radius: 8px; border: 1px solid #444; background: #2b2e3b; color: #eee; font-weight: 600; cursor: pointer;">90s</button>
            <button onclick="fijar(120)" style="padding: 6px 12px; border-radius: 8px; border: 1px solid #444; background: #2b2e3b; color: #eee; font-weight: 600; cursor: pointer;">120s</button>
            <button onclick="sumar(30)" style="padding: 6px 12px; border-radius: 8px; border: 1px solid #444; background: #2b2e3b; color: #eee; font-weight: 600; cursor: pointer;">+30s</button>
        </div>

        <div style="display: flex; gap: 10px; justify-content: center;">
            <button id="btnStart" onclick="toggleTimer()" style="padding: 10px 24px; border-radius: 8px; border: none; background: #ff4b4b; color: white; font-weight: bold; font-size: 16px; cursor: pointer;">Iniciar</button>
            <button onclick="reiniciar()" style="padding: 10px 18px; border-radius: 8px; border: 1px solid #555; background: transparent; color: #ccc; font-weight: bold; cursor: pointer;">Reiniciar</button>
        </div>
    </div>

    <script>
        let tiempoRestante = 90;
        let tiempoInicial = 90;
        let intervalo = null;

        function reproducirBeep() {
            try {
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = "sine";
                osc.frequency.setValueAtTime(800, ctx.currentTime);
                gain.gain.setValueAtTime(0.3, ctx.currentTime);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start();
                osc.stop(ctx.currentTime + 0.4);
            } catch(e) {}
            if (navigator.vibrate) {
                navigator.vibrate([200, 100, 200]);
            }
        }

        function actualizarDisplay() {
            let m = Math.floor(tiempoRestante / 60);
            let s = tiempoRestante % 60;
            document.getElementById("display").innerText = 
                (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s);
        }

        function toggleTimer() {
            let btn = document.getElementById("btnStart");
            if (intervalo) {
                clearInterval(intervalo);
                intervalo = null;
                btn.innerText = "Reanudar";
                btn.style.background = "#ff4b4b";
            } else {
                if (tiempoRestante <= 0) tiempoRestante = tiempoInicial;
                btn.innerText = "Pausar";
                btn.style.background = "#e08b00";
                intervalo = setInterval(() => {
                    tiempoRestante--;
                    actualizarDisplay();
                    if (tiempoRestante <= 0) {
                        clearInterval(intervalo);
                        intervalo = null;
                        btn.innerText = "¡Listo!";
                        btn.style.background = "#28a745";
                        reproducirBeep();
                    }
                }, 1000);
            }
        }

        function fijar(seg) {
            tiempoInicial = seg;
            tiempoRestante = seg;
            if (intervalo) { clearInterval(intervalo); intervalo = null; }
            document.getElementById("btnStart").innerText = "Iniciar";
            document.getElementById("btnStart").style.background = "#ff4b4b";
            actualizarDisplay();
        }

        function sumar(seg) {
            tiempoRestante += seg;
            actualizarDisplay();
        }

        function reiniciar() {
            fijar(tiempoInicial);
        }

        actualizarDisplay();
    </script>
    """
    components.html(temporizador_html, height=170)

st.divider()

# --- SELECCIÓN Y GENERACIÓN DE RUTINA ---
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
