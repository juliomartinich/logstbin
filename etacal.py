# coding: utf-8
# construyo una base de tickets, para analizar como funciona ticklet a ticket

# --- chequeo de que la integracion funciona bien para la etapa 2 = Asignacion
# Identifica los valores de rsdn que contienen al menos una fila con orderSubType = "DLV"
# También puede ser "HOM", y estos no me interesan por ahora
rsdn_dlv = logord[logord['orderSubType'] == "DLV"]['rsdn'].unique()

# Filtra el DataFrame para incluir solo las filas con los rsdn identificados
logord_dlv = logord[logord['rsdn'].isin(rsdn_dlv)]
# Filtra el DataFrame para seleccionar solo las filas con etapanum=2
logord_etapanum2 = logord_dlv[logord_dlv['etapanum'] == 2]

# Define el rango de valores de orden que te interesa
orden_requerido = set(range(1, 6))

# Agrupa por rtruck y rsdn, y verifica si el conjunto de valores de orden contiene todos los valores requeridos
completitud_2 = (
    logord_etapanum2.groupby(['rtruck', 'rsdn'])['orden']
    .apply(lambda x: 'completo' if set(x) >= orden_requerido else 'incompleto')
    .reset_index(name='estado')
)

print("el resultado queda en completitud_2.csv")
print("-------------------------------------------")
completitud_2.to_csv("completitud_2.csv", sep=";", decimal=",", header=True, na_rep="", index=False)
#----

# Define el rango de interés
etapas_interes = set(range(5, 11))

# Función para verificar etapas
def verificar_etapas(grupo):
    etapas_presentes = set(grupo['etapanum']).intersection(etapas_interes)
    if etapas_interes - etapas_presentes:
        return 'falta'
    else:
        return 'bueno'

# Aplica la verificación para cada combinación de rtruck y rsdn
resultados_faltas = (
    logord1.groupby(['rtruck', 'rsdn'])
    .apply(verificar_etapas)
    .reset_index(name='faltas')
)

resultados_cortos = (
    logord1.groupby(['rtruck', 'rsdn'])['trans']
    .apply(lambda x: 'malo' if 'corto' in x.values else 'bueno')
    .reset_index(name='cortos')
)

resultados_combinados = resultados_faltas.merge(
    resultados_cortos,
    on=['rtruck', 'rsdn'],
    how='outer'  # Puedes usar 'inner' si solo deseas las coincidencias
)

resultados_cancel = (
    logord1.groupby(['rtruck', 'rsdn'])['etapanum']
    .apply(lambda x: 'cancelado' if 11 in x.values else 'nocancel')
    .reset_index(name='cancelados')
)

resultados_combinados2 = resultados_combinados.merge(
    resultados_cancel,
    on=['rtruck', 'rsdn'],
    how='outer'  # Puedes usar 'inner' si solo deseas las coincidencias
)

# Muestra el resultado
print("el resultado queda en malosbuenos.csv")
print("-------------------------------------------")
resultados_combinados2.to_csv("malosbuenos.csv", sep=";", decimal=",", header=True, na_rep="", index=False)



