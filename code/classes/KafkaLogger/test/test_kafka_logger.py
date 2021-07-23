"""
@author           	:  rscalia
@build-date         :  Sun 09/05/2021
@last_update        :  Fri 23/07/2021

Questo componente serve per testare la classe KafkaLogger

"""

from ..lib.kafka_logger.KafkaLogger             import KafkaLogger
import asyncio
import pytest
from typing                                     import Union
import time

HOST_NAME:str               = "kafka"
PORT:str                    = "9092"
TOPIC_NAME:str              = "test"
PARTITION:int               = 0


@pytest.mark.asyncio
async def test_kafka_logger () -> None:
    """
    Questa funzione permette di testare il funzionamento di KafkaLogger
    
    """
    #Dati da scrivere sull'Event Store
    key:bytes                                               = b"client"
    timestamp:int                                           = round ( time.time() * 1000 )
    record:dict                                             = { "source_service":"catalog" , "destination_service": "client", "message_type":"send" , "communication_type":"async" , "timestamp_action":timestamp , "payload": {"value": 800000, "ls":[4,5] }  }


    #Istanzio Oggeto KafkaLogger
    kf_logger:KafkaLogger                                   = KafkaLogger(HOST_NAME, PORT ,TOPIC_NAME, PARTITION)


    #Scrivo dati
    result:Union[ None , Exception ]                        = await kf_logger.start()
    assert issubclass(type(result), Exception)              == False
    print("[!] Start andato a buon fine")

    result:Union[ None , Exception ]                        = await kf_logger.log(key , record , timestamp)
    assert issubclass(type(result), Exception)              == False
    print("[!] Invio Messaggio andato a buon fine")

    result:Union[ None , Exception ]                        = await kf_logger.stop()
    assert issubclass(type(result), Exception)              == False
    print("[!] Stop andato a buon fine")