from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functions import check_password, github_api


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
	date = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<Users %r>' % self.id


@application.route('/')
@application.route('/home')
def main_page():
	github_api('ViLsonCake')
	github_api('IsNAble')
	return render_template('index.html')


@application.route('/login', methods=['POST', 'GET'])
def login_page():
	if request.method == 'POST':
		user_login = request.form['login']
		user_password = request.form['pass']
		inputs = []
		inputs.append(user_login)
		inputs.append(user_password)

		if all(inputs) is False:
			alert = 'Поля не могут быть пустыми'
			return render_template('log-in.html', alert=alert)


		table = Users.query.all()

		for i in table:
			if (i.user_nickname == user_login or i.user_email == user_login) and i.user_password == user_password:
				return redirect(f'/home/{i.user_nickname}/{i.user_id}')

		alert = 'Неправильный логин или пароль'
		return render_template('log-in.html', alert=alert)

	else:
		alert = ""
		return render_template('log-in.html', alert=alert)


@application.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
	if request.method == 'POST':
		user_email = request.form['email']
		user_password = request.form['password']
		user_repeat_password = request.form['repeatpassword']
		user_nickname = request.form['nickname']
		inputs = []
		result = ['', '', '']
		inputs.append(user_email)
		inputs.append(user_password)
		inputs.append(user_repeat_password)
		inputs.append(user_nickname)

		if all(inputs) is False:
			result[0] = 'Поля не могут быть пустыми'
			return render_template('sign-up.html', result=result) 

		list_nicknames, list_emails = [], []

		table = Users.query.all()

		for i in table:
			list_nicknames.append(i.user_nickname)
			list_emails.append(i.user_email)

		info_nickname = f'Никнейм {user_nickname} занят'
		info_email = f'Почта {user_email} уже зарегистрирована'
		info_password = 'Пароли не совпадают'

		if user_nickname in list_nicknames:
			result[0] = info_nickname
		if user_email in list_emails:
			result[1] = info_email
		if user_password != user_repeat_password:
			result[2] = info_password

		if result != ['', '', '']:
			return render_template('sign-up.html', result=result)
		else:
			users = Users(
				user_nickname=user_nickname,
				user_email=user_email,
				user_password=user_password,
				user_repeat_password=user_repeat_password
				)

			try:
				db.session.add(users)
				db.session.commit()
				return redirect('/home')
			except:
				return 'error'

	else:
		result = ['', '', '']
		return render_template('sign-up.html', result=result)


@application.route('/users', methods=['POST', 'GET'])
def users_list():
	if request.method == 'POST':
		pass
	else:
		table = Users.query.all()

		return render_template('admin.html', table=table)


@application.route('/home/<string:user>/<int:user_id>')
def user(user, user_id):
	nickname = user
	return render_template('homelogin.html', nickname=nickname)


@application.route('/profile/<string:user>/<user_id>', methods=['POST', 'GET'])
def profile(user, user_id):
	if request.method == 'POST':
		pass
	else:
		table = Users.query.all()
		return render_template('profile.html', table=table)




if __name__ == '__main__':
	application.run(debug=True)