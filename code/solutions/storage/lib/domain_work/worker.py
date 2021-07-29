"""
@author           	    :  rscalia                              \n
@build-date             :  Wed 28/07/2021                       \n
@last-update            :  Thu 29/07/2021                       \n

Questo componente implementa un processo che sta in attesa in maniera asincrona su una coda RabbitMQ.

Una volta che si preleva un messaggio dalla coda, lo si archivierà in un'apposita base di dati.
"""

import signal
from signal                                                 import Signals
from typing                                                 import List, Union
import pickle

import asyncio
from asyncio                                                import AbstractEventLoop , Queue

from aio_pika.exceptions                                    import QueueEmpty
from bson.objectid                                          import ObjectId
from bson.binary                                            import Binary

from ..logger.Logger                                        import Logger
from ..service_set_up.system_set_up                         import set_up_guard
from ..event_sourcing_utility.event_sourcing_utility        import make_behavioral_event, setUpEventSourcing
from ..exception_manager.ExceptionManager                   import ExceptionManager
from ..abstract_event_sourcing.DomainEvent                  import DomainEvent
from ..rabbit_consumer.RabbitConsumer                       import RabbitConsumer
from ..mongo_engine.MongoEngine                             import MongoEngine
from ..concrete_event_sourcing.AutoLearnLogEntity           import AutoLearnLogEntity
from ..concrete_event_sourcing.KafkaEventStore              import KafkaEventStore
from ..time_stamp_manager.TimeStampManager                  import TimeStampManager
from ..service_config.ServiceConfig                         import ServiceConfig
from ..network_serializer.NetworkSerializer                 import NetworkSerializer


UNABLE_TO_CONNECT_TO_RABBIT_MQ:int      = 2
UNABLE_TO_CONNECT_TO_MONGO:int          = 3


async def shut_down_system( pQueue:Queue ) -> None:
    """
    # **shut_down_system**

    Questa funzione inserisce un messaggio nella coda che intima la corutine monitor di arrestare la sua computazione

    Args:\n
        pQueue                      ( Queue )       : coda asincrona
    """
    await pQueue.put("exit")


async def monitor (pParams:tuple, pRabbitConsumer:RabbitConsumer , pDBEngine:MongoEngine , pQueue:Queue) -> None:
    """
    # **monitor**

    Questa funzione monitora la coda RabbitMQ "StorageRecord" e ogni volta che trova un record lo scrive sul DB di Storage.


    Args:\n

        pParams             (tuple)              : parametri necessari all'event-sourcing e alla configurazione.
                                                        La tupla contiene i seguenti oggetti:
                                                            - **ServiceConfig**
                                                            - **AutoLearnLogEntity**
                                                            - **KafkaEventStore**
                                                            - **EVENT_STORE_PARAMS**    : dict
                                                            - **Logger**

        pRabbitConsumer     (RabbitConsumer)    : consumatore RabbitMQ

        pDBEngine           (MongoEngine)       : componente che si interfaccia col DB

    Raises:\n
        Exception           : errore di connessione/scrittura dati con RabbitMQ o MongoDB o Kafka.
    """
    network_logger:AutoLearnLogEntity                               = pParams[1]
    event_store:KafkaEventStore                                     = pParams[2]
    logger:Logger                                                   = pParams[4]
    serializer:NetworkSerializer                                    = NetworkSerializer()

    while True:

        # [0] Se ricevo un messaggio di "exit" nella coda, arresto il processo di guard
        try:
            pQueue.get_nowait()
            break
        except Exception as exp:
            pass


        # [1] Tentativo prelievo dati da coda RabbitMQ
        record:Union[ None , Exception]                             = await pRabbitConsumer.consume()

        if ExceptionManager.lookForExceptions (record) and issubclass ( type(record) , QueueEmpty) == False:
            logger.error ( "Impossibile consumare messaggio dalla coda RabbitMQ \n-> Causa: {}".format( str( record ) ) )
            continue
        elif issubclass( type(record) , QueueEmpty ):
            continue
        
        current_time:int                                            = TimeStampManager.currentTimeStampInMS()


        # [2] Log su Event-Store
        event:DomainEvent                                           = make_behavioral_event(b"session" , current_time , "session" , "storage" , "receive" , "async" , "archive_data")
        outcome:Union[ None , Exception]                            = await network_logger.emit(event)

        if ExceptionManager.lookForExceptions (outcome):
            logger.error ( "Impossibile Scrivere su Event-Store \n-> Causa: {}".format( str( outcome ) ) )


        # [4] Serializzo l'oggetto del checkpoint in binario utilizzando un formato compatibile con Mongo
        try:
            str_ser_obj:str                                             = record['train_data']['model']['model_checkpoint']
            check_point_obj:object                                      = serializer.decodeBinaryObj( str_ser_obj )
            slob:bytes                                                  = pickle.dumps(obj= check_point_obj)
            db_ready_object:Binary                                      = Binary(slob) 
            record['train_data']['model']['model_checkpoint']           = db_ready_object
        except Exception as exp:
            logger.error ("Record prelevato dalla coda avente un formato non riconosciuto dal sistema \n-> Record Mal Formato: {} \n-> Causa: {}".format( record , exp ))
            continue
       
        # [5] Scrittura Record sul DB
        insertion_ids:Union[ List[ObjectId] , Exception ]           = await pDBEngine.push( [record]  )
        if ExceptionManager.lookForExceptions ( insertion_ids ):
            logger.error ("Impossibile Scrivere sul DB :( \n-> Causa: {}".format( str( insertion_ids ) ))
        



async def launcher (pParams:tuple , pQueue:Queue) -> None:
    """
    # **launcher**

    Questa funzione permette di lanciare il processo che monitora la coda RabbitMQ "storageRecord".

    Tale coda conterra i nuovi record da scrivere nel DB Storage.

    Args:\n

        pParams        (tuple)              : parametri necessari all'event-sourcing e alla configurazione.
                                                La tupla contiene i seguenti oggetti:
                                                    - **ServiceConfig**
                                                    - **AutoLearnLogEntity**
                                                    - **KafkaEventStore**
                                                    - **EVENT_STORE_PARAMS**    : dict
                                                    - **Logger**

    Raises:\n
        Exception           : errore di connessione/scrittura/lettura dati con RabbitMQ o MongoDB o Kafka.
    """

    # [1] SetUp EventSourcing e Logging Locale
    cfg:ServiceConfig                                       = pParams[0]
    network_logger:AutoLearnLogEntity                       = pParams[1]
    event_store:KafkaEventStore                             = pParams[2]
    EVENT_STORE_PARAMS:dict                                 = pParams[3]
    logger:Logger                                           = pParams[4]

    await setUpEventSourcing( cfg.ENTITY_ID , event_store , network_logger , EVENT_STORE_PARAMS )

    # [2] SetUp RabbitMQ
    cons:RabbitConsumer                                     = RabbitConsumer(cfg.BROKER_LOGIN_TOKEN, cfg.QUEUE_NAME)
    outcome:Union[ None , Exception]                        = await cons.start()
    if ExceptionManager.lookForExceptions (outcome):
        err_msg:str                                         = "Impossibile connettersi con RabbitMQ, chiusura processo guard :( \n-> Causa: {}".format( str( outcome ) )
        logger.error (err_msg)

        await event_store.stop()
        raise (err_msg)
        exit( UNABLE_TO_CONNECT_TO_RABBIT_MQ )


    # [3] Connessione con Mongo
    engine:MongoEngine                                          = MongoEngine(cfg.DB_HOST_NAME, cfg.DB_PORT, cfg.DB_USER_NAME, cfg.DB_PASSWORD , cfg.DB_NAME, cfg.DB_COLLECTION   )

    outcome:Union[ None, Exception ]                            = engine.start()
    if ExceptionManager.lookForExceptions ( outcome  ):
        err_msg:str                                             = "Impossibile connettersi con MongoDB, chiusura processo guard :( \n-> Causa: {}".format( str( outcome ) )
        logger.error (err_msg)

        await cons.stop()
        await event_store.stop()
        raise (err_msg)
        exit( UNABLE_TO_CONNECT_TO_MONGO )


    # [4] Avvio Processo di Monitoraggio Coda
    await asyncio.create_task( monitor( pParams, cons , engine , pQueue) ) 

      
    # [5] Stop Connessione con RabbitMQ
    outcome:Union[ None , Exception]                         = await cons.stop()
    if ExceptionManager.lookForExceptions (outcome):
        err_msg:str                                          = "Impossibile chiudere connessione con RabbitMQ \n-> Causa: {}".format( str( outcome ) )
        logger.error (err_msg)

    
    # [6] Stop Connessione con MongoDB
    outcome:Union[None , Exception]                          = engine.stop()
    if ExceptionManager.lookForExceptions (outcome):
        err_msg:str                                          = "Impossibile chiudere connessione con MongoDB \n-> Causa: {}".format( str( outcome ) )
        logger.error (err_msg)


    # [7] Stop Connessione con Kafka
    outcome:Union[None , Exception]                          = await event_store.stop()
    if ExceptionManager.lookForExceptions (outcome):
        err_msg:str                                          = "Impossibile chiudere connessione con Kafka \n-> Causa: {}".format( str( outcome ) )
        logger.error (err_msg)

    
    # [8] Invio segnale cancel() a tutte le corutine ancora in esecuzione
    tasks:set                                                = [ task for task in asyncio.all_tasks() ]
    [ task.cancel() for task in tasks ]

    # [9] Stop Event-Loop
    loop:AbstractEventLoop                                   = asyncio.get_event_loop()
    loop.stop()


def guard () -> None:
    """
    # **guard**

    Questa funzione permette di far partire il processo di guard che permette di scrivere i record sul DB di Storage
    """
    # [0] Setup sistema
    params:tuple                    = set_up_guard()


    # [1] Modifica Event-Loop in modo da far chiudere l'applicativo di guard in maniera consona nel caso di segnale di terminazione 
    loop:AbstractEventLoop          = asyncio.get_event_loop()
    queue:Queue                     = asyncio.Queue()
    signals:tuple                   = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for sgn in signals:
        loop.add_signal_handler( sgn, lambda sgn = sgn : asyncio.create_task( shut_down_system( queue ) ) )


    # [2] Avvio Applicativo
    try:
        loop.create_task( launcher( params , queue ) )
        loop.run_forever()
    finally:
        loop.close()


async def view_experiments( pCfg:ServiceConfig , pLogger:Logger ) -> Union[ List[dict] , Exception ] :
    """
    # **view_experiments**

    Questa funzione restituisce tutti gli esperimenti presenti nel DB di Storage

    Args: \n
        pCfg            (ServiceConfig)     : oggetto che mantiene la configurazione dell'applicativo
        pLogger         (Logger)            : logger locale

    Returns:\n
        Union[ List[dict] , Exception ]     : record prelevati dal DB o eccezione

    Raises:\n
        Exception                           : eccezzione di connessione/disconnessione/lettura con MongoDB
    """

    serializer:NetworkSerializer                                = NetworkSerializer()

    # [1] Connessione con Mongo
    engine:MongoEngine                                          = MongoEngine(pCfg.DB_HOST_NAME, pCfg.DB_PORT, pCfg.DB_USER_NAME, pCfg.DB_PASSWORD , pCfg.DB_NAME, pCfg.DB_COLLECTION   )

    outcome:Union[ None, Exception ]                            = engine.start()
    if ExceptionManager.lookForExceptions ( outcome  ):
        err_msg:str                                             = "Impossibile connettersi con MongoDB :( \n-> Causa: {}".format( str( outcome ) )
        pLogger.error (err_msg)
        
        return outcome

    # [2] Query
    experiments:Union[ List[dict] , Exception ]                      = await engine.query( pQuery={} )
    for experiment in experiments:
        try:
            # Rendo esplicito il timestamp nel record
            experiment['timestamp']                                  = experiment['_id']
            del experiment['_id']

            #Serializzo l'oggetto del checkpoint in un formato adatto a viaggiare in rete
            model_ck:bytes                                           = experiment['train_data']['model']['model_checkpoint']
            model_obj:object                                         = pickle.loads( model_ck )
            model_obj_ready_for_net_transfer:str                     = serializer.encodeBinaryObj ( model_obj )
            experiment['train_data']['model']['model_checkpoint']    = model_obj_ready_for_net_transfer

        except Exception as exp:
            pLogger.error ("Record prelevato dal DB avente un formato non riconosciuto dal sistema \n-> Record Mal Formato: {} \n-> Causa: {}".format( experiment , exp ))
            return exp


    # [3] Stop Connessione con MongoDB
    outcome:Union[None , Exception]                              = engine.stop()
    if ExceptionManager.lookForExceptions (outcome):
        err_msg:str                                              = "Impossibile chiudere connessione con MongoDB \n-> Causa: {}".format( str( outcome ) )
        pLogger.error (err_msg)

    return { "experiments": experiments }