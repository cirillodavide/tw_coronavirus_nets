# Network representation and anlysis of Twitter coversations on COVID19

usage:

## generate a graph
python run.py generate-graph --database <database_name> --collection <collection_name> --tw_type <retweets|replies|quotes>

## analyze a graph
python run.py analyze-graph --graph ../sna/graphs/<edgelist_table>
