# chccs-post-update
These scripts are used as utilities to aid in the IDea Project for the Town of Chapel Hill

Written in Python 3

<strong>Usage</strong>
 
<strong>patron-post-update-student/staff:</strong>
    These two scripts were designed for the initial upload of CHCCS records to the CHPL database.  Due to formatting differences between CHCCS and CHPL the comparison function in these two scripts is not functional.  Comparison will be updated once a data format is agreed upon.

    The scripts will read in the initial CSV's, store each patron record in a constructor and then upload them to the database.  Upload is currently one at a time because of limitations from Sierra.

    Run script by navigating to parent folder in the command line and then typing "python patron-post-student.py" or "python patron-post-staff.py"

<strong>retrieve-patrons:</strong>
    This script will simply retrieve all non-deleted patron records from the CHPL database and writes them to a CSV to improve the speed of the find-duplicates script

    Run script by navigating to parent folder in the command line and then typing "python retrieve-patrons.py"

<strong>find-duplicates:</strong>
    Designed to find duplicates in the CHPL database that were produced during the initial upload of CHCCS data.

    Script reads a CSV produced by retrieve-patrons.py, perform a comparison and then produce two new CSV's of records to be updated & records to be deleted

    Run script by navigating to parent folder in the command line and then typing "python find-duplicates.py"

<strong>update/delete:</strong>
    These scripts will update or delete patron records based on the results produced from the find-duplicates.py script

    Reads the respective CSV (titled clearly by find-duplicates) and performs the function of it's namesake (UPDATE/DELETE) for each record included in CSV.

    Run script by navigating to parent folder in the command line and then typing "python update.py" or "python delete.py"


*** Scripts can only be run with the keys right keys and if you don't have those keys then you should not be running these scripts ***


