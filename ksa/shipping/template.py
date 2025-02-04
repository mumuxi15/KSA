import win32com.client as win32
import re, os
from config.contacts import *

outlook = win32.Dispatch('outlook.application')

##################################################
#
#              Send Tracking Emails
##################################################
def reply_not_shipped():
    return 'Thank you for the update. Please keep me posted when you have shipped. '

def reply_shipped():
    return 'Thank you for the update. Please send me the documents when ready. '

def reply_late():
    return 'Thanks for the quick response.  Please note a few orders are behind the schedule and would need to be shipped soon. '



def send_pricing_email(recipient, vendor, attachment=None):
    mail = outlook.CreateItem(0)
    mail.To = recipient
    mail.Subject = f'KSA 2025 Pricing - {vendor}'
    mail.Body = 'KSA pricing updates'
    mail.HTMLBody = f"""
    <!doctype html>
    <html>
        <head>
            <style>
                .red   {{color: red;}}
                .blue {{color:CadetBlue}}
                
                table, th, td {{
                  border: 1px solid black;
                  border-collapse: collapse;
                }}
            </style>
        </head>
    <body>
    <p>Hello, </p>
    <p>This is a reminder. Please send me the new prices for 2025 as soon as possible. </p>
    <p> Please EDIT on the table attached to this email .  </p>
    <p>1. Please fill the  <b class="red">Exchange Rate and Country</b>. </p> 
    <p>2. Please add your own images if it shows no image available. Unless you have 100+ items, then no images are needed. <p>
    <p>3. Please confirm the exchange rate or otherwise discuss with Howard </p>
    <p>4. Please let me know if there is an <b>early buy discount</b>.</p>
    <p><b>2025 price quotes</b> (with ± 2%  fluctuations).  </p>
    <p><b class="red">USD 1.00 / 7.00 RMB  </b></p>
    <p><b class="red">USD 1.00 / 30.00 NT  </b></p>    
    <p class="blue">For other currencies, if quoting in USD, please indicate the exchange rate used</p> 

    <p>All prices should be quoted F.O.B. Taiwan, F.O.B. Hong Kong and F.O.B. nearest China port (list port name). </p>
    <p>For suppliers with factories in other countries (e.g., Cambodia, Vietnam), provide separate price sheets and include minimum production and shipment requirements.</p>
    <p>Thank you!</p>
    <p>
    <br>{ksa_employee['PP']['name']}<br/>
    {ksa_employee['PP']['address']}
    </p>

    </body>
    </html>"""

    # To attach a file to the email (optional):
    # attachment  = "Path to the attachment"
    mail.Attachments.Add(attachment)
    mail.Send()

def send_email(recipient, sentfrom, title, highlight, table):
    mail = outlook.CreateItem(0)
    mail.To = recipient
    mail.Subject = title
    mail.Body = 'KSA shipping tracker'
    mail.HTMLBody = f"""
    <!doctype html>
    <html>
        <head>
            <style>
                .red   {{color: red;}}
                table, th, td {{
                  border: 1px solid black;
                  border-collapse: collapse;
                }}
                {highlight}
                
            </style>
        </head>
    <body>
    <p>Hello, </p>
    <p>Our records indicate that following purchase orders or PO balance will be due for shipment, where ORDERED is the ordered quantity and OUTQTY is the remaining quantity to ship.<p>
    {table}
    
    <p class="red">IMPORTANT: YOU MUST BOOK OUR ORDER WITH MOL 3 WEEKS IN ADVANCE TO RESERVE A SPACE. </p>
    <p>Please cc Jackie when you send Lily invoices, packing list and FCR.</p>
    <p>For any MOL-related questions, please email {ksa_employee['import']['email']} or Charlene. </p>
    <p>If there is a delay or need to extend the ship date, please email me. </p>
    <p>Thank you!</p>
    <p>
    <br>{sentfrom}<br/>
    {ksa_employee['PP']['address']}
    </p>
   
    </body>
    </html>"""


    # To attach a file to the email (optional):
    # attachment  = "Path to the attachment"
    # mail.Attachments.Add(attachment)

    mail.Send()

def send_late_reminders(recipient, sentfrom, highlight, table):
    mail = outlook.CreateItem(0)
    mail.To = recipient
    mail.Subject = 'KSA SHIPPING LATE - PLEASE SHIP SOON'
    mail.Body = 'KSA shipping tracker'
    mail.HTMLBody = f"""
    <!doctype html>
    <html>
        <head>
            <style>
                .red   {{color: red;}}
                table, th, td {{
                  border: 1px solid black;
                  border-collapse: collapse;
                }}
                {highlight}

            </style>
        </head>
    <body>
    <p>Hello, </p>
    <p class="red">Following items have been LATE. Please SHIP AS SOON AS POSSIBLE.<p>
    {table}
    <p>If there are any shipping related questions, please email {ksa_employee['import']['email']} or Charlene. </p>
    <p>Thank you!</p>
    <p>
    <br>{sentfrom}<br/>
    {ksa_employee['PP']['address']}
    </p>

    </body>
    </html>"""

    # To attach a file to the email (optional):
    # attachment  = "Path to the attachment"
    # mail.Attachments.Add(attachment)

    mail.Send()

def send_msg_from_ksa(recipient):
    mail = outlook.CreateItem(0)
    mail.To = recipient
    mail.Subject = 'A Message to All Chinese Vendors From Howard  '
    mail.Body = 'KSA message from Howard'
    mail.HTMLBody = f"""
    <!doctype html>
    <html>
        <head>
        </head>
    <body>
    <p>Hello, </p>
    <p>As you have heard or read, President Trump is likely planning on putting a 10% tariff on all goods from China. 
We cannot absorb the entire tariff  and cannot pass it on to our customers or they will probably cancel  many items. We  are going  to need your help with a reduction in  pricing  in order to be able to sell your product. What we feel is fair at this time is splitting the tariff. This means  a 5% reduction in your prices to us and we will absorb the other 5%. If the tariff amount changes up or down, we will still go with the 50/50 split.
The 5% or what ever the % is will be deducted when paying your invoices.
Thank you for your cooperation.<p>
    <p>Any comments, please send to Howard (hadler@kurtadler.com).  </p>
    <p>If you agree, please reply to Penny to confirm your acceptance of the 50/50 split. </p>
    <p>
    <br>Howard<br/>
    </p>

    </body>
    </html>"""

    # To attach a file to the email (optional):
    # attachment  = "Path to the attachment"
    # mail.Attachments.Add(attachment)

    mail.Send()

def send_price_request(recipient, customer, supplier,table,notes):
    mail = outlook.CreateItem(0)
    mail.To = recipient
    mail.Subject = f"KSA order - {customer} - {supplier}"
    mail.Body = f"KSA order - {customer}"
    mail.HTMLBody = f"""
    <!doctype html>
    <html>
        <head>
            <style>
                table, th, td {{
                  border: 1px solid black;
                  border-collapse: collapse;
                }}
            </style>
        </head>
    <body>
    <p>Hello, </p>
    <p>Could you please fill in the Unit Cost, MOQ, and Ship Date below thanks. <p>
    {table}
    <br>
    {notes}
    <p>Thank you!</p>
    <p>
    <br>{ksa_employee['PP']['name']}<br/>
    {ksa_employee['PP']['address']}
    </p>
   
    </body>
    </html>"""
    mail.Send()



def get_employee_emails(name):
    return ksa_employee[name]['email']
def text_filtering(s):
    s = re.sub(r'\s+', ' ', s)
    s = re.split(email_filter['from:'], s)
    return s[0]

def read_email(send_date):
    namespace = outlook.Getnamespace("MAPI")
    for acc in namespace.Accounts:
        if acc.SmtpAddress == admin['email']:
            account = acc
            break

    shipping_folder = namespace.Folders(account.DisplayName).Folders("shipping")

    df = []
    for message in shipping_folder.Items:
        subject = message.Subject
        sender_email = message.SenderEmailAddress if "@" in message.SenderEmailAddress else message.SenderName
        received_date = str(message.ReceivedTime)[0:10]
        if received_date>send_date:
            # Check for attachments
            # Print or process email details
            var = {
                "subject": subject,
                "sender": message.SenderName,
                "email": sender_email,
                "receive": received_date,
                "FCR": 1 if any('FCR' in attach.FileName for attach in message.Attachments) else 0 ,
                "body": text_filtering(message.Body)
            }
            df.append(var)
    return df

