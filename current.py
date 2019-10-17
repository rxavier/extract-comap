import datetime as dt
import glob
import re

import camelot
import pandas as pd
from dateutil.relativedelta import relativedelta

pdf = sorted(glob.glob1("pdfs", "*.pdf"))[-1]

pars_row_tol = 4.5
pars_cols = ["228, 249, 473"]

ext_current = camelot.read_pdf(f"pdfs/{pdf}", flavor="stream", pages="1-end",
                               row_tol=pars_row_tol, columns=pars_cols)

table_list = []
for i in range(0, len(ext_current)):
    table_list.append(ext_current[i].df)

raw_data = pd.concat(table_list)

raw_data.iloc[:, 3] = raw_data.iloc[:, 3].str.replace(".", "")
first_row_index = raw_data[raw_data.iloc[:, 3].str.isnumeric()].index[0]
proc_data = raw_data.iloc[first_row_index:, :].reset_index(drop=True)

proc_data.columns = ["Empresa", "Sector",
                     "Actividad", "Inversión promovida (US$)"]

proc_data["Fecha"] = dt.datetime(
    int(re.search("[0-9]{4}", pdf).group(0)), 1, 1)

for i in range(1, len(proc_data)):
    if (re.match("Total", proc_data.iloc[i, 1], re.IGNORECASE) or
            re.match("Total", proc_data.iloc[i, 2], re.IGNORECASE)):
        (proc_data.iloc[i, 4] = proc_data.iloc[i - 1, 4] +
            relativedelta(months=1))
    else:
        proc_data.iloc[i, 4] = proc_data.iloc[i - 1, 4]

final_data = proc_data[~(proc_data.Sector.str.contains("Total", case=False) |
                         proc_data.Actividad.str.contains("Total", case=False))]

final_data.to_csv("Current data.csv", sep=" ", encoding="utf-8-sig")
