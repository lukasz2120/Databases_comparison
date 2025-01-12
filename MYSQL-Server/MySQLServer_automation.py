import pandas
import pyodbc
import time
import time_tracker #Czym są te biblioteki? Jakie maja wersje??

queries = {}
quantity = input('Ile rekordow chcesz wprowadzić? (10_000/100_000/1000_000): ')

read_query = input("Wprowadź poprawne zapytanie SQL typu READ: ")
queries['READ'] = read_query

update_query = input("Wprowadź poprawne zapytanie SQL typu UPDATE: ")
queries['UPDATE'] = update_query

delete_query = input("Wprowadź poprawne zapytanie SQL typu DELETE: ")
queries["DELETE"] = delete_query

#Połączenie z SQL server
try:
    conn = pyodbc.connect(

        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-UM0P5PB;'
        'DATABASE=ztbd;'
        'Trusted_Connection=yes;'
    )

    #Przygotowanie kursora
    cursor = conn.cursor()

except pyodbc.Error as error:
    print(f"Połaczenie do bazy danych się nie udało: {error}")


#Wczytanie plików csv (chunksize do wczytywania plików po kawałku dla wydajności)
users_file = pandas.read_csv(f'D:\\Studia_Politechnika\\Zaawansowane_technologie_baz_danych\\datasets\\Users_{quantity}.csv')
posts_file = pandas.read_csv(f'D:\\Studia_Politechnika\\Zaawansowane_technologie_baz_danych\\datasets\\Posts_{quantity}.csv')

#Usunięcie wszystkich rekordów z bazy danych oraz reset primary key
tables = ['Users', 'Posts']
for table in tables:
    cursor.execute(f"""DELETE FROM {table};
    DBCC CHECKIDENT ('{table}', RESEED, 0);""")

cursor.execute("""DBCC FREEPROCCACHE; DBCC DROPCLEANBUFFERS;""")

create_start_time = time.time()

#Wstawianie danych do tabeli
for index, row in users_file.iterrows():

    # Zapytanie SQL z dynamicznymi parametrami
    cursor.execute("""
    INSERT INTO Users (Username, Email, PasswordHash, FullName, 
    ProfilePicture, Bio, CreatedAt) VALUES (?, ?, ?, ?, ?, ?, ?)""",
    row['Username'], row['Email'], row['PasswordHash'], row['FullName'],
    row['ProfilePicture'], row['Bio'], row['CreatedAt']
    )

for index, row in posts_file.iterrows():
    cursor.execute("""
    INSERT INTO Posts (UserID, Content, MediaURL, CreatedAt) VALUES
    (?,?,?,?)""", row['UserID'], row['Content'], row['MediaURL'], 
    row['CreatedAt']
    )

create_end_time = time.time()

print("\nZbior został zaimportowany poprawnie!")

#Wyświetlenie wyników poszczególnych zapytań SQL
for key, value in queries.items():
    with time_tracker(key):
        cursor.execute(value)

print(f"Polecenie CREATE trwało: {create_end_time - create_start_time:.4f} sekund")

#Zatwierdzenie operacji
conn.commit()

#Zamknięcie połączenia
cursor.close()
conn.close()


# UPDATE Users SET Bio = 'GniBvBEj8MmmlVCPR2XmOoZsr6lNQIdWxcAyHwdXv1kFYEPLfd' WHERE UserID >= 1;

# SELECT Users.UserID,Users.Username,Users.Email,Posts.PostID,Posts.Content,Posts.MediaURL,Posts.CreatedAt AS PostCreatedAt FROM Users INNER JOIN Posts ON Users.UserID = Posts.UserID ORDER BY Users.UserID, Posts.CreatedAt;

# Delete from Users where UserID = 1;
