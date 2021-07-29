"""
@author           	    :  rscalia                              \n
@build-date             :  Wed 27/07/2021                       \n
@last-update            :  Thu 29/07/2021                       \n

Questo componente serve per testare il Microservizio Catalog
"""

import sys
sys.path.append (".")

import pytest
from httpx                                          import AsyncClient, Response
import shutil
from main                                           import app

from lib.async_kafka_consumer.AsyncKafkaConsumer    import AsyncKafkaConsumer

URL:str                     = "http://localhost:9200/catalog/api"
HOST_NAME:str               = "kafka"
PORT:str                    = "9092"
TOPIC_NAME:str              = "catalog"
PARTITION:int               = 0


@pytest.mark.asyncio
async def test_api_positive():
    print ("\n<<<<<<<<<<< Test API Positivo >>>>>>>>>>>>")

    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response = await ac.get("/get_catalog?pIdClient=test_client")
        status_code:int   = response.status_code
        payload:dict      = response.json()

    assert status_code == 202
    assert set( [ "data_lake" , "models" , "metrics" , "learning" ] ).issubset( set( payload.keys() ) )


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

    assert send_msg['payload']['payload']       == "training_catalog_req" 
    assert receive_msg['payload']['payload']    == "training_catalog" or receive_msg['payload']['payload']    == "unable_to_find_catalog"

    #Test chiusura Connesione
    outcome:Union[ None , Exception ]           = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_api_negative():
    print ("\n<<<<<<<<<<< Test API Negativo >>>>>>>>>>>>")

    #Altero la posizione del file del catalogo in modo da simulare l'assenza di quest'ultimo
    shutil.move("./data/autolearn_catalog.json" , ".")

    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response = await ac.get("/get_catalog?pIdClient=test_client")
        status_code:int   = response.status_code
        payload:dict      = response.json()

    assert status_code == 503
    assert payload     == { "message" : "Unable to Retrieve Catalog" }

    #Rimetto a posto il file del catalogo
    shutil.move("./autolearn_catalog.json" , "./data/autolearn_catalog.json")


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

    assert send_msg['payload']['payload']       == "training_catalog_req" 
    assert receive_msg['payload']['payload']    == "training_catalog" or receive_msg['payload']['payload']    == "unable_to_find_catalog"

    #Test chiusura Connesione
    outcome:Union[ None , Exception ]           = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False

    