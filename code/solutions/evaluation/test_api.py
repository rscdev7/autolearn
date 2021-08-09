"""
@author           	    :  rscalia                              \n
@build-date             :  Mon 09/08/2021                       \n
@last-update            :  Mon 09/08/2021                       \n

Unit Test end-point REST del Microservizio di Evaluation
"""

import sys
sys.path.append (".")

import pytest
from httpx                                          import AsyncClient, Response
from .main                                          import app
from .lib.network_serializer.NetworkSerializer      import NetworkSerializer
from .test.mongo_engine.MongoEngine                 import MongoEngine
import asyncio
from .lib.async_kafka_consumer.AsyncKafkaConsumer   import AsyncKafkaConsumer
import time
from cryptography.fernet                            import Fernet

URL:str                                                         = "http://localhost:9094/evaluation/api"

DB_HOST_NAME:str                                                = "session_db"
DB_PORT:int                                                     =  27018
USERNAME:str                                                    = "root"
PASSWORD:str                                                    = "example"
DB_NAME:str                                                     = "Session"
COLLECTION_NAME:str                                             = "Sessions"

WAIT_TIME:int                                                   = 1

HOST_NAME:str                                                   = "kafka"
PORT:str                                                        = "9092"
RECORD_TOPIC:str                                                = "evaluation"
PARTITION:int                                                   = 0

EVAL_RECORD_ID:int                                              = 1628439976000
NOT_EXIST_SESS_ID:int                                           = 162844376


@pytest.mark.asyncio
async def test_api_async_pos():
    
    #Costruzione richiesta di evaluation
    serializer:NetworkSerializer                                = NetworkSerializer()
    outcome:Union[None , Exception]                             = serializer.readKeyFromFile()  
    assert issubclass( type( outcome ) , Exception ) == False                    

    crypt_id_sess:Union[ str, Exception ]                       = serializer.encryptField( str(EVAL_RECORD_ID) )
    assert issubclass( type( crypt_id_sess ) , Exception ) == False     

    request:dict                                                = {}
    request['payload']                                          = crypt_id_sess
    ser_data:bytes                                              = serializer.encodeJson(request)
    

    #Richiesta di Evaluation al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/eval_model" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print (payload)
    assert status_code == 202


    
    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': EVAL_RECORD_ID }
    
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res['eval_data'] != None

    engine.stop()

    
    # [3] Check Event Sourcing
    await asyncio.sleep(WAIT_TIME)
    
    consumer:AsyncKafkaConsumer                     = AsyncKafkaConsumer(HOST_NAME , PORT, RECORD_TOPIC , PARTITION)

    outcome:Union[ None , Exception ]               = await consumer.start()
    assert issubclass (type(outcome) , Exception) == False


    #Test Event Store
    outcome:Union[ None , Exception ]               = await consumer.consume()
    assert issubclass (type(outcome) , Exception)   == False

    last_message:dict                               = outcome[-1]
    assert last_message['payload']['payload']       == "update_session"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    train_req:dict                                  = outcome[-3]
    assert train_req['payload']['payload']          == "eval_dto"

    catalog_ans:dict                                = outcome[-4]
    assert catalog_ans['payload']['payload']       == "query_record"

    catalog_req:dict                                = outcome[-5]
    assert catalog_req['payload']['payload']       == "eval_req"
    

    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False



@pytest.mark.asyncio
async def test_api_async_neg():
    
    #Costruzione richiesta di evaluation
    serializer:NetworkSerializer                                = NetworkSerializer()
    outcome:Union[None , Exception]                             = serializer.readKeyFromFile()  
    assert issubclass( type( outcome ) , Exception ) == False                    

    crypt_id_sess:Union[ str, Exception ]                       = serializer.encryptField( str(NOT_EXIST_SESS_ID) )
    assert issubclass( type( crypt_id_sess ) , Exception ) == False     

    request:dict                                                = {}
    request['payload']                                          = crypt_id_sess
    ser_data:bytes                                              = serializer.encodeJson(request)
    

    #Richiesta di Evaluation al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/eval_model" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print (payload)
    assert status_code == 503


    
    # [3] Check Event Sourcing
    await asyncio.sleep(WAIT_TIME)
    
    consumer:AsyncKafkaConsumer                     = AsyncKafkaConsumer(HOST_NAME , PORT, RECORD_TOPIC , PARTITION)

    outcome:Union[ None , Exception ]               = await consumer.start()
    assert issubclass (type(outcome) , Exception) == False


    #Test Event Store
    outcome:Union[ None , Exception ]               = await consumer.consume()
    assert issubclass (type(outcome) , Exception)   == False

    req_ans:dict                                    = outcome[-1]
    assert req_ans['payload']['payload']            == "session_not_exists"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "session_not_exists"

    train_req:dict                                  = outcome[-3]
    assert train_req['payload']['payload']          == "query_record"

    catalog_ans:dict                                = outcome[-4]
    assert catalog_ans['payload']['payload']       == "eval_req"
    

    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False



@pytest.mark.asyncio
async def test_api_async_fake_key():
    
    #Costruzione richiesta di evaluation con chiave fake
    serializer:NetworkSerializer                                = NetworkSerializer()
    fake_key:bytes                                              = Fernet.generate_key()
    crypt_eng:Fernet                                            = Fernet(fake_key) 
    serializer._cryptEngine                                     = crypt_eng
    
    crypt_id_sess:Union[ str, Exception ]                       = serializer.encryptField( str(NOT_EXIST_SESS_ID) )
    assert issubclass( type( crypt_id_sess ) , Exception ) == False     

    request:dict                                                = {}
    request['payload']                                          = crypt_id_sess
    ser_data:bytes                                              = serializer.encodeJson(request)
    

    #Richiesta di Evaluation al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/eval_model" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print (payload)
    assert status_code == 503


    
    # [3] Check Event Sourcing
    await asyncio.sleep(WAIT_TIME)
    
    consumer:AsyncKafkaConsumer                     = AsyncKafkaConsumer(HOST_NAME , PORT, RECORD_TOPIC , PARTITION)

    outcome:Union[ None , Exception ]               = await consumer.start()
    assert issubclass (type(outcome) , Exception) == False


    #Test Event Store
    outcome:Union[ None , Exception ]               = await consumer.consume()
    assert issubclass (type(outcome) , Exception)   == False

    req_ans:dict                                    = outcome[-1]
    assert req_ans['payload']['payload']            == "req_rejected"

    catalog_ans:dict                                = outcome[-2]
    assert catalog_ans['payload']['payload']       == "eval_req"
    

    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False