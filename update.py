import requests
import secrets
import csv
import json
import jsonpickle
import re
import ast
from datetime import datetime

# "Patron" object to store collected patron data
class Patron(object):
    def __init__(self, id=None, emails=None, phones=None, barcodes=None, patronType=None):
        self.id = ''
        self.emails = []
        self.phones = ''
        self.barcodes = ''
        self.patronType = ''

# List for storing patron records
patron_list = []


# PUT request
# Loops through list of duplicates
def update_patron():

    for c in patron_list:
        # stores id to be passed into the API
        update_id = c['id']
        # removes id from the dict since Sierra won't accept that field
        c.pop('id', None)
        json_string = jsonpickle.dumps(c, unpicklable=False)
        active_patrons_token = get_token()
        header_text = {"Authorization": "Bearer " + active_patrons_token, "Content-Type": "application/json"}
        request = requests.put("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons/" + str(update_id), data=json_string, headers=header_text)
        print(request.text)
        log_file.write("Record: " + update_id + " HTTP Status: " + request.text + "\n")
        log_file.write("\n")

# Reads a file and stores patron info the "Patron" object.
# Then pushes each "Patron" into the patron_list array 
def read_csv():
    with open("update_patrons.csv", "r", newline='') as file:
        has_header = next(file, None)
        file.seek(0)
        patron_data = csv.reader(file, delimiter=",")
        if has_header:
            next(patron_data)
        for row in patron_data:
            emails = re.sub('[ ]', '', str(row[2]))
            barcodes_array = row[4].split(", ")
            phones_array = row[3].split(" | ")
            print(phones_array)
            new_phones_array = []
            for i in phones_array:
                try:
                    phone_dict = ast.literal_eval(i)
                    new_phones_array.append(phone_dict)
                except: 
                    continue
            print(new_phones_array)
            new_patron = Patron()
            new_patron.id = row[0]
            new_patron.emails.append(emails)
            new_patron.barcodes = barcodes_array
            new_patron.phones = new_phones_array
            new_patron.patronType = 15
            patron_list.append(new_patron.__dict__)
    update_patron()

def get_token():
    url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/token"

    # Get the API key from secrets file
    header = {"Authorization": "Basic " + str(secrets.sierra_api_2), "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=header)
    json_response = json.loads(response.text)
    # Create var to hold the response data
    active_patrons_token = json_response["access_token"]
    return active_patrons_token

log_file = open('chccs-log-update.txt', 'w')

# Calls read_csv() function
read_csv()
