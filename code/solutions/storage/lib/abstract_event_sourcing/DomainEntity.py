"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 25/07/2021                       \n
@last-update            :  Sun 25/07/2021                       \n

Questo componente rappresenta un'interfaccia all'Entità del Design Pattern Event Sourcing. 
"""

from .EventStore                                        import EventStore
from .DomainEvent                                       import DomainEvent
from ..exception_manager.ExceptionManager               import ExceptionManager
from ..singleton.Singleton                              import Singleton

from typing                                             import Union , List
from abc                                                import abstractmethod


class DomainEntity (object, metaclass=Singleton):

    __slots__       = ( "_status" , "_eventList" , "_eventStore" , "_entityId" )
    @abstractmethod
    def init(self , pEntityId:str , pEventStore:EventStore) -> None:
        """
        Metodo che inizializza l'oggetto

        Args:\n
            pEntityId         (str)             : entità rappresentata dalla classe
            pEventStore       (EventStore)      : classe che si interfaccia con l'EventStore in modo tale da persistere gli eventi
        """
        pass


    @abstractmethod
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
        pass


    @abstractmethod
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
        pass


    @abstractmethod
    async def rewind (self) -> Union [ None , Exception ]:
        """
        Metodo che permette di ricostruire l'entità sfruttando tutti gli eventi che hanno modificato il suo stato iniziale.

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                       : eccezione derivata da un problema di lettura sull'Event-Store
        """
        pass


    @abstractmethod
    def reset (self) -> None:
        """
        Metodo che permette di resettare l'Entità
        """
        pass
