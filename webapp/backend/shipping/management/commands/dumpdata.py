from django.core.management.base import BaseCommand
from django.conf import settings
import os, re
import pyodbc, yaml
import pandas as pd
from ksa_api.env import env
from shipping.models import Shipment

def load_queries(yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        queries = yaml.safe_load(file)
    return queries['sql_query']


class Command(BaseCommand):
    help = 'Pull data from external database and store it locally'
    def handle(self, *args, **options):
        environment = env('DJANGO_SETTINGS_MODULE')
        print('%%' * 10, ' CURRENT ENVIRONMENT = ', environment,'%%' * 10)
        if environment == 'ksa_api.settings.local':
            query = load_queries(os.path.join(settings.BASE_DIR, 'config', 'queries.yaml'))
            connection_string = env("PYODBC_CONNECTION_STRING")
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            cursor.execute(query['tracking'])
            rows = cursor.fetchall()
            #### empty table before dump data to shipment
            # Shipment.objects.all().delete()
            for row in rows:
                rowid = row[0]+row[2]
                Shipment.objects.update_or_create(
                    purord=row[0],
                    supplr=row[1],
                    item  =row[2],
                    ordqty=row[3],
                    outqty = row[5],
                    condat = row[6],
                    newdate= row[7],
                    type   = row[8],
                    late   = row[10],
                )
        self.stdout.write(self.style.SUCCESS('Dump data to local django database successfully'))

