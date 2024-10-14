
.PHONY : fava med balances expenses med fava documents medical beihilfe
.RECIPEPREFIX = -

input=data/2024-10-09-wise2024-bachelor.json
ba-courses:
- python json2csv/main.py ${input} -c -o output/bachelor-courses.csv

ba-studies:
- python json2csv/main.py ${input} -o output/bachelor-studies.csv

inputm=data/2024-10-09-wise2024-master.json
ma-courses:
- python json2csv/main.py ${inputm} -c -o output/master-courses.csv


inputf4=data/2024-10-09-wise2024-fb4.json
f4-courses:
- python json2csv/main.py ${inputf4} -c -o output/f4-courses.csv

f4-studies:
- python json2csv/main.py ${inputf4}  -o output/f4-studies.csv

