"""
RUNNI - Mapa de Calor de Uso de Bicicletas
==========================================
Paso 1: Visualizar patrones de uso para decidir expansión al sur del Valle de Aburrá

INSTRUCCIONES:
1. Instala dependencias: pip install pandas folium requests
2. Corre el script: python runni_heatmap.py
3. Abre el archivo 'mapa_runni.html' que se genera

Cuando tengas acceso a la API, reemplaza la función `obtener_datos_api()`
con tus credenciales reales. El resto del código no cambia.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import folium
from folium.plugins import HeatMap
import json
import random
from datetime import datetime, timedelta


# ==============================================================================
# SECCIÓN 1: FUENTE DE DATOS
# Cuando tengas la API, solo modifica esta función.
# ==============================================================================

def obtener_datos_api(api_url=None, api_key=None):
    """
    Conecta con la API de Runni y retorna datos de ubicación.
    
    Preguntas que debes hacerle a Pablo:
    - ¿Cuál es la URL base de la API?
    - ¿Cómo me autentico? (token, API key, usuario/contraseña)
    - ¿Qué endpoint da el historial de ubicaciones?
    - ¿Los datos son en tiempo real o históricos?
    - ¿En qué formato vienen? (JSON, CSV)
    
    Campos ideales a pedir:
    - bike_id, timestamp, latitude, longitude
    - station_id, battery_level, trip_id (si existen)
    """
    
    # --- MODO REAL (descomenta cuando tengas la API) ---
    # import requests
    # headers = {"Authorization": f"Bearer {api_key}"}
    # response = requests.get(f"{api_url}/locations/history", headers=headers)
    # datos = response.json()
    # return pd.DataFrame(datos)
    
    # --- MODO SIMULADO (datos de prueba mientras llega la API) ---
    print("⚠️  Usando datos SIMULADOS. Reemplaza con API real cuando esté disponible.")
    return generar_datos_simulados()


def generar_datos_simulados():
    """
    Genera datos falsos pero realistas para Medellín y sur del Valle de Aburrá.
    Simula patrones de uso reales: más actividad en corredores y zonas comerciales.
    """
    random.seed(42)
    
    # Zonas de alta actividad (donde se concentran las bicis)
    zonas = [
        # (nombre, lat_centro, lon_centro, radio, peso_actividad)
        ("El Poblado",          6.2086, -75.5680, 0.015, 150),
        ("Envigado Centro",     6.1752, -75.5940, 0.012, 120),
        ("Laureles",            6.2441, -75.5897, 0.012, 100),
        ("Sabaneta",            6.1514, -75.6160, 0.010,  80),
        ("Itagüí Centro",       6.1849, -75.5990, 0.010,  70),
        ("Av. El Poblado",      6.1900, -75.5750, 0.008,  90),  # Tu hipótesis!
        ("Bello Centro",        6.3389, -75.5578, 0.010,  50),
        ("Estadio",             6.2567, -75.5894, 0.010,  60),
    ]
    
    registros = []
    fecha_inicio = datetime.now() - timedelta(days=30)
    
    for nombre, lat, lon, radio, actividad in zonas:
        for _ in range(actividad):
            # Dispersión aleatoria alrededor del centro de la zona
            lat_r = lat + random.gauss(0, radio)
            lon_r = lon + random.gauss(0, radio)
            
            # Timestamp aleatorio en los últimos 30 días
            ts = fecha_inicio + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(6, 22),
                minutes=random.randint(0, 59)
            )
            
            registros.append({
                "bike_id":        f"RUNNI-{random.randint(1, 250):03d}",
                "timestamp":      ts.strftime("%Y-%m-%d %H:%M:%S"),
                "latitude":       round(lat_r, 6),
                "longitude":      round(lon_r, 6),
                "zona":           nombre,
                "battery_level":  random.randint(10, 100),
                "station_id":     f"ST-{random.randint(1, 4):02d}",
            })
    
    df = pd.DataFrame(registros)
    print(f"✅ Datos simulados generados: {len(df)} registros de {df['bike_id'].nunique()} bicis")
    return df


# ==============================================================================
# SECCIÓN 2: PROCESAMIENTO
# ==============================================================================

def procesar_datos(df):
    """Limpia y valida los datos antes de visualizar."""
    
    print(f"\n📊 Procesando {len(df)} registros...")
    
    # Eliminar filas sin coordenadas
    df = df.dropna(subset=["latitude", "longitude"])
    
    # Validar rango geográfico (Valle de Aburrá aprox.)
    df = df[
        (df["latitude"].between(6.10, 6.40)) &
        (df["longitude"].between(-75.70, -75.50))
    ]
    
    # Convertir timestamp si existe
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    print(f"✅ Registros válidos: {len(df)}")
    print(f"📍 Área cubierta:")
    print(f"   Lat: {df['latitude'].min():.4f} → {df['latitude'].max():.4f}")
    print(f"   Lon: {df['longitude'].min():.4f} → {df['longitude'].max():.4f}")
    
    return df


# ==============================================================================
# SECCIÓN 3: MAPA DE CALOR
# ==============================================================================

def construir_mapa(df):
    """
    Construye el mapa interactivo con:
    - Heatmap de uso de bicicletas
    - Estaciones actuales de Runni
    - Zonas clave del sur del Valle de Aburrá
    """
    
    print("\n🗺️  Construyendo mapa...")
    
    # Centro del mapa: Medellín
    centro = [6.2442, -75.5812]
    mapa = folium.Map(location=centro, zoom_start=12, tiles="CartoDB positron")
    
    # --- CAPA 1: Heatmap de uso ---
    coordenadas = df[["latitude", "longitude"]].values.tolist()
    HeatMap(
        coordenadas,
        name="🔥 Uso de bicicletas",
        radius=15,
        blur=10,
        max_zoom=13,
        gradient={0.2: "blue", 0.5: "lime", 0.8: "orange", 1.0: "red"}
    ).add_to(mapa)
    
    # --- CAPA 2: Estaciones actuales de Runni ---
    estaciones_actuales = [
        {"nombre": "Sede principal - Socya Guayabal (contratos, mantenimiento)", "lat": 6.2321, "lon": -75.5815},
        {"nombre": "Estación - Laureles (ubicación aprox.)",                     "lat": 6.2441, "lon": -75.5897},
        {"nombre": "Estación - Olaya Herrera ✨ (nuevo)",                        "lat": 6.2138, "lon": -75.5852},
    ]
    
    capa_estaciones = folium.FeatureGroup(name="📍 Estaciones actuales Runni")
    for est in estaciones_actuales:
        folium.Marker(
            location=[est["lat"], est["lon"]],
            popup=folium.Popup(est["nombre"], max_width=200),
            icon=folium.Icon(color="blue", icon="bolt", prefix="fa"),
        ).add_to(capa_estaciones)
    capa_estaciones.add_to(mapa)
    
    # --- CAPA 3: Zonas de expansión potencial (sur del Valle) ---
    zonas_expansion = [
        {"nombre": "Envigado Centro",    "lat": 6.1752, "lon": -75.5940, "score": "Alto"},
        {"nombre": "Sabaneta",           "lat": 6.1514, "lon": -75.6160, "score": "Medio-Alto"},
        {"nombre": "Itagüí",             "lat": 6.1849, "lon": -75.5990, "score": "Medio"},
        {"nombre": "Av. El Poblado ⭐",  "lat": 6.1900, "lon": -75.5750, "score": "Alto (hipótesis)"},
    ]
    
    colores = {"Alto": "green", "Medio-Alto": "orange", 
               "Medio": "beige", "Alto (hipótesis)": "green"}
    
    capa_expansion = folium.FeatureGroup(name="🚀 Zonas de expansión (sur)")
    for zona in zonas_expansion:
        folium.CircleMarker(
            location=[zona["lat"], zona["lon"]],
            radius=20,
            color=colores.get(zona["score"], "gray"),
            fill=True,
            fill_opacity=0.3,
            popup=folium.Popup(
                f"<b>{zona['nombre']}</b><br>Score: {zona['score']}", 
                max_width=200
            ),
        ).add_to(capa_expansion)
    capa_expansion.add_to(mapa)
    
    # Control de capas
    folium.LayerControl(collapsed=False).add_to(mapa)
    
    # Leyenda
    leyenda_html = """
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
                background-color: white; padding: 15px; border-radius: 8px;
                border: 2px solid #ccc; font-family: Arial; font-size: 13px;">
        <b>🚲 RUNNI - Expansión Sur</b><br><br>
        🔴 Alta demanda<br>
        🟠 Demanda media<br>
        🔵 Baja demanda<br><br>
        🟢 Zona prioritaria expansión<br>
        🟠 Zona a validar<br>
        ⚡ Estación actual
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(leyenda_html))
    
    return mapa


# ==============================================================================
# SECCIÓN 4: ANÁLISIS DE VACÍOS
# ==============================================================================

def analizar_vacios(df):
    """
    Identifica zonas con alta demanda pero sin estaciones cercanas.
    Esto es el corazón del modelo de expansión.
    """
    print("\n📈 ANÁLISIS DE ZONAS DE OPORTUNIDAD")
    print("=" * 45)
    
    # Dividir el sur en cuadrantes
    sur = df[df["latitude"] < 6.22].copy()
    
    if len(sur) == 0:
        print("No hay datos del sur aún.")
        return
    
    # Contar actividad por zona aproximada
    sur["zona_grid"] = (
        (sur["latitude"] * 100).astype(int).astype(str) + "_" +
        (sur["longitude"] * 100).astype(int).astype(str)
    )
    
    actividad = sur.groupby("zona_grid").size().sort_values(ascending=False)
    
    print(f"\nTop zonas con mayor actividad en el SUR:")
    print(f"(Estas son las candidatas para nuevas estaciones)\n")
    
    for i, (zona, count) in enumerate(actividad.head(5).items(), 1):
        lat_aprox = int(zona.split("_")[0]) / 100
        lon_aprox = int(zona.split("_")[1]) / 100
        print(f"  {i}. Zona ({lat_aprox:.2f}, {lon_aprox:.2f}) → {count} registros")
    
    print(f"\n💡 Total registros en el sur: {len(sur)}")
    print(f"💡 Zonas activas identificadas: {actividad[actividad > 5].count()}")


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("  🚲 RUNNI - Sistema de Expansión Inteligente")
    print("  Paso 1: Mapa de Calor de Uso")
    print("=" * 50)
    
    # 1. Obtener datos (simulados por ahora)
    df = obtener_datos_api()
    
    # 2. Limpiar y validar
    df = procesar_datos(df)
    
    # 3. Construir mapa
    mapa = construir_mapa(df)
    
    # 4. Analizar vacíos
    analizar_vacios(df)
    
    # 5. Guardar mapa
    archivo_salida = "mapa_runni.html"
    mapa.save(archivo_salida)
    
    print(f"\n✅ ¡Listo! Mapa guardado como '{archivo_salida}'")
    print(f"   Abre ese archivo en tu navegador para verlo.")
    print(f"\n🔜 Próximo paso:")
    print(f"   Cuando tengas la API, reemplaza obtener_datos_api()")
    print(f"   con tu URL y API key real.")