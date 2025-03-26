import streamlit as st
import requests
from datetime import datetime
import streamlit.components.v1 as components
import math

# Tarifas mínimas ajustadas
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

st.set_page_config(page_title="Calculadora de Tarifas Escalonadas", layout="centered")
st.title("🚌 Estimador de Tarifas Escalonadas por KM (Japón)")

st.markdown("Selecciona los puntos y fechas. El cálculo se basa en bloques escalonados de km.")

# Inputs de ruta
origin = st.text_input("Origen (Ej. Haneda Airport)")
destination = st.text_input("Destino Final")
stops = st.text_area("Paradas adicionales (una por línea)", placeholder="Opcional")

# Mapa visual activo
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
with st.form("fare_form"):
    col1, col2 = st.columns(2)
    with col1:
        fechas = st.date_input("Selecciona una o más fechas", [])
        start_time = st.time_input("Hora de inicio")
    with col2:
        end_time = st.time_input("Hora de finalización")
        bus_type = st.selectbox("Tipo de Autobús", list(MIN_TARIFAS.keys()))
    submitted = st.form_submit_button("Calcular tarifa")

# Lógica de cálculo escalonado
if submitted:
    if not origin or not destination or not fechas:
        st.error("Debes ingresar origen, destino y al menos una fecha.")
    else:
        st.info("Calculando distancia y aplicando tarifas escalonadas...")

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

            # Cálculo escalonado
            if km_total < 30:
                total_tarifa = tarifa_min
                detalle = "Tarifa mínima aplicada (menos de 30km)"
            elif 30 <= km_total <= 85:
                extra_km = km_total - 30
                total_tarifa = tarifa_min + extra_km * tarifa_km
                detalle = f"Desde 30km a {km_total:.2f}km: ¥{tarifa_min:,} + ({extra_km:.2f}km × ¥{tarifa_km})"
            elif 85 < km_total <= 100:
                total_tarifa = tarifa_min + (85 - 30) * tarifa_km
                detalle = "Tarifa plana entre 85 y 100km"
            elif 100 < km_total <= 120:
                total_tarifa = tarifa_min + (85 - 30) * tarifa_km + 20000
                detalle = "Tarifa plana + ¥20,000 (100-120km)"
            else:
                bloques_extra = math.ceil((km_total - 120) / 20)
                extra_km_charge = bloques_extra * 20000
                total_tarifa = tarifa_min + (85 - 30) * tarifa_km + 20000 + extra_km_charge
                detalle = f"Tarifa base + ¥20,000 (100-120km) + ¥{extra_km_charge:,} por {bloques_extra} bloques de 20km extra"

            tarifa_final = total_tarifa * dias

            st.success("Cálculo completado")
            st.metric("Distancia Total", f"{km_total:.2f} km")
            st.metric("Días de Servicio", dias)
            st.metric("Tarifa Total", f"¥{tarifa_final:,.0f} JPY")

            st.markdown("### Detalle del Cálculo")
            st.write(f"Tipo de Vehículo: {bus_type}")
            st.write(detalle)
            st.write(f"Tarifa por día: ¥{total_tarifa:,.0f}")
            st.write(f"Total por {dias} día(s): ¥{tarifa_final:,.0f}")
