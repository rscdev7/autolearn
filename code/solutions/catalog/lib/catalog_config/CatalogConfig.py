"""
@author           	:  rscalia
@version  		    :  1.0.0
@build-date         :  Sun 09/05/2021
@last_update        :  Sun 09/05/2021

Questo componente serve per caricare in memoria la configurazione del Microservizio Catalog.
"""

import sys
import os
import configparser
from typing                 import Union


class CatalogConfig (object):

    __slots__ = ("_config","ENTITY_ID" , "EVENT_STORE_NAME" , "EVENT_STORE_PORT" , "TOPIC" , "PARTITON", "CATALOG_PATH")
    def inspect (self) -> Union [ None , Exception ]:
        """
        Legge il file di configurazione e memorizza il suo contenuto nell'oggetto corrente

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception   : eccezione da lettura file
        """
        self._config                                    = configparser.ConfigParser(allow_no_value=True)

        try:
            self.ENTITY_ID:str                          = os.environ['HOST_NAME']
            self.EVENT_STORE_NAME:str                   = os.environ['EVENT_STORE_HOST_NAME']
            self.EVENT_STORE_PORT:str                   = os.environ['EVENT_STORE_PORT']
            self.TOPIC:str                              = os.environ['HOST_NAME']
        except Exception as exp:
            return exp


        #Locate file di configurazione e file Catalogo
        current_dir                                     = os.getcwd().split("/")[-1]
        if (current_dir == "test"):
            cfg_path:str                                = os.path.join ( "..", "config" , "config.conf" )
            self.CATALOG_PATH:str                       = os.path.join ( "..", "data" , "autolearn_catalog.json" )
        else:
            cfg_path:str                                = os.path.join ( "config" , "config.conf" )
            self.CATALOG_PATH:str                       = os.path.join ( ".", "data" , "autolearn_catalog.json" )


        #Avvio parsing
        try:
            self._config.read(cfg_path)
        except Exception as exp:
            return exp

        sections:list                                   = self._config.sections()


        #Recupero parametri cfg
        if 'General' in sections:
            s:str                                       = 'General'
            self.PARTITON                               = int(self._config.get(s, 'PARTITON'))