import requests
import secrets
import csv
import json
import jsonpickle
import re
from datetime import datetime

# "Patron" object to store collected patron data
class Patron(object):
    def __init__(self, names=None, emails=None, phones=None, pin=None, barcodes=None, patronType=None, expirationDate=None, birthDate=None, addresses=None, rowNumber=None):
        self.names = []
        self.emails = []
        self.phones = []
        self.pin = ''
        self.barcodes = []
        self.patronType = ''
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
def sierraPOST():
    
    log_file.write("Posting new patron records..." + "\n")
    log_file.write("\n")

    for i in non_dupes:
        identifier = i['rowNumber']
        pinIdentifier = i['pin']
        i.pop('id', None)
        i.pop('rowNumber', None)
        json_string = jsonpickle.dumps(i, unpicklable=False)
        print(json_string)
        active_patrons_token = get_token()
        header_text = {"Authorization": "Bearer " + active_patrons_token, "Content-Type": "application/json"}
        # request = requests.post("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons/", data=json_string, headers=header_text)
        request = requests.post("https://sandbox.iii.com:443/iii/sierra-api/v5/patrons/", data=json_string, headers=header_text)
        print(request.status_code)
        if int(request.status_code) >= 400:
            log_file.write("Failed at record: " + str(identifier) + " " + str(i['names']) + " " + str(pinIdentifier) + '\n' + str(request.text) + '\n')
    update_patron()

# PUT request
# Loops through list of duplicates
def update_patron():
    
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
        active_patrons_token = get_token()
        header_text = {"Authorization": "Bearer " + active_patrons_token, "Content-Type": "application/json"}
        request = requests.put("https://sandbox.iii.com:443/iii/sierra-api/v5/patrons/" + str(update_id), data=json_string, headers=header_text)
        # request = requests.post("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons/" + str(update_id), data=json_string, headers=header_text)
        print(request.status_code)
        if int(request.status_code) >= 400:
            log_file.write("Failed at record: " + str(identifier) + " " + str(c['names']) + " " + str(pinIdentifier) +  '\n' + str(request.text) + '\n' + '\n')

# runs comparison between retrieved patrons & entries from the csv
# sorts by first/last name and birthdate
def compare_lists():
    for staff in patron_list:
        non_duplicate = True
        for db_patron in all_patrons:
            # if student['names'][0] == db_patron['names'][0:-2]: (Production Conditional)
            if staff['names'][0] == db_patron['names'][0]:
                staff['id'] = db_patron['id']
                non_duplicate = False
                dupes.append(staff)
                break
        if non_duplicate == True:
            non_dupes.append(staff)

    # writes to log file with number of duplicates & non-duplicates
    log_file.write("Number of duplicates: " + str(len(dupes)) + "\n")
    print("Number of non-duplicates: " + str(len(non_dupes)))
    print("Number of duplicates: " + str(len(dupes)))
    log_file.write("Number of non-duplicates: " + str(len(non_dupes)) + '\n')
    log_file.write("\n")
    sierraPOST()

# Reads a file and stores patron info the "Patron" object.
# Then pushes each "Patron" into the patron_list array 
def read_csv():
    with open("MOCK_DATA_staff.csv", "r", newline='') as file:
        has_header = next(file, None)
        file.seek(0)
        patron_data = csv.reader(file, delimiter=",")
        row_number = 2
        if has_header:
            next(patron_data)
        for row in patron_data:
            first_last = str(row[2]) + ", " + str(row[1])
            pin_number = "123456AB" # Birthdates may not be provided, will need workaround to generate PIN
            address = str(row[4]) + " " + str(row[5]) + ", " + str(row[6]) + " " + str(row[7])
            barcode = re.sub('[^A-Za-z0-9]', '', str(row[0]))
            new_patron = Patron()
            new_patron.names.append(first_last)
            # new_patron.names.append(str(row[1]))
            new_patron.emails.append(str(row[8]))
            # new_patron.emails.append(str(row[13]))
            new_patron.barcodes.append(barcode)
            new_patron.phones.append({
                "number": "555-555-5555",
                "type": 't'
            })
            new_patron.birthDate = datetime.strptime("01/01/1980", "%m/%d/%Y").strftime("%Y-%m-%d")
            new_patron.expirationDate = datetime.strptime("08/31/2019", "%m/%d/%Y").strftime("%Y-%m-%d")
            new_patron.pin = pin_number
            new_patron.addresses.append({
                "lines": [address],
                "type": "a"
            })
            new_patron.patronType = 15
            new_patron.rowNumber = row_number
            patron_list.append(new_patron.__dict__)
            row_number += 1

# retrieves all patron info for comparison against student info
def get_all_patrons():
    iterator = 1672000
    active_patrons_token = get_token()

    # while True:
    get_header_text = {"Authorization": "Bearer " + active_patrons_token}
    # get_request = requests.get("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons?offset=" + str(iterator) + "&limit=2000&fields=updatedDate,createdDate,names,barcodes,expirationDate,birthDate,emails,patronType,patronCodes,homeLibraryCode,message,blockInfo,addresses,phones,moneyOwed,fixedFields,varFields&deleted=false", headers=get_header_text)
    get_request = requests.get('https://sandbox.iii.com/iii/sierra-api/v5/patrons?offset=' + str(iterator) +  '&limit=2000&fields=emails,names,addresses,phones,barcodes,patronType,expirationDate', headers=get_header_text)
    data = json.loads(get_request.text)
    # try:
    for i in data['entries']:
        all_patrons.append(i)
    # except:
        # compare_lists()
        # break
    print("Number of Patrons retrieved: " + str(len(all_patrons)))
        # iterator += 2000
        # print(iterator)
    compare_lists()


def get_token():
    # Still set for use with the Sierra sandbox, but contains both development & production urls
    # url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/token"
    url = "https://sandbox.iii.com:443/iii/sierra-api/v5/token"

    # Get the API key from secrets file
    header = {"Authorization": "Basic " + str(secrets.sandbox_token), "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=header)
    json_response = json.loads(response.text)
    # Create var to hold the response data
    active_patrons_token = json_response["access_token"]
    return active_patrons_token

log_file = open('chccs-log-staff.txt', 'w')

# Calls read_csv() function
read_csv()
# Calls get_all_patrons() to begin function chain
get_all_patrons()

