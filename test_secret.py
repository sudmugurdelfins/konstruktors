import os.path
import mysql.connector

from configparser import ConfigParser

print("----------")
print("Check if secret map exists")
assert os.path.isdir("/home/s138/my_secret_files/") == True
print("OK")
print("----------")
print("----------")
print("Check if secret file exists")
assert os.path.isfile("/home/s138/my_secret_files/config.ini") == True
print("OK")
print("----------")
print("----------")
print("Check if possible to connect to database")
try:
	config = ConfigParser()
	config.read('/home/s138/my_secret_files/config.ini')

	mysql_config_mysql_host = config.get('mysql_config', 'mysql_host')
	mysql_config_mysql_db = config.get('mysql_config', 'mysql_db')
	mysql_config_mysql_user = config.get('mysql_config', 'mysql_user')
	mysql_config_mysql_pass = config.get('mysql_config', 'mysql_pass')

except:
	print("")

connection = mysql.connector.connect(host=mysql_config_mysql_host, database=mysql_config_mysql_db, user=mysql_config_mysql_user, password=mysql_config_mysql_pass)
if connection.is_connected():
            print('Connected to database')

print("OK")
print("----------")
