import hashlib
from flask import Flask, request, render_template, session, flash, redirect, url_for, g
from flask.ext.pymongo import PyMongo

app = Flask(__name__)
app.secret_key = 'cocaines'
mongo = PyMongo(app)


def install(username, password):
    return create_user(username, password, admin=True)


@app.before_request
def before_request():
    pass


@app.teardown_request
def teardown_request(exception):
    pass


@app.route('/')
def hello_world():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('admin.html')


def create_user(username, password, admin=False):
    return mongo.db.users.insert({'_id': username, 'password': hashlib.sha1(password).hexdigest(), 'admin': admin},
                                 safe=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template('register.html', error="Username/password cannot be empty")

        session['logged_in'] = True
        flash('You are registered')
        create_user(username, password)

        return redirect(url_for('admin'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = mongo.db.users.find_one({'_id': username})
        if user is None:
            return render_template('login.html', error='Invalid username')

        if user['password'] != hashlib.sha1(password).hexdigest():
            return render_template('login.html', error='Invalid password')

        session['logged_in'] = True
        flash('You were logged in')
        return redirect(url_for('admin'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True)
