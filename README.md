API for User Data and Posts

This Flask application serves as an API for retrieving user data and posts from an external source and storing them in an SQLite database. It provides several endpoints to fetch user data, posts, and information about available API endpoints.
Table of Contents

    Installation
    Usage
    API Endpoints

Installation

    Clone the Repository:

    Clone this repository to your local machine using the following command:

    git clone https://github.com/0xtheak/users-api.git
    cd users-api


Set Up Virtual Environment:

Create a virtual environment and activate it:

    python3 -m venv venv
    source venv/bin/activate   # on windows: venv\scripts\activate


Install Dependencies:

Install the required packages using pip:

    pip install -r requirements.txt


Usage

    Run the Application:

    Start the Flask application using the following command:

    python3 app.py

    The application will be accessible at http://127.0.0.1:5000/.

Access API Endpoints:
    Use API endpoints to retrieve user data and posts. Check the API Endpoints section below for available routes and usage.

API Endpoints

    List of Available Endpoints:
        GET / - Provides a list of available API endpoints.
        GET /api/users - Retrieves user data.
        GET /api/users/<user_id>/posts - Retrieves posts for a specific user.


Feel free to customize this README to fit the specific details and needs of your project. Provide clear instructions for installation, usage, and any other relevant information that will help users and developers understand and use your application.