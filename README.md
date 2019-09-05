# chccs-post-update
These scripts are used as utilities to aid in the IDea Project for the Town of Chapel Hill

## delete.py
Mark Sierra records as deleted via the API
### Input 
A csv file (delete_patrons.csv) containing the Sierra PID

## retrieve-patrons.py
Retrieve all patron records that are not marked for delete
### Input
via the Sierra API - retrieve patron record

Note: Ptype=15 are CHCCS students and staff

### Output
#### all_patrons.csv  -- all selected patrons
#### patron_barcodes.csv -- barcode:PID
#### barcode_errors.csv -- malformed barcodes 
For record cleanup and debugging


## staff-match.py
Match incoming records against a barcode:PID dictionary

Note: assumes barcode is globally unique to a PID, will report key errors
### Input
#### patron_barcodes.csv -- csv file containing the barcode:PID
The staff csv file from CHCCS (CHCCS_staff.csv)
### Output
#### new_staff_patrons.csv -- csv file with staff records to add to Sierra
Format
```
Employment Status
UIDStaffID
FirstName
LastName
Address1
City
State
Zip
Mobile Phone
Home Phone
Email
PR Job Desc.
PrimarySiteId
Site Name
```
## student-match.py
Match incoming records against a barcode:PID dictionary

Note: assumes barcode is globally unique to a PID, will report key errors
### Input
#### patron_barcodes.csv -- csv file (patron_barcodes.csv) containing the barcode:PID
#### CHCCS_Students_upload.csv --The student csv file from CHCCS

### Output
#### new_patrons.csv -- csv file with student records to add to Sierra
Format
```
S_CHCCS_STUDENTINFO.PUBLIC.LIB.OPT.OUT
Student_Number
First_Name
Last_Name
DOB
SchoolID
Grade_Level
Mailing_Street (may repeat)
Mailing_City
Mailing_State
Mailing_Zip
S_NC_STUDENTDEMO.EMAIL_ADDRESS
Home_Phone
Guardian_Email (may repeat)
Enroll_Status
S_NC_STUDENTDEMO.STUDENTSDCID (auto incremented for each new student)
```

Enroll_Status
```
0 = Active
1 = Pre-Registered
2 = Transferred Out of District
3 = Graduated
4 = Imported to PowerSchool as a Historical Record
```
Only records with Enroll_Status or 0 or 1 are processed