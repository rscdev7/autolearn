"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 08/08/2021                       \n
@last-update            :  Wed 08/08/2021                       \n

Unit Test end-point REST del Microservizio di Training
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

URL:str                                                         = "http://localhost:9091/training/api"

DB_HOST_NAME:str                                                = "session_db"
DB_PORT:int                                                     =  27018
USERNAME:str                                                    = "root"
PASSWORD:str                                                    = "example"
DB_NAME:str                                                     = "Session"
COLLECTION_NAME:str                                             = "Sessions"

WAIT_TIME:int                                                   = 1

HOST_NAME:str                                                   = "kafka"
PORT:str                                                        = "9092"
RECORD_TOPIC:str                                                = "training"
PARTITION:int                                                   = 0


@pytest.mark.asyncio
async def test_api_async_1():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "SVM"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"kernel" , "hyper_param_value":"linear" } ]
    
    record["train_data"]                                        = { "dataset":dataset , "model":model }


    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)


    #Richiesta di Training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print (payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']       == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']       == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']       == "training_req"



    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_api_async_2():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Height-Weight Dataset"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "SVM"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"kernel" , "hyper_param_value":"linear" } ]

    record["train_data"]                                        = { "dataset":dataset , "model":model }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Richiesta di training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print (payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']        == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']        == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']          == "training_req"


    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False

@pytest.mark.asyncio
async def test_api_async_21():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Height-Weight Dataset"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "SVM"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"kernel" , "hyper_param_value":"skl" } ]

    record["train_data"]                                        = { "dataset":dataset , "model":model }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Richiesta di training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print (payload)
    assert status_code == 503


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert "bad_request"            in last_message['payload']['payload']    

    catalog_ans:dict                                = outcome[-2]
    assert catalog_ans['payload']['payload']        == "training_catalog"

    catalog_req:dict                                = outcome[-3]
    assert catalog_req['payload']['payload']        == "training_catalog_req"

    train_req:dict                                  = outcome[-4]
    assert train_req['payload']['payload']          == "training_req"


    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_api_async_3():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Height-Weight Dataset"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "SVM"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"kernel" , "hyper_param_value":"linear" } , { "hyper_param_name":"max_iter" , "hyper_param_value":200 } ]

    record["train_data"]                                        = { "dataset":dataset , "model":model }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Richiesta di training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print (payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']        == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']        == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']          == "training_req"


    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_api_async_4():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Height-Weight Dataset"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "SVM"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"kernel" , "hyper_param_value":"linear" } , { "hyper_param_name":"max_iter" , "hyper_param_value":200 } ]


    learning:dict                                               = {}
    learning['learning_hyperparams']                            = [  {"hyper_param_name":"regularization" , "hyper_param_value": "1.5" } ]

    record["train_data"]                                        = { "dataset":dataset , "model":model , "learning":learning }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Richiesta di training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print (payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']        == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']        == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']          == "training_req"


    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_api_async_5():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Height-Weight Dataset"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "SVM"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"kernel" , "hyper_param_value":"rbf" } , { "hyper_param_name":"max_iter" , "hyper_param_value":200 } ]


    learning:dict                                               = {}
    learning['learning_hyperparams']                            = [  {"hyper_param_name":"regularization" , "hyper_param_value": "1.5" } ]

    record["train_data"]                                        = { "dataset":dataset , "model":model , "learning":learning }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Richiesta di training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print (payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']        == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']        == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']          == "training_req"


    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_api_async_7():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Height-Weight Dataset"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "SVM"
    model['model_task']                                         = "Classification"

    record["train_data"]                                        = { "dataset":dataset , "model":model }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Richiesta di training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()


    print (payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']        == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']        == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']          == "training_req"


    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_api_async_8():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}

    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "RandomForest"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"max_depth" , "hyper_param_value": 2 } ]

    record["train_data"]                                        = { "dataset":dataset , "model":model }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Invio richiesta training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print(payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    #Connessione a MongoDB
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']       == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']       == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']         == "training_req"



    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False



@pytest.mark.asyncio
async def test_api_async_9():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}

    dataset['dataset_name']                                     = "Height-Weight Dataset"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "RandomForest"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"max_depth" , "hyper_param_value": 2 } , { "hyper_param_name":"n_estimator" , "hyper_param_value": 3 } ]

    record["train_data"]                                        = { "dataset":dataset , "model":model }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Invio richiesta training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print(payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    #Connessione a MongoDB
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']       == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']       == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']         == "training_req"



    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False



@pytest.mark.asyncio
async def test_api_async_10():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}

    dataset['dataset_name']                                     = "Height-Weight Dataset"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "RandomForest"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"max_depth" , "hyper_param_value": 2 }  ]

    record["train_data"]                                        = { "dataset":dataset , "model":model }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Invio richiesta training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print(payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    #Connessione a MongoDB
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']       == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']       == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']         == "training_req"



    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_api_async_11():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}

    dataset['dataset_name']                                     = "Height-Weight Dataset"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "RandomForest"
    model['model_task']                                         = "Classification"

    record["train_data"]                                        = { "dataset":dataset , "model":model }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Invio richiesta training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print(payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    #Connessione a MongoDB
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']       == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']       == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']         == "training_req"



    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_api_async_12():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}

    dataset['dataset_name']                                     = "Height-Weight Dataset"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "DecisionTree"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"max_depth" , "hyper_param_value": 2 }  ]
    record["train_data"]                                        = { "dataset":dataset , "model":model }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Invio richiesta training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print(payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    #Connessione a MongoDB
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']       == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']       == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']         == "training_req"



    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_api_async_13():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}

    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "DecisionTree"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"max_depth" , "hyper_param_value": 2 }  ]
    record["train_data"]                                        = { "dataset":dataset , "model":model }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Invio richiesta training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print(payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    #Connessione a MongoDB
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']       == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']       == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']         == "training_req"



    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_api_async_14():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}

    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "DecisionTree"
    model['model_task']                                         = "Classification"
    record["train_data"]                                        = { "dataset":dataset , "model":model }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Invio richiesta training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print(payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    #Connessione a MongoDB
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']       == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']       == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']         == "training_req"



    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_api_async_15():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}

    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "LogisticRegressor"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"random_state" , "hyper_param_value": 5 }  ]
    record["train_data"]                                        = { "dataset":dataset , "model":model }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Invio richiesta training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print(payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    #Connessione a MongoDB
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']       == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']       == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']         == "training_req"



    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_api_async_16():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}

    dataset['dataset_name']                                     = "Height-Weight Dataset"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "LogisticRegressor"
    model['model_task']                                         = "Classification"
    record["train_data"]                                        = { "dataset":dataset , "model":model }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Invio richiesta training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print(payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    #Connessione a MongoDB
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']       == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']       == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']         == "training_req"



    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_api_async_17():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}

    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "LogisticRegressor"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"random_state" , "hyper_param_value": 5 }  ]

    learning:dict                                               = {}
    learning['learning_hyperparams']                            = [  {"hyper_param_name":"max_iter" , "hyper_param_value": 300 } ]    
    record["train_data"]                                        = { "dataset":dataset , "model":model , "learning":learning}

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Invio richiesta training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print(payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    #Connessione a MongoDB
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']       == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']       == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']         == "training_req"



    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False



@pytest.mark.asyncio
async def test_api_async_18():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}

    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "Naive-Bayes"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [  {"hyper_param_name":"priors" , "hyper_param_value": [0.5,0.3,0.2] } ]    

    record["train_data"]                                        = { "dataset":dataset , "model":model }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Invio richiesta training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print(payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    #Connessione a MongoDB
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']       == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']       == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']         == "training_req"



    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_api_async_19():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}

    dataset['dataset_name']                                     = "Height-Weight Dataset"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "Naive-Bayes"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [  {"hyper_param_name":"priors" , "hyper_param_value": [0.5,0.3,35.0] } ]    

    record["train_data"]                                        = { "dataset":dataset , "model":model }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Invio richiesta training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print(payload)
    assert status_code == 503


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    #Connessione a MongoDB
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert "bad_request" in last_message['payload']['payload']      


    catalog_ans:dict                                = outcome[-2]
    assert catalog_ans['payload']['payload']       == "training_catalog"

    catalog_req:dict                                = outcome[-3]
    assert catalog_req['payload']['payload']       == "training_catalog_req"

    train_req:dict                                  = outcome[-4]
    assert train_req['payload']['payload']         == "training_req"



    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


@pytest.mark.asyncio
async def test_api_async_20():
    
    #Costruzione richiesta di training fake
    record:dict                                                 = {}

    dataset:dict                                                = {}

    dataset['dataset_name']                                     = "Height-Weight Dataset"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "Naive-Bayes"
    model['model_task']                                         = "Classification"

    record["train_data"]                                        = { "dataset":dataset , "model":model }

    #Serializzazione richiesta di training
    serializer:NetworkSerializer                                = NetworkSerializer()
    ser_data:bytes                                              = serializer.encodeJson(record)
    current_time:int                                            = int ( time.time() * 1000)

    #Invio richiesta training al backend
    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response                       = await ac.post("/training_req" , content=ser_data)
        status_code:int                         = response.status_code
        payload:dict                            = response.json()

    print(payload)
    assert status_code == 202


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = { '_id': { '$gt':current_time } }
    
    #Connessione a MongoDB
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res != {}

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
    assert last_message['payload']['payload']       == "train_data_record"

    req_ans:dict                                    = outcome[-2]
    assert req_ans['payload']['payload']            == "req_accepted"

    catalog_ans:dict                                = outcome[-3]
    assert catalog_ans['payload']['payload']       == "training_catalog"

    catalog_req:dict                                = outcome[-4]
    assert catalog_req['payload']['payload']       == "training_catalog_req"

    train_req:dict                                  = outcome[-5]
    assert train_req['payload']['payload']         == "training_req"



    outcome:Union[ None , Exception ]              = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False