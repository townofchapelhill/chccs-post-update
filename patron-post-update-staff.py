import requests
import secrets
import csv
import json
import jsonpickle
import re
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
        #request = requests.post("https://sandbox.iii.com/iii/sierra-api/v5/patrons/", data=json_string, headers=header_text)
        if int(request.status_code) == 200:
            found = re.search(sierraPID, request.text)
            if found:
                pid_end = re.search(sierraPID_end, request.text)
                pid = request.text[found.regs[0][0]:pid_end.regs[0][1]-1]
                log_file.write("Patron added: " + pid + ', ' + str(patron.barcodes) + '\n')
                print(f'Added: {pid}, {patron.barcodes}')
        else:
           log_file.write("Failed at record: " + str(identifier) + '\n' + json_string + '\n')
    except:
        pass

# Reads a file and stores patron info the "Patron" object.
# Then pushes each "Patron" into the patron_list array 
def read_csv():
    expiration = date.today() + timedelta(weeks=156)
    expirationDate = expiration.strftime('%Y-%m-%d')
    with open("new_staff_patrons.csv", "r", newline='') as file:
        has_header = next(file, None)
        file.seek(0)
        row_number = 1
        patron_data = csv.reader(file, delimiter=",")
        if has_header:
            next(patron_data)
        for row in patron_data:
            if not row:
                #log_file.write("Row %d is null\n" % row_number)
                continue
            first_last = str(row[3]).upper() + ", " + str(row[2]).upper()
            pin_number = row[1][6:8] + "x" + row[1][8:10]
            if str(row[4]):
                address = str(row[4]).upper() + "$" + str(row[5]).upper() + " " + str(row[6]).upper() + " " + str(row[7])
            else:
                address = ''
            barcode = re.sub('[^A-Za-z0-9]', '', str(row[1]))
            new_patron = Patron()
            new_patron.names.append(first_last)
            new_patron.emails.append(str(row[10]))
            new_patron.barcodes.append(barcode)
            new_patron.phones.append({"number": str(row[8]),"type": 't'})
            if row[9]:
                new_patron.phones.append({"number": str(row[9]),"type": 'p'})
            new_patron.birthDate = datetime.strptime("01/01/1980", "%m/%d/%Y").strftime("%Y-%m-%d")
            new_patron.expirationDate = expirationDate
            new_patron.pin = pin_number
            new_patron.addresses.append({
                "lines": [address],
                "type": "a"
            })
            new_patron.patronType = 15
            new_patron.rowNumber = row_number
            #print(f'name:{new_patron.names},email:{new_patron.emails},barcode:{new_patron.barcodes},phone:{new_patron.phones},PIN:{new_patron.pin},DOB:{new_patron.birthDate},Addr:{new_patron.addresses}')
            sierraPOST(new_patron)

            patron_list.append(new_patron.__dict__)
            row_number += 1

def get_token():
    # url = "https://sandbox.iii.com/iii/sierra-api/v5/token"
    url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v3/token"
    header = {"Authorization": "Basic " + str(secrets.sierra_api_2), "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=header)
    json_response = json.loads(response.text)
    token = json_response["access_token"]
    return token

log_file = open('chccs-log-staff.txt', 'w')
active_patrons_token = get_token()

read_csv()
log_file.close()