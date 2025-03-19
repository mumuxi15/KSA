import win32com.client as win32
outlook = win32.Dispatch('outlook.application')

def request_pricing(recipient, vendor, empolyee='employee_name', attachment=None):
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
    <p>3. Please confirm the exchange rate </p>
    <p>4. Please let me know if there is an <b>early buy discount</b>.</p>  
    <p class="blue">For other currencies, if quoting in USD, please indicate the exchange rate used</p> 

    <p>All prices should be quoted F.O.B. Taiwan, F.O.B. Hong Kong and F.O.B. nearest China port (list port name). </p>
    <p>For suppliers with factories in other countries (e.g., Cambodia, Vietnam), provide separate price sheets and include minimum production and shipment requirements.</p>
    <p>Thank you!</p>
    <p>
    {employee}
    </p>

    </body>
    </html>"""

    # To attach a file to the email (optional):
    # attachment  = "Path to the attachment"
    mail.Attachments.Add(attachment)
    mail.Send()


def send_shipping_reminder(recipient, sentfrom, title, highlight, table):
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
    </p>

    </body>
    </html>"""
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
    <p>If there are any shipping related questions, please email Charlene. </p>
    <p>Thank you!</p>

    </body>
    </html>"""
    mail.Send()


def read_email_shipping(send_date, useremail):
    '''  task is to extract FCR documents from supplier emails
    using outlook rules to filter keywords to categorize emails and use python read specific folder (Shipping)
    Then read FCR documents from MOL to compare with database data
    '''
    namespace = outlook.Getnamespace("MAPI")
    # code below handles multiple users in outlook problem
    #
    for acc in namespace.Accounts:
        if acc.SmtpAddress == useremail:
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

