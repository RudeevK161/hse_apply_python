import json
import os


def save_user_data(user_id, data, data_file='data/user_data.json'):
    os.makedirs(os.path.dirname(data_file), exist_ok=True)
    try:
        with open(data_file, 'r') as file:
            users = json.load(file)
    except FileNotFoundError:
        users = {}

    users[str(user_id)] = data

    with open(data_file, 'w') as file:
        json.dump(users, file, indent=4)


def load_user_data(user_id, data_file='data/user_data.json'):
    try:
        with open(data_file, 'r') as file:
            users = json.load(file)
            return users.get(str(user_id), None)
    except FileNotFoundError:
        return None