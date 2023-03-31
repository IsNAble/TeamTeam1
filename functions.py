from random import sample, randrange
import requests
import json
import re

def find_by_username(table, username: str):
	for i in table:
		if i.user_nickname == username:
			return i
	else:
		return False

def find_by_email(table, email: str):
	for i in table:
		if i.user_email == email:
			return i
	else:
		return False

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


def generate_primary_key():
	return str(randrange(1000, 10000))		# Four-digit key generation 


def generate_security_key():
	return str(randrange(100000, 1000000)) 	# Six-digit key generation


def to_seconds(days: int) -> int:
	return days * 24 * 60 * 60

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

