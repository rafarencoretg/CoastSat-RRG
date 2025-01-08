### VERIFICAR SI ESTA FUNCIÓN ES NECESARIA, YA QUE SI SE PUEDEN DESCARGAR LOS POLÍGONOS NO SERVIRÍA


import os
import geopandas as gpd

def convert_gis_files(input_folder):
    # Recorre todos los archivos en la carpeta de entrada
    for root, _, files in os.walk(input_folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_name, file_extension = os.path.splitext(file)
            
            # Determina el formato del archivo actual
            file_extension = file_extension.lower()
            if file_extension in ['.shp', '.geojson', '.kml', '.kmz']:
                try:
                    # Carga el archivo con GeoPandas
                    if file_extension in ['.kml', '.kmz']:
                        gdf = gpd.read_file(file_path, driver='KML')
                    else:
                        gdf = gpd.read_file(file_path)
                    
                    # Define los nombres de salida
                    output_shp = os.path.join(root, f"{file_name}.shp")
                    output_geojson = os.path.join(root, f"{file_name}.geojson")
                    output_kml = os.path.join(root, f"{file_name}.kml")
                    
                    # Exporta a SHP
                    if not os.path.exists(output_shp):
                        gdf.to_file(output_shp, driver='ESRI Shapefile')
                    
                    # Exporta a GeoJSON
                    if not os.path.exists(output_geojson):
                        gdf.to_file(output_geojson, driver='GeoJSON')
                    
                    # Exporta a KML
                    if not os.path.exists(output_kml):
                        gdf.to_file(output_kml, driver='KML')
                    
                    print(f"Convertido: {file_name} a SHP, GeoJSON y KML")
                except Exception as e:
                    print(f"Error procesando {file}: {e}")

# Carpeta de entrada (modificar según sea necesario)
input_folder = "GIS"

# Llama a la función
convert_gis_files(input_folder)
