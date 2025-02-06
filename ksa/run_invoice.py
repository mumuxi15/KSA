import os
import glob
import sqlite3
import pandas as pd
import gspread
from datetime import datetime
from config.env import env, PATH, ROUNDING_ERROR
from invoice import extract_data
from query import query_search, query_direct
from shipping import send_price_request
from config.contacts import *

pd.set_option('display.max_columns',10)
def function1():
    return "Hello from function1 in module1"

def get_supplier_emails():
    """ GET SUPPLIER EMAIL FROM GSHEET  """
    gc = gspread.service_account(filename=PATH['gsheet_key'])
    sh = gc.open_by_key(env("SUPPLIER_WORKSHEET_KEY"))
    df = pd.DataFrame(sh.get_worksheet(0).get_all_records())

    # Save DataFrame to SQLite table
    conn = sqlite3.connect(PATH['db_path'])
    df[['SUPPLR', 'EMAIL']].to_sql('supplier', conn, index=False, if_exists='replace')
    # Close the connection
    conn.close()
    print ('====   SUPPLIER CONTACTS UPDATED IN LOCAL DB !  ===== ')
    return

def excel_to_sqlite(excel_file, table_name, db_file):
    # everytime save to db, record history.
    # Read Excel file into a pandas DataFrame
    if excel_file.endswith('.xlsx'):
        df = pd.read_excel(excel_file)
    elif excel_file.endswith('.csv'):
        df = pd.read_csv(excel_file)
    conn = sqlite3.connect(db_file)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print(f"Excel file '{excel_file}' has been successfully converted to SQLite database '{db_file}'")


def get_ksa_filepath(po):
    p = f"{PATH['so_folder']}{po['customer_id']}"
    dummy_file = [glob.glob(rf"{p}/[oO]rder_[cC]onfirmation_[pP]{co[1::]}.*")[0] for co in po['dummy']]
    customer_file = [glob.glob(rf"{p}/[oO]rder_[cC]onfirmation_[pP]{co[1::]}.*")[0] for co in po['customer']]
    assert len(customer_file) == len(po['customer']), "can not read all customer files"
    return (dummy_file, customer_file)

def get_customer_code(customer_id):
    "  find company prefix for customer_id "
    conn = sqlite3.connect(PATH['database'])
    query = rf"SELECT CODE FROM customer WHERE customer = '{customer_id}'"
    code = pd.read_sql_query(query, conn).values[0][0]
    return code
def check_dummy_qty(po, customer_id=None):
    "dummy po - a string, customer po - list"
    if 'customer_id' not in po.keys():
        p = rf"{gb.PATH['so_folder']}/*/order_confirmation_[pP]{po["dummy"][0][1::]}.*"
        po['customer_id'] = glob.glob(p)[0].split("\\")[-2]
    dummy_file, customer_file = get_ksa_filepath(po)
    # print (dummy_file)
    # print (customer_file)
    dummy_file = dummy_file[0]
    du = extract_data(file=dummy_file).rename(columns={"Ordered":"Dummy_Qty","Quantity":"Dummy_Qty"})
    df = pd.concat([extract_data(file=c).rename(columns={"Quantity":"Ordered"}) for c in customer_file])
    # check only items begin with 'Y'
    df = df.loc[df['Product'].str[0] == "Y"]
    code = get_customer_code(po['customer_id'])
    df["Product"] = df["Product"].str.replace(f"Y{code}", "")

    df = df.groupby(by="Product").agg({'Ordered': 'sum'})
    du = du.groupby(by="Product").agg({'Dummy_Qty': 'sum'})
    #
    df = pd.concat([du, df], join="outer", axis=1)
    df['Flag'] = (df["Ordered"] != df["Dummy_Qty"]) * 1
    if len(df.loc[df['Flag']==1]) > 1:
        df.sort_values(by='Flag',ascending=False).to_csv(f'keli_{customer_id}.csv')
        print (df)
    else:
        print ('FINISHED, EVERYTHING IS CORRECT !! ')
    return df

class NewOrder:
    def __init__(self, **kwargs):
        for key, value in kwargs['po'].items():
            setattr(self, key, value)
        return
    def read_customer_po(self, file):
        "read customer orders from special order folders;"
        path = PATH['so_folder']+self.customer_id+'/'
        return extract_data(f"{path}{file}", template=self.customer_id)
    def read_customer_price(self):
        """1. download newest inventory report
           2. merge based on Product_id
           3. calculate price and flag difference
        """
        for k, order in self.orders.items():
            df = pd.concat(self.read_customer_po(order['customer']))
            df['ticket'] = self.ticket
            # if 'updates' in order:
            #     for item_id, v in order['updates'].items():
            #         for col, value in v.items():
            #             df.loc[df['Product'] == item_id, col] = value
            #             print('updated ', item_id, col, value)
            quoted_items ='(' + ','.join([f"'{item}'" for item in df['Product'].values])+ ')'
            query = query_search(target='inventory', item_tuple=quoted_items) # read_inventory from dbo
            print (query)
            df = pd.merge(df, query, how='left', left_on='Product', right_on='Item')
            if len(df.loc[df['Status'].isna()])>0:
                print (df.loc[df['Status'].isna()])
                df = df.loc[~df['Status'].isna()]

            if len(df.loc[df['Qty']>df['NETAVAIL']])>0:
                print ('----'*5,'NET AVAILABLE ERROR :   QTY WANTED > AVAILABLE ','----'*5)
                print (df.loc[df['Qty']>df['NETAVAIL']])
            print (df)
            df['caseflag'] = df['Qty'].astype(int) % df['CaseQty'].astype(int)
            df.loc[df['caseflag'] == 0, 'No.Case'] = df.loc[df['caseflag'] == 0, 'Qty'] // df.loc[df['caseflag'] == 0, 'CaseQty']
            df['Price'] = (df.apply(lambda x: x['CasePrice'] * (1 - self.discount) + x['ticket'] if x['No.Case'] > 0 else x['SplitPrice'] +x['ticket'],axis=1) + ROUNDING_ERROR).round(2)
            df['flag'] = df.apply(lambda x: '!' if x['Price'] != x['Unit Cost'] else '', axis=1)
            df = df.drop(columns=['caseflag'])
            # check total sum
            if df['Ext Cost'].sum().round(2) != (df['Price']*df['Qty']).sum().round(2):
                print (df['Ext Cost'].sum().round(2),(df['Price']*df['Qty']).sum().round(2) )
                print (df.loc[df['flag'] == '!'])
                msg = '= ' * 5 + 'Difference found !'
                df = df.drop(columns=['Item'])
                df.to_csv(f'query_{k}.csv')
            else:
                print (df)

                msg = '❀ ' * 5 + '   ALL CLEAR    ' + '❀ ' * 5
                df.to_csv('Kell_hold.csv')
            print(msg)
        return df
    def ask_supplier_quote(self, notes=''):
        # get_supplier_emails()   Update supplier contacts

        df = self.read_customer_price()
        cols = ['Customer', 'Product', 'Product_long', 'Qty', 'Ship Date', 'Unit Cost', 'Supplier']
        df = df.loc[df['Product_long'].str[0]=='Z', cols]
        df['SUPPLR'] =df['Supplier'].str.extract(r'\(([^)]+)\)$')
        conn = sqlite3.connect(PATH['db_path'])
        su = pd.read_sql_query("SELECT * FROM supplier", conn)
        df = df.merge(su, how='left', on='SUPPLR')
        df['Qty'] = df['Qty'].astype(str)
        df.loc[df['Qty']<='1','Qty'] = ''
        df = df.fillna('')

        for email in df['EMAIL'].unique():
            ds = df.loc[df['EMAIL']==email]
            customer = ds['Customer'].values[0]
            supplier = ds['SUPPLR'].values[0]
            ds = ds[['SUPPLR','Customer','Product','Product_long','Qty','Ship Date','Unit Cost']]
            send_price_request(recipient=admin['testemail'], customer=customer,supplier=supplier, table=ds.to_html(), notes=notes)
            # get_employee_emails('PP')
        print (df)
        return

    def check_order_status(self, po=None):
        return
def crack_pdf():
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader("")
    writer = PdfWriter()
    words_dict = open('', 'r')
    all_words = words_dict.readlines()

    # to remove all the newline characters from the words uncomment this
    # all_words = [x.strip('\n') for x in words_dict.readlines()]

    # print(all_words)
    pwd = ''
    count = 0
    # arrow
    for word in all_words:
        count +=1
        u_case = reader.decrypt(word.strip('\n'))
        # print(f"trying {word}...", u_case)
        if u_case > 0:
            pwd = word
            print(f"the password for the pdf file is {word}")
            break
        l_case = reader.decrypt(word.lower().strip('\n'))
        # print(f"trying {word.lower()}...", l_case)
        if l_case > 0:
            pwd = word
            print(f"the password for the pdf file is {word.lower()}")
            break
        if count%1000==0:
            print (count)
    if pwd == '':
        print("could not decrypt password")

def query_item_info(discount=0.2, ticket=0.25):
    df = query_search(target='inventory',item_tuple="('T3179')")
    df['Price'] = df['CasePrice']*(1-discount)+ticket
    print (df)
def main():
    # crack_pdf()
    # """        UNFINISHED         """
    # new = NewOrder(
    #     po={'customer_id': 'FL4494', 'sales_rep': 'cindy', 'dummy': '', "ticket": 0.45, "discount": 0.1,
    #         'orders': {
    #               1:{'customer':'KSA_467536_17.pdf','ksa': ''},    #
    #         }}
    # )

    # new = NewOrder(
    #     po={'customer_id': 'SALEREP', 'sales_rep': 'Cindy', 'dummy': '', "ticket": 0, "discount": 0.2,
    #         'orders': {
    #             1: {'customer': 'Cindy/Cindy_KSA_orders.xlsx', 'ksa': ''},  #
    #         }}
    # )
    new = NewOrder(
        po = { "customer_id":"FL2658", "sales_rep":"Cindy", "ticket":0, "discount":0.2, "dummy": "",
               "orders":{
                   "1": {"customer":"KSA_PO_10558.pdf","ksa": ""}
               }}
    )
    # new = NewOrder(
    #     po={"customer_id": "NV0356", "sales_rep": "Caryl", "ticket": 0.37, "discount": 0.1, "dummy": "",
    #         "orders": {
    #             "1": {"customer": "KURT S. ADLER, INC. 000294750.pdf", "ksa": ""}
    #         }}
    # )
    # new = NewOrder(
    #     po={"customer_id": "STEVE", "sales_rep": "Steve", "ticket": 0, "discount": 0, "dummy": "",
    #         "orders": {
    #             "1": {"customer": "Steve_KSA_orders.xlsx", "ksa": ""}
    #         }}
    # )

    # new.check_order_status()

    new.read_customer_price()
    #
    # new.ask_supplier_quote()
    # df.to_csv('tmp.csv')
    # print (df)
    # new.hold_inventory()
    # check_order_status(po={"customer_id":"FL4494","sale_repr":"Cindy", "dummy": ['P1194911'], "customer": ['P1194944','P1194945','P1194948','P1194957','P1194953','P1194947']})

main()