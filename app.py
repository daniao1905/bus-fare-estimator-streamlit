import streamlit as st
import requests
from datetime import datetime, time
import streamlit.components.v1 as components
import math

MIN_TARIFAS = {
    "Hiace (9 asientos)": 31940,
    "Alphard (4 asientos)": 30790,
    "Bus Mediano (30 asientos)": 62000,
    "Bus Grande (45 asientos)": 69500
}
TARIFAS_KM = {
    "Hiace (9 asientos)": 1087,
    "Alphard (4 asientos)": 974,
    "Bus Mediano (30 asientos)": 1950,
    "Bus Grande (45 asientos)": 2380
}

st.set_page_config(page_title="Tarifa de Autobús Escalonada", layout="centered")
st.title("🚌 Estimador de Tarifas Escalonadas (Japón)")

api_key = st.secrets["GOOGLE_MAPS_API_KEY"]

def get_suggestions(input_text):
    if not input_text:
        return []
    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {
        "input": input_text,
        "language": "es",
        "components": "country:jp",
        "key": api_key
    }
    res = requests.get(url, params=params).json()
    return [p["description"] for p in res.get("predictions", [])]

# Entradas con sugerencias
st.markdown("### Selección de Destinos con Autocompletado")

origin = st.text_input("Origen (Ej. Tokyo Station)")
if origin:
    suggestions = get_suggestions(origin)
    if suggestions:
        origin = st.selectbox("Sugerencias para origen:", suggestions, index=0)

destination = st.text_input("Destino Final (Ej. Hakone)")
if destination:
    suggestions_dest = get_suggestions(destination)
    if suggestions_dest:
        destination = st.selectbox("Sugerencias para destino:", suggestions_dest, index=0)

if origin and destination:
    map_url = f"https://www.google.com/maps/embed/v1/directions?key={api_key}&origin={origin}&destination={destination}&language=es&region=jp"
    st.markdown("### Vista previa del mapa")
    components.html(f"<iframe width='100%' height='400' style='border:0' src='{map_url}' allowfullscreen></iframe>", height=420)

stops = st.text_area("Paradas intermedias (una por línea)", placeholder="Opcional")

# Formulario
st.markdown("### Información del Servicio")
with st.form("fare_form"):
    fecha = st.date_input("Selecciona la fecha del servicio", datetime.today())
    horas_opciones = [time(h, m).strftime("%H:%M") for h in range(24) for m in [0, 30]]
    start_time = st.selectbox("Hora de inicio", [""] + horas_opciones)
    end_time = st.selectbox("Hora de finalización", [""] + horas_opciones)
    bus_type = st.selectbox("Tipo de Autobús", list(MIN_TARIFAS.keys()))
    submitted = st.form_submit_button("Calcular tarifa")

if submitted:
    if not origin or not destination or not fecha:
        st.error("Debes ingresar origen, destino y una fecha.")
    else:
        st.info("Calculando tarifa...")

        params = {
            "origin": origin,
            "destination": destination,
            "key": api_key,
            "language": "es",
            "region": "jp"
        }
        if stops.strip():
            waypoints = stops.strip().split("\n")
            params["waypoints"] = "|".join(waypoints)

        response = requests.get("https://maps.googleapis.com/maps/api/directions/json", params=params)
        data = response.json()

        if data["status"] != "OK":
            st.error("Error: " + data.get("error_message", data["status"]))
        else:
            km_total = sum(leg["distance"]["value"] for leg in data["routes"][0]["legs"]) / 1000
            tarifa_min = MIN_TARIFAS[bus_type]
            tarifa_km = TARIFAS_KM[bus_type]

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
                detalle = f"Base + ¥20,000 + ¥{extra_km_charge:,} por {bloques_extra} bloques de 20km extra"

            st.success("¡Cálculo completado!")
            st.metric("Distancia Total", f"{km_total:.2f} km")
            st.metric("Tarifa Total", f"¥{total_tarifa:,.0f} JPY")

            st.markdown("### Detalle del Cálculo")
            st.write(f"Tipo de vehículo: {bus_type}")
            st.write(detalle)
            st.write(f"Tarifa total estimada para {fecha.strftime('%d/%m/%Y')}: ¥{total_tarifa:,.0f}")
