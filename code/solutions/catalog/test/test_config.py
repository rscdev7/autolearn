"""
@author           	:  rscalia
@build-date         :  Sun 09/05/2021
@last_update        :  Sun 09/05/2021

Questo componente serve per testare la classe CatalogConfig
"""

from ..lib.catalog_config.CatalogConfig     import CatalogConfig
from typing                                 import Union

def test_config_read ():
    """
    Questa funzione permette di testare il parsing del file di configurazione presente nel componente CatalogConfig
    """

    cfg                                 = CatalogConfig()
    outcome:Union[ None, Exception ]    = cfg.inspect()
    assert issubclass ( type(outcome) , Exception ) == False

    print ("\n\nConfig Value: \n\n-> EntityID: {}\n-> Event-Store Host Name: {} \n-> Event-Store Port: {} \n-> Topic Name: {} \n-> Partition: {}\n-> Catalog Path: {} ".format(cfg.ENTITY_ID,cfg.EVENT_STORE_NAME, cfg.EVENT_STORE_PORT , cfg.TOPIC, cfg.PARTITON, cfg.CATALOG_PATH))