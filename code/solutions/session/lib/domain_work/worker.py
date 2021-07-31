"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 31/07/2021                       \n
@last-update            :  Sat 31/07/2021                       \n

Questo componente implementa una serie di utility necessarie al microservizio Session.

In particolar modo il componente affronta i seguenti 5 task:
    - Controllare messaggi nella coda sessionRecord ed eventualmente registrarli sul DB Session
    - Controllare messaggi nella coda sessionUpdate ed eventualmente aggiornare il corrispettivo record nel DB Session
    - Query su tutti i record del DB
    - Query su uno specifico record del DB Session
    - Archiviazione record sul DB di Storage
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
from pymongo.results                                        import InsertManyResult,UpdateResult

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
from ..rabbit_producer.RabbitProducer                       import RabbitProducer
from ..service_utility.utils                                import ser_model__net_2_db, ser_model__db_2_net


UNABLE_TO_CONNECT_TO_RABBIT_MQ:int      = 2
UNABLE_TO_CONNECT_TO_MONGO:int          = 3
SESSION_NOT_EXISTS:int                  = 4


async def shut_down_system( pQueue:Queue ) -> None:
    """
    # **shut_down_system**

    Questa funzione inserisce un messaggio nella coda che intima la corutine di update/record ad arrestarsi.

    Args:\n
        pQueue                      ( Queue )       : coda asincrona
    """
    await pQueue.put("exit")


async def session_record_guard (pParams:tuple, pRabbitConsumer:RabbitConsumer , pDBEngine:MongoEngine , pQueue:Queue) -> None:
    """
    # **session_record_guard**

    Questa funzione monitora la coda RabbitMQ "sessionRecord" e ogni volta che trova un record lo scrive sul DB di Session.


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

        pQueue              (Queue)             : coda utile per arrestare il guard

    Raises:\n
        Exception                               : errore di connessione/scrittura dati con RabbitMQ o MongoDB o Kafka.
    """
    network_logger:AutoLearnLogEntity                               = pParams[1]
    event_store:KafkaEventStore                                     = pParams[2]
    logger:Logger                                                   = pParams[4]

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
            logger.error ( "[RECORD_GUARD @ session_record_guard] Impossibile consumare messaggio dalla coda RabbitMQ \n-> Causa: {}".format( str( record ) ) )
            continue
        elif issubclass( type(record) , QueueEmpty ):
            continue
        
        current_time:int                                            = TimeStampManager.currentTimeStampInMS()


        # [2] Log su Event-Store
        event:DomainEvent                                           = make_behavioral_event(b"training" , current_time , "training" , "session" , "receive" , "async" , "train_data_record")
        outcome:Union[ None , Exception]                            = await network_logger.emit(event)

        if ExceptionManager.lookForExceptions (outcome):
            logger.error ( "[RECORD_GUARD @ session_record_guard] Impossibile Scrivere su Event-Store \n-> Causa: {}".format( str( outcome ) ) )


        # [4] Serializzo l'oggetto del checkpoint in binario utilizzando un formato compatibile con Mongo
        outcome:Union[ dict , Exception ]                           = ser_model__net_2_db(record )
        if ExceptionManager.lookForExceptions(record):
            logger.error ("[RECORD_GUARD] Record prelevato dalla coda avente un formato non riconosciuto dal sistema \n-> Record Mal Formato: {} \n-> Causa: {}".format( record , exp ))
            continue
        else:
            record                                                  = outcome
       

        # [5] Scrittura Record sul DB
        insertion_ids:Union[ List[ObjectId] , Exception ]           = await pDBEngine.push( [record]  )
        if ExceptionManager.lookForExceptions ( insertion_ids ):
            logger.error ("[RECORD_GUARD @ session_record_guard] Impossibile Scrivere sul DB :( \n-> Causa: {}".format( str( insertion_ids ) ))
        

async def session_update_guard (pParams:tuple, pRabbitConsumer:RabbitConsumer , pDBEngine:MongoEngine , pQueue:Queue) -> None:
    """
    # **session_update_guard**

    Questa funzione monitora la coda RabbitMQ "sessionUpdate" e ogni volta che trova un record lo sfrutta per aggiornarne un altro presente nel DB Session.


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

        pQueue              (Queue)             : coda utile per arrestare il guard

    Raises:\n
        Exception                               : errore di connessione/scrittura dati con RabbitMQ o MongoDB o Kafka.
    """
    network_logger:AutoLearnLogEntity                               = pParams[1]
    event_store:KafkaEventStore                                     = pParams[2]
    logger:Logger                                                   = pParams[4]

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
            logger.error ( "[UPDATE_GUARD @ session_update_guard] Impossibile consumare messaggio dalla coda RabbitMQ \n-> Causa: {}".format( str( record ) ) )
            continue
        elif issubclass( type(record) , QueueEmpty ):
            continue

        current_time:int                                            = TimeStampManager.currentTimeStampInMS()


        # [2] Log su Event-Store
        event:DomainEvent                                           = make_behavioral_event(b"evaluation" , current_time , "evaluation" , "session" , "receive" , "async" , "update_session")
        outcome:Union[ None , Exception]                            = await network_logger.emit(event)

        if ExceptionManager.lookForExceptions (outcome):
            logger.error ( "[UPDATE_GUARD @ session_update_guard] Impossibile Scrivere su Event-Store \n-> Causa: {}".format( str( outcome ) ) )


        # [3] Prelevo dal record l'id e il campo da aggiornare, fatto ciò costruisco i parametri di update
        query:dict      = { '_id' : record['_id'] }
        update_rule:dict = { "$set" : { "eval_data" : { "experiment_metrics" : record["eval_data"] } }  }
        
        # [4] Aggiornamento Record Record sul DB
        outcome:Union[UpdateResult, Exception]           = await pDBEngine.update ( query, update_rule )

        if ExceptionManager.lookForExceptions ( outcome ):
            logger.error ("[UPDATE_GUARD @ session_update_guard] Impossibile Aggiornare il record del DB :( \n-> Causa: {}".format( str( outcome ) ))

        if outcome.raw_result['nModified'] != 1 :
            logger.error ("[UPDATE_GUARD @ session_update_guard] Impossibile Aggiornare il record del DB :( \n-> Causa: {}".format( outcome.raw_result ))

        
async def launcher (pGuardType:str , pParams:tuple , pQueue:Queue) -> None:
    """
    # **launcher**

    Questa funzione permette di lanciare il processo che monitora la coda RabbitMQ "storageRecord".

    Tale coda conterra i nuovi record da scrivere nel DB Storage.

    Args:\n
        pGuardType      (str)               : tipo di guard da lanciare \n
                                              Opzioni:
                                                - **session_update_guard**
                                                - **session_record_guard**

        pParams        (tuple)              : parametri necessari all'event-sourcing e alla configurazione.
                                                La tupla contiene i seguenti oggetti:
                                                    - **ServiceConfig**
                                                    - **AutoLearnLogEntity**
                                                    - **KafkaEventStore**
                                                    - **EVENT_STORE_PARAMS**    : dict
                                                    - **Logger**

        pQueue              (Queue)         : coda utile per arrestare il guard

    Raises:\n
        Exception                           : errore di connessione/scrittura/lettura dati con RabbitMQ o MongoDB o Kafka.
    """

    # [1] SetUp EventSourcing e Logging Locale
    cfg:ServiceConfig                                           = pParams[0]
    network_logger:AutoLearnLogEntity                           = pParams[1]
    event_store:KafkaEventStore                                 = pParams[2]
    EVENT_STORE_PARAMS:dict                                     = pParams[3]
    logger:Logger                                               = pParams[4]

    await setUpEventSourcing( cfg.ENTITY_ID , event_store , network_logger , EVENT_STORE_PARAMS )

    # [2] SetUp RabbitMQ
    if pGuardType == "session_update_guard":
        cons:RabbitConsumer                                     = RabbitConsumer(cfg.BROKER_LOGIN_TOKEN, cfg.UPDATE_QUEUE)
    else:
        cons:RabbitConsumer                                     = RabbitConsumer(cfg.BROKER_LOGIN_TOKEN, cfg.RECORD_QUEUE)

    outcome:Union[ None , Exception]                            = await cons.start()
    if ExceptionManager.lookForExceptions (outcome):
        err_msg:str                                             = "[{} @ launcher] Impossibile connettersi con RabbitMQ, chiusura processo guard :( \n-> Causa: {}".format(pGuardType, str( outcome ) )
        logger.error (err_msg)

        await event_store.stop()
        raise (err_msg)
        exit( UNABLE_TO_CONNECT_TO_RABBIT_MQ )


    # [3] Connessione con Mongo
    engine:MongoEngine                                          = MongoEngine(cfg.DB_HOST_NAME, cfg.DB_PORT, cfg.DB_USER_NAME, cfg.DB_PASSWORD , cfg.DB_NAME, cfg.DB_COLLECTION   )

    outcome:Union[ None, Exception ]                            = engine.start()
    if ExceptionManager.lookForExceptions ( outcome  ):
        err_msg:str                                             = "[{} @ launcher] Impossibile connettersi con MongoDB, chiusura processo guard :( \n-> Causa: {}".format(pGuardType , str( outcome ) )
        logger.error (err_msg)

        await cons.stop()
        await event_store.stop()
        raise (err_msg)
        exit( UNABLE_TO_CONNECT_TO_MONGO )


    # [4] Avvio Processo di Monitoraggio Coda
    if pGuardType == "session_update_guard":
        await asyncio.create_task( session_update_guard( pParams, cons , engine , pQueue) ) 
    else:
        await asyncio.create_task( session_record_guard( pParams, cons , engine , pQueue) ) 

    
    # [5] Stop Connessione con RabbitMQ
    outcome:Union[ None , Exception]                            = await cons.stop()
    if ExceptionManager.lookForExceptions (outcome):
        err_msg:str                                             = "[{} @ launcher] Impossibile chiudere connessione con RabbitMQ \n-> Causa: {}".format( pGuardType ,str( outcome ) )
        logger.error (err_msg)

    
    # [6] Stop Connessione con MongoDB
    outcome:Union[None , Exception]                             = engine.stop()
    if ExceptionManager.lookForExceptions (outcome):
        err_msg:str                                             = "[{} @ launcher] Impossibile chiudere connessione con MongoDB \n-> Causa: {}".format( pGuardType ,str( outcome ) )
        logger.error (err_msg)


    # [7] Stop Connessione con Kafka
    outcome:Union[None , Exception]                             = await event_store.stop()
    if ExceptionManager.lookForExceptions (outcome):
        err_msg:str                                             = "[{} @ launcher] Impossibile chiudere connessione con Kafka \n-> Causa: {}".format(pGuardType ,str( outcome ) )
        logger.error (err_msg)

    
    # [8] Invio segnale cancel() a tutte le corutine ancora in esecuzione
    tasks:set                                                   = [ task for task in asyncio.all_tasks() ]
    [ task.cancel() for task in tasks ]

    # [9] Stop Event-Loop
    loop:AbstractEventLoop                                      = asyncio.get_event_loop()
    loop.stop()


def guard (pType:str) -> None:
    """
    # **guard**

    Questa funzione permette di far partire i processi di guard che permettono di aggiornare/scrivere i record nel DB di Session

    Args:\n
        pType               (str)       : tipo di guard da lanciare \n
                                          Opzioni:
                                            - **session_update_guard**
                                            - **session_record_guard**
    """
    # [0] Setup sistema
    params:tuple                    = set_up_guard(pType)


    # [1] Modifica Event-Loop in modo da far chiudere l'applicativo di guard in maniera consona nel caso di segnale di terminazione 
    loop:AbstractEventLoop          = asyncio.get_event_loop()
    queue:Queue                     = asyncio.Queue()
    signals:tuple                   = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for sgn in signals:
        loop.add_signal_handler( sgn, lambda sgn = sgn : asyncio.create_task( shut_down_system( queue ) ) )


    # [2] Avvio Applicativo
    try:
        loop.create_task( launcher( pType ,  params , queue ) )
        loop.run_forever()
    finally:
        loop.close()


async def view_sessions( pCfg:ServiceConfig , pLogger:Logger ) -> Union[ List[dict] , Exception ] :
    """
    # **view_sessions**

    Questa funzione restituisce tutti gli esperimenti presenti nel DB di Session

    Args: \n
        pCfg            (ServiceConfig)     : oggetto che mantiene la configurazione dell'applicativo
        pLogger         (Logger)            : logger locale

    Returns:\n
        Union[ List[dict] , Exception ]     : record prelevati dal DB o eccezione

    Raises:\n
        Exception                           : eccezzione di connessione/disconnessione/lettura con MongoDB
    """

    # [1] Connessione con Mongo
    engine:MongoEngine                                          = MongoEngine(pCfg.DB_HOST_NAME, pCfg.DB_PORT, pCfg.DB_USER_NAME, pCfg.DB_PASSWORD , pCfg.DB_NAME, pCfg.DB_COLLECTION   )

    outcome:Union[ None, Exception ]                            = engine.start()
    if ExceptionManager.lookForExceptions ( outcome  ):
        err_msg:str                                             = "[REST-API @ view_sessions] Impossibile connettersi con MongoDB :( \n-> Causa: {}".format( str( outcome ) )
        pLogger.error ( str(err_msg) )
        
        return outcome

    # [2] Query
    experiments:Union[ List[dict] , Exception ]                 = await engine.query( pQuery={} )
    for experiment in experiments:
        # Rendo esplicito il timestamp nel record
        experiment['timestamp']                                 = experiment['_id']
        del experiment['_id']

        #Serializzo l'oggetto del checkpoint in un formato adatto a viaggiare in rete
        outcome:Union[ dict , Exception]                        = ser_model__db_2_net(experiment)
        if ExceptionManager.lookForExceptions(outcome):
            pLogger.error ("[REST-API @ view_sessions] Record prelevato dal DB avente un formato non riconosciuto dal sistema \n-> Record Mal Formato: {} \n-> Causa: {}".format( experiment , str( outcome ) ))
            return outcome
            

    # [3] Stop Connessione con MongoDB
    outcome:Union[None , Exception]                              = engine.stop()
    if ExceptionManager.lookForExceptions (outcome):
        err_msg:str                                              = "[REST-API @ view_sessions] Impossibile chiudere connessione con MongoDB \n-> Causa: {}".format( str( outcome ) )
        pLogger.error ( str(err_msg) )

    return { "experiments": experiments }


async def check_session_exist (pIdSession:int , pLogger:Logger , pDB:MongoEngine ) -> Union[ dict , int , Exception ]:
    """
    # **check_session_exist**

    Questo metodo permette di verificare se una specifica sessione esiste sul DB

    Args:\n
        pIdSession                  (int)           : id sessione che si vuole ricercare nel DB
        pLogger                     (Logger)        : logger locale
        pDB                         (MongoEngine)   : oggetto che si interfaccia col DB

    Returns:\n
        Union[ dict , int , Exception ]

    Raises:\n
        Exception                                   : errore di connessione con MongoDB
    """
    query:List[dict]                                    = { "_id" : pIdSession }

    outcome:Union[  List[dict] , Exception ]            = await pDB.query ( query )
    if ExceptionManager.lookForExceptions (outcome):
        pLogger.error("[REST-API @ check_session_exist] Impossibile controllare se esiste il record di session sul DB \n-> Causa: {}".format( str( outcome ) ))
        return outcome

    if len(query) > 1:
        pLogger.error("[REST-API @ check_session_exist] Trovati record con chiave '_id' duplicata \n-> Lista Duplicati: {}".format( str( outcome ) ))


    return outcome[0] if outcome != [] and len(outcome)==1 else SESSION_NOT_EXISTS


async def decryptIdSession ( pIdSession:str , pSerializer:NetworkSerializer , pLogger:Logger , pDB:MongoEngine) -> Union [ int , Exception , bool ]:
    """
    # **decryptIdSession**

    Questa funzione permette di verificare se la richiesta di modifica di un record di sessione sia leggittima o meno.

    Args:\n
        pIdSession              (str)                   : id di sessione cifrato
        pSerializer             (NetworkSerializer)     : serializzatore
        pLogger                 (Logger)                : logger locale
        pDB                     (MongoEngine)           : oggetto che si interfaccia col DB

    Returns:\n
        Union [ int , Exception , bool ]                : FALSO se il messaggio è stato cifrato con una chiave non autentica

    Raises:\n
        Exception                                       : eccezione derivata da problemi di connessione con MongoDB oppure problemi di decifratura
    """
    decrypted_data:Union[ str , Exception]                           = pSerializer.decryptField(pIdSession)
    if ExceptionManager.lookForExceptions(decrypted_data):
        pLogger.error("[REST-API @ decryptIdSession] Impossibile decodificare i dati \n-> Causa: {}".format( str( decrypted_data) ))
        return decrypted_data

    #[1] Tentativo di casting ad intero che sarebbe il tipo degli id presenti nella collezione Sessions del DB Session
    try:
        decrypted_id_session:int                                      = int(decrypted_data)
    except Exception as exp:
        return False


    # [2] Controllo Esistenza Sessione sul DB
    outcome:Union[ dict , int , Exception ]                           = await check_session_exist(decrypted_id_session , pLogger, pDB)

    # [3] Restituisco risultato al chiamante
    if ExceptionManager.lookForExceptions(outcome) == False: 
        if type(outcome) == int and outcome == SESSION_NOT_EXISTS:
            return False
        else:
            return decrypted_id_session
    else:
        return outcome


async def queryOneRecord (pIdSession:int , pLogger:Logger , pDB:MongoEngine) -> Union[ dict , int , Exception ]:
    """
    # **queryOneRecord**

    Questo metodo permette di estrarre uno specifico record dal DB Session

    Args:\n
        pIdSession                  (int)               : id di sessione associato al record che si vuole recuperare
        pLogger                     (Logger)            : logger locale
        pDB                         (MongoEngine)       : oggetto che gestisce il database

    Returns:\n
        Union[ dict , int , Exception ] 

    Raises:\n
        Exception                                        : eccezione derivata da problemi di connessione con Mongo oppure dalla presenza di un record corrotto avente l'id sessione uguale a quello passato dal chiamante
    """
    outcome:Union[ dict , int , Exception ]                     = await check_session_exist(pIdSession , pLogger , pDB)
    
    # [1] Se è accaduta un eccezione, lo segnalo al chiamante
    if ExceptionManager.lookForExceptions (outcome):
        return outcome

    # [2] Se il record non è stato trovato nel DB, lo segnalo al chiamante
    if outcome == SESSION_NOT_EXISTS:
        return SESSION_NOT_EXISTS

    # [3] Tentativo serializzazione Modello ML presente nel record in un formato adatto a viaggiar in rete
    ser_outcome:Union[ dict , Exception ]                       = ser_model__db_2_net( outcome )
    if ExceptionManager.lookForExceptions(ser_outcome):
        pLogger.error("[REST-API @ queryOneRecord] Record del DB corrotto \n->Causa: {}".format( str( ser_outcome ) ))
        return ser_outcome

    #Rendo esplicito il timestamp nel record
    ser_outcome['timestamp']                                    = ser_outcome['_id']
    del ser_outcome['_id']


    return ser_outcome


async def save_session (pIdSession:int , pLogger:Logger , pDB:MongoEngine , pProducer:RabbitProducer ) -> Union[ Exception , int , None]:
    """
    # **save_session**

    Questa funzione permette di salvare un record del DB Session nello storage permanente del Sistema.

    Args:\n
        pIdSession                      (int)            : id del record di sessione da salvare nello Storage permantne
        pLogger                         (Logger)         : logger locale del sistema
        pDB                             (MongoEngine)    : componente che si interfaccia col DB
        pProducer                       (RabbitProducer) : produttore RabbitMQ

    Returns:\n
        Union[ Exception , int , None]

    Raises:\n
        Exception                                         : eccezione derivata da problemi di connessione con MongoDB/RabbitMQ oppure dalla presenza di record mal formati nel DB
    """

    outcome: Union[ dict , int , Exception ]               = await check_session_exist(pIdSession , pLogger , pDB)

    # [1] Se è accaduta un eccezione, lo segnalo al chiamante
    if ExceptionManager.lookForExceptions (outcome):
        return outcome

    # [2] Se il record non è stato trovato nel DB, lo segnalo al chiamante
    if outcome == SESSION_NOT_EXISTS:
        return SESSION_NOT_EXISTS

    # [3] Tentativo serializzazione Modello ML presente nel record in un formato adatto a viaggiar in rete
    ser_outcome:Union[ List[dict] , Exception ]                 = ser_model__db_2_net(outcome )
    if ExceptionManager.lookForExceptions(ser_outcome):
        pLogger.error("[REST-API @ save_session] Record corrotto prelevato dal DB \n-> Causa: {}".format( str( ser_outcome )))
        return ser_outcome

    # [4] Pubblicazione Messaggio di "archive_data" sulla coda storageRecord
    pubblish_outcome:Union[DeliveredMessage, Exception]         = await pProducer.pubblish(ser_outcome)
    if ExceptionManager.lookForExceptions( pubblish_outcome ):
        pLogger.error("[REST-API @ save_session] Impossibile pubblicare messaggio su RabbitMQ\n-> Causa: {}".format( str( pubblish_outcome ) ) )
        return pubblish_outcome


    # [5] Eliminazione record appena archiviato dal DB di Session
    try:
        await pDB._db[ pDB._collectionName ].delete_many( { "_id" : pIdSession } )
    except Exception as exp:
        pLogger.error("[REST-API @ save_session] Impossibile eliminare record di Sessione dal DB Session \n-> Causa: {}".format( str( exp ) ) )
        return exp


    