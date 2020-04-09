from __future__ import division

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import pygraphviz

from networkx.drawing.nx_agraph import graphviz_layout


def plot_graph(G, output_file):

	weight = 'status_sentiment'
	
	fig = plt.figure(figsize=(18, 16), dpi= 80, facecolor='w', edgecolor='k')
	pos = graphviz_layout(G, prog="neato")
	edges, weights = zip(*nx.get_edge_attributes(G,weight).items())
	edge_labels = dict([((u, v,), G.get_edge_data(u, v)[weight]) for u, v in G.edges])

	nx.draw(G,
        pos,
        node_size=15,
        node_color='k',
        vmin=0.0,
        vmax=1.0,
        with_labels=False,
        edgelist=edges, edge_color=weights, width=4.0, edge_cmap=plt.cm.RdBu
	) # red = negative sentiment; blue = positive sentiment

	#nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

	plt.savefig(output_file)
