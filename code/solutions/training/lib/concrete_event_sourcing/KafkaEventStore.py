"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 25/07/2021                       \n
@last-update            :  Sun 25/07/2021                       \n

Questo componente implementa l'interfaccia EventStore, per tanto quest'ultimo permette di implementare concretamente un componente che si interfaccia con l'Event-Store Kafka.
"""

from ..abstract_event_sourcing.EventStore       import EventStore
from ..abstract_event_sourcing.DomainEvent      import DomainEvent
from ..async_kafka_consumer.AsyncKafkaConsumer  import AsyncKafkaConsumer
from ..kafka_logger.KafkaLogger                 import KafkaLogger
from ..exception_manager.ExceptionManager       import ExceptionManager

from typing                                     import Union, List


class KafkaEventStore (EventStore):


    async def start (self, pParams:dict) -> Union [ None , Exception ]:
        """
        Questo metodo permette di avviare la connesione col broker Kafka.

        Args: \n
            pParams         (dict)      :   parametri di connesione \n
                                            Formato Parametri:\n
                                                - **host_name**   : str
                                                - **port**        : str
                                                - **topic**       : str
                                                - **partition**   : int

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception      : eccezione legata ad un errore di connesione col Broker Kafka
        """

        #Avvio Produttore Kafka
        self._writeModel:KafkaLogger                            = KafkaLogger(pParams["host_name"], pParams["port"] ,pParams["topic"], pParams["partition"])

        outcome:Union[ None , Exception ]                       = await self._writeModel.start()
        if ExceptionManager.lookForExceptions(outcome):
            return outcome


        #Avvio Consumatore Kafka
        self._readModel:AsyncKafkaConsumer                      = AsyncKafkaConsumer(pParams["host_name"], pParams["port"] ,pParams["topic"], pParams["partition"])

        outcome:Union[ None , Exception ]                       = await self._readModel.start()
        if ExceptionManager.lookForExceptions(outcome):
            return outcome

    
    async def stop (self, pParams:dict=None) -> Union [ None , Exception ]:
        """
        Questo metodo permette di chiudere la connesione col broker Kafka.

        Args:\n
            pParams     (dict | DEF = None)     : eventuali parametri di disconnesione

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception      : eccezione legata ad un errore di disconnesione col Broker Kafka
        """
        #Chiusura Connessione Produttore Kafka
        outcome:Union[ None , Exception ]                   = await self._writeModel.stop()
        if ExceptionManager.lookForExceptions(outcome):
            return outcome

        #Chiusura Connessione Consumatore Kafka
        outcome:Union[ None , Exception ]                   = await self._readModel.stop()
        if ExceptionManager.lookForExceptions(outcome):
            return outcome


    async def read (self, pParams:dict = None) -> Union [ List[dict] , Exception ]:
        """
        Metodo che preleva gli Eventi associati ad un Entità dall'Event-Store.

        Args:\n
            pParams         (dict | DEF = None) : eventuali parametri che regolano la lettura degli eventi

        Returns:\n
            Union [ List[dict] , Exception ] \n
            Formato Dizionari contenuti nella Lista:\n
                - **topic**                       : str
                - **partition**                   : int
                - **offset**                      : int
                - **key**                         : bytes
                - **timestamp_ms**                : int
                - **payload**                     : dict --> { ...  **payload** : _  ... }

        Raises:\n
            Exception                           : errore di lettura dall'EventStore
        """
        outcome:Union[ List[dict] , Exception ]             = await self._readModel._rewindTape()
        if ExceptionManager.lookForExceptions(outcome):
            return outcome
            
        outcome:Union[ List[dict] , Exception ]             = await self._readModel.consume()
        if ExceptionManager.lookForExceptions(outcome):
            return outcome

        return outcome


    async def write(self, pEvent:DomainEvent)        -> Union [ None , Exception ]:
        """
        Metodo che preleva gli Eventi associati ad un Entità dall'Event-Store.

        Args:\n
            pEvent         (DomainEvent)        : evento da scrivere sull'Event-Store \n
                                                  Formato Dizionario Payload:\n
                                                    - **key**: bytes
                                                    - **value**: 
                                                        - dict { ...  **payload** : _  ... }
                                                    - **timestamp**: int


        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                           : errore di scrittura dall'EventStore
        """
        #Estrazione dati necessari alla scrittura dall'ogetto di tipo DomainEvent
        key:bytes                           = pEvent._eventPayload["key"]
        value:dict                          = pEvent._eventPayload["value"]
        timestamp:int                       = pEvent._eventTimeStamp

        #Scrittura record nell'EventStore
        outcome:Union[ None , Exception ]   = await self._writeModel.log( key , value , timestamp )
        if ExceptionManager.lookForExceptions(outcome):
            return outcome