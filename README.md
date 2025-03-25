# Bus Fare Estimator - Streamlit App

Calculadora automática de tarifas de autobuses según ruta y tipo de vehículo, usando Google Maps API.

## Cómo usar

1. Clona el repositorio
2. Crea el archivo `.streamlit/secrets.toml` con tu Google Maps API Key
3. Ejecuta localmente:
```bash
streamlit run app.py
```

## Deploy en Streamlit Cloud

1. Sube este repo a GitHub
2. Ve a https://streamlit.io/cloud
3. Conecta tu cuenta GitHub y selecciona este repositorio
4. Agrega tu API Key en `Secrets`:
```toml
GOOGLE_MAPS_API_KEY = "TU_API_KEY"
```
