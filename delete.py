import requests
import secrets
import csv
import json
import jsonpickle
import re
from datetime import datetime

# DELETE request
def delete_patron(delete_id):
        global active_patrons_token
        header_text = {"Authorization": "Bearer " + active_patrons_token, "Content-Type": "application/json"}
        request = requests.delete("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons/" + str(delete_id), headers=header_text)
        #request = requests.delete("https://sandbox.iii.com/iii/sierra-api/v5/patrons/" + str(delete_id), headers=header_text)
        #print(request.text)
        print(f'Record: {delete_id} Status: {request.status_code}')
        

# Reads a file and stores patron info the "Patron" object.
# Then pushes each "Patron" into the patron_list array 
def read_csv():
    with open("/Users/dpcolar/Google Drive/TOCH/chccs-post-update/data/delete_patrons.csv", "r", newline='') as file:
        has_header = next(file, None)
        file.seek(0)
        patron_data = csv.reader(file, delimiter=",")
        if has_header:
            next(patron_data)
        for row in patron_data:
            delete_patron(row[0])

def get_token():
    #url = "https://sandbox.iii.com/iii/sierra-api/v5/token"
    url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v3/token"
    header = {"Authorization": "Basic " + str(secrets.sierra_api_2), "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=header)
    json_response = json.loads(response.text)
    token = json_response["access_token"]
    return token

active_patrons_token = get_token()
# Calls read_csv() function
read_csv()
