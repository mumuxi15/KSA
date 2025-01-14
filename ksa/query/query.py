import os, environ
import pandas as pd
from sqlalchemy import create_engine
import yaml

env = environ.Env()
env.read_env(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))
environ.Env.read_env()

def load_queries(yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        queries = yaml.safe_load(file)
    return queries['sql_query']

def query_search(target, item_tuple=None):
    connection_string = env("KSA_DB_STRING")
    engine = create_engine(connection_string)
    qry = load_queries(os.path.join(os.path.dirname(__file__), '..', 'config', 'queries.yaml'))
    if target not in qry:
        raise NameError("YAML FILE DOES NOT CONTAIN SUCH QUERY NAME")
    else:
        if item_tuple:
            sql = qry[target].format(item_tuple=item_tuple)
        else:
            sql = qry[target]
        return pd.read_sql(sql, engine)

def query_direct(query):
    connection_string = env("KSA_DB_STRING")
    engine = create_engine(connection_string)
    return pd.read_sql(query, engine)


