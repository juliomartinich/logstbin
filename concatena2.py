# coding: utf-8
# inicio pruebas de cargar directo un excel y cambiar los nombres de variables acá
# 2024-oct-13 agrego logica para fleet en uno o dos archivos
import numpy as py
import pandas as pd

# leo todos los archivos
print("---------------------------------")
print("leo archivos log de syncrotess...")
synerpcli = pd.read_csv("erp_cli.csv", delimiter=";", index_col=False)
synerpser = pd.read_csv("erp_ser.csv", delimiter=";", index_col=False)
syntelcli = pd.read_csv("tel_cli.csv", delimiter=";", index_col=False)
syntelser = pd.read_csv("tel_ser.csv", delimiter=";", index_col=False)
synerpcli["fechahora"]= pd.to_datetime(synerpcli["fechahora"])
synerpser["fechahora"]= pd.to_datetime(synerpser["fechahora"])
syntelcli["fechahora"]= pd.to_datetime(syntelcli["fechahora"])
syntelser["fechahora"]= pd.to_datetime(syntelser["fechahora"])
# Imprimo min y max de fechas
min_fecha = synerpcli['fechahora'].min()
max_fecha = synerpcli['fechahora'].max()
print(f"synerpcli: desde {min_fecha} hasta {max_fecha}")
min_fecha = synerpser['fechahora'].min()
max_fecha = synerpser['fechahora'].max()
print(f"synerpser: desde {min_fecha} hasta {max_fecha}")
min_fecha = syntelcli['fechahora'].min()
max_fecha = syntelcli['fechahora'].max()
print(f"syntelcli: desde {min_fecha} hasta {max_fecha}")
min_fecha = syntelser['fechahora'].min()
max_fecha = syntelser['fechahora'].max()
print(f"syntelser: desde {min_fecha} hasta {max_fecha}")

syncrotesslogs= pd.concat([synerpcli, synerpser, syntelcli, syntelser], axis=0, ignore_index=True)
# las columnas orderNo y erpTicketNumber se cargan con decimales a pesar de ser enteros, y con NaN los valores nulos
# syncrotesslogs["orderNo"] = syncrotesslogs["orderNo"].apply(lambda x: str(int(x)) if not pd.isna(x) else "")
syncrotesslogs["orderNo"] = syncrotesslogs["orderNo"].apply(lambda x: str(int(x)) if pd.notna(x) and str(x).isdigit() else str(x) if pd.notna(x) else "")
syncrotesslogs["erpTicketNumber"] = syncrotesslogs["erpTicketNumber"].apply(lambda x: str(int(x)) if not pd.isna(x) else "")
syncrotesslogs["mseg"] = syncrotesslogs["mseg"].apply(lambda x: str(int(x)) if not pd.isna(x) else "")
syncrotesslogs["tiponum"] = syncrotesslogs["tiponum"].apply(lambda x: str(int(x)) if not pd.isna(x) else "")
syncrotesslogs["shipPoint"] = syncrotesslogs["shipPoint"].apply(lambda x: str(int(x)) if not pd.isna(x) else "")
syncrotesslogs["productId"] = syncrotesslogs["productId"].apply(lambda x: str(int(x)) if not pd.isna(x) else "")
syncrotesslogs["principalPlant"] = syncrotesslogs["principalPlant"].apply(lambda x: str(int(x)) if not pd.isna(x) else "")
syncrotesslogs["S"]="S"

print(" ")
print("leo archivo TrackIt.xls...")
# leo el archivo excel tal como viene, y renombro columnas
trackit   = pd.read_excel("LogTrackIt.xls", header=None)
trackit = trackit.iloc[5:]   # las primeras 5 filas las borro
trackit = trackit.reset_index(drop=True) # para que no empiece del 5
trackit.columns = ["truckId","descequipo","nrofunc","nombre","apellido","erpTicketNumber","trabajo","desctrabajo","planta","descplanta","nroestado","status","statusSource","fechahora","dura","ptoref","latitude","longitude","inserirtiempo","inserirtiempo2","inserirtiempo3","millas","fuel"]
trackit["log"] = "TR"
trackit["T"] = "T"
trackit["fechahora"]= pd.to_datetime(trackit["fechahora"])
trackit["latitude"] = trackit["latitude"].apply(lambda x: str(x).replace('.', ',') if pd.notna(x) else x)
trackit["longitude"] = trackit["longitude"].apply(lambda x: str(x).replace('.', ',') if pd.notna(x) else x)
# Imprimo min y max de fechas
min_fecha = trackit['fechahora'].min()
max_fecha = trackit['fechahora'].max()
print(f"trackit: desde {min_fecha} hasta {max_fecha}")

# fleet    = pd.read_csv("LogFleetTransaccional.csv", delimiter=";", index_col=False)
# si viene separado en dos, leo uno como fleet1 y otro como fleet2 y los concateno de inmediato en uno llamado fleet con concat
# fleet= pd.concat([fleet1, fleet2], axis=0, ignore_index=True)
# del fleet1
# leo el archivo excel tal como viene, y renombro columnas
print(" ")
print("leo archivo Fleet...")
try:
    fleet   = pd.read_excel("LogFleetTransaccional.xls", header=None)
    endos   = "NO"
    print("encontrado el LogFleetTransaccional.xls")
except FileNotFoundError as e:
    fleet   = pd.read_excel("LogFleetTransaccional_1.xls", header=None)
    print("asumo el LogFleetTransaccional_1.xls y _2")
    endos   ="SI"

fleet = fleet.iloc[2:]   # la primera fila la borro
fleet = fleet.reset_index(drop=True)# para que no empiece del 2
fleetasc = fleet.sort_index(ascending=False) # el archivo viene descendente, y lo quiero ascendente
fleet = fleetasc
del fleetasc

if endos == "SI":
    fleet_2   = pd.read_excel("LogFleetTransaccional_2.xls", header=None)
    fleet_2 = fleet_2.iloc[2:]   # la primera fila la borro
    fleet_2 = fleet_2.reset_index(drop=True)# para que no empiece del 2
    fleetasc_2 = fleet_2.sort_index(ascending=False)
    fleet_2 = fleetasc_2
    del fleetasc_2
    fleet = pd.concat([fleet, fleet_2], axis=0, ignore_index=True)

fleet.columns = ["fechahora","erpTicketNumber","truckId","SIGU","TRANSTYPE","TRANSSUBTYPE","statusSource","DESCRIPTION"]
fleet["status"] = "(" + fleet["TRANSTYPE"].astype(str) + ") (" + fleet["TRANSSUBTYPE"].astype(str) + ") " + fleet["DESCRIPTION"].astype(str)
fleet["fechahora"]= pd.to_datetime(fleet["fechahora"])
# Imprimo min y max de fechas
min_fecha = fleet['fechahora'].min()
max_fecha = fleet['fechahora'].max()
fleet["log"] = "F"
fleet["F"]   = "F"
print(f"fleet: desde {min_fecha} hasta {max_fecha}")

print(" ")
print("leo archivo Err Fleet...")
#errfleet= pd.read_csv("LogFleetErrors.csv", delimiter=";", index_col=False)
# leo el archivo excel tal como viene, y renombro columnas
errfleet   = pd.read_excel("LogFleetErrors.xls", header=None)
errfleet = errfleet.iloc[2:]   # la primera fila la borro
errfleet = errfleet.reset_index(drop=True) # para que no empiece del 2
errfleet.columns = ["fechahora","status","detail","truckId","erpTicketNumber"]
errfleet["fechahora"]= pd.to_datetime(errfleet["fechahora"])
fleetasc = errfleet.sort_index(ascending=False)
errfleet = fleetasc
del fleetasc
# Imprimo min y max de fechas
min_fecha = errfleet['fechahora'].min()
max_fecha = errfleet['fechahora'].max()
errfleet["log"] = "FE"
errfleet["F"]   = "F"
print(f"errfleet: desde {min_fecha} hasta {max_fecha}")

print("filtro los registros de fleet y errfleet a solo los camiones que contengan SIGU 99")
# de fleet obtengo los camiones que tienen TrackIt (SIGU 99), y borro lo anterior para ahorrar memoria
# hay que tener cuidado con el tipo de dato, al leer en csv lo lee numerico, pero en excel string
filtered_df = fleet[fleet['SIGU'] == '99']
unique_truckIds = filtered_df['truckId'].unique()
del filtered_df

# de fleet  errfleet obtengo todos los registros de esos camiones, sean registros con SIGU 99 o no
fleettrackit = fleet[fleet["truckId"].isin(unique_truckIds)]
del fleet
errfleettrackit = errfleet[errfleet["truckId"].isin(unique_truckIds)]
del errfleet
 
print(" ")
print("Concateno todos los registros")
#los concateno 
todosconcat= pd.concat([syncrotesslogs, trackit, fleettrackit, errfleettrackit], axis=0, ignore_index=True)
del syncrotesslogs
del trackit
del fleettrackit
del errfleettrackit
print(" ")
print("leo archivo Camiones.xls")
#camiones  = pd.read_csv("Camiones.csv", delimiter=";", index_col=False)
# leo el archivo excel tal como viene, y renombro columnas
camiones   = pd.read_excel("Camiones.xls", header=None)
camiones = camiones.iloc[2:]   # la primera fila la borro
camiones = camiones.reset_index(drop=True)
camiones.columns = ["truckId","planta","licensePlate","driver"]

print("agrego licensePlate a todos los truckid de acuerdo a la tabla de Camiones.xls")
# todosconcat.to_csv("concat.csv", sep=";", header=True, na_rep="")
# primero convierto todo truckId a string desde entero, o ""
todosconcat['truckId'] = todosconcat['truckId'].apply(lambda x: str(int(x)) if pd.notna(x) else "")
camiones['truckId'] = camiones['truckId'].apply(lambda x: str(int(x)) if pd.notna(x) else "")
# busco la patente de todos los que tengan truckId
merged_df = pd.merge(todosconcat, camiones, on="truckId", how="left", suffixes=("_orig", "_extra"))
merged_df['licensePlate'] = merged_df['licensePlate_orig'].combine_first(merged_df['licensePlate_extra'])
merged_df.drop(columns=['licensePlate_orig', 'licensePlate_extra'], inplace=True)
merged_df["fechahora"]= pd.to_datetime(merged_df["fechahora"])
#
# reordeno columnas
# Seleccionar las columnas que deseas reordenar primero
columns_to_move = ['log','fechahora','mseg','S','F','T','metodo','api','httpstatus','status','statusSource','truckId','licensePlate','SIGU','orderNo','erpTicketNumber','syncrotessDeliveryNumber','deliveryType','deliveryQuantity','nrofunc']

# Crear una lista con el resto de las columnas (sin las que quieres mover)
remaining_columns = [col for col in merged_df.columns if col not in columns_to_move]

# Combinar las columnas en el orden deseado
new_column_order = columns_to_move + remaining_columns

# Reordenar el DataFrame
df = merged_df[new_column_order].sort_values(by=["fechahora","mseg"])
del merged_df

# Exportar a CSV
print(" ")
print("el resultado queda en logconsolidado.csv")
print("---------------------------------")
df.to_csv('logconsolidado.csv', sep=';', quotechar='"', quoting=1, decimal=',', header=True, na_rep='')
