"""
@author           	    :  rscalia                              \n
@build-date             :  Wed 27/07/2021                       \n
@last-update            :  Wed 27/07/2021                       \n

Test REST-API
"""

import sys
sys.path.append (".")

import pytest
from httpx                                              import AsyncClient, Response
from fastapi.testclient                                 import TestClient
from main                                               import app
from pprint                                             import pprint
from lib.async_kafka_consumer.AsyncKafkaConsumer        import AsyncKafkaConsumer

#Cfg
URL:str                     = "http://localhost:9099/storage/api"
HOST_NAME:str               = "kafka"
PORT:str                    = "9092"
TOPIC_NAME:str              = "storage"
PARTITION:int               = 0


@pytest.mark.asyncio
async def test_api_async():

    print ("\n<<<<<<<<<<< Test API >>>>>>>>>>>>")

    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.get("/view_experiments")
        status_code:int                         = response.status_code
        payload:dict                            = response.json()


    assert status_code == 202
    assert payload['experiments'] == [] or ( type( payload['experiments'][0]['timestamp'] ) == int and type( payload['experiments'][0]['train_data']['dataset']['split_test'] ) == float )


    #Controllo in merito alla buona riuscita dell'Event-Sourcing
    consumer:AsyncKafkaConsumer                 = AsyncKafkaConsumer(HOST_NAME , PORT, TOPIC_NAME , PARTITION)

    #Test avvio Consumer
    outcome:Union[ None , Exception ]           = await consumer.start()
    assert issubclass (type(outcome) , Exception) == False

    #Test prelievo messaggi
    outcome:Union[ List[dict] , Exception ]     = await consumer.consume()
    assert issubclass (type(outcome) , Exception) == False
    
    receive_msg:dict                            = outcome[-1]
    send_msg:dict                               = outcome[-2]

    assert send_msg['payload']['payload']       == "view_experiments" 
    assert receive_msg['payload']['payload']    == "storage_summary" or receive_msg['payload']['payload']    == "unable_to_fetch_data"

    #Test chiusura Connesione
    outcome:Union[ None , Exception ]           = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False

