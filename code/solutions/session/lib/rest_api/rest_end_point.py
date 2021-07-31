"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 31/07/2021                       \n
@last-update            :  Sat 31/07/2021                       \n

Questo componente implementa l'interfaccia REST del Microservizio Session.
"""

from fastapi                                            import APIRouter, status, HTTPException, BackgroundTasks
from fastapi.responses                                  import JSONResponse
from typing                                             import List,Set,Optional,Dict,Union
import asyncio
import os
from aiormq.types                                       import DeliveredMessage


from ..domain_work.worker                               import view_sessions , decryptIdSession , save_session, queryOneRecord, SESSION_NOT_EXISTS
from ..service_config.ServiceConfig                     import ServiceConfig
from ..abstract_event_sourcing.DomainEvent              import DomainEvent
from ..pydantic_models.Notify                           import Notify
from ..pydantic_models.Experiment                       import ViewExperimentsQuery , Experiment
from ..pydantic_models.SessionRequest                   import SessionRequest
from ..pydantic_models.ClearSessionRequest              import ClearSessionRequest
from ..network_serializer.NetworkSerializer             import NetworkSerializer
from ..logger.Logger                                    import Logger
from ..mongo_engine.MongoEngine                         import MongoEngine
from ..exception_manager.ExceptionManager               import ExceptionManager
from ..rabbit_producer.RabbitProducer                   import RabbitProducer
from ..event_sourcing_utility.event_sourcing_utility    import setUpEventSourcing, make_behavioral_event, final_communication_log
from ..time_stamp_manager.TimeStampManager              import TimeStampManager
from ..service_set_up.system_set_up                     import set_up_rest_end_point


# [0] SetUp Sistema
router , cfg, network_logger , event_store, EVENT_STORE_PARAMS, logger  = set_up_rest_end_point()



@router.get(
                                                                    "/session/api/view_sessions", 
    response_model                                      =           ViewExperimentsQuery, 
    responses                                           =           {503: {"model": Notify}},
    status_code                                         =           status.HTTP_202_ACCEPTED, 
    tags                                                =           ["session_experiments"],
    summary                                             =           "Visualizza Esperimenti di Session",
    response_description                                =           "Restituisce un Data Transfer Object contente tutti i record presenti nel DB di Sessione"
    )
async def view__sessions(background_tasks: BackgroundTasks):
    
    #Init Compoenti Logging Comportamentale
    current_time:int                               = TimeStampManager.currentTimeStampInMS()   
    await setUpEventSourcing(cfg.ENTITY_ID , event_store , network_logger , EVENT_STORE_PARAMS)


    #Scrittura record comportamentale associato all'azione richiesta dal Client
    client_req:DomainEvent                         = make_behavioral_event(b"client" , current_time , "client" , cfg.ENTITY_ID , "receive" , "async" , "view_sessions")
    
    outcome:Union[ None , Exception]               = await network_logger.emit(client_req)
    if ExceptionManager.lookForExceptions(outcome):
        logger.error("[REST-API @ view_sessions] Impossibile scrivere evento sull'Event-Store - Causa: {}".format( str( outcome ) ))


    #Svolgimento Domain Work
    experiments:Union[ dict , Exception]           = await view_sessions(cfg, logger)
    if ExceptionManager.lookForExceptions(experiments):
        logger.error("[REST-API @ view_sessions] Impossibile Recuperare Dati dal DB Sessions - Causa: {}".format( str( experiments ) ))
        outcome:str                                = "unable_to_fetch_data"
    else:
        outcome:str                                = "session_summary"


    #Aggiunta background task che inserisce il record della comunicazione server -> client nell'Event-Store
    background_tasks.add_task( final_communication_log , cfg.ENTITY_ID , "client" , "async" , outcome , network_logger  )


    #Restituisco catalogo al cliente
    return experiments if outcome == "session_summary" else JSONResponse(status_code=503, content={"message": "unable_to_fetch_data"})



@router.post(
                                                                    "/session/api/save_session", 
    response_model                                      =           Notify, 
    status_code                                         =           status.HTTP_202_ACCEPTED, 
    tags                                                =           ["save_session_data"],
    summary                                             =           "Commit Sessione nello storage Permanente",
    response_description                                =           "Archivia un record di Sessione nel DB di Storage e contestualmente cancella anche il corrispettivo record nel DB di Sessione"
    )
async def save__session(pSessId:SessionRequest , background_tasks: BackgroundTasks):
    
    #Init Compoenti Logging Comportamentale
    current_time:int                               = TimeStampManager.currentTimeStampInMS()   
    await setUpEventSourcing(cfg.ENTITY_ID , event_store , network_logger , EVENT_STORE_PARAMS)


    #Scrittura record comportamentale associato all'azione richiesta dal Client
    client_req:DomainEvent                         = make_behavioral_event(b"client" , current_time , "client" , cfg.ENTITY_ID , "receive" , "async" , "save_session")
    
    outcome:Union[ None , Exception]               = await network_logger.emit(client_req)
    if ExceptionManager.lookForExceptions(outcome):
        logger.error("[REST-API @ save_session] Impossibile scrivere evento sull'Event-Store - Causa: {}".format( str( outcome ) ))


    #Svolgimento Domain Work
    # [1] Setup Serializzatore
    serializer:NetworkSerializer                    = NetworkSerializer()

    outcome:Union[None , Exception]                 = serializer.readKeyFromFile()
    if ExceptionManager.lookForExceptions(outcome):
        logger.error("[REST-API @ save_session] Impossibile leggere file con la chiave per cifrare/decifrare i messaggi confidenziali \n-> Causa: {}".format( str( outcome ) ))
        outcome:str                                 = "internal_server_error"

        #Aggiunta background task che inserisce il record della comunicazione server -> client nell'Event-Store
        background_tasks.add_task( final_communication_log , cfg.ENTITY_ID , "client" , "async" , outcome , network_logger  )

        #Restituisco risultato al client
        return { "payload" : outcome }


    else:


        # [2] Setup Mongo
        engine:MongoEngine                                          = MongoEngine(cfg.DB_HOST_NAME, cfg.DB_PORT, cfg.DB_USER_NAME, cfg.DB_PASSWORD , cfg.DB_NAME, cfg.DB_COLLECTION   )

        outcome:Union[ None, Exception ]                            = engine.start()

        if ExceptionManager.lookForExceptions ( outcome  ):
            logger.error ("[REST-API @ save_session]  Impossibile connettersi con MongoDB :( \n-> Causa: {}".format( str( outcome ) ))
            outcome:str                                             = "internal_server_error"

            #Aggiunta background task che inserisce il record della comunicazione server -> client nell'Event-Store
            background_tasks.add_task( final_communication_log , cfg.ENTITY_ID , "client" , "async" , outcome , network_logger  )

            #Restituisco catalogo al cliente
            return { "payload" : outcome }


        else:


            # [3] Decifratura chiave Sessione
            outcome:Union [ int , Exception , bool ]                    = await decryptIdSession(pSessId.id_sess_cf, serializer, logger, engine)

            if ExceptionManager.lookForExceptions(outcome):
                outcome:str                                             = "internal_server_error"

                #Aggiunta background task che inserisce il record della comunicazione server -> client nell'Event-Store
                background_tasks.add_task( final_communication_log , cfg.ENTITY_ID , "client" , "async" , outcome , network_logger  )

                #Stop connessione con Mongo
                engine.stop()

                #Restituisco risultato computazione al client
                return { "payload" : outcome }


            elif outcome == False:


                #Caso Messaggio cifrato con una chiave non autentica
                logger.log("[REST-API @ save_session]  Impossibile decifrare id sessione, richiesta di save_session rigettata")
                outcome:str                                             = "req_rejected"

                #Stop connessione con Mongo
                engine.stop()

                #Aggiunta background task che inserisce il record della comunicazione server -> client nell'Event-Store
                background_tasks.add_task( final_communication_log , cfg.ENTITY_ID , "client" , "async" , outcome , network_logger  )

                #Restituisco risultato computazione al client
                return { "payload" : outcome }


            else:


                #Caso Messaggio Cifrato con la chiave Autentica
                id_session:int                                          = outcome

                producer:RabbitProducer                                 = RabbitProducer(cfg.STORAGE_RECORD_QUEUE , cfg.BROKER_LOGIN_TOKEN)

                #Connessione con RabbitMQ
                outcome:Union[ None , Exception]                        = await producer.start()

                if ExceptionManager.lookForExceptions(outcome):
                    logger.error("[REST-API @ save_session] Impossibile connettersi con RabbitMQ \n-> Causa: {}".format( str( outcome) ))
                    outcome:str                                         = "internal_server_error"

                    #Stop connessione con mongo
                    engine.stop()

                    #Aggiunta background task che inserisce il record della comunicazione server -> client nell'Event-Store
                    background_tasks.add_task( final_communication_log , cfg.ENTITY_ID , "client" , "async" , outcome , network_logger  )

                    #Restituisco risultato computazione al client
                    return { "payload" : outcome }


                else:


                    #Caso Connessione con Broker riuscita
                    outcome:Union[Exception , int , None]           = await save_session(id_session , logger , engine , producer)


                    #Gestione eccezioni
                    if ExceptionManager.lookForExceptions(outcome):
                        outcome:str                                 = "internal_server_error"
                    elif type(outcome) == int and outcome == SESSION_NOT_EXISTS:
                        outcome:str                                 = "internal_server_error"
                    else:
                        outcome:str                                 = "req_accepted"

                    #Stop connessioni con Componenti Distribuiti
                    engine.stop()
                    await producer.stop()


                    #Aggiunta background task che inserisce il record della comunicazione server -> client nell'Event-Store
                    background_tasks.add_task( final_communication_log , cfg.ENTITY_ID , "client" , "async" , outcome , network_logger  )

                    #Restituisco risultato computazione al client
                    return { "payload" : outcome }



@router.post(
                                                                    "/session/api/query_one_record", 
    response_model                                      =           Experiment, 
    status_code                                         =           status.HTTP_202_ACCEPTED, 
    tags                                                =           ["query_session_record"],
    summary                                             =           "Query sul DB Session per uno Specifico Record",
    response_description                                =           "Query sul DB Session per uno Specifico Record"
    )
async def query_record(pSessId:ClearSessionRequest , background_tasks: BackgroundTasks):
    
    #Init Compoenti Logging Comportamentale
    current_time:int                               = TimeStampManager.currentTimeStampInMS()   
    await setUpEventSourcing(cfg.ENTITY_ID , event_store , network_logger , EVENT_STORE_PARAMS)


    #Scrittura record comportamentale associato all'azione richiesta dal Client
    client_req:DomainEvent                         = make_behavioral_event(b"evaluation" , current_time , "evaluation" , cfg.ENTITY_ID , "receive" , "async" , "query_record")
    
    outcome:Union[ None , Exception]               = await network_logger.emit(client_req)
    if ExceptionManager.lookForExceptions(outcome):
        logger.error("[REST-API @ save_session] Impossibile scrivere evento sull'Event-Store - Causa: {}".format( str( outcome ) ))


    #Svolgimento Domain Work
    # [1] Setup Mongo
    engine:MongoEngine                                          = MongoEngine(cfg.DB_HOST_NAME, cfg.DB_PORT, cfg.DB_USER_NAME, cfg.DB_PASSWORD , cfg.DB_NAME, cfg.DB_COLLECTION   )

    outcome:Union[ None, Exception ]                            = engine.start()


    if ExceptionManager.lookForExceptions ( outcome  ):
        logger.error ("[REST-API @ query_record]  Impossibile connettersi con MongoDB :( \n-> Causa: {}".format( str( outcome ) ))
        outcome:str                                             = "internal_server_error"

        #Aggiunta background task che inserisce il record della comunicazione server -> client nell'Event-Store
        background_tasks.add_task( final_communication_log , cfg.ENTITY_ID , "client" , "async" , outcome , network_logger  )

        #Restituisco catalogo al cliente
        JSONResponse(status_code=503, content={"message": "Internal Server Error"})


    else:

        outcome:Union[dict , int , Exception]                       = await queryOneRecord(pSessId.id_rec , logger, engine )

        #Controlli sul Dato
        if ExceptionManager.lookForExceptions(outcome):
            outcome:str                                             = "internal_server_error"

            #Aggiunta background task che inserisce il record della comunicazione server -> client nell'Event-Store
            background_tasks.add_task( final_communication_log , cfg.ENTITY_ID , "client" , "async" , outcome , network_logger  )

            #Restituisco risultato al chiamante
            JSONResponse(status_code=503, content={"message": outcome})


        if type(outcome) == int and outcome == SESSION_NOT_EXISTS:
            outcome:str             = "session_not_exists"

            #Aggiunta background task che inserisce il record della comunicazione server -> client nell'Event-Store
            background_tasks.add_task( final_communication_log , cfg.ENTITY_ID , "client" , "async" , outcome , network_logger  )

            #Restituisco catalogo al cliente            
            return JSONResponse(status_code=202, content={"message": outcome})
        

        #Caso Record Trovato
        record:dict                         = outcome
        outcome:str                         = "eval_dto"

        background_tasks.add_task( final_communication_log , cfg.ENTITY_ID , "client" , "async" , outcome , network_logger  )


        return record