import json
import os
import random
import urllib.parse
from datetime import date
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Gym Routine", page_icon="🏋️‍♂️", layout="centered")

DATA_FILE = "datos_usuarios.json"
EXERCISES_FILE = "exercises.json"

# --- DICCIONARIO DE ILUSTRACIONES Y TÉCNICA DE CADA EJERCICIO ---
IMAGENES_EJERCICIOS = {
    # Pecho
    "press inclinado con mancuernas": "https://musclewiki.com/exercises/male/chest/incline-dumbbell-bench-press",
    "press inclinado en máquina": "https://musclewiki.com/exercises/male/chest/machine-incline-press",
    "press banca plano con barra": "https://musclewiki.com/exercises/male/chest/barbell-bench-press",
    "aperturas en polea media": "https://musclewiki.com/exercises/male/chest/cable-crossover",

    # Espalda
    "jalón al pecho agarre prono": "https://musclewiki.com/exercises/male/lats/lat-pulldown",
    "dominadas": "https://musclewiki.com/exercises/male/lats/pull-ups",
    "pullover en polea alta": "https://musclewiki.com/exercises/male/lats/cable-straight-arm-pulldown",
    "remo con barra": "https://musclewiki.com/exercises/male/traps-middle/barbell-bent-over-row",
    "remo gironda en polea baja": "https://musclewiki.com/exercises/male/traps-middle/cable-seated-row",
    "remo con mancuerna a una mano": "https://musclewiki.com/exercises/male/traps-middle/dumbbell-single-arm-row",
    "peso muerto convencional": "https://musclewiki.com/exercises/male/glutes/barbell-deadlift",
    "hiperextensiones": "https://musclewiki.com/exercises/male/lower-back/hyperextensions",

    # Hombro
    "press militar": "https://musclewiki.com/exercises/male/shoulders/barbell-overhead-press",
    "elevaciones frontales con polea": "https://musclewiki.com/exercises/male/shoulders/cable-front-raise",
    "elevaciones laterales con mancuernas": "https://musclewiki.com/exercises/male/shoulders/dumbbell-lateral-raise",
    "elevaciones laterales en polea": "https://musclewiki.com/exercises/male/shoulders/cable-lateral-raise",
    "laterales en banco inclinado": "https://musclewiki.com/exercises/male/shoulders/incline-dumbbell-lateral-raise",

    # Bíceps
    "curl en banco inclinado": "https://musclewiki.com/exercises/male/biceps/incline-dumbbell-curl",
    "curl arrastre con barra": "https://musclewiki.com/exercises/male/biceps/barbell-drag-curl",
    "curl predicador / scott": "https://musclewiki.com/exercises/male/biceps/barbell-preacher-curl",
    "curl araña": "https://musclewiki.com/exercises/male/biceps/dumbbell-spider-curl",
    "curl martillo con mancuernas": "https://musclewiki.com/exercises/male/biceps/dumbbell-hammer-curl",
    "curl martillo en polea con cuerda": "https://musclewiki.com/exercises/male/biceps/cable-rope-hammer-curl",

    # Tríceps
    "press francés con barra Z": "https://musclewiki.com/exercises/male/triceps/barbell-lying-triceps-extension",
    "extensión trasnuca en polea": "https://musclewiki.com/exercises/male/triceps/cable-overhead-triceps-extension",
    "extensión en polea con barra recta": "https://musclewiki.com/exercises/male/triceps/cable-straight-bar-pushdown",
    "extensión en polea con cuerda": "https://musclewiki.com/exercises/male/triceps/cable-rope-pushdown",
    "extensión invertida con agarre supino": "https://musclewiki.com/exercises/male/triceps/cable-reverse-grip-pushdown",
    "fondos entre bancos o paralelas": "https://musclewiki.com/exercises/male/triceps/parallel-bar-dips",

    # Pierna
    "sentadilla con barra trasera": "https://musclewiki.com/exercises/male/quads/barbell-squat",
    "prensa inclinada": "https://musclewiki.com/exercises/male/quads/sled-45-leg-press",
    "extensiones de cuádriceps en máquina": "https://musclewiki.com/exercises/male/quads/lever-leg-extension",
    "curl femoral tumbado": "https://musclewiki.com/exercises/male/hamstrings/lever-lying-leg-curl",
    "curl femoral sentado": "https://musclewiki.com/exercises/male/hamstrings/lever-seated-leg-curl",
    "peso muerto rumano": "https://musclewiki.com/exercises/male/hamstrings/barbell-romanian-deadlift",
    "hip thrust con barra": "https://musclewiki.com/exercises/male/glutes/barbell-hip-thrust",
    "elevación de talones de pie": "https://musclewiki.com/exercises/male/calves/standing-calf-raise",
    "elevación de talones sentado": "https://musclewiki.com/exercises/male/calves/seated-calf-raise"
}

def obtener_enlace_imagen(nombre_ejercicio):
    clave = nombre_ejercicio.strip().lower()
    if clave in IMAGENES_EJERCICIOS:
        return IMAGENES_EJERCICIOS[clave]
    # Enlace de búsqueda en caso de añadir ejercicios futuros
    return f"https://musclewiki.com/search?q={urllib.parse.quote(nombre_ejercicio)}"

# Rutinas estándar de inicio
RUTINAS_DEFECTO = {
    "Pierna": [
        {"musculo": "pierna", "cantidad": 5}
    ],
    "Espalda y Tríceps": [
        {"musculo": "espalda", "cantidad": 4},
        {"musculo": "triceps", "cantidad": 2}
    ],
    "Pecho, Hombro y Bíceps": [
        {"musculo": "pecho", "cantidad": 2},
        {"musculo": "hombro", "cantidad": 2},
        {"musculo": "biceps", "cantidad": 2}
    ]
}

def cargar_ejercicios():
    with open(EXERCISES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def cargar_datos_usuarios():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def guardar_datos_usuarios(datos):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def seleccionar_ejercicios_variados(ejercicios, cantidad):
    por_tipo = {}
    for ej in ejercicios:
        t = ej["tipo"]
        if t not in por_tipo:
            por_tipo[t] = []
        por_tipo[t].append(ej)

    tipos_disponibles = list(por_tipo.keys())
    random.shuffle(tipos_disponibles)

    elegidos = []
    for tipo in tipos_disponibles:
        if len(elegidos) < cantidad and por_tipo[tipo]:
            ej_al_azar = random.choice(por_tipo[tipo])
            elegidos.append(ej_al_azar)
            por_tipo[tipo].remove(ej_al_azar)

    if len(elegidos) < cantidad:
        sobrantes = [ej for lista in por_tipo.values() for ej in lista]
        faltan = cantidad - len(elegidos)
        if sobrantes:
            elegidos.extend(random.sample(sobrantes, min(faltan, len(sobrantes))))

    elegidos.sort(key=lambda x: x["tipo"])
    return elegidos

# Carga de datos
ejercicios_base = cargar_ejercicios()
db_usuarios = cargar_datos_usuarios()

if not db_usuarios:
    db_usuarios["Arturo"] = {
        "rutinas": RUTINAS_DEFECTO.copy(),
        "pesos": {}
    }
    guardar_datos_usuarios(db_usuarios)

# --- CABECERA Y SELECCIÓN DE USUARIO ---
st.title("🏋️‍♂️ Rutina de Entrenamiento")
st.caption(f"Fecha: {date.today().strftime('%d/%m/%Y')}")

nombres_usuarios = list(db_usuarios.keys())
col_user, col_add_user = st.columns([3, 1])

with col_user:
    usuario_activo = st.selectbox(
        "Perfil activo:",
        options=nombres_usuarios,
        key="selector_usuario"
    )

with col_add_user:
    with st.popover("➕ Nuevo"):
        nuevo_nombre = st.text_input("Nombre de usuario:")
        if st.button("Crear perfil", use_container_width=True):
            nombre_limpio = nuevo_nombre.strip()
            if nombre_limpio and nombre_limpio not in db_usuarios:
                db_usuarios[nombre_limpio] = {
                    "rutinas": RUTINAS_DEFECTO.copy(),
                    "pesos": {}
                }
                guardar_datos_usuarios(db_usuarios)
                st.session_state["selector_usuario"] = nombre_limpio
                st.rerun()

datos_perfil = db_usuarios[usuario_activo]

if "rutina_activa" not in st.session_state:
    st.session_state["rutina_activa"] = None
if "completados" not in st.session_state:
    st.session_state["completados"] = {}

# --- PANEL DE CRONÓMETROS: TIEMPO EN EL GYM + DESCANSO ---
with st.expander("⏱️ Cronómetros (Sesión y Descanso)", expanded=True):
    temporizador_html = """
    <div style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; background-color: #161822; padding: 14px; border-radius: 12px; color: white;">
        <div style="display: flex; gap: 10px; justify-content: space-between; flex-wrap: wrap;">
            
            <!-- PANEL 1: TIEMPO EN EL GYM -->
            <div style="flex: 1; min-width: 140px; background: #222634; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #32384a;">
                <div style="font-size: 11px; text-transform: uppercase; font-weight: bold; color: #7fe3aa; letter-spacing: 0.5px;">🏋️ Tiempo Gym</div>
                <div id="sessionDisplay" style="font-size: 26px; font-weight: bold; margin: 6px 0; font-variant-numeric: tabular-nums; color: #2ecc71;">00:00:00</div>
                <div style="display: flex; gap: 6px; justify-content: center;">
                    <button id="btnSession" onclick="toggleSession()" style="padding: 6px 12px; border-radius: 6px; border: none; background: #2ecc71; color: white; font-weight: bold; font-size: 13px; cursor: pointer;">Iniciar</button>
                    <button onclick="resetSession()" style="padding: 6px 10px; border-radius: 6px; border: 1px solid #555; background: transparent; color: #ccc; font-weight: bold; font-size: 13px; cursor: pointer;">Reset</button>
                </div>
            </div>

            <!-- PANEL 2: DESCANSO ENTRE SERIES -->
            <div style="flex: 1; min-width: 155px; background: #222634; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #32384a;">
                <div style="font-size: 11px; text-transform: uppercase; font-weight: bold; color: #ff8585; letter-spacing: 0.5px;">⏳ Descanso</div>
                <div id="restDisplay" style="font-size: 26px; font-weight: bold; margin: 6px 0; font-variant-numeric: tabular-nums; color: #ff4b4b;">01:30</div>
                <div style="display: flex; gap: 4px; justify-content: center; margin-bottom: 6px; flex-wrap: wrap;">
                    <button onclick="fijar(60)" style="padding: 3px 6px; border-radius: 4px; border: 1px solid #444; background: #2b3042; color: #eee; font-size: 11px; cursor: pointer;">60s</button>
                    <button onclick="fijar(90)" style="padding: 3px 6px; border-radius: 4px; border: 1px solid #444; background: #2b3042; color: #eee; font-size: 11px; cursor: pointer;">90s</button>
                    <button onclick="fijar(120)" style="padding: 3px 6px; border-radius: 4px; border: 1px solid #444; background: #2b3042; color: #eee; font-size: 11px; cursor: pointer;">120s</button>
                    <button onclick="sumar(30)" style="padding: 3px 6px; border-radius: 4px; border: 1px solid #444; background: #2b3042; color: #eee; font-size: 11px; cursor: pointer;">+30s</button>
                </div>
                <div style="display: flex; gap: 6px; justify-content: center;">
                    <button id="btnRest" onclick="toggleRest()" style="padding: 6px 12px; border-radius: 6px; border: none; background: #ff4b4b; color: white; font-weight: bold; font-size: 13px; cursor: pointer;">Iniciar</button>
                    <button onclick="reiniciarRest()" style="padding: 6px 10px; border-radius: 6px; border: 1px solid #555; background: transparent; color: #ccc; font-weight: bold; font-size: 13px; cursor: pointer;">Reset</button>
                </div>
            </div>

        </div>
    </div>

    <script>
        // --- LÓGICA CRONÓMETRO DE SESIÓN CON PERSISTENCIA ---
        let sessionRunning = localStorage.getItem("gym_session_running") === "true";
        let sessionStartTime = localStorage.getItem("gym_session_start") ? parseInt(localStorage.getItem("gym_session_start")) : null;
        let sessionAccumulated = localStorage.getItem("gym_session_accumulated") ? parseInt(localStorage.getItem("gym_session_accumulated")) : 0;

        function formatSession(totalSec) {
            let h = Math.floor(totalSec / 3600);
            let m = Math.floor((totalSec % 3600) / 60);
            let s = totalSec % 60;
            return (h < 10 ? "0" + h : h) + ":" + (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s);
        }

        function updateSessionUI() {
            let currentSec = sessionAccumulated;
            if (sessionRunning && sessionStartTime) {
                currentSec += Math.floor((Date.now() - sessionStartTime) / 1000);
            }
            document.getElementById("sessionDisplay").innerText = formatSession(currentSec);
        }

        function toggleSession() {
            let btn = document.getElementById("btnSession");
            if (sessionRunning) {
                sessionAccumulated += Math.floor((Date.now() - sessionStartTime) / 1000);
                sessionRunning = false;
                sessionStartTime = null;
                localStorage.setItem("gym_session_accumulated", sessionAccumulated);
                localStorage.setItem("gym_session_running", "false");
                localStorage.removeItem("gym_session_start");
                btn.innerText = "Reanudar";
                btn.style.background = "#2ecc71";
            } else {
                sessionRunning = true;
                sessionStartTime = Date.now();
                localStorage.setItem("gym_session_start", sessionStartTime);
                localStorage.setItem("gym_session_running", "true");
                btn.innerText = "Pausar";
                btn.style.background = "#e67e22";
            }
            updateSessionUI();
        }

        function resetSession() {
            sessionRunning = false;
            sessionStartTime = null;
            sessionAccumulated = 0;
            localStorage.removeItem("gym_session_start");
            localStorage.removeItem("gym_session_accumulated");
            localStorage.setItem("gym_session_running", "false");
            let btn = document.getElementById("btnSession");
            btn.innerText = "Iniciar";
            btn.style.background = "#2ecc71";
            updateSessionUI();
        }

        // Estado inicial del botón de sesión
        let btnSess = document.getElementById("btnSession");
        if (sessionRunning) {
            btnSess.innerText = "Pausar";
            btnSess.style.background = "#e67e22";
        } else if (sessionAccumulated > 0) {
            btnSess.innerText = "Reanudar";
            btnSess.style.background = "#2ecc71";
        }
        setInterval(updateSessionUI, 1000);
        updateSessionUI();

        // --- LÓGICA TEMPORIZADOR DE DESCANSO ---
        let restRestante = 90;
        let restInicial = 90;
        let restIntervalo = null;

        function sonarAviso() {
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

        function updateRestDisplay() {
            let m = Math.floor(restRestante / 60);
            let s = restRestante % 60;
            document.getElementById("restDisplay").innerText = 
                (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s);
        }

        function toggleRest() {
            let btn = document.getElementById("btnRest");
            if (restIntervalo) {
                clearInterval(restIntervalo);
                restIntervalo = null;
                btn.innerText = "Reanudar";
                btn.style.background = "#ff4b4b";
            } else {
                if (restRestante <= 0) restRestante = restInicial;
                btn.innerText = "Pausar";
                btn.style.background = "#e67e22";
                restIntervalo = setInterval(() => {
                    restRestante--;
                    updateRestDisplay();
                    if (restRestante <= 0) {
                        clearInterval(restIntervalo);
                        restIntervalo = null;
                        btn.innerText = "¡Listo!";
                        btn.style.background = "#28a745";
                        sonarAviso();
                    }
                }, 1000);
            }
        }

        function fijar(seg) {
            restInicial = seg;
            restRestante = seg;
            if (restIntervalo) { clearInterval(restIntervalo); restIntervalo = null; }
            let btn = document.getElementById("btnRest");
            btn.innerText = "Iniciar";
            btn.style.background = "#ff4b4b";
            updateRestDisplay();
        }

        function sumar(seg) {
            restRestante += seg;
            updateRestDisplay();
        }

        function reiniciarRest() {
            fijar(restInicial);
        }

        updateRestDisplay();
    </script>
    """
    components.html(temporizador_html, height=195)

st.divider()

# --- MODALIDAD DE ENTRENAMIENTO ---
modo = st.radio(
    "Modalidad:",
    ["📋 Rutinas guardadas", "🎯 Personalizar músculos"],
    horizontal=True
)

plan_a_generar = []

if modo == "📋 Rutinas guardadas":
    rutinas_usuario = datos_perfil.get("rutinas", {})
    if not rutinas_usuario:
        st.info("No tienes rutinas guardadas.")
    else:
        nombre_rutina_sel = st.selectbox(
            "Selecciona la rutina:",
            options=list(rutinas_usuario.keys())
        )
        plan_a_generar = rutinas_usuario[nombre_rutina_sel]
else:
    musculos_disponibles = [item["musculo"] for item in ejercicios_base]
    musculos_seleccionados = st.multiselect(
        "Músculos a entrenar:",
        options=musculos_disponibles,
        default=["pecho", "triceps"] if "pecho" in musculos_disponibles else [musculos_disponibles[0]],
        format_func=lambda x: x.capitalize()
    )

    if musculos_seleccionados:
        for m in musculos_seleccionados:
            max_ej = len(next(item["ejercicios"] for item in ejercicios_base if item["musculo"] == m))
            cant = st.slider(
                f"{m.capitalize()}:",
                min_value=1,
                max_value=max_ej,
                value=min(2, max_ej),
                key=f"slider_{m}"
            )
            plan_a_generar.append({"musculo": m, "cantidad": cant})

        with st.expander("💾 Guardar esta combinación en mis rutinas"):
            nombre_nueva_rutina = st.text_input("Nombre de la rutina:")
            if st.button("Guardar en mi perfil", use_container_width=True):
                nombre_guardar = nombre_nueva_rutina.strip()
                if nombre_guardar:
                    datos_perfil["rutinas"][nombre_guardar] = plan_a_generar
                    db_usuarios[usuario_activo] = datos_perfil
                    guardar_datos_usuarios(db_usuarios)
                    st.success(f"Rutina '{nombre_guardar}' guardada con éxito.")
                else:
                    st.warning("Escribe un nombre para la rutina.")

col_gen, col_limpiar = st.columns([3, 1])

with col_gen:
    if st.button("🔥 Generar Rutina", type="primary", use_container_width=True):
        if not plan_a_generar:
            st.warning("Selecciona al menos un músculo.")
        else:
            nueva_rutina = []
            for bloque in plan_a_generar:
                nombre_m = bloque["musculo"]
                cant_m = bloque["cantidad"]
                ejercicios_m = next((item["ejercicios"] for item in ejercicios_base if item["musculo"] == nombre_m), [])
                seleccionados = seleccionar_ejercicios_variados(ejercicios_m, cant_m)
                nueva_rutina.append({
                    "musculo": nombre_m,
                    "ejercicios": seleccionados
                })
            st.session_state["rutina_activa"] = nueva_rutina
            st.session_state["completados"] = {}

with col_limpiar:
    if st.button("🗑️ Limpiar", use_container_width=True):
        st.session_state["rutina_activa"] = None
        st.session_state["completados"] = {}
        st.rerun()

# --- MOSTRAR RUTINA ACTIVA ---
if st.session_state["rutina_activa"]:
    st.divider()
    ocultar_terminados = st.checkbox("Ocultar ejercicios completados", value=False)

    for bloque in st.session_state["rutina_activa"]:
        nombre_m = bloque["musculo"]
        ejercicios = bloque["ejercicios"]

        st.subheader(nombre_m.upper())

        for ej in ejercicios:
            nombre_ej = ej["nombre"]
            tipo_ej = ej["tipo"]
            key_ej = f"{usuario_activo}_{nombre_m}_{nombre_ej}"

            esta_completado = st.session_state["completados"].get(key_ej, False)

            if ocultar_terminados and esta_completado:
                continue

            with st.container():
                # 4 columnas: Checkbox | Info del ejercicio | Botón Imagen | Input Kilos
                c_check, c_info, c_foto, c_peso = st.columns([0.8, 3.8, 1.2, 2.2])

                with c_check:
                    hecho = st.checkbox(
                        "Listo",
                        value=esta_completado,
                        key=f"check_{key_ej}",
                        label_visibility="collapsed"
                    )
                    if hecho != esta_completado:
                        st.session_state["completados"][key_ej] = hecho
                        st.rerun()

                with c_info:
                    if hecho:
                        st.markdown(f"~~**{nombre_ej.capitalize()}**~~")
                        st.caption(f"✅ Hecho ({tipo_ej})")
                    else:
                        st.markdown(f"**{nombre_ej.capitalize()}**")
                        st.caption(f"Tipo: {tipo_ej}")

                with c_foto:
                    enlace_foto = obtener_enlace_imagen(nombre_ej)
                    st.link_button(
                        "🖼️",
                        enlace_foto,
                        help=f"Ver técnica e ilustración de {nombre_ej.capitalize()}",
                        use_container_width=True
                    )

                with c_peso:
                    pesos_usuario = datos_perfil.setdefault("pesos", {})
                    peso_guardado = float(pesos_usuario.get(nombre_ej, 0.0))

                    nuevo_peso = st.number_input(
                        "kg",
                        min_value=0.0,
                        max_value=500.0,
                        value=peso_guardado,
                        step=2.5,
                        key=f"peso_{key_ej}",
                        label_visibility="collapsed"
                    )
                    if nuevo_peso != peso_guardado:
                        pesos_usuario[nombre_ej] = nuevo_peso
                        db_usuarios[usuario_activo] = datos_perfil
                        guardar_datos_usuarios(db_usuarios)

            st.write("")

# --- BUZÓN DE SUGERENCIAS VÍA TELEGRAM ---
st.divider()
with st.expander("💬 ¿Tienes sugerencias o mejoras? Déjalas aquí"):
    with st.form("form_sugerencias", clear_on_submit=True):
        nombre = st.text_input("Tu nombre:", value=usuario_activo)
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
