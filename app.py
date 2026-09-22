import json
import random
from datetime import date
import streamlit as st

# Configuración visual de la pestaña
st.set_page_config(page_title="Gym Routine", page_icon="🏋️‍♂️", layout="centered")

def cargar_ejercicios():
    with open("exercises.json", "r") as f:
        return json.load(f)

# 1. Cargamos la base de datos
datos = cargar_ejercicios()

# 2. Interfaz principal
st.title("🏋️‍♂️ Rutina de Entrenamiento")
st.caption(f"Fecha: {date.today().strftime('%d/%m/%Y')}")

# Extraemos la lista de músculos disponibles directamente del JSON
lista_musculos = [item["musculo"] for item in datos]

# Selector desplegable
musculo_seleccionado = st.selectbox(
    "¿En qué quieres hacerte polvo hoy?",
    options=lista_musculos,
    format_func=lambda x: x.capitalize()
)

# Obtenemos los ejercicios asociados al músculo elegido
ejercicios_disponibles = []
for item in datos:
    if item["musculo"] == musculo_seleccionado:
        ejercicios_disponibles = item["ejercicios"]

# Selector de número de ejercicios limitado al máximo que exista en el JSON
max_disponibles = len(ejercicios_disponibles)
numero_ejercicios = st.slider(
    "¿Cuántos ejercicios?",
    min_value=1,
    max_value=max_disponibles,
    value=min(3, max_disponibles)
)

# Botón interactivo para generar la rutina
if st.button("🔥 Generar Rutina", type="primary", use_container_width=True):
    # Selección aleatoria
    ejercicios_elegidos = random.sample(ejercicios_disponibles, numero_ejercicios)
    ejercicios_elegidos.sort(key=lambda x: x["tipo"])

    st.divider()
    st.subheader(f"Rutina de {musculo_seleccionado.upper()}")

    # Renderizado en tarjetas limpias
    ultimo_tipo = ""
    for ej in ejercicios_elegidos:
        if ultimo_tipo != ej["tipo"]:
            st.markdown(f"**— {ej['tipo'].upper()} —**")
            ultimo_tipo = ej["tipo"]
        st.info(f"💪 {ej['nombre'].capitalize()}")
