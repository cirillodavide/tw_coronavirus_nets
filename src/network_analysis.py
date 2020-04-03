from utils.db_manager import DBManager
from utils.save_table import save_csv

import networkx as nx
import pandas as pd
import pathlib
import logging



class NetworkGenerator:
	__dbm_tweets = None

	def __init__(self, database=None, colletion=None, tw_type=None):
		if not None:
			self.__dbm_tweets = DBManager(database, colletion)

	def get_retweets(self):
		retweets = self.__dbm_tweets.get_retweets()
		file_loc = save_csv(retweets,'retweets')
		return(file_loc)

	def get_replies(self):
		replies = self.__dbm_tweets.get_replies()
		file_loc = save_csv(replies,'replies')
		return(file_loc)

	def get_quotes(self):
		quotes = self.__dbm_tweets.get_quotes()
		file_loc = save_csv(quotes,'quotes')
		return(file_loc)

	def get_items(self, tw_type):
		if tw_type == 'retweets':
			self.get_retweets()
		if tw_type == 'replies':
			self.get_replies()
		if tw_type == 'quotes':
			self.get_quotes()


class NetworkAnalyzer:
	__graph = None

	def __init__(self, graph=None):
		if not None:
			self.__graph = graph

	def read_graph(self):
		f_name = self.__graph
		df = pd.read_csv(f_name)
		G = nx.from_pandas_edgelist(df, source='id', target='in_reply_to_status_id', edge_attr='sentiment') 
		return(nx.info(G))