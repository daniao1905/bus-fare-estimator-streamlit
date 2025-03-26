# Calculadora de Tarifas con Autocompletado Popup + Mapa y Lógica Real

Este sistema calcula tarifas reales por distancia en Japón con:
- Lógica escalonada
- Autocompletado activo estilo popup
- Mapa justo debajo de los inputs de destino
- Soporte para bus mediano

## Cómo usar

1. Descomprime el zip
2. Crea `.streamlit/secrets.toml` con:
```toml
GOOGLE_MAPS_API_KEY = "TU_API_KEY"
```
3. Ejecuta:
```bash
streamlit run app.py
```
