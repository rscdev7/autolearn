"""
@author           	:  rscalia
@version  		    :  1.0.2
@build-date         :  Sun 09/05/2021
@last_update        :  Sun 09/05/2021

Questo componente serve per testare la classe KafkaLogger

"""

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
    logger:Logger                   = Logger(pName=LOGGER_NAME,pLogPath=LOG_PATH)
    logger.start()


    #Dati da scrivere sull'Event Store
    key:bytes                       = b"client"
    timestamp:int                   = 40000
    record:dict                     = { "source_service":"catalog" , "destination_service": "client", "message_type":"send" , "communication_type":"async" , "timestamp_action":timestamp , "payload": {"value": 800000, "ls":[4,5] }  }


    #Istanzio Oggeto KafkaLogger
    kf_logger:KafkaLogger           = KafkaLogger(NAME, TOPIC_NAME, PARTITION)


    #Scrivo dati
    result:bool                     = await kf_logger.start()
    assert result   == True
    logger.log("[!] Start andato a buon fine")

    result:bool                     = await kf_logger.log(key , record , timestamp)
    assert result   == True
    logger.log("[!] Invio Messaggio andato a buon fine")

    result:bool                     = await kf_logger.stop()
    assert result   == True
    logger.log("[!] Stop andato a buon fine")