import os
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt

from coastsat import SDS_download, SDS_preprocess, SDS_shoreline, SDS_tools, SDS_transects



### Archivo con funciones auxiliares para procesar código


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




def save_jpg(jpg_sat_list, metadata, settings, use_matplotlib=False):
    """
    Saves a .jpg image for all the images contained in metadata.

    KV WRL 2018

    Arguments:
    -----------
    jpg_sat_list: list
        List of satellites to process
    metadata: dict
        Contains all the information about the satellite images that were downloaded
    settings: dict
        Dictionary with configuration settings
    use_matplotlib: boolean
        False to save a .jpg and True to save as matplotlib plots

    Returns:
    -----------
    Stores the images as .jpg in a folder named /preprocessed
    """

    sitename = settings['inputs']['sitename']
    cloud_thresh = settings['cloud_thresh']
    s2cloudless_prob = settings['s2cloudless_prob']
    filepath_data = settings['inputs']['filepath']

    # Create subfolder to store the jpg files
    filepath_jpg = os.path.join(filepath_data, sitename, 'jpg_files', 'preprocessed')
    if not os.path.exists(filepath_jpg):
        os.makedirs(filepath_jpg)

    # Loop through satellite list
    for satname in jpg_sat_list:
        if satname not in metadata:
            print(f'Warning: {satname} not found in metadata. Skipping...')
            continue

        print(f'Saving images as jpg for {satname}:')
        filepath = SDS_tools.get_filepath(settings['inputs'], satname)
        filenames = metadata[satname]['filenames']
        print('%s: %d images' % (satname, len(filenames)))

        # Loop through images
        for i in range(len(filenames)):
            date = filenames[i][:19]  # Extract date from filename
            jpg_filename = os.path.join(filepath_jpg, f"{date}_{satname}.jpg")

            # Check if the image already exists
            if os.path.exists(jpg_filename):
                continue  # Skip to the next image

            print('\r%d%%' % int((i + 1) / len(filenames) * 100), end='')

            # Image filename
            fn = SDS_tools.get_filenames(filenames[i], filepath, satname)

            # Read and preprocess image
            im_ms, georef, cloud_mask, im_extra, im_QA, im_nodata = SDS_preprocess.preprocess_single(
                fn, satname, settings['cloud_mask_issue'], settings['pan_off'], s2cloudless_prob
            )

            # Compute cloud_cover percentage (with no data pixels)
            cloud_cover_combined = np.divide(sum(sum(cloud_mask.astype(int))),
                                             (cloud_mask.shape[0] * cloud_mask.shape[1]))
            if cloud_cover_combined > 0.99:  # If 99% of cloudy pixels in image, skip
                continue

            # Remove no data pixels from the cloud mask
            cloud_mask_adv = np.logical_xor(cloud_mask, im_nodata)

            # Compute updated cloud cover percentage (without no data pixels)
            cloud_cover = np.divide(sum(sum(cloud_mask_adv.astype(int))),
                                    (sum(sum((~im_nodata).astype(int)))))
            # Skip image if cloud cover is above threshold
            if cloud_cover > cloud_thresh or cloud_cover == 1:
                continue

            # Save .jpg
            plt.ioff()  # Turning interactive plotting off
            SDS_preprocess.create_jpg(im_ms, cloud_mask, date, satname, filepath_jpg, use_matplotlib)

        print('')

    # Print the location where the images have been saved
    print('Satellite images saved as .jpg in ' + filepath_jpg)
