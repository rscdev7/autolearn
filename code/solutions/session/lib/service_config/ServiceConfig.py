"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 31/07/2021                       \n
@last-update            :  Sat 31/07/2021                       \n

Questo componente serve per configurare il microservizio Session.

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
                    "UPDATE_GUARD_TOPIC",
                    "RECORD_GUARD_TOPIC",
                    "REST_EP_PARTITION", 
                    "UPDATE_GUARD_PARTITION",
                    "RECORD_GUARD_PARTITION",
                    "DB_HOST_NAME",
                    "DB_PORT",
                    "DB_USER_NAME",
                    "DB_PASSWORD",
                    "DB_NAME",
                    "DB_COLLECTION",
                    "UPDATE_QUEUE",
                    "RECORD_QUEUE",
                    "BROKER_LOGIN_TOKEN",
                    "STORAGE_RECORD_QUEUE"
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
            self.DB_HOST_NAME:str                       = os.environ['SESSION_DB_HOST_NAME']
            self.DB_PORT:int                            = int( os.environ['SESSION_DB_PORT'] )
            self.DB_USER_NAME:str                       = os.environ['SESSION_DB_USERNAME']
            self.DB_PASSWORD:str                        = os.environ['SESSION_DB_PASSWORD']
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
            self.UPDATE_GUARD_PARTITION                 = int( self._config.get(s, 'UPDATE_GUARD_PARTITION') )
            self.RECORD_GUARD_PARTITION                 = int( self._config.get(s, 'RECORD_GUARD_PARTITION') )

            self.REST_EP_TOPIC                          = self._config.get(s, 'REST_EP_TOPIC')  
            self.UPDATE_GUARD_TOPIC                     = self._config.get(s, 'UPDATE_GUARD_TOPIC')  
            self.RECORD_GUARD_TOPIC                     = self._config.get(s, 'RECORD_GUARD_TOPIC') 


            self.UPDATE_QUEUE                           = self._config.get(s, 'UPDATE_QUEUE')
            self.RECORD_QUEUE                           = self._config.get(s, 'RECORD_QUEUE')
            self.STORAGE_RECORD_QUEUE                   = self._config.get(s, 'STORAGE_RECORD_QUEUE')

            self.DB_NAME                                = self._config.get(s, 'DB_NAME')
            self.DB_COLLECTION                          = self._config.get(s, 'DB_COLLECTION')
            
