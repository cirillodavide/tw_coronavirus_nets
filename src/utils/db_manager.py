from pymongo import MongoClient, errors
from utils.get_config import get_config
from bson.json_util import loads

import pathlib
import pandas as pd
import random
import sys


class DBManager:
	__database = ''
	__collection = ''
	__db = ''
	__spain_db = ''

	def __init__(self, database, collection, where, json_file):

		if where == 'local':

			#local data
			json_file = json_file

			try:
				client = MongoClient('localhost', 27017)
				self.__db = client[database]

				#create a new collection if it does not exist in database
				if collection not in self.__db.list_collection_names():
					self.__collection = self.__db[collection]
					file_data = []
					for line in open(json_file, 'r'):
						file_data.append(loads(line))
					self.__collection.insert_many(file_data)
				
				# print the version of MongoDB server if connection successful
				print ("server version:", client.server_info()["version"])
			except errors.ServerSelectionTimeoutError as err:
				client = None
				print ("pymongo ERROR:", err)

			self.__database = database
			self.__collection = collection

		if where == 'remote':

			#connection configuration file
			json_file = json_file

			script_parent_dir = pathlib.Path(__file__).parents[1]
			config_fn = script_parent_dir.joinpath(json_file)
			config = get_config(config_fn)
			connection_dict = {
				'host': config['mongodb']['host'],
				'port': int(config['mongodb']['port']),
				'username': config['mongodb']['username'],
				'password': config['mongodb']['password']
			}
		
			self.__database = database
			self.__collection = collection

			uri = "mongodb://%s:%s@%s:%s/%s" % (
				connection_dict['username'],
				connection_dict['password'],
				connection_dict['host'],
				connection_dict['port'],
				database
				)
		
			try:
				client = MongoClient(uri, serverSelectionTimeoutMS = 3000) # 3 second timeout
				self.__db = client[self.__database]
				# print the version of MongoDB server if connection successful
				print ("server version:", client.server_info()["version"])
			except errors.ServerSelectionTimeoutError as err:
				client = None
				print ("pymongo ERROR:", err)

			#print('>>>')
			#db = self.__db
			#tweets = self.__collection
			#print(db.tweets.find({"$and": [{"lang": {"$in": ["es", "ca", "eu", "gl"]}}, {"$or": [{"place.country": "Spain"}, {"user.location": {"$in": ["espana","catalunya","spain","madrid","espanya"]}}]}]}).count())
			#print('<<<')

	def aggregate(self, pipeline, tw_type):
		lst = []
		c = 0
		for doc in self.__db[self.__collection].aggregate(pipeline, allowDiskUse=True):
			if c < 470000:
				sentiment = "{:.4f}".format(random.uniform(-2, 2))
				
				#retweeted_status will not appear if the tweet is not a retweet
				if tw_type != 'retweet':
					retweeted_status_id = None
					retweeted_user_id = None
				else:
					retweeted_status_id = doc['retweeted_status']['id']
					retweeted_user_id = doc['retweeted_status']['user']['id']
				
				#quoted_status_id will not appear if the tweet is not a quote
				if tw_type != 'quote':
					quoted_status_check = None
					quoted_status_id = None
					quoted_user_id = None
				else:
					quoted_status_id = doc['quoted_status_id']
					quoted_user_id = None
				
				L = [ tw_type,
					  doc['id'],
				  	  doc['user']['id'],
				  	  retweeted_status_id,
				  	  retweeted_user_id,
				  	  doc['in_reply_to_status_id'],
				  	  doc['in_reply_to_user_id'],
				  	  quoted_status_id,
				  	  quoted_user_id,
				  	  sentiment ]
				lst.append(L)
				c += 1
			else:
				break
		df = pd.DataFrame.from_records(lst)
		df.columns = [ 'status_type',
					   'status_id',
					   'user_id',
					   'retweeted_status_id',
					   'retweeted_user_id',
					   'in_reply_to_status_id',
					   'in_reply_to_user_id',
					   'quoted_status_id',
					   'quoted_user_id',
					   'status_sentiment' ]
		return(df)

	def __add_extra_filters(self, match, **kwargs):
		return(match)


	def get_retweets(self, **kwargs):
		match = {
			'retweeted_status': {'$exists': 1}, # it must be a retweet
			'in_reply_to_status_id_str': {'$eq': None}, # it must not be a reply
			'is_quote_status': False # it must not be a quote
		}
		match = self.__add_extra_filters(match, **kwargs)
		pipeline = [{'$match': match}]
		return(self.aggregate(pipeline, tw_type='retweet'))

	def get_replies(self, **kwargs):
		match = {
			'retweeted_status': {'$exists': 0}, # it must not be a retweet
			'in_reply_to_status_id_str': {'$ne': None}, # it must be a reply
			'is_quote_status': False # it must not be a quote
		}
		match = self.__add_extra_filters(match, **kwargs)
		pipeline = [{'$match': match}]
		return(self.aggregate(pipeline, tw_type='reply'))

	def get_quotes(self, **kwargs):
		match = {
			'is_quote_status': True, # it must be a quote
			'quoted_status_id': {'$exists': 1} # the quoted_status_id must exists
		}
		match = self.__add_extra_filters(match, **kwargs)
		pipeline = [{'$match': match}]
		return(self.aggregate(pipeline, tw_type='quote'))
