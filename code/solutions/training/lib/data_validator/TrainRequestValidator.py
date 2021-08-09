"""
@author           	    :  rscalia                              \n
@build-date             :  Thu 03/08/2021                       \n
@last-update            :  Thu 03/08/2021                       \n

Questo componente serve per validare una richiesta di training del Cliente
"""

from typing import Union, List, Tuple


class TrainRequestValidator (object):

    @staticmethod
    def checkRequest ( pRequest:dict , pCatalog:dict ) -> Union[ bool , Tuple[ bool , str ] , Exception ]:
        """
        Questo metodo permette di effettuare il check delle richieste di Training da parte del client

        Args:\n
            pRequest                (dict)      : richiesta di training inoltrata dal client.\n
                                                  Formato Dizionario:\n
                                                    - **train_data**                    : dict
                                                        - **dataset**
                                                            - **dataset_name**          : str
                                                            - **dataset_task**          : str
                                                            - **split_test**            : float
                                                            - **split_seed**            : int

                                                        - **model**
                                                            - **model_name**            : str
                                                            - **model_task**            : str
                                                            - **model_hyperparams**     : List[HyperParam]
                                                        
                                                        - **learning**
                                                            - **loss**                  : str
                                                            - **learning_algorithm**    : str
                                                            - **learning_hyperparams**  : List[HyperParam]

                                                    - **HyperParam**:
                                                        - **hyper_param_name**          : str
                                                        - **hyper_param_value**         : Union[ float , int , bool , str , List[float] , List[str] , List[int] ]


            pCatalog                (dict)      : catalogo di training.
                                                  Formato Dizionario:\n
                                                    - **data_lake**                     : List[Dataset]
                                                        - **Dataset**                   : dict
                                                            - **dataset_name**          : str
                                                            - **dataset_task**          : str
                                                            - **dataset_description**   : str  
                                                            - **features**              : List[str]
                                                            - **label**                 : List[str]
                                                            - **n_record**              : int
                                                            - **pre-processing**        : List[Seq_computation]
                                                                - **Seq_computation**   : dict
                                                                    - **step**          : int
                                                                    - **computation**   : str
                                                        
                                                        - **models**                    : List[Model]
                                                            - **model_name**            : str
                                                            - **model_task**            : str
                                                            - **model_hyperparams**     : List[ParamSpec]
                                                        
                                                        - **metrics**                   : Metric
                                                            - **metric_task**           : str
                                                            - **metric_name**           : str
                                                        
                                                        - **learning**                  : List[Learning]
                                                            - **model_reference**       : ModelReference
                                                                - **model_name**        : str
                                                                - **model_task**        : str
                                                            
                                                            - **loss**                  : str
                                                            - **learning_algorithm**    : str
                                                            - **learning_hyperparams**  : List[ParamSpec]

                                                    - **ParamSpec**                     : dict
                                                        - **param_name**                : str
                                                        - **param_type**                : str
                                                        - **default**                   : Union[ float , int , bool , str , List[float] , List[str] , List[int] ]
                                                        - **range_l**                   : str
                                                        - **range_u**                   : str
                                                        - **options**                   : List[str]

        Returns:\n
            Union[ bool , Tuple[bool , str ] , Exception ]  : True se la richiesta è corretta; altrimenti (FALSE , MSG_ERRORE) oppure Eccezione se il formato della richiesta/catalogo è diverso rispetto a quello sopra elencato.

        Raises:\n
            Exception                                        : eccezione derivata dall'assenza di una chiave nel dizionario
        """
        try:
            # [1] Check Correttezza Dataset Name
            req_dataset_name:str                                    = pRequest['train_data']['dataset']['dataset_name']
            catalog_datasets_name:List[str]                         = list ( map ( lambda x: x['dataset_name'] , pCatalog['data_lake'] ) )

            check__req_dataset_name:bool                            = req_dataset_name in catalog_datasets_name
            if check__req_dataset_name == False:
                err_msg:str                                         = "[!] Il dataset {} non è presente nel Catalogo".format(req_dataset_name)
                return ( False , err_msg )

            # [2] Check Correttezza Dataset Task
            req_dataset_task:str                                    = pRequest['train_data']['dataset']['dataset_task']
            catalog_datasets_task:List[str]                         = list ( filter ( lambda x: x['dataset_name'] == req_dataset_name and x['dataset_task'] == req_dataset_task , pCatalog['data_lake'] ) )

            check__req_dataset_task:int                             = len( catalog_datasets_task ) > 0
            if check__req_dataset_task == 0:
                err_msg:str                                         = "[!] Il Task {} non è disponibile per il Dataset Scelto ({})".format(req_dataset_task , req_dataset_name)
                return ( False , err_msg )
            
            # [3] Check correttezza Parametro Split Dataset
            req_dataset_split:float                                 = pRequest['train_data']['dataset']['split_test']    
            if req_dataset_split < 0.0 or req_dataset_split > 1.0:
                err_msg:str                                         = "[!] Lo split selezionato ({}) deve essere un numero compreso fra 0 e 1".format(req_dataset_split)
                return ( False , err_msg )


            # [4] Check Correttezza Modello e Task Scelti
            req__model_name_task:tuple                              = ( pRequest['train_data']['model']['model_name'] ,  pRequest['train_data']['model']['model_task'] )
            
            catalog_models_names:list                               = list ( map( lambda x: x["model_name"] , pCatalog['models'] ) )
            catalog_models_task:list                                = list ( map( lambda x: x["model_task"] , pCatalog['models'] ) )
            
            catalog_model_task_pairs:List[tuple]                    = list ( zip( catalog_models_names , catalog_models_task  ) )
            
            check_model_name_task:bool                              = req__model_name_task in catalog_model_task_pairs
            if check_model_name_task == False:
                err_msg:str                                         = "[!] La coppia Modello-Task {} non è disponibile nel Catalogo".format(req__model_name_task)
                return ( False , err_msg )                 


            # [5] Il Task dichiarato nel Modello deve combaciare con quello del dataset
            if req__model_name_task[1] != req_dataset_task:
                err_msg:str                                         = "[!] Il Task scelto per il Modello ({}) non combacia col task scelto per il dataset ({})".format(req__model_name_task[1] , req_dataset_task)
                return ( False , err_msg )   


            # [6] Check Iperparametri Modello
            if "model_hyperparams" in pRequest['train_data']['model'].keys() and pRequest['train_data']['model']["model_hyperparams"] != None:
                req_model_hyperparams:List[dict]                        = pRequest['train_data']['model']['model_hyperparams']  
                
                catalog_filtered_models:List[dict]                      = list ( filter ( lambda x: x['model_name'] == req__model_name_task[0] and x['model_task'] == req__model_name_task[1] and "model_hyperparams" in x.keys(), pCatalog['models'] ) )
                

                if len( catalog_filtered_models ) > 0:
                    catalog_filtered_hyperparams:List[dict]                 = list ( map ( lambda x: x['model_hyperparams'] , catalog_filtered_models ) )[0]

                    outcome:Union[ bool , Tuple[ bool, str ] , Exception ]  = TrainRequestValidator.checkHyperparams( req_model_hyperparams , catalog_filtered_hyperparams , req__model_name_task  )
                    
                    if issubclass( type( outcome ) , Exception) or type(outcome) == tuple:
                        return outcome

                else:
                    err_msg:str                                         = "[!] La coppia Modello-Task {} non supporta Iperparametri".format(req__model_name_task)
                    return ( False , err_msg )   

            
            
            # [7] Check Parametri di Learning 
            if "learning" in pRequest['train_data'].keys() and pRequest['train_data']['learning'] != None and "loss" in pRequest['train_data']['learning'].keys() and pRequest['train_data']['learning']['loss'] != None and "learning" in pCatalog.keys() and pCatalog['learning'] != None:
                req_loss:str                                        = pRequest['train_data']['learning']['loss']

                check_loss:List[dict]                               = list ( filter ( lambda x: x['model_reference']['model_name'] == req__model_name_task[0] and x['model_reference']['model_task'] == req__model_name_task[1] and "loss" in x.keys() and x['loss'] ==  req_loss , pCatalog["learning"]  ) ) 

                if len( check_loss ) != 1:
                    err_msg:str                                     = "[!] La Loss scelta ({}) non è compatibile con quelle disponibili per la coppia Modello-Task selezionata ({})".format(req_loss , req__model_name_task)
                    return ( False , err_msg )
            

            if "learning" in pRequest['train_data'].keys() and pRequest['train_data']['learning'] != None and "learning_algorithm" in pRequest['train_data']['learning'].keys() and pRequest['train_data']['learning']['learning_algorithm'] != None and "learning" in pCatalog.keys() and pCatalog['learning'] != None:
                
                req_lr_algo:str                                     = pRequest['train_data']['learning']['learning_algorithm']

                check_lr_algo:List[dict]                            = list ( filter ( lambda x: x['model_reference']['model_name'] == req__model_name_task[0] and x['model_reference']['model_task'] == req__model_name_task[1] and "learning_algorithm" in x.keys() and x['learning_algorithm'] ==  req_lr_algo , pCatalog["learning"]  ) ) 

                if len( check_lr_algo ) != 1:
                    err_msg:str                                     = "[!] L'algoritmo di Learning Scelto ({}) non è compatibile con quelli disponibili per la coppia Modello-Task selezionata ({})".format(req_lr_algo,req__model_name_task)
                    return ( False , err_msg )

            # [8] Check Iperparametri Algoritmo di Learning
            if "learning" in pRequest['train_data'].keys() and pRequest['train_data']['learning'] != None and "learning_hyperparams" in pRequest["train_data"]["learning"].keys() and pRequest['train_data']['learning']['learning_hyperparams'] != None and "learning" in pCatalog.keys() and pCatalog['learning'] != None:
                req_learning_hyperparams:List[dict]                     = pRequest['train_data']['learning']['learning_hyperparams'] 

                catalog_filtered_learning_assets:List[dict]             = list ( filter ( lambda x: x['model_reference']['model_name'] == req__model_name_task[0] and x['model_reference']['model_task'] == req__model_name_task[1] and "learning_hyperparams" in x.keys() , pCatalog['learning'] ) )
                

                if len(catalog_filtered_learning_assets) > 0:

                    catalog_filtered_learning_hyperparams:List[dict]    = list ( map ( lambda x: x['learning_hyperparams'] , catalog_filtered_learning_assets ) )[0]
                else:
                    err_msg:str                                         = "[!] La coppia Modello-Task scelta {} non supporta Iperparametri di Learning".format(req__model_name_task)
                    return ( False , err_msg )  
                
                
                outcome:Union[ bool , Tuple[ bool, str ] , Exception ]  = TrainRequestValidator.checkHyperparams(req_learning_hyperparams , catalog_filtered_learning_hyperparams , req__model_name_task)
                
                if issubclass( type(outcome) , Exception) or type(outcome) == tuple:
                    return outcome

                
            return True

        except Exception as exp:
            return exp


    @staticmethod
    def checkHyperparams ( pReqHyperParams:List[dict] , pCatalogHyperParams:List[dict] , pModelTaskPair:tuple) -> Union[ bool , Tuple[ bool, str ] , Exception ]:
        """
        Questa funzione permette di controllare se una lista di Iperparametri è conforme rispetto al catalogo.

        Args:\n
            pReqHyperParams                 (List[dict])        : Iperparametri Richiesta
            pCatalogHyperParams             (List[dict])        : Iperparametri Catalogo abbinati alla richiestqa
            pModelTaskPair                  (tuple)             : Coppia Modello-Task scelti

        Returns:\n
            Union[ bool , Tuple[bool , str ] , Exception ]      : True se la richiesta è corretta; altrimenti (FALSE , MSG_ERRORE) oppure Eccezione se il formato della richiesta/catalogo è diverso rispetto a quello sopra elencato.

        Raises:\n
            Exception                                           : eccezione derivata dall'assenza di una chiave nel dizionario
        """

        for hyperparam in pReqHyperParams:

            try:
                
                # [1] Check sul Nome degli Iperparametri Scelti
                catalog_hyperparam:List[dict]           = list ( filter ( lambda x: x["param_name"] == hyperparam['hyper_param_name'] , pCatalogHyperParams ) )
                
                if  len( catalog_hyperparam ) != 1:
                    err_msg:str                         = "[!] L'iperparametro {} non è presente per la coppia Modello-Task Scelta ({})".format(hyperparam['hyper_param_name'] , pModelTaskPair)
                    return ( False , err_msg ) 
                else:
                    catalog_hyperparam:dict              = catalog_hyperparam[0]
                
                # [2] Check sul Tipo del Parametro
                catalog_param_type:str                   = catalog_hyperparam["param_type"]

                if catalog_param_type == "int" and type(hyperparam["hyper_param_value"]) != int :
                    err_msg:str                          = "[!] L'iperparametro '{} = {}' ha un tipo diverso da quello previsto ('int')".format( hyperparam['hyper_param_name'] , hyperparam['hyper_param_value'] )
                    return ( False , err_msg ) 

                if catalog_param_type == "float" and type(hyperparam["hyper_param_value"]) != float :
                    err_msg:str                          = "[!] L'iperparametro '{} = {}' ha un tipo diverso da quello previsto ('float')".format(hyperparam['hyper_param_name'] , hyperparam['hyper_param_value'] )
                    return ( False , err_msg ) 
                
                if catalog_param_type == "str" and type(hyperparam["hyper_param_value"]) != str :
                    err_msg:str                         = "[!] L'iperparametro '{} = {}' ha un tipo diverso da quello previsto ('str')".format( hyperparam['hyper_param_name'] , hyperparam['hyper_param_value'] )
                    return ( False , err_msg )

                if catalog_param_type == "bool" and type(hyperparam["hyper_param_value"]) != bool:
                    err_msg:str                         = "[!] L'iperparametro '{} = {}' ha un tipo diverso da quello previsto ('bool')".format( hyperparam['hyper_param_name'] , hyperparam['hyper_param_value'] )
                    return ( False , err_msg )


                #Controlli su tipi di dati composti
                if catalog_param_type == "List[float]" and (type(hyperparam["hyper_param_value"]) != list or len( list( filter ( lambda x: type(x)  != float , hyperparam["hyper_param_value"] ) ) ) > 0 ):
                    err_msg:str                         = "[!] L'iperparametro '{} = {}' ha un tipo diverso da quello previsto ('List[float]')".format( hyperparam['hyper_param_name'] , hyperparam['hyper_param_value'] )
                    return ( False , err_msg )

                if catalog_param_type == "List[str]" and (type(hyperparam["hyper_param_value"]) != list or len( list( filter ( lambda x: type(x)  != str , hyperparam["hyper_param_value"] ) ) ) > 0 ):
                    err_msg:str                         = "[!] L'iperparametro '{} = {}' ha un tipo diverso da quello previsto ('List[str]')".format( hyperparam['hyper_param_name'] , hyperparam['hyper_param_value'] )
                    return ( False , err_msg )

                if catalog_param_type == "List[bool]" and (type(hyperparam["hyper_param_value"]) != list or len( list( filter ( lambda x: type(x)  != bool , hyperparam["hyper_param_value"] ) ) ) > 0 ):
                    err_msg:str                         = "[!] L'iperparametro '{} = {}' ha un tipo diverso da quello previsto ('List[bool]')".format( hyperparam['hyper_param_name'] , hyperparam['hyper_param_value'] )
                    return ( False , err_msg )

                if catalog_param_type == "List[int]" and (type(hyperparam["hyper_param_value"]) != list or len( list( filter ( lambda x: type(x)  != int , hyperparam["hyper_param_value"] ) ) ) > 0 ):
                    err_msg:str                         = "[!] L'iperparametro '{} = {}' ha un tipo diverso da quello previsto ('List[int]')".format( hyperparam['hyper_param_name'] , hyperparam['hyper_param_value'] )
                    return ( False , err_msg )

    

                # [3] Check sul Contenuto dell'Iperparametro
                # [3.1] Str Value
                if catalog_param_type == "str"  and (hyperparam["hyper_param_value"] not in catalog_hyperparam["options"]):
                    err_msg:str                         = "[!] L'iperparametro '{} = {}' ha un valore non ammissibile (Valori Ammissibili: {})".format( hyperparam['hyper_param_name'] , hyperparam['hyper_param_value'], catalog_hyperparam["options"] )
                    return ( False , err_msg )

                
                # [3.2] Int Value
                if catalog_param_type == "int" and ( ( str(catalog_hyperparam["range_l"]) != "inf" and hyperparam["hyper_param_value"] <  int(catalog_hyperparam["range_l"]) ) or ( str(catalog_hyperparam["range_u"]) != "inf" and  hyperparam["hyper_param_value"] >  int(catalog_hyperparam["range_u"]) ) ):

                    err_msg:str                         = "[!] L'iperparametro '{} = {}' ha un valore non ammissibile (Valori Ammissibili: [{}-{}])".format(hyperparam['hyper_param_name'] , hyperparam['hyper_param_value']  ,catalog_hyperparam["range_l"] ,  catalog_hyperparam["range_u"] )
                    return ( False , err_msg )

                
                # [3.3] Float Value
                if catalog_param_type == "float" and ( ( str(catalog_hyperparam["range_l"]) != "inf" and hyperparam["hyper_param_value"] <  float(catalog_hyperparam["range_l"]) ) or ( str(catalog_hyperparam["range_u"]) != "inf" and  hyperparam["hyper_param_value"] >  float(catalog_hyperparam["range_u"]) ) ) :

                    err_msg:str                         = "[!] L'iperparametro '{} = {}' ha un valore non ammissibile (Valori Ammissibili: [{}-{}])".format(hyperparam['hyper_param_name'] , hyperparam['hyper_param_value'] , catalog_hyperparam["range_l"] ,  catalog_hyperparam["range_u"] )
                    return ( False , err_msg )


                
                #[4.0] Controlli su Tipi di Dato Composti
                if "range_l" in catalog_hyperparam.keys() and  "range_u" in catalog_hyperparam.keys() and str(catalog_hyperparam["range_l"]) != "inf" and str(catalog_hyperparam["range_u"]) != "inf":
                    
                    
                    # Caso List[float]
                    if catalog_param_type == "List[float]" and len( list( filter ( lambda x: x < float(catalog_hyperparam["range_l"]) or x > float(catalog_hyperparam["range_u"]) , hyperparam["hyper_param_value"] ) ) ) > 0:

                        err_msg:str                         = "[!] L'iperparametro '{} = {}' ha un valore non ammissibile (Valori Ammissibili: [{}-{}])".format(hyperparam['hyper_param_name'] , hyperparam['hyper_param_value'] , catalog_hyperparam["range_l"] ,  catalog_hyperparam["range_u"] )
                        return ( False , err_msg )
                    

                    # Caso List[int]
                    if catalog_param_type == "List[int]" and len( list( filter ( lambda x: x < int(catalog_hyperparam["range_l"]) or x > int(catalog_hyperparam["range_u"]) , hyperparam["hyper_param_value"] ) ) ) > 0:

                        err_msg:str                         = "[!] L'iperparametro '{} = {}' ha un valore non ammissibile (Valori Ammissibili: [{}-{}])".format(hyperparam['hyper_param_name'] , hyperparam['hyper_param_value'] , catalog_hyperparam["range_l"] ,  catalog_hyperparam["range_u"] )
                        return ( False , err_msg )


                elif "range_l" in catalog_hyperparam.keys() and str(catalog_hyperparam["range_l"]) != "inf":

                    # Caso List[float]
                    if catalog_param_type == "List[float]" and len( list( filter ( lambda x: x < float(catalog_hyperparam["range_l"])  , hyperparam["hyper_param_value"] ) ) ) > 0:

                        err_msg:str                         = "[!] L'iperparametro '{} = {}' ha un valore non ammissibile (Valori Ammissibili: [{}-{}])".format(hyperparam['hyper_param_name'] , hyperparam['hyper_param_value'] , catalog_hyperparam["range_l"] ,  catalog_hyperparam["range_u"] )
                        return ( False , err_msg )


                    # Caso List[int]
                    if catalog_param_type == "List[int]" and len( list( filter ( lambda x: x < int(catalog_hyperparam["range_l"]) , hyperparam["hyper_param_value"] ) ) ) > 0:

                        err_msg:str                         = "[!] L'iperparametro '{} = {}' ha un valore non ammissibile (Valori Ammissibili: [{}-{}])".format(hyperparam['hyper_param_name'] , hyperparam['hyper_param_value'] , catalog_hyperparam["range_l"] ,  catalog_hyperparam["range_u"] )
                        return ( False , err_msg )

                elif "range_u" in catalog_hyperparam.keys() and str(catalog_hyperparam["range_u"]) != "inf":

                    # Caso List[float]
                    if catalog_param_type == "List[float]" and len( list( filter ( lambda x: x > float(catalog_hyperparam["range_u"]) , hyperparam["hyper_param_value"] ) ) ) > 0:

                        err_msg:str                         = "[!] L'iperparametro '{} = {}' ha un valore non ammissibile (Valori Ammissibili: [{}-{}])".format(hyperparam['hyper_param_name'] , hyperparam['hyper_param_value'] , catalog_hyperparam["range_l"] ,  catalog_hyperparam["range_u"] )
                        return ( False , err_msg )


                    # Caso List[int]
                    if catalog_param_type == "List[int]" and len( list( filter ( lambda x: x > int(catalog_hyperparam["range_u"]) , hyperparam["hyper_param_value"] ) ) ) > 0:

                        err_msg:str                         = "[!] L'iperparametro '{} = {}' ha un valore non ammissibile (Valori Ammissibili: [{}-{}])".format(hyperparam['hyper_param_name'] , hyperparam['hyper_param_value'] , catalog_hyperparam["range_l"] ,  catalog_hyperparam["range_u"] )
                        return ( False , err_msg )
                

                
            except Exception as exp:
                return exp

        
        return True