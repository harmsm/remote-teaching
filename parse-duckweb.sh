#!/bin/bash

duckweb_file="${1}"

grep -A1 "<tr>" "$duckweb_file" | grep CLASS | awk -F">" '{print $2}' | awk -F"<" '{print $1}' | sed 's/  //g' | awk -F"," '{print $1}' > last-name.tmp
grep -A1 "<tr>" "$duckweb_file" | grep CLASS | awk -F">" '{print $2}' | awk -F"<" '{print $1}' | sed 's/  //g' | awk -F"," '{print $2}' > first-name.tmp
grep HREF "$duckweb_file" | awk -F'\"' '{print $4}' | sed 's/mailto://' > email.tmp

echo "LastName,FirstName,PrimaryEmail"
paste -d"," last-name.tmp first-name.tmp email.tmp | sed 's/ ,/,/g' | sed 's/, /,/g' | sed 's/ \n/\n/'

rm -rf last-name.tmp first-name.tmp email.tmp 
