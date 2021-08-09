"""
@author           	    :  rscalia                              \n
@build-date             :  Mon 09/08/2021                       \n
@last-update            :  Mon 09/08/2021                       \n

Questo componente serve per configurare il microservizio Evaluation
"""
import sys
import os
import configparser
from typing                 import Union


class ServiceConfig (object):

    __slots__ = (   "ENTITY_ID" , 
                    "EVENT_STORE_NAME",
                    "EVENT_STORE_PORT",
                    "BROKER_LOGIN_TOKEN",
                    "REST_EP_PARTITION",
                    "REST_EP_TOPIC",
                    "QUEUE",
                    "HEIGHT_WEIGHT_DATA_PATH",
                    "QUERY_RECORD_URL",
                    "_config" )
    def inspect (self) -> Union [ None , Exception ]:
        """
        Legge il file di configurazione e memorizza il suo contenuto nell'oggetto corrente

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception   : eccezione da lettura file
        """
        self._config:ConfigParser                       = configparser.ConfigParser(allow_no_value=True)


        #Acquisizione configurazione dall'ambiente
        try:
            self.ENTITY_ID:str                          = os.environ['HOST_NAME']
            self.EVENT_STORE_NAME:str                   = os.environ['EVENT_STORE_HOST_NAME']
            self.EVENT_STORE_PORT:str                   = os.environ['EVENT_STORE_PORT']
            self.BROKER_LOGIN_TOKEN:str                 = os.environ['BROKER_LOGIN_TOKEN']
        except Exception as exp:
            return exp


        #Avvio parsing
        try:
            self._config.read("./config/cfg.conf")
        except Exception as exp:
            return exp

    
        #Recupero parametri cfg
        sections:list                                   = self._config.sections()
        
        #Recupero parametri cfg
        if 'General' in sections:
            s:str                                       = 'General'
            self.REST_EP_PARTITION:int                  = int( self._config.get(s, 'REST_EP_PARTITION') )
            self.REST_EP_TOPIC:str                      = self.ENTITY_ID 
            self.QUEUE:str                              = self._config.get(s, 'QUEUE')
            self.HEIGHT_WEIGHT_DATA_PATH:str            = self._config.get(s, 'HEIGHT_WEIGHT_DATA_PATH')
            self.QUERY_RECORD_URL:str                   = self._config.get(s, 'QUERY_RECORD_URL')