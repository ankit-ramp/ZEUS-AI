import requests
import json
import pandas as pd
import numpy as np
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import logging
logging.basicConfig(filename="dataverse.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


class Dataverse_read:
    def __init__(self):
        load_dotenv()
        self.dataverse_id = None
        self.dataverse = None
        self.tables = None
        self.table_ids = None
        self.table_names = None
        self.table_readers = None
        self.table_readers_dict = None  
        self.read_url = f"{os.getenv("Read_Url")}"

    def get_token(self):
        token_url = f"{os.getenv('Token_Url')}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
        "grant_type": "client_credentials",
       
        "client_id": f"{os.getenv('Client_ID')}",
        
        "scope": f"{os.getenv('Scope')}",
        
        "client_secret" : f"{os.getenv('Client_Secret')}",
       
    }
        logging.debug(f"printing the payload : {payload}")
        response = requests.get(token_url, data=payload, headers=headers)
        return response.json()['access_token']
    #global_token = get_token()

 

    def read_dataverse(self , table):
        token= self.get_token()
        headers = {'Content-Type': 'application/json; charset=utf-8'
                   ,'OData-MaxVersion': '4.0'
                   ,'OData-Version': '4.0'
                   ,'Authorization': f'{token}'
                   ,'Cache-Control': 'no-cache'
                  ,'Prefer': 'return=representation'
                  }
        
        response = requests.get(f'{self.read_url}{table}', headers=headers)
        
        
        try:
            if len(response.json()['value']) > 0:
                
                response = {"code" : 200, "message" : "Data found in dataverse table" , "data" : response.json()['value']}
                return response
            else:
                response = {"code" : 404, "message" : "Data not found in dataverse table" , "data" : response.json()['value']}
                return response
        except Exception as e:
            response = {"code" : 500, "message" : "Data not found in dataverse table" , "data" : response.json()}
            return response

    def read_dataverse_withfilter(self , dataversetbl,filtercolumn,filtervalue):
        token= self.get_token()
        url = f"{self.read_url}{dataversetbl}?$filter={filtercolumn} eq '{filtervalue}'"
        print(url)
        headers = {'Content-Type': 'application/json; charset=utf-8'
                   ,'OData-MaxVersion': '4.0'
                   ,'OData-Version': '4.0'
                   ,'Authorization': f'{token}'
                   ,'Cache-Control': 'no-cache'
                  ,'Prefer': 'return=representation'
                  }
        response = requests.get(url, headers=headers)
        logging.debug(f"printing the response of read_dataverse_withfilter : {response.text}")
        try:
            if len(response.json()['value']) > 0:
                
                response = {"code" : 200, "message" : "Data found in dataverse table" , "data" : response.json()['value']}
                return response
            else:
                response = {"code" : 404, "message" : "Data not found in dataverse table" , "data" : response.json()['value']}
                return response
        except Exception as e:
            response = {"code" : 500, "message" : "Data not found in dataverse table" , "data" : response.json()}
            return response

    def update_dataverse_data(self, table, guid, update_data ):
        token= self.get_token()
        
        patch_url = f"{self.read_url}{table}({guid})"
        logging.debug(f"inside the data opreation file update_dataverse_data method the patch url : {patch_url}")
        headers = {'Content-Type': 'application/json; charset=utf-8'
                   ,'OData-MaxVersion': '4.0'
                   ,'OData-Version': '4.0'
                   ,'Authorization': f'{token}'
                   ,'Cache-Control': 'no-cache'
                  ,'Prefer': 'return=representation'
                  }
        logging.debug(f" the update data : {update_data}")
        response = requests.patch(patch_url, headers=headers, json=update_data)
        
        if response.status_code == 200:
            response = {"code" : 200, "message" : "Data updated sucessfully" , "data" : response.json()}
            return response
        else:
            response = {"code" : 404, "message" : "Data not updated in dataverse table" , "data" : response.json()}
            return response
        


    def insert_records_into_dataverse(self, table, data):
        token= self.get_token()
        logging.debug(f"inside the data_opreation insert record function: {data}")
        headers = {'Content-Type': 'application/json; charset=utf-8'
                   ,'OData-MaxVersion': '4.0'
                   ,'OData-Version': '4.0'
                   ,'Authorization': f'{token}'
                   ,'Cache-Control': 'no-cache'
                  ,'Prefer': 'return=representation'
                  }
        
        post_url = f"{self.read_url}{table}"
        logging.debug(f" the post url : {post_url}")
        response = requests.post(post_url, headers=headers, json=data)
        logging.debug(f" the response of insert : {response.text}")
        if response.status_code == 201:
            
            response = {"code" : 200, "message" : "Data inserted sucessfully" , "data" : response.json()}
            return response
        else:
            
            response = {"code" : 404, "message" : "Data not inserted in dataverse table" , "data" : response.json()}
            return response
        
  
