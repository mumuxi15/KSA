from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from ksa_api.env import env
import pyodbc
import pandas as pd
import os, re, environ, datetime
import yaml
from .models import *
from .serializers import  *

today = datetime.datetime.now().date()
lateline = today - datetime.timedelta(days=21)
next_month = today.replace(day=28) + datetime.timedelta(days=4)
deadline = next_month - datetime.timedelta(days=next_month.day)

def load_queries(yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        queries = yaml.safe_load(file)
    return queries['sql_query']

def validate_supplr_id(supplr_id):
    # If supplr_id contains invalid characters, reject the request
    if re.match(r'^[A-Z][A-Z0-9]{0,9}', supplr_id):
        return supplr_id
    else:
        return None

# def get_shipment_from_dev(request):
#     try:
#         shipment = Shipment.objects.using('dev_db').all()
#         output = [{"supplier": u.supplr,
#                    "item": u.item       } for u in shipment]
#         return Response(output)
#
# def get_shipment_from_prod(request):
#     output = [{"supplier": u.supplr,
#                "item": u.item       } for u in Shipment.objects.all()]
#     return Response(output)



class SupplierView(APIView):
    serializer_class = SupplierSerializer
    def get(self,request):
        output = [{"supplier":output.SUPPLR,
                   "supplier_name":output.SUPPLR_NAME,
                   "email":output.EMAIL
                   } for output in Supplier.objects.all()]
        return Response(output)

    def post(self, request):
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

class ShipmentView(APIView):
    # pull data from database
    def get(self, request):
        environment = os.getenv('ENVIRONMENT')
        print('%%'*10,' CURRENT ENVIRONMENT = ',environment)
        if environment == 'DEV':
            output = Shipment.objects.all()
        elif environment == 'PROD':
            query = load_queries(os.path.join(os.path.dirname(__file__), '..', 'config', 'queries.yaml'))
            connection_string = os.getenv("PYODBC_CONNECTION_STRING")
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            cursor.execute(query['tracking'])
            rows = cursor.fetchall()
            output = []
            for row in rows:
                output.append({
                    "purord": row[0],
                    "supplr": row[1],
                    "item":   row[2],
                    # "ordqty": row[3],
                    # "outqty": row[5],
                    # "condat": row[6],
                    # "newdate": row[7],
                    # "type": row[8],
                    # "late": row[10],
                })
        return Response(output)


class TrackingView(APIView):
    # pull data from database
    def get(self, request):
        query = load_queries(os.path.join(os.path.dirname(__file__), '..', 'config', 'queries.yaml'))
        connection_string = os.getenv("PYODBC_CONNECTION_STRING")
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute(query['tracking'])
        rows = cursor.fetchall()

        # data filtering
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(rows, columns=columns)
        df['LATE'], df['ATTN'] = 0, 0
        df['CONDAT'] = pd.to_datetime(df['CONDAT'], errors='coerce').dt.date
        df['NEWCONDAT'] = pd.to_datetime(df['NEWCONDAT'], errors='coerce').dt.date
        df = df.loc[(df['CONDAT'] <= deadline)]
        df.loc[df['NEWCONDAT'] < lateline, 'ATTN'] = 1  # bring attention if late
        df.loc[df['NEWCONDAT'] < today, 'LATE'] = 1
        df.loc[(df['TYPE'] == 'C') & (df['ATTN'] == 1), 'Z_ITEMS'] = 1
        # df.loc[df['LATE'] == 1].sort_values(by=['SUPPLR', 'NEWCONDAT']).to_csv('late_orders.csv')
        df = df.groupby(['SUPPLR']).agg({'NEWCONDAT': 'min', 'LATE': 'sum', 'ATTN': 'max', 'Z_ITEMS': 'any'}
                                        ).sort_values(by=['SUPPLR'])
        df['Z_ITEMS'] = df['Z_ITEMS'].astype(int)
        output = df.reset_index().to_dict(orient='records')
        cursor.close()
        connection.close()
        return Response(output)

class TrackingSupplierView(APIView):
    def get(self, request, supplr_id):
        print('-' * 30, '\n', supplr_id)
        supplr_id = validate_supplr_id(supplr_id)
        print('+' * 30, '\n', supplr_id)

        query = load_queries(os.path.join(os.path.dirname(__file__), '..', 'config', 'queries.yaml'))
        connection_string = os.getenv("PYODBC_CONNECTION_STRING")
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute(query['tracking_by_id'].format(item_tuple=supplr_id))
        rows = cursor.fetchall()

        # data filtering
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(rows, columns=columns)
        if df.empty:
            return Response({'message': 'No records found for supplier ID ' + supplr_id}, status=404)
        output = df.reset_index().to_dict(orient='records')
        return Response(output)


    def post(self, request):
        supplr_id = request.POST.get('supplr_id')
        print ('-'*30,'\n',supplr_id)
        query = load_queries(os.path.join(os.path.dirname(__file__), '..', 'config', 'queries.yaml'))
        connection_string = os.getenv("PYODBC_CONNECTION_STRING")
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute(query['tracking_by_id'].format(item_tuple=supplr_id))
        rows = cursor.fetchall()

        # data filtering
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(rows, columns=columns)
        df['LATE'], df['ATTN'] = 0, 0
        df['CONDAT'] = pd.to_datetime(df['CONDAT'], errors='coerce').dt.date
        df['NEWCONDAT'] = pd.to_datetime(df['NEWCONDAT'], errors='coerce').dt.date
        df = df.loc[(df['CONDAT'] <= deadline)]
        df.loc[df['NEWCONDAT'] < lateline, 'ATTN'] = 1  # bring attention if late
        df.loc[df['NEWCONDAT'] < today, 'LATE'] = 1
        df.loc[(df['TYPE'] == 'C') & (df['ATTN'] == 1), 'Z_ITEMS'] = 1
        df['Z_ITEMS'] = df['Z_ITEMS'].astype(int)
        output = df.reset_index().to_dict(orient='records')
        cursor.close()
        connection.close()
        return Response(output)




