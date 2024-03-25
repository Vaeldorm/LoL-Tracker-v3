#!/usr/bin/env python3 feat

from flask import Flask, render_template, request, redirect, session
from flask_login import LoginManager, login_user, logout_user
import json
import os
import secrets
import time

app = Flask(__name__)                               # Create a Flask application instance
top_secret_key = secrets.token_hex()                # Generate key used for session management, should be kept secret
app.secret_key = f'{top_secret_key}'.encode()       # Set the secret key for the Flask application
login_manager = LoginManager()                      # Create a LoginManager instance
login_manager.init_app(app)                         # Initialize the LoginManager with the Flask application

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


# TODO
#   class User:
#   def load_user():
#   def login():
#   def logout():


def load_entries():
    """
    Load game entries from the master JSON file.

    Returns:
        list: A list of Entry objects loaded from the JSON file.
    """
    entries = []
    master_filename = "tracker_master_entries.json"
    if os.path.exists(master_filename) and os.path.getsize(master_filename) > 0:
        try:
            with open(master_filename, mode='r') as master_file:
                entries_data = json.load(master_file)
                for entry_data in entries_data:
                    entry = Entry(**entry_data)
                    entries.append(entry)
        except json.JSONDecodeError:
            print("Error: Unable to parse JSON file. The file may contain invalid JSON data.")
    return entries


def save_to_json(entry):
    """
    Save a game entry to the master JSON file.

    Args:
        entry (Entry): The Entry object to be saved.
    """
    master_filename = "tracker_master_entries.json"
    entries = load_entries()
    entries.append(entry)

    with open(master_filename, mode='w') as master_file:
        json.dump([vars(e) for e in entries], master_file, indent=4, separators=(", ", ": "))


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
        save_to_json(entry)
        return redirect('/')
    else:
        entries = load_entries()
        return render_template('index.html', entries=reversed(entries))


if __name__ == '__main__':
    app.run(debug=True)
