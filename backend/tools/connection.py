import urllib
import sqlalchemy
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
import logging
load_dotenv()

logging.basicConfig(filename="app.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)



class Connect:

    def __init__(self):
        load_dotenv()
        
        self.Server=os.getenv('Server')
        self.Driver=os.getenv('Driver')
        self.Username=os.getenv('user')
        self.Password=os.getenv('Password')
        self.DataBaseBronze=os.getenv('DataBaseBronze')
        self.DataBaseSilver=os.getenv('DataBaseSilver')
        self.DataBaseGold=os.getenv('DataBaseGold')
        self.DataBaseZeusAutomation = os.getenv('DataBaseZeusAutomation')
        print("constructor variable :")
        print(self.Server)

        


    def bronze_connection(self):
        server = self.Server
        driver = self.Driver
        username = self.Username
        password = self.Password
        database = self.DataBaseBronze
        params = urllib.parse.quote_plus(
            f'DRIVER={driver};'
            f'SERVER={server};'
            f'UID={username};'
            f'PWD={password};'
            f'DATABASE={database};'
            'TrustServerCertificate=yes;'
        )
        print(params)
        logging.debug("creating engine for bronze connection")
        logging.debug(f"Server: {server}, Driver: {driver}, Username: {username}, Password: {password}, Database: {database}")
        try:
            engine= create_engine("mssql+pyodbc:///?odbc_connect=%s" % params) 
            return engine
        except:
            logging.error("Error creating engine for bronze connection")
            return  {"code": 500, "message": "Connection build is failed bronze", "status": 'failed'}
    
    def silver_connection(self):
        server = self.Server
        driver = self.Driver
        username = self.Username
        password = self.Password
        database = self.DataBaseSilver
        params = urllib.parse.quote_plus(
            f'DRIVER={driver};'
            f'SERVER={server};'
            f'UID={username};'
            f'PWD={password};'
            f'DATABASE={database};'
            'TrustServerCertificate=yes;'
        )
     
        try:
            logging.debug("creating engine for silver connection")
            logging.debug(f"Server: {server}, Driver: {driver}, Username: {username}, Password: {password}, Database: {database}")
            engine= create_engine("mssql+pyodbc:///?odbc_connect=%s" % params) 
            return engine
        except:
            logging.error("Error creating engine for silver connection")
            return  {"code": 500, "message": "Connection build is failed silver connection", "status": 'failed'}
    
    def gold_connection(self):
        server = self.Server
        driver = self.Driver
        username = self.Username
        password = self.Password
        database = self.DataBaseGold
        params = urllib.parse.quote_plus(
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"UID={username};"
            f"PWD={password};"
            f"DATABASE={database};"
            f"TrustServerCertificate=yes;"
            
        )

        logging.debug("creating engine for gold connection")
        logging.debug(f"Server: {server}, Driver: {driver}, Username: {username}, Password: {password}, Database: {database}")
        try:
            engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
            return engine
        except SQLAlchemyError as e:
            logging.error("Error creating engine for gold connection")
            raise ConnectionError("Connection build is failed gold connection") from e
        
    def zeus_automation_connection(self):
        server = self.Server
        driver = self.Driver
        username = self.Username
        password = self.Password
        database = self.DataBaseZeusAutomation
        params = urllib.parse.quote_plus(
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"UID={username};"
            f"PWD={password};"
            f"DATABASE={database};"
            f"TrustServerCertificate=yes;"
            
        )

        logging.debug("creating engine for zeus automation connection")
        logging.debug(f"Server: {server}, Driver: {driver}, Username: {username}, Password: {password}, Database: {database}")
        try:
            engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
            return engine
        except SQLAlchemyError as e:
            logging.error("Error creating engine for gold connection")
            raise ConnectionError("Connection build is failed gold connection") from e
