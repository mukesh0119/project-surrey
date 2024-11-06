from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from helpers import load_club_data  # Importing the helper function to load club data

clubs_bp = Blueprint('clubs', __name__)

@clubs_bp.route('/clubs')
def clubs():
    if 'logged_in' in session:
        # Sample user data for club stats (this can be dynamically set as needed)
        user_data = {
            'name': 'Mukesh Saravanan',
            'clubs': {
                'events_attended': 11,
                'next_event': 'Photography Workshop - 11th Sep 2024'
            }
        }

        # Load clubs data from the CSV
        clubs_data = load_club_data()

        # Get the search query from the request
        search_query = request.args.get('search', '').lower()

        # Filter clubs data if there is a search query
        if search_query:
            clubs_data = [club for club in clubs_data if search_query in club['name'].lower()]

        # Pass user and clubs data to the template
        return render_template('clubs.html', user=user_data, clubs=clubs_data)
    else:
        flash('Please log in first.', 'danger')
        return redirect(url_for('login.login'))
