import mysql.connector
import base64
import pickle
import os
from dotenv import load_dotenv

load_dotenv()

mysql_host = os.getenv('MYSQL_HOST')
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_database = os.getenv("MYSQL_DATABASE")
mysql_port = int(os.getenv("MYSQL_PORT"))

# mysql_host = 'localhost'
# mysql_user = 'root'
# mysql_password = ''
# mysql_database = 'voca-tech-challenge'
# mysql_port = 3306

def connect_to_database():
    conn = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database,
        port=mysql_port
    )
    cursor = conn.cursor()
    return conn, cursor

class User:
    def __init__(self, user_id, username, password):
        self.user_id = user_id
        self.username = username
        self.password = password

def b64encodeUser(user):
    serialized_user = pickle.dumps(user)
    return base64.b64encode(serialized_user).decode('utf-8')

def b64decodeUser(s):
    serialized_user = base64.b64decode(s.encode('utf-8'))
    return pickle.loads(serialized_user)
