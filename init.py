#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib
from datetime import datetime

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 8001,
                       user='root',
                       password='root',
                       db='PriCoSha',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route for index
@app.route('/')
def index():
    return render_template('index.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    email = request.form['email']
    password = hashlib.sha256(request.form['password'].encode()).hexdigest()
    fname = request.form['fname']
    lname = request.form['lname']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE email = %s'
    cursor.execute(query, (email))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO Person VALUES(%s, %s, %s, %s)'
        cursor.execute(ins, (email, password, fname, lname))
        conn.commit()
        cursor.close()
        return render_template('index.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    email = request.form['email']
    password = hashlib.sha256(request.form['password'].encode()).hexdigest()

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE email = %s and password = %s'
    cursor.execute(query, (email, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['email'] = email
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

@app.route('/home')
def home():
    email = session['email']
    cursor = conn.cursor()
    query = 'SELECT * FROM ContentItem NATURAL JOIN Belong NATURAL JOIN Share WHERE email = %s ORDER BY post_time DESC'
    cursor.execute(query, (email))
    data = cursor.fetchall()
    items=data
    for item in items:
        check=item.get('item_id')
        query2='SELECT * FROM Tag NATURAL JOIN Person WHERE Tag.email_tagged=Person.email AND item_id=%s AND status="True"'
        cursor.execute(query2, (check))
        data2 = cursor.fetchall()
    cursor.close()
    return render_template('home.html', email=email, items=data, names=data2)

@app.route('/public')
def public():
    cursor = conn.cursor()
    query = 'SELECT item_id, email_post, post_time, file_path, item_name FROM ContentItem WHERE is_pub = 1 AND post_time > DATE_SUB(CURDATE(), INTERVAL 1 DAY) ORDER BY post_time DESC'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('public.html', items=data)

@app.route('/manageFriendgroup')
def manageFriendgroup():
    email = session['email']
    return render_template('manageFriendgroup.html', email=email)

# Start of creating Friendgroup
@app.route('/createFriendgroup')
def createFriendgroup():
    email = session['email']
    return render_template('createFriendgroup.html',email=email)

# Creating a Friendgroup
@app.route('/createFriendgroupAuth', methods=['GET', 'POST'])
def createFriendgroupAuth():
    email = session['email']
    friendgroup = request.form['friendgroup']
    description = request.form['description']
    cursor = conn.cursor()
    # Check if friendgroup was already created
    query = 'SELECT * FROM Friendgroup WHERE owner_email = %s AND fg_name = %s'
    cursor.execute(query, (email, friendgroup))
    data = cursor.fetchone()
    error = None
    if(data):
        error = "This friendgroup is already created by you"
        return render_template('createFriendgroup.html', error=error)
    else:
        # Create Friendgroup and insert into Friendgroup table
        ins = 'INSERT INTO Friendgroup VALUES(%s, %s, %s)'
        cursor.execute(ins, (email, friendgroup, description))
        conn.commit()
        # Also insert owner into Belong table
        ins2 = 'INSERT INTO Belong VALUES(%s, %s, %s)'
        cursor.execute(ins2, (email, email, friendgroup))
        conn.commit()
        cursor.close()
        return redirect(url_for('createFriendgroup'))

@app.route('/addFriend')
def addFriend():
    email = session['email']
    return render_template('addFriend.html', email=email)

@app.route('/addFriendAuth', methods=['GET', 'POST'])
def addFriendAuth():
    email = session['email']
    friendFirst = request.form['friendFirst']
    friendLast = request.form['friendLast']
    friendEmail = request.form['friendEmail']
    friendgroup = request.form['friendgroup']
    cursor = conn.cursor()
    query = 'SELECT email FROM Person WHERE fname = %s AND lname = %s'
    cursor.execute(query, (friendFirst, friendLast))
    data = cursor.fetchall()
    print(friendEmail)
    query2 = 'SELECT * FROM Friendgroup WHERE owner_email = %s AND fg_name = %s'
    cursor.execute(query2, (email, friendgroup))
    data2 = cursor.fetchone()
    query3 = 'SELECT * FROM Belong WHERE owner_email = %s AND fg_name = %s AND email = (SELECT email FROM Person WHERE fname = %s AND lname = %s)'
    cursor.execute(query3, (email, friendgroup, friendFirst, friendLast))
    data3 = cursor.fetchone()
    error = None
    if(data is None):
        error = "This friend does not exist"
        return render_template('addFriend.html', error=error)
    elif(len(data) > 1 and friendEmail is None):
        error = "Please specify friend's email"
        return render_template('addFriend.html', error=error)
    elif(data2 is None):
        error = "This friendgroup does not exist"
        return render_template('addFriend.html', error=error)
    elif(data3):
        error = "This friend is already in the friendgroup"
        return render_template('addFriend.html', error=error)
    else:
        if(friendEmail == ""):
            friendEmail = data[0].get('email')
            print(friendEmail)
        ins = 'INSERT INTO Belong VALUES(%s, %s, %s)'
        cursor.execute(ins, (friendEmail, email, friendgroup))
        conn.commit()
        cursor.close()
        return redirect(url_for('addFriend'))

@app.route('/managePosts')
def managePosts():
    email = session['email']
    return render_template('managePosts.html', email=email)

@app.route('/createPublicPost')
def createPublicPost():
    email = session['email']
    return render_template('createPublicPost.html', email=email)

@app.route('/createPublicPostAuth', methods=['GET', 'POST'])
def createPublicPostAuth():
    email = session['email']
    itemID = request.form['itemID']
    filePath = request.form['filePath']
    itemName = request.form['itemName']
    cursor = conn.cursor()
    query = 'SELECT * FROM ContentItem WHERE item_id = %s AND email_post = %s'
    cursor.execute(query, (itemID, email))
    data = cursor.fetchone()
    error = None
    if(data):
        error = "You have already posted about this item"
        return render_template('createPublicPost.html', error=error)
    else:
        ins = 'INSERT INTO ContentItem VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (itemID, email, datetime.now(), filePath, itemName, 1))
        conn.commit()
        cursor.close()
        return redirect(url_for('createPublicPost'))

@app.route('/createPrivatePost')
def createPrivatePost():
    email = session['email']
    cursor = conn.cursor()
    query = 'SELECT fg_name FROM Belong WHERE email = %s'
    cursor.execute(query, (email))
    data = cursor.fetchall()
    error = None
    if(data is None):
        error = "You are not in any friendgroups"
        return render_template('createPrivatePost.html', error=error)
    else:
        return render_template('createPrivatePost.html', groups=data)

@app.route('/createPrivatePostAuth', methods=['GET', 'POST'])
def createPrivatePostAuth():
    email = session['email']
    itemID = request.form['itemID']
    filePath = request.form['filePath']
    itemName = request.form['itemName']
    friendgroups = request.form.getlist('friendgroups')
    cursor = conn.cursor()
    query = 'SELECT * FROM ContentItem WHERE item_id = %s AND email_post = %s'
    cursor.execute(query, (itemID, email))
    data = cursor.fetchone()
    error = None
    if(data):
        error = "You have already posted about this item"
        return render_template('createPrivatePost.html', error=error)
    elif(len(friendgroups) == 0):
        error = "You did not select a friendgroup"
        return render_template('createPrivatePost.html', error=error)
    else:
        ins = 'INSERT INTO ContentItem VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (itemID, email, datetime.now(), filePath, itemName, 0))
        conn.commit()
        for i in range(len(friendgroups)):
            query2 = 'SELECT * FROM Share WHERE item_id = %s AND owner_email = (SELECT owner_email FROM Belong WHERE email = %s AND fg_name = %s) AND fg_name = %s'
            cursor.execute(query2, (itemID, email, friendgroups[i], friendgroups[i]))
            data2 = cursor.fetchone()
            error2 = None
            if(data2):
                error2 = "You have already shared this item with " + friendgroups[i]
                return render_template('createPrivatePost.html', error2=error2)
            else:
                query3 = 'SELECT owner_email FROM Belong WHERE email = %s AND fg_name = %s'
                cursor.execute(query3, (email, friendgroups[i]))
                data3 = cursor.fetchone()
                ins2 = 'INSERT INTO Share VALUES(%s, %s, %s)'
                cursor.execute(ins2, (data3.get('owner_email'), friendgroups[i], itemID))
                conn.commit()
        cursor.close()
        return redirect(url_for('createPrivatePost'))

@app.route('/manageTags')
def manageTags():
    email=session['email']
    return render_template('ManageTags.html', email=email)

@app.route('/tag')
def tag():
    email=session['email']
    return render_template('Tag.html', email=email)

@app.route('/tagAuth', methods=['GET', 'POST'])
def tagAuth():
    email=session['email']
    item_id=request.form['item_id']
    tagged_email=request.form['tagged_email']
    cursor=conn.cursor()
    query='SELECT * FROM ContentItem NATURAL JOIN Share NATURAL JOIN Belong WHERE item_id = %s AND email = %s'
    cursor.execute(query, (item_id, email))
    data=cursor.fetchone()
    error=None
    if(data is None):
        error='This item is not visible to you'
        return render_template('Tag.html', error=error)
    else:
        query2='SELECT * FROM ContentItem NATURAL JOIN Share NATURAL JOIN Belong WHERE item_id = %s AND email = %s'
        cursor.execute(query2, (item_id, tagged_email))
        data2=cursor.fetchone()
        error=None
        if(data2 is None):
            error='This item is not visible to the person you have tagged'
            return render_template('Tag.html', error=error)
        else:
            ins = 'INSERT INTO Tag VALUES(%s, %s, %s, %s, %s)'
            cursor.execute(ins, (tagged_email, email, item_id, 'False', datetime.now()))
            conn.commit()
            cursor.close()
            return redirect(url_for('manageTags'))

@app.route('/AcceptDecline')
def accdec():
    email=session['email']
    cursor=conn.cursor()
    query='SELECT * FROM Tag WHERE email_tagged=%s AND status=%s'
    cursor.execute(query, (email, 'False'))
    data=cursor.fetchall()
    error=None
    if(data is None):
        error='No pending tags'
        return render_template('AcceptDecline.html', error=error)
    else:
        return render_template('AcceptDecline.html', tags=data)

@app.route('/AcceptDeclineAuth', methods=['GET', 'POST'])
def accdecauth():
    email=session['email']
    tagger=request.form['tagger']
    item_id=request.form['item_id']
    decide=request.form['decide']
    cursor=conn.cursor()
    query='SELECT * FROM Tag WHERE email_tagger=%s AND email_tagged = %s AND item_id = %s AND status=%s'
    cursor.execute(query, (tagger, email, item_id, 'False'))
    data=cursor.fetchone()
    error = None
    if(data is None):
        error = "Invalid Tag information"
        return render_template('AcceptDecline.html', error=error)
    else:
        if decide=='accept':
            ins='UPDATE Tag SET status=%s WHERE email_tagged=%s AND email_tagger=%s AND item_id=%s'
            cursor.execute(ins, ('True', email, tagger, item_id))
            conn.commit()
        elif decide=='decline':
            ins2='DELETE FROM  Tag WHERE email_tagged=%s AND email_tagger=%s AND item_id=%s'
            cursor.execute(ins2, (email, tagger, item_id))
            conn.commit()
        cursor.close()
        return redirect(url_for('manageTags'))

# Start of deleting a friend
@app.route('/deleteFriend')
def deleteFriend():
    email=session['email']
    return render_template('deleteFriend.html', email=email)

# Deleting a friend
@app.route('/deleteFriendAuth', methods=['GET', 'POST'])
def deleteFriendAuth():
    email=session['email']
    exfriend=request.form['exfriend']
    cursor=conn.cursor()
    # Check if the friend exists
    query='SELECT * FROM Belong WHERE owner_email=%s AND email=%s'
    cursor.execute(query, (email, exfriend))
    data=cursor.fetchone()
    error=None
    if(data is None):
        error="No such friend exists"
        return render_template('deleteFriend.html', error=error)
    else:
        # Delete friend from the Belong table
        query2 = 'DELETE FROM Belong WHERE owner_email=%s AND email=%s'
        cursor.execute(query2, (email, exfriend))
        conn.commit()
        # Delete friend from Tag table and all the other tags associated within that friendgroup
        query3 = 'DELETE FROM Tag WHERE email_tagger IN (SELECT email FROM Belong WHERE owner_email = %s) AND email_tagged=%s'
        cursor.execute(query3, (email, exfriend))
        conn.commit()
        cursor.close()
        return redirect(url_for('manageFriendgroup'))

@app.route('/logout')
def logout():
    session.pop('email')
    return redirect('/')
    
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
