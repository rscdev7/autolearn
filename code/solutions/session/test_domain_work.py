"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 31/07/2021                       \n
@last-update            :  Sat 31/07/2021                       \n

Questo modulo permette di testare il domain-work del microservizio Session
"""

import signal
import os
import pytest
import asyncio
from .lib.domain_work.worker                            import guard , save_session
from .lib.mongo_engine.MongoEngine                      import MongoEngine
from multiprocessing                                    import Process
from .lib.rabbit_producer.RabbitProducer                import RabbitProducer
from sklearn.svm                                        import SVC

import time
from .lib.network_serializer.NetworkSerializer          import NetworkSerializer
from .lib.time_stamp_manager.TimeStampManager           import TimeStampManager
import base64
from .lib.async_kafka_consumer.AsyncKafkaConsumer       import AsyncKafkaConsumer
from .lib.logger.Logger                                 import Logger

#Config
SESSION_RECORD_QUEUE:str                            = "sessionRecord"
SESSION_UPDATE_QUEUE:str                            = "sessionUpdate"
LOGIN_TOKEN:str                                     = "amqp://guest:guest@rabbitmq:5672/"

HOST_NAME:str                                       = "kafka"
PORT:str                                            = "9092"
RECORD_TOPIC:str                                    = "sessionRecord"
UPDATE_TOPIC:str                                    = "sessionUpdate"
PARTITION:int                                       = 0

DB_HOST_NAME:str                                    = "session_db"
DB_PORT:int                                         =  27018
USERNAME:str                                        = "root"
PASSWORD:str                                        = "example"
DB_NAME:str                                         = "Session"
COLLECTION_NAME:str                                 = "Sessions"

RECORD_GUARD_TYPE:str                               = "session_record_guard"
UPDATE_GUARD_TYPE:str                               = "session_update_guard"
UPDATE_RECORD_ID:int                                = 1627977121
WAIT_TIME:int                                       = 1


# Lancio Processo che preleva dalla coda i messaggi
p:Process                                           = Process(target=guard , args=( (RECORD_GUARD_TYPE), ))
p.daemon                                            = True
p.start()
pid:int                                             = p.pid
@pytest.mark.asyncio
async def test_record_guard():
    # Istanziazione Serializzatore
    serializer:NetworkSerializer                    = NetworkSerializer()

    # [1] building fake DB Record
    current_time:int                                = TimeStampManager.currentTimeStampInSec()
    record:dict                                     = {}
    record["_id"]                                   = current_time

    dataset:dict                                    = {}
    dataset['dataset_name']                         = "MINIST"
    dataset['dataset_task']                         = "Classification"
    dataset['split_test']                           = 0.03
    dataset['split_seed']                           = 1234

    model:dict                                      = {}
    model['model_name']                             = "SVM"
    model['model_task']                             = "Classification"
    svm:SVC                                         = SVC(kernel='linear',C=200)
    model['model_checkpoint']                       = serializer.encodeBinaryObj(svm)
    model['model_hyperparams']                      = [ { "hyper_param_name":"kernel" , "hyper_param_value":"linear" } ]

    record["train_data"]                            = { "dataset":dataset , "model":model }

    
    # [2] Pubblicazione record su RabbitMQ
    pr:RabbitProducer                               = RabbitProducer(SESSION_RECORD_QUEUE,LOGIN_TOKEN)

    res:Union[None , Exception]                     = await pr.start()
    assert issubclass(type(res) , Exception)        == False

    res:Union[DeliveredMessage, Exception]          = await pr.pubblish( record  )
    assert issubclass(type(res) , Exception)        == False

    res:Union[None , Exception]                     = await pr.stop()
    assert issubclass(type(res) , Exception)        == False


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = {'_id':current_time}
    
    #Connessione a MongoDB
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res["_id"] == current_time

    engine.stop()


    # [3] Check Event Sourcing
    # Invio segnale arresto a processo che legge la coda di RabbitMQ
    os.kill(pid, signal.SIGTERM)
    await asyncio.sleep(WAIT_TIME)

    #Inizio Test EventSourcing
    consumer:AsyncKafkaConsumer                     = AsyncKafkaConsumer(HOST_NAME , PORT, RECORD_TOPIC , PARTITION)

    #Test avvio Consumer
    outcome:Union[ None , Exception ]               = await consumer.start()
    assert issubclass (type(outcome) , Exception) == False

    #Test prelievo messaggi
    outcome:Union[ None , Exception ]               = await consumer.consume()
    assert issubclass (type(outcome) , Exception)   == False

    last_message:dict                               = outcome[-1]
    assert last_message['payload']['payload']       == "train_data_record"

    #Test chiusura Connesione
    outcome:Union[ None , Exception ]               = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False


# Lancio Processo che preleva dalla coda i messaggi
p:Process                                           = Process(target=guard , args=( (UPDATE_GUARD_TYPE), ))
p.daemon                                            = True
p.start()
pid:int                                             = p.pid
@pytest.mark.asyncio
async def test_update_guard():
    # Istanziazione Serializzatore
    serializer:NetworkSerializer                    = NetworkSerializer()

    # [1] building fake DB Record
    record:dict                                     = {}
    record["_id"]                                   = UPDATE_RECORD_ID
    record["eval_data"]                             = [ { "metric_name": "accuracy" , "metric_value": 0.95 } ]


    # [2] Pubblicazione record su RabbitMQ
    pr:RabbitProducer                               = RabbitProducer(SESSION_UPDATE_QUEUE,LOGIN_TOKEN)

    res:Union[None , Exception]                     = await pr.start()
    assert issubclass(type(res) , Exception)        == False

    res:Union[DeliveredMessage, Exception]          = await pr.pubblish( record  )
    assert issubclass(type(res) , Exception)        == False

    res:Union[None , Exception]                     = await pr.stop()
    assert issubclass(type(res) , Exception)        == False


    # [2.1] Test se il record è stato scritto correttamente sul DB
    QUERY:dict                                      = {'_id':UPDATE_RECORD_ID}
    
    #Connessione a MongoDB
    engine:MongoEngine                              = MongoEngine(DB_HOST_NAME, DB_PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)

    res:Union[ None, Exception ]                    = engine.start()
    assert issubclass (type(res) , Exception) == False

    #Attendo scrittura record
    await asyncio.sleep(WAIT_TIME)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res["eval_data"]['experiment_metrics'] == [ { "metric_name": "accuracy" , "metric_value": 0.95 } ]
    engine.stop()

    # [3] Check Event Sourcing
    # Invio segnale arresto a processo che legge la coda di RabbitMQ
    os.kill(pid, signal.SIGTERM)
    await asyncio.sleep(WAIT_TIME)

    #Inizio Test EventSourcing
    consumer:AsyncKafkaConsumer                     = AsyncKafkaConsumer(HOST_NAME , PORT, UPDATE_TOPIC , PARTITION)

    #Test avvio Consumer
    outcome:Union[ None , Exception ]               = await consumer.start()
    assert issubclass (type(outcome) , Exception) == False

    #Test prelievo messaggi
    outcome:Union[ None , Exception ]               = await consumer.consume()
    assert issubclass (type(outcome) , Exception)   == False

    last_message:dict                               = outcome[-1]
    assert last_message['payload']['payload']       == "update_session"

    #Test chiusura Connesione
    outcome:Union[ None , Exception ]               = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False