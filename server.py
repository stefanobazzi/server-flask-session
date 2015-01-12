import os
from flask import Flask, request, session, redirect, url_for, \
    abort, render_template, flash, send_from_directory
from werkzeug import secure_filename
from functools import wraps


# Server Configuration files
DEBUG = True
SECRET_KEY = 'under construction'
USERNAME = 'admin'
PASSWORD = 'password'
UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__file__))
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# User Configuration
FILENAME = 'files_list.txt'

files_list = []

app = Flask(__name__)
app.config.from_object(__name__)


def create_folder():
    path = os.path.dirname(os.path.relpath(__file__))
    files_path = os.join(path, 'files')


def allowed_file(name):
    return '.' in name and \
        name.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def save_files_list(filename):
    with open(filename, 'w') as f:
        for filename in files_list:
            f.write('{}\n'.format(filename))


def load_files_list(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            files_list = [line.replace('\n', '') for line in f.readlines()]


@app.route('/login', methods=['GET', 'POST'])
def login():
    load_files_list(FILENAME)
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or \
           request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid login'
        else:
            session['logged_in'] = True
            flash('Welcome %s, you are correctly logged in'
                  % app.config['USERNAME'].capitalize())
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Goodbye, you are logged out')
    files_list = []
    return redirect(url_for('login'))


def is_logged(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return abort(401)
        else:
            return f(*args, **kwargs)
    return wrapper


@app.route('/home', methods=['GET', 'POST'])
@is_logged
def home(files_list=files_list):
    return render_template('home.html', files_list=files_list)


@app.route('/upload', methods=['GET', 'POST'])
@is_logged
def upload():
    if request.method == 'POST':
        f = request.files['file']
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            files_list.append(filename)
            save_files_list(FILENAME)
            return redirect(url_for('home'))
    return redirect(url_for('home'))


@app.route('/download/<filename>', methods=['GET'])
@is_logged
def download(filename=None):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename, as_attachment=True)


def main():
    app.run()


if __name__ == '__main__':
    main()
