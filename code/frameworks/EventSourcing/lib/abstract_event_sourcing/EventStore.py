"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 25/07/2021                       \n
@last-update            :  Sun 25/07/2021                       \n

Questo componente rappresenta un'interfaccia (o astrazione) ai componenti che si interfacciano con l'Event-Store con l'obbiettivo di leggere e scrivere dati su quest'ultimo.

"""

from abc            import ABC, ABCMeta, abstractmethod
from typing         import List, Union
from .DomainEvent   import DomainEvent


class EventStore (ABC, metaclass=ABCMeta):

    __slots__                           = ( "_readModel" , "_writeModel")

    @abstractmethod
    async def start(self, pParams:dict)              -> Union [ None , Exception ]:
        """
        Metodo che configura gli oggetti che leggono/scrivono sull'EventStore.\n

        In particolar modo, viene avviata una connessione con l'Event-Store.

        Args:\n
            pParams     (dict)      : parametri di configurazione

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception               : errore di connessione
        """
        pass


    @abstractmethod
    async def stop(self, pParams:dict=None)          -> Union [ None , Exception ]:
        """
        Metodo che stoppa la connessione con l'Event-Store

        Args:\n
            pParams     (dict | DEF = None)         : eventuali parametri per la disconnesione

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                               : errore di connessione
        """
        pass


    @abstractmethod
    async def read(self, pParams:dict = None)        -> Union [ List[dict] , Exception ]:
        """
        Metodo che preleva gli Eventi associati ad un Entità dall'Event-Store.

        Args:\n
            pParams         (dict | DEF = None) : eventuali parametri che regolano la lettura degli eventi

        Returns:\n
            Union [ List[dict] , Exception ]

        Raises:\n
            Exception                           : errore di lettura dall'EventStore
        """
        pass


    @abstractmethod
    async def write(self, pEvent:DomainEvent)        -> Union [ None , Exception ]:
        """
        Metodo che preleva gli Eventi associati ad un Entità dall'Event-Store.

        Args:\n
            pEvent         (DomainEvent)        : evento da scrivere sull'Event-Store

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                           : errore di scrittura dall'EventStore
        """
        pass

