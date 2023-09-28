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

# database initialization
def initialize_database():
    try:
        connection = sqlite3.connect('users.db')
        with open('schema.sql') as f:
            # execute the schema script to initialize the database
            connection.executescript(f.read())
        # commit the changes
        connection.commit()

    except FileNotFoundError:
        print("Error: schema.sql file not found.")
    except sqlite3.Error as e:
        print(f"Error executing SQL script: {str(e)}")
    finally:
        if connection:
            # close the database connection
            connection.close()




# Function to fetch users and store in the database
def fetch_and_store_users_data():
    try:
        # Make a request to the users API
        response = requests.get(users_api_url, headers=header)

        # raise an exception for bad status codes
        response.raise_for_status()  

        users_data = response.json().get("data", [])

        # connect to the database
        conn = sqlite3.connect("users.db")
        conn.row_factory = sqlite3.Row
        query = "SELECT * FROM users WHERE firstName = ? AND lastName = ? "

        # insert users data into the database
        for user in users_data:
            firstName = user['firstName']
            lastName = user['lastName']
            users = conn.execute(query, (firstName, lastName)).fetchall()

            # If user's data is already present in the database, then skip
            if len(users) >= 1:
                continue

            conn.execute("""
                INSERT INTO users (id, title, firstName, lastName, picture)
                VALUES (?, ?, ?, ?, ?)
            """, (user["id"], user["title"], firstName, lastName, user["picture"]))

        # commit and close the connection
        conn.commit()
        conn.commit()
    except requests.RequestException as e:
        print(f"Error making API request: {str(e)}")
    except sqlite3.Error as e:
        print(f"Error inserting data into the database: {str(e)}")
    finally:
        if conn:
            conn.close()



# Function to fetch posts for each user and store in the database
def fetch_and_store_users_posts_data(userId):
    try:
        # connect to the database
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # fetch users' post data from the API
        response = requests.get(posts_api_url.format(userId), headers=header)
        # raise an exception for bad status codes
        response.raise_for_status()  

        posts_data = response.json().get("data", [])

        # insert posts data into the database
        for post in posts_data:
            cursor.execute("""
                INSERT INTO posts (id, userId, image, likes, tags, body, publishDate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (post["id"], post["owner"]["id"], post["image"],  post["likes"], ",".join(post["tags"]), post["text"], post["publishDate"]))

        # commit and close the connection
        conn.commit()
        conn.close()
    except requests.RequestException as e:
        print(f"Error making API request: {str(e)}")
    except sqlite3.Error as e:
        print(f"Error inserting data into the database: {str(e)}")
    finally:
        if conn:
            conn.close()


# all api lists
@app.route('/')
def home():
    endpoints = {
    "message" : "api endpoints",
    "users list" : "api/users",
    "users posts" : "api/users/user_id/posts"
    }
    return jsonify(endpoints)


# users list api
@app.route('/api/users', methods=['GET'])
def users():
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # retrieve all user data from the database
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        # If there is no data present in the database, fetch and store users' data
        if len(users) == 0:

            # retriev users data from api and store in the database
            fetch_and_store_users_data()
            # retrive users data after filling data
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()

        # Create a list of dictionaries of users' data
        users_list = [{'userId': user[0], 'First Name': user[1], 'Last Name': user[2], 'Title': user[3], 'Picture': user[4]} for user in users]

        # Commit and close the connection
        conn.commit()
        conn.close()

        # return the users as a JSON response
        return jsonify({"users" : users_list }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()


# user's posts data search api
@app.route('/api/users/<string:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    try:
        conn = sqlite3.connect("users.db")
        conn.row_factory = sqlite3.Row

        # check if the user exists
        query = "SELECT id FROM users WHERE id = ?"
        user = conn.execute(query, (user_id, )).fetchone()

        if user:
            # retrieve posts for the user
            query = "SELECT * FROM posts WHERE userId = ?"
            posts = conn.execute(query, (user_id, )).fetchall()

            if not posts:
                fetch_and_store_users_posts_data(user_id)
                posts = conn.execute(query, (user_id, )).fetchall()

            # return the posts as a JSON response
            return jsonify({'posts': [dict(post) for post in posts]}), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.commit()
            conn.close()


if __name__ == "__main__":

    #initialize the database
    initialize_database()

    # start the application
    # for development
    # app.run(debug=True, host="0.0.0.0", port="5000")

    # for production
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)