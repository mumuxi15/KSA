from .customer.pdf_format import MA0603, NV0356, FL4494
import tabula
import pandas as pd

def to_text(file):
    return 'hello'
def convert_to_numeric(df, filter_words):
        try:
            print (col, ' Convert to numeric')
            pd.to_numeric(df[col].str.replace(filter_words,''))
        except ValueError:
            print (col, ' NOOO')
            return False
def get_customer_id(file):
    return file.split('/')[-2]

def parse_ksa_order(file):
    "area = [3.5, 0.25, 9.1, 8.26] [top, left, bottom, right]"
    # Concatenate all tables into one DataFrame
    df = pd.concat(tabula.read_pdf(input_path=file, pages='all', multiple_tables=True,area=[250, 18, 655, 600]))
    assert 'Product' in df.columns, "pdf_format read pdf issue"
    df = df.dropna(how="all",axis=1)
    if 'Product' not in df.columns:
        df.rename(columns={'Unnamed: 0':'Product'},inplace=True)
    df = df.loc[df['Product'].notna()]
    return df

def parse_customer_order(file, customer_id, template=None):
    " return list of dataframe of each page"
    # tables = tabula.read_pdf(input_path=file, pages='all', multiple_tables=True)
    # dfs = []
    print('template: ', template)
    dfs = []

    if customer_id == 'MA0603':
        template = MA0603
        dfs = template.read_po(file)

    elif customer_id == 'NV0356':
        template = NV0356
        dfs = template.read_po(file)

    elif customer_id == 'FL4494':
        template = FL4494
        dfs = template.read_po(file)

    elif template == 'AZ1239':
        tables = tabula.read_pdf(input_path=file, pages='all', multiple_tables=True)
        tables[0] = tabula.read_pdf(input_path=file, pages='1', area=[414, 14.4, 575, 773])[0]
        for df in tables:
            df = df.rename(columns={'Vendor Part No':'Product','Order Cost':'Unit Cost'})
            object_cols = df.select_dtypes('object').columns
            df[object_cols] = df[object_cols].replace('EaOnly|,','', regex=True)
            num_cols = df[object_cols].apply(pd.to_numeric, errors='coerce').dropna(how="all",axis=1)
            df[num_cols.columns] = num_cols
            num_cols = df.select_dtypes(include=['int64','float64']).columns.to_list()
            ##  rename
            if 'Product' not in df.columns:
                col = df.columns[df.apply(lambda x: x.astype(str).str.match(r'^(?=.*[A-Z])(?=.*\d)(?!.*\.).*$')).any()][0]
                df = df.rename(columns={col:'Product'})

            df = df[['Product']+num_cols].dropna(how="all",axis=1)
            df = df.loc[df['Product'].notna()]
            if len(df.columns) ==4:
                df.columns = ['Product','Qty', 'Unit Cost', 'Ext Cost' ]
            dfs.append(df[['Product','Qty', 'Unit Cost', 'Ext Cost' ]])
        return dfs

    # elif template =='FL4494':
        # !!!!!!!!!!!!!!!!   SINGLE PAGE  !!!!!!!!!!!!!!!
        # tables[0] = tabula.read_pdf(input_path=file, pages='1', area=[226, 0, 540, 751], guess=False)[0]
        # df = tabula.read_pdf(input_path=file, pages='1', guess=True)
        # print (file)
        # tables = tabula.read_pdf(input_path=file, pages='all', multiple_tables=True)
        # df = tabula.read_pdf(input_path=file, pages='1', guess=True,area=[226, 0, 540, 751])[0]
        # # print (df)
        # if 'Description' not in df.columns:
        #     # print (df)
        #     i = df[df[df.columns[0]].str.contains('Description')==True]
        #     if 'Description' in df.columns[0]:
        #         df.columns = ['Description'] + list(df.columns[1::])
        #         print (df)
        #     else:
        #         print (df)
        #         print ('TRY CONVERT TO EXCEL ')
        #
        #     df.columns = i.values[0]
        #     df = df[i.index[0]+1:-1]
        # df.columns = ['Description','Product']+ list(df.columns[2:-1])+['Ext Cost']
        # df = df.loc[:, ~df.columns.duplicated()]
        # df.update(df['Product'].fillna(df['Description'].str.split().str[-1]))
        # df['UPC2'] = df['Product'].shift(-1)
        # df['UPC']  = df['Product'].shift(-2)
        # df['UPC'] = df['UPC'].where(df['UPC'].str.isnumeric(), df['UPC2'])
        # # df.columns = df.columns + np.vectorize(lambda x: '_2' if x else '')(df.columns.duplicated())
        # df = df[df['Product'].str.contains(r'(?=.*[A-Z])(?=.*\d)', regex=True)]
        #
        # df = df.rename(columns={'Pcs':'Qty','Cost':'Unit Cost'})
        # # to numeric
        # numeric_columns = ['Qty', 'Unit Cost', 'Ext Cost', 'Retail']
        # df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
        # dfs.append(df[['Product', 'Description', 'Qty', 'Unit Cost', 'Ext Cost', 'Retail', 'UPC']])

    elif template=='PA1683':
        tables = tabula.read_pdf(input_path=file, pages='all', multiple_tables=True)
        for df in tables:
            if len(df)>0:
                df = df[['SUPPLIER #', 'QTY', 'PRICE/UN', 'AMOUNT']] #
                df.columns = ['Product','Qty','Unit Cost','Ext Cost']
                # df['Product'] = df['Product'].str[2::]
                df.update(df['Unit Cost'].str.replace('$',''))
                df.update(df['Ext Cost'].str.replace('$','').str.replace(',', ''))
                df[['Unit Cost', 'Ext Cost']] = df[['Unit Cost', 'Ext Cost']].apply(pd.to_numeric, errors='coerce').dropna(how="all",axis=1)
                df = df.loc[~df['Product'].isna()]
                df = df.loc[~df['Qty'].isna()]
                dfs.append(df)
        return dfs

    else:
        print (template, '  parse_customer_order()  pdf_format not defined yet')

    ### all return dfs ######
    return dfs

