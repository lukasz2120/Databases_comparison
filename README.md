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
```

## Neo4j Script

### Steps:

1. **Generate Data**: Random data for users, posts, comments, reactions, and messages is generated using the `Faker` library.
2. **Cypher Queries**: Create the data in the Neo4j database using Cypher query language.
3. **Relationships**: Set up relationships between users and their posts, comments, reactions, etc.
4. **Execute Commands**: The commands are executed in batches to avoid memory overflow and optimize execution time.
5. **Measure Time**: Track the time taken for each operation using the `time_tracker` library.

### Example Neo4j Code:
```python
from neo4j import GraphDatabase
import random
import time
import pandas as pd
from faker import Faker

# Configuration & Initialization
fake = Faker()
NUM_USERS = 10000
NUM_POSTS = 10000

# Generate User Data
user_data = []
for _ in range(NUM_USERS):
    user_data.append({
        "username": fake.user_name(),
        "email": fake.email(),
        "password_hash": fake.sha256(),
        "full_name": fake.name(),
        "profile_picture": fake.image_url(),
        "bio": fake.text(max_nb_chars=100),
        "created_at": fake.date_time_this_decade().strftime('%Y-%m-%dT%H:%M:%S')
    })

# Create Cypher commands for nodes
user_create_commands = []
for user in user_data:
    bio_escaped = user['bio'].replace('"', '\\"')
    cypher = (
        "CREATE (u:User {"
        f"username: '{user['username']}', "
        f"email: '{user['email']}', "
        f"password_hash: '{user['password_hash']}', "
        f"full_name: '{user['full_name']}', "
        f"profile_picture: '{user['profile_picture']}', "
        f'bio: "{bio_escaped}", '
        f"created_at: datetime('{user['created_at']}')"
        "})"
    )
    user_create_commands.append(cypher)

# Execute Cypher queries
def execute_cypher_commands(commands, batch_size=10000):
    data_base_connection = GraphDatabase.driver(uri="bolt://localhost:7999", auth=("neo4j", "password"))
    session = data_base_connection.session()
    start_time = time.time()

    try:
        for i in range(0, len(commands), batch_size):
            batch = commands[i:i + batch_size]
            tx = session.begin_transaction()
            for cmd in batch:
                tx.run(cmd)
            tx.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        session.close()
        data_base_connection.close()

    end_time = time.time()
    print(f"Executed {len(commands)} commands in {end_time - start_time:.2f} seconds.")

# Example execution
execute_cypher_commands(user_create_commands)




