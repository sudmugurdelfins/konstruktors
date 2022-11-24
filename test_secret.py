import os.path
import mysql.connector
import yaml
import logging
import logging.config
import tweepy
import tweepy.errors

from configparser import ConfigParser

# Loading logging configuration
with open('./log_worker.yaml', 'r') as stream:
   log_config = yaml.safe_load(stream)

logging.config.dictConfig(log_config)
# Creating logger
logger = logging.getLogger('root')
logger.info('Asteroid processing service')

# Initiating and reading config values
logger.info('Loading configuration from file')


logger.info("----------")
logger.info("Check if secret map exists")
assert os.path.isdir("/home/s138/my_secret_files/") == True
logger.info("OK")
logger.info("----------")
logger.info("----------")
logger.info("Check if secret file exists")
assert os.path.isfile("/home/s138/my_secret_files/config.ini") == True
logger.info("OK")
logger.info("----------")
logger.info("----------")
logger.info("Check if possible to connect to database")
try:
	config = ConfigParser()
	config.read('/home/s138/my_secret_files/config.ini')

	mysql_config_mysql_host = config.get('mysql_config', 'mysql_host')
	mysql_config_mysql_db = config.get('mysql_config', 'mysql_db')
	mysql_config_mysql_user = config.get('mysql_config', 'mysql_user')
	mysql_config_mysql_pass = config.get('mysql_config', 'mysql_pass')

except:
	logger.exception("")

connection = mysql.connector.connect(host=mysql_config_mysql_host, database=mysql_config_mysql_db, user=mysql_config_mysql_user, password=mysql_config_mysql_pass)
if connection.is_connected():
            logger.info('Connected to database')

logger.info("OK")
logger.info("----------")
logger.info("----------")
logger.info("Check if twitter data exist")
assert config.has_option('twitter', 'api_key')  == True
assert config.has_option('twitter', 'api_secret')  == True
assert config.has_option('twitter', 'access_token')  == True
assert config.has_option('twitter', 'access_token_secret')  == True
logger.info("OK")
logger.info("----------")
logger.info("----------")
logger.info("Check if twitter data is valid")
twitter_api_key = config.get('twitter', 'api_key')
twitter_api_secret = config.get('twitter', 'api_secret')
twitter_access_token = config.get('twitter', 'access_token')
twitter_access_token_secret = config.get('twitter', 'access_token_secret')

auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
auth.set_access_token(twitter_access_token, twitter_access_token_secret)

api = tweepy.API(auth)
try:
	user = api.verify_credentials()
except tweepy.errors.Forbidden:
	logger.info('Twitter is connected!')
except:
	logger.error('Twitter didnt connect!')
logger.info("OK")
logger.info("----------")