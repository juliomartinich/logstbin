#!/bin/bash
#se llama con parametros dia y mes del log desde donde está
#los archivos deben estar en un directorio al mismo nivel de bintest
# .../bin/full_log.sh 29 10    -- para el día 29 del mes 10

# Verifica si se ha pasado un argumento
if [ $# -eq 0 ]; then
    echo "Uso: $0 <número>"
    exit 1
fi

# Asignar el argumento a una variable
nro=$1
mes=$2

cp ../bin/archivosbase/* .

../bin/genlogs.sh $nro

echo "concatena los archivos de log ..."
python3 ../bin/concatena2.py

echo "enriquece ..."
python3 ../bin/enrich.py

../bin/filtragpsoauth.sh

python3 ../bin/tetapa.py

python3 ../bin/exttick.py

cp logetapa.csv logetapa_$mes$nro.csv
cp logetapa1.csv logetapa1_$mes$nro.csv
cp tickets.csv tickets_$mes$nro.csv

echo "transporta a Dropbox"
cp *$mes$nro.csv /Users/stjepan/Dropbox/clientesJMInext/Polpaico/04_INTERMEDIOS/cronos/logs
