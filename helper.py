import os
import geopandas as gpd


def transform_geojson_epsg(input_geojson, output_geojson, settings):
    """
    Identifica el EPSG de un archivo GeoJSON que contiene transectos (LINESTRING) en su segunda columna,
    imprime el EPSG actual y lo transforma al EPSG especificado en settings['output_epsg'].

    :param input_geojson: Ruta del archivo GeoJSON de entrada.
    :param output_geojson: Ruta del archivo GeoJSON de salida (transformado).
    :param settings: Diccionario con configuración, debe contener la clave 'output_epsg'.
    """
    # Cargar el archivo GeoJSON
    gdf = gpd.read_file(input_geojson)

    # Verificar el CRS (EPSG actual)
    if gdf.crs:
        input_epsg = gdf.crs.to_epsg()
        print(f"El EPSG actual del archivo es: {input_epsg}")
    else:
        print("No se encontró información de CRS en el archivo GeoJSON.")
        return

    # Verificar que 'output_epsg' esté en settings
    if 'output_epsg' not in settings:
        raise ValueError("El diccionario 'settings' debe contener la clave 'output_epsg'.")

    # Obtener el EPSG objetivo
    output_epsg = settings['output_epsg']

    # Transformar el GeoDataFrame al EPSG objetivo
    gdf_transformed = gdf.to_crs(epsg=output_epsg)
    print(f"Transformado al EPSG: {output_epsg}")

    # Guardar el archivo transformado en el GeoJSON de salida
    gdf_transformed.to_file(output_geojson, driver="GeoJSON")
    print(f"Archivo GeoJSON transformado guardado en: {output_geojson}")


"""settings = {
    'output_epsg': 32718  # Cambia al EPSG deseado (ejemplo: WGS 84)
}

input_geojson = "CoastSat_Web\OHIGGINS\chi0356\chi0356_transects.geojson"
output_geojson = "CoastSat_Web\OHIGGINS\chi0356\chi0356_transects_transformed.geojson"

transform_geojson_epsg(input_geojson, output_geojson, settings)"""



def convert_geojson_to_excel(geojson_folder):
    """
    Convierte todos los archivos .geojson de una carpeta a formato .xlsx y los guarda en otra carpeta.

    :param geojson_folder: Ruta de la carpeta que contiene los archivos .geojson.
    """

    # Iterar sobre todos los archivos en la carpeta de entrada
    for file_name in os.listdir(geojson_folder):
        if file_name.endswith('.geojson'):
            # Ruta completa del archivo de entrada
            file_path = os.path.join(geojson_folder, file_name)

            # Cargar el archivo .geojson
            data = gpd.read_file(file_path)

            # Convertir geometría a formato WKT
            data['geometry'] = data['geometry'].apply(lambda x: x.wkt)

            # Ruta completa del archivo de salida
            output_path = os.path.join(geojson_folder, file_name.replace('.geojson', '.xlsx'))

            # Guardar en formato Excel
            data.to_excel(output_path, index=False)
            print(f"Archivo convertido y guardado en: {output_path}")

    print("Todos los archivos .geojson han sido procesados.")