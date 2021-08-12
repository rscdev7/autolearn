"""
@author           	    :  rscalia                              \n
@build-date             :  Mon 09/08/2021                       \n
@last-update            :  Thu 10/08/2021                       \n

Questo modulo permette di svolgere il domain work del microservizio Evaluation
"""

# [1] Import Modelli
from ..concrete_ml_engine.DecisionTreePandasDataset         import DecisionTreePandasDataset
from ..concrete_ml_engine.RandomForestPandasDataset         import RandomForestPandasDataset
from ..concrete_ml_engine.SVMPandasDataset                  import SVMPandasDataset
from ..concrete_ml_engine.LogisticRegressorPandasDataset    import LogisticRegressorPandasDataset
from ..concrete_ml_engine.NaiveBayesPandasDataset           import NaiveBayesPandasDataset

# [2] Import dataset
from ..concrete_ml_engine.IrisFisherDataset                 import IrisFisher
from ..dataset_pipelines.datasets_load_pipelines            import build_iris_dataset_load_pipeline

from ..concrete_ml_engine.HeightWeightDataset               import HeightWeightDataset
from ..dataset_pipelines.datasets_load_pipelines            import build_height_weight_dataset_load_pipeline

from ..abstract_ml_engine.Dataset                           import Dataset
from ..abstract_ml_engine.Model                             import Model
from ..abstract_streaming_pipeline.GeneralStreamingPipe     import StreamingPipe
from ..concrete_ml_engine.HeightWeightDataset               import HeightWeightDataset
from ..concrete_ml_engine.IrisFisherDataset                 import IrisFisher

from typing                                                 import List, Union, Dict, Tuple
from ..exception_manager.ExceptionManager                   import ExceptionManager
from ..http_engine.HTTPEngine                               import HTTPEngine
from ..time_stamp_manager.TimeStampManager                  import TimeStampManager
from ..event_sourcing_utility.event_sourcing_utility        import make_behavioral_event
from ..service_config.ServiceConfig                         import ServiceConfig
from ..concrete_event_sourcing.AutoLearnLogEntity           import AutoLearnLogEntity
from ..concrete_event_sourcing.KafkaEventStore              import KafkaEventStore
import asyncio
from asyncio                                                import AbstractEventLoop
from concurrent.futures                                     import ProcessPoolExecutor
from ..logger.Logger                                        import Logger
import                                                      os
from ..rabbit_producer.RabbitProducer                       import RabbitProducer
from ..network_serializer.NetworkSerializer                 import NetworkSerializer
from aiormq.types                                           import DeliveredMessage


def decryptSessId (pCryptSessId:str , pLogger:Logger  ) -> Union [ int , Exception ]:
    """
    # **decryptSessId**
    
    Questa funzione permette di decifrare l'id sessione passato dal client

    Args:\n
        pCryptSessId         (str)                  : id di sessione cifrato
        pLogger              (Logger)               : logger locale dell'applicativo

    Returns:\n
        Union [ int , Exception ]

    Raises:\n
        Exception                                   : eccezione durante la decifratura della chiave
    """
    serializer:NetworkSerializer                = NetworkSerializer()

    # [1] Lettura chiave da Disco
    outcome:Union[ None , Exception]            = serializer.readKeyFromFile()
    if ExceptionManager.lookForExceptions(outcome):
        pLogger.error("[ REST-API @ decryptSessId] Impossibile caricare chiave crittografica da disco \n-> Causa: {}".format( str( outcome ) ))
        return outcome
    
    # [2] Decrypt della chiave
    outcome:Union[ str , Exception]             = serializer.decryptField(pCryptSessId)
    if ExceptionManager.lookForExceptions(outcome):
        pLogger.error("[ REST-API @ decryptSessId] Impossibile decrifrare ID di Sessione \n-> Causa: {}".format( str( outcome ) ))
        return outcome
    
    # [3] Tentativo di Casting ad Intero dell'ID Session
    try:
        sess_id:int     = int( outcome )
    except Exception as exp:
        pLogger.error("[ REST-API @ decryptSessId] Impossibile effettuare casting ad Intero dell'ID Sessione \n-> Causa: {}".format( str( exp ) ))
        return exp

    return sess_id


async def checkTrainingExist (pIdSession:int , pCfg:ServiceConfig , pNetLogger:AutoLearnLogEntity , pLogger:Logger) -> Union[ dict , Exception, Tuple[ Exception , int]]:
    """
    # **checkTrainingExist**

    Questa funzione permette di verificare se un determinato training è presente nel DB di Sessione

    Args:\n
        pIdSession                  (int)                   : id sessione del training che si vuole ricercare
        pCfg                        (ServiceConfig)         : configurazione dell'applicativo
        pNetLogger                  (AutoLearnLogEntity)    : logger comportamentale del microservizio
        pLogger                     (Logger)                : logger locale

    Returns:\n
        Union[ dict , Exception, Tuple[ Exception , int]]

    Raises:\n
        Exception                                           : eccezione nella comunicazione col microservizio Session 
    """
    
    # [1] Costruzione record da inoltrare al microservizio Session
    serializer:NetworkSerializer                                                     = NetworkSerializer()
    request:dict                                                                     = { "id_rec" : pIdSession }


    # [2] Inoltro richiesta a Session
    engine:HTTPEngine                                                                = HTTPEngine(60)
    engine.startAsync()

    current_time:int                                                                 = TimeStampManager.currentTimeStampInMS()
    query_record_outcome:Union[Dict[int, dict], Exception, Tuple[Exception, int]]    = await engine.postAsync(pCfg.QUERY_RECORD_URL , request)
    await engine.closeAsync()

    #[3] Logging su Event-Store richiesta effettuata a Sessione
    sess_exist_req:DomainEvent                                                       = make_behavioral_event( b"session" , current_time , "evaluation" , "session" , "send" , "async" , "query_record")
    
    outcome:Union[ None , Exception]                                                 = await pNetLogger.emit(sess_exist_req)
    if ExceptionManager.lookForExceptions(outcome):
        pLogger.error("[REST-API @ checkTrainingExist] Impossibile scrivere evento Richiesta Dati Sessione \n-> Causa: {}".format( str( outcome ) ))


    # [4] Verifica Dati Ricevuti - Casi Errore Connessione
    current_time:int                                                                 = TimeStampManager.currentTimeStampInMS()
    if ExceptionManager.lookForExceptions(query_record_outcome):

        pLogger.error("[REST-API @ checkTrainingExist] Errore nella connessione col microservizio Session \n-> Causa: {}".format( str( query_record_outcome ) ))


        #[4.1] Logging su Event-Store risultato ricezione ID Sessione
        sess_exist_ans:DomainEvent                                                       = make_behavioral_event( b"session" , current_time , "session" , "evaluation" , "receive" , "async" , "internal_server_error")
        
        outcome:Union[ None , Exception]                                                 = await pNetLogger.emit(sess_exist_ans)
        if ExceptionManager.lookForExceptions(outcome):
            pLogger.error("[REST-API @ checkTrainingExist] Impossibile scrivere evento Ricezione Dati Sessione Errata \n-> Causa: {}".format( str( outcome ) ))

        #[4.1] Logging su Event-Store risultato ricezione ID Sessione al Client
        sess_exist_ans:DomainEvent                                                       = make_behavioral_event( b"client" , current_time , "evaluation" , "client" , "send" , "async" , "internal_server_error")
        
        outcome:Union[ None , Exception]                                                 = await pNetLogger.emit(sess_exist_ans)
        if ExceptionManager.lookForExceptions(outcome):
            pLogger.error("[REST-API @ checkTrainingExist] Impossibile scrivere evento Notifica Ricezione Dati Sessione Errata \n-> Causa: {}".format( str( outcome ) ))


        return query_record_outcome


    if type(query_record_outcome) == tuple:
        pLogger.error("[REST-API @ checkTrainingExist] Errore nella connessione col microservizio Session \n-> Causa: {} \n-> Status Code: {}".format( str( query_record_outcome[0] ) , query_record_outcome[1] ))


        #[4.1] Logging su Event-Store risultato ricezione ID Sessione
        sess_exist_ans:DomainEvent                                                       = make_behavioral_event( b"session" , current_time , "session" , "evaluation" , "receive" , "async" , "internal_server_error")
        
        outcome:Union[ None , Exception]                                                 = await pNetLogger.emit(sess_exist_ans)
        if ExceptionManager.lookForExceptions(outcome):
            pLogger.error("[REST-API @ checkTrainingExist] Impossibile scrivere evento Ricezione Dati Sessione Errata \n-> Causa: {}".format( str( outcome ) ))

        #[4.2] Logging su Event-Store risultato ricezione ID Sessione al Client
        sess_exist_ans:DomainEvent                                                       = make_behavioral_event( b"client" , current_time , "evaluation" , "client" , "send" , "async" , "internal_server_error")
        
        outcome:Union[ None , Exception]                                                 = await pNetLogger.emit(sess_exist_ans)
        if ExceptionManager.lookForExceptions(outcome):
            pLogger.error("[REST-API @ checkTrainingExist] Impossibile scrivere evento Notifica Ricezione Dati Sessione Errata \n-> Causa: {}".format( str( outcome ) ))


        return query_record_outcome

    
    # [5] Ritorno risultato al chiamante
    session_record:dict                                                                  = query_record_outcome['payload']

    # [5.1] Verifica Errori Semantici sulla richiesta
    if type(session_record) == dict and "message" in session_record.keys() and session_record['message'] ==  "session_not_exists":
        msg:str                 = "session_not_exists"

    elif type(session_record) == dict and "message" in session_record.keys():

        pLogger.error("[REST-API @ checkTrainingExist] Errore nell'elaborazione della richiesta lato Session \n-> Causa: {}".format( session_record['message']  ))

        msg:str                 = "internal_server_error"

    else:
        msg:str                 = "eval_dto"


    #[5.2] Log Ricezione dati da Session
    sess_exist_ans:DomainEvent                                                       = make_behavioral_event( b"session" , current_time , "session" , "evaluation" , "receive" , "async" , msg)
        
    outcome:Union[ None , Exception]                                                 = await pNetLogger.emit(sess_exist_ans)
    if ExceptionManager.lookForExceptions(outcome):
        pLogger.error("[REST-API @ checkTrainingExist] Impossibile scrivere evento Ricezione Dati Sessione \n-> Causa: {}".format( str( outcome ) ))


    #[5.3] Log Risultato Finale Operazioni col Client
    if msg == "eval_dto":
        msg = "req_accepted"
    
    sess_exist_ans:DomainEvent                                                       = make_behavioral_event( b"client" , current_time , "evaluation" , "client" , "send" , "async" , msg)
            
    outcome:Union[ None , Exception]                                                 = await pNetLogger.emit(sess_exist_ans)
    if ExceptionManager.lookForExceptions(outcome):
        pLogger.error("[REST-API @ checkTrainingExist] Impossibile scrivere evento Notifica Ricezione Dati Sessione \n-> Causa: {}".format( str( outcome ) ))


    return session_record


async def evaluate_model(pRecord:dict, pCfg:ServiceConfig , pNetLogger:AutoLearnLogEntity , pLogger:Logger , pEventStore:KafkaEventStore) -> None:
    """
    # **evaluate_model**

    Questa funzione permette di valutare un Modello di ML precedentemente addestrato e di archiviarne il risultato nell'apposito record di sessione

    Args:\n
        pRecord                             (dict)                  : record di sessione contenente il modello di ML da valutare    
        pCfg                                (ServiceConfig)         : configurazione dell'applicativo
        pNetLogger                          (AutoLearnLogEntity)    : logger comportamental applicativo
        pLogger                             (Logger)                : logger locale applicativo
        pEventStore                         (KafkaEventStore)       : oggetto che si interfaccia con l'event-store

    Raises:\n
        Exception                                                   : eccezione scaturita da errori nella fase di evaluation del modello oppure dall'assenza del dataset su disco oppuew da problemi con la connessione col Message Broker
    """
    # [1] Deserializzo Checkpoint
    serializer:NetworkSerializer                        = NetworkSerializer()
    loop:AbstractEventLoop                              = asyncio.get_event_loop()
    ml_model:object                                     = serializer.decodeBinaryObj(pRecord['train_data']['model']['model_checkpoint'] )

    # [1.1] Controllo buona riuscita deserializzazione Modello
    if type(ml_model) == str:
        pLogger.error("[REST-API @ evaluate_model] Impossibile deserializzare checkpoint \n-> Causa: {}".format( str( ml_model ) ))
        return "deserialize_error"
    

    # [2] Avvio Evaluation
    choosen_model:str                                   = pRecord['train_data']['model']['model_name'] 
    pool:ProcessPoolExecutor                            = ProcessPoolExecutor(1)

    metrics_outcome:Union[List[dict], str]              = await loop.run_in_executor( pool, ev_model , choosen_model , ml_model , pRecord['train_data']['dataset'] , { "height_weight_dataset" : pCfg.HEIGHT_WEIGHT_DATA_PATH } )


    # [3] Retrieve Risultati Evaluation
    if type(metrics_outcome) != str:

        # [1] Scrittura Evaluation Modello su un apposito record di aggiornamento
        update_record:dict                            = {}
        update_record['_id']                          = pRecord['timestamp']
        update_record['eval_data']                    = []
        for metric_outcome in metrics_outcome:
            update_record['eval_data'].append(metric_outcome)


        # [2] Avvio RabbitMQ
        pr:RabbitProducer                               = RabbitProducer(pCfg.QUEUE,pCfg.BROKER_LOGIN_TOKEN)
        res:Union[None , Exception]                     = await pr.start()
        if ExceptionManager.lookForExceptions(res):
            pLogger.error("[ REST-API @ evaluate_model] Errore nella connessione con RabbitMQ \n-> Causa: {}".format( str( res ) ) )
            return


        # [3] Pubblicazione messaggio aggiornamento
        res:Union[DeliveredMessage, Exception]          = await pr.pubblish( update_record  )
        if ExceptionManager.lookForExceptions(res):
            pLogger.error("[ REST-API @ evaluate_model] Errore nel pubblicare messaggi nella coda RabbitMQ \n-> Causa: {}".format( str( res ) ) )
            return


        # [4] Prelievo tempo invio messaggio
        current_time:int                                = TimeStampManager.currentTimeStampInMS()


        # [5] Stop Produttore RabbitMQ
        res:Union[None , Exception]                     = await pr.stop()
        if ExceptionManager.lookForExceptions(res):
            pLogger.error("[ REST-API @ evaluate_model] Errore nella chiusura della connessione con RabbitMQ \n-> Causa: {}".format( str( res ) ) )


        # [6] Logging comunicazione con Session in merito all'aggiornamento del record
        sess_update_req:DomainEvent                                                      = make_behavioral_event( b"session" , current_time , "evaluation" , "session" , "send" , "async" , "update_session")
        
        outcome:Union[ None , Exception]                                                 = await pNetLogger.emit(sess_update_req)
        if ExceptionManager.lookForExceptions(outcome):
            pLogger.error("[REST-API @ evaluate_model] Impossibile scrivere evento Invio Update Record a Session \n-> Causa: {}".format( str( outcome ) ))
    
    
    # [4] Chiusura Connessione con Event Store
    outcome:Union[ None , Exception]     = await pEventStore.stop()
    if ExceptionManager.lookForExceptions(outcome):
        pLogger.error("[REST-API @ evaluate_model] Impossibile chiudere connessione con Event-Store \n-> Causa: {}".format( str( outcome ) ))


def ev_model (pModelType:str , pModelImpl:object , pDatasetInfo:dict , pDataPath:dict) -> Union [ List[dict] , str  ]:
    """
    # **ev_model**

    Questa funzione permette di valutare un Modello di ML

    Args:\n
        pModelType                  (str)       : nome del Modello
        pModelImpl                  (object)    : oggetto rappresentante l'implementazione del Modello da valutare
        pDatasetInfo                (dict)      : informazioni sul dataset su cui valutare il Modello
        pDataPath                   (dict)      : path al dataset
                                                  Formato:\n
                                                    - **height_weight_dataset** : str
    Returns:\n
        Union [ List[dict] , str  ]             : metriche di valutazione oppure eccezione sotto forma di messaggio d'errore testuale

    Raises:\n   
        Exception                               : errore nella valutazione del modello di ML
    """
    # [1] Setup Logger
    LOGGER_NAME:str                                     = "evaluation_evaluator"+str ( os.getpid() )
    LOG_PATH:str                                        = "./log"

    #[2] Costruzione Logger per Computazioni Locali del Microservizio
    logger:Logger                                       = Logger(pName=LOGGER_NAME, pLogPath=LOG_PATH)
    logger.start()

    # [3] Caricamento Dataset in memoria
    choosen_dataset:str                                 = pDatasetInfo['dataset_name']
    seed:int                                            = pDatasetInfo['split_seed']
    split_test:float                                    = pDatasetInfo['split_test']

    try:

        if choosen_dataset == "Iris-Fisher":

            dataset:Union[ object , Exception]          = load_iris(seed , split_test , logger)
            if ExceptionManager.lookForExceptions(dataset):
                logger.error("[ REST-API @ ev_model] Errore nel caricamento del dataset Iris \n-> Causa: {}".format( str( dataset ) ) )
                return "data_load_error"
            
        elif choosen_dataset == "Height-Weight Dataset":
            dataset:HeightWeightDataset                 = load_height_weight(pDataPath['height_weight_dataset'] , seed , split_test , logger)
            
            if ExceptionManager.lookForExceptions(dataset):
                logger.error("[ REST-API @ ev_model] Errore nel caricamento del dataset Height-Weight \n-> Causa: {}".format( str( dataset ) ) )
                return "data_load_error"

        else:
            raise ValueError("[ REST-API @ ev_model] Il dataset scelto non è presente nel Catalogo")

    except Exception as exp:
        logger.error("[ REST-API @ ev_model] Il dataset scelto non è presente nel Catalogo")
        return str( exp)


    #[4] Prelievo Modello Opportuno in base al nome
    try:
        if    pModelType == "SVM":
            model:Model                                 = SVMPandasDataset()
        elif        pModelType == "DecisionTree":
            model:Model                                 = DecisionTreePandasDataset()
        elif        pModelType == "RandomForest":
            model:Model                                 = RandomForestPandasDataset()
        elif        pModelType == "LogisticRegressor":
            model:Model                                 = LogisticRegressorPandasDataset()
        elif        pModelType == "Naive-Bayes":
            model:Model                                 = NaiveBayesPandasDataset()

        else:
            raise ValueError("Il Modello scelto non è presente nel Catalogo")
    except Exception as exp:
        logger.error("[ REST-API @ ev_model] Il Modello scelto non è presente nel Catalogo")
        return str( exp )


    #[5] SetUp Modello
    outcome:Union[ None , Exception ]                    = model.setUp()
    if ExceptionManager.lookForExceptions(outcome):
        logger.error("[ REST-API @ ev_model] Impossibile effettuare setup modello di ML \n-> Causa: {}".format( str(outcome) ))
        return str(outcome)

    outcome:Union[ None , Exception ]                    = model.loadCheckPoint( {'model' : pModelImpl } )
    if ExceptionManager.lookForExceptions(outcome):
        logger.error("[ REST-API @ ev_model] Impossibile effettuare load checkpoint modello di ML \n-> Causa: {}".format( str(outcome) ))
        return str(outcome)

    # [6] valuation Modello
    outcome:Union[ None , Exception ]                    = model.evaluate(dataset)
    if ExceptionManager.lookForExceptions(outcome):
        logger.error("[ REST-API @ ev_model] Impossibile effettuare evaluation modello di ML \n-> Causa: {}".format( str(outcome) ))
        return str(outcome)

    return outcome


def load_iris(pSeed:int , pSplit:float , pLogger:Logger ) -> Union [ object , Exception ]:
    """
    # **load_iris**

    Questa funzione permette di caricare in memoria il dataset Iris

    Args:\n
        pSeed           (int)       : seme per gli algoritmi random
        pSplit          (float)     : percentuale dati test-set
        pLogger         (Logger)    : logger locale

    Returns:\n
        Union [ object , Exception ]

    Raises:\n
        Exception                   : eccezione durante il caricamento del dataset
    """
    load_pipeline:StreamingPipe             = build_iris_dataset_load_pipeline( pSplit , pSeed )
    iris_dataset:IrisFisher                 = IrisFisher()
    iris_dataset.setUp(load_pipeline)

    outcome:Union[ None , Exception]        = iris_dataset.load()
    if ExceptionManager.lookForExceptions( outcome ):
        pLogger.error("[ REST-API @ load_iris] Errore nell'applicazione della pipeline di caricamento del dataset Iris \n-> Causa: {}".format( str( outcome ) ) )
        return outcome

    return iris_dataset


def load_height_weight(pDataPath:str , pSeed:int , pSplit:float , pLogger:Logger) -> Union [ object , Exception ]:
    """
    # **load_height_weight**

    Questa funzione permette di caricare in memoria il dataset HeightWeight

    Args:\n
        pDataPath       (str)       : path del dataset 
        pSeed           (int)       : seme per gli algoritmi random
        pSplit          (float)     : percentuale dati test-set
        pLogger         (Logger)    : logger locale

    Returns:\n
        Union [ object , Exception ]

    Raises:\n
        Exception                   : eccezione durante il caricamento del dataset
    """
    load_pipeline:StreamingPipe             = build_height_weight_dataset_load_pipeline(pDataPath, pSplit , pSeed)
    hw_dataset:HeightWeightDataset          = HeightWeightDataset()
    hw_dataset.setUp(load_pipeline)

    outcome:Union[ None , Exception]        = hw_dataset.load()
    if ExceptionManager.lookForExceptions( outcome ):
        pLogger.error("[ REST-API @ load_height_weight] Errore nell'applicazione della pipeline di caricamento del dataset Height Weight \n-> Causa: {}".format( str( outcome ) ) )
        return outcome

    return hw_dataset