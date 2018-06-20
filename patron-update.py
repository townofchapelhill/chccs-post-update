# imports dependencies
import requests
import secrets
import json
import jsonpickle
import datetime

# initializes "Patron" object
class Patron(object):
    def __init__(self, id=None, names=None, emails=None, addresses=None, phones=None, pin=None, barcodes=None, patronType=None, expirationDate=None):
        self.id = ''
        self.names = ''
        self.emails = ''
        self.addresses = ''
        self.phones = ''
        self.pin = '123456AB'
        self.barcodes = ''
        self.patronType = ''
        self.expirationDate = ''

# stores retrieved patron data       
patron_list = []

# PUT request, does the actualy updating
def update_patron():
    final_patron = patron_list[0]
    json_string = jsonpickle.dumps(final_patron, unpicklable=False)
    print(json_string)
    header_text = {"Authorization": "Bearer " + active_patrons_token, "Content-Type": "application/json"}
    request = requests.put("https://sandbox.iii.com:443/iii/sierra-api/v5/patrons/" + str(final_patron.id), data=json_string, headers=header_text)
    print(request)

# Navigation function to direct user for updating certain attributes
def navigator():
    print("Type in which patron attribute you'd like to change")
    director = input("name, email, phone, pin, barcode, patron type, expiration date: ")
    if director == 'name':
        change_name()
    if director == 'email':
        change_email()
    if director == 'phone':
        change_phone()
    if director == 'pin':
        change_pin()
    if director == 'barcode':
        change_barcode()
    if director == 'patron type':
        change_patronType()
    if director == 'expiration date':
        change_expirationDate()

# Changes name based on user input
def change_name():
    updated_patron = patron_list[0]
    updated_patron.names.pop()
    print('What would you like to change the name to?')
    new_name = input("Type here: ")
    updated_patron.names.append(new_name)
    reDirector = input("Would you like to alter another attribute? (Y/N)")
    if reDirector == 'Y':
        navigator()
    else:
        update_patron()

# Changes email based on user input
def change_email():
    updated_patron = patron_list[0]
    updated_patron.emails.pop()
    print('What would you like to change the email to?')
    new_email = input("Type here: ")
    updated_patron.emails.append(new_email)
    reDirector = input("Would you like to alter another attribute? (Y/N)")
    if reDirector == 'Y':
        navigator()
    else:
        update_patron()

# Under construction
# def change_address():
    

# def change_phone():
    

# def change_pin():
    

# def change_barcode():
    

# def change_patronType():
    

# def change_expirationDate():

# Currently searches for a patron by ID number and then updates "Patron" object
# will be split into 2 functions to improve flow
def search_patron():
    patronId = input("What's the patron Id number? ")
    get_header_text = {"Authorization": "Bearer " + active_patrons_token}
    # get_request = requests.get('https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/patrons/' + patronId, headers=get_header_text)
    get_request = requests.get('https://sandbox.iii.com/iii/sierra-api/v5/patrons/' + patronId, headers=get_header_text)
    patron = json.loads(get_request.text)
    patron2 = patron.entries
    print(get_request)
    print(patron2)
    new_patron = Patron()
    new_patron.id = patron['id']
    new_patron.names = patron['names'[0:]]
    new_patron.barcodes = patron['barcodes'[0:]]
    new_patron.expirationDate = patron['expirationDate']
    new_patron.emails = patron['emails'[0:]]
    new_patron.patronType = patron['patronType']
    new_patron.addresses = patron['addresses'[0:]]
    new_patron.phones = patron['phones'[0:]]
    new_patron.pin = patron['pin']
    patron_list.append(new_patron)
    print(jsonpickle.dumps(new_patron, unpicklable=False))
    navigator()

# Setting urls, can switch between sandbox & production
# url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/token"
url = "https://sandbox.iii.com:443/iii/sierra-api/v5/token"

# Get the API key from secrets.py
header = {"Authorization": "Basic " + str(secrets.sandbox_token), "Content-Type": "application/x-www-form-urlencoded"}
response = requests.post(url, headers=header)
json_response = json.loads(response.text)

# Create var to hold the response data
active_patrons_token = json_response["access_token"]
get_header_text = {"Authorization": "Bearer " + active_patrons_token}
get_request = requests.get('https://sandbox.iii.com/iii/sierra-api/v5/patrons/?limit=1&fields=id,emails,names,addresses,phones,barcodes,patronType,expirationDate,birthDate,patronCodes,blockInfo,uniqueIds,pMessage,homeLibraryCode,langPref,fixedFields,varFields', headers=get_header_text)

# prints test data for comparison
print(json.loads(get_request.text))

# calls search_patron
search_patron()

