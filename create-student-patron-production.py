import requests
import secrets
import csv
import json
import jsonpickle
import re
import os
import sys
from datetime import datetime, timedelta, date

# "Patron" object to store collected patron data
class Patron(object):
    def __init__(self, names=None, emails=None, phones=None, pin=None, barcodes=None, patronType=None, expirationDate=None, birthDate=None, addresses=None, rowNumber=None):

        self.names = []
        self.emails = []
        self.phones = []
        self.pin = ''
        self.barcodes = []
        self.patronType = 15
        self.expirationDate = ''
        self.birthDate = ''
        self.addresses = []
        self.rowNumber = ''

# Lists for storing patron records
all_patrons = []
patron_list = []
non_dupes = []
dupes = []

# search strings
sierraPID = re.compile(r'\d{6}')
sierraPID_end = re.compile(r'\d+\"')

# Submits patron records to the Sierra API
def sierraPOST(patron):
    global active_patrons_token
    global sierraPID
    global sierraPID_end
    try:
        identifier = patron.rowNumber
        pinIdentifier = patron.pin
        delattr(patron,'rowNumber')
        json_string = jsonpickle.dumps(patron, unpicklable=False)
        #print(json_string)
        header_text = {"Authorization": "Bearer " + active_patrons_token, "Content-Type": "application/json"}
        request = requests.post("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons/", data=json_string, headers=header_text)
        #request = requests.post("https://sandbox.iii.com:443/iii/sierra-api/v5/patrons/", data=json_string, headers=header_text)
        #print(request.status_code)
        #print(request.text)
        
        if int(request.status_code) == 200:
            found = re.search(sierraPID, request.text)
            if found:
                pid_end = re.search(sierraPID_end, request.text)
                pid = request.text[found.regs[0][0]:pid_end.regs[0][1]-1]
                log_file.write("Patron added: " + pid + '\n' + json_string + '\n')
        else:
           log_file.write("Failed at record: " + str(identifier) + '\n' + json_string + '\n')
    except:
        pass

# Reads a file and creates a patron.
def read_csv():
    expiration = date.today() + timedelta(weeks=156)
    expirationDate = expiration.strftime('%Y-%m-%d')
    zipcode = re.compile(r'\d{5}')
    email_match = re.compile(r'[@]')

    print(f'Expiration Date: {expirationDate}')
    with open("/Users/dpcolar/Google Drive/TOCH/chccs-post-update/data/mock-student.csv", mode='r') as file:
        has_header = next(file, None)
        file.seek(0)
        row_number = 1
        patron_data = csv.reader(file, delimiter=",")
        if has_header:
            next
#        try: 
        for row in patron_data:
           if not row:
             #log_file.write("Row %d is null\n" % row_number)
             continue
           #print(f'Patron Record: {row}')
           first_last = str(row[3]).upper() + ", " + str(row[2]).upper()
           pin_number = str(row[4][0:2]) + "x" + str(row[4][3:5])
           offset = 0
           if re.search(zipcode, str(row[10])):
               address = str(row[7]).upper() + "$" + str(row[8]).upper() + " " + str(row[9]).upper() + " " + str(row[10])
           elif re.search(zipcode, str(row[11])):
               offset = 1
               address = str(row[7]).upper() + " " + str(row[8]).upper() + "$" + str(row[9]).upper() + " " + str(row[10]) + " " + str(row[11])
           else:
               log_file.write("Row format problem: %s\n" % row)
               continue
           address = re.sub('[.]','',address)
           barcode = re.sub('[^A-Za-z0-9]', '', str(row[1]))
           new_patron = Patron()
           new_patron.birthDate = datetime.strptime(str(row[4]), "%m/%d/%Y").strftime("%Y-%m-%d")
           new_patron.names.append(first_last)
           email = []
           if re.search(email_match, str(row[11+offset])):
               email.append(str(row[11+offset]))
           if re.search(email_match, str(row[13+offset])):
               email.append(str(row[13+offset]))
           if re.search(email_match, str(row[14+offset])):
               email.append(str(row[14+offset]))
           if len(email):
               new_patron.emails.append(",".join(email))
           new_patron.barcodes.append(str(barcode))
           new_patron.phones.append({"number": str(row[12+offset]),"type": 't'})
           new_patron.expirationDate = expirationDate
           new_patron.pin = pin_number
           new_patron.addresses.append({"lines": [address], "type": "a"})
           new_patron.patronType = 15
           new_patron.rowNumber = row_number
           # print(f'name:{new_patron.names},email:{new_patron.emails},barcode:{new_patron.barcodes},phone:{new_patron.phones},PIN:{new_patron.pin},DOB:{new_patron.birthDate},Addr:{new_patron.addresses}')
           sierraPOST(new_patron)
           patron_list.append(new_patron.__dict__)
           row_number += 1

 #       except IndexError:
 #         print(f'Key Error on patron record')
 #         next(patron_data)

def get_token():

    # url = "https://sandbox.iii.com/iii/sierra-api/v5/token"
    url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v3/token"
    header = {"Authorization": "Basic " + str(secrets.sierra_api_2), "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=header)
    json_response = json.loads(response.text)
    token = json_response["access_token"]
    return token

# MAIN 
log_file = open('chccs-log-student.txt', 'w+')
active_patrons_token = get_token()
read_csv()
log_file.close()