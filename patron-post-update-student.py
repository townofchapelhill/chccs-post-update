import requests
import secrets
import csv
import json
import jsonpickle
import re
from datetime import datetime

# "Patron" object to store collected patron data
class Patron(object):
    def __init__(self, names=None, emails=None, phones=None, pin=None, barcodes=None, patronType=None, expirationDate=None, birthDate=None, addresses=None):
        self.names = []
        self.emails = []
        self.phones = []
        self.pin = ''
        self.barcodes = []
        self.patronType = ''
        self.expirationDate = ''
        self.birthDate = ''
        self.addresses = []

# Lists for storing patron records
all_patrons = []
patron_list = []
non_dupes = []
dupes = []

# Submits patron records to the Sierra API
def sierraPOST():
    # active_patrons_token = get_token()
    for i in non_dupes:
        json_string = jsonpickle.dumps(i, unpicklable=False)
        active_patrons_token = get_token()
        print(active_patrons_token)
        header_text = {"Authorization": "Bearer " + active_patrons_token, "Content-Type": "application/json"}
        # request = requests.post("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons/", data=json_string, headers=header_text)
        request = requests.post("https://sandbox.iii.com:443/iii/sierra-api/v5/patrons/", data=json_string, headers=header_text)
        print(request)
        continue
        if int(request.httpStatus) >= 400:
            print("POST failed")
            print(request.text)
            break

# PUT request
# Loops through list of duplicates
def update_patron():
    # active_patrons_token = get_token()
    for c in dupes:
        # stores id to be passed into the API
        update_id = c['id']
        # removes id from the dict since Sierra won't accept that field
        c.pop('id', None)
        json_string = jsonpickle.dumps(c, unpicklable=False)
        active_patrons_token = get_token()
        print(active_patrons_token)
        header_text = {"Authorization": "Bearer " + active_patrons_token, "Content-Type": "application/json"}
        request = requests.put("https://sandbox.iii.com:443/iii/sierra-api/v5/patrons/" + str(update_id), data=json_string, headers=header_text)
        # request = requests.post("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons/" + str(update_id), data=json_string, headers=header_text)
        # if int(request.text) >= 400:
        #         print("update failed")
        #         print(request)
        #         break
        print(request)
    update_patron()

# runs comparison between retrieved patrons & entries from the csv
# sorts by barcode
def compare_lists():
    for i in range(len(patron_list)):
        try:
            if patron_list[i]['names'][0] == all_patrons[i]['names'][0][0:-2] and patron_list[i]['birthDate'] == all_patrons[i]['birthDate']:
                patron_list[i]['id'] = all_patrons[i]['id']
                dupes.append(patron_list[i])
            else:
                non_dupes.append(patron_list[i])
        except:
            non_dupes.append(patron_list[i])
            
    print("Number of duplicates: " + str(len(dupes)))
    print("Number of non-duplicates: " + str(len(non_dupes)))
    sierraPOST()

# Reads a file and stores patron info the "Patron" object.
# Then pushes each "Patron" into the patron_list array 
def read_csv():
    with open("MOCK_DATA_students.csv", "r", newline='') as file:
        has_header = next(file, None)
        file.seek(0)
        patron_data = csv.reader(file, delimiter=",")
        if has_header:
            next(patron_data)
        for row in patron_data:
            first_last = str(row[3]) + ", " + str(row[2])
            pin_number = re.sub('[^A-Za-z0-9]', '', str(row[4][0:6])) + "00AB" # string required for dev testing, removing for production
            address = str(row[7]) + " " + str(row[8]) + ", " + str(row[9]) + " " + str(row[10])
            barcode = re.sub('[^A-Za-z0-9]', '', str(row[0]))
            print(first_last)
            print(pin_number)
            print(address)
            new_patron = Patron()
            new_patron.names.append(first_last)
            # new_patron.names.append(str(row[1]))
            new_patron.emails.append(str(row[11]))
            new_patron.emails.append(str(row[13]))
            new_patron.barcodes.append(barcode)
            new_patron.phones.append({
                "number": str(row[12]),
                "type": 't'
            })
            new_patron.birthDate = datetime.strptime(row[4], "%m/%d/%Y").strftime("%Y-%m-%d")
            new_patron.expirationDate = datetime.strptime("08/31/2019", "%m/%d/%Y").strftime("%Y-%m-%d")
            new_patron.pin = pin_number
            new_patron.addresses.append({
                "lines": [address],
                "type": "a"
            })
            new_patron.patronType = 15
            patron_list.append(new_patron.__dict__)

# retrieves all patron info for comparison against student info
def get_all_patrons():
    iterator = 0
    active_patrons_token = get_token()

    # while True:
    get_header_text = {"Authorization": "Bearer " + active_patrons_token}
    # get_request = requests.get("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons?offset=" + str(iterator) + "&limit=2000&fields=updatedDate,createdDate,names,barcodes,expirationDate,birthDate,emails,patronType,patronCodes,homeLibraryCode,message,blockInfo,addresses,phones,moneyOwed,fixedFields,varFields&deleted=false", headers=get_header_text)
    get_request = requests.get('https://sandbox.iii.com/iii/sierra-api/v5/patrons?offset=' + str(iterator) +  '&limit=2000&fields=emails,names,addresses,phones,barcodes,patronType,expirationDate', headers=get_header_text)
    data = json.loads(get_request.text)
    print(data)
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

# Calls read_csv() function
read_csv()
# Calls get_all_patrons() to begin function chain
get_all_patrons()
