# This script was created to perform database cleanup after the inital upload of CHCCS data
# If the database needs to be cleaned again after the next upload then this script can help

import secrets
import csv
import json
import jsonpickle
import re
import itertools
import os
from datetime import datetime
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import requests

# Constructor to store Patron data
class Patron(object):
    def __init__(self, id=None, names=None, emails=None, phones=None, pin=None, barcodes=None, patronType=None, expirationDate=None, birthDate=None, addresses=None):
        self.id = ''
        self.names = ''
        self.emails = ''
        self.phones = ''
        self.pin = ''
        self.barcodes = ''
        self.patronType = ''
        self.expirationDate = ''
        self.birthDate = ''
        self.addresses = []
    
    # Hash method, makes comparison faster
    def __hash__(self):
        return hash(self.__key())

# Lists for storing patron records
all_patrons = []
patron_list = []
to_delete = []
to_update = []

# Function compares the entries of the patron list by calculating a ratio produced from fuzzywuzzy
# Ratio was necessary to capture patron records that were the same person, but one record had a middle initial
# Range of acceptable ratio is 93-96, reliably captures names that differ by 1 letter
def narrow_search():
    count = 0
    for i in patron_list:
        name1 = i['names']
        # Not all records have birthdays inputted, hence try/catch
        try:
            bDay1 = datetime.strptime(i['birthDate'], "%Y-%m-%d")
        except:
            pass
        for j in patron_list:
            name2 = j['names']
            try:
                bDay2 = datetime.strptime(j['birthDate'], "%Y-%m-%d")
            except:
                pass

            # Produce ratio
            ratio = fuzz.ratio(name1, name2)

            # Rules for comparison
            rules = [ratio >= 93,
                     ratio <= 96,
                     bDay1 == bDay2]
            
            # if match is found, exchange emails, phone numbers, & barcodes
            if all(rules):
                count += 1
                print("Found:" + str(count))
                if len(name1) < len(name2) or len(name1) == len(name2):
                    if j['emails'] != i['emails']:
                        j['emails'] = j['emails'] + ", " + i['emails']
                    if j['phones'] != i['phones']:
                        j['phones'] = j['phones'] + ", " + i['phones']
                    if j['barcodes'] != i['barcodes']:
                        j['barcodes']= j['barcodes'] + ", " + i['barcodes']

                    # Place "j" iterators in update list
                    to_update.append(j)
                    # Place "i" iterators in delete list
                    to_delete.append(i)
            else:
                continue
    print(len(to_update))
    print(len(to_delete))
    write_csv()



# Reads a file and stores patron info the "Patron" object.
# Then pushes each "Patron" into the patron_list array
def read_csv():
    with open("all_patrons.csv", "r", newline='') as file:
        has_header = next(file, None)
        file.seek(0)
        patron_data = csv.reader(file, delimiter=",")
        row_number = 2
        if has_header:
            next(patron_data)
        for row in patron_data:
            names = re.sub('[^A-Za-z0-9_\-\.:,@ ]', '', str(row[1]))
            email = re.sub('[^A-Za-z0-9_\-\.:,@ ]', '', str(row[4])).upper()
            barcodes = re.sub('[^A-Za-z0-9_\-\.:,@ ]', '', str(row[2]))
            phones = row[7][1:-1]
            new_patron = Patron()
            new_patron.id = str(row[0])
            new_patron.names = names
            new_patron.emails = email
            new_patron.barcodes = barcodes
            new_patron.phones = phones
            new_patron.birthDate = str(row[3])
            patron_list.append(new_patron.__dict__)
            row_number += 1
        print(len(patron_list))
    narrow_search()

# write the CSV's of final lists
def write_csv():
    # This CSV will contain the records that will be updated with update.py
    with open("update_patrons.csv", "w+") as update_patrons:
        
        if os.stat('update_patrons.csv').st_size == 0:
            fieldnames = patron_list[0].keys()
            csv_writer = csv.DictWriter(update_patrons, fieldnames=fieldnames, extrasaction='ignore', delimiter=',')
            csv_writer.writeheader()
        
        for entry in to_update:
            csv_writer.writerow(entry)
    
    # This CSV will contain the records that will be deleted with delete.py
    with open("delete_patrons.csv", "w+") as delete_patrons:
        
        if os.stat('delete_patrons.csv').st_size == 0:
            fieldnames = patron_list[0].keys()
            csv_writer = csv.DictWriter(delete_patrons, fieldnames=fieldnames, extrasaction='ignore', delimiter=',')
            csv_writer.writeheader()
        
        for entry in to_delete:
            csv_writer.writerow(entry)

# log file
log_file = open('chccs-delete.txt', 'w')

# Calls read_csv() function
read_csv()

