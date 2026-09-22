import json
import random
from datetime import date
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

    # 2. Si aún faltan ejercicios, rellenar con los restantes sin repetir
    if len(elegidos) < cantidad:
        sobrantes = [ej for lista in por_tipo.values() for ej in lista]
        faltan = cantidad - len(elegidos)
        if sobrantes:
            elegidos.extend(random.sample(sobrantes, min(faltan, len(sobrantes))))

    elegidos.sort(key=lambda x: x["tipo"])
    return elegidos

# Carga de base de datos
datos = cargar_ejercicios()

# Configuración correcta de los 3 días de entrenamiento
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

# Interfaz Streamlit
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

        # Buscar ejercicios del músculo correspondiente
        ejercicios_musculo = []
        for item in datos:
            if item["musculo"] == nombre_musculo:
                ejercicios_musculo = item["ejercicios"]
                break

        # Selección garantizando variedad de tipos
        rutina_musculo = seleccionar_ejercicios_variados(ejercicios_musculo, cantidad)

        st.subheader(f"{nombre_musculo.upper()} ({len(rutina_musculo)} ejercicios)")
        ultimo_tipo = ""
        for ej in rutina_musculo:
            if ultimo_tipo != ej["tipo"]:
                st.markdown(f"**— {ej['tipo'].upper()} —**")
                ultimo_tipo = ej["tipo"]
            st.info(f"💪 {ej['nombre'].capitalize()}")
