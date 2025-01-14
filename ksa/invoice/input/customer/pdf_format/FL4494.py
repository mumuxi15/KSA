import tabula
import re
import pandas as pd
import numpy as np
def find_upc(row):
    pattern = r'(4\d{11})'

    for col in ['UPC1', 'UPC2', 'UPC3']:
        match = pd.Series(row[col]).str.extract(pattern, expand=False)
        if not match.isna().all():
            return match.iloc[0]  # Return the first match found
    return None  # Return None if no match is found
def read_po(file):
    print('----' * 10)
    print (file)
    dfs = []

    tables = tabula.read_pdf(input_path=file, pages='all', multiple_tables=True)
    if len(tables) <= 1:
        df = tables[0].copy()
        col_y = df.iloc[0]
        col = [re.sub(r'[.0-9/]','',c) for c in df.columns]
        col = [col[i]+' '+col_y.iloc[i] for i in range(len(col))]
        if 'Description' in col[0]:
            col[0] = 'Description'
        else:
            raise TypeError('Description Column Not Found, TRY CONVERT TO EXCEL ')
        df.columns = col
        df = df[1::]
        df['Product'] = df['Description'].str.split().str[-1].str.replace('-','')
        df['UPC1'] = df['Product'].shift(-1).str.extract(r'(\d+)').fillna('')
        df['UPC2'] = df['Product'].shift(-2).str.extract(r'(\d+)').fillna('')
        df['UPC3'] = df['Product'].shift(-3).str.extract(r'(\d+)').fillna('')
        df['UPC'] = df[['UPC1','UPC2','UPC3']].apply(lambda x: max(x,key=len), axis=1)
        # df['Product'] = df['Product'].str.extract(r'([A-Z0-9]+)', expand=False)  # Keep only uppercase letters and numbers
        df = df[df['Product'].str.contains(r'\b[A-Z][A-Z0-9]+$', na=False)]
        df = df[['Description', 'Unit Retail', 'Unit Cost', 'Ord Pcs', 'Extended Cost', 'Product', 'UPC']]
        df = df.rename(columns={'Ord Pcs':'Qty', 'Extended Cost':'Ext Cost'})
        df[['Qty', 'Unit Cost', 'Ext Cost']] = df[['Qty', 'Unit Cost', 'Ext Cost']].apply(pd.to_numeric, errors='coerce')
        dfs.append(df)
        # print (df)
        return dfs

