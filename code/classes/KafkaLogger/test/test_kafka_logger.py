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

from ..lib.kafka_logger.KafkaLogger import KafkaLogger
from ..lib.logger.Logger import Logger
import asyncio
import pytest
import logging


NAME                    = "broker"
TOPIC_NAME              = "catalog"
PARTITION               = 0
LOGGER_NAME             = "catalog_logger"
LOG_PATH:str            = "../log"


@pytest.mark.asyncio
async def test_kafka_logger () -> None:
    """
    Questa funzione permette di testare il funzionamento di KafkaLogger
    
    """

    #Setup logger
    logger:Logger       = Logger(pName=LOGGER_NAME,pLogPath=LOG_PATH)
    logger.start()

    #Scrittura Log sull'Event Store
    key:bytes                       = b"client"
    timestamp:int                   = 40000
    record:dict                     = { "source_service":"catalog" , "destination_service": "client", "message_type":"send" , "communication_type":"async" , "timestamp_action":timestamp , "payload": {"value": 800000, "ls":[4,5] }  }

    kf_logger:KafkaLogger           = KafkaLogger(NAME, TOPIC_NAME, PARTITION ,LOGGER_NAME)


    result                          = await kf_logger.setUp()
    assert result   == True

    result                          = await kf_logger.log(key , record , timestamp)
    assert result   == True

    result                          = await kf_logger.shutDown()
    assert result   == True