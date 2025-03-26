import streamlit as st
import requests
from datetime import datetime
import streamlit.components.v1 as components

FARES = {
    "Alphard (4 asientos)": 974,
    "Hiace (9 asientos)": 1087,
    "Charter Bus (45 asientos)": 2790
}

st.set_page_config(page_title="Tarifa de Autobús con Mapa", layout="centered")
st.title("🚌 Estimador de Tarifas de Autobús con Mapa (Japón)")
st.markdown("Selecciona los puntos y visualízalos instantáneamente en el mapa.")

# Entradas de origen/destino/paradas
st.markdown("### Puntos de ruta")
origin = st.text_input("Origen (Ej. Tokyo Station)")
destination = st.text_input("Destino Final")
stops = st.text_area("Paradas adicionales (una por línea)", placeholder="Opcional")

# Mostrar mapa siempre
api_key = st.secrets["GOOGLE_MAPS_API_KEY"]
if origin and destination:
    map_url = f"https://www.google.com/maps/embed/v1/directions?key={api_key}&origin={origin}&destination={destination}"
    if stops.strip():
        stop_list = stops.strip().split("\n")
        map_url += "&waypoints=" + "|".join(stop_list)
    map_url += "&language=es&region=jp"
else:
    map_url = f"https://www.google.com/maps/embed/v1/view?key={api_key}&center=35.6895,139.6917&zoom=10&language=es"

components.html(f"<iframe width='100%' height='400' style='border:0' src='{map_url}' allowfullscreen></iframe>", height=420)

# Datos del servicio
st.markdown("### Información del Servicio")
with st.form("fare_form"):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Fecha del servicio", datetime.today())
        start_time = st.time_input("Hora de inicio")
    with col2:
        end_time = st.time_input("Hora de finalización")
        bus_type = st.selectbox("Tipo de Autobús", list(FARES.keys()))
    submitted = st.form_submit_button("Calcular tarifa")

# Calcular distancia y tarifa
if submitted:
    if not origin or not destination:
        st.error("Debes ingresar al menos origen y destino.")
    else:
        endpoint = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "key": api_key,
            "language": "es",
            "region": "jp"
        }
        if stops.strip():
            stop_list = stops.strip().split("\n")
            params["waypoints"] = "|".join(stop_list)

        response = requests.get(endpoint, params=params)
        data = response.json()

        if data["status"] != "OK":
            st.error("Error al consultar la distancia: " + data.get("error_message", data["status"]))
        else:
            total_distance_m = sum(leg["distance"]["value"] for leg in data["routes"][0]["legs"])
            total_distance_km = total_distance_m / 1000
            rate = FARES[bus_type]
            total_price = total_distance_km * rate * 1.10  # +10% impuestos

            st.success("Ruta encontrada correctamente")
            st.metric("Distancia total", f"{total_distance_km:.2f} km")
            st.metric("Tarifa total (con impuestos)", f"¥{total_price:,.0f} JPY")
