"""
@author           	    :  rscalia                              \n
@build-date             :  Mon 09/08/2021                       \n
@last-update            :  Mon 09/08/2021                       \n

Questo componente permette di avviare il Microservizio evaluation
"""

import os
from fastapi                                        import APIRouter
from ..logger.Logger                                import Logger
from ..service_config.ServiceConfig                 import ServiceConfig
from ..exception_manager.ExceptionManager           import ExceptionManager
from typing                                         import Tuple
from ..concrete_event_sourcing.AutoLearnLogEntity   import AutoLearnLogEntity
from ..concrete_event_sourcing.KafkaEventStore      import KafkaEventStore


def set_up_rest_end_point () -> Tuple[ APIRouter , ServiceConfig , AutoLearnLogEntity , KafkaEventStore , dict , Logger ]:
    """
    # **set_up_rest_end_point**
    
    Questa funzione permette di configurare il Microservizio evaluation lato REST.

    Returns:\n
        Tuple[ APIRouter ,ServiceConfig , AutoLearnLogEntity , KafkaEventStore , tuple , Logger ] :\n
            Restituisce una tupla contente:\n
                - **APIRouter**, router FastAPI
                - **StorageConfig**, oggetto che mantiene la configurazione dell'applicativo
                - **AutoLearnLogEntity**, oggetto che permette di fare event sourcing
                - **KafkaEventStore**, oggetto che fornisce il layer di persistenza all'event sourcing del microservizio
                - **dict**, tupla contente i parametri di configurazione dell'Event-Store
                - **Logger**, oggetto che permette di loggare una serie di informazioni in merito alle computazioni locali del Microservizio
    """

    #[0] Costanti programma
    UNABLE_TO_READ_CFG_FILE:int                         = 1
    LOGGER_NAME:str                                     = "evaluation__"+str ( os.getpid() )
    LOG_PATH:str                                        = "./log"


    #[1] Costruzione Logger per Computazioni Locali del Microservizio
    logger:Logger                                       = Logger(pName=LOGGER_NAME, pLogPath=LOG_PATH)
    logger.start()


    #[2] Lettura file di congifurazione del Microservizio
    cfg:ServiceConfig                                   = ServiceConfig()
    outcome:Union [ None , Exception]                   = cfg.inspect()
    if ExceptionManager.lookForExceptions(outcome):
        error_msg:str       =  "[REST-API @ set_up_rest_end_point] Impossibile leggere il file di configurazione :(\n-> Causa: {}".format(str(outcome))
        logger.error(error_msg)
        raise RuntimeError (error_msg)
        exit(UNABLE_TO_READ_CFG_FILE)


    #[3] Costruzione Logger per Computazioni che implicano la comunicazione con l'Esterno
    EVENT_STORE_PARAMS:dict                             = { "host_name": cfg.EVENT_STORE_NAME , "port":cfg.EVENT_STORE_PORT , "topic":cfg.REST_EP_TOPIC , "partition":cfg.REST_EP_PARTITION }
    event_store:KafkaEventStore                         = KafkaEventStore()
    network_logger:AutoLearnLogEntity                   = AutoLearnLogEntity()


    #[4] Creazione Router API
    router:APIRouter                                    = APIRouter()


    return router , cfg, network_logger , event_store , EVENT_STORE_PARAMS , logger
