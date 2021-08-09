"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 09/08/2021                       \n
@last-update            :  Sun 09/08/2021                       \n

Questo componente implementa l'interfaccia REST del Microservizio Evaluation
"""

from fastapi                                            import APIRouter, status, HTTPException, BackgroundTasks
from fastapi.responses                                  import JSONResponse
from typing                                             import List,Set,Optional,Dict,Union
from multiprocessing                                    import Process

from ..service_config.ServiceConfig                     import ServiceConfig
from ..pydantic_models.Notify                           import Notify
from ..domain_work.worker                               import decryptSessId , checkTrainingExist , evaluate_model
from ..logger.Logger                                    import Logger
from ..exception_manager.ExceptionManager               import ExceptionManager
from ..service_set_up.system_set_up                     import set_up_rest_end_point
from ..event_sourcing_utility.event_sourcing_utility    import make_behavioral_event,setUpEventSourcing
from ..time_stamp_manager.TimeStampManager              import TimeStampManager
from ..event_sourcing_utility.event_sourcing_utility    import final_communication_log
from cryptography.fernet                                import InvalidToken

router , cfg, network_logger , event_store, EVENT_STORE_PARAMS, logger  = set_up_rest_end_point()


@router.post(
                                                                    "/evaluation/api/eval_model", 
    response_model                                              =           Notify, 
    status_code                                                 =           status.HTTP_202_ACCEPTED, 
    tags                                                        =           ["eval_ml_model"],
    summary                                                     =           "Valutazione Modello ML",
    response_description                                        =           "Quest'API permette di valutare le prestazioni di un Modello di ML precedentemente addestrato"
    )
async def eval_model(pEvalReq:Notify , background_tasks: BackgroundTasks):
    
    #Init Compoenti Logging Comportamentale e Scrittura record comportamentale associato all'azione richiesta dal Client
    current_time:int                                            = TimeStampManager.currentTimeStampInMS()   
    await setUpEventSourcing(cfg.ENTITY_ID , event_store , network_logger , EVENT_STORE_PARAMS)

    client_req:DomainEvent                                      = make_behavioral_event(b"client" , current_time , "client" , cfg.ENTITY_ID , "receive" , "async" , "eval_req")
    
    outcome:Union[ None , Exception]                            = await network_logger.emit(client_req)
    if ExceptionManager.lookForExceptions(outcome):
        logger.error("[REST-API @ eval_model] Impossibile scrivere evento inizio comunicazione col client sull'Event-Store - Causa: {}".format( str( outcome ) ))



    #Decifratura ID Sessione inoltrato dal Cliente
    outcome:Union[ int , Exception]                             = decryptSessId( pEvalReq.dict()['payload'] ,logger)
    if ExceptionManager.lookForExceptions(outcome):

        #Log su Event-Store risposta server
        current_time:int                                        = TimeStampManager.currentTimeStampInMS()   
        client_req_out:DomainEvent                              = make_behavioral_event(b"client" , current_time , "evaluation" , "client" , "send" , "async" , "req_rejected")
    
        outcome:Union[ None , Exception]                        = await network_logger.emit(client_req_out)
        if ExceptionManager.lookForExceptions(outcome):
            logger.error("[REST-API @ eval_model] Impossibile scrivere evento Request Rejected su Event-Store - Causa: {}".format( str( outcome ) ))

        #Stop connessione con Event Store
        outcome:Union[ None , Exception]                        = await event_store.stop()
        if ExceptionManager.lookForExceptions(outcome):
            logger.error("[REST-API @ eval_model] Impossibile chiudere connessione con Event-Store \n-> Causa: {}".format( str( outcome ) ))
        
        return JSONResponse(status_code=503, content={"message": "req_rejected"})
    


    #Prelievo Record Sessione dal DB
    outcome:Union[ dict , Exception, Tuple[ Exception , int]]   = await checkTrainingExist(outcome , cfg, network_logger ,logger )
    
    if ExceptionManager.lookForExceptions(outcome):

        outcome:Union[ None , Exception]                        = await event_store.stop()
        if ExceptionManager.lookForExceptions(outcome):
            logger.error("[REST-API @ eval_model] Impossibile chiudere connessione con Event-Store \n-> Causa: {}".format( str( outcome ) ))

        return JSONResponse(status_code=503, content={"message": "internal_server_error"})


    if type(outcome) == tuple:

        outcome:Union[ None , Exception]                        = await event_store.stop()
        if ExceptionManager.lookForExceptions(outcome):
            logger.error("[REST-API @ eval_model] Impossibile chiudere connessione con Event-Store \n-> Causa: {}".format( str( outcome ) ))

        return JSONResponse(status_code=503, content={"message": "internal_server_error"})


    if type(outcome) == dict and "message" in outcome.keys() and outcome['message'] ==  "session_not_exists":

        outcome:Union[ None , Exception]                        = await event_store.stop()
        if ExceptionManager.lookForExceptions(outcome):
            logger.error("[REST-API @ eval_model] Impossibile chiudere connessione con Event-Store \n-> Causa: {}".format( str( outcome ) ))

        return JSONResponse(status_code=503, content={"message": "session_not_exists"})


    if type(outcome) == dict and "message" in outcome.keys():
        outcome:Union[ None , Exception]                        = await event_store.stop()
        if ExceptionManager.lookForExceptions(outcome):
            logger.error("[REST-API @ eval_model] Impossibile chiudere connessione con Event-Store \n-> Causa: {}".format( str( outcome ) ))

        return JSONResponse(status_code=503, content={"message": "internal_server_error"})



    #Aggiunta background task che inserisce il record della comunicazione server -> client nell'Event-Store
    background_tasks.add_task( evaluate_model , outcome , cfg , network_logger , logger, event_store  )

    #Restituisco risultato al client
    return { "payload" : "req_accepted" }