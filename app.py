import json
import os
import random
from datetime import date
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Gym Routine", page_icon="🏋️‍♂️", layout="centered")

DATA_FILE = "datos_usuarios.json"
EXERCISES_FILE = "exercises.json"

# Rutinas estándar de inicio para perfiles nuevos
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
    """Selecciona ejercicios garantizando variedad por categoría."""
    por_tipo = {}
    for ej in ejercicios:
        t = ej["tipo"]
        if t not in por_tipo:
            por_tipo[t] = []
        por_tipo[t].append(ej)

    tipos_disponibles = list(por_tipo.keys())
    random.shuffle(tipos_disponibles)

    elegidos = []

    # 1. Un ejercicio por cada tipo distinto
    for tipo in tipos_disponibles:
        if len(elegidos) < cantidad and por_tipo[tipo]:
            ej_al_azar = random.choice(por_tipo[tipo])
            elegidos.append(ej_al_azar)
            por_tipo[tipo].remove(ej_al_azar)

    # 2. Completar con los restantes sin repetir
    if len(elegidos) < cantidad:
        sobrantes = [ej for lista in por_tipo.values() for ej in lista]
        faltan = cantidad - len(elegidos)
        if sobrantes:
            elegidos.extend(random.sample(sobrantes, min(faltan, len(sobrantes))))

    elegidos.sort(key=lambda x: x["tipo"])
    return elegidos

# Carga de catálogo de ejercicios y base de perfiles
ejercicios_base = cargar_ejercicios()
db_usuarios = cargar_datos_usuarios()

# Garantizar al menos un usuario por defecto
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

# Inicialización del estado en la sesión
if "rutina_activa" not in st.session_state:
    st.session_state["rutina_activa"] = None
if "completados" not in st.session_state:
    st.session_state["completados"] = {}

# --- TEMPORIZADOR DE DESCANSO ---
with st.expander("⏱️ Temporizador de Descanso", expanded=False):
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

# --- CONFIGURACIÓN DE LA SESIÓN DE ENTRENAMIENTO ---
modo = st.radio(
    "Modalidad:",
    ["📋 Rutinas guardadas", "🎯 Personalizar músculos"],
    horizontal=True
)

plan_a_generar = []

if modo == "📋 Rutinas guardadas":
    rutinas_usuario = datos_perfil.get("rutinas", {})
    if not rutinas_usuario:
        st.info("No tienes rutinas registradas. Crea una en 'Personalizar músculos'.")
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

        # Guardar como rutina predeterminada del usuario
        with st.expander("💾 Guardar esta combinación en mis rutinas"):
            nombre_nueva_rutina = st.text_input("Nombre de la rutina (ej. Pierna y Hombro):")
            if st.button("Guardar en mi perfil", use_container_width=True):
                nombre_guardar = nombre_nueva_rutina.strip()
                if nombre_guardar:
                    datos_perfil["rutinas"][nombre_guardar] = plan_a_generar
                    db_usuarios[usuario_activo] = datos_perfil
                    guardar_datos_usuarios(db_usuarios)
                    st.success(f"Rutina '{nombre_guardar}' añadida a tus rutinas guardadas.")
                else:
                    st.warning("Introduce un nombre para la rutina.")

# Botones de acción
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

        # Subheading limpio sin recuentos
        st.subheader(nombre_m.upper())

        for ej in ejercicios:
            nombre_ej = ej["nombre"]
            tipo_ej = ej["tipo"]
            key_ej = f"{usuario_activo}_{nombre_m}_{nombre_ej}"

            esta_completado = st.session_state["completados"].get(key_ej, False)

            if ocultar_terminados and esta_completado:
                continue

            with st.container():
                c_check, c_info, c_peso = st.columns([1, 4, 2])

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
                        st.caption(f"✅ Completado ({tipo_ej})")
                    else:
                        st.markdown(f"**{nombre_ej.capitalize()}**")
                        st.caption(f"Tipo: {tipo_ej}")

                with c_peso:
                    # Peso vinculado únicamente al usuario activo
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
