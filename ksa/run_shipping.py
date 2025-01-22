import pandas as pd
import datetime, os, environ
import gspread
import calendar
from dateutil import relativedelta
from shipping import send_email, send_late_reminders, read_email, get_employee_emails
from query import query_search, query_direct
from config.env import PATH, env

pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 200)

def get_end_month():
    # today+10 -> get end of month
    d = datetime.datetime.now().date() + datetime.timedelta(days=10)
    return datetime.date(d.year, d.month, calendar.monthrange(d.year, d.month)[-1])

def function2():
    return "Hello from function2 in module2"

def get_supplier_contacts():
    """ GET SUPPLIER EMAIL FROM GSHEET  """
    gc = gspread.service_account(filename=PATH['gsheet_key'])
    sh = gc.open_by_key(env("PRICING_WORKSHEET_KEY"))
    df = pd.DataFrame(sh.get_worksheet(2).get_all_records())
    # print ('remaining vendor left:', len(df))
    return df[['SUPPLR', 'EMAIL']]


def format_table(df):
    renamecol = {"SUPPLR": "Supplier", "PURORD":"PO#",
                 "PRODCT": "Item#", "ORDQTY": "ORDERED"}
    df = df.rename(columns=renamecol).reset_index(drop=True)
    df['TYPE'] = df['TYPE'].map({'C':'Special', 'S':'Stock','P':'P','D':'D'})
    html = df.style.highlight_between(subset=['CONDAT'], color='yellow',right=today).to_html()
    style, table = html.split("</style>")
    style = style.lstrip('<style type="text/css">')
    return style, table

def query_open_order(Ann):
    df = query_search(target='shipping')
    df['SUPPLR'] = df['SUPPLR'].str.replace(" ", "")
    df['ORDQTY'] = df['ORDQTY'].astype(int)
    df['CONDAT'] = pd.to_datetime(df['CONDAT'], errors='coerce').dt.date
    df['NEWCONDAT'] = pd.to_datetime(df['NEWCONDAT'], errors='coerce').dt.date
    df['PCTSHIP'] = df['OUTQTY']/df['ORDQTY']
    df = df.loc[(df['CONDAT'] <= deadline)]

    ##### 10 % error   #####
    error = df.loc[(df['PCTSHIP'] < 0.1) & (df['INTQTY']==0), ['PURORD', 'SUPPLR', 'PRODCT','ORDQTY','OUTQTY', 'CONDAT']]
    if not error.empty:
        print ('---'*5, 'ITEM MISSING REPORT', '---'*5, '\n', error, '\n -----  CORRECTION APPLY : HIDE MISSING ITEMS -------\n')
        # error.to_csv(f'{deadline.strftime("%b")} missing item report.csv')
        df = df.loc[~((df['PCTSHIP']<0.1) & (df['INTQTY']==0))]

    #####  Extended CONDAT  ############
    error = df.loc[df['DATEDFF'] >150]
    if not error.empty:
        print (error, '\n-----------------    TELL JACKIE  DATA ENTRY ISSUE         -----------------' )
        df.loc[df['DATEDFF'] > 100,'NEWCONDAT'] = df.loc[df['DATEDFF'] > 100,'CONDAT']

    #### read supplr emails
    sup = get_supplier_contacts()
    df = df.drop(columns=['INTQTY'])
    df = df.merge(sup, on='SUPPLR', how='left')

    # task one: Ann send all type=S, supplier begins with C to Ann
    if Ann:
        ann = df.loc[(df['SUPPLR'].str[0] == 'C') & (df['TYPE'] == 'S')].sort_values(by=['SUPPLR', 'CONDAT'])
    # task two: mine
    pp = df.loc[((df['SUPPLR'].str[0] != 'C') & (df['TYPE'] == 'S')) | (df['TYPE'] == 'C')]
    return pp, ann

def email_suppliers(df, sendto='default'):
    col = ['PURORD', 'SUPPLR', 'PRODCT','ORDQTY','OUTQTY', 'CONDAT', 'NEWCONDAT', 'TYPE']
    nan_rows = df[df['EMAIL'].isna()]
    if len(nan_rows) > 1:
        print (nan_rows)
        warnings.warn("supplier emails missing")

    for contact in df['EMAIL'].dropna().unique():
        table = df.loc[df['EMAIL'] == contact,col]
        #  drop duplicated columns if duplicated
        if table.loc[table['ORDQTY'] != table['OUTQTY']].empty:
            table = table.drop(columns=['OUTQTY'])
        if table.loc[table['CONDAT'] != table['NEWCONDAT']].empty:
            table = table.drop(columns=['NEWCONDAT'])
        table = table.sort_values(by=['SUPPLR','PRODCT'])
        ##### supplier

        style, html = format_table(table)
        if sendto == 'default':
            send_email(recipient=contact,sentfrom='Penny',title=f'KSA {deadline.strftime("%b")} Shipments', highlight=style, table=html)
            print ()
        elif sendto == 'Ann':
            send_email(recipient=get_employee_emails('Annmarie'), sentfrom='Anne-Marie JeanBaptiste',title=f'KSA {deadline.strftime("%b")} Shipments-{'-'.join(table['SUPPLR'].unique())}', highlight=style, table=html)
            print ()
        else:
            print (table)
        print ('- - '*10)

    return df

def gen_tracking_sheet(df, savecsv=False):
    """ ATTN=2 if special orders are very late; """
    df['LATE'], df['ATTN'] = 0, 0
    df.loc[df['NEWCONDAT'] < lateline, 'ATTN'] = 1   #bring attention if late
    df.loc[df['NEWCONDAT'] < today, 'LATE'] = 1
    df.loc[(df['TYPE'] == 'C') & (df['ATTN'] == 1), 'Z_ITEMS'] = 1
    df.loc[(df['TYPE'] == 'S') & (df['ATTN'] == 1) & (df['PCTSHIP']<0.5), 'ATTN'] = 0
    if savecsv:
        df.loc[df['LATE']==1].sort_values(by=['SUPPLR','NEWCONDAT']).to_csv('late_orders.csv')
    df = df.groupby(['SUPPLR']).agg({'EMAIL':'first','NEWCONDAT':'min','LATE':'sum', 'ATTN':'max','Z_ITEMS':'any'}).sort_values(by=['SUPPLR'])
    df['Z_ITEMS'] = df['Z_ITEMS'].astype(int)
    if savecsv:
        df.to_csv(f'{deadline.strftime("%b")} tracking.csv')
    return df

def read_reply(send_date, df=None):
    print ('---'*10)
    em = pd.DataFrame(read_email(send_date))#
    if any(em):
        em = em.groupby(['email']).agg({'receive': 'max', 'FCR': 'sum', 'body':'-'.join})
        em.index = em.index.str.lower()
        replied_list = list(em.index)
        # em.to_csv('read_reply.csv')
        if any(df):
            df['REPLY'] =df['EMAIL'].apply(lambda x: '' if x in replied_list else False)
            df.to_csv(f'{deadline.strftime("%b")} tracking wt replies.csv')
        return em
    else:
        print ('NO REPLIES ')
    # if any(df):
        # df['REPLY'] = df['email'].apply(lambda x: 1 if x in em.index.unique() else 0)

    return em

def get_GTIN_by_item(item):
    # print (item_id)
    item = tuple(item) if isinstance(item, list) else f'({item})'
    df = query_direct(f"""select PRODCT, SUPPLR, GTIN, TYPE, GTINDESC, EAN_UCC,TOTSKUQTY from kuradl_97x_740_prod_x.dbo.POGTIN
            where PRODCT in {item} AND TYPE=4""")
    print (df)
    print (df.columns)

def check_by_item(item):
    item = tuple(item) if isinstance(item, list) else f'({item})'
    df = query_search(target="shipping_by_item",item_tuple=item)
    print (df)


def remind_supplier_late(summary, df):
    late = summary.loc[summary['ATTN']>0]
    for vendor in late.index:
        print (vendor,'\n','--'*10)
        table = df.loc[(df['SUPPLR']==vendor)&(df['NEWCONDAT']<today)]
        contact = table['EMAIL'].unique()[0]
        table = table[['PURORD', 'SUPPLR', 'PRODCT', 'ORDQTY', 'OUTQTY', 'CONDAT', 'NEWCONDAT', 'TYPE', 'LATE']]
        style, html = format_table(table)
        send_late_reminders(recipient=contact,sentfrom='Penny', highlight=style, table=html)

def update_supplier_data():
    # get_supplier_contacts()
    df = query_search(target="getsupplrcontacts")
    # df.to_csv('tmp.csv')
    print (df)


if __name__ == '__main__':
    deadline = get_end_month()
    today = datetime.datetime.now().date()
    lateline = today - datetime.timedelta(days=21)
    # check_by_item(['CC0748DC','C7954GP'])
    # get_GTIN_by_item(["ZDH991288",""])

    # update_supplier_data()

    df, ann = query_open_order(Ann=True)
    # print (df)
    # print (ann)
    # email_suppliers(df, sendto='default')  #send emails monthly
    # email_suppliers(ann, sendto='Ann')
    # summary = gen_tracking_sheet(df,savecsv=True)
    # remind_supplier_late(summary, df)  # send late reminders if late




