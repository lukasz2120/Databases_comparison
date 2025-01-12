import random
import time
import pandas as pd
from faker import Faker
from neo4j import GraphDatabase

# ------------------------------
# Configuration & Initialization
# ------------------------------
fake = Faker()
NUM_USERS = 10000
NUM_POSTS = 10000
NUM_COMMENTS = 10000
NUM_REACTIONS = 10000
NUM_MESSAGES = 10000
NUM_TAGS = 10000

# Neo4j connection info
URI = "bolt://localhost:7999"
USERNAME = "neo4j"
PASSWORD = "password"

# ----------------------
# 1. Generate User Data
# ----------------------
user_data = []
for _ in range(NUM_USERS):
    user_data.append({
        "username": fake.user_name(),
        "email": fake.email(),
        "password_hash": fake.sha256(),
        "full_name": fake.name(),
        "profile_picture": fake.image_url(),
        "bio": fake.text(max_nb_chars=100),
        "created_at": fake.date_time_this_decade().strftime('%Y-%m-%dT%H:%M:%S')  # ISO 8601
    })

# Convert to DataFrame just for preview (optional)
user_df = pd.DataFrame(user_data)
print("Sample Users:")
print(user_df.head())

# ----------------------
# 2. Generate Post Data
# ----------------------
post_data = []
for i in range(NUM_POSTS):
    post_data.append({
        "post_id": i + 1,
        "content": fake.text(max_nb_chars=200),
        "media_url": fake.image_url(),
        "created_at": fake.date_time_this_decade().strftime('%Y-%m-%dT%H:%M:%S')
    })

post_df = pd.DataFrame(post_data)
print("\nSample Posts:")
print(post_df.head())

# -------------------------
# 3. Generate Comment Data
# -------------------------
comment_data = []
for i in range(NUM_COMMENTS):
    comment_data.append({
        "comment_id": i + 1,
        "content": fake.sentence(nb_words=8),
        "created_at": fake.date_time_this_decade().strftime('%Y-%m-%dT%H:%M:%S')
    })

comment_df = pd.DataFrame(comment_data)
print("\nSample Comments:")
print(comment_df.head())

# -------------------------
# 4. Generate Reaction Data
# -------------------------
reaction_types = ["Like", "Love", "Haha", "Wow", "Angry", "Sad"]
reaction_data = []
for i in range(NUM_REACTIONS):
    reaction_data.append({
        "reaction_id": i + 1,
        "reaction_type": random.choice(reaction_types),
        "created_at": fake.date_time_this_decade().strftime('%Y-%m-%dT%H:%M:%S')
    })

reaction_df = pd.DataFrame(reaction_data)
print("\nSample Reactions:")
print(reaction_df.head())

# -------------------------
# 5. Generate Message Data
# -------------------------
message_data = []
for i in range(NUM_MESSAGES):
    message_data.append({
        "message_id": i + 1,
        "content": fake.text(max_nb_chars=100),
        "created_at": fake.date_time_this_decade().strftime('%Y-%m-%dT%H:%M:%S')
    })

message_df = pd.DataFrame(message_data)
print("\nSample Messages:")
print(message_df.head())

# -------------------------
# 6. Generate Tag Data
# -------------------------
# We'll generate random "words" as tags; ensure uniqueness by set or something similar if needed
tag_data = []
for i in range(NUM_TAGS):
    tag_data.append({
        "tag_id": i + 1,
        "tag_name": fake.word() + str(i)  # include index to reduce collisions
    })

tag_df = pd.DataFrame(tag_data)
print("\nSample Tags:")
print(tag_df.head())

# ----------------------------------
# Build Cypher statements for NODES
# ----------------------------------
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

post_create_commands = []
for post in post_data:
    content_escaped = post['content'].replace('"', '\\"')
    cypher = (
        "CREATE (p:Post {"
        f"post_id: {post['post_id']}, "
        f'content: "{content_escaped}", '
        f"media_url: '{post['media_url']}', "
        f"created_at: datetime('{post['created_at']}')"
        "})"
    )
    post_create_commands.append(cypher)

comment_create_commands = []
for c in comment_data:
    content_escaped = c['content'].replace('"', '\\"')
    cypher = (
        "CREATE (c:Comment {"
        f"comment_id: {c['comment_id']}, "
        f'content: "{content_escaped}", '
        f"created_at: datetime('{c['created_at']}')"
        "})"
    )
    comment_create_commands.append(cypher)

reaction_create_commands = []
for r in reaction_data:
    cypher = (
        "CREATE (r:Reaction {"
        f"reaction_id: {r['reaction_id']}, "
        f"reaction_type: '{r['reaction_type']}', "
        f"created_at: datetime('{r['created_at']}')"
        "})"
    )
    reaction_create_commands.append(cypher)

message_create_commands = []
for m in message_data:
    content_escaped = m['content'].replace('"', '\\"')
    cypher = (
        "CREATE (m:Message {"
        f"message_id: {m['message_id']}, "
        f'content: "{content_escaped}", '
        f"created_at: datetime('{m['created_at']}')"
        "})"
    )
    message_create_commands.append(cypher)

tag_create_commands = []
for t in tag_data:
    cypher = (
        "CREATE (t:Tag {"
        f"tag_id: {t['tag_id']}, "
        f"tag_name: '{t['tag_name']}'"
        "})"
    )
    tag_create_commands.append(cypher)

# -----------------------------------------------------------
# Build Cypher statements for RELATIONSHIPS
# -----------------------------------------------------------
# 1) User -> CREATED_POST -> Post
#    We'll randomly assign each Post to a User
rel_create_post_commands = []
for post in post_data:
    user_idx = random.randint(0, NUM_USERS - 1)
    user_name = user_data[user_idx]["username"]
    cypher = (
            "MATCH (u:User {username: '%s'}), (p:Post {post_id: %d}) "
            "CREATE (u)-[:CREATED_POST]->(p)"
            % (user_name, post["post_id"])
    )
    rel_create_post_commands.append(cypher)

# 2) User -> WROTE_COMMENT -> Comment -> ON_POST -> Post
rel_create_comment_commands = []
for c in comment_data:
    user_idx = random.randint(0, NUM_USERS - 1)
    user_name = user_data[user_idx]["username"]
    post_idx = random.randint(0, NUM_POSTS - 1)
    post_id = post_data[post_idx]["post_id"]

    cypher_user_comment = (
            "MATCH (u:User {username: '%s'}), (c:Comment {comment_id: %d}) "
            "CREATE (u)-[:WROTE_COMMENT]->(c)"
            % (user_name, c["comment_id"])
    )
    cypher_comment_post = (
            "MATCH (c:Comment {comment_id: %d}), (p:Post {post_id: %d}) "
            "CREATE (c)-[:ON_POST]->(p)"
            % (c["comment_id"], post_id)
    )
    rel_create_comment_commands.append(cypher_user_comment)
    rel_create_comment_commands.append(cypher_comment_post)

# 3) User -> REACTION -> Post
rel_create_reaction_commands = []
for r in reaction_data:
    user_idx = random.randint(0, NUM_USERS - 1)
    user_name = user_data[user_idx]["username"]
    post_idx = random.randint(0, NUM_POSTS - 1)
    post_id = post_data[post_idx]["post_id"]
    cypher = (
            "MATCH (u:User {username: '%s'}), (p:Post {post_id: %d}), (r:Reaction {reaction_id: %d}) "
            "CREATE (u)-[:REACTION {reaction_type: r.reaction_type, created_at: r.created_at}]->(p)"
            % (user_name, post_id, r["reaction_id"])
    )
    rel_create_reaction_commands.append(cypher)

# 4) FOLLOWS (User -> User)
rel_create_follows_commands = []
for i in range(NUM_USERS):
    follows_list = random.sample(range(NUM_USERS), 5)
    user_name_src = user_data[i]["username"]
    for flw_idx in follows_list:
        if flw_idx == i:
            continue
        user_name_target = user_data[flw_idx]["username"]
        cypher = (
                "MATCH (u1:User {username: '%s'}), (u2:User {username: '%s'}) "
                "CREATE (u1)-[:FOLLOWS {created_at: datetime()}]->(u2)"
                % (user_name_src, user_name_target)
        )
        rel_create_follows_commands.append(cypher)

# 5) User -> SENT_MESSAGE -> Message -> TO -> User
rel_create_message_commands = []
for m in message_data:
    sender_idx = random.randint(0, NUM_USERS - 1)
    sender_name = user_data[sender_idx]["username"]
    receiver_idx = random.randint(0, NUM_USERS - 1)
    while receiver_idx == sender_idx:
        receiver_idx = random.randint(0, NUM_USERS - 1)
    receiver_name = user_data[receiver_idx]["username"]

    cypher_sender = (
            "MATCH (u:User {username: '%s'}), (m:Message {message_id: %d}) "
            "CREATE (u)-[:SENT_MESSAGE]->(m)"
            % (sender_name, m["message_id"])
    )
    cypher_receiver = (
            "MATCH (m:Message {message_id: %d}), (u:User {username: '%s'}) "
            "CREATE (m)-[:TO]->(u)"
            % (m["message_id"], receiver_name)
    )
    rel_create_message_commands.append(cypher_sender)
    rel_create_message_commands.append(cypher_receiver)

# 6) Post -> HAS_TAG -> Tag
rel_create_tag_commands = []
for p in post_data:
    tag_list = random.sample(range(NUM_TAGS), 5)
    for t_idx in tag_list:
        t = tag_data[t_idx]
        cypher = (
                "MATCH (p:Post {post_id: %d}), (t:Tag {tag_id: %d}) "
                "CREATE (p)-[:HAS_TAG]->(t)"
                % (p["post_id"], t["tag_id"])
        )
        rel_create_tag_commands.append(cypher)

# --------------------------------------
# Combine all CREATE statements in order
# --------------------------------------
all_create_commands = (
        user_create_commands +
        post_create_commands +
        comment_create_commands +
        reaction_create_commands +
        message_create_commands +
        tag_create_commands
)

all_relationship_commands = (
        rel_create_post_commands +
        rel_create_comment_commands +
        rel_create_reaction_commands +
        rel_create_follows_commands +
        rel_create_message_commands +
        rel_create_tag_commands
)

def execute_cypher_commands(commands, batch_size=10000):
    """
    Execute a list of Cypher commands in batches to avoid
    sending too-large transactions.
    """
    data_base_connection = GraphDatabase.driver(uri=URI, auth=(USERNAME, PASSWORD))
    session = data_base_connection.session()
    start_time = time.time()

    try:
        # Execute in batches
        for i in range(0, len(commands), batch_size):
            batch = commands[i : i + batch_size]
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


if __name__ == "__main__":
    print("\n--- Creating Nodes ---")
    execute_cypher_commands(all_create_commands, batch_size=10000)

    print("\n--- Creating Relationships ---")
    execute_cypher_commands(all_relationship_commands, batch_size=10000)

    print("\nData was successfully injected into Neo4j!")

