import streamlit as st
import requests
from datetime import datetime, time
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

st.set_page_config(page_title="Tarifa de Autobús Escalonada", layout="centered")
st.title("🚌 Estimador de Tarifas Escalonadas con Autocompletado (Japón)")

# Google API
api_key = st.secrets["GOOGLE_MAPS_API_KEY"]

# Función para autocompletar desde Google Places API
def get_place_suggestions(query):
    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {
        "input": query,
        "key": api_key,
        "language": "es",
        "components": "country:jp"
    }
    res = requests.get(url, params=params).json()
    return [p["description"] for p in res.get("predictions", [])]

# Entradas con sugerencias manuales simuladas
st.markdown("### Ingreso de puntos con sugerencia automática")
origin_query = st.text_input("Origen", "")
origin_suggestions = get_place_suggestions(origin_query) if origin_query else []
origin = st.selectbox("Selecciona origen sugerido", origin_suggestions) if origin_suggestions else origin_query

dest_query = st.text_input("Destino Final", "")
dest_suggestions = get_place_suggestions(dest_query) if dest_query else []
destination = st.selectbox("Selecciona destino sugerido", dest_suggestions) if dest_suggestions else dest_query

stops = st.text_area("Paradas adicionales (una por línea)", placeholder="Opcional")

# Configuración
st.markdown("### Información del Servicio")
with st.form("fare_form"):
    fechas = st.date_input("Selecciona una o más fechas", [])

    # Horas por intervalos de 30 min
    horas_opciones = [time(h, m).strftime("%H:%M") for h in range(24) for m in [0, 30]]
    start_time = st.selectbox("Hora de inicio", [""] + horas_opciones)
    end_time = st.selectbox("Hora de finalización", [""] + horas_opciones)
    bus_type = st.selectbox("Tipo de Autobús", list(MIN_TARIFAS.keys()))
    submitted = st.form_submit_button("Calcular tarifa")

# Calculo de tarifa
if submitted:
    if not origin or not destination or not fechas:
        st.error("Debes ingresar origen, destino y al menos una fecha.")
    else:
        st.info("Calculando tarifa y distancia...")

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
                detalle = "Tarifa base + ¥20,000 (100-120km)"
            else:
                bloques_extra = math.ceil((km_total - 120) / 20)
                extra_km_charge = bloques_extra * 20000
                total_tarifa = tarifa_min + (85 - 30) * tarifa_km + 20000 + extra_km_charge
                detalle = f"Tarifa base + ¥20,000 + ¥{extra_km_charge:,} por {bloques_extra} bloques de 20km extra"

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

            # Mapa al final
            map_url = f"https://www.google.com/maps/embed/v1/directions?key={api_key}&origin={origin}&destination={destination}"
            if stops.strip():
                map_url += "&waypoints=" + "|".join(stop_list)
            map_url += "&language=es&region=jp"

            st.markdown("### Mapa del recorrido")
            components.html(f"<iframe width='100%' height='400' style='border:0' src='{map_url}' allowfullscreen></iframe>", height=420)
