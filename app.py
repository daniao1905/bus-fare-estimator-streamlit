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
st.markdown("Completa el formulario para calcular la tarifa según el recorrido.")

with st.form("bus_form"):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Fecha del servicio", datetime.today())
        start_time = st.time_input("Hora de inicio")
    with col2:
        end_time = st.time_input("Hora de finalización")
        bus_type = st.selectbox("Tipo de Autobús", list(FARES.keys()))

    st.markdown("### Ingreso de direcciones (autocompletado)")
    origin = st.text_input("Dirección de origen (Ej. Haneda Airport)")
    destination = st.text_input("Dirección de destino final")
    waypoints = st.text_area("Puntos intermedios (uno por línea)", placeholder="Opcional")

    submitted = st.form_submit_button("Calcular tarifa")

def get_place_suggestions(input_text):
    endpoint = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    api_key = st.secrets["GOOGLE_MAPS_API_KEY"]
    params = {
        "input": input_text,
        "language": "es",
        "components": "country:jp",
        "key": api_key
    }
    response = requests.get(endpoint, params=params)
    return [p["description"] for p in response.json().get("predictions", [])]

if submitted:
    if not origin or not destination:
        st.error("Debes ingresar origen y destino.")
    else:
        st.info("Consultando distancia con Google Maps...")

        endpoint = "https://maps.googleapis.com/maps/api/directions/json"
        api_key = st.secrets["GOOGLE_MAPS_API_KEY"]
        params = {
            "origin": origin,
            "destination": destination,
            "key": api_key,
            "language": "es",
            "region": "jp"
        }

        if waypoints.strip():
            waypoints_list = waypoints.strip().split("\n")
            params["waypoints"] = "|".join(waypoints_list)

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
