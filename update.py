import requests
import secrets
import csv
import json
import jsonpickle
import re
import ast
import datetime

def get_token():
    url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/token"

    # Get the API key from secrets file
    header = {"Authorization": "Basic " + str(secrets.sierra_api_2), "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=header)
    json_response = json.loads(response.text)
    # Create var to hold the response data
    active_patrons_token = json_response["access_token"]
    return active_patrons_token


# "Patron" object to store collected patron data
class Patron(object):
    def __init__(self, id=None, patronType=15):
        self.id = ''
        self.patronType = ''
        self.expirationDate = expirationDate

# calculate new expiration date
expiration = datetime.date.today() + datetime.timedelta(weeks=156)
expirationDate = expiration.strftime('%Y-%m-%d')

def update_patron(patron):
    global active_patrons_token

    update_id = patron.id
    delattr(patron,'id')
    json_string = jsonpickle.dumps(patron, unpicklable=False)
    header_text = {"Authorization": "Bearer " + active_patrons_token, "Content-Type": "application/json"}
    request = requests.put("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons/" + str(update_id), data=json_string, headers=header_text)
    if request.status_code != 204:
        print(f'Status: {request.status_code}, Patron: {json_string}')
    log_file.write(update_id + "," + str(request.status_code) + "\n")

# Reads a file and stores patron info the "Patron" object.
def read_csv():
    global counter
    with open("update_patrons.csv", "r", newline='') as file:
        has_header = next(file, None)
        file.seek(0)
        patron_data = csv.reader(file, delimiter=",")
        for row in patron_data:
          if row:
            #print(row)
            new_patron = Patron()
            new_patron.id = row[0]
            new_patron.patronType = 15
            new_patron.expirationDate = expirationDate
            update_patron(new_patron)
            counter += 1

# Main
counter = 0
log_file = open('chccs-log-update.txt', 'w')
active_patrons_token = get_token()
read_csv()
print(f'Total records updated: {counter}')
log_file.close()