#!/bin/bash
#se llama con parametro el nro de dia que aparece en el log y opcionalmente el huso horario (UTC o CLT)
# ./genlogs.sh 9 CLT   -- para el día 9 con hora CLT

# Verifica si se ha pasado un argumento
if [ $# -eq 0 ]; then
    echo "Uso: $0 <número> [huso_horario (UTC o CLT)]"
    exit 1
fi

# Asignar el argumento a una variable
nro=$1
tz=${2:-UTC}

# Llamar al script gawk con el número pasado como argumento
gawk -v tz=$tz -f ../bin/glee_tel_cli.awk sttTelematicClient_developer.log.$nro > tel_cli.csv
gawk -v tz=$tz -f ../bin/glee_tel_ser.awk sttTelematicServer_developer.log.$nro > tel_ser.csv
gawk -v tz=$tz -f ../bin/glee_erp_cli.awk syncroTessErpClient_developer.log.$nro > erp_cli.csv
gawk -v tz=$tz -f ../bin/glee_erp_ser.awk syncroTessErpServer_developer.log.$nro > erp_ser.csv

