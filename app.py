from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


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
	date = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<Users %r>' % self.id


@application.route('/')
@application.route('/home')
def main_page():
	return render_template('index.html')


@application.route('/login')
def login_page():
	return render_template('log-in.html')


@application.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
	if request.method == 'POST':
		user_email = request.form['email']
		user_password = request.form['password']
		user_repeat_password = request.form['repeatpassword']
		user_nickname = request.form['nickname']

		list_nicknames, list_emails = [], []

		table = Users.query.all()

		for i in table:
			list_nicknames.append(i.user_nickname)
			list_emails.append(i.user_email)

		if user_nickname in list_nicknames:
			info_nickname = f'Никнейм {user_nickname} занят'
			return render_template('sign-up.html', info_nickname=info_nickname)
		if user_email in list_emails:
			info_email = f'Почта {user_email} уже зарегистрирована'
			return render_template()

		if user_password == user_repeat_password:
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
			return 'error'

	else:
		return render_template('sign-up.html')




if __name__ == '__main__':
	application.run(debug=True)