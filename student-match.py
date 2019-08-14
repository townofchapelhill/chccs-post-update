# Match Student record to barcode
# Inputs
# barcode table - a csv loaded into a Dict
# Student file - a csv from CHCCS with all student records

import csv

update_patrons = open("update_patrons.csv", encoding='utf-8', mode='w+')
update_patron = csv.writer(update_patrons)

new_patrons = open("new_patrons.csv", encoding='utf-8', mode='w+')
create_patron = csv.writer(new_patrons)

barcode_dict = {}
updates = 0
inserts = 0
records = 0

# load the dictionary
with open("patron_barcodes.csv") as lookup_file:
    try:
        barcode_match = csv.DictReader(lookup_file) 
        for row in barcode_match:
            barcode_dict[row['Barcode']] = row['Patron ID']
    except KeyError:
        print(f'duplicate barcode detected {row}')
    


# read and process the student file
with open("CHCCS_Students_upload.csv", encoding='utf-8') as student_file:
    students = csv.reader(student_file, delimiter=',')
    for student in students:
        records += 1
        try:
            matched = barcode_dict[student[1]]
            student[0] = matched
            update_patron.writerow(student)
            updates += 1
        except KeyError:
            create_patron.writerow(student)
            inserts += 1

print(f'Total read: {records}, New: {inserts}, Updates: {updates}')
new_patrons.close()
update_patrons.close()