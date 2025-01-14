import tabula
import pandas as pd
import numpy as np

def read_po(file):
    print('----' * 10)
    dfs = []
    tables = tabula.read_pdf(input_path=file, pages='all', multiple_tables=True, area=[255, 15, 593, 925])
    ### first page  ##########

    for df in tables:
        ### find column name of upc column
        upc_column = df.columns[df.iloc[0] == 'UPC'][0]
        df = df.rename(columns={'Style description / Vendor style': 'Product', 'Extended cost': 'Ext Cost',
                                'Unit cost': 'Unit Cost', 'Ordered qty': 'Qty',upc_column:'UPC'})
        if 'Product' not in df.columns:
            df = df.rename(columns={'Style description / Vendor style Expected rec date': 'Product'})

        df = df[['Product', 'Qty', 'Unit Cost', 'Ext Cost', 'Unit retail', 'UPC']].ffill()
        df = df[~df['Product'].isna()]
        df = df[df['Product'].str.match(r'^[A-Z0-9]{1,9}$')]
        df['Qty'] = df['Qty'].str.extract(r'(\d+\.?\d*)')
        df['Unit Cost'] = df['Unit Cost'].str.extract(r'(\d+\.?\d*)')
        df['Ext Cost'] = df['Ext Cost'].str.extract(r'(\d+\.?\d*)')

        df[['Qty', 'Unit Cost', 'Ext Cost']] = df[['Qty', 'Unit Cost', 'Ext Cost']].apply(pd.to_numeric,errors='coerce')
        dfs.append(df)
    return dfs



