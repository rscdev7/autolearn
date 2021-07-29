"""
@author           	    :  rscalia                              \n
@build-date             :  Wed 28/07/2021                       \n
@last-update            :  Thu 29/07/2021                       \n

Questo componente implementa l'interfaccia REST del Microservizio Storage.
"""

from fastapi                                            import APIRouter, status, HTTPException, BackgroundTasks
from fastapi.responses                                  import JSONResponse
from typing                                             import List,Set,Optional,Dict,Union
import asyncio
import os

from ..domain_work.worker                               import view_experiments
from ..service_config.ServiceConfig                     import ServiceConfig
from ..abstract_event_sourcing.DomainEvent              import DomainEvent
from ..pydantic_models.Notify                           import Notify
from ..pydantic_models.Experiment                       import ViewExperimentsQuery
from ..logger.Logger                                    import Logger
from ..exception_manager.ExceptionManager               import ExceptionManager
from ..event_sourcing_utility.event_sourcing_utility    import setUpEventSourcing, make_behavioral_event, final_communication_log
from ..time_stamp_manager.TimeStampManager              import TimeStampManager
from ..service_set_up.system_set_up                     import set_up_rest_end_point


# [0] SetUp Sistema
router , cfg, network_logger , event_store, EVENT_STORE_PARAMS, logger  = set_up_rest_end_point()



@router.get(
                                                                    "/storage/api/view_experiments", 
    response_model                                      =           ViewExperimentsQuery, 
    responses                                           =           {503: {"model": Notify}},
    status_code                                         =           status.HTTP_202_ACCEPTED, 
    tags                                                =           ["experiments"],
    summary                                             =           "Visualizza Esperimenti",
    response_description                                =           "Restituisce un Data Transfer Object contente tutti i record presenti nel DB di Storage"
    )
async def get_all_experiments(background_tasks: BackgroundTasks):
    """
    Quest'API-REST preleva il catalogo da disco e lo restituisce al client
    """
    
    #Init Compoenti Logging Comportamentale
    current_time:int                               = TimeStampManager.currentTimeStampInMS()   
    await setUpEventSourcing(cfg.ENTITY_ID , event_store , network_logger , EVENT_STORE_PARAMS)


    #Scrittura record comportamentale associato all'azione richiesta dal Client
    client_req:DomainEvent                         = make_behavioral_event(b"client" , current_time , "client" , cfg.ENTITY_ID , "receive" , "async" , "view_experiments")
    
    outcome:Union[ None , Exception]               = await network_logger.emit(client_req)
    if ExceptionManager.lookForExceptions(outcome):
        logger.error("Impossibile scrivere evento sull'Event-Store - Causa: {}".format( str( outcome ) ))


    #Svolgimento Domain Work
    experiments:Union[ dict , Exception]           = await view_experiments(cfg, logger)
    if ExceptionManager.lookForExceptions(experiments):
        logger.error("Impossibile leggere file catalogo - Causa: {}".format( str( experiments ) ))
        outcome:str                                = "unable_to_fetch_data"
    else:
        outcome:str                                = "storage_summary"


    #Aggiunta background task che inserisce il record della comunicazione server -> client nell'Event-Store
    background_tasks.add_task( final_communication_log , cfg.ENTITY_ID , "client" , "async" , outcome , network_logger  )


    #Restituisco catalogo al cliente
    return experiments if outcome == "storage_summary" else JSONResponse(status_code=503, content={"message": "Unable to fetch data into the DB"})