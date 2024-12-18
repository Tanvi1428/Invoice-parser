import re
import json


def extract(text):
    dict_extract={
        'billing_date': None,
    'due_date': None,
    'invoice_no': None,
    'name': None,
    'tax_rate': None,
    'total': None,
    'item': []  
    }

    # Extracting Invoice Date
    billing_date_pattern=r"Invoice Date \d{2} [a-zA-Z]+ \d{4}"
    billing_date_match = re.search(billing_date_pattern, text)
        
    #print(billing_date_match.group())

    # Extracting Due Date
    due_date_pattern=r"Due Date \d{2} [a-zA-Z]+ \d{4}"
    due_date_match = re.search(due_date_pattern,text)
   # print(due_date_match.group())

    # Extract Invoce Number
    invoice_pattern=r"Invoice#\sINV-\w+\d+"
    invoice_match = re.search(invoice_pattern,text)
    #print(invoice_match.group())

    #Extract Name of Bill to
    name_pattern=r"M[s|r|rs]. [A-Za-z]+ [A-za-z.]+ [A-Za-z]+"
    name_match=re.search(name_pattern,text)
    #print(name_match.group())


    #tax rate
    tax_rate=r"Tax Rate \d.\d+%"
    tax_rate_match=re.search(tax_rate,text)
    #print(tax_rate_match.group())

    #Total amount
    total=r"Total \W[\d,.]+"
    total_match=re.search(total,text)
    #print(total_match.group())
    #print("---")

    #Item
    item_pattern=r"(\w+)\s(\d+.\d+)\s(\W[\d,.]+)\s(\W*[\d,.]+)"
    item_match=re.finditer(item_pattern,text)

    for match in item_match:
        #print("Product Name:", match.group(1))
        #print("Quantity:", match.group(2))
        #print("Unit Price:", match.group(3))
        #print("Total Price:", match.group(4))
        #print("---")

        item_details = {
        'Product Name': match.group(1),
        'Quantity': match.group(2),
        'Unit Price': match.group(3),
        'Total Price': match.group(4)}

        dict_extract['item'].append(item_details)

    dict_extract['billing_date'] = billing_date_match.group()
    dict_extract['due_date'] = due_date_match.group()
    dict_extract['invoice_no'] = invoice_match.group()
    dict_extract['name'] = name_match.group()
    dict_extract['tax_rate'] = tax_rate_match.group()
    dict_extract['total'] = total_match.group()
    
    json_extract=json.dumps(dict_extract,indent=4)
    #print(json_extract)
    return json_extract
