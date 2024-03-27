#!/usr/bin/env python3


from flask import Flask, render_template, request, redirect, session
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user
import hashlib
import json
import os
import secrets
import time

app = Flask(__name__)                               # Create a Flask application instance
top_secret_key = secrets.token_hex()                # Generate key used for session management, should be kept secret
app.secret_key = f'{top_secret_key}'.encode()       # Set the secret key for the Flask application
login_manager = LoginManager()                      # Create a LoginManager instance
login_manager.init_app(app)                         # Initialize the LoginManager with the Flask application


class User(UserMixin):                      # Inheriting implementations from UserMixin
    def __init__(self, username):
        self.username = username


class Entry:
    """
    Represents a game entry for League of Legends.

    Attributes:
        champion (str): The name of the champion.
        opponent (str): The name of the opponent champion.
        outcome (str): The outcome of the game (Win/Loss).
        notes (str): Any additional notes about the game.
        matchup_tips (str): Tips for the matchup.
    """

    def __init__(self, champion="", opponent="", role="", outcome="", notes="", matchup_tips="", date=""):
        """
        Initializes an Entry object with optional attributes.

        Args:
            champion (str): The name of the champion (default is an empty string).
            opponent (str): The name of the opponent champion (default is an empty string).
            outcome (str): The outcome of the game (default is an empty string).
            notes (str): Any additional notes about the game (default is an empty string).
            matchup_tips (str): Tips for the matchup (default is an empty string).
            date (str): The date of the entry (default is an empty string).
        """
        self.champion = champion
        self.opponent = opponent
        self.role = role
        self.outcome = outcome
        self.notes = notes
        self.matchup_tips = matchup_tips
        self.date = date


def load_all_users():
    all_users = {}
    user_filename = "users.json"
    if os.path.exists(user_filename) and os.path.getsize(user_filename) > 0:
        try:
            with open(user_filename, mode='r') as user_file:
                users_data = json.load(user_file)
                for user_data in users_data:
                    username = user_data['username']
                    password_hash = user_data['password_hash']
                    all_users[username] = password_hash
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"Error: Unable to parse JSON file. {e}")
    return all_users


def hash_password(password):
    """Hash the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def new_user(username, password):
    users_filename = "users.json"
    all_users = load_all_users()
    password_hash = hash_password(password)
    all_users[username] = password_hash
    with open(users_filename, mode='w') as users_file:
        json.dump(all_users, users_file, indent=4)


def load_user_entries(username):
    """
    Load game entries for a specific user from their JSON file.

    Args:
        username (str): The username of the user.

    Returns:
        list: A list of Entry objects loaded from the user's JSON file.
    """
    entries = []
    user_filename = f"{username}_entries.json"  # Create a user-specific filename
    if os.path.exists(user_filename) and os.path.getsize(user_filename) > 0:
        try:
            with open(user_filename, mode='r') as user_file:
                entries_data = json.load(user_file)
                for entry_data in entries_data:
                    entry = Entry(**entry_data)
                    entries.append(entry)
        except json.JSONDecodeError:
            print(f"Error: Unable to parse JSON file for user {username}. The file may contain invalid JSON data.")
    return entries


def check_password(username, password):
    """Check if the provided password matches the hashed password."""
    all_users = load_all_users()
    if username in all_users:
        password_hash = all_users[username]
        return hash_password(password) == password_hash
    return False


def login():
    pass


def logout():
    pass


def save_entry(entry):
    """
    Save a game entry to the user's JSON file.

    Args:
        entry (Entry): The Entry object to be saved.
    """
    user_filename = f"{current_user.username}_entries.json"  # Use the current user's username for the filename
    entries = load_user_entries(current_user.username)
    entries.append(entry)

    with open(user_filename, mode='w') as user_file:
        json.dump([vars(e) for e in entries], user_file, indent=4, separators=(", ", ": "))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        champion = request.form['champion']
        opponent = request.form['opponent']
        role = request.form['role']
        outcome = request.form['outcome']
        notes = request.form['notes']
        matchup_tips = request.form['matchup_tips']
        date = time.strftime("%m-%d-%Y")
        entry = Entry(
            champion=champion,
            opponent=opponent,
            role=role,
            outcome=outcome,
            notes=notes,
            matchup_tips=matchup_tips,
            date=date
        )
        save_entry(entry)
        return redirect('/')
    else:
        if current_user.is_authenticated:
            entries = load_user_entries(current_user.username)  # Load entries for the current user
            return render_template('index.html', entries=reversed(entries))
        else:
            return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
