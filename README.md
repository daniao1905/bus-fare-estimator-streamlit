# Bus Fare Estimator - Streamlit (Google Maps con Place ID)

Calculadora de tarifas de autobuses en Japón usando Google Maps API y selecciones con `place_id`.

## Cómo usar

1. Clona el repositorio o descomprime este zip.
2. Crea un archivo `.streamlit/secrets.toml` con tu API Key de Google:
```toml
GOOGLE_MAPS_API_KEY = "TU_API_KEY"
```
3. Ejecuta localmente:
```bash
streamlit run app.py
```

## Deploy en Streamlit Cloud

1. Sube este repo a GitHub.
2. Ve a https://streamlit.io/cloud y conéctalo.
3. Agrega tu API Key en la sección "Secrets".
