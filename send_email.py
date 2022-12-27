import smtplib
import os
from email.mime.text import MIMEText


def send_email(message: str, recipient: str, sender='teamsitechangepassw0rd@gmail.com'):
	with open('email-password.txt', 'r', encoding='utf-8') as file:
		password = file.read()

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()

	try:
		server.login(sender, password)

		msg = MIMEText(message)
		server.sendmail(sender, recipient, msg.as_string())

		return 'Сообщение отправленно!'
	except Exception as _ex:
		return _ex
