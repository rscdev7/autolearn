"""
@author           	    :  rscalia                              \n
@build-date             :  Wed 27/07/2021                       \n
@last-update            :  Sat 31/07/2021                       \n

Questo modulo permette di testare il domain-work del microservizio Storage
"""

import signal
import os
import pytest
import asyncio

from .lib.domain_work.worker                            import guard
from .lib.mongo_engine.MongoEngine                      import MongoEngine
from multiprocessing                                    import Process
from .test.rabbit_producer.RabbitProducer               import RabbitProducer
from sklearn.svm                                        import SVC

from .lib.network_serializer.NetworkSerializer          import NetworkSerializer
from .lib.time_stamp_manager.TimeStampManager           import TimeStampManager
from .lib.async_kafka_consumer.AsyncKafkaConsumer       import AsyncKafkaConsumer


#Config
QUEUE_NAME:str                                      = "storageRecord"
LOGIN_TOKEN:str                                     = "amqp://guest:guest@rabbitmq:5672/"

HOST_NAME:str                                       = "kafka"
PORT:str                                            = "9092"
TOPIC_NAME:str                                      = "storageRecord"
PARTITION:int                                       = 0

DB_HOST_NAME:str                                    = "storage_db"
DB_PORT:int                                         =  27017
USERNAME:str                                        = "root"
PASSWORD:str                                        = "example"
DB_NAME:str                                         = "Storage"
COLLECTION_NAME:str                                 = "Experiments"


# Lancio Processo che preleva dalla coda i messaggi
p:Process                                           = Process(target=guard)
p.daemon                                            = True
p.start()
pid:int                                             = p.pid


@pytest.mark.asyncio
async def test_guard():
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
    pr:RabbitProducer                               = RabbitProducer(QUEUE_NAME,LOGIN_TOKEN)

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
    await asyncio.sleep(1)

    res:Union[dict, Exception, None]                = await engine.queryOnes(QUERY)
    assert issubclass (type(res) , Exception) == False and type(res) != None
    assert res["_id"] == current_time


    # [3] Check Event Sourcing
    # Invio segnale arresto a processo che legge la coda di RabbitMQ
    os.kill(pid, signal.SIGTERM)
    await asyncio.sleep(1)

    #Inizio Test EventSourcing
    consumer:AsyncKafkaConsumer                     = AsyncKafkaConsumer(HOST_NAME , PORT, TOPIC_NAME , PARTITION)

    #Test avvio Consumer
    outcome:Union[ None , Exception ]               = await consumer.start()
    assert issubclass (type(outcome) , Exception) == False

    #Test prelievo messaggi
    outcome:Union[ None , Exception ]               = await consumer.consume()
    assert issubclass (type(outcome) , Exception)   == False
    last_message:dict                               = outcome[-1]
    assert last_message['payload']['payload']       == "archive_data"

    #Test chiusura Connesione
    outcome:Union[ None , Exception ]               = await consumer.stop()
    assert issubclass (type(outcome) , Exception) == False
        






    

