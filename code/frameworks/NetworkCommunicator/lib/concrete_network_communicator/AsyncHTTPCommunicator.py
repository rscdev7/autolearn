"""
@author           	    :  rscalia                              \n
@build-date             :  Thu 10/08/2021                       \n
@last-update            :  Thu 10/08/2021                       \n

Questo componente implementa l'interfaccia NetworkCommunicator
"""
from typing                                                 import List, Union
from ..abstract_network_communicator.NetworkCommunicator    import NetworkCommunicator
from ..http_engine.HTTPEngine                               import HTTPEngine
from ..network_serializer.NetworkSerializer                 import NetworkSerializer
from ..exception_manager.ExceptionManager                   import ExceptionManager


class AsyncHTTPCommunicator (NetworkCommunicator):


    __slots__ = ( "_networkEngine" ,
                  "_serializer",
                  "_connData",
                  "_recipients" )
    async def setUp(self, pRecipients:List[dict] , pConnData:dict = None ) -> Union [ None , Exception ]:
        """
        Questo metodo permette di configurare la connessione che permettera' di comunicare successivamente con host remoti.

        Args:\n
            pRecipients             (List[dict])        : destinatari connessione
                                                          Formato Dizionari presenti nella lista: \n
                                                            - **recipient_name**    : str
                                                            - **base_address**      : str
                                                            - **actions**           : List[ Tuple[ str ,str , str , bool ] ]
                                                                - **( request_name , req_address , "GET/POST" , bool_need_params )**


            pConnData               (dict | DEF = None) : parametri configurazione connessione. \n
                                                          Formato Dizionario: \n
                                                            - **timeout**       : int (timeout in secondi richiesta HTTP)

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                                   : errori di configurazione connessione  
        """
        try:
            if self.isConnected()                       : await self.stop() 
                
            self._connData:dict                         = pConnData
            self._recipients:List[dict]                 = pRecipients
            
            self._serializer:NetworkCommunicator        = NetworkSerializer()
            self._networkEngine:HTTPEngine              = HTTPEngine( self._connData['timeout'] )

        except Exception as exp:
            return exp


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
        try:
            self._networkEngine.startAsync()
        except Exception as exp:
            return exp


    async def stop (self, pParams:dict = None) -> Union[None , Exception]:
        """
        Questo metodo permette di chiudere la connessione precedentemente avviata

        Args:\n
            pParams             (dict | DEF = None)          : eventuali parametri di stop della connessione

        Returns:\n
            Union[None , Exception]

        Raises:\n
            Exception                                        : errori nella chiusura della connessione
        """
        outcome:Union[ None , Exception ]              = await self._networkEngine.closeAsync()
        if ExceptionManager.lookForExceptions(outcome) == False:
            del self._networkEngine

        return outcome


    def isConnected(self) -> bool:
        """
        Questo metodo permette di verificare se è presente una connessione attiva con la rete.

        Returns:\n
            bool                            : VERO se è presente una connessione avviata, FALSO altrimenti
        """
        return True if hasattr(self, '_networkEngine') else False


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
            NotImplementedError                             : questo metodo non è implementato per questa classe
        """
        raise NotImplementedError


    def receive (self, pEntity:str , pParams:dict = None) -> Union [ object , Exception ]:
        """
        Questo metodo permette di ricevere dati da un destinatario.

        Args:\n
            pEntity                 (str)                   : destinatario
            pParams                 (dict | DEF = None)     : eventuali parametri di ricezione

        Returns:\n
            Union [ object , Exception ]

        Raises:\n
            NotImplementedError                             : questo metodo non è implementato per questa classe
        """
        raise NotImplementedError


    async def request (self, pRecipient:str , pReqType:str , pReqData:dict = None , pParams:dict = None) -> Union [ object , Exception ]:
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
        try:
            
            # [1] Check Esistenza Destinatario
            recipient_search:List[dict]            = list ( filter ( lambda x: x['recipient_name'] == pRecipient , self._recipients ))
            if len(recipient_search) != 1:
                raise ValueError("[!] Il Destinatario scleto ({}) è inesistente".format(pRecipient))
            else:
                recipient_search:dict               = recipient_search[0]

            
            # [2] Check Esistenza Azione per il Destinatario Scelto
            recipient_action_search:List[dict]     = list ( filter ( lambda x: x[0] == pReqType , recipient_search['actions'] ))
            if len(recipient_action_search) != 1:
                raise ValueError("[!] L'azione richiesta non è disponibile per il Destinatario scelto ({})".format(pRecipient))
            else:
                recipient_action_search:dict        = recipient_action_search[0]


            # [3] Preparazione Esecuzione richiesta
            base_address:str                        = recipient_search['base_address']
            domain_address:str                      = recipient_action_search[1]
            final_address:str                       = base_address+domain_address
            action_kind:str                         = recipient_action_search[2]
            need_params:bool                        = recipient_action_search[3]


            # [3.1] Check Presenza Parametri passati dal chiamante ove necessario
            if need_params and pReqData == None:
                raise Exception ("[!] L'azione richiesta ({}-{}) richiede il passaggio dei parametri".format(pRecipient ,pReqType ))

            
            # [4] Esecuzione richiesta
            if action_kind == "GET" and need_params:
                outcome:Union[Dict[int, dict], Exception, Tuple[Exception, int]]   = await self._networkEngine.getAsync(final_address , pReqData)

            elif action_kind == "GET" and need_params == False:
                outcome:Union[Dict[int, dict], Exception, Tuple[Exception, int]]   = await self._networkEngine.getAsync(final_address)

            elif action_kind == "POST" :
                outcome:Union[Dict[int, dict], Exception, Tuple[Exception, int]]   = await self._networkEngine.postAsync(final_address , pReqData)

            else:
                raise ValueError("[!] Verbo HTTP ({}) non supportato".format(action_kind))
                

            # [5] Recupero risposta richiesta
            if ExceptionManager.lookForExceptions(outcome):
                return outcome

            if type(outcome) == tuple:
                return outcome[0]

            return outcome['payload']
            

        except Exception as exp:
            return exp
