from functions import check_password, github_api, check_extension, generate_primary_key, to_seconds, find_by_username, find_by_email
from db_functions import create_typing_test_table, add_typing_test, show_all_data
from send_email_file import send_email
from flask import Flask, request, render_template, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os


application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(application)

class Users(db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	user_nickname = db.Column(db.String(30), nullable=False)
	user_email = db.Column(db.String(30), nullable=False)
	user_password = db.Column(db.String(30), nullable=False)
	user_repeat_password = db.Column(db.String(30), nullable=False)
	user_description = db.Column(db.Text, default="")
	user_avatar = db.Column(db.String(50), default="Circle_Davys-Grey_Solid.svg.png")
	user_first_name = db.Column(db.String(30), default="")
	user_last_name = db.Column(db.String(30), default="")
	user_phone_number = db.Column(db.String(30), default="")
	user_github_link = db.Column(db.String(50), default="")
	user_primary_key = db.Column(db.String(10), default="") 
	user_incoming_invitations = db.Column(db.Text, default="empty")
	user_sent_invitations = db.Column(db.Text, default="empty")
	user_friends_list = db.Column(db.Text, default="empty")
	date = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<Users %r>' % self.id


@application.route('/', methods=['POST', 'GET'])
@application.route('/home', methods=['POST', 'GET'])
def main_page():
	if request.method == 'POST':
		user_input = request.form['search-bar']

		if '#' not in user_input:
			return redirect('/home')

		username, primary_key = user_input.split('#')

		table = Users.query.all()

		data = find_by_username(table, username)

		# Make response
		response = make_response(render_template("profile/public-profile.html", data=data))
		response.set_cookie("viewed_profile", data.user_nickname)

		return response

	elif request.method == 'GET':

		if (request.cookies.get("logged_username")):
			cookie_value = request.cookies.get("logged_username")

			table = Users.query.all()

			data = find_by_username(table, cookie_value)

			# Find invites
			if data.user_incoming_invitations.split() and '#' in data.user_incoming_invitations.split()[0]:
				notifications = '!'
			else:
				notifications = ""

			if data:
				response = make_response(render_template("homelogin.html", data=data, notifications=notifications))

				return response

		return render_template('index.html')


@application.route('/typing-test/<string:username>/<int:wpm>', methods=['POST', 'GET'])
def get_request_from_page(username, wpm):
	if request.method == 'POST':
		# Find user
		table = Users.query.all()

		data = find_by_username(table, username)

		add_typing_test(data.user_id, wpm)

		return redirect('/home')


@application.route('/logout')
def logout():
	response = make_response(redirect("/home"))
	response.set_cookie("logged_username", "", 0)

	return response


@application.route('/login', methods=['POST', 'GET'])
def login_page():
	if request.method == 'POST':
		user_login = request.form['login'] 		# Getting values from html
		user_password = request.form['pass']
		inputs = []
		inputs.append(user_login)
		inputs.append(user_password)

		if not all(inputs):
			alert = 'Fields cannot be empty'
			return render_template('log-in.html', alert=alert)

		table = Users.query.all()

		for i in table:		# Conditions for login
			if (i.user_nickname == user_login or i.user_email == user_login) and i.user_password == user_password:

				# Add user to cookie session
				response = make_response(redirect("/home"))
				response.set_cookie("logged_username", i.user_nickname, to_seconds(30))

				return response

		alert = 'Incorrect login or password'
		return render_template('log-in.html', alert=alert)

	elif request.method == 'GET':
		return render_template('log-in.html')


@application.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
	if request.method == 'POST':
		user_email = request.form['email']
		user_password = request.form['password'] 				# Getting values from html
		user_repeat_password = request.form['repeatpassword']
		this_user_nickname = request.form['nickname']
		inputs = []
		result = ['', '', '']
		inputs.append(user_email)
		inputs.append(user_password)
		inputs.append(user_repeat_password)
		inputs.append(this_user_nickname)

		if all(inputs) is False:
			result[0] = 'Fields cannot be empty'
			return render_template('sign-up.html', result=result) 

		list_nicknames, list_emails, list_primary_keys = [], [], []

		table = Users.query.all()

		for i in table:
			list_nicknames.append(i.user_nickname)
			list_emails.append(i.user_email)
			list_primary_keys.append(i.user_primary_key)

		info_nickname = f'Nickname {this_user_nickname} already is use'
		info_email = f'Email {user_email} already registered'
		info_password = "Passwords don't equals"

		if this_user_nickname in list_nicknames:
			result[0] = info_nickname
		if user_email in list_emails:
			result[1] = info_email
		if user_password != user_repeat_password:
			result[2] = info_password

		if result != ['', '', '']:
			return render_template('sign-up.html', result=result)

		current_primary_key = generate_primary_key()
		while current_primary_key in list_primary_keys:		# Generation of a unique user key
			current_primary_key = generate_primary_key()

		users = Users(
			user_nickname=this_user_nickname,
			user_email=user_email,
			user_password=user_password,
			user_repeat_password=user_repeat_password,
			user_primary_key=current_primary_key
			)

		try:
			db.session.add(users) 	# Adding new data to SQL
			db.session.commit()
		except Exception as _ex:
			return _ex

		response = make_response(redirect("/home"))
		response.set_cookie("logged_username", this_user_nickname, to_seconds(30))

		return response

	elif request.method == 'GET':
		result = ['', '', '']
		return render_template('sign-up.html', result=result)


@application.route('/users=<string:key>')
def users_list(key):
	with open('keys/secret-key.txt', 'r', encoding='utf-8') as file:
		output = file.readlines()	# Reading the admin panel key
		current_key = output[0]

	string = f'{current_key} {key}'.split()

	if string[0] == string[1]:
		table = Users.query.all()

		return render_template('admin.html', table=table)
	else:
		return '404 NOT FOUND'

@application.route('/profile')
def profile():
	table = Users.query.all()

	cookie_value = ""

	# Get username from cookie
	if request.cookies.get("logged_username"):
		cookie_value = request.cookies.get("logged_username")

	# Find user
	data = find_by_username(table, cookie_value)

	if data:
		return make_response(render_template("profile/profile.html", data=data))

	return "Error"

@application.route('/edit-profile/', methods=['POST', 'GET'])
def edit_profile():
	if request.method == 'POST':
		file = request.files['file']
		first_name = request.form['first-name']
		last_name = request.form['last-name']
		nickname = request.form['nickname']			# Getting values from html
		email = request.form['email']
		description = request.form['textarea']
		phone_number = request.form['phone-number']
		github_link = request.form['github']
		flag = True 
		table = Users.query.all()

		cookie_value = ""

		# Get username from cookie
		if request.cookies.get("logged_username"):
			cookie_value = request.cookies.get("logged_username")

		# Find user
		current_user = find_by_username(table, cookie_value)

		if not current_user:
			return "Error"

		if first_name == '':
			first_name = current_user.user_first_name
		if last_name == '':
			last_name = current_user.user_last_name
		if nickname == '':
			nickname = current_user.user_nickname
		if email == '': 							# If no value is specified, leave current
			email = current_user.user_email
		if description == '':
			description = current_user.user_description
		if phone_number == '':
			phone_number = current_user.user_phone_number
		if github_link == '':
			github_link = current_user.user_github_link


		if check_extension(file.filename) is False and file.filename != '':
			return 'An error occurred, invalid file extension'

		if file.filename == '': 	# If the image is not transferred, nothing needs to be saved
			flag = False

		if flag:
			user_avatar_path = 'static/img/' + current_user.user_nickname + str(current_user.user_id) + file.filename
			filename = current_user.user_nickname + str(current_user.user_id) + file.filename
			current_user.user_avatar = filename

		current_user.user_first_name = first_name 		
		current_user.user_last_name = last_name 		
		current_user.user_nickname = nickname 			
		current_user.user_email = email 				# Writing data to the database	
		current_user.user_description = description
		current_user.user_phone_number = phone_number
		current_user.user_github_link = github_link

		try:
			db.session.commit()
		except Exception as _ex:
			return _ex

		if flag:
			list_image = os.listdir('static/img') 	# List files in img folder
			for img in list_image:
				if current_user.user_nickname + str(current_user.user_id) in img: 	# If this is the user's previous file
					os.remove(f'static/img/{img}') 				# then it is removed

			file.save(user_avatar_path)		# Saving a picture

		# Add new username to cookie
		response = make_response(redirect("/home"))
		response.set_cookie("logged_username", nickname, to_seconds(30))

		return response

		return redirect("/home")

	elif request.method == 'GET':
		table = Users.query.all()

		cookie_value = ""

		# Get username from cookie
		if request.cookies.get("logged_username"):
			cookie_value = request.cookies.get("logged_username")

		# Find user
		data = find_by_username(table, cookie_value)

		if data:
			return make_response(render_template("profile/profilesetting.html", data=data))

		return "Error"

@application.route('/change-password', methods=['POST', 'GET'])
def change_password():
	if request.method == 'POST':
		table = Users.query.all()

		if request.cookies.get:
			username = request.cookies.get("logged_username")

			data = find_by_username(table, username)

			old_password = request.form['old-password']
			password = request.form['password']
			repeatpassword = request.form['repeatpassword']

			if old_password == "" or password == "" or repeatpassword == "":
				alert_up = 'The field cannot be empty'
				return render_template('changepass.html', alert_up=alert_up, user=user, primary_key=primary_key, key=key)

			if old_password.strip() != data.user_password:
				alert_up = 'You entered the wrong password'
				return render_template('changepass-page.html', alert_up=alert_up, user=user, primary_key=primary_key, key=key)

			if password.strip() != repeatpassword.strip():
				alert_down = "Passwords don't equals"
				return render_template('changepass-page.html', alert_down=alert_down, user=user, primary_key=primary_key, key=key)

			if password.strip() == data.user_password:
				alert_down = 'The new password must not be the same as the old one'
				return render_template('changepass-page.html', alert_down=alert_down, user=user, primary_key=primary_key, key=key)

			data.user_password = password
			data.user_repeat_password = password

			try:
				db.session.commit()
			except Exception as _ex:
				return _ex

			return redirect('/edit-profile')

		return "Error"
	elif request.method == 'GET':
		return render_template('changepass-page.html')


@application.route('/new-password', methods=['POST', 'GET'])
def new_password():
	if request.method == 'GET':
		return render_template('newpassword.html')

	elif request.method == 'POST':
		table = Users.query.all()

		cookie_value = ""

		if request.cookies.get("verify_email"):
			cookie_value = request.cookies.get("verify_email")

		data = find_by_email(table, cookie_value)

		password = request.form['password']
		repeat_password = request.form['repeat-password']

		if password.strip() != repeat_password.strip():
			alert = 'Passwords are not equal!'
			return render_template('newpassword.html', alert=alert)

		if password.strip() == data.user_password:
			alert = 'The new password cannot be equal to the old one!'
			return render_template('newpassword.html', alert=alert)

		data.user_password = password
		data.user_repeat_password = repeat_password

		try:
			db.session.commit()
		except Exception as _ex:
			return _ex

		# Add user to cookie session
		response = make_response(redirect("/home"))
		response.set_cookie("logged_username", data.user_nickname, to_seconds(30))

		return response


@application.route('/forgot-password/<string:page>')
def forgot_password(page):
	table = Users.query.all()
	username = ""

	# Get username from cookie
	if not request.cookies.get("verify_email"):
		username = request.cookies.get("logged_username")

		email = find_by_username(table, username).user_email
	else:
		email = request.cookies.get("verify_email")

	if page == 'l': 	# Mode when the user enters from the login page
		link_back = '/login'
	elif page == 'c': 	# Mode when the user enters from the password change page
		link_back = '/change-password'

	return render_template('forgotpass.html', email=email, link_back=link_back)


@application.route('/enter-login', methods=['POST', 'GET'])
def enter_login():
	if request.method == 'GET':
		return render_template('enterlogin.html')
	elif request.method == 'POST':
		email = request.form['email']

		if email == '':
			alert = 'field cannot be empty!'
			return render_template('enterlogin.html', alert=alert)

		table = Users.query.all()

		for i in table:		# Search for the current user by his email address
			if i.user_email == email:
				data = i
				break
		else:
			alert = 'this email is not registered'
			return render_template('enterlogin.html', alert=alert)

		response = make_response(redirect('/forgot-password/l'))
		response.set_cookie("verify_email", email)

		return response


@application.route('/enter-code', methods=['POST', 'GET'])
def enter_code():
	if request.method == 'GET':
		return render_template('entercode.html')
	elif request.method == 'POST':
		user_code = request.form['security-code']

		if request.cookies.get("verify_code"):
			code_from_cookie = request.cookies.get("verify_code")

			table = Users.query.all()

			if user_code.strip() != code_from_cookie:
				alert = 'Wrong code'
				return render_template('entercode.html', alert=alert)

		return redirect('/new-password')


@application.route('/user-friends-list')
def friend_list():
	table = Users.query.all()

	cookie_value = ""

	# Get username from cookie
	if request.cookies.get("logged_username"):
		cookie_value = request.cookies.get("logged_username")

	# Find user
	data = find_by_username(table, cookie_value)

	# Return error if user undefined
	if not data:
		return "Error"

	friends_list = data.user_friends_list.split()  # Getting data about the user's friends

	for i in range(len(friends_list)):
		friends_list[i] = friends_list[i].split('#')  # Dividing each friend into a tuple (avatar, nickname, key)

	return render_template('friends-page.html', data=data, friends_list=friends_list)


@application.route('/send-invite')
def send_invite():
	table = Users.query.all()

	if request.cookies.get("logged_username") and request.cookies.get("viewed_profile"):
		data = find_by_username(table, request.cookies.get("viewed_profile")) 	# Search for the current user by his unique key

		previous_data = find_by_username(table, request.cookies.get("logged_username")) 	# Search for a previous user by their unique key

		if data.user_incoming_invitations == 'empty': 	# Record data about friend invites
			data.user_incoming_invitations = f'{previous_data.user_avatar}#{previous_data.user_nickname}#{previous_data.user_primary_key}'
		elif f'{previous_data.user_avatar}#{previous_data.user_nickname}#{previous_data.user_primary_key}' not in data.user_incoming_invitations:
			data.user_incoming_invitations += f' {previous_data.user_avatar}#{previous_data.user_nickname}#{previous_data.user_primary_key}'

		try:
			db.session.commit()
		except Exception as _ex:
			return _ex

		return render_template("profile/public-profile.html", data=data)

	return "Error"

@application.route('/invite-list')
def invite_list():
	table = Users.query.all()

	if request.cookies.get("logged_username"):
		data = find_by_username(table, request.cookies.get("logged_username")) 	# Search for the current user by his unique key

		invites_list = data.user_incoming_invitations.split() 	# split all invitations

		for i in range(len(invites_list)):
			invites_list[i] = invites_list[i].split('#') 	# Splitting elements into a tuple (avatar, nickname, key)

		return render_template('invite-list.html', data=data, invites_list=invites_list)

	return "Error"

@application.route('/accept/<string:username>')
def accept(username: str):
	table = Users.query.all()

	if request.cookies.get("logged_username"):
		data = find_by_username(table, request.cookies.get("logged_username"))

		user_from_invite = find_by_username(table, username)

		invites_list = data.user_incoming_invitations.split() 	# Split per invite

		for i in range(len(invites_list)):
			invites_list[i] = invites_list[i].split('#') 	# Splitting elements into a tuple (avatar, nickname, key)
			if invites_list[i][1] == username:		# If this is the user we are accepting invite, remove him
				invites_list[i] = ''
			invites_list[i] = '#'.join(invites_list[i]) 	# Join element back by type avatar#nickname#key

		invites_list = " ".join(invites_list) 	 # Join all invites

		if data.user_friends_list == 'empty': 	# default value
			data.user_friends_list = f'{user_from_invite.user_avatar}#{user_from_invite.user_nickname}#{user_from_invite.user_primary_key}' 	# Adding as a friend and deleting an invitation after that
			data.user_incoming_invitations = invites_list
		elif f'{user_from_invite.user_avatar}#{user_from_invite.user_nickname}#{user_from_invite.user_primary_key}' not in data.user_friends_list:
			data.user_friends_list += f' {user_from_invite.user_avatar}#{user_from_invite.user_nickname}#{user_from_invite.user_primary_key}'
			data.user_incoming_invitations = invites_list

		try:
			db.session.commit()
		except Exception as _ex:
				return _ex

		return redirect('/invite-list')

	return "Error"


@application.route('/accept-send-code')
def accept_send_code():
	table = Users.query.all()

	cookie_value = ""

	# Get username from cookie
	if request.cookies.get("verify_email"):
		cookie_value = request.cookies.get("verify_email")

		# Find user
		data = find_by_email(table, cookie_value)

		verify_code = generate_security_key()
		message = f'Your verify code is:\n{verify_code}'
		recipient = data.user_email

		output = send_email(message, recipient)

		if output == 'Success':
			response = make_response(redirect('/enter-code'))
			response.set_cookie("verify_code")

			return response
		elif output == 'Email invalid':
			alert = 'Email invalid'
			return render_template('forgotpass.html', alert=alert)

	return "Error"


@application.route('/decline/<string:username>')
def decline(username: str):
	table = Users.query.all()

	if request.cookies.get("logged_username"):
		data = find_by_username(table, request.cookies.get("logged_username"))

		invites_list = data.user_incoming_invitations.split() 	# Split per invite

		for i in range(len(invites_list)):
			invites_list[i] = invites_list[i].split('#') 	# Splitting elements into a tuple (avatar, nickname, key)
			if invites_list[i][1] == username: 		# If this is the user we are declining invite, remove him
				invites_list[i] = ''
			invites_list[i] = '#'.join(invites_list[i]) 	# Join element back by type avatar#nickname#key

		invites_list = " ".join(invites_list) 	 # Join all invites

		data.user_incoming_invitations = invites_list 		# Rewriting the invite list

		try:
			db.session.commit()
		except Exception as _ex:
			return _ex

		return redirect('/invite-list')

	return "Error"


if __name__ == '__main__':
	#github_api('ViLsonCake')
	#github_api('IsNAble')
	#generate_admin_key('secret-key.txt')
	#generate_users_key('users-key.txt')

	application.run(debug=True)
