from pymongo import MongoClient, errors
from utils.get_config import get_config
from utils.utils_spain import SPAIN_LANGUAGES, get_spain_places_regex
from bson.json_util import loads, dumps
from tqdm import tqdm

import pathlib
import pandas as pd
import random
import sys
import json


class DBManager:
	__database = ''
	__collection = ''
	__db = ''
	__query = ''

	def __init__(self, database, collection, where, json_file, export):

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

			
			if export == 'yes':

				export_path = '../sna/data/es-tweets.hpai.json'

				self.__query = {'$and': [{'lang': {'$in': SPAIN_LANGUAGES}},
								{'$or': [{'place.country': 'Spain'}, 
								 	{'user.location': {'$in': \
										get_spain_places_regex()}}]}]}

				print ("Exporting cursor...")
				cursor = self.search(self.__query)
				file = open(export_path, "w")
				for document in tqdm(cursor, total=470000):
					file.write(dumps(document))
					file.write("\n")
				sys.exit("Bye!")

	def search(self, query):
		return self.__db[self.__collection].find(self.__query, no_cursor_timeout=True)


	def aggregate(self, pipeline, tw_type):
		lst = []
		for doc in self.__db[self.__collection].aggregate(pipeline, allowDiskUse=True):

			try:
				sentiment = doc['sentiment']['score']
			except:
				sentiment = None
				
			#retweeted_status will not appear if the tweet is not a retweet
			if tw_type != 'retweet':
				retweeted_status_id = None
				retweeted_user_id = None
			else:
				retweeted_status_id = doc['retweeted_status']['id']
				retweeted_user_id = doc['retweeted_status']['user']['screen_name']
				
			#quoted_status_id will not appear if the tweet is not a quote
			if tw_type != 'quote':
				quoted_status_check = None
				quoted_status_id = None
				quoted_user_id = None
			else:
				quoted_status_id = doc['quoted_status_id']
				try:
					quoted_user_id = doc['quoted_status']['user']['screen_name']
				except:
					quoted_user_id = None
				
			L = [ tw_type,
				  doc['id'],
			  	  doc['user']['screen_name'],
			  	  doc['created_at'],
			  	  retweeted_status_id,
			  	  retweeted_user_id,
			  	  doc['in_reply_to_status_id'],
			  	  doc['in_reply_to_screen_name'],
			  	  quoted_status_id,
			  	  quoted_user_id,
			  	  sentiment ]
			lst.append(L)

		df = pd.DataFrame.from_records(lst)
		df.columns = [ 'status_type',
					   'status_id',
					   'user_screen_name',
					   'created_at',
					   'retweeted_status_id',
					   'retweeted_user_screen_name',
					   'in_reply_to_status_id',
					   'in_reply_to_user_screen_name',
					   'quoted_status_id',
					   'quoted_user_screen_name',
					   'status_sentiment' ]
		return(df)

	def __add_extra_filters(self, match, **kwargs):
		return(match)

	#filters
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

	def get_text(self, **kwargs):
		match = {}
		match = self.__add_extra_filters(match, **kwargs)
		pipeline = [{'$match': match}]
		
		lst = []
		for doc in self.__db[self.__collection].aggregate(pipeline, allowDiskUse=True):

			try:
				sentiment = doc['sentiment']['score']
			except:
				sentiment = None

			L = [ doc['id'],
				  doc['user']['screen_name'],
				  doc['created_at'],
				  sentiment,
				  doc['text'] ]

			lst.append(L)

		df = pd.DataFrame.from_records(lst)
		df.columns = [ 'status_id',
					   'user_screen_name',
					   'date',
					   'sentiment',
					   'text' ]
		return(df)


	def get_stats(self, **kwargs):
		match = {}
		match = self.__add_extra_filters(match, **kwargs)
		pipeline = [{'$match': match}]

		lst = []
		for doc in self.__db[self.__collection].aggregate(pipeline, allowDiskUse=True):

			try:
				sentiment = doc['sentiment']['score']
			except:
				sentiment = None

			try:
				mentions = doc['entities']['user_mentions']['id']
			except:
				mentions = None

			L = [ doc['id'],
				  doc['user']['screen_name'],
				  doc['user']['followers_count'],
				  doc['user']['friends_count'],
				  doc['user']['favourites_count'],
				  doc['reply_count'],
				  doc['retweet_count'],
				  doc['quote_count'],
				  sentiment,
				  mentions ]
			lst.append(L)

		df = pd.DataFrame.from_records(lst)
		df.columns = [ 'status_id',
					   'user_screen_name',
					   'followers_count',
					   'friends_count',
					   'favorites_count',
					   'reply_count',
					   'retweet_count',
					   'quote_count',
					   'sentiment',
					   'mentions' ]
		return(df)


