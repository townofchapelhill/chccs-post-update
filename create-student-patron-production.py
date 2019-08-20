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

# Submits patron records to the Sierra API
def sierraPOST(patron):
    global active_patrons_token
    #log_file.write("Posting new patron records..." + "\n")
    #log_file.write("\n")
    try:
        identifier = patron.rowNumber
        pinIdentifier = patron.pin
        patron.pop('rowNumber', None)
        patron.pop('id', None)
        json_string = jsonpickle.dumps(patron, unpicklable=False)
        print(json_string)
        header_text = {"Authorization": "Bearer " + active_patrons_token, "Content-Type": "application/json"}
        # request = requests.post("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons/", data=json_string, headers=header_text)
        #request = requests.post("https://sandbox.iii.com:443/iii/sierra-api/v5/patrons/", data=json_string, headers=header_text)
        #print(request.status_code)
        #if int(request.status_code) >= 400:
        #    log_file.write("Failed at record: " + str(identifier) + " " + str(i['names']) + " " + str(pinIdentifier) + '\n' + str(request.text) + '\n')
    except:
        pass
    #update_patron()

# PUT request
# Loops through list of duplicates
def update_patron(active_patrons_token):
    
    log_file.write("\n")
    log_file.write("Updating duplicate patron records... " + "\n")
    log_file.write("\n")

    for c in dupes:
        # stores id to be passed into the API
        update_id = c['id']
        identifier = c['rowNumber']
        pinIdentifier = c['pin']
        # removes id from the dict since Sierra won't accept that field
        c.pop('id', None)
        c.pop('rowNumber', None)
        json_string = jsonpickle.dumps(c, unpicklable=False)
        print(json_string)
        header_text = {"Authorization": "Bearer " + active_patrons_token, "Content-Type": "application/json"}
        request = requests.put("https://sandbox.iii.com:443/iii/sierra-api/v5/patrons/" + str(update_id), data=json_string, headers=header_text)
        # request = requests.post("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons/" + str(update_id), data=json_string, headers=header_text)
        print(request.status_code)
        if int(request.status_code) >= 400:
            log_file.write("Failed at record: " + str(identifier) + " " + str(c['names']) + " " + str(pinIdentifier) +  '\n' + str(request.text) + '\n')
    delete_data()

# runs comparison between retrieved patrons & entries from the csv
# sorts by first/last name and birthdate
def compare_lists():
    for student in patron_list:
        non_duplicate = True
        for db_patron in all_patrons:
            # if student['names'][0] == db_patron['names'][0:-2] and student['birthDate'] == db_patron['birthDate']: (Production Conditional)
            try:
                if student['names'][0] == db_patron['names'][0] and student['birthDate'] == db_patron['birthDate']:
                    student['id'] = db_patron['id']
                    non_duplicate = False
                    dupes.append(student)
                    break
            except:
                continue
        if non_duplicate == True:
            non_dupes.append(student)

    # writes to log file with number of duplicates & non-duplicates   
    log_file.write("Number of duplicates: " + str(len(dupes)) + "\n")
    print("Number of non-duplicates: " + str(len(non_dupes)))
    print("Number of duplicates: " + str(len(dupes)))
    log_file.write("Number of non-duplicates: " + str(len(non_dupes)) + '\n')
    log_file.write("\n")
    sierraPOST()

# Reads a file and stores patron info in "Patron" object.
# Then pushes each "Patron" into patron_list array 
def read_csv():
    expiration = date.today() + timedelta(weeks=156)
    expirationDate = expiration.strftime('%Y-%m-%d')
    zipcode = re.compile(r'\d{5}')
    print(f'Expiration Date: {expirationDate}')
    with open("mock-student.csv", mode='r') as file:
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
           first_last = str(row[3]) + ", " + str(row[2])
           pin_number = str(row[4][0:2]) + "x" + str(row[4][3:5])
           offset = 0
           if re.search(zipcode, str(row[10])):
               address = str(row[7]) + " " + str(row[8]) + ", " + str(row[9]) + " " + str(row[10])
           elif re.search(zipcode, str(row[11])):
               offset = 1
               address = str(row[7]) + " " + str(row[8]) + ", " + str(row[9]) + " " + str(row[10]) + " " + str(row[11])
           else:
               log_file.write("Row format problem: %s\n" % row)
               continue
           barcode = re.sub('[^A-Za-z0-9]', '', str(row[1]))
           new_patron = Patron()
           new_patron.birthDate = datetime.strptime(str(row[4]), "%m/%d/%Y").strftime("%Y-%m-%d")
           new_patron.names.append(first_last)
           new_patron.emails.append(str(row[11+offset]))
           new_patron.emails.append(str(row[13+offset]))
           new_patron.emails.append(str(row[14+offset]))
           new_patron.barcodes.append(str(barcode))
           new_patron.phones.append({"number": str(row[12+offset]),"type": 't'})
           new_patron.expirationDate = expirationDate
           new_patron.pin = pin_number
           new_patron.addresses.append({"lines": [address], "type": "a"})
           new_patron.patronType = 15
           new_patron.rowNumber = row_number
           print(f'name:{new_patron.names},email:{new_patron.emails},barcode:{new_patron.barcodes},phone:{new_patron.phones},PIN:{new_patron.pin},DOB:{new_patron.birthDate},Addr:{new_patron.addresses}')
           sierraPOST(new_patron)
           patron_list.append(new_patron.__dict__)

           row_number += 1
 #       except IndexError:
 #         print(f'Key Error on patron record')
 #         next(patron_data)

# retrieves all patron info for comparison against student info
def get_all_patrons(active_patrons_token):
    iterator = 1671000

    while True:
        get_header_text = {"Authorization": "Bearer " + active_patrons_token}
        # get_request = requests.get("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons?offset=" + str(iterator) + "&limit=2000&fields=updatedDate,createdDate,names,barcodes,expirationDate,birthDate,emails,patronType,patronCodes,homeLibraryCode,message,blockInfo,addresses,phones,moneyOwed,fixedFields,varFields&deleted=false", headers=get_header_text)
        get_request = requests.get('https://sandbox.iii.com/iii/sierra-api/v5/patrons?offset=' + str(iterator) +  '&limit=2000&fields=emails,names,addresses,phones,barcodes,patronType,expirationDate,birthDate', headers=get_header_text)
        data = json.loads(get_request.text)
        try:
            for i in data['entries']:
                all_patrons.append(i)
        except:
            compare_lists()
            break
        print("Number of Patrons retrieved: " + str(len(all_patrons)))
        iterator += 2000
        print(iterator)


def get_token():
    # url = "https://sandbox.iii.com/iii/sierra-api/v5/token"

    url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v3/token"
    header = {"Authorization": "Basic " + str(secrets.sierra_api), "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=header)
    json_response = json.loads(response.text)
    token = json_response["access_token"]
    return token

def delete_data():
    try:
        os.remove("./MOCK_DATA.csv")
    except:
        sys.exit()

log_file = open('chccs-log-student.txt', 'w+')
active_patrons_token = get_token()

read_csv()

# Calls get_all_patrons() to begin function chain
# get_all_patrons()
log_file.close()