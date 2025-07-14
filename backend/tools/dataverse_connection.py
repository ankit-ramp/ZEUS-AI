import requests
import json
import pandas as pd
import numpy as np
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from fastapi.responses import JSONResponse
from dotenv import load_dotenv # Import load_dotenv
import logging

# Load environment variables at the top of the file
load_dotenv()

# --- Configure dataverse_logger ---
logger_dataverse = logging.getLogger("dataverse_logger") # Get the specific named logger
handler_dataverse = logging.FileHandler("dataverse.log")
formatter_dataverse = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler_dataverse.setFormatter(formatter_dataverse)
logger_dataverse.addHandler(handler_dataverse)
logger_dataverse.setLevel(logging.DEBUG)
logger_dataverse.propagate = False # Prevent messages from going to the root logger


class Dataverse_read:
    def __init__(self):
        # No need to call load_dotenv() again here, it's done at the module level

        self.dataverse_id = None
        self.dataverse = None
        self.tables = None
        self.table_ids = None
        self.table_names = None
        self.table_readers = None
        self.table_readers_dict = None  
        self.read_url = os.getenv("Read_Url") # Use os.getenv directly

        logger_dataverse.debug("Dataverse_read instance initialized.")
        if not self.read_url:
            logger_dataverse.error("Read_Url environment variable is not set.")

    def get_token(self):
        token_url = os.getenv('Token_Url')
        client_id = os.getenv('Client_ID')
        scope = os.getenv('Scope')
        client_secret = os.getenv('Client_Secret')

        if not all([token_url, client_id, scope, client_secret]):
            logger_dataverse.error("Missing environment variables for token retrieval.")
            raise ValueError("Missing environment variables for token retrieval.")

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "scope": scope,
            "client_secret" : client_secret,
        }
        logger_dataverse.debug(f"Payload for token request (excluding client_secret): { {k:v for k,v in payload.items() if k!='client_secret'} }") # Log payload safely
        
        try:
            response = requests.post(token_url, data=payload, headers=headers) # Changed to POST as it's typically a POST request for OAuth tokens
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            token_data = response.json()
            if 'access_token' in token_data:
                logger_dataverse.debug("Token retrieved successfully.")
                return token_data['access_token']
            else:
                logger_dataverse.error(f"Access token not found in response: {token_data}")
                raise ValueError("Access token not found in response.")
        except requests.exceptions.RequestException as e:
            logger_dataverse.error(f"Error getting token from {token_url}: {e}")
            raise # Re-raise the exception after logging if the token is critical
        except json.JSONDecodeError as e:
            logger_dataverse.error(f"JSON decode error from token response: {response.text}. Error: {e}")
            raise ValueError("Invalid JSON response from token endpoint.")


    def read_dataverse(self, table_with_query):
        try:
            token = self.get_token()
        except (ValueError, requests.exceptions.RequestException) as e:
            logger_dataverse.error(f"Failed to get token for reading dataverse: {e}")
            return {"code": 500, "message": "Failed to authenticate for Dataverse read", "data": str(e)}

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0',
            'Authorization': f'Bearer {token}',
            'Cache-Control': 'no-cache',
            'Prefer': 'return=representation'
        }

        url = f'{self.read_url}{table_with_query}'  # Accept query in parameter
        logger_dataverse.debug(f"Attempting to read from Dataverse URL: {url}")

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response_json = response.json()

            if 'value' in response_json and len(response_json['value']) > 0:
                logger_dataverse.info(f"Data found in Dataverse table '{table_with_query}'. Count: {len(response_json['value'])}")
                return {"code": 200, "message": "Data found in dataverse table", "data": response_json['value']}
            else:
                logger_dataverse.warning(f"No data found in Dataverse table '{table_with_query}'. Response: {response_json}")
                return {"code": 404, "message": "Data not found in dataverse table", "data": response_json.get('value', [])}
        except requests.exceptions.HTTPError as e:
            logger_dataverse.error(f"HTTP Error reading Dataverse table '{table_with_query}': {e.response.status_code} - {e.response.text}")
            return {"code": e.response.status_code, "message": f"HTTP Error: {e.response.status_code}", "data": e.response.text}
        except json.JSONDecodeError as e:
            logger_dataverse.error(f"JSON decode error when reading Dataverse table '{table_with_query}'. Response text: {response.text}. Error: {e}")
            return {"code": 500, "message": "Invalid JSON response from Dataverse", "data": response.text}
        except Exception as e:
            logger_dataverse.error(f"Unexpected error reading Dataverse table '{table_with_query}': {e}. Response text: {response.text if 'response' in locals() else 'N/A'}")
            return {"code": 500, "message": "Error processing Dataverse response", "data": str(e)}

    def read_dataverse_withfilter(self , dataversetbl,filtercolumn,filtervalue):
        try:
            token= self.get_token()
        except (ValueError, requests.exceptions.RequestException) as e:
            logger_dataverse.error(f"Failed to get token for reading dataverse with filter: {e}")
            return {"code" : 500, "message" : "Failed to authenticate for Dataverse read with filter" , "data" : str(e)}

        url = f"{self.read_url}{dataversetbl}?$filter={filtercolumn} eq '{filtervalue}'"
        # print(url) # Avoid print statements if logging is enabled
        logger_dataverse.debug(f"Attempting to read from Dataverse with filter URL: {url}")
        headers = {'Content-Type': 'application/json; charset=utf-8'
                   ,'OData-MaxVersion': '4.0'
                   ,'OData-Version': '4.0'
                   ,'Authorization': f'Bearer {token}' # Added Bearer prefix
                   ,'Cache-Control': 'no-cache'
                   ,'Prefer': 'return=representation'
                  }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status() # Raise an HTTPError for bad responses
            logger_dataverse.debug(f"Response from read_dataverse_withfilter: {response.text}")
            response_json = response.json()
            
            if 'value' in response_json and len(response_json['value']) > 0:
                logger_dataverse.info(f"Data found in Dataverse table '{dataversetbl}' with filter '{filtercolumn}'='{filtervalue}'. Count: {len(response_json['value'])}")
                return {"code" : 200, "message" : "Data found in dataverse table" , "data" : response_json['value']}
            else:
                logger_dataverse.warning(f"No data found in Dataverse table '{dataversetbl}' with filter '{filtercolumn}'='{filtervalue}'. Response: {response_json}")
                return {"code" : 404, "message" : "Data not found in dataverse table" , "data" : response_json.get('value', [])}
        except requests.exceptions.HTTPError as e:
            logger_dataverse.error(f"HTTP Error reading Dataverse table '{dataversetbl}' with filter: {e.response.status_code} - {e.response.text}")
            return {"code" : e.response.status_code, "message" : f"HTTP Error: {e.response.status_code}", "data" : e.response.text}
        except json.JSONDecodeError as e:
            logger_dataverse.error(f"JSON decode error when reading Dataverse table '{dataversetbl}' with filter. Response text: {response.text}. Error: {e}")
            return {"code" : 500, "message" : "Invalid JSON response from Dataverse" , "data" : response.text}
        except Exception as e:
            logger_dataverse.error(f"An unexpected error occurred while reading Dataverse table '{dataversetbl}' with filter. Error: {e}. Response text: {response.text if 'response' in locals() else 'N/A'}")
            return {"code" : 500, "message" : "Error processing Dataverse response" , "data" : str(e)}

    def update_dataverse_data(self, table, guid, update_data ):
        try:
            token= self.get_token()
        except (ValueError, requests.exceptions.RequestException) as e:
            logger_dataverse.error(f"Failed to get token for updating dataverse: {e}")
            return {"code" : 500, "message" : "Failed to authenticate for Dataverse update" , "data" : str(e)}
        
        patch_url = f"{self.read_url}{table}({guid})"
        logger_dataverse.debug(f"Attempting to update Dataverse data. Patch URL: {patch_url}")
        headers = {'Content-Type': 'application/json; charset=utf-8'
                   ,'OData-MaxVersion': '4.0'
                   ,'OData-Version': '4.0'
                   ,'Authorization': f'Bearer {token}' # Added Bearer prefix
                   ,'Cache-Control': 'no-cache'
                   ,'Prefer': 'return=representation'
                  }
        logger_dataverse.debug(f"Update data payload: {update_data}")
        
        try:
            response = requests.patch(patch_url, headers=headers, json=update_data)
            response.raise_for_status() # Raise an HTTPError for bad responses
            
            logger_dataverse.info(f"Data updated successfully for {table} with GUID {guid}.")
            return {"code" : 200, "message" : "Data updated sucessfully" , "data" : response.json()}
        except requests.exceptions.HTTPError as e:
            logger_dataverse.error(f"HTTP Error updating Dataverse table '{table}' with GUID '{guid}': {e.response.status_code} - {e.response.text}")
            return {"code" : e.response.status_code, "message" : f"HTTP Error: {e.response.status_code}", "data" : e.response.text}
        except json.JSONDecodeError as e:
            logger_dataverse.error(f"JSON decode error from update response for '{table}' with GUID '{guid}'. Response text: {response.text}. Error: {e}")
            return {"code" : 500, "message" : "Invalid JSON response from Dataverse update" , "data" : response.text}
        except Exception as e:
            logger_dataverse.error(f"An unexpected error occurred while updating Dataverse table '{table}' with GUID '{guid}'. Error: {e}. Response text: {response.text if 'response' in locals() else 'N/A'}")
            return {"code" : 500, "message" : "Error processing Dataverse update response" , "data" : str(e)}

    def insert_records_into_dataverse(self, table, data):
        try:
            token= self.get_token()
        except (ValueError, requests.exceptions.RequestException) as e:
            logger_dataverse.error(f"Failed to get token for inserting into dataverse: {e}")
            return {"code" : 500, "message" : "Failed to authenticate for Dataverse insert" , "data" : str(e)}

        logger_dataverse.debug(f"Attempting to insert record into Dataverse table '{table}'. Data: {data}")
        headers = {'Content-Type': 'application/json; charset=utf-8'
                   ,'OData-MaxVersion': '4.0'
                   ,'OData-Version': '4.0'
                   ,'Authorization': f'Bearer {token}' # Added Bearer prefix
                   ,'Cache-Control': 'no-cache'
                   ,'Prefer': 'return=representation'
                  }
        
        post_url = f"{self.read_url}{table}"
        logger_dataverse.debug(f"Post URL for insert: {post_url}")
        
        try:
            response = requests.post(post_url, headers=headers, json=data)
            response.raise_for_status() # Raise an HTTPError for bad responses
            logger_dataverse.debug(f"Response from insert: {response.text}")
            
            if response.status_code == 201:
                logger_dataverse.info(f"Data inserted successfully into Dataverse table '{table}'.")
                return {"code" : 200, "message" : "Data inserted sucessfully" , "data" : response.json()}
            else:
                # This block might not be reached if raise_for_status() already caught it
                logger_dataverse.warning(f"Data not inserted into Dataverse table '{table}'. Status: {response.status_code}, Response: {response.text}")
                return {"code" : 404, "message" : "Data not inserted in dataverse table" , "data" : response.json()}
        except requests.exceptions.HTTPError as e:
            logger_dataverse.error(f"HTTP Error inserting into Dataverse table '{table}': {e.response.status_code} - {e.response.text}")
            return {"code" : e.response.status_code, "message" : f"HTTP Error: {e.response.status_code}", "data" : e.response.text}
        except json.JSONDecodeError as e:
            logger_dataverse.error(f"JSON decode error from insert response for '{table}'. Response text: {response.text}. Error: {e}")
            return {"code" : 500, "message" : "Invalid JSON response from Dataverse insert" , "data" : response.text}
        except Exception as e:
            logger_dataverse.error(f"An unexpected error occurred while inserting into Dataverse table '{table}'. Error: {e}. Response text: {response.text if 'response' in locals() else 'N/A'}")
            return {"code" : 500, "message" : "Error processing Dataverse insert response" , "data" : str(e)}