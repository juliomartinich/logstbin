# coding: utf-8
# proceso para un informe de estados por camión
# 2-dic-2024 inicio con lectura
import pandas as pd
import numpy as np
# Leer el archivo CSV con las plantas
print("---------------------------------------------")
print("leo geoplantas.csv")
geoplantas = pd.read_csv('geoplantas.csv', sep=';', low_memory=False, decimal=',')
print("---------------------------------------------")

from datetime import datetime
import argparse

# Configurar argparse para leer argumentos de la línea de comandos
parser = argparse.ArgumentParser(description="Leer un archivo Excel con fecha como parámetro.")
parser.add_argument(
    "fecha", 
    type=str, 
    help="Fecha en formato dd-mm-yy (por ejemplo, 28-11-24)."
)
args = parser.parse_args()
# leo todos los archivosacrhivo trackit
# Función para generar el nombre del archivo
def generar_nombre_archivo(nombre, fecha, extension):
    # Convierte la fecha en el formato deseado: MM-DD-YYYY
    fecha_formateada = fecha.strftime("%-m-%-d-%Y")
    nombre_archivo = f"{nombre} {fecha_formateada}.{extension}"
    return nombre_archivo

# Ingresar la fecha como parámetro
try:
    # Convertir la fecha de texto a objeto datetime
    fecha = datetime.strptime(args.fecha, "%d-%m-%y")
    
    # Generar el nombre del archivo
    nombre = 'StatusBreakdown'
    extension = 'xls'
    nombre_archivo = generar_nombre_archivo(nombre, fecha, extension)
    print(f"Leyendo el archivo: {nombre_archivo}")
    
    # Leer el archivo Excel
    trackit = pd.read_excel(nombre_archivo, header=None)
except FileNotFoundError:
    print(f"El archivo '{nombre_archivo}' no se encontró.")
except ValueError:
    print("Formato de fecha inválido. Por favor use el formato YYYY-MM-DD.")

trackit = trackit.iloc[5:]   # las primeras 5 filas las borro
trackit = trackit.reset_index(drop=True) # para que no empiece del 5
trackit.columns = ["truckId","descequipo","nrofunc","nombre","apellido","erpTicketNumber","trabajo","desctrabajo","planta","descplanta","nroestado","status","statusSource","fechahora","dura","ptoref","latitude","longitude","it1","it2","it3","millas","fuel"]
trackit["fechahora"]= pd.to_datetime(trackit["fechahora"])
# Convertir la columna 'latitude' a numérico, dejando NaN para valores no convertibles
trackit["dura"] = pd.to_numeric(trackit["dura"], errors="coerce")
trackit["latitude"] = pd.to_numeric(trackit["latitude"], errors="coerce")
trackit["longitude"] = pd.to_numeric(trackit["longitude"], errors="coerce")
trackit["nroestado"] = pd.to_numeric(trackit["nroestado"], errors="coerce")
#trackit["latitude"] = trackit["latitude"].apply(lambda x: str(x).replace('.', ',') if pd.notna(x) else x)
#trackit["longitude"] = trackit["longitude"].apply(lambda x: str(x).replace('.', ',') if pd.notna(x) else x)
#trackit["dura"] = trackit["dura"].apply(lambda x: str(x).replace('.', ',') if pd.notna(x) else x)
print("Archivo de trackit leído correctamente")

# Imprimo min y max de fechas
min_fecha = trackit['fechahora'].min()
max_fecha = trackit['fechahora'].max()
print(f"trackit: desde {min_fecha} hasta {max_fecha}")

# agrego variable NuevoTicket para los casos en que se cambia de Ticket en la mitad del proceso

# Crear la nueva columna "NuevoTicket"
trackit["OldTicket"] = trackit["erpTicketNumber"]

for truck_id, group in trackit.groupby("truckId"):
  current_ticket = None

  for i in group.index:
    row = trackit.loc[i]
    
    # Si el estado es 34, asignar un nuevo ticket
    if row["nroestado"] in [9, 17, 7, 34] :
        current_ticket = row["OldTicket"]
    
    # Asignar el valor actual de current_ticket a la nueva columna
    trackit.at[i, "erpTicketNumber"] = current_ticket

    # Si el estado es 6, el ticket ya no se debe propagar
    if row["nroestado"] == 6:
        current_ticket = None
    

# Exportar a CSV
print("el resultado queda en estadostrackit.csv")
print("---------------------------------")
trackit.to_csv('estadostrackit.csv', sep=';', quotechar='"', quoting=1, decimal=',', header=True, na_rep='')

#------------------------------- ahora comienzo a hacer una tabla pivote

# Filtrar el DataFrame para obtener filas donde nroestado está entre 0 y 6
trackit["nroestado"] = pd.to_numeric(trackit["nroestado"], errors="coerce")
tif = trackit[(trackit["nroestado"] >= 0) & (trackit["nroestado"] <= 6)]

# Función para calcular la distancia en metros usando la fórmula de Haversine
def haversine(lat1, lon1, lat2, lon2):

    # Comprobar si alguna de las variables de entrada es nula
    if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
        return np.nan  # Retornar NaN si alguna de las coordenadas es nula

    # Reemplazar las comas por puntos y convertir a float
    #lat1, lon1, lat2, lon2 = map(lambda x: float(x.replace(',', '.')), [lat1, lon1, lat2, lon2])

    # Convertir de grados a radianes
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # Diferencias
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Fórmula de Haversine
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

    # Radio de la Tierra en metros (aproximadamente)
    R = 6371000

    # Calcular distancia en metros
    distancia = R * c

    return round(distancia, 0)


# Creamos la tabla pivot
pt = tif.pivot_table(
    index=['planta', 'truckId', 'erpTicketNumber'],       # Filas
    columns='nroestado',             # Columnas
    values=['statusSource', 'dura', 'latitude', 'longitude', 'fechahora'],
    aggfunc={'statusSource': 'first', 'dura': 'first', 'latitude': 'first', 'longitude': 'first', 'fechahora': 'first'}
)
# Ordenamos las columnas de forma que las variables de cada etapanum queden agrupadas
pt = pt.reorder_levels([1, 0], axis=1).sort_index(axis=1, level=0)

# Aplanamos los nombres de las columnas para facilitar el acceso
pt.columns = [f"{nroestado}_{var}" for nroestado, var in pt.columns]

# Restablecemos el índice para que 'rtruck' aparezca en todas las filas
pt = pt.reset_index()

# Iterar sobre las etapas de 0 a 6
for etapa in range(0, 7):
    # Crear los nombres de las columnas 'forma' y 'fechahora' para cada etapa
    statusSource_col = f"{etapa}_statusSource"
    fechahora_col = f"{etapa}_fechahora"

    # Asignar 'falta' en la columna 'forma' donde 'fechahora' sea NaN
    pt[statusSource_col] = pt.apply(
        lambda row: 'Falta' if pd.isna(row[fechahora_col]) else row[statusSource_col], axis=1
    )


# Iterar sobre cada fila de 'pt'
for idx, row in pt.iterrows():
# Iterar sobre las etapas

  # geo de la planta = estado 0 (cargando)
  latiplanta = row['0_latitude']  
  longplanta = row['0_longitude']  
  # geo de la obra = estado 2 (en obra)
  latiobra = row['2_latitude']  
  longobra = row['2_longitude']  

  # calculo los metros a planta (mp) y a obra (mo)
  for etapa in range(0, 7):
    metrosplanta = f"{etapa}_mp"
    metrosobra = f"{etapa}_mo"
    numlat = f"{etapa}_latitude"
    numlong = f"{etapa}_longitude"

    etalat = row[numlat]
    etalong = row[numlong]

    pt.at[idx, metrosplanta] = haversine(latiplanta, longplanta, etalat, etalong)
    pt.at[idx, metrosobra] = haversine(latiobra, longobra, etalat, etalong)

# Filtrar las columnas que no contienen 'latitude' ni 'longitude'
pt['horacarga'] = pt['0_fechahora']
pt = pt.loc[:, ~pt.columns.str.contains('_latitude|_longitude|_fechahora')]

# Crear una lista de las columnas de interés en el orden deseado
columnas_ordenadas = []

# Iterar sobre el rango de etapas
for etapa in range(0, 7):
    # Crear los nombres de las columnas para cada etapa
    etapas = [
        f"{etapa}_statusSource",
        f"{etapa}_dura",
        f"{etapa}_mp",
        f"{etapa}_mo",
    ]
    # Agregar las columnas en el orden adecuado
    columnas_ordenadas.extend(etapas)

# Asegúrate de incluir las demás columnas del DataFrame que no forman parte de las etapas
otras_columnas = [col for col in pt.columns if col not in columnas_ordenadas]

# Crear el nuevo DataFrame con las columnas ordenadas
pt = pt[otras_columnas + columnas_ordenadas]

# agrego columnas de resumen de resultado 
# s = 1 el estado existe
# t = 1 dura más de un minuto
# g = 1 está a más de 1000 metros de la planta
# OK = todos los anteriores están bien (1)
# EO = En Obra, nroestado 2
pt['EO_s'] = pt['2_statusSource'].apply(lambda x: 0 if x == 'Falta' else 1)
pt['EO_t'] = pt['2_dura'].apply(lambda x: 0 if x <= 1 else 1)
pt['EO_g'] = pt['2_mp'].apply(lambda x: 0 if x <= 1000 else 1)
pt['EO_OK'] = pt['EO_s'] * pt['EO_t'] * pt['EO_g']
# ID = Inicio Descarga
pt['ID_s'] = pt['3_statusSource'].apply(lambda x: 0 if x == 'Falta' else 1)
pt['ID_t'] = pt['3_dura'].apply(lambda x: 0 if x <= 1 else 1)
pt['ID_g'] = pt['3_mp'].apply(lambda x: 0 if x <= 1000 else 1)
pt['ID_OK'] = pt['ID_s'] * pt['ID_t'] * pt['ID_g']
# FD = Fin Descarga
pt['FD_s'] = pt['4_statusSource'].apply(lambda x: 0 if x == 'Falta' else 1)
pt['FD_t'] = pt['4_dura'].apply(lambda x: 0 if x <= 1 else 1)
pt['FD_g'] = pt['4_mp'].apply(lambda x: 0 if x <= 1000 else 1)
pt['FD_OK'] = pt['FD_s'] * pt['FD_t'] * pt['FD_g']
# RE = Retornando
pt['RE_s'] = pt['5_statusSource'].apply(lambda x: 0 if x == 'Falta' else 1)
pt['RE_t'] = pt['5_dura'].apply(lambda x: 0 if x <= 1 else 1)
pt['RE_g'] = pt['5_mp'].apply(lambda x: 0 if x <= 1000 else 1)
pt['RE_OK'] = pt['RE_s'] * pt['RE_t'] * pt['RE_g']
# EP = En Planta
# g = 1 está a menos de 1000 metros de la planta
pt['EP_s'] = pt['6_statusSource'].apply(lambda x: 0 if x == 'Falta' else 1)
pt['EP_t'] = pt['6_dura'].apply(lambda x: 0 if x <= 1 else 1)
pt['EP_g'] = pt['6_mp'].apply(lambda x: 1 if x <= 1000 else 0)
pt['EP_OK'] = pt['EP_s'] * pt['EP_t'] * pt['EP_g']
# si todo esta bueno, entonces esta bueno
pt['OK'] =pt['EO_OK'] * pt['ID_OK'] * pt['FD_OK'] * pt['RE_OK'] * pt['EP_OK']

# Exportar a CSV
out_nombre = 'pivottrackit'
out_extension = 'csv'
out_archivo = generar_nombre_archivo(out_nombre, fecha, out_extension)
print("el resultado queda en ", out_archivo)
print("---------------------------------")
pt.to_csv(out_archivo, sep=';', quotechar='"', quoting=1, decimal=',', header=True, na_rep='')

#--------------------------- ahora pongo los tickets hacia el lado por camión

# Crear un índice basado en la numeración dentro de cada grupo de planta y truckId
pt["indice"] = pt.groupby(["planta", "truckId"]).cumcount() + 1

# Pivotar los datos para ID_bueno
pivot_ides = pt.pivot(index=["planta", "truckId"], columns="indice", values="ID_OK")
pivot_ides.columns = [f"ID_OK_{i}" for i in pivot_ides.columns]

# Pivotar los datos para FDES_bueno
pivot_fdes = pt.pivot(index=["planta", "truckId"], columns="indice", values="FD_OK")
pivot_fdes.columns = [f"FD_OK_{i}" for i in pivot_fdes.columns]

# Unir ambas tablas pivoteadas
result = pd.concat([pivot_ides, pivot_fdes], axis=1).reset_index()

# Exportar a CSV
out_nombre = 'etlateral'
out_extension = 'csv'
out_archivo = generar_nombre_archivo(out_nombre, fecha, out_extension)
print("el resultado queda en ", out_archivo)
print("---------------------------------")
result.to_csv(out_archivo, sep=';', quotechar='"', quoting=1, decimal=',', header=True, na_rep='')

# --------------------------- Realizar el agrupamiento por 'planta' y 'truckId', sumando las columnas
resultado = (
    pt.groupby(["planta", "truckId"])
    .agg(
        Q =("planta", "size"),  # Contar filas
        QOK=("OK", "sum"),
        QEO_OK=("EO_OK", "sum"),
        QEO_s=("EO_s", "sum"),
        QEO_t=("EO_t", "sum"),
        QEO_g=("EO_g", "sum"),
        QID_OK=("ID_OK", "sum"),
        QID_s=("ID_s", "sum"),
        QID_t=("ID_t", "sum"),
        QID_g=("ID_g", "sum"),
        QFD_OK=("FD_OK", "sum"),
        QFD_s=("FD_s", "sum"),
        QFD_t=("FD_t", "sum"),
        QFD_g=("FD_g", "sum"),
        QRE_OK=("RE_OK", "sum"),
        QRE_s=("RE_s", "sum"),
        QRE_t=("RE_t", "sum"),
        QRE_g=("RE_g", "sum"),
        QEP_OK=("EP_OK", "sum"),
        QEP_s=("EP_s", "sum"),
        QEP_t=("EP_t", "sum"),
        QEP_g=("EP_g", "sum"),
    )
    .reset_index()  # Resetear el índice para convertir a DataFrame normal
)

# Exportar a CSV
out_nombre = 'et_sumas'
out_extension = 'csv'
out_archivo = generar_nombre_archivo(out_nombre, fecha, out_extension)
print("el resultado queda en ", out_archivo)
print("---------------------------------")
resultado.to_csv(out_archivo, sep=';', quotechar='"', quoting=1, decimal=',', header=True, na_rep='')


print(" ")
