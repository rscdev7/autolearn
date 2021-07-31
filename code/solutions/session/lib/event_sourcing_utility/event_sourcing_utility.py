"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 25/07/2021                       \n
@last-update            :  Wed 28/07/2021                       \n

Questo modulo raccoglie una serie di utility necessarie all'Event Sourcing
"""

from ..concrete_event_sourcing.KafkaEventStore                      import KafkaEventStore
from ..concrete_event_sourcing.AutoLearnLogEntity                   import AutoLearnLogEntity
from ..exception_manager.ExceptionManager                           import ExceptionManager
from ..abstract_event_sourcing.DomainEvent                          import DomainEvent
from ..time_stamp_manager.TimeStampManager                          import TimeStampManager

from typing                                                         import Union
import os
from logging                                                        import Logger,getLogger



def getLocalLogger (pServiceName:str) -> Logger:
    """
    # **getLocalLogger** 

    Preleva il logger locale dell'applicativo.

    Args:\n
        pServiceName        (str)       : nome del logger associato all'applicativo
    
    Returns:\n
        Logger                          : oggetto della classe logging.Logger
    """
    logger_name:str                                     = pServiceName + "__" + str ( os.getpid() )
    logger:Logger                                       = getLogger(logger_name)
    return logger


async def setUpEventSourcing (pServiceName:str, pEventStore:KafkaEventStore, pNetworkLogger:AutoLearnLogEntity , pEventStoreParams:dict) -> bool:
    """
    # **setUpEventSourcing** 

    Questa funzione permette di inizializzare i componenti necessari all'EventSourcing del microservizio Catalog.\n

    In particolar modo, la funzione effettua i seguenti tre passi:\n
        - Inizializzazione EventStore
        - Inizializzazione componente Log Comportamentale
        - Rewind Eventi Passati

    Args:\n
        pServiceName        (str)                   : nome del microservizio che utilizzera il componente di Logging comportamentale
        pEventStore         (KafkaEventStore)       : oggetto che si interfaccia con l'EventStore Kafka
        pNetworkLogger      (AutoLearnLogEntity)    : oggetto che permette di effetture il log comportamentale
        pEventStoreParams   (dict)                  : parametri di configurazione per la connessione con Kafka
    
    Returns:\n
        bool                                        : VERO se non si sono verificate eccezioni, falso altrimenti
    """
    #Prelievo logger
    logger:Logger                                       = getLocalLogger(pServiceName)

    #Setup Event Sourcing 
    event_store_conn:Union[None, Exception]             = await pEventStore.start(pEventStoreParams)

    #Init componente Event Sourcing
    pNetworkLogger.init(pServiceName, pEventStore)


    if ExceptionManager.lookForExceptions(event_store_conn):
        logger.error("ERROR | Impossibile connettersi con Kafka --> {} ".format(event_store_conn))
        
        return False
    else:
        #Tentativo di Rewind
        outcome:Union [ None , Exception ]              = await pNetworkLogger.rewind()
        if ExceptionManager.lookForExceptions(outcome):
            logger.error("ERROR | Impossibile fare rewind degli eventi :(\n-> Causa: {}".format(str(outcome)))
            return False

    return True


def make_behavioral_event (pKey:bytes , pTimeStamp:int , pSourceService:str , pDestinationService:str , pMessageType:str , pComType:str , pPayload:str) -> DomainEvent:
    """
    # **make_behavioral_event** 

    Questa funzione permette di costruire un record comportamentale del Sistema Outlearn.

    Args:\n
        pKey                (bytes)     : chiave del record
        pTimeStamp          (int)       : timestamp
        pSourceService      (str)       : servizio sorgente della comunicazione
        pDestinationService (str)       : servizio destinazione della comunicazione
        pMessageType        (str)       : tipo messaggio. ("send" o "receive")
        pComType            (str)       : tipo comunicazione ("sync" o "async")
        pPayload            (str)       : payload del record, rappresenta un'azione richiesta dal componente sorgente a quello di destinazione

    Returns:\n
        DomainEvent                     : evento che modifica lo stato del microservizio
    """
    record:dict                                 = {}

    #Fill dizionario 
    record["key"]                               = pKey
    record["value"]                             = {}
    record["value"]["source_service"]           = pSourceService
    record["value"]["destination_service"]      = pDestinationService
    record["value"]["message_type"]             = pMessageType
    record["value"]["com_type"]                 = pComType
    record["value"]["payload"]                  = pPayload
    record["timestamp"]                         = pTimeStamp

    client_request_event:DomainEvent            = DomainEvent(pSourceService , pTimeStamp , record)

    return client_request_event


async def final_communication_log (pService:str, pDestId:str, pComType:str , pPayload:str ,pNetworkLogger:AutoLearnLogEntity) -> None:
    """
    # **final_communication_log**
    
    Questa funzione rappresenta un FastAPI Background Task.\n

    Tale funzione permette di scrivere il record comportamentale associato alla risposta del Server ad una richiesta del Cliente

    Args:\n
        pService             (str)                  : server
        pDestId              (str)                  : client
        pComType             (str)                  : tipo di comunicazione ("sync" o "async")
        pPayload             (str)                  : payload della comunicazione
        pNetworkLogger       (AutoLearnLogEntity)   : componente che fa loggin sull'EventStore

    Raises:\n
        Exception                                   : eccezione derivata dalla scrittura sull'EventStore oppure dalla chiusura della connessione con quest'ultimo

    """
    #[1] Prelievo logger
    logger:Logger                                       = getLocalLogger(pService)

    #[2] Scrittura record comportamentale associato alla risposta del Server ad una richiesta del Cliente
    current_time:int                                    = TimeStampManager.currentTimeStampInMS()
    client_req_ans:DomainEvent                          = make_behavioral_event(pDestId.encode("ascii") , current_time , pService , pDestId, "send" , pComType , pPayload)
    
    outcome:Union[ None , Exception]                    = await pNetworkLogger.emit(client_req_ans)
    if ExceptionManager.lookForExceptions(outcome):
        logger.error("ERROR | Impossibile scrivere evento di fine Comunicazione - Causa: {}".format( str( outcome ) ))

    #[3] Stop Connessione con EventStore
    await pNetworkLogger._eventStore.stop()