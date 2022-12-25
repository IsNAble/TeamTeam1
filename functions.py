from random import sample, randrange
import requests
import json
import re


def check_password(password: str) -> bool:
	upper = False 		# Проверка верхнего регистра
	lower = False 		# Проверка нижнего регистра

	if len(password) > 8 and len(password) < 16:
		for i in password:
			if i.isupper():
				upper = True
			elif i.islower():
				lower = True

	return upper and lower


def check_extension(filename: str) -> bool: 	# Функция для проверки допустимых расширений у файла
	extensions = ('jpg', 'jpeg', 'png')			#jpg jpeg png

	if '.' in filename:
		extension = filename.split('.')[-1].lower() 	# Получение текущего расширения (если оно существует)
		return extension in extensions	
	else:
		return False


def check_key(key: str, filename='users-key.txt') -> bool:
	with open(filename, 'r', encoding='utf-8') as file:
		current_key = file.read()

	string = f'{key} {current_key}'.split()

	return string[0] == string[1], current_key


def generate_primary_key():
	return str(randrange(1000, 10000))		# Генерация четырехзначного ключа 


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
			current_key = ''.join(sample(string, length)) 	# Генерация нового ключа каждые 10 запусков сервера
		else:
			count += 1

		with open(filename, 'w', encoding='utf-8') as file:
			file.write(f'{current_key}\ncount: {count}') 	# Запись нового ключа 

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

	response = requests.get(url) 	# Get запрос на пользователя

	result = re.findall(r'avatar_url.*?,', response.text)[0] 	# Парсинг url из запроса
	photo_url = result[13:-2]

	response_photo = requests.get(photo_url) 	# Get запрос по url картинки
	img = open(f'static/img/{name_photo}', 'wb')
	img.write(response_photo.content)			# Считывание и запись картинки
	img.close()


if __name__ == '__main__':
	pass