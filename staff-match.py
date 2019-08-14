# Match staff record to barcode
# Inputs
# barcode table - a csv loaded into a Dict
# staff file - a csv from CHCCS with all staff records

import csv

update_patrons = open("update_staff_patrons.csv", encoding='utf-8', mode='w+')
update_patron = csv.writer(update_patrons)

new_patrons = open("new_staff_patrons.csv", encoding='utf-8', mode='w+')
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
    


# read and process the staff file
with open("CHCCS_staff.csv", encoding='utf-8') as staff_file:
    staffs = csv.reader(staff_file, delimiter=',')
    for staff in staffs:
        records += 1
        try:
            matched = barcode_dict[staff[1]]
            staff[0] = matched
            update_patron.writerow(staff)
            updates += 1
        except KeyError:
            create_patron.writerow(staff)
            inserts += 1

print(f'Total read: {records}, New: {inserts}, Updates: {updates}')
new_patrons.close()
update_patrons.close()