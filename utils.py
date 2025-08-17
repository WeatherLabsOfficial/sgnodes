import random, string, json

def generate_vps_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def generate_ssh_credentials():
    user = ''.join(random.choices(string.ascii_lowercase, k=8))
    password = ''.join(random.choices(string.ascii_letters + string.digits + "*&^%$#@", k=12))
    return user, password

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

def load_data():
    with open('data.json', 'r') as f:
        return json.load(f)
