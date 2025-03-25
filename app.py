import streamlit as st
import requests
from datetime import datetime

FARES = {
    "Alphard (4 asientos)": 974,
    "Hiace (9 asientos)": 1087,
    "Charter Bus (45 asientos)": 2790
}

st.set_page_config(page_title="Tarifa de Autobús con Google Maps", layout="centered")
st.title("🚌 Estimador de Tarifas de Autobús (Japón)")
st.markdown("Completa el formulario seleccionando direcciones válidas de la lista.")

def get_place_id(input_text):
    endpoint = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    api_key = st.secrets["GOOGLE_MAPS_API_KEY"]
    params = {
        "input": input_text,
        "language": "es",
        "components": "country:jp",
        "key": api_key
    }
    response = requests.get(endpoint, params=params)
    predictions = response.json().get("predictions", [])
    return [(p["description"], p["place_id"]) for p in predictions]

with st.form("bus_form"):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Fecha del servicio", datetime.today())
        start_time = st.time_input("Hora de inicio")
    with col2:
        end_time = st.time_input("Hora de finalización")
        bus_type = st.selectbox("Tipo de Autobús", list(FARES.keys()))

    st.markdown("### Dirección de origen")
    origin_input = st.text_input("Empieza a escribir... (Ej. Tokyo Station)")
    origin_choices = get_place_id(origin_input) if origin_input else []
    origin_place_id = st.selectbox("Selecciona origen", origin_choices, format_func=lambda x: x[0]) if origin_choices else None

    st.markdown("### Dirección de destino")
    destination_input = st.text_input("Empieza a escribir destino...")
    dest_choices = get_place_id(destination_input) if destination_input else []
    dest_place_id = st.selectbox("Selecciona destino", dest_choices, format_func=lambda x: x[0]) if dest_choices else None

    submitted = st.form_submit_button("Calcular tarifa")

if submitted:
    if not origin_place_id or not dest_place_id:
        st.error("Debes seleccionar origen y destino válidos desde la lista.")
    else:
        st.info("Consultando distancia con Google Maps...")

        endpoint = "https://maps.googleapis.com/maps/api/directions/json"
        api_key = st.secrets["GOOGLE_MAPS_API_KEY"]
        params = {
            "origin": f"place_id:{origin_place_id[1]}",
            "destination": f"place_id:{dest_place_id[1]}",
            "key": api_key,
            "language": "es",
            "region": "jp"
        }

        response = requests.get(endpoint, params=params)
        data = response.json()

        if data["status"] != "OK":
            st.error("Error al consultar la distancia: " + data.get("error_message", data["status"]))
        else:
            total_distance_m = sum(leg["distance"]["value"] for leg in data["routes"][0]["legs"])
            total_distance_km = total_distance_m / 1000
            rate = FARES[bus_type]
            total_price = total_distance_km * rate

            st.success("Ruta encontrada correctamente")
            st.metric("Distancia total", f"{total_distance_km:.2f} km")
            st.metric("Tarifa total", f"¥{total_price:,.0f} JPY")
