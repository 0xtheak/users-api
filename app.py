from flask import Flask, jsonify
import sqlite3
import requests

app = Flask(__name__)
# app-id 
header = {
    "app-id": "6513f5792a878451843139b1"
    } 

# API endpoints
users_api_url = "https://dummyapi.io/data/v1/user"
posts_api_url = "https://dummyapi.io/data/v1/user/{}/post"

# initialize database
def initialize_database():
    connection = sqlite3.connect('users.db')
    with open('schema.sql') as f:
        connection.executescript(f.read())
    connection.commit()
    connection.close()




# Function to fetch users and store in the database
def fetch_and_store_users_data():
    response = requests.get(users_api_url, headers=header)
    users_data = response.json().get("data", [])
    # print(users_data)

    # Connect database
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    query = "SELECT * FROM users WHERE firstName= ? AND lastName = ? "
    # execute the sql query
    
    # Insert users data into the database
    for user in users_data:
        firstName = user['firstName']
        lastName = user['lastName']
        users = conn.execute(query, (firstName, lastName, )).fetchall()
        
        # if user's data already present in database, then skip
        if len(users)>=1:
            break
        conn.execute("""
            INSERT INTO users (id, title, firstName, lastName, picture)
            VALUES (?, ?, ?, ?, ?)
        """, (user["id"], user["title"], user["firstName"], user["lastName"], user["picture"]))

    # Commit and close the connection
    conn.commit()
    conn.close()

# Function to fetch posts for each user and store in the database
def fetch_and_store_posts_data():
    
    # Connect to the database
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Retrieve users from the database
    cursor.execute("SELECT id FROM users")
    user_ids = cursor.fetchall()

    # Iterate through each user and fetch their posts
    for user_id in user_ids:
        response = requests.get(posts_api_url.format(user_id[0]), headers=header)
        posts_data = response.json().get("data", [])
        

        # Insert posts data into the database
        for post in posts_data:
            cursor.execute("""
                INSERT INTO posts (id, userId, image, likes, tags, body, publishDate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (post["id"], post["owner"]["id"], post["image"],  post["likes"], post["text"], ",".join(post["tags"]), post["publishDate"]))

    # Commit and close the connection
    conn.commit()
    conn.close()

@app.route('/')
def home():
    endpoints = {
    "message" : "api endpoints",
    "users list" : "api/users",
    "users posts" : "api/users/user_id/posts"
    }
    return jsonify(endpoints)

@app.route('/api/users')
def users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Retrieve users from the database
    cursor.execute("SELECT id, firstName FROM users")
    users = cursor.fetchall()
    #if there is not data present in database, then use api to fill data in database
    if len(users)==0:
        fetch_and_store_users_data()
    # Create a list of dictionaries of users data
    users = [{"user_id": user[0], "First Name":  user[1]} for user in users]

    # Commit and close the connection
    conn.commit()
    conn.close()
    return jsonify(users)

if __name__ == "__main__":
    initialize_database()
    # fetch_and_store_users_data()
    # fetch_and_store_posts_data()

    app.run(debug=True, host="0.0.0.0", port="5000")

