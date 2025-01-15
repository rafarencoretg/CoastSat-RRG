import lzma
import shutil
import os

def decompress_all_nc_files_in_folder(folder_path):
    """
    Descomprime todos los archivos .nc.xz en una carpeta a su versión .nc.

    Parameters:
        folder_path (str): Ruta de la carpeta que contiene los archivos .nc.xz.

    Returns:
        list: Lista de rutas de los archivos descomprimidos (.nc).
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"La ruta '{folder_path}' no es una carpeta válida.")

    decompressed_files = []

    # Buscar todos los archivos .nc.xz en la carpeta
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.nc.xz'):
            compressed_file_path = os.path.join(folder_path, file_name)
            decompressed_file_path = compressed_file_path[:-3]  # Remueve el sufijo '.xz'
            
            try:
                # Descomprimir el archivo
                with lzma.open(compressed_file_path, 'rb') as compressed, open(decompressed_file_path, 'wb') as decompressed:
                    shutil.copyfileobj(compressed, decompressed)
                print(f"Archivo descomprimido exitosamente: {decompressed_file_path}")
                decompressed_files.append(decompressed_file_path)
            except Exception as e:
                print(f"Error al descomprimir '{compressed_file_path}': {e}")
    
    return decompressed_files

"""# Ruta de la carpeta que contiene los archivos .nc.xz
filepath = os.path.join(os.pardir,'AVISO','tide_model','fes2022b', 'ocean_tide_extrapolated')


# Llamar a la función para descomprimir todos los archivos
decompressed_files = decompress_all_nc_files_in_folder(filepath)

if decompressed_files:
    print("Archivos descomprimidos:")
    for file in decompressed_files:
        print(file)
else:
    print("No se encontraron archivos .nc.xz para descomprimir.")"""





# load pyfes and the global tide model (may take one minute)
import pyfes
import os
from datetime import datetime
import pytz

filepath = os.path.join(os.pardir,'AVISO','tide_model','fes2022b')
filepath = os.path.abspath(filepath)
config =  os.path.join(filepath, 'fes2022.yaml')
handlers = pyfes.load_config(config)

ocean_tide = handlers['tide']
load_tide = handlers['radial']
# load coastsat module to estimate slopes
from coastsat import SDS_slope

# get centroid, date range and timestep
centroid = [151.3023463 -33.7239154]
date_range = [pytz.utc.localize(datetime(2024,1,1)),
              pytz.utc.localize(datetime(2025,1,1))]
timestep = 900 # in seconds

# predict tides
dates_ts, tides_ts = SDS_slope.compute_tide(centroid, date_range, timestep, ocean_tide, load_tide)