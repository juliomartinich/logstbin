import pandas as pd

# Leer el archivo CSV
print("---------------------------------------------")
print("leo geoplantas.csv")
geoplantas = pd.read_csv('geoplantas.csv', sep=';', low_memory=False, decimal=',')

# Leer el archivo CSV
print("---------------------------------------------")
print("leo logetapa.csv")
logetapa = pd.read_csv('logetapa.csv', sep=';', low_memory=False, decimal=',')

# Filtrar las filas que vienen del log SEo y son assignment
f1 = logetapa[(logetapa['log'] == "SEo") & (logetapa['apisola'] == "assignment")]
r1 = f1[['rtruck', 'rsdn', 'shipPoint', 'deliveryQuantity', 'fechahora','dispatchGroup']]

# filtro las filas STo assignment DLV para encontrar la latitude y longitude de la obra
f2 = logetapa[(logetapa['log'] == "STo") & (logetapa['apisola'] == "assignment") & (logetapa['orderSubType'] == 'DLV') ]
r2 = f2[['rtruck', 'rsdn', 'latitude', 'longitude', 'fechahora']]

# filtro las filas STo assignment RET para encontrar la latitude y longitude de la planta de destino
f3 = logetapa[(logetapa['log'] == "STo") & (logetapa['apisola'] == "assignmentRR") & (logetapa['orderSubType'] == 'RET') ]
r3 = f3[['rtruck', 'rsdn','fechahora', 'locationID']]

# Realizamos el merge de r1 y r2 renombro la esegunda columna 'fechahora' como 'fechahoraT'
r12 = pd.merge(r1, r2, on=['rtruck', 'rsdn'], how='left', suffixes=('', 'T'))
# Creamos el cardinal agrupando por 'rtruck' y 'rsdn' y contando las repeticiones, por si hace join 2 veces
r12['cardinal'] = r12.groupby(['rtruck', 'rsdn']).cumcount() + 1

# Realizamos el merge de r1 y r2 renombro la esegunda columna 'fechahora' como 'fechahoraT'
regticket = pd.merge(r12, r3, on=['rtruck', 'rsdn'], how='left', suffixes=('', 'R'))
# Creamos el cardinal agrupando por 'rtruck' y 'rsdn' y contando las repeticiones, por si hace join 2 veces
regticket['cardinalR'] = regticket.groupby(['rtruck', 'rsdn']).cumcount() + 1

#### hay algunos casos que no hay DLV, en esos casos debería buscar el assignmentLD DLV

# los cancelados
can = logetapa[(logetapa['log'] == "SEo") & (logetapa['apisola'] == "cancel")]
rcan = can[['rtruck', 'rsdn', 'fechahora']]

# Realizamos el merge y renombramos la segunda columna 'fechahora' como 'fechahoraCAN'
regticket2 = pd.merge(regticket, rcan, on=['rtruck', 'rsdn'], how='left', suffixes=('', 'CAN'))

# desde la tabla de geoplantas obtengo las latitu y longitud de las plantas de origen y destino
rpori = geoplantas[['shipPoint', 'NombrePlanta', 'Plati', 'Plong']]
regticket2A = pd.merge(regticket2, rpori, on=['shipPoint'], how='left', suffixes=('', 'ORI'))
rpdes = geoplantas[['locationID', 'NombrePlanta', 'Plati', 'Plong']]
regticket2B = pd.merge(regticket2A, rpdes, on=['locationID'], how='left', suffixes=('', 'DES'))

# quiero obtener el erpTicketNumber
ft = logetapa[(logetapa['log'] == "STo") & (logetapa['apisola'] == "assignmentLD")]
rt = ft[['rtruck', 'rsdn', 'erpTicketNumber','fechahora']]
rt2 = pd.merge(regticket2B, rt, on=['rtruck', 'rsdn'], how='left', suffixes=('', 'TN'))

# -------------
## ahora hago una tabla pivote, para obtener los valores de las etapa 
#solo las filas donde 'orden' es igual a "1,0" y 'etapanum' está entre 5 y 10

logetapa['forma'] = logetapa['statusSource'].fillna('') + ' ' + logetapa['trans'].fillna('')
logetapa_filtered = logetapa[(logetapa['orden'] == 1) & (logetapa['etapanum'].between(5, 10))].copy()

# Creamos una columna para identificar duplicados, agrupando por 'rtruck', 'rsdn', y 'etapanum'
logetapa_filtered['dup'] = logetapa_filtered.groupby(['rtruck', 'rsdn', 'etapanum']).cumcount() + 1

# Creamos la tabla pivot incluyendo 'duplicate_count' y 'trans'
pivot_table = logetapa_filtered.pivot_table(
    index=['rtruck', 'rsdn'],       # Filas
    columns='etapanum',             # Columnas
    values=['forma', 'latitude', 'longitude', 'fechahora', 'dif3', 'dup'],
    aggfunc={'forma': 'first', 'latitude': 'first', 'longitude': 'first', 
             'fechahora': 'first', 'dif3': 'first', 'dup': 'max'}
)
# Ordenamos las columnas de forma que las variables de cada etapanum queden agrupadas
pivot_table = pivot_table.reorder_levels([1, 0], axis=1).sort_index(axis=1, level=0)

# Aplanamos los nombres de las columnas para facilitar el acceso
pivot_table.columns = [f"{etapanum}_{var}" for etapanum, var in pivot_table.columns]

# Restablecemos el índice para que 'rtruck' aparezca en todas las filas
pivot_table = pivot_table.reset_index()

# -------------
# Realizamos el join entre regticket2B y la tabla pivote usando 'rtruck' y 'rsdn'
regticket_final = rt2.merge(pivot_table, on=['rtruck', 'rsdn'], how='left')

# Asegurar que todas las columnas esperadas existan (para evitar KeyError si falta alguna etapa en los datos)
for etapa in range(5, 11):
    for var in ['forma', 'latitude', 'longitude', 'fechahora', 'dif3', 'dup']:
        col_name = f"{etapa}_{var}"
        if col_name not in regticket_final.columns:
            if var == 'forma':
                regticket_final[col_name] = 'Falta'
            else:
                regticket_final[col_name] = pd.NA

# Iterar sobre las etapas de 5 a 10
for etapa in range(5, 11):
    # Crear los nombres de las columnas 'forma' y 'fechahora' para cada etapa
    forma_col = f"{etapa}_forma"
    fechahora_col = f"{etapa}_fechahora"
    
    # Asignar 'falta' en la columna 'forma' donde 'fechahora' sea NaN
    regticket_final[forma_col] = regticket_final.apply(
        lambda row: 'Falta' if pd.isna(row[fechahora_col]) else row[forma_col], axis=1
    )

import numpy as np

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


# Iterar sobre cada fila de 'regticket_final'
for idx, row in regticket_final.iterrows():
# Iterar sobre las etapas de 5 a 10
  for etapa in range(5, 11):
    hav = f"{etapa}_hav"
    numlat = f"{etapa}_latitude"
    numlong = f"{etapa}_longitude"

    if etapa == 5:
      lat = row['Plati']
      long = row['Plong']
    elif etapa == 10:
      lat = row['PlatiDES']
      long = row['PlongDES']
    else:
      lat = row['latitude']
      long = row['longitude']

    etalat = row[numlat]
    etalong = row[numlong]

    regticket_final.at[idx, hav] = haversine(lat, long, etalat, etalong)



# Filtrar las columnas que no contienen 'latitude' ni 'longitude'
regticket_final = regticket_final.loc[:, ~regticket_final.columns.str.contains('_latitude|_longitude|_fechahora')]

# Crear una lista de las columnas de interés en el orden deseado
columnas_ordenadas = []

# Iterar sobre el rango de etapas (de 5 a 10 en tu caso, o ajusta según sea necesario)
for etapa in range(5, 11):
    # Crear los nombres de las columnas para cada etapa
    etapas = [
        f"{etapa}_dup", 
        f"{etapa}_forma", 
        f"{etapa}_hav", 
        f"{etapa}_dif3"
    ]
    # Agregar las columnas en el orden adecuado
    columnas_ordenadas.extend(etapas)

# Asegúrate de incluir las demás columnas del DataFrame que no forman parte de las etapas
otras_columnas = [col for col in regticket_final.columns if col not in columnas_ordenadas]

# Crear el nuevo DataFrame con las columnas ordenadas
regticket_final = regticket_final[otras_columnas + columnas_ordenadas]

# agrego algunas columnas resumen
regticket_final['cuenta'] = regticket_final['fechahoraCAN'].apply(lambda x: 1 if pd.isnull(x) else 0)
# Verificar si alguna de las columnas 5_forma a 10_forma tiene el valor "Falta"
regticket_final['faltan'] = regticket_final[
    ['5_forma', '6_forma', '7_forma', '8_forma', '9_forma', '10_forma']
].apply(lambda row: 'falta' if 'Falta' in row.values else 'NO', axis=1)
# Verificar si alguna de las columnas 5_forma a 10_forma tiene el valor "Manual corto"
regticket_final['cortos'] = regticket_final[
    ['5_forma', '6_forma', '7_forma', '8_forma', '9_forma', '10_forma']
].apply(lambda row: 'corto' if 'Manual corto' in row.values else 'NO', axis=1)
regticket_final['bueno'] = ((regticket_final['faltan'] == 'NO') & (regticket_final['cortos'] == 'NO')).astype(int)

# Guardar el resultado en un nuevo archivo CSV
print("---------------------------------------------")
print("escribo tickets.csv")
regticket_final.to_csv('tickets.csv', index=False, sep=';', decimal=',')

