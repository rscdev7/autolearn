"""
@author           	    :  rscalia                              \n
@build-date             :  Thu 13/08/2021                       \n
@last-update            :  Thu 13/08/2021                       \n

Questo componente serve per prelevare la configurazione dell'applicativo admin_console
"""
import configparser
from typing                 import Union , List, Tuple
import os

UNABLE_TO_READ_CFG:int                                          = 1


class AdminConfigurator (object):

    __slots__= ( 
                    "ENTITY_ID",
                    "EVENT_STORE_NAME",
                    "EVENT_STORE_PORT",
                    "EVENT_STORE_LOGIN_TOKEN",
                    "OFF_SET_SETUP",
                    "WAIT_TIME",
                    "INFINITE_FETCH"        
    )
    def inspect(self) -> Union [ None , Exception ]:
        """
        Legge il file di configurazione e memorizza il suo contenuto nell'oggetto corrente

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception   : eccezione da lettura file
        """
        try:
            self.ENTITY_ID:str                          = os.environ['HOST_NAME']
            self.EVENT_STORE_NAME:str                   = os.environ['EVENT_STORE_HOST_NAME']
            self.EVENT_STORE_PORT:str                   = os.environ['EVENT_STORE_PORT']

            self.EVENT_STORE_LOGIN_TOKEN:str            = self.EVENT_STORE_NAME+":"+self.EVENT_STORE_PORT
            self.OFF_SET_SETUP:str                      = 'smallest'
            self.WAIT_TIME:int                          = 2
            self.INFINITE_FETCH:bool                    = False
        except Exception as exp:
            return exp