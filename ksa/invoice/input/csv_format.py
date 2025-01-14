import pandas as pd

def to_text(file):
    return 'hello'
def get_customer_id(file):
    return file.split('/')[-2]

def parse_ksa_order(file):
    #some csv files are saved in lower cap
    file = file.replace('Order_Confirmation_P','order_confirmation_p')
    # usecol = ["Product", "Description", "Ordered", "B/O'd", "To Ship", "Price","Expected Date"]
    df = pd.read_csv(file)
    df = df.loc[df['Product'].notna()]
    return df

def parse_customer_order(file,template):
    usecols = ['Product','Qty','Unit Cost','Ext Cost']
    df = pd.read_csv(file,usecols=usecols)
    print (df)
    return [df]



