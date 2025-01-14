import tabula
import pandas as pd
import numpy as np

def read_po(file):
    print('----' * 10)
    print (file)
    dfs = []
    df = tabula.read_pdf(input_path=file, pages='1', multiple_tables=True, area=[150, 0, 550, 792])[0]
    ########  first page is different  ##############
    df.columns = df.iloc[0]
    dfs.append(df[1::])

    #
    # print (df.columns)
    # print(df.loc[df['UPC-A/EAN'].notna()])

    tables = tabula.read_pdf(input_path=file, pages='all', multiple_tables=True,area=[142, 0, 550, 792])[1::]
    print (len(tables))
    for df in tables:
        df.columns = ['DESCRIPTION' if 'DESCRIPTION' in col else col for col in df.columns]
        ds = df.select_dtypes(include=['object']).stack()
        retail =ds[ds.str.contains('UNIT RETAIL')].index.get_level_values(1)[0]
        df['Retail'] = df[retail].shift(-2) #.str.split(' ').str[0]
        df = df.loc[df['UPC-A/EAN'].notna()]
        print (df)
        print ('===='*20)
        # print (df)

        tables = tabula.read_pdf(input_path=file, pages='all', multiple_tables=True, area=[255, 15, 593, 925])
        for df in tables:
            df = df.rename(columns={'Style description / Vendor style': 'Product', 'Extended cost': 'Ext Cost',
                                    'Unit cost': 'Unit Cost', 'Ordered qty': 'Qty', 'Unnamed: 1': 'UPC'})
            if 'Product' not in df.columns:
                df = df.rename(columns={'Style description / Vendor style Expected rec date': 'Product'})

            df = df[['Product', 'Qty', 'Unit Cost', 'Ext Cost', 'Unit retail', 'UPC']].fillna(method='ffill')
            df = df[~df['Product'].isna()]
            df = df[df['Product'].str.match(r'^[A-Z0-9]{1,9}$')]

            df['Qty'] = df['Qty'].str.extract(r'(\d+\.?\d*)')
            df['Unit Cost'] = df['Unit Cost'].str.extract(r'(\d+\.?\d*)')
            df['Ext Cost'] = df['Ext Cost'].str.extract(r'(\d+\.?\d*)')
            df[['Qty', 'Unit Cost', 'Ext Cost']] = df[['Qty', 'Unit Cost', 'Ext Cost']].apply(pd.to_numeric,
                                                                                              errors='coerce')
            dfs.append(df)
        return dfs

