"""
@author           	:  rscalia
@build-date         :  Sat 31/07/2021
@last_update        :  Sat 31/07/2021

Questo componente serve per testare la classe ServiceConfig
"""

from ..lib.service_config.ServiceConfig     import ServiceConfig
from typing                                 import Union

def test_config_read ():
    """
    Questa funzione permette di testare il parsing del file di configurazione presente nel microservizio Session
    """

    cfg                                 = ServiceConfig()
    outcome:Union[ None, Exception ]    = cfg.inspect()
    assert issubclass ( type(outcome) , Exception ) == False
    
    print ("\n\n-> Config Value: \n\n")
    print("-> EntityID: {}".format(cfg.ENTITY_ID))
    print("-> EVENT_STORE_NAME: {}".format(cfg.EVENT_STORE_NAME))
    print("-> EVENT_STORE_PORT: {}".format(cfg.EVENT_STORE_PORT))
    print("-> REST_EP_TOPIC: {}".format(cfg.REST_EP_TOPIC))
    print("-> UPDATE_GUARD_TOPIC: {}".format(cfg.UPDATE_GUARD_TOPIC))
    print("-> RECORD_GUARD_TOPIC: {}".format(cfg.RECORD_GUARD_TOPIC))
    print("-> REST_EP_PARTITION: {}".format(cfg.REST_EP_PARTITION))
    print("-> UPDATE_GUARD_PARTITION: {}".format(cfg.UPDATE_GUARD_PARTITION))
    print("-> RECORD_GUARD_PARTITION: {}".format(cfg.RECORD_GUARD_PARTITION))
    print("-> DB_HOST_NAME: {}".format(cfg.DB_HOST_NAME))
    print("-> DB_PORT: {}".format(cfg.DB_PORT))
    print("-> DB_USER_NAME: {}".format(cfg.DB_USER_NAME))
    print("-> DB_PASSWORD: {}".format(cfg.DB_PASSWORD))
    print("-> DB_NAME: {}".format(cfg.DB_NAME))
    print("-> DB_COLLECTION: {}".format(cfg.DB_COLLECTION))
    print("-> UPDATE_QUEUE: {}".format(cfg.UPDATE_QUEUE))
    print("-> RECORD_QUEUE: {}".format(cfg.RECORD_QUEUE))
    print("-> BROKER_LOGIN_TOKEN: {}".format(cfg.BROKER_LOGIN_TOKEN))
    print("-> STORAGE_RECORD_QUEUE: {}".format(cfg.STORAGE_RECORD_QUEUE))