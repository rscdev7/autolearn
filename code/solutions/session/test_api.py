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
from lib.network_serializer.NetworkSerializer           import NetworkSerializer
from pprint                                             import pprint

#Cfg
URL:str                     = "http://localhost:9097/session/api"
HOST_NAME:str               = "kafka"
PORT:str                    = "9092"
TOPIC_NAME:str              = "session"
PARTITION:int               = 0
ARCHIVE_RECORD:int          = 1627977121
QUERY_RECORD:int            = 1627977121


@pytest.mark.asyncio
async def test_view_sessions():

    print ("\n<<<<<<<<<<< Test API >>>>>>>>>>>>")

    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.get("/view_sessions")
        status_code:int                         = response.status_code
        payload:dict                            = response.json()


    assert status_code == 202
    assert payload['experiments'] == [] or ( type( payload['experiments'][0]['timestamp'] ) == str and type( payload['experiments'][0]['train_data']['dataset']['split_test'] ) == float )
    pprint ( payload )

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

    assert send_msg['payload']['payload']       == "view_sessions" 
    assert receive_msg['payload']['payload']    == "session_summary" 

    #Test chiusura Connesione
    outcome:Union[ None , Exception ]           = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_save_session():

    print ("\n<<<<<<<<<<< Test API >>>>>>>>>>>>")

    serializer:NetworkSerializer                = NetworkSerializer()
    outcome:Union[None , Exception]             = serializer.readKeyFromFile()
    assert issubclass( type(outcome) , Exception ) == False

    crypt_id:str                                = serializer.encryptField( str(ARCHIVE_RECORD) )
    assert issubclass( type(crypt_id) , Exception ) == False

    req:dict                                    = { "id_sess_cf":crypt_id }
    bytes_req:bytes                             = serializer.encodeJson(req)
    
    
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/save_session" , content=bytes_req)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()


    assert status_code == 202
    assert payload['payload'] == "req_accepted" or payload['payload'] == "req_rejected"

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

    assert send_msg['payload']['payload']       == "save_session" 
    assert receive_msg['payload']['payload']    == "req_accepted" or receive_msg['payload']['payload']  == "req_rejected"

    #Test chiusura Connesione
    outcome:Union[ None , Exception ]           = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False



@pytest.mark.asyncio
async def test_query_record():

    print ("\n<<<<<<<<<<< Test API >>>>>>>>>>>>")

    ser:NetworkSerializer                       = NetworkSerializer()
    ser_data:bytes                              = ser.encodeJson( { "id_rec" : QUERY_RECORD } )

    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/query_one_record", content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()


    assert status_code == 202 
    assert type(payload['timestamp']) == int
    
    if "timestamp" in payload.keys():
        assert  payload['timestamp']    == QUERY_RECORD
    else:
        assert  payload["message"]      == "session_not_exists"


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

    assert send_msg['payload']['payload']       == "query_record" 
    assert receive_msg['payload']['payload']    == "eval_dto" or receive_msg['payload']['payload']    == "session_not_exists"


    #Test chiusura Connesione
    outcome:Union[ None , Exception ]           = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False