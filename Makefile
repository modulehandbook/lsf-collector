
.PHONY : fava med balances expenses med fava documents medical beihilfe
.RECIPEPREFIX = -


ba-courses:
- python json2csv/main.py ./data/2024-09-30-wise2024-bachelor.json -c -o output/bachelor-courses.csv

ba-studies:
- python json2csv/main.py ./data/2024-09-30-wise2024-bachelor.json -o output/bachelor-studies.csv



