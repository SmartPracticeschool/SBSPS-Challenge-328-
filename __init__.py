from __future__ import division, print_function

from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session
import sqlite3 as sql
import os
# coding=utf-8
import sys
import glob
import json
import operator
from watson_developer_cloud import VisualRecognitionV3
from werkzeug.utils import secure_filename
from twilio.rest import Client

app = Flask(__name__)
kir={}
z=1
  
@app.route('/')
def home():
    return render_template('userprehome.html')


# admin site
@app.route('/admin')
def admin():
    return render_template('admin.html')


# Creating new database
@app.route('/bus.html')
def new_student():
    conn = sql.connect('database.db')
    print("Opened database successfully")
    conn.execute(
        'CREATE TABLE IF NOT EXISTS buses (id INTEGER PRIMARY KEY,name TEXT, source TEXT, destination TEXT, time TEXT, price INT,nos INT,rem INT)')
    print("Table created successfully")
    conn.close()
    return render_template('bus.html')


# Adding new bus record
@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:

            nm = request.form['nm']
            sourc = request.form['src']
            desti = request.form['dest']
            tim = request.form['t']
            pric = request.form['p']
            nos = request.form['nos']
            rem = nos

            with sql.connect("database.db") as con:
                cur = con.cursor()

                cur.execute("INSERT INTO buses (name,source,destination,time,price,nos,rem) VALUES (?,?,?,?,?,?,?)",
                            (nm, sourc, desti, tim, pric, nos, rem))

                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("result.html", msg=msg)
            con.close()


# renders template to delete a bus record
@app.route('/delete.html')
def deleterecord():
    return render_template('delete.html')


# delete the record
@app.route('/delrec', methods=['POST', 'GET'])
def delrec():
    if request.method == 'POST':
        try:

            id = request.form['id']

            with sql.connect("database.db") as con:
                cur = con.cursor()

                cur.execute("DELETE FROM buses WHERE id=(?)", (id,))

                con.commit()
                msg = "result of delete operation: Record successfully deleted"
        except:
            con.rollback()
            msg = "Result of delete operation: error in delete operation"

        finally:
            return render_template("result.html", msg=msg)
            con.close()


@app.route('/find.html')
def findrecord():
    return render_template('find.html')


# find the record
@app.route('/findbus', methods=['POST', 'GET'])
def findbus():
    src = request.form['src']
    desti = request.form['dest']
    tradate = request.form['tradate']
    con = sql.connect("database.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("SELECT * FROM buses WHERE source=(?) AND destination=(?) AND rem!=0 AND time=(?)", (src, desti, tradate))

    rows = cur.fetchall();
    if (rows):
        msg = "LIST OF BUSES FOR GIVEN SOURCE AND DESTINATION"
        return render_template("list.html", rows=rows, msg=msg)
    else:
        msg = "NO BUSES AVAILABLE"
        return render_template("result.html", msg=msg)


# list all records
@app.route('/list.html')
def list():
    username = session['username']
    con = sql.connect("database.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from buses")

    rows = cur.fetchall();
    msg = "LIST OF ALL BUSES"
    return render_template("list.html", rows=rows, msg=msg, user=username)


# list all buses booked by user
@app.route('/userbookinglist.html')
def userbookinglist():
    username = session['username']
    pw = session['password']
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    flag = 1  # to prevent find form from displaying
    cur = con.cursor()
    cur.execute("select * from user where name=(?) AND pass=(?)", (username, pw))
    row = cur.fetchone();
    userid = row[0]
    cur.execute("select * from book where userid=(?)", (userid,))
    rows = cur.fetchall();
    msg = "LIST OF ALL BUSES"
    return render_template("list1.html", rows=rows, msg=msg, user=username, fl=flag)


@app.route('/bookinglist.html')
def bookinglist():
    username = session['username']
    con = sql.connect("database.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from book")

    rows = cur.fetchall();
    msg = "LIST OF ALL BUSES"
    return render_template("list1.html", rows=rows, msg=msg, user=username)


# list of cancelled bookings
@app.route('/cancellist.html')
def cancellist():
    username = session['username']
    con = sql.connect("database.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from cancel")

    rows = cur.fetchall();
    msg = "LIST OF ALL BUSES"
    return render_template("list1.html", rows=rows, msg=msg, user=username)


# list of users
@app.route('/userlist.html')
def userlist():
    username = session['username']
    con = sql.connect("database.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from user")

    rows = cur.fetchall();
    msg = "LIST OF ALL USERS"
    return render_template("userlist.html", rows=rows, msg=msg, user=username)


# Creating user database
@app.route('/user.html')
def new_user():
    conn = sql.connect('database.db')
    print("Opened database successfully")
    conn.execute('CREATE TABLE IF NOT EXISTS user (ids INTEGER PRIMARY KEY,name TEXT, pass TEXT)')
    print("Table created successfully")
    conn.close()
    return render_template('user.html')


# adding user
@app.route('/adduser', methods=['POST', 'GET'])
def adduser():
    if request.method == 'POST':
        try:
            nm = request.form['nm']
            password = request.form['pass']
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO user (name,pass) VALUES (?,?)", (nm, password))
                con.commit()
                msg = "User record:Record successfully added"
        except:
            con.rollback()
            msg = "User record: error in insert operation"

        finally:
            return render_template("result.html", msg=msg)
            con.close()


# Delete a user
@app.route('/deleteuser.html')
def deleteuserrecord():
    return render_template('delete1.html')


@app.route('/deluserrec', methods=['POST', 'GET'])
def deluserrec():
    if request.method == 'POST':
        try:

            id = request.form['id']

            with sql.connect("database.db") as con:
                cur = con.cursor()

                cur.execute("DELETE FROM user WHERE ids=(?)", (id,))

                con.commit()
                msg = "result of delete operation: Record successfully deleted"
        except:
            con.rollback()
            msg = "Result of delete operation: error in delete operation"

        finally:
            return render_template("result.html", msg=msg)
            con.close()


@app.route('/user')  # user and admin login
def user():
    flag = 0
    if 'username' in session:
        username = session['username']
        pw = session['password']
        if username == 'admin' and pw == 'admin':
            flag = 1
        elif username == 'traffic' and pw == 'police':
            flag = 3
        else:
            con = sql.connect("database.db")
            con.row_factory = sql.Row

            cur = con.cursor()
            cur.execute("SELECT * FROM user WHERE name=(?) AND pass=(?) ", (username, pw))

            rows = cur.fetchone();
            if (rows):
                flag = 2
        if flag == 1:
            return render_template('admin.html')
        elif flag == 3:
            return render_template('bas.html')
        elif flag == 2:
            return render_template('userhome.html', user=username)

        else:
            return "You are not logged in as username or password is incorrect <br><a href = '/login'></b>" + \
                   "click here to log in</b></a>"

    return render_template('userprehome.html')  # initial page for login/sign up

@app.route('/predict', methods=['GET', 'POST'])
def upload():

    if request.method == 'POST':
        # Get the file from post request
        f = request.files['image']
        x=""
        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)
        visual_recognition = VisualRecognitionV3('2018-03-19',iam_apikey='d1ritDZ_IYG2pcxYGByisbcKdrH7MOLSjptMbd5AN9Em')
        with open(file_path, 'rb') as images_file:
            classes = visual_recognition.classify(images_file,threshold='0.6',classifier_ids='DefaultCustomModel_1528303781').get_result()
            a=json.loads(json.dumps(classes, indent=3))
            preds=a['images'][0]['classifiers'][0]['classes']
            print(a)
            for i in preds:
                x=i['class']
                y=i['score']
                global z
                x=x+str(z)
                z=z+1
                kir.update({x:y})
            print(kir)
        return x+" :"+str(y)
    return None 

@app.route('/light', methods=['GET', 'POST'])
def light():  
    traffic={}
    lesstraffic={}
    k=0
    l=0
    ind=[]
    for m,n in kir.items():
        if m.startswith('traffic',0):
            traffic.update({m:n})
        else:
            lesstraffic.update({m:n})
    traffic = dict(sorted(traffic.items(), key=operator.itemgetter(1),reverse=True))
    lesstraffic= dict(sorted(lesstraffic.items(), key=operator.itemgetter(1)))
    print(traffic)
    print(lesstraffic)
    for k in traffic:
        ind.append(k[-1])
    for l in lesstraffic:
        ind.append(l[-1])
    return render_template('tralight1.html',ind=ind)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']

        return redirect(url_for('user'))
    return render_template('userlogin.html')


@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    return redirect(url_for('user'))


@app.route('/book.html')
def book():
    conn = sql.connect('database.db')
    print("Opened database successfully")
    conn.execute(
        'CREATE TABLE IF NOT EXISTS book (bookid INTEGER PRIMARY KEY,busid TEXT,busname TEXT,userid TEXT,username TEXT,nopass TEXT)')
    print("Table created successfully")
    conn.close()
    return render_template('find.html')


@app.route('/booking', methods=['POST', 'GET'])
def booking():
    if request.method == 'POST':
        try:
            idbus = request.form['id']
            nop = request.form['nop']
            num=request.form['num']
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM buses WHERE id=(?)", (idbus,))
                bus = cur.fetchone()
                busn = bus[1]
                num_seats = bus[7]
                username = session['username']
                pw = session['password']
                cur.execute("SELECT * FROM user WHERE name=(?) AND pass=(?) ", (username, pw))
                rows = cur.fetchone()
                user = rows[0]
                un = rows[1]
                cur.execute("INSERT INTO book (busid,busname,userid,username,nopass) VALUES (?,?,?,?,?)",
                            (idbus, busn, user, un, nop))
                new_rem = int(num_seats) - int(nop)
                cur.execute("UPDATE buses SET rem=(?) WHERE id=(?)", (new_rem, idbus))
                con.commit()
                client = Client("AC25efff9599401a3789a4b48b7bf19fac", "73ccf19912d3066d281d9c01bffdf10b")
                client.messages.create(to="+91"+str(num), 
                       from_="+12569523813", 
                       body="Ticket booking success!")
                msg = "Booking success"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("result.html", msg=msg)
            con.close()


@app.route('/cancel.html')
def cancel():
    conn = sql.connect('database.db')
    print("Opened database successfully")
    conn.execute(
        'CREATE TABLE IF NOT EXISTS cancel (canid INTEGER PRIMARY KEY,bookid TEXT,busid TEXT,busname TEXT,userid TEXT,username TEXT,nopass TEXT)')
    print("Table created successfully")
    conn.close()
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    username = session['username']
    pw = session['password']
    cur.execute("SELECT * FROM user WHERE name=(?) AND pass=(?) ", (username, pw))
    rows = cur.fetchone();
    user = rows[0]

    cur.execute("SELECT * FROM book WHERE userid=(?)", (user,))

    rows = cur.fetchall();
    username = session['username']
    if (rows):
        msg = "LIST OF BUSES FOR BOOKED BY YOU"
        return render_template("cancel.html", rows=rows, msg=msg)
    else:
        msg = "NO BUSES BOOKED"
        return render_template("result.html", msg=msg, user=username)
    con.close()


@app.route('/canceling', methods=['POST', 'GET'])
def canceling():
    if request.method == 'POST':
        try:
            canid = request.form['id']
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM book WHERE bookid=(?)", (canid,))
                can = cur.fetchone()
                nop = can[5]
                print(nop)
                cur.execute("INSERT INTO cancel (bookid,busid,busname,userid,username,nopass) VALUES (?,?,?,?,?,?)",
                            (can[0], can[1], can[2], can[3], can[4], can[5]))
                print(can[1])
                cur.execute("SELECT * FROM buses WHERE id=(?)", (can[1],))
                bus = cur.fetchone()
                print('bus')
                rem = bus[7]
                new_rem = int(rem) + int(nop)
                print(new_rem)
                cur.execute("UPDATE buses SET rem=(?) WHERE id=(?)", (new_rem, can[1],))
                print(can[1])
                cur.execute("DELETE FROM book WHERE bookid=(?)", (canid,))
                con.commit()
                msg = "canceling success"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("result.html", msg=msg)
            con.close()


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True)
