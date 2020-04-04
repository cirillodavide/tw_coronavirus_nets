from __future__ import division

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import pygraphviz

from networkx.drawing.nx_agraph import graphviz_layout


def plot_with_PageRank(G, output_file):

	weight = 'status_sentiment'
	
	pr = nx.pagerank(G, alpha=0.85, weight=weight)
	pr_df = pd.DataFrame(pr.items(), columns=['id', 'PR'])
	print("Top PageRank:")
	print(pr_df.sort_values(by='PR', ascending=False).head())

	fig = plt.figure(figsize=(18, 16), dpi= 80, facecolor='w', edgecolor='k')
	pos = graphviz_layout(G, prog="neato")
	edges, weights = zip(*nx.get_edge_attributes(G,weight).items())
	edge_labels = dict([((u, v,), G.get_edge_data(u, v)[weight]) for u, v in G.edges])

	node_sizes = []
	for node in G.nodes:
		node_sizes.append( pr_df[pr_df['id']==node]['PR'].values )
	node_sizes = [item for sublist in node_sizes for item in sublist]
	node_sizes = 10 + (node_sizes - min(node_sizes)) * (200 - 10) / (max(node_sizes) - min(node_sizes))

	nx.draw(G,
        pos,
        node_size=node_sizes,
        node_color='k',
        vmin=0.0,
        vmax=1.0,
        with_labels=False,
        edgelist=edges, edge_color=weights, width=4.0, edge_cmap=plt.cm.RdBu
	) # red = negative sentiment; blue = positive sentiment

	#nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

	plt.savefig(output_file)
