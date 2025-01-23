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
