# coding: utf-8
# inicio pruebas de cargar directo un excel y cambiar los nombres de variables acá
# 2024-oct-13 lógica para cambiar el returnRun como estado, y dejar en rsdn el ticket original
#             perfecciono la columna estado
#         -14 agrego un campo etapa a partir de un archivo excel etapasS.xls
import numpy as py
import pandas as pd
import sys

def convert_to_int64(value):
    try:
        # Intenta convertir a int y luego a Int64
        return pd.Series([int(value)], dtype="Int64")[0]
    except (ValueError, TypeError):
        # Si no es un número, devuelve el valor original
        return value

# leo todos los archivos, la primera columna trae el indice que se exportó, lo renombro como ID
log = pd.read_csv("logconsolidado.csv", delimiter=";", low_memory=False, index_col=0)
log.reset_index(inplace=True)
log.rename(columns={'index': 'ID'}, inplace=True)

log['rtruck'] = ''
license_to_truck = {}

print("-------------------------------------------")
print("1. completo rtruck a partir de licensePlate")
for i in range(len(log)):
    # obtengo los valores de la fila actual
    license_plate = log.at[i, 'licensePlate']
    truck_id = log.at[i, 'truckId']
    log.at[i, 'rtruck'] = truck_id
    if pd.notna(license_plate) and license_plate != "":            # si existe el valor
       if pd.notna(truck_id) and truck_id != "":              # si viene un valor, lo guardo en el diccionario
           license_to_truck[license_plate] = truck_id
       elif license_plate in license_to_truck:                # si license_plate ya está en el diccionario, lo uso
           log.at[i, 'rtruck'] = license_to_truck[license_plate]

# 2da pasada
print(" 2da pasada")
for i in range(len(log)):
    # obtengo los valores de la fila actual
    license_plate = log.at[i, 'licensePlate']
    truck_id = log.at[i, 'truckId']
    r_truck = log.at[i,'rtruck']
    if ( pd.notna(license_plate) and license_plate in license_to_truck ) and ( pd.isna(r_truck) or r_truck == "" ):
        log.at[i, 'rtruck'] = license_to_truck[license_plate]
        
# diccionario syncrotessDeliveryNumber a rtruck
# todo lo que venga con sdn y no tenga rtruck, le pongo el rtruck de la lista que se construye a partir de telcli assignment
print("2. lleno rtruck a partir del valor de assignment")
sdn_to_rtruck = {}
for i in range(len(log)):
    rtruck   = log.at[i, 'rtruck']
    sdn      = log.at[i, 'syncrotessDeliveryNumber']
    if sdn != "SignOff" and pd.notna(sdn) and sdn != "":
        if log.at[i,'log'] == 'STo' and log.at[i, 'api'] == '/webservices/telematics/assignment':
            sdn_to_rtruck[sdn] = rtruck
        elif log.at[i,'log'] == 'STi' and log.at[i, 'api'] == '/webservices/telematics/deliveryState' and ( pd.isna(rtruck) or rtruck == "" ) and sdn in sdn_to_rtruck:
            log.at[i, 'rtruck'] = sdn_to_rtruck[sdn]
# diccionario truckId a syncrotessDeliveryNumber
truck_to_sdn = {}
log['rsdn'] = ''
# diccionarios rsdn a erpTicketNumber y truck
rsdn_to_ticket = {}
rsdn_to_truck  = {}
log['rticket'] = ''
print("3. lleno rsdn con syncrotes delivery number de la asignación")
for i in range(len(log)):
    truck_id = log.at[i, 'truckId']
    sdn      = log.at[i, 'syncrotessDeliveryNumber']
    log.at[i, 'rsdn'] = sdn
    if log.at[i,'log'] == 'SEo' and log.at[i, 'api'] == '/webservices/erp/delivery/assignment':
       # a partir de aca el camion tiene el syncrotessDeliveryNumber y la orderNo hasta que cambie
       truck_to_sdn[truck_id] = sdn
       rsdn_to_truck[sdn] = truck_id
       log.at[i,'rsdn'] = sdn
    # pongo en la columna rsdn el valor almacenado de ese camion (el camion está asignado a ese sdn)
    # si es que el camion tiene valor, y el sdn esta vacio
    if pd.notna(truck_id) and pd.isna(sdn) and truck_id in truck_to_sdn:
       log.at[i, 'rsdn'] = truck_to_sdn[truck_id]
    # si en la fila tengo rsdn, y no tengo truck, lo lleno (si tengo el valor de sdn en rsdn_to_truck
    rsdn = log.at[i, 'rsdn']
    r_truck = log.at[i, 'rtruck']
    if pd.notna(rsdn) and pd.isna(r_truck) and rsdn in rsdn_to_truck:
       log.at[i, 'rtruck'] = rsdn_to_truck[rsdn]

# si el syncrotessDeliveryNumber termina en returnRun, pongo RR en assignment y delivery, y limpio de _returnRun el sdn en rsdn
print("4. si el delivery number termina en _returnRun pongo sufijo RR al assignment y al delivery")
for i in range(len(log)):
    sdn      = log.at[i, 'syncrotessDeliveryNumber']
    apisola  = log.at[i, 'apisola']
    # si el assignment tiene erpTicketNumber entonces es la asignación cargado (LD)
    if pd.notna(log.at[i, 'erpTicketNumber']) and log.at[i, 'apisola'] == "assignment":
      log.at[i, 'apisola'] = apisola + "LD"
    if pd.notna(sdn):
      if sdn.endswith('_returnRun'):
        log.at[i, 'apisola'] = apisola + "RR"
        log.at[i, 'rsdn'] = sdn[:-len('_returnRun')]


# debo hacer el ultimo paso de agrupar los rtruck, license_plate; y repasar aquellos license_plate que no tienen rtruck
print("5. hago un group by de licensePlate y rtruck, y lo uso para rellenar el truck vacio")

# Filtrar las filas donde license_plate no sea nulo ni esté en blanco
filtered_log = log[log['licensePlate'].notna() & (log['licensePlate'].str.strip() != '')]
# Agrupar por las columnas license_plate, truckId y rtruck, y obtener valores distintos
trucks = filtered_log.groupby(['licensePlate', 'rtruck']).size().reset_index().drop(columns=0)
# Realizar un merge entre log y trucks basado en licensePlate
log_updated = log.merge(trucks[['licensePlate', 'rtruck']], on='licensePlate', how='left', suffixes=('', '_trucks'))
# Rellenar rtruck en log con rtruck de trucks donde esté vacío
log_updated['rtruck'] = log_updated['rtruck'].fillna(log_updated['rtruck_trucks'])
# Eliminar la columna auxiliar creada en el merge
log_updated.drop(columns=['rtruck_trucks'], inplace=True)
log = log_updated

print("6. hago un group by de rsdn y rtruck, y lo uso para rellenar el truck vacio")

# Filtrar las filas donde rsdn no sea nulo ni esté en blanco
filtered_log = log[log['rsdn'].notna() & (log['rsdn'].str.strip() != '') & (log['rsdn'].str.strip() != 'SignOff') ]
# Agrupar por las columnas license_plate, truckId y rtruck, y obtener valores distintos
trucks_rsdn = filtered_log.groupby(['rsdn', 'rtruck']).size().reset_index().drop(columns=0)
# Realizar un merge entre log y trucks basado en licensePlate
log_updated = log.merge(trucks_rsdn[['rsdn', 'rtruck']], on='rsdn', how='left', suffixes=('', '_trucks'))
# Rellenar rtruck en log con rtruck de trucks donde esté vacío
log_updated['rtruck'] = log_updated['rtruck'].fillna(log_updated['rtruck_trucks'])
# Eliminar la columna auxiliar creada en el merge
log_updated.drop(columns=['rtruck_trucks'], inplace=True)
log = log_updated

print("7. pinto rsdn a partir de sdn, cuando erpTicketNumber sea igual")

# Filtrar filas donde erpTicketNumber ni syncrotessDeliveryNumber sea nulo ni vacío
df_filtrado = log[log['erpTicketNumber'].notna() & (log['erpTicketNumber'] != '') &
                  log['syncrotessDeliveryNumber'].notna() & (log['syncrotessDeliveryNumber'] != '')]
# Crear un diccionario de correspondencia erpTicketNumber -> syncrotessDeliveryNumber
mapa_erp_sync = dict(zip(df_filtrado['erpTicketNumber'], df_filtrado['syncrotessDeliveryNumber']))
# Actualizar rsdn solo cuando está nulo o en blanco
log.loc[log['rsdn'].isna() | (log['rsdn'] == ''), 'rsdn'] = log['erpTicketNumber'].map(mapa_erp_sync)

print("8. pinto rtruck a partir de truckId, cuando erpTicketNumber sea igual")
# Filtrar filas donde erpTicketNumber y truckId no sean nulos ni vacíos
df_filtrado = log[log['erpTicketNumber'].notna() & (log['erpTicketNumber'] != '') & 
                  log['truckId'].notna() & (log['truckId'] != '')]
# Crear un diccionario de correspondencia erpTicketNumber -> truckId
mapa_erp_truck = dict(zip(df_filtrado['erpTicketNumber'], df_filtrado['truckId']))
# Actualizar rtruck solo cuando está nulo o en blanco
log.loc[log['rtruck'].isna() | (log['rtruck'] == ''), 'rtruck'] = log['erpTicketNumber'].map(mapa_erp_truck)


print("9. pinto rtruck a partir de rtruck, rsdn, cuando rsdn sea igual y no sea SignOff")
# Filtrar filas donde rsdn y rtruck no sean nulos ni vacíos, y rsdn no sea "SignOff"
df_filtrado = log[(log['rsdn'].notna()) & (log['rsdn'] != '') & (log['rsdn'] != 'SignOff') & 
                  (log['rtruck'].notna()) & (log['rtruck'] != '')]
# Crear un diccionario de correspondencia rsdn -> rtruck
mapa_rsdn_rtruck = dict(zip(df_filtrado['rsdn'], df_filtrado['rtruck']))
# Actualizar rtruck solo cuando está nulo o en blanco y tenga el mismo rsdn
log.loc[(log['rtruck'].isna() | (log['rtruck'] == '')) & log['rsdn'].isin(mapa_rsdn_rtruck), 'rtruck'] = log['rsdn'].map(mapa_rsdn_rtruck)

# Concatenar apisola y status, agregando un espacio antes del status si no es NaN
#log['estado'] = ( log['log'].fillna('')
                #+ log['apisola'].apply(lambda x: f"-{x}" if pd.notna(x) else '') 
                #+ log['status'].apply(lambda x: f"-{x}" if pd.notna(x) else '') 
                #+ log['statusSource'].apply(lambda x: f"-{x}" if pd.notna(x) else '') 
                #+ log['deliveryType'].apply(lambda x: f"-{x}" if pd.notna(x) else '')
                #+ log['httpstatus'].apply(lambda x: f"-{x[:3]}" if isinstance(x, str) else x)
                #)
                #+ log['httpstatus'].str[:3].apply(lambda x: f"-{x}" if pd.notna(x) else '')

log['estado'] = (
    log['log'].fillna('') +
    log['apisola'].apply(lambda x: f"-{x}" if pd.notna(x) else '') +
    log['status'].apply(lambda x: f"-{x}" if pd.notna(x) else '') +
    log['statusSource'].apply(lambda x: f"-{x}" if pd.notna(x) else '') +
    log['deliveryType'].apply(lambda x: f"-{x}" if pd.notna(x) else '') +
    log['httpstatus'].apply(lambda x: f"-{str(x)[:3]}" if pd.notna(x) and isinstance(x, str) else '')
)

# agrego el campo etapa
print("10. pongo las etapas del archivo de etapas")
env = sys.argv[1] if len(sys.argv) > 1 else None
if env == 'test':
    etapas_file = "etapas_test.xls"
elif env == 'prod':
    etapas_file = "etapas_prod.xls"
else:
    etapas_file = "etapas.xls"

etapas = pd.read_excel(etapas_file, dtype={"orden": "Int64"})

# intento descubrir que columna tiene el problema de tipo de datos (3-ago-26)
columnas_join = ['log', 'apisola', 'status', 'deliveryType']

print("Tipos en log:")
print(log[columnas_join].dtypes)

print("\nTipos en etapas:")
print(etapas[columnas_join].dtypes)

# convierto a string

log["deliveryType"] = (
    log["deliveryType"]
    .astype("string")
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
)

etapas["deliveryType"] = (
    etapas["deliveryType"]
    .astype("string")
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
)

# Realizar el join entre logord y etapas usando las columnas log, apisola, status y deliveryType
log_merged = pd.merge(log, etapas[['log', 'apisola', 'status', 'deliveryType', 'etapa','orden']],
                         on=['log', 'apisola', 'status', 'deliveryType'],
                         how='left')  # 'left' mantiene todas las filas de logord

log_merged["orden"] = log_merged["orden"].astype("Int64")
log_merged["rtruck"] = log_merged["rtruck"].astype("Int64")
log_merged["truckId"] = log_merged["truckId"].astype("Int64")
log_merged["erpTicketNumber"] = log_merged["erpTicketNumber"].apply(convert_to_int64)

columns_to_move = ['ID', 'log','fechahora','orden','etapa','estado','rtruck','truckId','erpTicketNumber','orderSubType','rsdn','syncrotessDeliveryNumber','detail','shipPoint','locationID','deliveryQuantity','reuseQuantity','reasonCode','nrofunc','licensePlate','metodo','api','apisola','httpstatus','status','statusSource', 'deliveryType']
remaining_columns = [col for col in log.columns if col not in columns_to_move]
new_column_order = columns_to_move + remaining_columns

logord = log_merged[new_column_order]

# rtruck decimal point is comma
#print("cambio punto decimal por coma en rtruck")
#logord['rtruck'] = logord['rtruck'].apply(lambda x: x.replace('.', ',') if isinstance(x, str) and x else x)


print("el resultado queda en logenrich.csv")
print("-------------------------------------------")
logord.to_csv("logenrich.csv", sep=";", decimal=",", header=True, na_rep="", index=False)

