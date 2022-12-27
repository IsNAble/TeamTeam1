from email.mime.text import MIMEText
from email_validator import validate_email, EmailNotValidError
import smtplib
import os


def send_email(message: str, recipient: str, sender='teamsitechangepassw0rd@gmail.com'):
	try:
		valid = validate_email(recipient).email
	except EmailNotValidError:
		return 'Email invalid'

	with open('email-password.txt', 'r', encoding='utf-8') as file:
		password = file.read()

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()

	if valid:
		try:
			server.login(sender, password)

			msg = MIMEText(message)
			server.sendmail(sender, recipient, msg.as_string())

			return 'Success'
		except Exception as _ex:
			return _ex

