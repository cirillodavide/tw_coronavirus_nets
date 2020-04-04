import click
import logging
import os
import pathlib
import sys


from network_analysis import NetworkAnalyzer, NetworkGenerator

# Add the directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(filename=str(pathlib.Path(__file__).parents[0].joinpath('logs/tw_coronavirus.log')),
                    level=logging.DEBUG)

def check_current_directory():
    cd_name = os.path.basename(os.getcwd())
    if cd_name != 'src':
        click.UsageError('Illegal use: This script must run from the src directory')


@click.group()
def run():
    pass


@run.command()
@click.option('--database', default='covid-un', help='MongoDB database to query.')
@click.option('--collection', default='bsc-ls', help='MongoDB collection to query.')
@click.option('--where', default='remote', help='Local or remote database connection.')
@click.option('--json_file', default='../sna/config/config.json', help='Local or remote database connection.')
@click.option('--tw_type', default='retweets', help='Type of tweets (retweets, replies, quotes).')
@click.option('--export', default='no', help='Export filtered collection.')

def generate_graph(database, collection, where, json_file, tw_type, export):
    """
    Generate a graph by querying a MongoDB collection
    """
    check_current_directory()
    print('Generating the network...')
    na = NetworkGenerator(database, collection, where, json_file, export)

    file_loc = na.get_items(tw_type)

    print('Process has finished, results were stored in'+str(file_loc))


@run.command()
@click.option('--graph', default='../sna/graphs/replies_040120.csv', help='Path to graph gexf file.')

def analyze_graph(graph):
    """
    Analyze a given graph of interactions
    """
    check_current_directory()
    print('Analyzing the network...')
    na = NetworkAnalyzer(graph)
    _ = na.read_graph()
    print('Process has finished, results were stored in...')

if __name__ == "__main__":
	run()