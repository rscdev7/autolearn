"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 25/07/2021                       \n
@last-update            :  Wed 27/07/2021                       \n

Questo componente implementa l'interfaccia REST del Microservizio Catalog.
"""

from fastapi                                            import APIRouter, status, HTTPException, BackgroundTasks
from fastapi.responses                                  import JSONResponse
from typing                                             import List,Set,Optional,Dict,Union
import asyncio
import os


from ..catalog_config.CatalogConfig                     import CatalogConfig
from ..concrete_event_sourcing.KafkaEventStore          import KafkaEventStore
from ..concrete_event_sourcing.AutoLearnLogEntity       import AutoLearnLogEntity
from ..abstract_event_sourcing.DomainEvent              import DomainEvent
from ..domain_work.worker                               import get_catalog
from ..pydantic_models.Catalog                          import Catalog
from ..pydantic_models.Notify                           import Notify
from ..logger.Logger                                    import Logger
from ..exception_manager.ExceptionManager               import ExceptionManager
from ..event_sourcing_utility.event_sourcing_utility    import setUpEventSourcing, make_behavioral_event, final_communication_log
from ..time_stamp_manager.TimeStampManager              import TimeStampManager
from ..catalog_set_up.system_set_up                     import setUp


# [0] SetUp Sistema
router , cfg, network_logger , event_store, EVENT_STORE_PARAMS, logger = setUp()



@router.get(
    "/catalog/api/get_catalog", 
    response_model=Catalog, 
    responses={503: {"model": Notify}},
    status_code=status.HTTP_202_ACCEPTED, 
    tags=["view"],
    summary="Restituisce il Catalogo",
    response_description="Restituisce un Data Transfer Object contente Modelli e Dataset presenti nel Catalogo")
async def getCatalog(pIdClient:str, background_tasks: BackgroundTasks):
    """
    Quest'API-REST preleva il catalogo da disco e lo restituisce al client
    """
    
    #Init Compoenti Logging Comportamentale
    current_time:int                               = TimeStampManager.currentTimeStampInMS()   
    await setUpEventSourcing(cfg.ENTITY_ID , event_store , network_logger , EVENT_STORE_PARAMS)


    #Scrittura record comportamentale associato all'azione richiesta dal Client
    client_req:DomainEvent                         = make_behavioral_event(pIdClient.encode("ascii") , current_time , pIdClient , cfg.ENTITY_ID , "receive" , "async" , "training_catalog_req")
    
    outcome:Union[ None , Exception]               = await network_logger.emit(client_req)
    if ExceptionManager.lookForExceptions(outcome):
        logger.error("Impossibile scrivere evento sull'Event-Store - Causa: {}".format( str( outcome ) ))


    #Svolgimento Domain Work
    training_catalog:Union[ dict , Exception]      = await get_catalog()
    if ExceptionManager.lookForExceptions(training_catalog):
        logger.error("Impossibile leggere file catalogo - Causa: {}".format( str( training_catalog ) ))
        outcome:str                                = "unable_to_find_catalog"
    else:
        outcome:str                                = "training_catalog"


    #Aggiunta background task che inserisce il record della comunicazione server -> client nell'Event-Store
    background_tasks.add_task( final_communication_log , cfg.ENTITY_ID , pIdClient , "async" , outcome , network_logger  )


    #Restituisco catalogo al cliente
    return training_catalog if outcome == "training_catalog" else JSONResponse(status_code=503, content={"message": "Unable to Retrieve Catalog"})