from flask import Blueprint, render_template, session, flash, redirect, url_for

academic_bp = Blueprint('academic', __name__)

@academic_bp.route('/academic')
def academic():
    if 'logged_in' in session:
        return render_template('academic.html')
    else:
        flash('Please log in first.', 'danger')
        return redirect(url_for('login.login'))
