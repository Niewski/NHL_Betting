import openpyxl
from pathlib import Path 

xlsx_file = Path('Excel Data', '2020-21', 'Summary.xlsx')
wb_obj = openpyxl.load_workbook(xlsx_file)
sheet = wb_obj.active

i = 0
for row in sheet.iter_rows(1, 1, values_only=True):
    for col in row:
        print(col, " : ", i)
        i = i + 1
