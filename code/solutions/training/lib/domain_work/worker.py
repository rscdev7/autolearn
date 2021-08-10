"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 08/08/2021                       \n
@last-update            :  Thu 10/08/2021                       \n

Questo modulo permette di svolgere il domain work del microservizio Training
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
from logging                                                import Logger
from ..exception_manager.ExceptionManager                   import ExceptionManager
from ..data_validator.TrainRequestValidator                 import TrainRequestValidator
from ..http_engine.HTTPEngine                               import HTTPEngine
from ..time_stamp_manager.TimeStampManager                  import TimeStampManager
from ..service_set_up.system_set_up                         import set_up_rest_end_point
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


async def validate_request(pCatalogUrl:str , pRequest:dict, pLogger:Logger , pNetLogger:AutoLearnLogEntity) -> Union[ bool , str ]:
    """
    # **validate_request**

    Questo metodo permette di validare una richiesta di training del client

    Args:\n
        pCatalogUrl            (str)                        : url da cui scaricare il catalogo
        pRequest               (dict)                       : richiesta di training inoltrata dal cliente
        pLogger                (Logger)                     : logger locale
        pNetLogger             (AutoLearnLogEntity)         : logger per l'event-store

    Returns:\n
        Union[ bool , str ]                                 : VERO se la validazione non ha riscontrato errori nella richiesta, messaggio d'errore in merito alla richiesta altrimenti

    Raises:\n
        Exception                                           : eccezione nel download del catalogo oppure nella verifica della richiesta del cliente
    """
    # [1] Tentativo Downlaod Catalogo
    catalog:Union[ Dict[int,dict] , Exception, Tuple [Exception , int] ]        = await download_catalog(pCatalogUrl)


    # [2] Log su event-store comunicazione con Catalog per il download
    current_time:int                                                            = TimeStampManager.currentTimeStampInMS()   
    catalog_req:DomainEvent                                                     = make_behavioral_event(b"catalog" , current_time , "training" , "catalog" , "send" , "async" , "training_catalog_req")
    
    outcome:Union[ None , Exception]                                            = await pNetLogger.emit(catalog_req)
    if ExceptionManager.lookForExceptions(outcome):
        pLogger.error("[REST-API @ validate_request] Impossibile scrivere evento comunicazione col catalog sull'Event-Store - Causa: {}".format( str( outcome ) ))



    # [3] Check Risultato Richiesta Catalogo
    if ExceptionManager.lookForExceptions(catalog):
        pLogger.error("[ REST-API @ validate_request ] Errore durante il download del catalogo, richiesta di training rigettata \n->Causa: {} ".format( str( catalog ) ) )

        # [3.1] Log su event-store in merito alla risposta negativa di catalog in merito alla richeista di download
        current_time:int                                                        = TimeStampManager.currentTimeStampInMS()   
        catalog_ans:DomainEvent                                                 = make_behavioral_event(b"catalog" , current_time , "catalog" , "training" , "receive" , "async" , "unable_to_find_catalog")
        
        outcome:Union[ None , Exception]                                        = await pNetLogger.emit(catalog_ans)
        if ExceptionManager.lookForExceptions(outcome):
            pLogger.error("[REST-API @ validate_request] Impossibile scrivere evento comunicazione col catalog sull'Event-Store - Causa: {}".format( str( outcome ) ))

        return "download_catalog_error"


    # [3] Check Risultato Richiesta Catalogo
    if type(catalog) == tuple:
        pLogger.error("[ REST-API @ validate_request ] Errore durante il download del catalogo, richiesta di training rigettata \n->Causa: {} \n-> Status Code: {} ".format(str(catalog[0]) , catalog[1]))

        # [3.1] Log su event-store in merito alla risposta negativa di catalog in merito alla richeista di download
        current_time:int                                                        = TimeStampManager.currentTimeStampInMS()   
        catalog_ans:DomainEvent                                                 = make_behavioral_event(b"catalog" , current_time , "catalog" , "training" , "receive" , "async" , "unable_to_find_catalog")
        
        outcome:Union[ None , Exception]                                        = await pNetLogger.emit(catalog_ans)
        if ExceptionManager.lookForExceptions(outcome):
            pLogger.error("[REST-API @ validate_request] Impossibile scrivere evento comunicazione col catalog sull'Event-Store - Causa: {}".format( str( outcome ) ))


        return "download_catalog_error"

    
    # [3] Check Risultato Richiesta Catalogo - Caso Download riuscito
    current_time:int                                                            = TimeStampManager.currentTimeStampInMS()   
    catalog_ans:DomainEvent                                                     = make_behavioral_event(b"catalog" , current_time , "catalog" , "training" , "receive" , "async" , "training_catalog")
    
    outcome:Union[ None , Exception]                                            = await pNetLogger.emit(catalog_ans)
    if ExceptionManager.lookForExceptions(outcome):
        pLogger.error("[REST-API @ validate_request] Impossibile scrivere evento comunicazione col catalog sull'Event-Store - Causa: {}".format( str( outcome ) ))


    #Verifico Dati
    catalog:dict                                                                = catalog['payload']
    outcome:Union[bool, Tuple[bool, str], Exception]                            = TrainRequestValidator.checkRequest(pRequest , catalog)
    if ExceptionManager.lookForExceptions(outcome):
        pLogger.error("[ REST-API @ validate_request ] Errore durante la validazione della richiesta, richiesta di training rigettata \n->Causa: {} ".format(outcome))
        return "validation_error"

    #Restituisco risultato al chiamante
    if type(outcome) == bool:
        return outcome

    elif type(outcome) == tuple:
        return outcome[1]


async def download_catalog(pUrl:str) -> Union[ Dict[int,dict] , Exception, Tuple [Exception , int] ]:
    """
    # **download_catalog**

    Questa funzione permette di scaricare il catalogo dei Modelli di ML

    Args:\n
        pUrl            (str)       : url da cui scaricare i dati

    Returns:\n
        Union[ Dict[int,dict] , Exception, Tuple [Exception , int] ]

    Raises:\n
        Exception                   : eccezione nel download del catalogo
    """
    engine:HTTPEngine                                                   = HTTPEngine(60)
    engine.startAsync()
    res:Union[ Dict[int,dict] , Exception, Tuple [Exception , int] ]    = await engine.getAsync(pUrl)
    await engine.closeAsync()
    
    return res


async def train_ml_model (pCfg:ServiceConfig , pLogger:Logger ,pService:str, pDestId:str, pComType:str , pPayload:str ,pNetworkLogger:AutoLearnLogEntity , pTrainReq:dict , pTimeStamp:int) -> None:
    """
    # **train_ml_model**
    
    Questa funzione rappresenta un FastAPI Background Task.\n

    Tale funzione permette di scrivere il record comportamentale associato alla risposta del Server ad una richiesta del Cliente

    Args:\n
        pCfg                 (ServiceConfig)        : configurazione dell'applicativo
        pLogger              (Logger)               : logger locale dell'applicativo
        pService             (str)                  : ID server
        pDestId              (str)                  : ID client
        pComType             (str)                  : tipo di comunicazione ("sync" o "async")
        pPayload             (str)                  : payload della comunicazione
        pNetworkLogger       (AutoLearnLogEntity)   : componente che fa logging sull'EventStore
        pTrainReq            (dict)                 : richiesta di training 
        pTimeStamp           (int)                  : timestamp associato alla richiesta di training

    Raises:\n
        Exception                                   : eccezione derivata dalla scrittura sull'EventStore oppure dalla chiusura della connessione con quest'ultimo oppure da problemi durante l'addestramento di un Modello di ML

    """
    #[1] Logging su Event-Store Fine comunicazione col Client
    current_time:int                                            = TimeStampManager.currentTimeStampInMS()
    client_req_ans:DomainEvent                                  = make_behavioral_event(pDestId.encode("ascii") , current_time , pService , pDestId, "send" , pComType , pPayload)
    
    outcome:Union[ None , Exception]                            = await pNetworkLogger.emit(client_req_ans)
    if ExceptionManager.lookForExceptions(outcome):
        pLogger.error("[REST-API @ train_ml_model] Impossibile scrivere evento di fine Comunicazione \n-> Causa: {}".format( str( outcome ) ))


    # [2] Avvio training su un Processo apposito
    serializer:NetworkSerializer                                = NetworkSerializer()
    loop:AbstractEventLoop                                      = asyncio.get_running_loop()
    pool:ProcessPoolExecutor                                    = ProcessPoolExecutor(1)
    hw_data_path:dict                                           = { "hw_dataset" : pCfg.HEIGHT_WEIGHT_DATA_PATH }

    trained_model:Union[ object , str]                          = await loop.run_in_executor( pool, launch_training , pTrainReq ,hw_data_path )


    # [3] Recupero Risultato training e scrittura dato su DB di Sessione attraverso l'ausilio del Broker e del microservizio Session
    if type(outcome) != str:

        #Preparazione record per la scrittura su DB
        record                                                      = pTrainReq
        record['_id']                                               = pTimeStamp
        record['train_data']['model']['model_checkpoint']           = serializer.encodeBinaryObj(trained_model)
        
        #Istanziazione Componente per la comunciazione col Broker
        pr:RabbitProducer                                           = RabbitProducer(pCfg.QUEUE,pCfg.BROKER_LOGIN_TOKEN)
        res:Union[None , Exception]                                 = await pr.start()
        if ExceptionManager.lookForExceptions(res):
            pLogger.error("[REST-API @ train_ml_model] Impossibile avviare connessione con RabbitMQ \n-> Causa: {}".format(str( res ) ))
            return

        #Pubblicazione Messaggio nella coda
        res:Union[DeliveredMessage, Exception]                      = await pr.pubblish(record)
        if ExceptionManager.lookForExceptions(res):
            pLogger.error("[REST-API @ train_ml_model] Impossibile pubblicare messaggi nella coda RabbitMQ \n-> Causa: {}".format( str( res ) ))
            return
        
        #Chiusura Connessione con RabbitMQ
        current_time:int                                            = TimeStampManager.currentTimeStampInMS()
        res:Union[None , Exception]                                 = await pr.stop()
        if ExceptionManager.lookForExceptions(res):
            pLogger.error("[REST-API @ train_ml_model] Impossibile chiudere connessione con RabbitMQ \n-> Causa: {}".format( str( res ) ))


        #Logging su Event-Store comunicazione col microservizio Session
        sess_record_rec:DomainEvent                                 = make_behavioral_event(b"session", current_time , pService, "session" , "send" , "async" , "train_data_record")
        outcome:Union[ None , Exception]                            = await pNetworkLogger.emit(sess_record_rec)
        if ExceptionManager.lookForExceptions(outcome):
            pLogger.error("[REST-API @ train_ml_model] Impossibile scrivere evento di fine Comunicazione - Causa: {}".format( str( outcome ) ))


    #[4] Stop Connessione con EventStore
    await pNetworkLogger._eventStore.stop()


def launch_training (pDirectives:dict , pDataPath:dict) -> Union [ object , str ]:
    """
    # **launch_training**

    Questa funzione permette di lanciare il training di un Modello di ML

    Args:\n
        pDirectives             (dict)      : settaggi del training
        pDataPath               (dict)      : data path dei dataset

    Returns:\n
        Union [ object , str ]

    Exception                               : eccezione durante il caricamento del dataset/training o durante il salvataggio del Modello
    """
    # [0] Setup Logger
    LOGGER_NAME:str                                     = "training__trainer"+str ( os.getpid() )
    LOG_PATH:str                                        = "./log"

    #[1] Costruzione Logger per Computazioni Locali del Microservizio
    logger:Logger                                       = Logger(pName=LOGGER_NAME, pLogPath=LOG_PATH)
    logger.start()

    # [1] Caricamento Dataset
    choosen_dataset:str                                 = pDirectives['train_data']['dataset']['dataset_name']
    seed:int                                            = pDirectives['train_data']['dataset']['split_seed']
    split_test:float                                    = pDirectives['train_data']['dataset']['split_test']
        
    try:

        if choosen_dataset == "Iris-Fisher":
            dataset:Union[ object , Exception]          = load_iris(seed , split_test , logger)
            if ExceptionManager.lookForExceptions(dataset):
                return "error"
            
        elif choosen_dataset == "Height-Weight Dataset":
            hw_dataset_path:str                         = pDataPath['hw_dataset']
            dataset:HeightWeightDataset                 = load_height_weight(hw_dataset_path , seed , split_test , logger)
            if ExceptionManager.lookForExceptions(dataset):
                return "error"

        else:
            raise ValueError("[ REST-API @ launch_training] Il dataset scelto non è presente nel Catalogo")

    except Exception as exp:
        logger.error("[ REST-API @ launch_training] Il dataset scelto non è presente nel Catalogo")
        return str(exp)


    # [2] Avvio Training
    choosen_model:str                                   = pDirectives['train_data']['model']['model_name'] 
    try:
        if          choosen_model == "SVM":
            model:Union[Model, Exception]            = train_SVM ( pDirectives , dataset  )
        elif        choosen_model == "DecisionTree":
            model:Union[Model, Exception]            = train_decision_tree ( pDirectives , dataset  )
        elif        choosen_model == "RandomForest":
            model:Union[Model, Exception]            = train_random_forest ( pDirectives , dataset  )
        elif        choosen_model == "LogisticRegressor":
            model:Union[Model, Exception]            = train_logistic_regressor ( pDirectives , dataset  )
        elif        choosen_model == "Naive-Bayes":
            model:Union[Model, Exception]            = train_naive_bayes ( pDirectives , dataset  )

        else:
            raise ValueError("Il Modello scelto non è presente nel Catalogo")
    except Exception as exp:
        logger.error("[ REST-API @ launch_training] Errore durante il training del Modello di ML \n-> Causa: {}".format( str(exp) ))
        return str( exp ) 


    # [2] Check buona riuscita training
    if ExceptionManager.lookForExceptions(model):
        return "error"

    
    # [3] Salvataggio Checkpoint Modello
    saved_model:Union[ object , Exception]          = model.saveCheckPoint()
    if ExceptionManager.lookForExceptions(saved_model):
        logger.error("[ REST-API @ launch_training] Errore nel salvataggio del Modello \n-> Causa: {}".format( str( saved_model ) ))
        return "error"


    return saved_model 


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


def train_SVM (pDirectives:dict , pDataset:Dataset  ) -> Union [ SVMPandasDataset , Exception]:
    """
    # **train_SVM**

    Questa funzione permette di addestrare il Modello SVM

    Args:\n
        pDirectives             (dict)              : direttive di training
        pDataset                (Dataset)           : dataset su cui addestrare il Modello

    Returns:\n
        Union [ SVMPandasDataset , Exception]       : modello addestrato o eccezione

    Raises:\n
        Exception                                   : eccezione durante il training del Modello
    """
    svm:SVMPandasDataset                            = SVMPandasDataset()

    # [1] Prelievo Iperparametri Modello
    params:dict                                     = {}
    
    if "model_hyperparams" in pDirectives['train_data']['model'].keys() and pDirectives['train_data']['model']['model_hyperparams'] != None: 
        hyperparams:List[dict]                      = pDirectives['train_data']['model']['model_hyperparams']

        kernel_svm:List[str]                        = list( filter ( lambda x: x['hyper_param_name'] == "kernel" , hyperparams )  )
        if len(kernel_svm) == 1:
            params['kernel']                        = kernel_svm[0]['hyper_param_value'] 
        
        max_iter:List[int]                          = list( filter ( lambda x: x['hyper_param_name'] == "max_iter" , hyperparams )  )
        if len(max_iter) == 1:
            params['max_iter']                      = max_iter[0]['hyper_param_value'] 

        if 'learning' in pDirectives['train_data'].keys() and pDirectives['train_data']['learning'] != None:
            learning_hyperparams:List[dict]         = pDirectives['train_data']['learning']['learning_hyperparams'] 
            regularization:List[float]              = list( filter ( lambda x: x['hyper_param_name'] == "regularization" , learning_hyperparams ) )

            if len(regularization) == 1:
                params['regularization']            = regularization[0]['hyper_param_value'] 

    # [2] Model Setup
    outcome:Union[ None , Exception]                = svm.setUp(params)
    if ExceptionManager.lookForExceptions(outcome):
        return outcome

    # [3] Fitting Modello
    outcome:Union[ None , Exception]                = svm.fit(pDataset)
    if ExceptionManager.lookForExceptions(outcome):
        return outcome
    
    return svm


def train_random_forest (pDirectives:dict , pDataset:Dataset  ) -> Union [ RandomForestPandasDataset , Exception]:
    """
    # **train_random_forest**

    Questa funzione permette di addestrare il Modello RandomForest

    Args:\n
        pDirectives             (dict)                          : direttive di training
        pDataset                (Dataset)                       : dataset su cui addestrare il Modello

    Returns:\n
        Union [ RandomForestPandasDataset , Exception]          : modello addestrato o eccezione

    Raises:\n
        Exception                                               : eccezione durante il training del Modello
    """
    forest:RandomForestPandasDataset        = RandomForestPandasDataset()

    # [1] Prelievo Iperparametri Modello
    params:dict                             = {}

    if "model_hyperparams" in pDirectives['train_data']['model'].keys() and pDirectives['train_data']['model']['model_hyperparams'] != None:
        hyperparams:List[dict]              = pDirectives['train_data']['model']['model_hyperparams']

        n_estimators:List[int]              = list( filter ( lambda x: x['hyper_param_name'] == "n_estimators" ,hyperparams  ) )
        if len(n_estimators) == 1:
            params["n_estimators"]          = n_estimators[0]['hyper_param_value'] 


        max_depth:List[int]                 = list( filter ( lambda x: x['hyper_param_name'] == "max_depth"  ,hyperparams ) )
        if len(max_depth) == 1:
            params["max_depth"]             = max_depth[0]['hyper_param_value'] 


    # [2] Model Setup
    outcome:Union[ None , Exception]        = forest.setUp(params)
    if ExceptionManager.lookForExceptions(outcome):
        return outcome


    # [3] Fitting Modello
    outcome:Union[ None , Exception]        = forest.fit(pDataset)
    if ExceptionManager.lookForExceptions(outcome):
        return outcome

    return forest


def train_decision_tree (pDirectives:dict , pDataset:Dataset  ) -> Union [ DecisionTreePandasDataset , Exception]:
    """
    # **train_decision_tree**

    Questa funzione permette di addestrare il Modello DecisionTree

    Args:\n
        pDirectives             (dict)                          : direttive di training
        pDataset                (Dataset)                       : dataset su cui addestrare il Modello

    Returns:\n
        Union [ DecisionTreePandasDataset , Exception]          : modello addestrato o eccezione

    Raises:\n
        Exception                                               : eccezione durante il training del Modello
    """
    tree:DecisionTreePandasDataset          = DecisionTreePandasDataset()

    # [1] Prelievo Iperparametri Modello
    params:dict                             = {}
    if "model_hyperparams" in pDirectives['train_data']['model'].keys() and pDirectives['train_data']['model']['model_hyperparams'] != None:
        hyperparams:List[dict]              = pDirectives['train_data']['model']['model_hyperparams']

        max_depth:List[int]                 = list( filter ( lambda x: x['hyper_param_name'] == "max_depth" , hyperparams ) )
        if len(max_depth) == 1:
            params['max_depth']             = max_depth[0]['hyper_param_value'] 
    

    # [2] Setup Modello
    outcome:Union[ None , Exception]       = tree.setUp(params)
    if ExceptionManager.lookForExceptions(outcome):
        return outcome


    # [3] Fitting Modello
    outcome:Union[ None , Exception]        = tree.fit(pDataset)
    if ExceptionManager.lookForExceptions(outcome):
        return outcome

    return tree


def train_logistic_regressor (pDirectives:dict , pDataset:Dataset  ) -> Union [ LogisticRegressorPandasDataset , Exception]:
    """
    # **train_logistic_regressor**

    Questa funzione permette di addestrare il Modello LogisticRegressor

    Args:\n
        pDirectives             (dict)                          : direttive di training
        pDataset                (Dataset)                       : dataset su cui addestrare il Modello

    Returns:\n
        Union [ LogisticRegressorPandasDataset , Exception]     : modello addestrato o eccezione

    Raises:\n
        Exception                                               : eccezione durante il training del Modello
    """
    logit:LogisticRegressorPandasDataset            = LogisticRegressorPandasDataset()


    # [1] Prelievo Iperparametri Modello
    params:dict                                     = {}
    if "model_hyperparams" in pDirectives['train_data']['model'].keys() and pDirectives['train_data']['model']['model_hyperparams'] != None:
        hyperparams:List[dict]                      = pDirectives['train_data']['model']['model_hyperparams']

        random_state:List[int]                      = list( filter ( lambda x: x['hyper_param_name'] == "random_state" , hyperparams ) )
        if len(random_state) == 1:
            params['random_state']                  = random_state[0]['hyper_param_value'] 

        if 'learning' in pDirectives['train_data'].keys() and pDirectives['train_data']['learning'] != None:
            learning_hyperparams:List[dict]         = pDirectives['train_data']['learning']['learning_hyperparams'] 
            max_iter:List[int]                      = list( filter ( lambda x: x['hyper_param_name'] == "max_iter" , learning_hyperparams ) )

            if len(max_iter) == 1:
                params['max_iter']                  = max_iter[0]['hyper_param_value'] 


    # [2] SetUp Modello
    outcome:Union[ None , Exception]                = logit.setUp(params)
    if ExceptionManager.lookForExceptions(outcome):
        return outcome


    # [3] Fitting Modello
    outcome:Union[ None , Exception]                = logit.fit(pDataset)
    if ExceptionManager.lookForExceptions(outcome):
        return outcome

    return logit


def train_naive_bayes (pDirectives:dict , pDataset:Dataset  ) -> Union [ NaiveBayesPandasDataset , Exception]:
    """
    # **train_naive_bayes**

    Questa funzione permette di addestrare il Modello NaiveBayes

    Args:\n
        pDirectives             (dict)                          : direttive di training
        pDataset                (Dataset)                       : dataset su cui addestrare il Modello

    Returns:\n
        Union [ NaiveBayesPandasDataset , Exception]            : modello addestrato o eccezione

    Raises:\n
        Exception                                               : eccezione durante il training del Modello
    """
    bayes:NaiveBayesPandasDataset                   = NaiveBayesPandasDataset()

    # [1] Prelievo Iperparametri Modello
    params:dict                                     = {}
    if "model_hyperparams" in pDirectives['train_data']['model'].keys() and pDirectives['train_data']['model']['model_hyperparams'] != None:
        hyperparams:List[dict]                      = pDirectives['train_data']['model']['model_hyperparams']
        priors:List[float]                          = list( filter ( lambda x: x['hyper_param_name'] == "priors" , hyperparams ) )

        if len(priors) ==1:
            params["priors"]                        = priors[0]['hyper_param_value'] 
    

    # [2] SetUp Modello
    outcome:Union[ None , Exception]               = bayes.setUp(params)
    if ExceptionManager.lookForExceptions(outcome):
        return outcome


    # [3] Fitting Modello
    outcome:Union[ None , Exception]                = bayes.fit(pDataset)
    if ExceptionManager.lookForExceptions(outcome):
        return outcome

    return bayes