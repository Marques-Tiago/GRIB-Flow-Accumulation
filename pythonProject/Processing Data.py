# Função para processar cada arquivo GRIB
def process_grib_file(file_path):

    ds = cfgrib.open_dataset(file_path)

    df = ds.to_dataframe().reset_index()

    df['time'] = pd.to_datetime(df['time'])
    df_sorted = df.sort_values(by='time')

    return df_sorted

# Caminho para os arquivos GRIB
file_pattern = 'C:/.grib'

files = glob.glob(file_pattern)

# Armazenar DataFrames processados
dataframes = []

for file_path in files:
    df_sorted = process_grib_file(file_path)
    dataframes.append(df_sorted[['time', 'dis24','latitude','longitude']])

all_data = pd.concat(dataframes)

max_value = all_data['dis24'].max()

output_path = 'C:/.csv' # Nome do arquivo de saída
all_data.to_csv(output_path, index=False)

print(f"Valor máximo: {max_value}")
print(f"Dados exportados para {output_path}")

#-----------------------------------------

%%time

output_path = 'C:/.csv' # Nome do arquivo de saída
# Carregar o CSV em um DataFrame
csv_file = output_path
df = pd.read_csv(csv_file)

# Corrigir longitude se necessário
df['longitude'] = df['longitude'].apply(lambda x: x if x <= 180 else x - 360)

# Supondo que o CSV tenha colunas 'longitude' e 'latitude'
df['geometry'] = df.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)

# Definir o CRS dos pontos (ajuste conforme necessário, por exemplo, EPSG:4326 para WGS84)
gdf_points = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')

# Carregar o GeoJSON em um GeoDataFrame
geojson_file = 'C:/.geojson'
gdf_polygons = gpd.read_file(geojson_file)

# Verificar se os sistemas de coordenadas são os mesmos e, se necessário, fazer a reprojeção
if gdf_points.crs != gdf_polygons.crs:
    gdf_points = gdf_points.to_crs(gdf_polygons.crs)

# Filtrar os pontos que estão dentro dos polígonos
points_within_polygons = gpd.sjoin(gdf_points, gdf_polygons, predicate='within', how='inner')

# Salvar o resultado em um novo CSV
output_csv_file = 'C:/.csv'
points_within_polygons.to_csv(output_csv_file, index=False)

print(f'Os pontos filtrados foram salvos em {output_csv_file}')



