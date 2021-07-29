"""
@author           	:  rscalia
@build-date         :  Tue 27/07/2021
@last_update        :  Tue 27/07/2021

Questo componente serve per testare la classe StorageConfig
"""

from ..lib.service_config.ServiceConfig     import ServiceConfig
from typing                                 import Union

def test_config_read ():
    """
    Questa funzione permette di testare il parsing del file di configurazione presente nel componente CatalogConfig
    """

    cfg                                 = ServiceConfig()
    outcome:Union[ None, Exception ]    = cfg.inspect()
    assert issubclass ( type(outcome) , Exception ) == False
    
    print ("\n\nConfig Value: \n\n-> EntityID: {}\n-> Event-Store Host Name: {} \n-> Event-Store Port: {} \n-> REST Topic Name: {} \n-> REST Partition: {}\n-> Guard Topic: {}\n-> Guard Partition: {} \n-> Broker Login Token: {} \n-> Queue Name: {}\n-> DB Host Name: {}\n-> DB Port:{}\n-> DB User Name: {}\n-> DB Password: {}\n-> DB Name: {}\n-> DB Collection: {}".format(
    cfg.ENTITY_ID,
    cfg.EVENT_STORE_NAME,
    cfg.EVENT_STORE_PORT,
    cfg.REST_EP_TOPIC, 
    cfg.REST_EP_PARTITION,
    cfg.GUARD_TOPIC,
    cfg.GUARD_PARTITION, 
    cfg.BROKER_LOGIN_TOKEN,
    cfg.QUEUE_NAME,
    cfg.DB_HOST_NAME,
    cfg.DB_PORT,
    cfg.DB_USER_NAME,
    cfg.DB_PASSWORD,
    cfg.DB_NAME,
    cfg.DB_COLLECTION
    ))
    