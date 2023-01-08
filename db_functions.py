import sqlite3


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

			output, nicknames, emails, keys = [], [], [], []

			for i in data:
				nicknames.append(i[0])
				emails.append(i[1])
				keys.append(i[2])

			output.append(nicknames)
			output.append(emails)
			output.append(keys)

			return output

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