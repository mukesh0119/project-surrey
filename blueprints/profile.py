# blueprints/profile.py
from flask import Blueprint, render_template, redirect, url_for, flash, session
from helpers import get_user

profile_bp = Blueprint('profile', __name__)

# Define the users list
users = [
    {"id": 1, "username": "john_doe", "email": "john@example.com", "role": "Student"},
    {"id": 2, "username": "jane_smith", "email": "jane@example.com", "role": "Lecturer"}
]
posts = [
    {"id": 1, "title": "Sample Post 1", "content": "This is the first sample post.", "user_id": 1, "comments": [], "category": "General"},
    {"id": 2, "title": "Sample Post 2", "content": "This is the second sample post.", "user_id": 2, "comments": [
        {"content": "This is a comment on post 2", "user_id": 1}
    ], "category": "Academic"}
]

@profile_bp.route('/profile')
def profile():
    user_id = session.get('user_id')
    logged_in_user = get_user(user_id, users)
    
    if not logged_in_user:
        flash('User not found. Please log in again.', 'danger')
        return redirect(url_for('login.login'))
    
    user_posts = [post for post in posts if post['user_id'] == logged_in_user['id']]
    return render_template('profile.html', user=logged_in_user, posts=user_posts)




@profile_bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'logged_in' in session:
        user = get_user(session['user_id'], users=[])
        if request.method == 'POST':
            user['email'] = request.form['email']
            user['role'] = request.form['role']
            flash('Profile updated successfully.')
            return redirect(url_for('profile.profile'))
        return render_template('edit_profile.html', user=user)
    else:
        flash('Please log in first.', 'danger')
        return redirect(url_for('login.login'))
