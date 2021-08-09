"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 08/08/2021                       \n
@last-update            :  Sun 08/08/2021                       \n

Questo componente implementa l'interfaccia REST del Microservizio Training
"""

from fastapi                                            import APIRouter, status, HTTPException, BackgroundTasks
from fastapi.responses                                  import JSONResponse
from typing                                             import List,Set,Optional,Dict,Union
from multiprocessing                                    import Process

from ..service_config.ServiceConfig                     import ServiceConfig
from ..pydantic_models.Notify                           import Notify
from ..pydantic_models.TrainRequest                     import TrainRequest
from ..domain_work.worker                               import validate_request , train_ml_model
from ..logger.Logger                                    import Logger
from ..exception_manager.ExceptionManager               import ExceptionManager
from ..service_set_up.system_set_up                     import set_up_rest_end_point
from ..event_sourcing_utility.event_sourcing_utility    import make_behavioral_event,setUpEventSourcing
from ..time_stamp_manager.TimeStampManager              import TimeStampManager
from ..event_sourcing_utility.event_sourcing_utility    import final_communication_log


router , cfg, network_logger , event_store, EVENT_STORE_PARAMS, logger  = set_up_rest_end_point()


@router.post(
                                                                    "/training/api/training_req", 
    response_model                                      =           Notify, 
    status_code                                         =           status.HTTP_202_ACCEPTED, 
    tags                                                =           ["train_ml_model"],
    summary                                             =           "Addestra un Modello di Machine Learning",
    response_description                                =           "Quest'API permette di addestrare un Modello di ML nel cloud"
    )
async def training_req(pRequest:TrainRequest , background_tasks: BackgroundTasks):

    #Init Compoenti Logging Comportamentale e Scrittura record comportamentale associato all'azione richiesta dal Client
    current_time:int                                    = TimeStampManager.currentTimeStampInMS()   
    await setUpEventSourcing(cfg.ENTITY_ID , event_store , network_logger , EVENT_STORE_PARAMS)

    client_req:DomainEvent                              = make_behavioral_event(b"client" , current_time , "client" , cfg.ENTITY_ID , "receive" , "async" , "training_req")
    
    outcome:Union[ None , Exception]                    = await network_logger.emit(client_req)
    if ExceptionManager.lookForExceptions(outcome):
        logger.error("[REST-API @ training_req] Impossibile scrivere evento inizio comunicazione col client sull'Event-Store - Causa: {}".format( str( outcome ) ))


    #Svolgimento Domain Work
    outcome_val:Union[ bool , str]                      = await validate_request(cfg.CATALOG_URL_DOWNLOAD,pRequest.dict(),logger , network_logger)

    if type(outcome_val) == str and "[!]" in outcome_val:
        outcome:str                                     = "bad_request__{}".format(outcome_val)
        background_tasks.add_task( final_communication_log , cfg.ENTITY_ID , "client" , "async" , outcome , network_logger  )

    elif type(outcome_val) == str:
        outcome:str                                     = "internal_server_error"
        background_tasks.add_task( final_communication_log , cfg.ENTITY_ID , "client" , "async" , outcome , network_logger  )

    else:
        outcome:str                                     = "req_accepted"
        background_tasks.add_task( train_ml_model , cfg , logger , cfg.ENTITY_ID , "client" , "async" , outcome , network_logger , pRequest.dict() , current_time  )



    #Restituisco catalogo al cliente
    return { "payload" : outcome } if outcome == "req_accepted" else JSONResponse(status_code=503, content={"message": outcome})