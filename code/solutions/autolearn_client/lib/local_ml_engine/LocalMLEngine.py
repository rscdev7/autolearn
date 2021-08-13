"""
@author           	    :  rscalia                              \n
@build-date             :  Thu 12/08/2021                       \n
@last-update            :  Fri 13/08/2021                       \n

Questo componente rappresenta l'implementazione di un Remote Proxy (e di un Forwarder del DP Forwarder-Receiver) atto a fornire al client un'interfaccia "locale" per gestire gli esperimenti di ML.
"""

from ..abstract_network_communicator.NetworkCommunicator        import NetworkCommunicator
from ..time_stamp_manager.TimeStampManager                      import TimeStampManager
from ..exception_manager.ExceptionManager                       import ExceptionManager
from ..client_config.ClientConfigurator                         import ClientConfigurator
from typing                                                     import Union, List
from ..network_serializer.NetworkSerializer                     import NetworkSerializer
from ..concrete_network_communicator.AsyncHTTPCommunicator      import AsyncHTTPCommunicator

class LocalMLEngine (object):


    def __init__(self , pCfg:ClientConfigurator) -> object:
        """
        Costruttore

        Args:\n
            pCfg                    (ClientConfigurator)    : configurazione applicativo
        """
        #Collect Cfg info
        self._communicator:NetworkCommunicator      = None

        self._catalogServiceID:str                  = pCfg.CATALOG_SERVICE_NAME
        self._catalogReqGetCatalog:str              = pCfg.CATALOG_ACTIONS[0][0]

        self._trainingServiceID:str                 = pCfg.TRAINING_SERVICE_NAME
        self._trainingReqTrainModel:str             = pCfg.TRAINING_ACTIONS[0][0]

        self._evaluationServiceID:str               = pCfg.EVALUATION_SERVICE_NAME
        self._evaluationReqEvalModel:str            = pCfg.EVALUATION_ACTIONS[0][0]

        self._sessionServiceID:str                  = pCfg.SESSION_SERVICE_NAME
        self._sessionReqViewSessions:str            = pCfg.SESSION_ACTIONS[0][0]
        self._sessionReqSaveSession:str             = pCfg.SESSION_ACTIONS[1][0]

        self._storageServiceID:str                  = pCfg.STORAGE_SERVICE_NAME
        self._storageReqViewExps:str                = pCfg.STORAGE_ACTIONS[0][0]


        #Init Crypt Engine
        self._serializer:NetworkSerializer          = NetworkSerializer()
        outcome:Union[ None , Exception ]           = self._serializer.readKeyFromFile()

        self._cryptEngineReady:bool                 = True if ExceptionManager.lookForExceptions(outcome) == False else False


        #Collect Communicator Info
        self._servicesList:List[dict]               = pCfg.SERVICES_LIST 
        self._connParams:dict                       = { 'timeout' : pCfg.HTTP_REQ_TIME_OUT_IN_SEC }


    async def start (self , pParams:dict=None ) -> Union [ None , Exception ]:
        """
        Questo metodo permette di effettuare lo start del communicator del LocalMLEngine

        Args:\n
            pParams                 (dict | DEF = None)         : eventuali parametri di start

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                                           : errore nello start del LocalMLEngine
        """
        self._communicator:AsyncHTTPCommunicator                = AsyncHTTPCommunicator()

        # [1] SetUp Communicator
        outcome:Union[ None , Exception]                        = await self._communicator.setUp( self._servicesList , self._connParams )
        
        if ExceptionManager.lookForExceptions(outcome):
            print ("\n[!] ERRORE, impossibile effettuare setup LocalMLEngine \n-> Causa: {}".format(outcome))
            return outcome

        # [2] Start Communicator
        outcome:Union[ None , Exception]                        = self._communicator.start()
        if ExceptionManager.lookForExceptions(outcome):
            print ("\n[!] ERRORE, impossibile effettuare setup LocalMLEngine \n-> Causa: {}".format(outcome))
            return outcome
    

    async def stop(self, pParams:dict=None) -> Union [ None , Exception ]:
        """
        Questo metodo permette di effettuare lo stop del communicator del LocalMLEngine

        Args:\n
            pParams                 (dict | DEF = None)         : eventuali parametri di stop

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                                           : errore nello stop del LocalMLEngine
        """
        outcome:Union[ None , Exception]                        = await self._communicator.stop()
        if ExceptionManager.lookForExceptions(outcome):
            print ("\n[!] ERRORE, impossibile effettuare stop LocalMLEngine \n-> Causa: {}".format(outcome))
            return outcome


    async def getCatalog (self) -> Union [ dict , Exception ]:
        """
        Questo metodo permette di prelevare il catalogo contenente la Lista dei Dataset e Modelli (comprensivi di settaggi) disponibili per l'applicativo.

        Returns:\n
            Union [ dict , Exception ]

        Raises:\n
            Exception                               : eccezione durante il prelievo del catalogo
        """
        outcome:Union [ dict , Exception ]          = await self._communicator.request(self._catalogServiceID , self._catalogReqGetCatalog)

        return outcome


    async def trainMLModel (self, pTrainParams:dict) -> Union [ str , Exception , dict ]:
        """
        Questo metodo permette di addestrare un Modello di Machine Learning

        Args:\n
            pTrainParams                (dict)      : parametri di training. \n
                                                      Per il formato del dizionario, vedere la documentazione del Baclend

        Returns:\n
            Union [ str , Exception , dict ]

        Raises:\n
            Exception                               : eccezione durante il training del Modello di ML
        """
        outcome:Union [ dict , Exception ]          = await self._communicator.request(self._trainingServiceID , self._trainingReqTrainModel , pTrainParams)

        return self._returnOpOutcome(outcome)


    async def evaluateMLModel (self, pSessID:int) -> Union [ str , Exception , dict ]:
        """
        Questo metodo permette di valutare un Modello di ML precedentemente addestrato.

        Args:\n
            pSessID                (int)            : ID di Sessione del Modello di ML. 

        Returns:\n
            Union [ str , Exception , dict ]

        Raises:\n
            Exception                               : eccezione durante l'evaluation del Modello di ML
        """
        # [1] Check presenza engine crittografico
        if self._cryptEngineReady == False:
            return SystemError("[!] Impossibile cifrare id di sessione a causa di problemi all'engine crittografico del sistema, richiesta rigettata")


        # [2] Cifratura ID di Sessione Passato dall'utente
        crypt_id_sess:Union[ str , Exception]       = self._serializer.encryptField( str(pSessID) )
        if ExceptionManager.lookForExceptions(crypt_id_sess):
            return crypt_id_sess

        crypt_id_sess_dict:dict                     = { 'payload' : crypt_id_sess }


        # [3] Valutazione Modello di ML
        outcome:Union [ dict , Exception ]          = await self._communicator.request(self._evaluationServiceID , self._evaluationReqEvalModel , crypt_id_sess_dict)

        return self._returnOpOutcome(outcome)


    async def viewSessionData (self) -> Union [ dict , Exception ]:
        """
        Questo metodo permette di visualizzare i dati di sessione dell'applicativo.

        Returns:\n
            Union [ dict , Exception ]

        Raises:\n
            Exception                               : eccezione durante la query in merito ai dati di sessione
        """
        # [0] Query in merito ai dati di Sessione
        outcome:Union [ dict , Exception ]              = await self._communicator.request(self._sessionServiceID , self._sessionReqViewSessions )

        
        # [2] Decifratura Chiavi Sessione Record
        if ExceptionManager.lookForExceptions(outcome) == False and len( outcome['experiments'] )  >=1 :

            # [2.1] Verifica disponibilità engine crittografico
            if self._cryptEngineReady == False:
                return SystemError("[!] Impossibile cifrare id di sessione a causa di problemi all'engine crittografico del sistema, richiesta rigettata")


            decrypted_experiments:List[dict]    = list( map ( lambda x: self.decryptRecordIdSess(x) , outcome['experiments'] ) )
            check_for_exception:List[dict]      = list ( filter ( lambda x: ExceptionManager.lookForExceptions( x['timestamp'] ) , decrypted_experiments  ) )


            if len(check_for_exception) == 0:
                outcome['experiments']          = decrypted_experiments
            else:
                return Exception("[!] Errore durante la decifratura dei Record di Sessione")
        

        return outcome


    def decryptRecordIdSess (self, pRecord:dict) -> Union [ dict , Exception ]:
        """ 
        Questo metodo permette di decifrare un'id di sessione presente in un record del DB Session

        Args:\n
            pRecord                 (dict)      : record di sessione
        
        Returns:\n
            Union [ dict , Exception ]

        Raises:\n
            Exception                           : eccezione durante la decifratura
        """
        pRecord['timestamp']                    = int( self._serializer.decryptField( pRecord['timestamp'] ) )
        return pRecord


    async def saveSession (self , pSessID:int ) -> Union [ str , Exception , dict ]:
        """
        Questo metodo permette di salvare una sessione nello storage permanente.

        Args:\n
            pSessID                (int)            : ID della Sessione che si vuole Salvare. 

        Returns:\n
            Union [ str , Exception , dict ]

        Raises:\n
            Exception                               : eccezione durante il salvataggio della Sessione
        """
        # [1] Check presenza engine crittografico
        if self._cryptEngineReady == False:
            return SystemError("[!] Impossibile cifrare id di sessione a causa di problemi all'engine crittografico del sistema, richiesta rigettata")


        # [2] Cifratura ID di Sessione Passato dall'utente
        crypt_id_sess:Union[ str , Exception]       = self._serializer.encryptField( str(pSessID) )
        if ExceptionManager.lookForExceptions(crypt_id_sess):
            return crypt_id_sess

        crypt_id_sess_dict:dict                     = { 'id_sess_cf' : crypt_id_sess }


        # [3] Salvo la Sessione
        outcome:Union [ dict , Exception ]          = await self._communicator.request(self._sessionServiceID , self._sessionReqSaveSession , crypt_id_sess_dict )

        return self._returnOpOutcome(outcome)


    async def viewExperiments (self) -> Union [ dict , Exception ]:
        """
        Questo metodo permette di visualizzare gli esperimenti effettuati in passato

        Returns:\n
            Union [ dict , Exception ]

        Raises:\n
            Exception                               : eccezione durante la query in merito ai dati degli esperimenti
        """
        outcome:Union [ dict , Exception ]          = await self._communicator.request(self._storageServiceID , self._storageReqViewExps )

        return outcome


    def _returnOpOutcome(self, pReqOut:Union[ dict , Exception ] ) -> Union[ str , Exception , dict ]:
        """
        Questo metodo permette di restituire al cliente i risultati delle operazioni invocate

        Args:\n
            pReqOut                 (Union[ dict , Exception ])     : oggetto contente il risultato dell'operazione invocata dal client

        Returns:\n
            Union[ str , Exception , dict ]                         : Casi:\n
                                                                        - **str**, stringa rappresentante l'esito dell'operazione
                                                                        - **dict**, impossibile comprendere l'esito della richiesta invocata dal client
                                                                        - **Exception**, eccezione durante l'esecuzione della richiesta invocata dal cliente
        """
        if type(pReqOut) == dict and 'payload' in pReqOut.keys():
            return pReqOut['payload']

        if type(pReqOut) == dict and 'message' in pReqOut.keys():
            return pReqOut['message']   

        if ExceptionManager.lookForExceptions(pReqOut):
            return pReqOut

        return { 'type_error_data' : pReqOut  }