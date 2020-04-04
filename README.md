# Network representation and anlysis of Twitter coversations on COVID19

usage:

## generate a graph

python run.py generate-graph --database <database_name> --collection <collection_name> --where local --json_file <data_file> --tw_type <retweets|replies|quotes>

python run.py generate-graph --database <database_name> --collection <collection_name> --where remote --json_file <config_file> --tw_type <retweets|replies|quotes> --export yes

## analyze a graph

python run.py analyze-graph --graph <edgelist_file>
