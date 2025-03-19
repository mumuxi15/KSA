from django.core.management.base import BaseCommand
from django.conf import settings
import os, re, environ, datetime
import pyodbc
from shipping.models import Shipment

env = environ.Env()
environ.Env.read_env(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

def load_queries(yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        queries = yaml.safe_load(file)
    return queries['sql_query']

class Command(BaseCommand):
    help = 'Delete data from local database'


    def handle(self, *args, **options):
        print('this is a delete command ')
        # Shipment.objects.create(
        #     "purord": row[0],
        # "supplr": row[1],
        # "item": row[2],
        # "ordqty": row[3],
        # "outqty": row[5],
        # "condat": row[6],
        # "newdate": row[7],
        # "type": row[8],
        # "late": row[10],
        # )
        # Iterate over the DataFrame and save data to the local database
        # for index, row in df.iterrows():
        #     YourModel.objects.create(
        #         field1=row['column1'],  # Replace with your actual fields
        #         field2=row['column2'],
        #         # Add more fields as needed
        #     )
        #
        self.stdout.write(self.style.SUCCESS('Data pulled and stored successfully'))

