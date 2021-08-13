"""
@author           	    :  rscalia                              \n
@build-date             :  Thu 12/08/2021                       \n
@last-update            :  Thu 12/08/2021                       \n

Questo componente serve per prelevare la configurazione dell'applicativo AutoLearn
"""
import configparser
from typing                 import Union , List, Tuple


UNABLE_TO_READ_CFG:int                                          = 1


class ClientConfigurator (object):

    __slots__= ( 
                    "_config",
                    "HTTP_REQ_TIME_OUT_IN_SEC",
                    "CATALOG_RETENTATION_TIME_IN_DAYS",
                    "CATALOG_SERVICE_NAME",
                    "CATALOG_BASE_ADDRESS",
                    "CATALOG_ACTIONS",
                    "TRAINING_SERVICE_NAME",
                    "TRAINING_BASE_ADDRESS",
                    "TRAINING_ACTIONS",
                    "EVALUATION_SERVICE_NAME",
                    "EVALUATION_BASE_ADDRESS",
                    "EVALUATION_ACTIONS",
                    "SESSION_SERVICE_NAME",
                    "SESSION_BASE_ADDRESS",
                    "SESSION_ACTIONS",
                    "STORAGE_SERVICE_NAME",
                    "STORAGE_BASE_ADDRESS",
                    "STORAGE_ACTIONS",
                    "SERVICES_LIST"
    )
    def inspect(self) -> Union [ None , Exception ]:
        """
        Legge il file di configurazione e memorizza il suo contenuto nell'oggetto corrente

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception   : eccezione da lettura file
        """
        #Avvio parsing
        self._config                                            = configparser.ConfigParser(allow_no_value=True)
        try:
            self._config.read("config/cfg.conf")
            
        except Exception as exp:
            print ("[!] Errore nella lettura del file di configurazione \n-> Causa: {} \n-> Arresto applicazione !".format( str( exp ) ))
            exit(UNABLE_TO_READ_CFG)


        sections:List[str]                                      = self._config.sections()


        #Memorizzazione Informazioni sull'oggetto corrente
        try:
            if 'Connection' in sections:
                s:str                                           = 'Connection'
                self.HTTP_REQ_TIME_OUT_IN_SEC:int               = int ( self._config.get(s, 'HTTP_REQ_TIME_OUT_IN_SEC') )


            if 'Catalog Retentation Logic' in sections:
                s:str                                           = "Catalog Retentation Logic"
                self.CATALOG_RETENTATION_TIME_IN_DAYS:int       = int ( self._config.get(s, 'CATALOG_RETENTATION_TIME_IN_DAYS') )


            if 'Catalog Service' in sections:
                s:str                                           = 'Catalog Service'
                self.CATALOG_SERVICE_NAME:str                   = self._config.get(s, 'CATALOG_SERVICE_NAME')
                self.CATALOG_BASE_ADDRESS:str                   = self._config.get(s, 'CATALOG_BASE_ADDRESS')

                #Prelievo Azioni Catalog
                self.CATALOG_ACTIONS:List[ Tuple [ str, str , str , bool ] ] = []
                self.CATALOG_ACTIONS.append( 
                    self.extractActionSpec(s , "CATALOG_ACTIONS_GET_CATALOG_ID" , "CATALOG_ACTIONS_GET_CATALOG_ADDR" , "CATALOG_ACTIONS_GET_CATALOG_VERB" , "CATALOG_ACTIONS_GET_CATALOG_PARAMS" ) )

            
            if 'Training Service' in sections:
                s:str                                           = 'Training Service'
                self.TRAINING_SERVICE_NAME:str                  = self._config.get(s, 'TRAINING_SERVICE_NAME')
                self.TRAINING_BASE_ADDRESS:str                  = self._config.get(s, 'TRAINING_BASE_ADDRESS')

                #Prelievo Azioni Catalog
                self.TRAINING_ACTIONS:List[ Tuple [ str, str , str , bool ] ] = []
                self.TRAINING_ACTIONS.append( 
                    self.extractActionSpec(s , "TRAINING_ACTIONS_TRAINING_REQ_ID" , "TRAINING_ACTIONS_TRAINING_REQ_ADDR" , "TRAINING_ACTIONS_TRAINING_REQ_VERB" , "TRAINING_ACTIONS_TRAINING_REQ_PARAMS" ) )


            if 'Evaluation Service' in sections:
                s:str                                           = 'Evaluation Service'
                self.EVALUATION_SERVICE_NAME:str                = self._config.get(s, 'EVALUATION_SERVICE_NAME')
                self.EVALUATION_BASE_ADDRESS:str                = self._config.get(s, 'EVALUATION_BASE_ADDRESS')

                #Prelievo Azioni Catalog
                self.EVALUATION_ACTIONS:List[ Tuple [ str, str , str , bool ] ] = []
                self.EVALUATION_ACTIONS.append( 
                    self.extractActionSpec(s , "EVALUATION_ACTIONS_EVALUATION_REQ_ID" , "EVALUATION_ACTIONS_EVALUATION_REQ_ADDR" , "EVALUATION_ACTIONS_EVALUATION_REQ_VERB" , "EVALUATION_ACTIONS_EVALUATION_REQ_PARAMS" ) )


            if 'Session Service' in sections:
                s:str                                           = 'Session Service'
                self.SESSION_SERVICE_NAME:str                   = self._config.get(s, 'SESSION_SERVICE_NAME')
                self.SESSION_BASE_ADDRESS:str                   = self._config.get(s, 'SESSION_BASE_ADDRESS')

                #Prelievo Azioni Catalog
                self.SESSION_ACTIONS:List[ Tuple [ str, str , str , bool ] ] = []
                self.SESSION_ACTIONS.append( 
                    self.extractActionSpec(s , "SESSION_ACTIONS_VIEW_SESSIONS_REQ_ID" , "SESSION_ACTIONS_VIEW_SESSIONS_REQ_ADDR" , "SESSION_ACTIONS_VIEW_SESSIONS_REQ_VERB" , "SESSION_ACTIONS_VIEW_SESSIONS_REQ_PARAMS" ) )

                self.SESSION_ACTIONS.append( 
                    self.extractActionSpec(s , "SESSION_ACTIONS_SAVE_SESSION_REQ_ID" , "SESSION_ACTIONS_SAVE_SESSION_REQ_ADDR" , "SESSION_ACTIONS_SAVE_SESSION_REQ_VERB" , "SESSION_ACTIONS_SAVE_SESSION_REQ_PARAMS" ) )


            if 'Storage Service' in sections:
                s:str                                           = 'Storage Service'
                self.STORAGE_SERVICE_NAME:str                   = self._config.get(s, 'STORAGE_SERVICE_NAME')
                self.STORAGE_BASE_ADDRESS:str                   = self._config.get(s, 'STORAGE_BASE_ADDRESS')

                #Prelievo Azioni Catalog
                self.STORAGE_ACTIONS:List[ Tuple [ str, str , str , bool ] ] = []
                self.STORAGE_ACTIONS.append( 
                    self.extractActionSpec(s , "STORAGE_ACTIONS_VIEW_EXPERIMENTS_ID" , "STORAGE_ACTIONS_VIEW_EXPERIMENTS_ADDR" , "STORAGE_ACTIONS_VIEW_EXPERIMENTS_VERB" , "STORAGE_ACTIONS_VIEW_EXPERIMENTS_PARAMS" ) )


            #Costruzione Lista Servizi
            catalog:dict                            = {
                                                        "recipient_name"  : self.CATALOG_SERVICE_NAME ,
                                                        "base_address"    : self.CATALOG_BASE_ADDRESS  ,
                                                        "actions"         : self.CATALOG_ACTIONS
                                                      }

            training:dict                           = {
                                                        "recipient_name"  : self.TRAINING_SERVICE_NAME ,
                                                        "base_address"    : self.TRAINING_BASE_ADDRESS  ,
                                                        "actions"         : self.TRAINING_ACTIONS
                                                      }

            evaluation:dict                         = {
                                                        "recipient_name"  : self.EVALUATION_SERVICE_NAME ,
                                                        "base_address"    : self.EVALUATION_BASE_ADDRESS  ,
                                                        "actions"         : self.EVALUATION_ACTIONS
                                                      }

            session:dict                            = {
                                                        "recipient_name"  : self.SESSION_SERVICE_NAME ,
                                                        "base_address"    : self.SESSION_BASE_ADDRESS  ,
                                                        "actions"         : self.SESSION_ACTIONS
                                                     }


            storage:dict                            = {
                                                        "recipient_name"  : self.STORAGE_SERVICE_NAME ,
                                                        "base_address"    : self.STORAGE_BASE_ADDRESS  ,
                                                        "actions"         : self.STORAGE_ACTIONS    
                                                      }

            self.SERVICES_LIST:List[dict]           = [ catalog , training , evaluation , session , storage ]


        except Exception as exp:
            print ("[!] Errore nella lettura del file di configurazione \n-> Causa: {} \n-> Arresto applicazione !".format( str( exp ) ))
            exit(UNABLE_TO_READ_CFG)

            
    def extractActionSpec(self, pCfgSection:str , pCfgId:str , pCfgAddr:str , pCfgVerb:str , pCfgParams:str ) -> Tuple [ str, str , str , bool ]:
        """
        Questo metodo permette di estrapolare le info principali per ogni azione supportata dal backend

        Args:\n
            pCfgSection             (str)       : sezione del file di configurazione che contiene le informazioni
            pCfgId                  (str)       : nome dell'azione
            pCfgAddr                (str)       : porzione finale del base_address che permette di innescare l'azione
            pCfgVerb                (str)       : verbo HTTP dell'azione
            pCfgParams              (bool)      : VERO se l'azione richiede il passaggio di parametri , FALSO altrimenti

        Returns:
            Tuple [ str, str , str , bool ]     : Formato:\n
                                                    - **0** : Nome Servizio
                                                    - **1** : porzione finale del base_address che permette di innescare l'azione
                                                    - **2** : Verbo HTTP associato all'azione
                                                    - **3** : booleano che indica se l'azione necessità il passaggio di parametri

        Raises:\n
            Exception                           : eccezione derivata dal prelievo di informazioni dal file di configurazione
        """
        action_id:str                                           = self._config.get(pCfgSection, pCfgId)
        action_addr:str                                         = self._config.get(pCfgSection, pCfgAddr)
        action_verb:str                                         = self._config.get(pCfgSection, pCfgVerb)
        action_params:bool                                      = True if self._config.get(pCfgSection, pCfgParams) == "1" else False

        service_actions:tuple                                   = ( action_id , action_addr , action_verb , action_params )
        return service_actions