# SQL scripts

The `sql/` folder contains the following two sql scripts which are called by the main script to create the necessary tables:

* `EditHistory.sql`

    This script is used to create the EditHistory table. This table aggregates the events (the initial body, body edits, and comments) of every question and answer with the event's creation date. This tables allows us to see a chronological history of each question and answer. 

* `EditHistory_Code.sql`

    This script creates the EditHistory_Code table. This table is similar to the EditHistory table. However, it does not store questions and question history, it only stores answers and answer history, and comments. The answers and answer histories also only store the code changes for each edit.

To run these scripts in SQLite, you need to open the database and run the scripts, e.g.,
```
sqlite3 sotorrent.sqlite3
.read EditHistory.sql
.read EditHistory_Code.sql
```

# Importing
Official SQLite guide [here](https://www.sqlitetutorial.net/sqlite-import-csv/).

To import CSVs into an sqlite3 database follow these steps:

1. Start sqlite3 with an empty database using `sqlite3 <database_name>`

2. Create tables to store the data in the CSVs. You can write a *.sql file and run it in sqlite using `.read <path-to-script>`
    * To create a table for storing CSV data you need to write the script for those CSVs with the first row of the CSV being the names of the columns, e.g., for the `data/ground_truth.csv` file, it has 4 columns "AnswerId", "CommentId", "EditIds", and "Useful", so the SQL script to create a table for this should be: `ground_truth.sql`:
    ```
    CREATE TABLE ground_truth(
      "AnswerId" TEXT,
      "CommentId" TEXT,
      "EditIds" TEXT,
      "Useful" TEXT,
    );
    ```
3. Delete the first row of the CSV file (the one containing the column names). This is because if you are importing into an existing table then SQLite will treat all rows as data.

4. Change the read mode of sqlite3 by using `.mode csv`. This is necessary so SQLite reads the next command, which gives a CSV file, as a CSV and not as anything else.

5. Import the csvs by runnning `.import <path-to-csv> <table-name>`

The entire command sequence should look similar to this:
```
sqlite3 sotorrent.sqlite3

.read ground_truth.sql
.mode csv
.import data/ground_truth.csv ground_truth
```

### Alternate importing
OR if you do not want to create the table yourself you can make SQLite try

1. Change the read mode of SQLite to read as CSV.
```
.mode csv
```

2. Import the data and provide a name for the table. `.import <table_path> <table_name>`
```
.import data/ground_truth.csv ground_truth
```