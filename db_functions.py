import sqlite3


def create_db_for_bot():
	with sqlite3.connect('telegram_user.db') as connect:
		cursor = connect.cursor()

		cursor.execute("""CREATE TABLE IF NOT EXISTS Login_data
						(Telegram_username TEXT DEFAULT '', Last_logged_user_key TEXT DEFAULT '')""")

		print('Success, db is created!')


def set_values_in_telegram_db(username: str, primary_key: str) -> None:
	with sqlite3.connect('telegram_user.db') as connect:
		cursor = connect.cursor()

		data_tuple = (username, primary_key)

		cursor.execute("""INSERT INTO Login_data 
						(Telegram_username, Last_logged_user_key)
						VALUES (?, ?);""", data_tuple)


def update_values_in_telegram_db(username: str, primary_key) -> None:
	with sqlite3.connect('telegram_user.db') as connect:
		cursor = connect.cursor()

		data_tuple = (primary_key, username)

		cursor.execute("""UPDATE Login_data SET Last_logged_user_key = ? WHERE Telegram_username = ?""", data_tuple)


def get_values_in_telegram_db() -> list:
	with sqlite3.connect('telegram_user.db') as connect:
		cursor = connect.cursor()

		cursor.execute("""SELECT * FROM Login_data""")

		data = cursor.fetchall()

		usernames, keys = [], []

		for i in data:
			usernames.append(i[0])
			keys.append(i[1])

		return usernames, keys


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


def get_values_from_db(mode='partial'):
	with sqlite3.connect('database.db') as connect:
		cursor = connect.cursor()

		if mode == 'partial':
			cursor.execute("SELECT user_nickname, user_email, user_primary_key FROM users")

			data = cursor.fetchall()

			nicknames, emails, keys = [], [], []

			for i in data:
				nicknames.append(i[0])
				emails.append(i[1])
				keys.append(i[2])

			return nicknames, emails, keys

		elif mode == 'full':
			cursor.execute("""SELECT user_nickname, user_email, user_password, user_first_name, user_last_name,
							user_description, user_avatar, user_phone_number, user_id, user_primary_key FROM users""")

			data = cursor.fetchall()

			return data


def update_values_in_db(element, value, primary_key) -> int:
    with sqlite3.connect('database.db') as connect:
        cursor = connect.cursor()

        values_tuple = (value, primary_key)

        cursor.execute(f"UPDATE users SET {element} = ? WHERE user_primary_key = ?", values_tuple)

        return 1