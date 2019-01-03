import requests
import secrets
import csv
import json
import jsonpickle
import re
import os
from datetime import datetime

# Lists for storing patron records
all_patrons = []

# retrieves all patron info for comparison against student info
def get_all_patrons():
    iterator = 0
    active_patrons_token = get_token()

    while True:
        get_header_text = {"Authorization": "Bearer " + active_patrons_token}
        get_request = requests.get("https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons?offset=" + str(iterator) + "&limit=2000&fields=id,names,barcodes,birthDate,emails,patronType,addresses,phones&deleted=false", headers=get_header_text)
        data = json.loads(get_request.text)
        try:
            for i in data['entries']:
                all_patrons.append(i)
        except:
            write_csv()
            break
        print("Number of Patrons retrieved: " + str(len(all_patrons)))
        iterator += 2000
        print(iterator)

def write_csv():
    with open("all_patrons.csv", "w+") as update_patrons:
        
        if os.stat('all_patrons.csv').st_size == 0:
            fieldnames = all_patrons[0].keys()
            csv_writer = csv.DictWriter(update_patrons, fieldnames=fieldnames, extrasaction='ignore', delimiter=',')
            csv_writer.writeheader()
        
        for entry in all_patrons:
            csv_writer.writerow(entry)

def get_token():
    url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/token"

    # Get the API key from secrets file
    header = {"Authorization": "Basic " + str(secrets.sierra_api_2), "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=header)
    json_response = json.loads(response.text)
    # Create var to hold the response data
    active_patrons_token = json_response["access_token"]
    return active_patrons_token

get_all_patrons()