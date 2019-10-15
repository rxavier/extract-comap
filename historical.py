import datetime as dt
import glob
import re

import camelot
import openpyxl
import pandas as pd
from dateutil.relativedelta import relativedelta
from openpyxl.utils.dataframe import dataframe_to_rows

pdfs = sorted(glob.glob1("pdfs", "*.pdf"))[3:-1]
pars_row_tol = [5.8, 5.8, 5.8, 5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 5]
pars_cols = [["207, 251, 426"],
             None,
             ["223, 278, 497"],
             ["190, 215, 436"],
             ["186, 220, 423"],
             ["240, 270, 483"],
             ["240, 270, 483"],
             ["239, 272, 514"],
             ["242, 274, 513"],
             ["241, 272, 498"],
             ["719, 810, 1640"]]
pdfs_dict = dict(zip(pdfs, zip(pars_row_tol, pars_cols)))

extracted_data = {}
workbook = openpyxl.Workbook()
for filename, parameters in pdfs_dict.items():

    ext_tables = camelot.read_pdf(filename, flavor="stream", pages="1-end",
                                  row_tol=parameters[0], columns=parameters[1])

    table_list = []
    for i in range(0, len(ext_tables)):
        table_list.append(ext_tables[i].df)

    raw_data = pd.concat(table_list)

    raw_data.iloc[:, 3] = raw_data.iloc[:, 3].str.replace(".", "")
    first_row_index = raw_data[raw_data.iloc[:, 3].str.isnumeric()].index[0]
    proc_data = raw_data.iloc[first_row_index:, :].reset_index(drop=True)

    proc_data.columns = ["Empresa", "Sector",
                         "Actividad", "Inversión promovida (US$)"]

    proc_data["Fecha"] = dt.datetime(
        int(re.search("[0-9]{4}", filename).group(0)), 1, 1)
    for i in range(1, len(proc_data)):
        if (re.match("Total", proc_data.iloc[i, 1], re.IGNORECASE) or
                re.match("Total", proc_data.iloc[i, 2], re.IGNORECASE)):
            (proc_data.iloc[i, 4] = proc_data.iloc[i - 1, 4] +
                relativedelta(months=1))
        else:
            proc_data.iloc[i, 4] = proc_data.iloc[i - 1, 4]

    final_data = proc_data[~(proc_data.Sector.str.contains("Total", case=False) |
                             proc_data.Actividad.str.contains("Total", case=False))]

    extracted_data.update({filename: final_data})
    ws = workbook.create_sheet(title=filename)
    for r in dataframe_to_rows(final_data, index=True, header=True):
        ws.append(r)

workbook.save("Historical data.xlsx")
