from functions import generate_primary_key
from datetime import datetime
import telebot
from telebot import types
import sqlite3
import keyboard
import colorama


def set_values_in_db(nickname: str, email: str, password: str, repeat_password: str, primary_key: str, avatar='Circle_Davys-Grey_Solid.svg.png') -> int:
	with sqlite3.connect('database.db') as connect:
		cursor = connect.cursor()

		db_request = f"""INSERT INTO users
			(user_nickname, user_email, user_password, user_repeat_password,
			user_description, user_avatar, user_first_name, user_last_name, 
			user_phone_number, user_github_link, user_primary_key, 
			user_incoming_invitations, user_sent_invitations, user_friends_list, date)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

		clear = ""
		empty = 'empty'
		date = datetime.utcnow()

		data_tuple = (nickname, email, password, repeat_password, clear, avatar, 
					clear, clear, clear, clear, primary_key, empty, empty, empty, date)


		cursor.execute(db_request, data_tuple)
		connect.commit()

		return 1 	# Function worked

	return 0 	# Error


def get_values_from_db():
	with sqlite3.connect('database.db') as connect:
		cursor = connect.cursor()

		cursor.execute("SELECT user_nickname, user_email, user_primary_key FROM users")

		data = cursor.fetchall()

		output, nicknames, emails, keys = [], [], [], []

		for i in data:
			nicknames.append(i[0])
			emails.append(i[1])
			keys.append(i[2])

		output.append(nicknames)
		output.append(emails)
		output.append(keys)

		return output

	return 'Error'


def main():
	colorama.init()

	with open('keys/token.txt') as file:
		token = file.read()

	bot = telebot.TeleBot(token)
	print(colorama.Fore.YELLOW, 'Press Ctrl + C to quit')

	def stop_bot():
		bot.polling(none_stop=False)

	keyboard.add_hotkey('Ctrl + C', stop_bot)

	main.sign_flag = False
	main.login_flag = False
	main.nickname_flag = False
	main.email_flag = False
	main.password_flag = False
	main.repeatpassword_flag = False
	main.flag = False

	main.user_data = []


	@bot.message_handler(commands=['start'])
	@bot.message_handler(commands=['info'])
	def buttons(message):
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		button1 = types.KeyboardButton('Log-in')
		button2 = types.KeyboardButton('Sign-up')

		markup.add(button1, button2)
		bot.send_message(message.chat.id, text='Text', reply_markup=markup)


	@bot.message_handler(content_types=['text'])
	def send_text(message):
		markup = types.InlineKeyboardMarkup(row_width=1)
		exit_button = types.InlineKeyboardButton('Exit', callback_data='exit')
		markup.add(exit_button)

		db_data = get_values_from_db()

		if message.text == 'Sign-up' and not main.login_flag:
			main.sign_flag = True
			main.nickname_flag = True

			bot.send_message(message.chat.id, text='Enter your nickname', reply_markup=markup)
		elif main.nickname_flag:
			user_nickname = message.text
			main.nickname = user_nickname

			for i in db_data[0]:
				if i.lower() == user_nickname.lower():
					bot.send_message(message.chat.id, f'Nickname {user_nickname} already used', reply_markup=markup)
					return

			main.user_data.append(user_nickname)

			main.nickname_flag = False
			main.email_flag = True

			bot.send_message(message.chat.id, f'Your nickname is {user_nickname}', reply_markup=markup)
		elif main.email_flag:
			user_email = message.text
			main.email = user_email

			for i in db_data[1]:
				if i.lower() == user_email.lower():
					bot.send_message(message.chat.id, f'Email {user_email} already used', reply_markup=markup)
					return

			main.user_data.append(user_email)

			main.email_flag = False
			main.password_flag = True

			bot.send_message(message.chat.id, f'Your email is {user_email}', reply_markup=markup)
		elif main.password_flag:
			user_password = message.text
			main.password = user_password

			main.user_data.append(user_password)

			main.password_flag = False
			main.repeatpassword_flag = True

			bot.send_message(message.chat.id, f'Your password is {user_password}', reply_markup=markup)
		elif main.repeatpassword_flag:
			user_repeat_password = message.text
			main.repeat_password = user_repeat_password

			if user_repeat_password != main.password:
				bot.send_message(message.chat.id, "Passwords don't equals", reply_markup=markup)
				return

			main.user_data.append(user_repeat_password)

			main.nickname_flag = False
			main.email_flag = False
			main.password_flag = False
			main.repeatpassword_flag = False
			main.flag = True

			bot.send_message(message.chat.id, f'Your repeat password is {user_repeat_password}', reply_markup=markup)

		if main.flag:
			primary_key = generate_primary_key()

			while primary_key in db_data[2]:
				primary_key = generate_primary_key()

			main.user_data.append(primary_key)

			response = set_values_in_db(main.user_data[0], main.user_data[1], main.user_data[2], main.user_data[3], main.user_data[4])

			if response:
				bot.send_message(message.chat.id, f'You have successfully registered!\nYour primary_key is {primary_key}')
			else:
				bot.send_message(message.chat.id, 'Error db')

		if message.text == 'Log-in' and not main.sign_flag:
			pass


	@bot.callback_query_handler(func=lambda call: True)
	def callback(call):
		if call.message:
			if call.data == 'exit':
				main.nickname_flag = False
				main.email_flag = False
				main.password_flag = False
				main.repeatpassword_flag = False
				main.nickname = ""
				main.email = ""
				main.password = ""
				main.repeat_password = ""
				bot.send_message(call.message.chat.id, 'Exit')


	bot.polling(none_stop=True)




if __name__ == '__main__':
	main()
	#print(get_value_from_db())
	