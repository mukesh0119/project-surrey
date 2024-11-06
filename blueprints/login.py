from flask import Blueprint, render_template, redirect, url_for, request, flash, session

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == 'student@example.com' and password == 'projectsurrey':
            session['logged_in'] = True
            session['user_id'] = 1
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email or password', 'danger')
            return render_template('login.html')
    return render_template('login.html')
