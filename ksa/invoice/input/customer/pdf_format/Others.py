import sys
import sqlite3


def write_to_db(self):
    df = pd.DataFrame(self.orders).T[['ksa', 'customer']]
    df = df.rename(columns={"customer": "customer_po"})
    df['customer'] = self.customer_id
    df['sales_rep'] = self.sales_rep
    df['dummy'] = self.dummy
    df['required_date'] = self.required_date
    df['cancel_date'] = self.cancel_date
    conn = sqlite3.connect(PATH['database'])

    conn.execute('''
       CREATE TABLE IF NOT EXISTS orders(
           ksa TEXT PRIMARY KEY,
           customer_po TEXT,
           Customer TEXT,
           sales_rep TEXT,
           dummy TEXT, 
           required_date TEXT,
           cancel_date TEXT
       )
       ''')
    # df.to_sql("orders", conn, if_exists='replace')
    print(df.columns)
    return

def write_db(file, table_name, db_path):
    if file.endswith('.xlsx'):
        df = pd.read_excel(file)
    elif file.endswith('.csv'):
        df = pd.read_csv(file)
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print(f"Insert File '{file}' to database")

def create_inv_table(file,db_path, table_name='inventory'):
    df = pd.read_excel(file)
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists='append', index=False)
    conn.close()
    print(f"update inventory to database")
def read_db():
    return


