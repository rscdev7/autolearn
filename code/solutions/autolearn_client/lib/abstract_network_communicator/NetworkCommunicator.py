"""
@author           	    :  rscalia                              \n
@build-date             :  Thu 10/08/2021                       \n
@last-update            :  Thu 10/08/2021                       \n

Questo componente serve per costruire un interfaccia che permette ad un applicativo Python di accedere a dei servizi remoti in maniera uniforme indipendnetemente dalla tecnologia di comunicazione impiegata.
"""
from typing                                         import List, Union
from abc                                            import ABC, ABCMeta, abstractmethod
        

class NetworkCommunicator (ABC, metaclass=ABCMeta):

    __slots__ = ( "_networkEngine" ,
                  "_serializer",
                  "_connData",
                  "_recipients" )
    @abstractmethod
    def setUp(self, pRecipients:List[dict] , pConnData:dict = None ) -> Union [ None , Exception ]:
        """
        Questo metodo permette di configurare la connessione che permettera' di comunicare successivamente con host remoti.

        Args:\n
            pRecipients             (List[dict])        : destinatari connessione
            pConnData               (dict | DEF = None) : parametri configurazione connessione

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                                   : errori di configurazione connessione  
        """
        pass


    @abstractmethod
    def start (self, pParams:dict = None) -> Union[None , Exception]:
        """
        Questo metodo permette di avviare la connessione precedentemente configurata

        Args:\n
            pParams             (dict | DEF = None)          : eventuali parametri di avvio della connessione

        Returns:\n
            Union[None , Exception]

        Raises:\n
            Exception                                        : errori nell'avvio della connessione
        """
        pass


    @abstractmethod
    def stop (self, pParams:dict = None) -> Union[None , Exception]:
        """
        Questo metodo permette di chiudere la connessione precedentemente avviata

        Args:\n
            pParams             (dict | DEF = None)          : eventuali parametri di stop della connessione

        Returns:\n
            Union[None , Exception]

        Raises:\n
            Exception                                        : errori nella chiusura della connessione
        """
        pass


    @abstractmethod
    def isConnected(self) -> bool:
        """
        Questo metodo permette di verificare se è presente una connessione attiva con la rete.

        Returns:\n
            bool                            : VERO se è presente una connessione avviata, FALSO altrimenti
        """
        pass


    @abstractmethod
    def send (self, pData:object , pRecipient:str , pParams:dict = None) -> Union[None , Exception]:
        """
        Questo metodo permette di inoltrare dei dati ad un destinatario presente nella lista di setup.

        Args:\n
            pData                   (object)                : dati da inviare
            pRecipient              (str)                   : destinatario
            pParams                 (dict | DEF = None)     : eventuali parametri di invio

        Returns:\n
            Union[None , Exception]                         

        Raises:\n
            Exception                                       : errore durante l'invio dei dati al destinatario
        """
        pass


    @abstractmethod
    def receive (self, pEntity:str , pParams:dict = None) -> Union [ object , Exception ]:
        """
        Questo metodo permette di ricevere dati da un destinatario.

        Args:\n
            pEntity                 (str)                   : destinatario
            pParams                 (dict | DEF = None)     : eventuali parametri di ricezione

        Returns:\n
            Union [ object , Exception ]

        Raises:\n
            Exception                                       : errore ricezione dati
        """
        pass


    @abstractmethod
    def request (self, pRecipient:str , pReqType:str , pReqData:dict = None , pParams:dict = None) -> Union [ object , Exception ]:
        """
        Questo metodo permette di inoltrare una richiesta (comando, query su dato ecc...) ad un destinatario appartenente alla lista di destinatari di setup.

        Args:\n
            pRecipient                  (str)               : destinatario richiesta
            pReqType                    (str)               : tipo richiesta
            pReqData                    (dict | DEF = None) : eventuali dati richiesta
            pParams                     (dict | DEF = None) : eventuali parametri richiesta

        Returns:\n
            Union [ object , Exception ]

        Raises:\n
            Exception                                       : errore nella richiesta al destinatario   
        """
        pass