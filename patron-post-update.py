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
all_patrons = []
patron_list = []
non_dupes = []
dupes = []
post_batch = []

# Submits patron records to the Sierra API
def sierraPOST():
    count = 1
    for i in non_dupes:
        post_batch.append(i)
        if len(post_batch) == 100:
            json_string = jsonpickle.dumps(post_batch[0:], unpicklable=False)
            true_json = json_string[1:-1]
            header_text = {"Authorization": "Bearer " + active_patrons_token, "Content-Type": "application/json"}
            # request = requests.post("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons/", data=json_string, headers=header_text)
            request = requests.post("https://sandbox.iii.com:443/iii/sierra-api/v5/patrons/", data=true_json, headers=header_text)
            print(request.text)
            post_batch[:] = []
            continue
            if int(request.status_code) >= 400:
                print("Batch POST failed")
                print(request.text)
                break
        print(count)
        count += 1

# PUT request
# Loops through list of duplicates
def update_patron():
    for c in dupes:
        # stores id to be passed into the API
        update_id = c['id']
        # removes id from the dict since Sierra won't accept that field
        c.pop('id', None)
        json_string = jsonpickle.dumps(c, unpicklable=False)
        header_text = {"Authorization": "Bearer " + active_patrons_token, "Content-Type": "application/json"}
        request = requests.put("https://sandbox.iii.com:443/iii/sierra-api/v5/patrons/" + str(update_id), data=json_string, headers=header_text)
        if int(request.status_code) >= 400:
                print("update failed")
                print(request)
                break
        print(request)

# runs comparison between retrieved patrons & entries from the csv
# sorts by barcode
def compare_lists():
    for i in range(len(patron_list)):
        if patron_list[i]['barcodes'] == all_patrons[i]['barcodes']:
            patron_list[i]['id'] = all_patrons[i]['id']
            dupes.append(patron_list[i])
        else:
            non_dupes.append(patron_list[i])
    print("Number of duplicates: " + str(len(dupes)))
    print("Number of non-duplicates: " + str(len(non_dupes)))
    sierraPOST()
    update_patron()

# Reads a file and stores patron info the "Patron" object.
# Then pushes each "Patron" into the patron_list array 
def read_csv():
    with open("patrons2.csv", "r", newline='') as file:
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
            patron_list.append(new_patron.__dict__)

# retrieves all patron info for comparison against student info
def get_all_patrons():
    get_header_text = {"Authorization": "Bearer " + active_patrons_token}
    get_request = requests.get('https://sandbox.iii.com/iii/sierra-api/v5/patrons/?limit=15000&fields=emails,names,addresses,phones,barcodes,patronType,expirationDate', headers = get_header_text)
    data = json.loads(get_request.text)
    for i in data['entries']:
        all_patrons.append(i)
    print("Number of Patrons retrieved: " + str(len(all_patrons)))
    compare_lists()

# Calls read_csv() function
read_csv()


# Still set for use with the Sierra sandbox, but contains both development & production urls
# url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/token"
url = "https://sandbox.iii.com:443/iii/sierra-api/v5/token"

# Get the API key from secrets file
header = {"Authorization": "Basic " + str(secrets.sandbox_token), "Content-Type": "application/x-www-form-urlencoded"}
response = requests.post(url, headers=header)
json_response = json.loads(response.text)
# Create var to hold the response data
active_patrons_token = json_response["access_token"]

# Calls get_all_patrons() to begin function chain
get_all_patrons()