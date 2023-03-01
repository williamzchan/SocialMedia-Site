######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
from datetime import datetime

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Password'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/AddFriends', methods=['GET', 'POST'])
@flask_login.login_required
def AddFriends():
	if flask.request.method == 'GET':
		return '''
				<form action='AddFriends' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
			<a href='/'>Home</a>
				'''
	email = flask.request.form['email']
	if(email == ""):
		return render_template('hello.html', message= 'could not find all tokens')
	cursor = conn.cursor()
	if cursor.execute("SELECT user_id FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		u2 = str(data[0][0])

		cursor.execute("SELECT user_id FROM Users WHERE email = '{0}'".format(flask_login.current_user.id))
		data = cursor.fetchall()
		u1 = str(data[0][0])
		
		if cursor.execute("SELECT user1_ID, user2_ID FROM friends WHERE user1_ID = '{0}' and user2_ID = '{1}'".format(u1, u2)):
			return render_template('addFriends.html', message='Already Friends.')
		else:
			cursor.execute("INSERT INTO friends (user1_ID, user2_ID) VALUES ('{0}', '{1}')".format(u1, u2))
			conn.commit()

		return render_template('addFriends.html', message='Added!', userid=getNameFromID(u2))
	
	return  render_template('addFriends.html', message='User Not Found.')

@app.route('/MyFriends', methods=['GET'])
@flask_login.login_required
def MyFriends():
	cursor = conn.cursor()
	cursor.execute("SELECT user2_ID FROM friends WHERE user1_ID = '{0}'".format(getUserIdFromEmail(flask_login.current_user.id)))
	friends = cursor.fetchall()
	return render_template('showFriends.html', friends = friends)

@app.route('/MyFriends', methods=['POST'])
def SearchFriends():
	try:
		uid = request.form.get('uid')
	except:
		return flask.redirect(flask.url_for('MyFriends'))
	
	if(uid == ""):
		return render_template('hello.html', message= 'could not find all tokens')
	
	cursor = conn.cursor()
	cursor.execute("SELECT first_name FROM Users WHERE user_ID = '{0}'".format(uid))
	name = cursor.fetchone()[0]
	return render_template('hello.html', message = name, photos=getUsersPhotos(uid), likes = getAllPhotosLikes(uid), base64=base64)

@app.route('/activities')
def activities():
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM users order by contribution_score desc LIMIT 10")
	users = cursor.fetchall()
	return render_template('topUsers.html', users = users)

@app.route('/comments', methods=['POST'])
def comments():
	try:
		comment = request.form.get('comment')
		pid = request.form.get('pid')
		like = request.form.get('like')
	except:
		return render_template('hello.html', message= 'could not find all tokens')
	
	if(comment == "" or pid == ""):
		return render_template('hello.html', message= 'could not find all tokens')

	try:
		user = flask_login.current_user.id
	except:
		user = "guest"

	cursor = conn.cursor()

	if(like != "" and user != "guest"):
		if(isLikeUnique(getUserIdFromEmail(flask_login.current_user.id), pid)):
			cursor.execute("INSERT INTO likes (user_id, picture_id) VALUES ('{0}', '{1}')".format(getUserIdFromEmail(flask_login.current_user.id), pid))
		else:
			return render_template('hello.html', message= 'you cannot like a picture twice')


	cursor.execute("SELECT comment_id FROM comments order by comment_id desc LIMIT 1")
	cid = cursor.fetchone()[0]

	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM pictures WHERE picture_id = '{0}'".format(pid))
	owner = cursor.fetchone()[0]

	if(getUserIdFromEmail(flask_login.current_user.id) != owner):
		cursor.execute("INSERT INTO comments (comment_text, commenter, date_of_comment) VALUES ('{0}', '{1}', '{2}')".format(comment, user, datetime.now().strftime('%Y-%m-%d')))
		conn.commit()
		if(user == "guest"):
			cursor.execute("INSERT INTO commented (user_id, comment_id, picture_id) VALUES ('{0}', '{1}', '{2}')".format(12, cid, pid))
			conn.commit()
		else:
			cursor.execute("INSERT INTO commented (user_id, comment_id, picture_id) VALUES ('{0}', '{1}', '{2}')".format(getUserIdFromEmail(flask_login.current_user.id), cid, pid))
			conn.commit()
			increaseContributionScore(getUserIdFromEmail(flask_login.current_user.id))
	else:
		return render_template('hello.html', message= 'Cannot comment on your own picture')

	return render_template('hello.html', message= 'Commeted')




@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		first_name = request.form.get('first_name')
		last_name = request.form.get('last_name')
		dob = request.form.get('dob')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	
	if(email == "" or password == "" or first_name == "" or last_name == "" or dob == ""):
		return render_template('hello.html', message= 'could not find all tokens')
	
	hometown = request.form.get('hometwon')
	gender = request.form.get('gender')
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (email, password, first_name, last_name, dob, hometown, gender, contribution_score) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')".format(email, password, first_name, last_name, dob, hometown, gender, 0)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getAllPhotosLikes(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT U.first_name, P.picture_id FROM users U, likes L, pictures P WHERE P.user_id = '{0}' AND L.picture_id = P.picture_id AND L.user_id = U.user_ID".format(uid))
	return cursor.fetchall()

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getNameFromID(id):
	cursor = conn.cursor()
	cursor.execute("SELECT first_name FROM Users WHERE user_id = '{0}'".format(id))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
	
def isLikeUnique(uid, pid):
	
	cursor = conn.cursor()
	if cursor.execute("SELECT picture_id FROM likes WHERE user_id = '{0}' AND picture_id = '{1}'".format(uid, pid)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

def increaseContributionScore(id):
	cursor = conn.cursor()
	cursor.execute("UPDATE users set contribution_score = contribution_score + 1 WHERE user_id = '{0}'".format(id))
	conn.commit()
	return 

@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, photos=getUsersPhotos(getUserIdFromEmail(flask_login.current_user.id)), likes = getAllPhotosLikes(getUserIdFromEmail(flask_login.current_user.id)), base64=base64, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		photo_data =imgfile.read()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Pictures (imgdata, user_id, caption, like_count) VALUES (%s, %s, %s)''', (photo_data, uid, caption))
		conn.commit()
		increaseContributionScore(getUserIdFromEmail(flask_login.current_user.id))
		#add something to go into album
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid), base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code
#albums stuff
@app.route('/albums', methods=['GET'])
@flask_login.login_required
def albums():
   uid = getUserIdFromEmail(flask_login.current_user.id)
   cursor = conn.cursor()
   cursor.execute("SELECT album_id, album_name FROM Albums WHERE user_id = '{0}'".format(uid))
   albums = cursor.fetchall()
   return render_template('albums.html', albums=albums)
#aid being album id maybe not work idk
def getAlbumPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id,  album_name, user_ID, date_of_creation FROM album WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]






#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
