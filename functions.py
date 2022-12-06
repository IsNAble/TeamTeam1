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


def github_api(nickname: str):
	if nickname == 'ViLsonCake':
		name_photo = 'ViLson.png'
	elif nickname == 'IsNAble':
		name_photo = 'Hwesus.png'

	url = f'https://api.github.com/users/{nickname}'

	response = requests.get(url)

	result = re.findall(r'avatar_url.*?,', response.text)[0]
	photo_url = result[13:-2]

	response_photo = requests.get(photo_url)
	img = open(f'static/img/{name_photo}', 'wb')
	img.write(response_photo.content)
	img.close()


if __name__ == '__main__':
	print(github_api('IsNAble'))