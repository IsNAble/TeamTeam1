from functions import check_password, github_api, check_extension, generate_admin_key, generate_users_key, generate_primary_key, check_key
from flask import Flask, request, render_template, redirect, url_for
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


@application.route('/')
@application.route('/home')
def main_page():
	return render_template('index.html')


@application.route('/login', methods=['POST', 'GET'])
def login_page():
	if request.method == 'POST':
		user_login = request.form['login'] 		# Получение значений из html
		user_password = request.form['pass']
		inputs = []
		inputs.append(user_login)
		inputs.append(user_password)

		if all(inputs) is False:
			alert = 'Поля не могут быть пустыми'
			return render_template('log-in.html', alert=alert)


		table = Users.query.all()

		with open('users-key.txt', 'r', encoding='utf-8') as file:
			current_key = file.read()

		for i in table:		# Условия для логина
			if (i.user_nickname == user_login or i.user_email == user_login) and i.user_password == user_password:
				return redirect(f'/home/{i.user_nickname}/{i.user_primary_key}={current_key}')

		alert = 'Неправильный логин или пароль'
		return render_template('log-in.html', alert=alert)

	elif request.method == 'GET':
		alert = ""
		return render_template('log-in.html', alert=alert)


@application.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
	if request.method == 'POST':
		user_email = request.form['email']
		user_password = request.form['password'] 				# Получение значений из html
		user_repeat_password = request.form['repeatpassword']
		this_user_nickname = request.form['nickname']
		inputs = []
		result = ['', '', '']
		inputs.append(user_email)
		inputs.append(user_password)
		inputs.append(user_repeat_password)
		inputs.append(this_user_nickname)

		if all(inputs) is False:
			result[0] = 'Поля не могут быть пустыми'
			return render_template('sign-up.html', result=result) 

		list_nicknames, list_emails, list_primary_keys = [], [], []

		table = Users.query.all()

		for i in table:
			list_nicknames.append(i.user_nickname)
			list_emails.append(i.user_email)
			list_primary_keys.append(i.user_primary_key)


		info_nickname = f'Никнейм {this_user_nickname} занят'
		info_email = f'Почта {user_email} уже зарегистрирована'
		info_password = 'Пароли не совпадают'

		if this_user_nickname in list_nicknames:
			result[0] = info_nickname
		if user_email in list_emails:
			result[1] = info_email
		if user_password != user_repeat_password:
			result[2] = info_password

		if result != ['', '', '']:
			return render_template('sign-up.html', result=result)

		current_primary_key = generate_primary_key()
		while current_primary_key in list_primary_keys:		# Генерация собственного ключа пользователя
			current_primary_key = generate_primary_key()

		users = Users(
			user_nickname=this_user_nickname,
			user_email=user_email,
			user_password=user_password,
			user_repeat_password=user_repeat_password,
			user_primary_key=current_primary_key
			)

		try:
			db.session.add(users) 	# Добавление новых данных в SQL
			db.session.commit()
		except:
			return 'error'	

		table = Users.query.all()

		with open('users-key.txt', 'r', encoding='utf-8') as file:
			current_key = file.read()	# Считывание текущего ключа

		for i in table:		# Поиск текущего пользователя в бд
			if i.user_nickname == this_user_nickname:
				return redirect(f'/home/{i.user_nickname}/{i.user_primary_key}={current_key}') 

	elif request.method == 'GET':
		result = ['', '', '']
		return render_template('sign-up.html', result=result)


@application.route('/users=<string:key>')
def users_list(key):
	with open('secret-key.txt', 'r', encoding='utf-8') as file:
		output = file.readlines()	# Считывание ключа админ-панели
		current_key = output[0]

	string = f'{current_key} {key}'.split()

	if string[0] == string[1]:
		table = Users.query.all()

		return render_template('admin.html', table=table)
	else:
		return '404 NOT FOUND'


@application.route('/home/<string:user>/<string:primary_key>=<string:key>', methods=['POST', 'GET'])
def user(user, primary_key, key):
	if request.method == 'GET':
		table = Users.query.all()

		for i in table:		# Поиск текущего пользователя по его уникальному ключу
			if i.user_primary_key == primary_key:
				data = i
				break
		else:
			return 'User not found'

		with open('users-key.txt', 'r', encoding='utf-8') as file:
			current_key = file.read() 	# Считывание текущего ключа

		string = f'{current_key} {key}'.split()

		if data.user_incoming_invitations == 'empty':
			notifications = ""
		else:
			notifications = '!'

		if data is not None and data.user_nickname == user and string[0] == string[1]:
			return render_template('homelogin.html', data=data, current_key=current_key, notifications=notifications)
		else:
			return 'User not found'
	elif request.method == 'POST':
		nickname_with_key = request.form['search-bar']		# Получение никнейма и айди пользователя из поиска

		table = Users.query.all()

		for i in table:		# Поиск текущего пользователя по его уникальному ключу
			if i.user_primary_key == primary_key:
				data = i
				break
		else:
			return 'User not found'

		if '#' not in nickname_with_key:
			with open('users-key.txt', 'r', encoding='utf-8') as file:
				current_key = file.read() 	# Считывание текущего ключа

			alert = 'Неккоректный поиск'
			return render_template('homelogin.html', data=data, current_key=current_key, alert=alert)

		nickname_with_key = nickname_with_key.split('#')
		
		with open('users-key.txt', 'r', encoding='utf-8') as file: 		
			current_key = file.read()

		table = Users.query.all()

		for i in table:
			if i.user_primary_key == nickname_with_key[1]:
				return redirect(f'/public-profile/{nickname_with_key[0]}/{primary_key}-{nickname_with_key[1]}={current_key}')
		else:
			alert = 'Такого пользователя не существует'
			return render_template('homelogin.html', data=data, current_key=current_key, alert=alert)


@application.route('/profile/<string:user>/<string:primary_key>=<string:key>')
def profile(user, primary_key, key):
	table = Users.query.all()

	for i in table:		# Поиск текущего пользователя по его уникальному ключу
		if i.user_primary_key == primary_key:
			data = i
			break
	else:
		return 'User not found'

	with open('users-key.txt', 'r', encoding='utf-8') as file:
		current_key = file.read()

	string = f'{current_key} {key}'.split()

	if data is not None and data.user_nickname == user and string[0] == string[1]:
		if data.user_first_name == "":
			data.user_first_name = 'No data'
		if data.user_last_name == "":
			data.user_last_name = 'No data'
		if data.user_description == "":
			data.user_description = 'No data'
		if data.user_phone_number == "":
			data.user_phone_number = 'No data'

		return render_template('profile/profile.html', data=data, current_key=current_key)
	else:
		return '404 NOT FOUND'


@application.route('/public-profile/<string:user>/<string:previous_primary_key>-<string:primary_key>=<string:key>', methods=['POST', 'GET'])
def public_profile(user, previous_primary_key, primary_key, key):
	if request.method == 'GET':
		if check_key(key) is not True:
			return '404 NOT FOUND'

		table = Users.query.all()

		for i in table:		# Поиск текущего пользователя по его уникальному ключу
			if i.user_primary_key == primary_key:
				data = i
				break
		else:
			return 'User not found'

		for i in table:
			if i.user_primary_key == previous_primary_key:
				previous_user = i.user_nickname
				break
		else:
			return 'User not found'

		with open('users-key.txt', 'r', encoding='utf-8') as file:
			current_key = file.read()

		string = f'{current_key} {key}'.split()

		if data is not None and data.user_nickname == user and string[0] == string[1]:
			if data.user_first_name == "":
				data.user_first_name = 'No data'
			if data.user_last_name == "":
				data.user_last_name = 'No data'
			if data.user_description == "":
				data.user_description = 'No data'
			if data.user_phone_number == "":
				data.user_phone_number = 'No data'

			return render_template('profile/public-profile.html', data=data, current_key=current_key, previous_user=previous_user, previous_primary_key=previous_primary_key)
		else:
			return '404 NOT FOUND'
	elif request.method == 'POST':
		table = Users.query.all()

		for i in table:		# Поиск текущего пользователя по его уникальному ключу
			if i.user_primary_key == primary_key:
				data = i
				break
		else:
			return 'User not found'

		data.user_incoming_invitations = f'{user}#{previous_primary_key}'

		try:
			db.session.commit()
		except:
			return 'error'

		return redirect(f'public-profile/{user}/{previous_primary_key}-{primary_key}={key}')


@application.route('/edit-profile/<string:user>/<string:primary_key>=<string:key>', methods=['POST', 'GET'])
def edit_profile(user, primary_key, key):
	if request.method == 'POST':
		file = request.files['file']
		first_name = request.form['first-name']
		last_name = request.form['last-name']
		nickname = request.form['nickname']			# Получение значений из html
		email = request.form['email']
		description = request.form['textarea']
		phone_number = request.form['phone-number']
		github_link = request.form['github']
		flag = True 
		table = Users.query.all()

		for i in table:		# Поиск текущего пользователя по его уникальному ключу
			if i.user_primary_key == primary_key:
				data = i
				break
		else:
			return '404 NOT FOUND'

		if first_name == '':
			first_name = current_user.user_first_name
		if last_name == '':
			last_name = current_user.user_last_name
		if nickname == '':
			nickname = current_user.user_nickname
		if email == '': 							# Если значение не указано, оставлять текущее
			email = current_user.user_email
		if description == '':
			description = current_user.user_description
		if phone_number == '':
			phone_number = current_user.user_phone_number
		if github_link == '':
			github_link = current_user.user_github_link


		if check_extension(file.filename) is False and file.filename != '':
			return 'Произошла ошибка, недопустимое расширение'

		if file.filename == '': 	# Если картинка не передана, соотвестсвенно ничего сохранять не нужно
			flag = False

		if flag:
			user_avatar_path = 'static/img/' + user + str(current_user.user_id) + file.filename
			filename = user + str(current_user.user_id) + file.filename 	
			current_user.user_avatar = filename

		current_user.user_first_name = first_name 		
		current_user.user_last_name = last_name 		
		current_user.user_nickname = nickname 			
		current_user.user_email = email 				# Запись данных в бд	
		current_user.user_description = description
		current_user.user_phone_number = phone_number
		current_user.user_github_link = github_link

		try:
			db.session.commit()
		except:
			return 'Произошла ошибка'

		if flag:
			file.save(user_avatar_path)		# Сохранение картинки 

		with open('users-key.txt', 'r', encoding='utf-8') as file:
			current_key = file.read() 	# Считывание текущего ключа

		return redirect(f'/home/{user}/{primary_key}={current_key}')

	elif request.method == 'GET':
		if check_key(key) is not True:
			return '404 NOT FOUND'

		table = Users.query.all()

		for i in table:		# Поиск текущего пользователя по его уникальному ключу
			if i.user_primary_key == primary_key:
				data = i
				break
		else:
			return 'User not found'
		
		with open('users-key.txt', 'r', encoding='utf-8') as file:
			current_key = file.read() 	# Считывание текущего ключа

		string = f'{current_key} {key}'.split()

		if data is not None and data.user_nickname == user and string[0] == string[1]:
			if data.user_first_name == "":
				data.user_first_name = 'No data'
			if data.user_last_name == "": 			# Установка значений по умолчанию
				data.user_last_name = 'No data'
			if data.user_description == "":
				data.user_description = 'No data'

			return render_template('profile/profilesetting.html', data=data, current_key=current_key)


@application.route('/user-friend-list=<string:primary_key>&<string:key>')
def friend_list(primary_key, key):
	with open('users-key.txt', 'r', encoding='utf-8') as file:
		current_key = file.read() 	# Считывание текущего ключа

	string = f'{current_key} {key}'.split()

	if string[0] == string[1]:
		table = Users.query.all()

		return render_template('friends-page.html', table=table)
	else:
		return '404 NOT FOUND'


@application.route('/send-invite&<string:user>-<string:primary_key>&<string:previous_user>-<string:previous_primary_key>')
def send_invite(user, primary_key, previous_user, previous_primary_key):
	table = Users.query.all()

	for i in table:		# Поиск текущего пользователя по его уникальному ключу
		if i.user_primary_key == primary_key:
			data = i
			break
	else:
		return 'User not found'

	for i in table:		# Поиск предыдущего пользователя по его уникальному ключу
		if i.user_primary_key == previous_primary_key:
			previous_data = i
			break
	else:
		return 'User not found'

	if data.user_incoming_invitations == 'empty':
		data.user_incoming_invitations = f'{previous_data.user_avatar}#{previous_user}#{previous_primary_key}'
	elif f'{previous_data.user_avatar}#{previous_user}#{previous_primary_key}' not in data.user_incoming_invitations:
		data.user_incoming_invitations += f' {previous_data.user_avatar}#{previous_user}#{previous_primary_key}'

	try:
		db.session.commit()
	except:
		return 'error'

	with open('users-key.txt', 'r', encoding='utf-8') as file:
		current_key = file.read()

	return redirect(f'/public-profile/{user}/{previous_primary_key}-{primary_key}={current_key}')


@application.route('/invite-list/<string:user>-<string:primary_key>=<string:key>')
def invite_list(user, primary_key, key):
	if check_key(key) is not True:
		return '404 NOT FOUND'

	table = Users.query.all()

	for i in table:		# Поиск текущего пользователя по его уникальному ключу
		if i.user_primary_key == primary_key:
			data = i
			break
	else:
		return 'User not found'

	invites_list = data.user_incoming_invitations.split() 	# split на каждое приглашение отдельно

	for i in range(len(invites_list)):
		invites_list[i] = invites_list[i].split('#') 

	return render_template('invite-list.html', invites_list=invites_list, primary_key=primary_key)


@application.route('/accept/<string:user>#<string:key>-<string:primary_key>')
def accept(user, key, primary_key):
	table = Users.query.all()

	for i in table:		# Поиск текущего пользователя по его уникальному ключу
		if i.user_primary_key == primary_key:
			data = i
			break
	else:
		return 'User not found'

	invites_list = data.user_incoming_invitations.split()

	for i in range(len(invites_list)):
		invites_list[i] = invites_list[i].split('#') 
		if invites_list[i][-1] == key:
			invites_list[i] == ''

	invites_list = " ".join(invites_list)

	#if data.user_friends_list == 'empty':
	#	data.user_friends_list = f'{avatar}#{user}#{key}'
	#	data.user_incoming_invitations = invites_list
	#else:
	#	data.user_friends_list += f' {avatar}#{user}#{key}'
	#	data.user_incoming_invitations = invites_list
#
	#try:
	#	db.session.commit()
	#except:
	#	return 'error'

	with open('users-key.txt', 'r', encoding='utf-8') as file:
		current_key = file.read() 	# Считывание текущего ключа

	return redirect(f'/invite-list/{data.user_nickname}-{data.user_primary_key}={current_key}')




if __name__ == '__main__':
	#github_api('ViLsonCake')
	#github_api('IsNAble')
	#generate_admin_key('secret-key.txt')
	#generate_users_key('users-key.txt')

	application.run(debug=True)
