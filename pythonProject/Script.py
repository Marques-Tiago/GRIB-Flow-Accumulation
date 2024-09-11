%pip install cfgrib
%pip install basemap
%pip install cartopy
%pip install cdsapi
%pip install xarray
%pip install pandas
%pip install geopandas
%pip install pygrib

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.basemap import shiftgrid
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import pandas as pd
import pygrib
import os
import cdsapi
import cfgrib
import glob
import json
from shapely.geometry import shape, Point, polygon

print("As bibliotecas rodaram")

import json
from shapely.geometry import shape, MultiPolygon, Polygon

#-----------------------------------------
def carregar_poligono_geojson(caminho_geojson):
    with open(caminho_geojson, 'r') as f:
        geojson = json.load(f)

        poligonos = []
        for feature in geojson['features']:
            geom = shape(feature['geometry'])
            if isinstance(geom, Polygon):
                poligonos.append(geom)
            elif isinstance(geom, MultiPolygon):
                poligonos.extend(geom.geoms)  # Adiciona os polígonos individuais do MultiPolygon à lista
            else:
                print(f"Geometria ignorada: {geom}")

        if not poligonos:
            raise ValueError("Nenhum polígono válido encontrado no GeoJSON.")

        multi_poligono = MultiPolygon(poligonos)
        bbox = multi_poligono.bounds  # (min_lon, min_lat, max_lon, max_lat)
        return multi_poligono, bbox


# Defina o caminho para o arquivo GeoJSON
geojson_path = 'C:/'

# Carregar o polígono do GeoJSON e obter a caixa delimitadora
poligono, bbox = carregar_poligono_geojson(geojson_path)

# A bounding box na ordem (max_lat, min_lon, min_lat, max_lon)
bbox_ordem_cds = [bbox[3], bbox[0], bbox[1], bbox[2]]

print(f"As coordenadas são {bbox_ordem_cds}")
#-----------------------------------------


# Definir a API e a chave
cds_api_url = 'https://cds.climate.copernicus.eu/api/v2'
cds_api_key = "" # Inserir sua API Key

# Guardar a chave da API
cdsapirc_path = os.path.expanduser('~/.cdsapirc')
with open(cdsapirc_path, 'w') as f:
    f.write(f"url: {cds_api_url}\n")
    f.write(f"key: {cds_api_key}\n")

with open(cdsapirc_path, 'r') as f:
    print(f.read())

c = cdsapi.Client()

# Função para consultar dados de um ano
def consultar_dados_ano(ano):
    try:
        output_file = f'C:/.grib'
        c.retrieve(
            'cems-glofas-historical',
            {
                'system_version': 'version_4_0',
                'variable': 'river_discharge_in_the_last_24_hours',
                'format': 'grib',
                'hydrological_model': 'lisflood',
                'hyear': [ano],
                'product_type': 'consolidated',
                'hmonth': [
                    'january', 'february', 'march',
                    'april', 'may', 'june',
                    'july', 'august', 'september',
                    'october', 'november', 'december',
                ],
                'hday': [
                    '05', '10', '15', '20',
                    '25', '30',
                ],
                'area': bbox_ordem_cds,  # Corrigido para o formato adequado
                'time': ['12:00'],
            },
            output_file
        )
        print(f"Dados de {ano} baixados com sucesso!")
        return output_file
    except Exception as e:
        print(f"Erro ao consultar dados de {ano}: {e}")
        return None

# Loop para consultar dados de vários anos
anos = range(1996,2000)  # Substitua com os anos desejados
for ano in anos:
    input_file = consultar_dados_ano(ano)

#-----------------------------------------
