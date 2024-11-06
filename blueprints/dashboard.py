from flask import Blueprint, render_template, session, flash, redirect, url_for

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def index():
    if 'logged_in' in session:
        return render_template('index.html')
    else:
        flash('Please log in first.', 'danger')
        return redirect(url_for('login.login'))
