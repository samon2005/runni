"""
RUNNI - Mapa de Calor de Domicilios (Demanda Potencial)
========================================================
Usa OpenStreetMap para extraer restaurantes y zonas comerciales
del Valle de Aburrá y construir un heatmap de demanda potencial.

INSTRUCCIONES:
1. pip install pandas folium requests
2. python runni_domicilios_heatmap.py
3. Abre 'mapa_domicilios_runni.html' en tu navegador

La primera vez tarda ~1-2 minutos descargando datos de OSM.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json
import time
import pandas as pd
import folium
from folium.plugins import HeatMap
import math


# ==============================================================================
# SECCIÓN 1: DESCARGA DE DATOS — OpenStreetMap (Overpass API)
# ==============================================================================

def descargar_restaurantes_osm():
    """
    Descarga todos los restaurantes, cafés, bares y comida rápida
    del Valle de Aburrá desde OpenStreetMap. Gratis y sin límites.
    """
    print("📡 Descargando datos de restaurantes desde OpenStreetMap...")
    print("   (Esto puede tardar 1-2 minutos la primera vez)\n")

    # Bounding box del Valle de Aburrá completo
    # Sur: Caldas, Norte: Bello, Oeste-Este: límites del valle
    bbox = "6.08,-75.72,6.40,-75.50"

    # Query Overpass: todos los negocios de comida
    query = f"""
    [out:json][timeout:60];
    (
      node["amenity"="restaurant"]({bbox});
      node["amenity"="fast_food"]({bbox});
      node["amenity"="cafe"]({bbox});
      node["amenity"="food_court"]({bbox});
      node["shop"="bakery"]({bbox});
      node["amenity"="bar"]({bbox});
    );
    out center;
    """

    url = "https://overpass-api.de/api/interpreter"

    try:
        response = requests.post(url, data={"data": query}, timeout=90)
        response.raise_for_status()
        datos = response.json()

        elementos = datos.get("elements", [])
        print(f"✅ Descargados {len(elementos)} negocios de comida del Valle de Aburrá")
        return elementos

    except requests.exceptions.Timeout:
        print("⚠️  Timeout en OSM. Usando datos de respaldo...")
        return datos_respaldo()
    except Exception as e:
        print(f"⚠️  Error conectando a OSM: {e}")
        print("   Usando datos de respaldo simulados...")
        return datos_respaldo()


def datos_respaldo():
    """
    Datos de respaldo si OSM no responde.
    Puntos reales de zonas comerciales del Valle de Aburrá.
    """
    import random
    random.seed(99)

    zonas = [
        # (nombre, lat, lon, cantidad, peso)
        ("El Poblado / Parque Lleras",    6.2086, -75.5680, 80, 1.0),
        ("Envigado Centro",               6.1752, -75.5940, 60, 0.9),
        ("Laureles / Estadio",            6.2480, -75.5897, 55, 0.8),
        ("Sabaneta Parque",               6.1514, -75.6160, 40, 0.7),
        ("Itagüí Centro",                 6.1849, -75.5990, 35, 0.6),
        ("Av. El Poblado (Medellin-Env)", 6.1950, -75.5760, 45, 0.85),
        ("Bello Centro",                  6.3389, -75.5578, 30, 0.5),
        ("Centro Medellín",               6.2518, -75.5636, 70, 0.9),
        ("Belén",                         6.2350, -75.6100, 40, 0.6),
        ("Robledo",                       6.2700, -75.5950, 25, 0.5),
        ("Sabaneta Sur / La Doctora",     6.1400, -75.6180, 20, 0.6),
        ("Caldas",                        6.0940, -75.6350, 15, 0.4),
    ]

    elementos = []
    for nombre, lat, lon, cant, peso in zonas:
        for _ in range(cant):
            elementos.append({
                "type": "node",
                "lat": lat + random.gauss(0, 0.008),
                "lon": lon + random.gauss(0, 0.008),
                "tags": {"name": nombre, "amenity": "restaurant"}
            })

    print(f"✅ Datos de respaldo: {len(elementos)} puntos generados")
    return elementos


# ==============================================================================
# SECCIÓN 2: PROCESAMIENTO
# ==============================================================================

def procesar_elementos(elementos):
    """Convierte los elementos OSM a un DataFrame limpio."""

    registros = []
    for el in elementos:
        lat = el.get("lat") or (el.get("center", {}).get("lat"))
        lon = el.get("lon") or (el.get("center", {}).get("lon"))
        tags = el.get("tags", {})

        if lat and lon:
            registros.append({
                "lat":      float(lat),
                "lon":      float(lon),
                "nombre":   tags.get("name", "Sin nombre"),
                "tipo":     tags.get("amenity", tags.get("shop", "comercio")),
            })

    df = pd.DataFrame(registros)

    # Filtrar solo Valle de Aburrá
    df = df[
        (df["lat"].between(6.08, 6.40)) &
        (df["lon"].between(-75.72, -75.50))
    ].reset_index(drop=True)

    # Clasificar zona
    df["zona"] = df["lat"].apply(clasificar_zona)

    print(f"\n📊 Resumen por zona:")
    resumen = df["zona"].value_counts()
    for zona, count in resumen.items():
        print(f"   {zona}: {count} negocios")

    return df


def clasificar_zona(lat):
    """Clasifica por zona geográfica norte-sur del Valle."""
    if lat > 6.30:
        return "Norte (Bello)"
    elif lat > 6.25:
        return "Medellín Norte"
    elif lat > 6.22:
        return "Medellín Centro"
    elif lat > 6.19:
        return "Medellín Sur / El Poblado"
    elif lat > 6.17:
        return "Frontera Medellín-Envigado"  # ⭐ Tu hipótesis
    elif lat > 6.14:
        return "Envigado"
    elif lat > 6.12:
        return "Sabaneta"
    else:
        return "Sur (Itagüí / Caldas)"


# ==============================================================================
# SECCIÓN 3: SCORE DE OPORTUNIDAD
# ==============================================================================

def calcular_score_zonas(df):
    """
    Calcula el score de oportunidad por zona.
    Score = densidad de negocios de comida (proxy de demanda de domicilios)
    """
    print("\n🏆 RANKING DE ZONAS — Score de Oportunidad para Runni")
    print("=" * 55)

    # Score por zona
    score = df.groupby("zona").agg(
        negocios=("lat", "count"),
        lat_centro=("lat", "mean"),
        lon_centro=("lon", "mean"),
    ).reset_index()

    # Normalizar score 0-100
    score["score"] = (score["negocios"] / score["negocios"].max() * 100).round(1)
    score = score.sort_values("score", ascending=False)

    # Estaciones actuales de Runni (para detectar vacíos)
    estaciones_runni = [
        (6.2321, -75.5815),  # Socya Guayabal (sede principal)
        (6.2441, -75.5897),  # Laureles
        (6.2138, -75.5852),  # Olaya Herrera (nuevo)
    ]

    def tiene_cobertura(lat, lon, radio_km=2.0):
        for elat, elon in estaciones_runni:
            dist = math.sqrt((lat - elat)**2 + (lon - elon)**2) * 111
            if dist < radio_km:
                return True
        return False

    score["tiene_estacion"] = score.apply(
        lambda r: tiene_cobertura(r["lat_centro"], r["lon_centro"]), axis=1
    )
    score["oportunidad"] = score.apply(
        lambda r: "⚠️ YA CUBIERTO" if r["tiene_estacion"] else "🚀 OPORTUNIDAD", axis=1
    )

    print(f"\n{'#':<3} {'Zona':<35} {'Score':>6} {'Negocios':>9} {'Estado'}")
    print("-" * 70)
    for i, row in score.iterrows():
        print(f"{score.index.get_loc(i)+1:<3} {row['zona']:<35} {row['score']:>6.1f} {row['negocios']:>9} {row['oportunidad']}")

    print("\n💡 Score = densidad de restaurantes/comida rápida/cafés")
    print("💡 Mayor score + sin estación = mejor candidato para expansión")

    return score


# ==============================================================================
# SECCIÓN 4: MAPA INTERACTIVO
# ==============================================================================

def construir_mapa(df, score):
    """
    Mapa con 4 capas:
    1. Heatmap de densidad de restaurantes (demanda potencial)
    2. Estaciones actuales de Runni
    3. Zonas de expansión recomendadas
    4. Markers de negocios individuales (solo zoom alto)
    """
    print("\n🗺️  Construyendo mapa interactivo...")

    centro = [6.2200, -75.5800]
    mapa = folium.Map(location=centro, zoom_start=12, tiles="CartoDB positron")

    # --- CAPA 1: Heatmap de domicilios ---
    coords = df[["lat", "lon"]].values.tolist()
    HeatMap(
        coords,
        name="🍔 Densidad de restaurantes (demanda domicilios)",
        radius=18,
        blur=12,
        max_zoom=14,
        gradient={0.2: "#0000ff", 0.4: "#00ff00", 0.6: "#ffff00",
                  0.8: "#ff8000", 1.0: "#ff0000"}
    ).add_to(mapa)

    # --- CAPA 2: Estaciones actuales Runni ---
    estaciones = [
        {"nombre": "Sede principal - Socya Guayabal (contratos, mantenimiento)", "lat": 6.2321, "lon": -75.5815},
        {"nombre": "Estación - Laureles (ubicación aprox.)",                     "lat": 6.2441, "lon": -75.5897},
        {"nombre": "Estación - Olaya Herrera ✨ (nuevo)",                        "lat": 6.2138, "lon": -75.5852},
    ]
    capa_est = folium.FeatureGroup(name="⚡ Estaciones actuales Runni")
    for e in estaciones:
        folium.Marker(
            [e["lat"], e["lon"]],
            popup=folium.Popup(f"<b>{e['nombre']}</b>", max_width=220),
            icon=folium.Icon(color="blue", icon="bolt", prefix="fa")
        ).add_to(capa_est)
        # Radio de cobertura (~2km)
        folium.Circle(
            [e["lat"], e["lon"]],
            radius=2000,
            color="blue", fill=True, fill_opacity=0.05,
            tooltip="Cobertura actual (~2km)"
        ).add_to(capa_est)
    capa_est.add_to(mapa)

    # --- CAPA 3: Zonas de expansión recomendadas ---
    oportunidades = score[~score["tiene_estacion"]].head(5)
    capa_exp = folium.FeatureGroup(name="🚀 Zonas recomendadas para expansión")

    colores_score = {range(80, 101): "green", range(50, 80): "orange",
                     range(0, 50): "lightgray"}

    for _, row in oportunidades.iterrows():
        color = "green" if row["score"] >= 70 else \
                "orange" if row["score"] >= 40 else "lightgray"

        folium.CircleMarker(
            [row["lat_centro"], row["lon_centro"]],
            radius=25,
            color=color, fill=True, fill_opacity=0.35,
            popup=folium.Popup(
                f"<b>📍 {row['zona']}</b><br>"
                f"Score: <b>{row['score']}</b>/100<br>"
                f"Negocios de comida: {row['negocios']}<br>"
                f"Estado: {row['oportunidad']}",
                max_width=240
            ),
            tooltip=f"🚀 {row['zona']} — Score {row['score']}"
        ).add_to(capa_exp)
    capa_exp.add_to(mapa)

    # --- Control de capas y leyenda ---
    folium.LayerControl(collapsed=False).add_to(mapa)

    leyenda = """
    <div style="position:fixed; bottom:30px; left:30px; z-index:1000;
                background:white; padding:15px; border-radius:10px;
                border:2px solid #aaa; font-family:Arial; font-size:12px;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.2);">
        <b>🚲 RUNNI — Mapa de Expansión</b><br><br>
        <span style="color:red">■</span> Alta densidad domicilios<br>
        <span style="color:orange">■</span> Densidad media<br>
        <span style="color:blue">■</span> Baja densidad<br><br>
        ⚡ Estación actual Runni<br>
        🟢 Zona prioritaria (sin cobertura)<br>
        🟠 Zona secundaria<br><br>
        <i>Círculo azul = radio ~2km cobertura</i>
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(leyenda))

    return mapa


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("=" * 55)
    print("  🚲 RUNNI — Mapa de Demanda de Domicilios")
    print("  Valle de Aburrá — Análisis de Expansión")
    print("=" * 55 + "\n")

    # 1. Descargar datos de restaurantes (OSM)
    elementos = descargar_restaurantes_osm()

    # 2. Procesar
    df = procesar_elementos(elementos)

    # 3. Calcular scores
    score = calcular_score_zonas(df)

    # 4. Construir mapa
    mapa = construir_mapa(df, score)

    # 5. Guardar
    archivo = "mapa_domicilios_runni.html"
    mapa.save(archivo)

    print(f"\n✅ ¡Listo! Abre '{archivo}' en tu navegador.")
    print("\n🔜 Próximo paso:")
    print("   Cuando tengas la API de Runni, corremos runni_heatmap.py")
    print("   y superponemos ambos mapas para ver vacíos reales.")