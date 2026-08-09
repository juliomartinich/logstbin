#!/bin/bash
#se llama con parametro el nro de dia que aparece en el log
# ./genlogs.sh 9    -- para el día 9

# Verifica si se ha pasado un argumento
if [ $# -eq 0 ]; then
    echo "Uso: $0 <número>"
    exit 1
fi

# Asignar el argumento a una variable
nro=$1

# Llamar al script gawk con el número pasado como argumento
gawk -f ../bintest/glee_tel_cli.awk sttTelematicClient_developer.log.$nro > tel_cli.csv
gawk -f ../bintest/glee_tel_ser.awk sttTelematicServer_developer.log.$nro > tel_ser.csv
gawk -f ../bintest/glee_erp_cli.awk syncroTessErpClient_developer.log.$nro > erp_cli.csv
gawk -f ../bintest/glee_erp_ser.awk syncroTessErpServer_developer.log.$nro > erp_ser.csv

