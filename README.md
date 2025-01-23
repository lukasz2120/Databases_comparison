# CRUD Operation Comparison on MSSQL and Neo4j

This project compares the performance of CRUD operations (Create, Read, Update, Delete) between two database management systems: **MSSQL** and **Neo4j**. The aim is to analyze the time taken for performing these operations with similar datasets using both systems.

## Requirements

- **MSSQL**: You will need a working SQL Server instance, and the `pyodbc` library to establish connections.
- **Neo4j**: Requires the Neo4j database, along with the `neo4j` Python library for interaction.

### Python Libraries

1. **pandas**: Used for handling large datasets and performing operations like reading CSV files.
   - Version: `1.5.3`

2. **pyodbc**: A Python library for connecting to databases via ODBC.
   - Version: `4.0.32`

3. **time**: Built-in library for tracking the time of operations.
   
4. **time_tracker**: Custom or third-party library for tracking specific time intervals during execution. Ensure it's installed and available in your environment.
   
5. **neo4j**: Used to connect and interact with the Neo4j graph database.
   - Version: `4.4.0`

6. **faker**: Library for generating fake data, used to create random user and post data.
   - Version: `15.0.0`

## MSSQL Script

### Steps:

1. **Input**: Choose the number of records (10,000/100,000/1,000,000) to insert into the database.
2. **Queries**: Enter valid SQL queries for the CRUD operations (`READ`, `UPDATE`, `DELETE`).
3. **Insert Data**: A **sample dataset** containing 10,000 records is used to populate the `Users` and `Posts` tables in the MSSQL database.
4. **Measure Time**: Track the time taken for each operation using the `time_tracker` library.
5. **Commit and Clean**: After executing queries, commit the changes and close the connection.

### Example MSSQL Code:
```python
import pandas
import pyodbc
import time
import time_tracker

queries = {}
quantity = input('Enter the number of records to insert (10_000/100_000/1_000_000): ')

# Define queries
read_query = input("Enter the correct READ SQL query: ")
queries['READ'] = read_query

update_query = input("Enter the correct UPDATE SQL query: ")
queries['UPDATE'] = update_query

delete_query = input("Enter the correct DELETE SQL query: ")
queries["DELETE"] = delete_query

# MSSQL Connection
try:
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-UM0P5PB;'
        'DATABASE=ztbd;'
        'Trusted_Connection=yes;'
    )
    cursor = conn.cursor()
except pyodbc.Error as error:
    print(f"Connection failed: {error}")

# Insert data and track time
