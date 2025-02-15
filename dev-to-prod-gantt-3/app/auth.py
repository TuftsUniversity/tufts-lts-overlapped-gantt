from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from functools import wraps
import os
import json
from dotenv import load_dotenv

load_dotenv()

auth = Blueprint('auth', __name__)

# Hardcoded credentials
credentials = json.loads(os.getenv("GANTT_CREDENTIALS"))
USERNAME = credentials["username"]
PASSWORD = credentials["password"]

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == USERNAME and password == PASSWORD:
            session['user'] = username
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('auth.login'))


def login_required(f):
    """Decorator to protect routes that require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))  # Redirect to the login page if not logged in
        return f(*args, **kwargs)
    return decorated_function