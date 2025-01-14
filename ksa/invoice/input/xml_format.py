import xml.etree.ElementTree as ET
import pandas as pd

def to_text(file):
    return 'hello'
def get_customer_id(file):
    return file.split('/')[-2]

def parse_ksa_order(file):
    tree = ET.parse(file)
    root = tree.getroot()
    namespace = {'ss': 'urn:schemas-microsoft-com:office:spreadsheet'}
    table = root.find('.//ss:Table', namespace)
    # # Extract the column headers
    headers = [cell.find('ss:Data', namespace).text for cell in table.find('ss:Row', namespace)]
    rows = []
    for row in table.findall('ss:Row', namespace)[1:]:
        row_data = []
        for cell in row.findall('ss:Cell', namespace):
            data = cell.find('ss:Data', namespace)
            row_data.append(data.text if data is not None else None)
        rows.append(row_data)
    # to dataframe
    df = pd.DataFrame(rows, columns=headers)
    df = df.loc[df["Product"].notna()]
    return df[["Product", "Description", "Ordered", "B/O'd", "To Ship", "Price","Expected Date"]]


