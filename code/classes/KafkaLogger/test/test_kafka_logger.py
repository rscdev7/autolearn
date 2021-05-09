"""
@author           	:  rscalia
@version  		    :  1.0.0
@build-date         :  Sun 09/05/2021
@last_update        :  Sun 09/05/2021

Questo componente serve per testare la classe KafkaLogger

"""

#import sys
#sys.path.append("../lib")
#from KafkaLogger import *

from ..lib.KafkaLogger import *
import asyncio
import pytest
import logging


NAME                    = "broker"
TOPIC_NAME              = "Catalog"
PARTITION               = 0
LOGGER_NAME             = "catalog_logger"


def logger_create () -> None:
    """
    Questa funzione permette di creare un logger ausiliario da passare al KafkaLogger presente nei test

    """
    logger                  = logging.getLogger(LOGGER_NAME)

    #Error Handler 
    error_handler           = logging.StreamHandler()
    error_handler.setLevel(logging.ERROR)

    error_handler_format    = logging.Formatter('%(asctime)s %(message)s')
    error_handler.setFormatter(error_handler_format)

    #Error Handler 
    info_handler           = logging.StreamHandler()
    info_handler.setLevel(logging.INFO)

    info_handler_format    = logging.Formatter('%(asctime)s %(message)s')
    info_handler.setFormatter(info_handler_format)


    #Aggiunta Handler al logger
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

    #Imposto il livello del Logger
    logger.setLevel(logging.INFO)


@pytest.mark.asyncio
async def test_kafka_logger () -> None:
    """
    Questa funzione permette di testare il funzionamento di KafkaLogger
    
    """

    #Setup logger
    logger_create()


    #Scrittura Log sull'Event Store
    key = b"client"
    timestamp = 40000
    record    = { "source_service":"catalog" , "destination_service": "client", "message_type":"send" , "communication_type":"async" , "timestamp_action":timestamp , "payload": {"value": 800000, "ls":[4,5] }  }

    kf_logger = KafkaLogger(NAME, TOPIC_NAME, PARTITION ,LOGGER_NAME)


    result          = await kf_logger.setUp()
    assert result   == True

    result          = await kf_logger.log(key , record , timestamp)
    assert result   == True

    result          = await kf_logger.shutDown()
    assert result   == True