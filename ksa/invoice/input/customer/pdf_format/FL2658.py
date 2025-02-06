import tabula
import re
import pandas as pd
import numpy as np

def currency_to_float(series):
    return pd.to_numeric(
        series.str.replace('[\$,]', '', regex=True),
        errors='coerce'
    )

def find_upc(row):
    pattern = r'(4\d{11})'

    for col in ['UPC1', 'UPC2', 'UPC3']:
        match = pd.Series(row[col]).str.extract(pattern, expand=False)
        if not match.isna().all():
            return match.iloc[0]  # Return the first match found
    return None  # Return None if no match is found
def read_po(file):
    dfs = []

    tables = tabula.read_pdf(input_path=file, pages='all', multiple_tables=True)
    tables = [tb for tb in tables if len(tb.columns)>3]
    if len(tables) <= 1:
        df = tables[0].copy()
        df = df.rename(columns={'ITEM NO.':'Product','QTY':'Qty','Unit Price':'Unit Cost','SubTotal':'Ext Cost'})
        df = df.loc[(df['Product'].notna())&((df['Unit Cost'].notna()))]
        df[['Qty','Unit Cost','Ext Cost']] = df[['Qty','Unit Cost','Ext Cost']].apply(currency_to_float)
        dfs.append(df)
        # print (df)
        return dfs
    else:
        print ('---'*10)
        print ('EDIT ')

