import pandas as pd
import re
def to_text(file):
    return 'hello'
def get_customer_id(file):
    return file.split('/')[-2]
def extract_upc(description):
    return [s for s in description.split() if s.startswith('4') and len(s)>10][0]
def parse_memo(file):
    "read memo here, return item list "
    re_filter = r'\b[A-Z](?:\w*\d){3,}\w*\b'

    df = pd.read_excel(file)
    items = []
    for line in df.columns:
        items += re.compile(re_filter).findall(line)
    # print (items)
    for i in df.values:
        for j in i:
            if isinstance(j,str):
                if "NOTE THE FOLLOWING CHANGES" in j:
                    print ('REACHED ADJUSTMENT LINE - STOP ')
                    return items
                elif "HAVE BEEN ADDED TO THE LINE" in j:
                    print ('REACHED ADD LINE - STOP ')
                    return items
                elif "AGAIN FOR SALE" in j:
                    print ('REACHED RESALE LINE - STOP ')
                    return items
                else:
                    items += re.compile(re_filter).findall(j)

    return items

def parse_ksa_order(file):
    #some csv files are saved in lower cap
    file = file.replace('Order_Confirmation_P','order_confirmation_p')
    # usecol = ["Product", "Description", "Ordered", "B/O'd", "To Ship", "Price","Expected Date"]
    df = pd.read_excel(file)
    df = df.loc[df['Product'].notna()]
    return df


def parse_customer_order(file, template):
    skip = 0
    namemapper = {'colname':{}, 'skip': 23},

    mydict = {'CL7158': {'colname': {'STYLE #':'Product','QTY':'Qty', 'Unit Total':'Unit Cost', 'Total Cost':'Ext Cost' }, 'skip':23},
              'PA6502': {'colname': {'Item':'Product', 'Unit Price':'Unit Cost', 'Total':'Ext Cost' }, 'skip': 0},
              'FL4494': {'colname':{'SKU Number  Description':'Description','Vendor Part No.':'Product', 'Qty Ord/ Pcs': 'Qty','Unit Retail':'Retail', 'Extended\nCost':'Ext Cost'},
                         'skip': 15},
              'SALEREP': {'colname':{}, 'skip': 0},
              }

    df = pd.read_excel(file,skiprows=mydict[template]['skip']).rename(columns=mydict[template]['colname'])
    df = df.loc[df['Product'].notna()]
    if template == 'FL4494':
        df['UPC'] = df['Description'].apply(extract_upc)
    if template == 'SALEREP':
        df = df.loc[df['Completed']!=1]
    return [df]



