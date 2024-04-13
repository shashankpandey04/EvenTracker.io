from flask import Flask, session, render_template, request, redirect, url_for,flash
import mysql.connector as mysql
import requests

app = Flask(__name__)
mycon = mysql.connect( host="localhost", user="root", passwd="root", database="flaskdb")
mycur = mycon.cursor()
app.secret_key = 'secret'

def check_user(username, password):
    mycur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = mycur.fetchone()
    return user

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = check_user(username, password)
        user = user[0] if user != None else None
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials. Please try again.", "error")
            return render_template('login.html')
    return render_template('login.html')

@app.route("/dashboard")
def dashboard():
    if 'username' in session:
        username = session['username']
        mycur.execute("SELECT COUNT(*) FROM event WHERE username = %s", (username,))
        total_events = mycur.fetchone()[0]  # Fetching the total count of events
        
        mycur.execute("SELECT name FROM event WHERE username = %s", (username,))
        events = mycur.fetchall()  # Fetching all events
        
        return render_template('dashboard.html', total_events=total_events, events=events)
    else:
        return render_template('403.html')

@app.route("/pricing")
def pricing():
    return render_template('pricing.html')

@app.route("/logout")
def logout():
    session.pop('username', None)
    flash("You have been logged out", "info")
    return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            mycur.execute('SELECT * FROM users WHERE username = %s', (username,))
            if mycur.fetchone():
                flash("Username already exists", "error")
                return render_template('register.html')
            else:
                mycur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                mycon.commit()
                return redirect(url_for('login'))
        except Exception as e:
            print(e)
            flash("An error occurred. Please try again", "error")
            return render_template('register.html')
    return render_template('register.html')

@app.route('/about-us')
def aboutus():
    return render_template('aboutus.html')

@app.route('/events')
def events():
    if 'username' in session:
        username = str(session['username'])
        mycur.execute("SELECT * FROM event WHERE username = %s", (username,))
        events = mycur.fetchall()
        return render_template('events.html', events=events)
    else:
        return render_template('403.html')

@app.route('/add-event', methods=['GET','POST'])
def add_event():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        date = request.form['date']
        time = request.form['time']
        try:
            mycur.execute("INSERT INTO event (username, name, date, time,location) VALUES (%s, %s, %s, %s, %s)", (session['username'], name, date, time,location))
            mycon.commit()
            flash("Event created successfully", "info")
        except Exception as e:
            print(e)
            flash("An error occurred. Please try again", "error")
        return redirect(url_for('events'))
    return render_template('dashboard.html')

app.run(debug=True, port=5000)