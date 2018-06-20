import requests
import secrets
import csv
import json
import jsonpickle
import datetime

# "Patron" object to store collected patron data
class Patron(object):
    def __init__(self, names=None, emails=None, phones=None, pin=None, barcodes=None, patronType=None, expirationDate=None):
        self.names = []
        self.emails = []
        self.phones = []
        self.pin = ''
        self.barcodes = []
        self.patronType = ''
        self.expirationDate = ''

# Lists for storing patron records
patron_list = []
post_batch = []

# Submits patron records to the Sierra API
# Attempting a batch POST method, but unsure if Sierra allows for it
def sierraPOST():
    count = 1
    for i in patron_list:
        post_batch.append(i)
        if len(post_batch) == 100:
            json_string = jsonpickle.dumps(post_batch[0:], unpicklable=False)
            true_json = json_string[1:-1]
            print(true_json)
            header_text = {"Authorization": "Bearer " + active_patrons_token, "Content-Type": "application/json"}
            # request = requests.post("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons/", data=json_string, headers=header_text)
            request = requests.post("https://sandbox.iii.com:443/iii/sierra-api/v5/patrons/", data=true_json, headers=header_text)
            print(request)
            post_batch[:] = []
            continue
            if int(request.status_code) != 200:
                print("Batch POST failed")
                break
        print(count)
        count += 1

# Reads a file and stores patron info the "Patron" object.
# Then pushes each "Patron" into the patron_list array 
def read_csv():
    with open("patrons.csv", "r", newline='') as file:
        has_header = csv.Sniffer().has_header(file.read(1024))
        file.seek(0)
        patron_data = csv.reader(file, delimiter=",")
        if has_header:
            next(patron_data)
        for row in patron_data:
            new_patron = Patron()
            new_patron.emails.append(str(row[3]))
            new_patron.names.append(str(row[0]))
            new_patron.phones.append({
                "number": str(row[2]),
                "type": 't'
            })
            new_patron.pin = "123456AB"
            new_patron.barcodes.append("24708351111")
            new_patron.patronType = 0
            new_patron.expirationDate = "2017-09-23"
            patron_list.append(new_patron)

# Calls read_csv() function
read_csv()

# Still set for use with the Sierra sandbox, but contains both development & production urls
# url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/token"
url = "https://sandbox.iii.com:443/iii/sierra-api/v5/token"

# Get the API key from secrets.py
header = {"Authorization": "Basic " + str(secrets.sandbox_token), "Content-Type": "application/x-www-form-urlencoded"}
response = requests.post(url, headers=header)
json_response = json.loads(response.text)
print(json_response)
# Create var to hold the response data
active_patrons_token = json_response["access_token"]

# Purely for testing purposes, will be removed when script is finalized
# get_header_text = {"Authorization": "Bearer " + active_patrons_token}
# get_request = requests.get('https://sandbox.iii.com/iii/sierra-api/v5/patrons/?limit=100&fields=emails,names,addresses,phones,barcodes,patronType,expirationDate', headers=get_header_text)
# print(json.loads(get_request.text))


# Calls sierraPOST() function
sierraPOST()