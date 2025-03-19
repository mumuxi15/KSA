import os
import datetime
import calendar
import openpyxl
import pandas as pd
import gspread
from .config import GSHEET_KEY, PRICING_WORKSHEET_KEY, PRICING_PATH

def get_end_month():
    # today+10 -> get end of month
    d = datetime.datetime.now().date() + datetime.timedelta(days=10)
    return datetime.date(d.year, d.month, calendar.monthrange(d.year, d.month)[-1])

##########################
### google sheet connection
#########################


import gspread
import pandas as pd
from typing import List


##########################
### Google Sheets Connection
##########################
def test_gsheet_connection(gsheet_key: str) -> None:
    """
    Test the connection to Google Sheets and list all available spreadsheets

    Args:
        gsheet_key (str): = GSHEET_KEY stored in config/.env

    Returns:
        None
    """
    try:
        gc = gspread.service_account(filename=gsheet_key)
        spreadsheets = gc.openall()

        if spreadsheets:
            for spreadsheet in spreadsheets:
                print("Title:", spreadsheet.title, "URL:", spreadsheet.url)
        else:
            print("No spreadsheets available. Please share the spreadsheet with the Service Account email.")

    except Exception as e:
        print(f"An error occurred while testing Google Sheets connection: {e}")


def get_supplier_contacts(gsheet_key: str, pricing_worksheet_key: str) -> pd.DataFrame:
    """
    Fetch supplier contacts from Google Sheet.

    Args:
        gsheet_key (str):  KEY stored in config/.env
        pricing_worksheet_key (str):  KEY stored in config/.env

    Returns:
        pd.DataFrame: A DataFrame containing supplier contacts with columns ['SUPPLR', 'EMAIL'].
    """
    try:
        gc = gspread.service_account(filename=gsheet_key)

        sh = gc.open_by_key(pricing_worksheet_key)

        # Fetch data from the 3rd worksheet
        worksheet = sh.get_worksheet(2)
        df = pd.DataFrame(worksheet.get_all_records())

        # Return only the relevant columns
        return df[['SUPPLR', 'EMAIL']]

    except Exception as e:
        print(f"An error occurred while fetching supplier contacts: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error


def get_inactive_suppliers(gsheet_key: str, pricing_worksheet_key: str) -> List[str]:
    """
    Fetch a list of inactive suppliers from Google sheet
    Returns:
        List[str]: A list of inactive supplier codes.
    """
    try:
        gc = gspread.service_account(filename=gsheet_key)
        sh = gc.open_by_key(pricing_worksheet_key)
        # Fetch data from the 2nd worksheet
        worksheet = sh.get_worksheet(1)
        df = pd.DataFrame(worksheet.get_all_records())

        # Filter and return inactive suppliers
        return df.loc[df['OUT'] == 'x', 'SUPPLR'].tolist()

    except Exception as e:
        print(f"An error occurred while fetching inactive suppliers: {e}")
        return []  # Return an empty list in case of error


def get_inactive_items(gsheet_key: str, pricing_worksheet_key: str) -> List[str]:
    """
        List[str]: A list of inactive item codes. Do not include those items when send pricing emails
    """
    try:
        gc = gspread.service_account(filename=gsheet_key)
        sh = gc.open_by_key(pricing_worksheet_key)
        # Fetch data from the 4th worksheet
        worksheet = sh.get_worksheet(3)
        df = pd.DataFrame(worksheet.get_all_records())
        # Filter and return inactive items
        return df.loc[df['Active'] != 1, 'Item'].tolist()

    except Exception as e:
        print(f"An error occurred while fetching inactive items: {e}")
        return []

def get_reviewed_list(gsheet_key: str, pricing_worksheet_key: str):
    """GET LIST OF VENDORS THAT COMPLETED THE TASK """

    try:
        gc = gspread.service_account(filename=gsheet_key)
        sh = gc.open_by_key(pricing_worksheet_key)
        df = pd.DataFrame(sh.get_worksheet(0).get_all_records())[['SUPPLR', 'REVIEWED', 'PRINTED', 'Exchange Rate']]
        df = df.loc[(df['PRINTED'] != 1) & ((df['REVIEWED'] == 1) | (df['REVIEWED'] == 2)), ['SUPPLR', 'Exchange Rate']]
        df.index = df['SUPPLR']
        df = df[['Exchange Rate']]
        return df.to_dict()

    except Exception as e:
        print(f"An error occurred while get reviewed list: {e}")
        return []

###################################

def format_table(df):
    """  add highlight to dates if it's pass due
         used in sending emails with tables
    """
    renamecol = {"SUPPLR": "Supplier", "PURORD": "PO#", "PRODCT": "Item#", "ORDQTY": "ORDERED"}
    df = df.rename(columns=renamecol).reset_index(drop=True)
    df['TYPE'] = df['TYPE'].map({'C': 'Special', 'S': 'Stock', 'P': 'P', 'D': 'D'})
    html = df.style.highlight_between(subset=['CONDAT'], color='yellow', right=datetime.datetime.now().date()).to_html()
    style, table = html.split("</style>")
    style = style.lstrip('<style type="text/css">')
    return style, table


def get_GTIN_by_item(item):
    """ get upc """
    from query.db_handler import query_direct
    item = tuple(item) if isinstance(item, list) else f'({item})'
    df = query_direct(f"""select PRODCT, SUPPLR, GTIN, TYPE, GTINDESC, EAN_UCC, TOTSKUQTY from tb_name
            where PRODCT in {item} AND TYPE=4""")
    print (df)


def mass_print():
    " can print all documents under folder - can choose printer, print styles, papersize, landscape or vertical"

    import win32api
    import win32print
    import time
    # all_printers = win32print.EnumPrinters(2)
    defaultPrinter = win32print.GetDefaultPrinter()
    print (defaultPrinter)
    # if defaultPrinter != 'Art Dept C8100-716E PS':
    win32print.SetDefaultPrinter('Art Dept C8100-716E PS')
    mydir = "C:/Users/mpan/Desktop/print"
    files = os.listdir(mydir)
    for f in files:
        print ( "printing file " + str(mydir + f) + " on " + str(win32print.GetDefaultPrinter()))
        win32api.ShellExecute(0, "print", os.path.join(mydir, f), None, ".", 0)
        time.sleep(6)

def test_database():
    from query.db_handler import query_search
    tb = """
    """

    tbs = [t for t in tb.split('\n') if t!=""]
    for tb in tbs:
        try:
            df = query_search(target="testdb", item_tuple=tb)
            if len(df)<30:
                print (tb, '   SKIP  ')
            else:
                print (df.columns)
                suffix = ''
                if 'TRANSCTN' in df.columns:
                    suffix='_transctn'
                elif 'PRODCT' in df.columns:
                    suffix='_prod'
                elif 'INVOICE' in df.columns:
                    suffix='_invoice'

                df.to_csv(tb+suffix+'.csv')
        except exc.SQLAlchemyError:
            print (tb, '  db issues  SKIP  ')

def serena_files():
    """
    taiwan office - use a different pricing template
    """
    # re-edit her sheets
    path = f'{PRICING_PATH["prc_folder"]}serena/'
    filenames = os.listdir(path)
    for filename in filenames:
        vendor = filename.split('.')[0].split(' ')[-1]
        print (vendor)
        df = pd.read_excel(f'{path}{filename}')
        s = df[df.columns[0]]
        i = s[s.str.contains('KSA', na=False)].index[0]
        df = pd.read_excel(f'{path}{filename}',skiprows=i+1)
        col2025 = [c for c in df.columns if '2025' in c][0]
        col2024 = [c for c in df.columns if '2024' in c][0]
        df = df.rename(columns={col2025:"2025 COST", col2024: "2024 COST", "NW/GW LBS":"NW/GW","2024 PURCH":"PURCH"})
        df = df.dropna(how="all",axis=1)
        df["DIMENSIONS (INCHES)"] =  df["DIMENSIONS (INCHES)"].str.replace(r'\s+', ' ', regex=True).str.replace('CTN','\nCTN')
        df = df.drop(columns=['IN/OUT/   PACK PCS',])
        df['Photo'] =''
        df['% Change'] = df['2025 COST']/df['2024 COST']-1
        df = df[list(df.columns[0:1])+['Photo']+list(df.columns[1:4])+['% Change']+list(df.columns[4:-2])]

        writer = pd.ExcelWriter(f'{PRICING_PATH["prc_folder"]}/KSA 2025 PRICING {vendor}.xlsx')
        df.to_excel(writer, startcol=0, startrow=3)
        #
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        border_format = workbook.add_format({'border': 1})

        # Apply the border format to the entire table
        worksheet.conditional_format(f'A4:{chr(ord("A") + len(df.columns))}{len(df) + i-1}',
                                     {'type': 'no_errors', 'format': border_format})

        format1 = workbook.add_format({'num_format': '0%'})
        # worksheet.set_column('C:C', None, format2)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('L:L', 18)
        for r in range(4,len(df)+5):
            worksheet.set_row(r,height=49)

        worksheet.write_string(0, 0, 'EXCHANGE RATE:___RMB 7.00___')
        worksheet.write_string(1, 0, 'PRICES QUOTED DO NOT INCLUDE UPC BAR CODING')
        worksheet.write_string(0, 5, f'SUPPLIER:  ')
        worksheet.write_string(1, 5, f'VENDOR#:')
        worksheet.write_string(1, 6, vendor)
        worksheet.set_landscape()

        writer._save()

        ### add currency
        wb = openpyxl.load_workbook(f'{PRICING_PATH["prc_folder"]}/KSA 2025 PRICING {vendor}.xlsx')
        ws = wb.active
        currency_style = openpyxl.styles.NamedStyle(name='currency_rmb', number_format='¥#,##0.00')
        # Apply the currency style to columns E and F
        for col in ['E', 'F']:
            for row in ws[col]:
                row.number_format = currency_style.number_format
        # Save the workbook with currency formatting
        wb.save(f'{PRICING_PATH["prc_folder"]}/KSA 2025 PRICING {vendor}.xlsx')
    return

