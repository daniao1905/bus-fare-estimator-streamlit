import streamlit as st
import requests
from datetime import datetime
import streamlit.components.v1 as components

# Tarifas ajustadas
MIN_TARIFAS = {
    "Alphard (4 asientos)": 30790,
    "Hiace (9 asientos)": 31940,
    "Charter Bus (45 asientos)": 81400
}
TARIFAS_KM = {
    "Alphard (4 asientos)": 974,
    "Hiace (9 asientos)": 1087,
    "Charter Bus (45 asientos)": 2783
}

st.set_page_config(page_title="Tarifa de Autobús con Mapa", layout="centered")
st.title("🚌 Estimador de Tarifas de Autobús con Mapa y Lógica Real (Japón)")

st.markdown("Selecciona los puntos y fechas para calcular tu tarifa visualmente.")

# Entradas de ruta
st.markdown("### Puntos de ruta")
origin = st.text_input("Origen (Ej. Haneda Airport)")
destination = st.text_input("Destino Final")
stops = st.text_area("Paradas intermedias (una por línea)", placeholder="Opcional")

# Mostrar mapa desde el inicio
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
        fechas = st.date_input("Selecciona una o más fechas", [])
        start_time = st.time_input("Hora de inicio")
    with col2:
        end_time = st.time_input("Hora de finalización")
        bus_type = st.selectbox("Tipo de Autobús", list(MIN_TARIFAS.keys()))
    submitted = st.form_submit_button("Calcular tarifa")

if submitted:
    if not origin or not destination or not fechas:
        st.error("Debes ingresar origen, destino y al menos una fecha.")
    else:
        st.info("Consultando Google Maps para calcular la distancia...")

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
            st.error("Error en la consulta: " + data.get("error_message", data["status"]))
        else:
            km_total = sum(leg["distance"]["value"] for leg in data["routes"][0]["legs"]) / 1000
            tarifa_min = MIN_TARIFAS[bus_type]
            tarifa_km = TARIFAS_KM[bus_type]
            dias = len(fechas) if isinstance(fechas, list) else 1

            if km_total < 80:
                base = tarifa_min
                extra = 0
            elif 80 <= km_total <= 100:
                base = tarifa_min
                extra = 0
            else:
                extra = (km_total - 100) * tarifa_km
                base = tarifa_min + extra

            total = base * dias

            st.success("¡Cálculo completo!")
            st.metric("Distancia Total", f"{km_total:.2f} km")
            st.metric("Días de Servicio", dias)
            st.metric("Tarifa Total", f"¥{total:,.0f} JPY")

            st.markdown("### Detalle del Cálculo")
            st.write(f"Tarifa base mínima: ¥{tarifa_min:,}")
            if extra > 0:
                st.write(f"Adicional por distancia: ¥{extra:,.0f} ({km_total - 100:.2f} km x ¥{tarifa_km:,}/km)")
            else:
                st.write("No se aplicó tarifa extra por km (menor a 100km)")
            st.write(f"Total multiplicado por {dias} día(s): ¥{total:,.0f}")
