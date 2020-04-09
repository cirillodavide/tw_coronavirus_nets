from utils.db_manager import DBManager
from utils.save_table import save_csv
from utils.plot_graph import plot_graph

import networkx as nx
import pandas as pd
import pathlib
import logging



class NetworkGenerator:
	__dbm_tweets = None
	__database = ''
	__collection = ''

	def __init__(self, database=None, collection=None, where=None, json_file=None, export=None):
		if not None:
			self.__dbm_tweets = DBManager(database, collection, where, json_file, export)

		self.__database = database
		self.__collection = collection


	def get_stats(self):
		stats = self.__dbm_tweets.get_stats()
		file_loc = save_csv(stats,'stats', self.__database, self.__collection)
		return(file_loc)

	def get_retweets(self):
		retweets = self.__dbm_tweets.get_retweets()
		file_loc = save_csv(retweets,'retweets', self.__database, self.__collection)
		return(file_loc)

	def get_replies(self):
		replies = self.__dbm_tweets.get_replies()
		file_loc = save_csv(replies,'replies', self.__database, self.__collection)
		return(file_loc)

	def get_quotes(self):
		quotes = self.__dbm_tweets.get_quotes()
		file_loc = save_csv(quotes,'quotes', self.__database, self.__collection)
		return(file_loc)

	def get_text(self):
		text = self.__dbm_tweets.get_text()
		file_loc = save_csv(text,'text', self.__database, self.__collection)
		return(file_loc)

	def get_items(self, tw_type):
		if tw_type == 'retweets':
			self.get_retweets()
		if tw_type == 'replies':
			self.get_replies()
		if tw_type == 'quotes':
			self.get_quotes()
		if tw_type == 'stats':
			self.get_stats()
		if tw_type == 'text':
			self.get_text()


class NetworkAnalyzer:
	__graph = None

	def __init__(self, graph=None):
		if not None:
			self.__graph = graph

	def read_graph(self):
		f_name = self.__graph
		df = pd.read_csv(f_name,sep='\t')
		
		if df['status_type'].unique() == 'retweet':
			target = 'retweeted_status_id'

		if df['status_type'].unique() == 'reply':
			target='in_reply_to_status_id' 
		
		if df['status_type'].unique() == 'quote':
			target='quoted_status_id'

		G = nx.from_pandas_edgelist(df, source='status_id', target=target, edge_attr='status_sentiment', create_using=nx.DiGraph())

		print(nx.info(G))
		print('')

		print('Number of strongly connected components:',nx.number_strongly_connected_components(G))
		print('Largest strongly connected component:')
		G_strong = max(nx.strongly_connected_component_subgraphs(G), key=len)
		print(nx.info(G_strong))
		print('')
		
		print('Number of weakly connected components:',nx.number_weakly_connected_components(G))
		print('Largest weakly connected component:')
		G_weakly = max(nx.weakly_connected_component_subgraphs(G), key=len)
		print(nx.info(G_weakly))
		print('')

		#level of influence by user
		plot_graph(G, output_file=f_name+'.png')

		return()



