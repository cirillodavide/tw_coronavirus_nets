from utils.db_manager import DBManager
from utils.save_table import save_csv

import networkx as nx
import pandas as pd
import pathlib
import logging



class NetworkGenerator:
	__dbm_tweets = None

	def __init__(self, database=None, colletion=None):
		if not None:
			self.__dbm_tweets = DBManager(database, colletion)

	def get_replies(self):
		replies = self.__dbm_tweets.get_replies()
		file_loc = save_csv(replies,'replies')
		return(file_loc)



class NetworkAnalyzer:
	__graph = None

	def __init__(self, graph=None):
		if not None:
			self.__graph = graph

	def read_graph(self):
		f_name = self.__graph
		#G = nx.read_gexf(f_name)
		df = pd.read_csv(f_name)
		G = nx.from_pandas_edgelist(df, source='id', target='in_reply_to_status_id', edge_attr='sentiment') 
		return(nx.info(G))