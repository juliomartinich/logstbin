#!/bin/bash
# filtra basado en patronesafiltrar.txt

grep -v -f patronesafiltrar.txt logenrich.csv > logenrichf.csv
