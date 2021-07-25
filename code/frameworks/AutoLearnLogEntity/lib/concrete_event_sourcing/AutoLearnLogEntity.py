"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 25/07/2021                       \n
@last-update            :  Sun 25/07/2021                       \n

Questo componente rappresenta un Entità di Log presente nell'applicativo 
"""

from ..abstract_event_sourcing.EventStore       import EventStore
from ..abstract_event_sourcing.DomainEvent      import DomainEvent
from ..abstract_event_sourcing.DomainEntity     import DomainEntity
from ..exception_manager.ExceptionManager       import ExceptionManager
from typing                                     import Union , List


class AutoLearnLogEntity (DomainEntity):

    __slots__       = ( "_status" , "_eventList" , "_eventStore" , "_entityId" )
    def init(self , pEntityId:str , pEventStore:EventStore) -> None:
        """
        Metodo che inizializza l'oggetto

        Args:\n
            pEntityId         (str)             : entità rappresentata dalla classe
            pEventStore       (EventStore)      : classe che si interfaccia con l'EventStore in modo tale da persistere gli eventi
        """
        self._status:str                    = "init"
        self._eventList:List[DomainEvent]   = []
        self._eventStore:EventStore         = pEventStore
        self._entityId:str                  = pEntityId


    async def emit(self, pEvent:DomainEvent) -> Union [ None , Exception ]:
        """
        Metodo che permette di segnalare e applicare un evento all'entità.

        Args:\n
            pEvent          (DomainEvent)   : evento da emettere e applicare

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                       : eccezione derivata dall'applicazione dell'evento, molto probabilmente scaturità da un problema di scrittura sull'Event-Store
        """
        outcome:Union [ None , Exception] = await self.apply(pEvent)
        self._eventList.append( pEvent )

        return outcome


    async def apply(self, pEvent:DomainEvent , pRewindMode=False) -> Union [ None , Exception ]:
        """
        Metodo che permette di cambiare lo stato dell'entità.

        Args:\n
            pEvent          (DomainEvent)                   : evento che modifica lo stato dell'entità
            pRewindMode     (bool | DEF = False)            : flag che permette di evitare la duplicazione degli eventi nell'Event-Store nel caso di Rewind

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                                       : eccezione derivata dall'applicazione dell'evento, molto probabilmente scaturità da un problema di scrittura sull'Event-Store
        """
        if (pRewindMode == False):
            outcome:Union [ None , Exception ]  = await self._eventStore.write(pEvent)
        else: 
            outcome                             = None

        self._status                            = pEvent._eventPayload["value"]["payload"]

        return outcome


    async def rewind (self) -> Union [ None , Exception ]:
        """
        Metodo che permette di ricostruire l'entità sfruttando tutti gli eventi che hanno modificato il suo stato iniziale.

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                       : eccezione derivata da un problema di lettura sull'Event-Store
        """
        retrieved_raw_events:Union[ List[dict] , Exception ] = await self._eventStore.read()

        if ExceptionManager.lookForExceptions(retrieved_raw_events):
            return retrieved_raw_events

        
        #Restore Events in right format
        self.reset()
        retrieved_events:List[DomainEvent]                   = []

        for raw_evt in retrieved_raw_events:
            event:dict         = {}
            event["key"]       = raw_evt["key"]
            event["value"]     = raw_evt["payload"]
            event["timestamp"] = raw_evt["timestamp_ms"]

            event:DomainEvent  = DomainEvent( self._entityId , event["timestamp"] , event)
            retrieved_events.append( event )

        #Rewind
        for event in retrieved_events:
            await self.apply( event , pRewindMode=True)
            self._eventList.append(event)


    def reset (self) -> None:
        """
        Metodo che permette di resettare l'Entità
        """
        self._eventList     = []
        self._status        = "init"
