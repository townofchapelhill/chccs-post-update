# CHCCS Patron Process runbook

## A comprehensive run book for processing CHCCS Powerschool data into Sierra

### Goal 
Load new patron records and update the expiration of existing records in Sierra for CHCCS students and staff.

### Purpose 
CHPL provides services, materials, and access to electronic resources to CHCCS staff and students. 

The goal of this process is to pre-populate staff and students into Sierra from CHCCS data sources.
### Methodology 
1) CHCCS provides a data dump of Powerschool records via sFTP to ToCH.
2) Data is held in an encrypted zip file on town\chccs-library
3) On a workstation, run retrieve-patrons.py
4) Output Files
   1) barcode_errors.csv - contains malformed barcodes and non-barcode info in the barcode field, patron ID, and expiration date
   2) patron_barcodes.csv - contains a list of all barcodes and corresponding patron ID for non-deleted patrons. 
   3) Relationship for Patron ID:Barcode -> 1:many
5) Share the barcode_errors file with Tracy, Christie, Tim for cleanup
6) move the patron_barcodes file to town\chccs-library
7) unzip the CHCCS data files
8) run student-match.py and staff-match.\
9) 
10) Output Files
   1)  update_staff_patrons.csv - barcode matched patrons which need patron database expiration date updated
   2)  new_staff_patrons.csv - no barcode match - insert into patron database as a new record
   3)  update_patrons.csv - student barcode matched patrons which need patron database expiration date updated
   4)  new_patrons.csv - no barcode match - insert into patron database as a new student record
11) run patron-post-update-staff.py and patron-post-update-student.py
12) run create-student-patron-production.py
13) create staff records by running (?)
14) securely delete all files generated during this process 
### Data Source
- CHCCS data feed
- Sierra patron extractions
### Output 
- chccs-log-student.txt
- chccs-log-staff.txt

### Constraints
Due to the sensitive nature of the input and log data, no permanent logs of this process are kept. All files produced in the update process are securely deleted at completion. Unencrypted files should not be kept on town\chccs-library past the close of the current working day.