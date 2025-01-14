import re
from .input import pdf_format
from .input import xml_format
from .input import csv_format
from .input import xls_format

def to_text(path):
    with open(path, 'r') as f:
        return f.read()

def extract_data(myfile, template=None, input_module=None):
    """Extracts tables from PDF/image invoices.
        ----------
        file : str
            path of electronic invoice file in PDF,JPEG,PNG (example: "/home/duskybomb/pdf/invoice.pdf")
        templates : list of instances of class `InvoiceTemplate`, optional
            Templates are loaded using `read_template` function in `loader.py`
        input_module : {'xml_format', 'pdf_format', 'csv_format', 'excel_format'}, optional
        Returns: dataframe
        -------
        # >>> from invoice.input import pdf_format
        # >>> extract_data(file="../../Order_Confirmation_P1195257.xml")
        """
    file = myfile.lower()
    if input_module is None:
        if file.endswith('.pdf'):
            input_module = pdf_format
        elif file.endswith('.xml'):
            input_module = xml_format
        elif file.endswith('.csv'):
            input_module = csv_format
        elif file.endswith('.xlsx') or file.endswith('.xls'):
            input_module = xls_format
    # extracted_str = input_module.to_text(file)

    if 'order_confirmation' in file:
        table = input_module.parse_ksa_order(myfile)
    elif any(re.compile(r'adler|ksa|po').findall(file)):
        table = input_module.parse_customer_order(myfile,template)
    elif 'xerox scan' in file:
        table = input_module.parse_memo(myfile)
    else:
        print ('no functions built for those types: ',myfile)

    return table
