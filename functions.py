from random import sample, randrange
import requests
import json
import re


def found_user(database, primary_key):
	for i in database:
		if i.user_primary_key == primary_key:
			user = i
			break
	else:
		return 'User not found'

	return user


def check_password(password: str) -> bool:
	upper = False 		# Check uppercase
	lower = False 		# Check lowercase

	if len(password) > 8 and len(password) < 16:
		for i in password:
			if i.isupper():
				upper = True
			elif i.islower():
				lower = True

	return upper and lower


def check_extension(filename: str) -> bool: 	# Function to check valid file extensions
	extensions = ('jpg', 'jpeg', 'png')			#jpg jpeg png

	if '.' in filename:
		extension = filename.split('.')[-1].lower() 	# Getting the current extension (if it exists)
		return extension in extensions	
	else:
		return False


def check_key(key: str, filename='users-key.txt') -> bool:
	with open('keys/' + filename, 'r', encoding='utf-8') as file:
		current_key = file.read()

	string = f'{key} {current_key}'.split()

	return string[0] == string[1], current_key


def generate_primary_key():
	return str(randrange(1000, 10000))		# Four-digit key generation 


def generate_security_key():
	return str(randrange(100000, 1000000)) 	# Six-digit key generation


def generate_admin_key(filename: str, length=6) -> None:
	try:
		with open(filename, 'r', encoding='utf-8') as file:
			output = file.readlines()
			current_key = output[0]
			count = int(output[-1].split()[-1])

		if count % 10 == 0:
			count += 1
			lower_case = "qwertyuiopasdfghjklzzxcvbnm"
			upper_case = "QWERTYUIOPASDFGHJKLZXCVBNM"
			numbers = "0123456789"
			string = lower_case + upper_case + numbers
			current_key = ''.join(sample(string, length)) 	# Generating a new key every 10 server starts
		else:
			count += 1

		with open(filename, 'w', encoding='utf-8') as file:
			file.write(f'{current_key}\ncount: {count}') 	# Writing a new key

	except FileNotFoundError:
		return 'File not exists'


def generate_users_key(filename: str, length=8):
	try:
		lower_case = "qwertyuiopasdfghjklzzxcvbnm"
		upper_case = "QWERTYUIOPASDFGHJKLZXCVBNM"
		numbers = "0123456789"
		string = lower_case + upper_case + numbers
		current_key = ''.join(sample(string, length))

		with open(filename, 'w', encoding='utf-8') as file:
			file.write(current_key)

	except FileNotFoundError:
		return 'File not exists'


def github_api(nickname: str):
	if nickname == 'ViLsonCake':
		name_photo = 'ViLson.png'
	elif nickname == 'IsNAble':
		name_photo = 'Hwesus.png'
	else:
		name_photo = 'someone.png'

	url = f'https://api.github.com/users/{nickname}'

	response = requests.get(url) 	# Get request per user

	result = re.findall(r'avatar_url.*?,', response.text)[0] 	# Parsing url from request
	photo_url = result[13:-2]

	response_photo = requests.get(photo_url) 	# Get request by image url
	img = open(f'static/img/{name_photo}', 'wb')
	img.write(response_photo.content)			# Reading and writing a picture
	img.close()

