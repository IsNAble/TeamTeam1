from random import sample
import requests
import json
import re


def check_password(password: str) -> bool:
	upper = False
	lower = False

	if len(password) > 8 and len(password) < 16:
		for i in password:
			if i.isupper():
				upper = True
			elif i.islower():
				lower = True

	return upper and lower


def check_extension(filename: str) -> bool:
	extensions = ('jpg', 'jpeg', 'png')

	if '.' in filename:
		extension = filename.split('.')[-1].lower()
		return extension in extensions	
	else:
		return False


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
			current_key = ''.join(sample(string, length))
		else:
			count += 1

		with open(filename, 'w', encoding='utf-8') as file:
			file.write(f'{current_key}\ncount: {count}')

	except FileNotFoundError:
		return 'Файла не существует'


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
		return 'Файла не существует'


def github_api(nickname: str):
	if nickname == 'ViLsonCake':
		name_photo = 'ViLson.png'
	elif nickname == 'IsNAble':
		name_photo = 'Hwesus.png'
	else:
		name_photo = 'someone.png'

	url = f'https://api.github.com/users/{nickname}'

	response = requests.get(url)

	result = re.findall(r'avatar_url.*?,', response.text)[0]
	photo_url = result[13:-2]

	response_photo = requests.get(photo_url)
	img = open(f'static/img/{name_photo}', 'wb')
	img.write(response_photo.content)
	img.close()


if __name__ == '__main__':
	pass