from functions import generate_primary_key
from db_functions import set_values_in_db, get_values_from_db, update_values_in_db, set_values_in_telegram_db, get_values_from_telegram_db, update_values_in_telegram_db
from datetime import datetime
from telebot import types
import telebot
import keyboard
import colorama


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
	main.full_login_flag = False

	main.login_nick_flag = False
	main.login_password_flag = False
	main.change_names_flag = False
	main.change_nickname_flag = False
	main.change_email_flag = False
	main.change_phone_flag = False
	main.change_description_flag = False
	main.change_avatar_flag = False

	main.user_data = []
	main.user_login_data = []


	@bot.message_handler(commands=['start'])
	def buttons(message):
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		button1 = types.KeyboardButton('Log-in')
		button2 = types.KeyboardButton('Sign-up')

		markup.add(button1, button2)
		bot.send_message(message.chat.id, text='Text', reply_markup=markup)


	@bot.message_handler(commands=['change'])
	def change_settings(message):
		info_markup = types.InlineKeyboardMarkup(row_width=2)
		edit_names = types.InlineKeyboardButton('Edit names', callback_data='edit_names')
		edit_nickname = types.InlineKeyboardButton('Edit nickname', callback_data='edit_nickname')
		edit_email = types.InlineKeyboardButton('Edit email', callback_data='edit_email')
		edit_phone = types.InlineKeyboardButton('Edit phone number', callback_data='edit_phone')
		edit_description = types.InlineKeyboardButton('Edit description', callback_data='edit_description')
		edit_avatar = types.InlineKeyboardButton('Edit avatar', callback_data='edit_avatar')
		info_markup.add(edit_names, edit_nickname, edit_email, edit_phone, edit_description, edit_avatar)

		bot.send_message(message.chat.id, text='What do you want to edit?', reply_markup=info_markup)


	@bot.message_handler(commands=['out'])
	def sign_out(message):
		usernames, keys = get_values_from_telegram_db()

		if message.from_user.username not in usernames:
			bot.send_message(message.chat.id, 'You are not logged')
			return

		update_values_in_telegram_db(message.from_user.username, 'out')


	# Sign-up and log-in
	@bot.message_handler(content_types=['text'])
	def send_text(message):
		markup = types.InlineKeyboardMarkup(row_width=1)
		exit_button = types.InlineKeyboardButton('Exit', callback_data='exit')
		markup.add(exit_button)

		info_markup = types.InlineKeyboardMarkup(row_width=1)
		info_button = types.InlineKeyboardButton('Add more information', callback_data='add_info')
		info_markup.add(info_button)

		db_data = get_values_from_db()

		data = get_values_from_telegram_db()

		for i in range(len(data[0])):
			if data[0][i] == message.from_user.username:
				current_user_key = data[1][i]
				break
		else:
			current_user_key = 'out'

		# Sign-up case
		if message.text == 'Sign-up' and not main.login_flag:
			main.sign_flag = True
			main.nickname_flag = True

			bot.send_message(message.chat.id, text='Enter your nickname', reply_markup=markup)
		# Added nickname
		elif main.nickname_flag:
			user_nickname = message.text.strip()
			main.nickname = user_nickname

			for i in db_data[0]:
				if i.lower() == user_nickname.lower():
					bot.send_message(message.chat.id, f'Nickname {user_nickname} already used', reply_markup=markup)
					return

			main.user_data.append(user_nickname)

			main.nickname_flag = False
			main.email_flag = True

			bot.send_message(message.chat.id, text='Enter your email', reply_markup=markup)
		# Added email
		elif main.email_flag:
			user_email = message.text.strip()
			main.email = user_email

			for i in db_data[1]:
				if i.lower() == user_email.lower():
					bot.send_message(message.chat.id, f'Email {user_email} already used', reply_markup=markup)
					return

			main.user_data.append(user_email)

			main.email_flag = False
			main.password_flag = True

			bot.send_message(message.chat.id, text='Enter your password', reply_markup=markup)
		# Added password
		elif main.password_flag:
			user_password = message.text.strip()
			main.password = user_password

			main.user_data.append(user_password)

			main.password_flag = False
			main.repeatpassword_flag = True

			bot.send_message(message.chat.id, text='Repeat password', reply_markup=markup)
		# Added repeat password
		elif main.repeatpassword_flag:
			user_repeat_password = message.text.strip()
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

		# Added primary key and save data in sqlite
		if main.flag:
			primary_key = generate_primary_key()

			while primary_key in db_data[2]:
				primary_key = generate_primary_key()

			main.user_data.append(primary_key)

			response = set_values_in_db(main.user_data[0], main.user_data[1], main.user_data[2], main.user_data[3], main.user_data[4])

			if response:
				bot.send_message(message.chat.id, f'You have successfully registered!\nYour primary_key is {primary_key}', reply_markup=info_markup)
			else:
				bot.send_message(message.chat.id, 'Error db')

			data = get_values_from_db(mode='full')

			data_tuple = get_values_from_telegram_db()
			# Save last logged user data
			if message.from_user.username in data_tuple[0]:
				update_values_in_telegram_db(message.from_user.username, primary_key)
			else:
				set_values_in_telegram_db(message.from_user.username, primary_key)

			main.flag = False
			main.sign_flag = False

		# Log-in case
		if message.text == 'Log-in' and not main.sign_flag:
			main.login_flag = True
			main.login_nick_flag = True
			bot.send_message(message.chat.id, 'Enter your nickname', reply_markup=markup)
		# Enter nickname for login
		elif main.login_nick_flag:
			user_nickname = message.text.strip()
			main.user_login_data.append(user_nickname)
			main.login_nick_flag = False
			main.login_password_flag = True
			bot.send_message(message.chat.id, 'Enter your password "||your password||"')
		# Enter password for login
		elif main.login_password_flag:
			user_password = message.text.strip()

			main.user_login_data.append(user_password)

			main.login_password_flag = False
			main.full_login_flag = True
		# Check data
		if main.full_login_flag:
			data = get_values_from_db(mode='full')

			for i in data:
				if i[0] == main.user_login_data[0] and i[2] == main.user_login_data[1]:
					current_user = i
					break
			else:
				bot.send_message(message.chat.id, 'Wrong login or password!')

			main.login_flag = False
			main.full_login_flag = False
			main.current_logged_user_key = current_user[-1] 	# Index -1 it's always primary key

			data_tuple = get_values_from_telegram_db()

			if message.from_user.username in data_tuple[0]:
				update_values_in_telegram_db(message.from_user.username, current_user[-1])
			else:
				set_values_in_telegram_db(message.from_user.username, current_user[-1])

			bot.send_message(message.chat.id, text=f'You are logged, {current_user[0]}', reply_markup=info_markup)


		# Change something
		# ---------------
		# Change first name and last name
		if main.change_names_flag:
			new_names = message.text.split()

			if len(new_names) != 2:
				bot.send_message(message.chat.id, text='Wrong input, repeat please', reply_markup=markup)
				return

			if current_user_key == 'out':
				bot.send_message(message.chat.id, text='You are not logged!')
				return

			update_values_in_db('user_first_name', new_names[0], current_user_key)
			update_values_in_db('user_last_name', new_names[1], current_user_key)

			main.change_names_flag = False

			bot.send_message(message.chat.id, text=f'Your first name is {new_names[0]}, last name is {new_names[1]}')
		# Change nickname
		elif main.change_nickname_flag:
			new_nickname = message.text.strip()

			if current_user_key == 'out':
				bot.send_message(message.chat.id, text='You are not logged!')
				return

			update_values_in_db('user_nickname', new_nickname, current_user_key)

			main.change_nickname_flag = False

			bot.send_message(message.chat.id, text=f'Success, your new nickname is {new_nickname}')
		# Change email
		elif main.change_email_flag:
			new_email = message.text.strip()

			if current_user_key == 'out':
				bot.send_message(message.chat.id, text='You are not logged!')
				return

			update_values_in_db('user_email', new_email, current_user_key)

			main.change_email_flag = False

			bot.send_message(message.chat.id, text=f'Success, your new email is {new_email}')
		# Change phone number
		elif main.change_phone_flag:
			new_phone_number = message.text.strip()

			if current_user_key == 'out':
				bot.send_message(message.chat.id, text='You are not logged!')
				return

			update_values_in_db('user_phone_number', new_phone_number, current_user_key)

			main.change_phone_flag = False

			bot.send_message(message.chat.id, text=f'Success, your new phone number is {new_phone_number}')
		# Change description
		elif main.change_description_flag:
			new_description = message.text.strip()

			if current_user_key == 'out':
				bot.send_message(message.chat.id, text='You are not logged!')
				return

			update_values_in_db('user_description', new_description, current_user_key)

			main.change_description_flag = False

			bot.send_message(message.chat.id, text=f'Success, your new description is {new_description}')


	@bot.message_handler(content_types=['photo'])
	def change_avatar(message):
		if main.change_avatar_flag:
			# Searching user data
			data = get_values_from_db('full')

			tg_data = get_values_from_telegram_db()

			for i in range(len(tg_data[0])):
				if tg_data[0][i] == message.from_user.username:
					current_user_key = tg_data[1][i]
					break
			else:
				current_user_key = 'out'

			if current_user_key == 'out':
				bot.send_message(message.chat.id, text='You are not logged!')
				return

			for i in data:
				if i[-1] == current_user_key:
					current_user = i
					break
			else:
				bot.send_message(message.chat.id, 'User not found')
			# Get photo info
			file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
			downloaded_file = bot.download_file(file_info.file_path)
			# Save photo
			with open(f'static/img/{current_user[0]}{current_user[-2]}{file_info.file_path[7:]}', 'wb') as img:
				img.write(downloaded_file)

			update_values_in_db('user_avatar', f'{current_user[0]}{current_user[-2]}{file_info.file_path[7:]}', current_user_key)

			bot.send_message(message.chat.id, 'Success, you change your avatar')


	@bot.callback_query_handler(func=lambda call: True)
	def callback(call):
		if call.message:
			tg_data = get_values_from_telegram_db()

			for i in range(len(tg_data[0])):
				if tg_data[0][i] == call.message.from_user.username:
					current_user_key = tg_data[1][i]
					break
			else:
				current_user_key = 'out'

			if current_user_key == 'out':
				bot.send_message(call.message.chat.id, text='You are not logged!')
				return

			markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
			button1 = types.KeyboardButton('Log-in')
			button2 = types.KeyboardButton('Sign-up')
			markup.add(button1, button2)

			# Exit from all
			if call.data == 'exit':
				# Sign-up flags
				main.nickname_flag = False
				main.email_flag = False
				main.password_flag = False
				main.repeatpassword_flag = False
				main.flag = False
				main.user_data = []

				# Log-in flags
				main.login_nick_flag = False
				main.login_password_flag = False
				main.full_login_flag = False
				main.user_login_data = []

				# Change data
				main.login_nick_flag = False
				main.login_password_flag = False
				main.change_names_flag = False
				main.change_nickname_flag = False
				main.change_email_flag = False
				main.change_phone_flag = False
				main.change_description_flag = False
				main.change_avatar_flag = False

				bot.send_message(call.message.chat.id, 'Exit')
			# Add information
			if call.data == 'add_info':
				info_markup = types.InlineKeyboardMarkup(row_width=2)
				edit_names = types.InlineKeyboardButton('Edit names', callback_data='edit_names')
				edit_nickname = types.InlineKeyboardButton('Edit nickname', callback_data='edit_nickname')
				edit_email = types.InlineKeyboardButton('Edit email', callback_data='edit_email')
				edit_phone = types.InlineKeyboardButton('Edit phone number', callback_data='edit_phone')
				edit_description = types.InlineKeyboardButton('Edit description', callback_data='edit_description')
				edit_avatar = types.InlineKeyboardButton('Edit avatar', callback_data='edit_avatar')
				info_markup.add(edit_names, edit_nickname, edit_email, edit_phone, edit_description, edit_avatar)

				bot.send_message(call.message.chat.id, text='What do you want to edit?', reply_markup=info_markup)
			# Change names
			if call.data == 'edit_names':
				main.change_names_flag = True
				bot.send_message(call.message.chat.id, text='Enter your first name and last name separated by a space', reply_markup=markup)
			# Change nickname
			if call.data == 'edit_nickname':
				main.change_nickname_flag = True
				bot.send_message(call.message.chat.id, text='Enter your new nickname', reply_markup=markup)
			# Change email
			if call.data == 'edit_email':
				main.change_email_flag = True
				bot.send_message(call.message.chat.id, text='Enter your new email', reply_markup=markup)
			# Change phone number
			if call.data == 'edit_phone':
				main.change_phone_flag = True
				bot.send_message(call.message.chat.id, text='Enter your new phone number', reply_markup=markup)
			# Change description
			if call.data == 'edit_description':
				main.change_description_flag = True
				bot.send_message(call.message.chat.id, text='Enter your new description', reply_markup=markup)
			# Change avatar
			if call.data == 'edit_avatar':
				main.change_avatar_flag = True
				bot.send_message(call.message.chat.id, text='Send your new avatar', reply_markup=markup)


	bot.polling(none_stop=True)




if __name__ == '__main__':
	main()
	