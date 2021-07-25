"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 24/07/2021                       \n
@last-update            :  Sat 25/07/2021                       \n

Questo componente serve per .........

"""


from ..lib.async_kafka_consumer.AsyncKafkaConsumer      import AsyncKafkaConsumer
import asyncio
import pytest
from typing                                             import Union
import time

HOST_NAME:str               = "kafka"
PORT:str                    = "9092"
TOPIC_NAME:str              = "testeventsourcing"
PARTITION:int               = 0


@pytest.mark.asyncio
async def test_kafka_consumer () -> None:

    consumer:AsyncKafkaConsumer         = AsyncKafkaConsumer(HOST_NAME , PORT, TOPIC_NAME , PARTITION)

    #Test avvio Consumer
    outcome:Union[ None , Exception ]   = await consumer.start()
    assert issubclass (type(outcome) , Exception) == False

    #Test prelievo messaggi
    outcome:Union[ None , Exception ]   = await consumer.consume()
    assert issubclass (type(outcome) , Exception) == False
    print ("\n[!] Retrieved Data:\n\n {}".format(outcome))

    #Test chiusura Connesione
    outcome:Union[ None , Exception ]   = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False