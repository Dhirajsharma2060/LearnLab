from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import os
import bcrypt  # Import bcrypt for hashing
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Fetch Project and Environment IDs from environment variables
PROJECT_ID = os.getenv("projectId")
ENVIRONMENT_ID = os.getenv("environmentId")

# CosmosCloud API endpoint for user creation
COSMO_CLOUD_API = "https://free-ap-south-1.cosmocloud.io/development/api/user"

@app.route('/')
def home():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    # Get form data
    username = request.form['name']
    password = request.form['password']

    # Hash the password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Prepare headers and payload for CosmosCloud API
    headers = {
        'Content-Type': 'application/json',
        'projectId': PROJECT_ID,
        'environmentId': ENVIRONMENT_ID
    }
    
    # Payload to be sent to the API
    payload = {
        'username': username,       # The username from the form
        'password_hash': password_hash  # The hashed password
    }

    try:
        # Send POST request to CosmosCloud API
        response = requests.post(COSMO_CLOUD_API, json=payload, headers=headers)

        # Check response status
        if response.status_code == 201:
            return redirect(url_for('login'))  # Redirect to login on success
        else:
            return jsonify({'error': response.json()}), response.status_code  # Return error if any

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500  # Handle request exceptions

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # API endpoint to get user by username (Assuming API supports querying by username)
        user_api = f"{COSMO_CLOUD_API}?username={username}"

        # Prepare headers for the API request
        headers = {
            'Content-Type': 'application/json',
            'projectId': PROJECT_ID,
            'environmentId': ENVIRONMENT_ID
        }

        try:
            # Send GET request to fetch user data by username
            response = requests.get(user_api, headers=headers)

            if response.status_code == 200:
                user_data = response.json()

                # Verify password by comparing the entered password with the stored hash
                if bcrypt.checkpw(password.encode('utf-8'), user_data['password_hash'].encode('utf-8')):
                    return redirect(url_for('dashboard'))  # Redirect to dashboard on success
                else:
                    return render_template('login.html', error='Invalid password')  # Display error on login page
            else:
                return render_template('login.html', error='User not found')  # Display error on login page

        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e)}), 500
    else:
        return render_template('login.html')  # Ensure this matches your template file name

# Dashboard Route (example)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')  # Ensure this template exists

if __name__ == '__main__':
    app.run(debug=True)
