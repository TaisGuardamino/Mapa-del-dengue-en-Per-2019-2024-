import pandas as pd
import folium
import json
import streamlit as st
from streamlit_folium import folium_static

# Especificamos las rutas de nuestros archivos
## Base de datos de casos de dengue por departamentos:
ruta_csv = 'dengue.csv'
## Archivo Json del mapa de Perú dividido por epartamentos: 
ruta_geojson = 'peru_departamental_simple.geojson'

# Leemos el archivo CSV en un DataFrame
df = pd.read_csv(ruta_csv)

# Normalizamos los nombres de las regiones en el DataFrame
df['Departamentos'] = df['Departamentos'].str.strip().str.upper()

# Verificamos las primeras filas del DataFrame
print(df.head())

# Leemos el archivo GeoJSON
with open(ruta_geojson) as f:
    geojson_data = json.load(f)

# Creamos el mapa
def crear_mapa(año):
    mapa = folium.Map(location=[-9.19, -75.0152], zoom_start=5)

    # Creamos una función de estilo para el mapa de densidad (Asignamos colores según la cantidad de casos)
    def estilo(feature):
        Departamentos = feature['properties']['NOMBDEP']
        Departamentos = Departamentos.strip().upper()
        try:
            densidad = df.loc[df['Departamentos'] == Departamentos, str(año)].values[0]
            return {
                'fillColor': '#ff0000' if densidad > 1500 else '#FF5900' if densidad > 1000 else
                             '#FF8F00' if densidad > 500 else '#FFB600' if densidad > 300 else
                             '#FFE400' if densidad > 100 else "#FFF176" if densidad > 100 else
                             "#FFF9C1" ,
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.6,
            }
        except IndexError:
            return {
                'fillColor': '#ffffff',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.1,
            }

    # Añadimos las regiones al mapa
    folium.GeoJson(
        geojson_data,
        style_function=estilo,
        tooltip=folium.GeoJsonTooltip(fields=['NOMBDEP'], aliases=['Departamentos:'])
    ).add_to(mapa)

    # Creamos la leyenda como un DivIcon (Los colores y textos que indican el número de casos de dengue por departamento)
    html_leyenda = """
    <div style="position: fixed;
                bottom: 50px; left: 50px; width: 220px; height: 200px;
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color: white; opacity: 0.8;">
         <b>Leyenda</b><br>
    <i style="background: #ff0000; width: 16px; height: 18px; display: inline-block;"></i> > 1500<br>
    <i style="background: #FF5900; width: 16px; height: 18px; display: inline-block;"></i> 1000 - 1500<br>
    <i style="background: #FF8F00; width: 16px; height: 18px; display: inline-block;"></i> 500 - 1000<br>
    <i style="background: #FFB600; width: 16px; height: 18px; display: inline-block;"></i> 300 - 500<br>
    <i style="background: #FFE400; width: 16px; height: 18px; display: inline-block;"></i> 100 - 300<br>
    <i style="background: #FFF176; width: 16px; height: 18px; display: inline-block;"></i> 50 - 100<br>
    <i style="background: #FFF9C1; width: 16px; height: 18px; display: inline-block;"></i> <= 50<br>
</div>
"""

    leyenda = folium.Marker(
        location=[-12.0464, -77.0428], 
        icon=folium.DivIcon(
            icon_size=(700, 250),
            icon_anchor=(0, 0),
            html=html_leyenda,
        )
    )

    mapa.add_child(leyenda)
    
    return mapa

# Título de la aplicación
st.title('Mapa de Densidad Poblacional de los casos de dengue en Perú (2019 - 2024)')

# Subtítulo que advierte sobre la fecha de corte en los datos del año 2024
st.subheader('Importante: El año 2024 cuenta con datos registrados hasta la semana epidemiológica 10.')

# Indicación para que el usuario seleccione el año
año = st.selectbox('Seleccione el año:', options=[2019, 2020, 2021, 2022, 2023, 2024])

# Creamos y mostramos el mapa
if año:
    mapa = crear_mapa(año)
    folium_static(mapa)
