import pandas as pd
from sqlalchemy import create_engine
import yaml
import supabase as supa
from ksa_api.config import SUPABASE_URL, SUPABASE_KEY

##################################
## DEV MODE: connect to cloud database service
##################################
def connect_supabase():
    client: supa.Client = supa.create_client(SUPABASE_URL, SUPABASE_KEY)
    response = (
        client.table("shipping").select("*").execute()
    )
    df = pd.DataFrame(response.data)
    return df


##################################
## KEEP ALL QUERY IN A config/queries.yaml file
##################################

def load_queries(yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        queries = yaml.safe_load(file)
    return queries['sql_query']

def query_search(target, item_tuple=None):
    engine = create_engine(DB_STRING)
    qry = load_queries(SQL_YAML_PATH)
    if target not in qry:
        raise NameError("YAML FILE DOES NOT CONTAIN SUCH QUERY NAME")
    else:
        if item_tuple:
            sql = qry[target].format(item_tuple=item_tuple)
        else:
            sql = qry[target]
        return pd.read_sql(sql, engine)

def query_direct(query):
    engine = create_engine(DB_STRING)
    return pd.read_sql(query, engine)
