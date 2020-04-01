#  Retrieve all CHCCS patron records
#  Create csvs
#     all selected patrons
#     records with malformed barcodes
#     lookup table of Patron ID and Barcode 
#  
import requests
import pathlib
import csv
import json
import jsonpickle
import re
import os
import datetime
import secrets, filename_secrets
import sierra_util

# Dicts for storing patron records and barcodes
all_patrons = []
all_barcodes = []

# retrieves all patron info for comparison against student info

iterator = 0
first_pass = True
patron_count = 0
# today = datetime.date.today().strftime('%Y-%m-%d')
active_patrons_token = sierra_util.get_token()
barcode_match = re.compile(r'(;|\s)+')
barcode_format_error = re.compile(r'\D+')
barcode_note = re.compile(r'(\d+)(?=\D+)')

# compare_date = datetime.datetime.strptime('2022-08-30','%Y-%m-%d')
# compare date is 2 years in the future
compare_date = (datetime.datetime.today() + datetime.timedelta(weeks=104)).strftime('%Y-%m-%d')
allpatronsFile = pathlib.Path(filename_secrets.productionStaging).joinpath("all_patrons.csv")
update_patrons = open(allpatronsFile, "w+")

row = ['Barcode', 'Patron ID']
patronbarcodesFile = pathlib.Path(filename_secrets.productionStaging).joinpath("patron_barcodes.csv")
patron_barcodes = open(patronbarcodesFile, "w+")
csv_barcode = csv.writer(patron_barcodes)
csv_barcode.writerow(row)

row = ['Patron ID', 'Barcode', 'Expiration Date']
barcodeerrorsFile = pathlib.Path(filename_secrets.productionStaging).joinpath("barcode_errors.csv")
barcode_error = open(barcodeerrorsFile, "w+")
barcode_errors = csv.writer(barcode_error)
barcode_errors.writerow(row)


while True:
    get_header_text = {"Authorization": "Bearer " + active_patrons_token}
    get_request = requests.get("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons?offset=" + str(iterator) + "&limit=2000&fields=id,names,barcodes,birthDate,emails,patronType,addresses,phones,expirationDate&deleted=false", headers=get_header_text)
    data = json.loads(get_request.text)    

    try:
        for i in data['entries']:
            try:
                if i['expirationDate']:
                    patron_expiration = datetime.datetime.strptime(i['expirationDate'],'%Y-%m-%d')
                else:
                    continue
            except KeyError:
                continue
            # Select patrons with expiration dates before the comparison date set above
            # if (patron_expiration < compare_date):
            if (True): # retrieve all (non-deleted) patron records
                if first_pass:
                    fieldnames = i.keys()
                    csv_writer = csv.DictWriter(update_patrons, fieldnames=fieldnames, extrasaction='ignore', delimiter=',')
                    csv_writer.writeheader()
                    first_pass = False
                    
                csv_writer.writerow(i)
                patron_count += 1
                for barcode in i['barcodes']:
                    # remove whitespace 
                    barcode = barcode.strip()
                    found = re.split(barcode_match, barcode)
                    if found[0]: 
                        format_error = re.search(barcode_note, barcode)
                        format_error_alpha = re.search(barcode_format_error, barcode)
                        if (format_error is None) and (format_error_alpha is None): 
                          row = [found[0], i['id']]
                          csv_barcode.writerow(row)
                        else:
                          row = [i['id'], str(barcode), str(i['expirationDate'])]
                          barcode_errors.writerow(row)
                          #print(row)
    except KeyError:
        break
    print(f'Total patrons retrieved: {patron_count} of {iterator + 2000}')
    iterator += 2000

update_patrons.close()
patron_barcodes.close()
barcode_error.close()