from .customer.pdf_format import MA0603, NV0356, FL4494, FL2658
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

def parse_customer_order(file, customer_id):
    " return list of dataframe of each page"
    # tables = tabula.read_pdf(input_path=file, pages='all', multiple_tables=True)
    # dfs = []
    dfs = []

    template_map =  {
    'MA0603': MA0603,
    'NV0356': NV0356,
    'FL4494': FL4494,
    'FL2658': FL2658,
    }
    template = template_map.get(customer_id)
    if template:
        dfs = template.read_po(file)
    else:
        raise ValueError('Unknown customer ID template not found', customer_id)

    if template == 'AZ1239':
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

    ### all return dfs ######
    return dfs

