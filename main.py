#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect
import csv
import time
import os

app = Flask(__name__)


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

    def __init__(self, champion="", opponent="", outcome="", notes="", matchup_tips="", date=""):
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
        self.outcome = outcome
        self.notes = notes
        self.matchup_tips = matchup_tips
        self.date = date


def load_entries():
    """
    Load game entries from the master CSV file.

    Returns:
        list: A list of Entry objects loaded from the CSV file.
    """
    entries = []
    master_filename = "tracker_master_entries.csv"
    if os.path.exists(master_filename):
        with open(master_filename, mode='r') as master_file:
            reader = csv.DictReader(master_file)
            for row in reader:
                entry = Entry(
                    champion=row['Champion'],
                    opponent=row['Opponent'],
                    outcome=row['Outcome'],
                    notes=row['Notes'],
                    matchup_tips=row['Matchup Tips'],
                    date=row['Date']
                )
                entries.append(entry)
    return entries


def save_to_csv(entry):
    """
    Save a game entry to the master CSV file.

    Args:
        entry (Entry): The Entry object to be saved.
    """
    master_filename = "tracker_master_entries.csv"
    fieldnames = ["Date", "Champion", "Opponent", "Outcome", "Notes", "Matchup Tips"]

    with open(master_filename, mode='a', newline='') as master_file:
        writer = csv.DictWriter(master_file, fieldnames=fieldnames)
        writer.writerow({
            "Date": entry.date,
            "Champion": entry.champion,
            "Opponent": entry.opponent,
            "Outcome": entry.outcome,
            "Notes": entry.notes,
            "Matchup Tips": entry.matchup_tips
        })


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        champion = request.form['champion']
        opponent = request.form['opponent']
        outcome = request.form['outcome']
        notes = request.form['notes']
        matchup_tips = request.form['matchup_tips']
        date = time.strftime("%m-%d-%Y")
        entry = Entry(champion=champion, opponent=opponent, outcome=outcome, notes=notes, matchup_tips=matchup_tips, date=date)
        save_to_csv(entry)
        return redirect('/')
    else:
        entries = load_entries()
        return render_template('index.html', entries=reversed(entries))


if __name__ == '__main__':
    app.run(debug=True)
