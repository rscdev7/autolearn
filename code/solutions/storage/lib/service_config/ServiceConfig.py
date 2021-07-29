"""
@author           	    :  rscalia                              \n
@build-date             :  Thu 27/07/2021                       \n
@last-update            :  Thu 29/07/2021                       \n

Questo componente serve per configurare il microservizio Storage.

"""
import sys
import os
import configparser
from typing                 import Union

class ServiceConfig (object):

    __slots__ = (   "_config",
                    "ENTITY_ID" , 
                    "EVENT_STORE_NAME" , 
                    "EVENT_STORE_PORT" , 
                    "REST_EP_TOPIC" , 
                    "GUARD_TOPIC",
                    "REST_EP_PARTITION", 
                    "GUARD_PARTITION",
                    "DB_HOST_NAME",
                    "DB_PORT",
                    "DB_USER_NAME",
                    "DB_PASSWORD",
                    "DB_NAME",
                    "DB_COLLECTION",
                    "QUEUE_NAME",
                    "BROKER_LOGIN_TOKEN"
                    )
    def inspect (self) -> Union [ None , Exception ]:
        """
        Legge il file di configurazione e memorizza il suo contenuto nell'oggetto corrente

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception   : eccezione da lettura file
        """
        self._config:ConfigParser                       = configparser.ConfigParser(allow_no_value=True)

        try:
            self.ENTITY_ID:str                          = os.environ['HOST_NAME']
            self.EVENT_STORE_NAME:str                   = os.environ['EVENT_STORE_HOST_NAME']
            self.EVENT_STORE_PORT:str                   = os.environ['EVENT_STORE_PORT']
            self.DB_HOST_NAME:str                       = os.environ['STORAGE_DB_HOST_NAME']
            self.DB_PORT:int                            = int( os.environ['STORAGE_DB_PORT'] )
            self.DB_USER_NAME:str                       = os.environ['STORAGE_DB_USERNAME']
            self.DB_PASSWORD:str                        = os.environ['STORAGE_DB_PASSWORD']
            self.BROKER_LOGIN_TOKEN:str                 = os.environ['BROKER_LOGIN_TOKEN']
        except Exception as exp:
            return exp


        #Locate file di configurazione e file Catalogo
        current_dir                                     = os.getcwd().split("/")[-1]
        if (current_dir == "test"):
            cfg_path:str                                = os.path.join ( "..", "config" , "cfg.conf" )
        else:
            cfg_path:str                                = os.path.join ( "config" , "cfg.conf" )


        #Avvio parsing
        try:
            self._config.read(cfg_path)
        except Exception as exp:
            return exp

    
        #Recupero parametri cfg
        sections:list                                   = self._config.sections()
        if 'General' in sections:
            s:str                                       = 'General'
            self.REST_EP_PARTITION                      = int( self._config.get(s, 'REST_EP_PARTITION') )
            self.GUARD_PARTITION                        = int( self._config.get(s, 'GUARD_PARTITION') )
            self.QUEUE_NAME                             = self._config.get(s, 'QUEUE_NAME')
            self.DB_NAME                                = self._config.get(s, 'DB_NAME')
            self.DB_COLLECTION                          = self._config.get(s, 'DB_COLLECTION')
            self.REST_EP_TOPIC                          = self._config.get(s, 'REST_EP_TOPIC')  
            self.GUARD_TOPIC                            = self._config.get(s, 'GUARD_TOPIC')  