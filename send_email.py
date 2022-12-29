from email.mime.text import MIMEText
from email_validator import validate_email, EmailNotValidError
import smtplib
import os


def send_email(message: str, recipient: str, sender='teamsitechangepassw0rd@gmail.com', input_password=None):
	try:
		valid = validate_email(recipient).email 	# Check valid email
	except EmailNotValidError: 		# Case where the email is invalid
		return 'Email invalid'

	if input_password is None:
		with open('email-password.txt', 'r', encoding='utf-8') as file:
			password = file.read()
	else:
		password = input_password

	server = smtplib.SMTP('smtp.gmail.com', 587) 	# Start server
	server.starttls()

	try:
		server.login(sender, password) 		# Try to login 

		msg = MIMEText(message)
		server.sendmail(sender, recipient, msg.as_string()) 	# Send message

		return 'Success'
	except Exception as _ex:
		return _ex

