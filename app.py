# app.py

import os
from flask import Flask, redirect, url_for, request
from blueprints import register_blueprints
from config import config_by_name
from blueprints.forum import forum_bp
from blueprints.profile import profile_bp
from blueprints.placements import placements_bp



app = Flask(__name__)

# Set configuration based on environment
config_name = os.environ.get('FLASK_ENV', 'development')  # Defaults to 'development'
app.config.from_object(config_by_name[config_name])

# Register blueprints
register_blueprints(app)


@app.route('/')
def home():
    return redirect(url_for('login.login'))

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=app.config['DEBUG'])