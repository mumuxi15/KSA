import pandas as pd
import datetime
import warnings
from outlook.email_handler import send_shipping_reminder, send_late_reminders, read_email_shipping
from query.db_handler import query_search, query_direct
from .utils import get_end_month, get_supplier_contacts, format_table

class ShippingHandler:
    def __init__(self):
        self.deadline = get_end_month()
        self.today = datetime.datetime.now().date()
        self.lateline = self.today - datetime.timedelta(days=21)

    def query_open_order(self):
        """
        Query open orders and filter based on conditions.
        :return: DataFrames
        """
        df = query_search(target='shipping')
        df['SUPPLR'] = df['SUPPLR'].str.replace(" ", "")
        df['ORDQTY'] = df['ORDQTY'].astype(int)
        df['CONDAT'] = pd.to_datetime(df['CONDAT'], errors='coerce').dt.date
        df['NEWCONDAT'] = pd.to_datetime(df['NEWCONDAT'], errors='coerce').dt.date
        df['PCTSHIP'] = df['OUTQTY'] / df['ORDQTY']
        df = df.loc[(df['CONDAT'] <= self.deadline)]

        # Handle missing items  - allow 5% error
        error = df.loc[(df['PCTSHIP'] < 0.05) & (df['INTQTY'] == 0)]
        if not error.empty:
            warnings.warn("Items missing report generated.")
            df = df.loc[~((df['PCTSHIP']<0.05) & (df['INTQTY'] ==0))]
            # Handle extended CONDAT
            error = df.loc[df['DATEDFF'] > 150]
            if not error.empty:
                warnings.warn("Data entry issue detected.")
            df.loc[df['DATEDFF'] > 100, 'NEWCONDAT'] = df.loc[df['DATEDFF'] > 100, 'CONDAT']

            # Merge supplier contacts
            sup = get_supplier_contacts()
            df = df.drop(columns=['INTQTY'])
            df = df.merge(sup, on='SUPPLR', how='left')
        return df

    def email_monthly_reminder(self, df):
        """
        Email suppliers with order details.

        :param df: DataFrame containing supplier data.
        :param sendto: Recipient type ('default')
        """
        col = ['PURORD', 'SUPPLR', 'PRODCT', 'ORDQTY', 'OUTQTY', 'CONDAT', 'NEWCONDAT', 'TYPE']
        nan_rows = df[df['EMAIL'].isna()]
        if len(nan_rows) > 1:
            warnings.warn("Supplier emails missing.")

        for contact in df['EMAIL'].dropna().unique():
            table = df.loc[df['EMAIL'] == contact, col]
            if table.loc[table['ORDQTY'] != table['OUTQTY']].empty:
                table = table.drop(columns=['OUTQTY'])
            if table.loc[table['CONDAT'] != table['NEWCONDAT']].empty:
                table = table.drop(columns=['NEWCONDAT'])
            table = table.sort_values(by=['SUPPLR', 'PRODCT'])

            style, html = format_table(table)
            send_shipping_reminder(recipient=contact, sentfrom='Sender_Name', title=f'KSA {self.deadline.strftime("%b")} Shipments',
                           highlight=style, table=html)

    def gen_tracking_sheet(self, df, savecsv=False):
        """
        Generate a tracking sheet for late orders.

        :param df: DataFrame containing order data.
        :param savecsv: If True, save the DataFrame to a CSV file.
        :return: DataFrame with tracking information.
        """
        df['LATE'], df['ATTN'] = 0, 0
        df.loc[df['NEWCONDAT'] < self.lateline, 'ATTN'] = 1
        df.loc[df['NEWCONDAT'] < self.today, 'LATE'] = 1
        df.loc[(df['TYPE'] == 'C') & (df['ATTN'] == 1), 'Z_ITEMS'] = 1
        df.loc[(df['TYPE'] == 'S') & (df['ATTN'] == 1) & (df['PCTSHIP'] < 0.5), 'ATTN'] = 0

        if savecsv:
            df.loc[df['LATE'] == 1].sort_values(by=['SUPPLR', 'NEWCONDAT']).to_csv('late_orders.csv')
            df.to_csv(f'{self.deadline.strftime("%b")} tracking.csv')

        return df

    def remind_supplier_late(self, summary, df):
        """
        Send reminders to suppliers with late orders.

        :param summary: Summary DataFrame.
        :param df: DataFrame containing order data.
        """
        late = summary.loc[summary['ATTN'] > 0]
        for vendor in late.index:
            table = df.loc[(df['SUPPLR'] == vendor) & (df['NEWCONDAT'] < self.today)]
            contact = table['EMAIL'].unique()[0]
            table = table[['PURORD', 'SUPPLR', 'PRODCT', 'ORDQTY', 'OUTQTY', 'CONDAT', 'NEWCONDAT', 'TYPE', 'LATE']]
            style, html = format_table(table)
            send_late_reminders(recipient=contact, sentfrom='Sender', highlight=style, table=html)

    def read_reply_shipping(self, send_date, df=None):
        print('---' * 10)
        em = pd.DataFrame(read_email_shipping(send_date))  #
        if any(em):
            em = em.groupby(['email']).agg({'receive': 'max', 'FCR': 'sum', 'body': '-'.join})
            em.index = em.index.str.lower()
            replied_list = list(em.index)
            # em.to_csv('read_reply.csv')
            if any(df):
                df['REPLY'] = df['EMAIL'].apply(lambda x: '' if x in replied_list else False)
                df.to_csv(f'{deadline.strftime("%b")} tracking wt replies.csv')
            return em
        else:
            print('NO REPLIES ')