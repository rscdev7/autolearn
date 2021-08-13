"""
@author           	    :  rscalia                              \n
@build-date             :  Thu 12/08/2021                       \n
@last-update            :  Thu 12/08/2021                       \n

Questo componente permette di guidare l'utente verso la compilazione corretta della richiesta di addestramento di un Modello di ML
"""


from ..async_input.utils                        import int_input , str_input , bool_input , selection_input, float_input
from typing                                     import Union,List
from ..exception_manager.ExceptionManager       import ExceptionManager


async def training_wizard (pCatalog:dict) -> Union [ dict , Exception ]:
    """
    # **training_wizard**

    Questa funzione permette di guidare l'utente attraverso una corretta compilazione del form che permette di addestrare un Modello di ML

    Args:\n
        pCatalog                    (dict)          : catalogo applicativo AutoLearn \n

                                                      Per il formato del dizionario, consulatare la documentazione dell'applicativo

    Returns:\n
        Union [ dict , Exception ]

    Raises:\n
        Exception                                   : eccezione durante l'input dei parametri da tastiera
    """

    to_iter:bool        = True

    try:
        
        while to_iter == True:

            print ("\n\n________________________________TRAINING WIZARD________________________________\n")

            # [0] Init strutture dati che collezionano i dati di training
            train_request:dict                      = {}
            dataset:dict                            = {}
            model:dict                              = {}
            learning:dict                           = {}
            
            
            # [1] Scelta Dataset e Task
            dataset_choices:List[str]               = list( map ( lambda x : ( x['dataset_name'] , x['dataset_task'] ) , pCatalog['data_lake']  )  )
            n_dataset_choice:int                    = len(dataset_choices)
            
            if n_dataset_choice == 0: raise ValueError("\n[!] ERRORE, Il catalogo dei Dataset è vuoto \n")
            

            dataset_choice_guide:str                = guide_selection_build(dataset_choices)

            print("\n[Q] Scegli una coppia Dataset-Task dalla seguente lista: \n")
            dataset_choice:Union[ int , Exception ] = await selection_input(dataset_choice_guide , n_dataset_choice)

            if type(dataset_choice) == ValueError:
                print("\n\n[!] ERRORE, l'opzione scelta non è disponibile, scegliere un dataset digitando un numero compreso fra 1 e {} \n".format(n_dataset_choice))
                continue

            if type(dataset_choice) == TypeError:
                print("\n\n[!] ERRORE, per scegliere il dataset bisogna inserire un numero intero da tastiera ! \n")
                continue
            
            dataset['dataset_name']                 = dataset_choices[dataset_choice-1][0]
            dataset['dataset_task']                 = dataset_choices[dataset_choice-1][1]
            

            
            # [1.1] Scelta Split
            split:Union[float , Exception]         = await float_input("\n\n[Q] Scegli uno Percentuale del dataset da destinare ai dati di Test \n")
            if ExceptionManager.lookForExceptions(split):
                print ("\n\n[!] ERRORE, lo split da inserire deve essere un numero in virgola mobile !\n")
                continue
            else:
                dataset['split_test']               = split


            # [1.2] Scelta Seed
            seed:Union[int , Exception]             = await int_input("\n\n[Q] Scegli un Seed per gli algoritmi random degli Esperimenti\n")
            if ExceptionManager.lookForExceptions(seed):
                print ("\n\n[!] ERRORE, il seed da inserire deve essere un numero intero! \n")
                continue
            else:
                dataset['split_seed']               = seed



            # [2] Scelta Modello ML
            model_choices:List[dict]                = list( filter ( lambda x : x['model_task'] == dataset['dataset_task'], pCatalog['models']  )  )
            n_models_choice:int                     = len(model_choices)
            if n_models_choice == 0: 
                raise ValueError("\n\n[!] ERRORE, impossibile trovare modelli nel catalogo che affrontano il task scelto ({}) \n".format(dataset['dataset_task']))
                continue


            models_name_choices:List[str]              = list( map ( lambda x : x['model_name'] , model_choices  )  )
            models_choice_guide:str                    = guide_selection_build(models_name_choices)

            print("\n\n[Q] Scegli il Modello di ML da addestrare: \n")
            model_choice:Union[ int , Exception ]       = await selection_input(models_choice_guide , n_models_choice)
            if type(model_choice) == ValueError:
                print("\n[!] ERRORE, l'opzione scelta non è disponibile, scegliere un Modello digitando un numero compreso fra 1 e {}\n".format(n_models_choice))
                continue

            if type(model_choice) == TypeError:
                print("\n[!] ERRORE, per scegliere il Modello bisogna inserire un numero intero da tastiera !\n")
                continue

            model['model_name']                         = models_name_choices[model_choice-1]
            model['model_task']                         = dataset['dataset_task']


            #[3] Scelta Iperparametri Modello
            model_hypeparams:List[dict]                         = list( filter ( lambda x: x['model_name'] == model['model_name'] and x['model_task'] == model['model_task'] and 'model_hyperparams' in x.keys()  , model_choices ) ) 

            if len(model_hypeparams) > 0: 
                print("\n\n___________MODEL HYPERPARAMS___________")
                model['model_hyperparams']                      = []

                outcome:Union[ None , str]                      = await hyper_params_input(model_hypeparams[0]['model_hyperparams'] , model ,'model_hyperparams')
                if type(outcome) == str:
                    continue
                
                if model['model_hyperparams'] == []:
                    del model['model_hyperparams']


            #[4] Scelta Iperparametri d Learning
            learning_hypeparams:List[dict]                              = list( filter ( lambda x: x['model_reference']['model_name'] == model['model_name'] and x['model_reference']['model_task'] == model['model_task'] and 'learning_hyperparams' in x.keys(), pCatalog['learning']  ) ) 

            if len(learning_hypeparams) > 0: 
                print("\n\n___________LEARNING HYPERPARAMS___________")

                learning['learning_hyperparams']                      = []
                outcome:Union[ None , str]                            = await hyper_params_input(learning_hypeparams[0]['learning_hyperparams'] , learning ,'learning_hyperparams')
                if type(outcome) == str:
                    continue
                

                # [5] Scelta Loss e LR Algorithm
                if learning['learning_hyperparams'] != []:
                    loss:str                                              = await str_input("\n\n[Q] Inserisci la Loss Function da utilizzare \n\t-> Inserisci -1 per ometterla\n")
                    if loss != "-1":
                        learning['loss']                                  = loss

                    lr_algo:str                                           = await str_input("\n\n[Q] Inserisci l'algoritmo di Learning' da utilizzare \n\t-> Inserisci -1 per ometterlo \n")
                    if lr_algo != "-1":
                        learning['learning_algorithm']                    = lr_algo


            #Compilazione Dizionario Richiesta
            if learning != {} and learning['learning_hyperparams'] != []:
                train_request["train_data"]                           = { "dataset":dataset , "model":model , "learning" : learning  }
            else:
                train_request["train_data"]                           = { "dataset":dataset , "model":model }

            break
        

        #Restituisco dizionario richiesta al chiamante
        return train_request

    except Exception as exp:
        return exp


async def hyper_params_input(pHyperParamsList:List[dict] , pFillDict:dict , pFillToken:str) -> Union [ None , str ]:
    """
    # **hyper_params_input**

    Questo metodo permette di raccogliere i valori degli Iperparametri dei Modelli/Algoritmi di ML attraverso l'input da tastiera.

    Args:\n
        pHyperParamsList            (List[dict])        : lista di iperparametri da prelevare
        pFillDict                   (dict)              : dizionario da riempire
        pFillToken                  (str)               : chiave che permette di riempire il dizionario

    Returns:\n
        Union [ None , str ]
    """
    pFillDict[pFillToken]       = []

    for hyperparam in pHyperParamsList:

        hyperparam_record:dict  = { "hyper_param_name": hyperparam['param_name'] , "hyper_param_value": -99999999 }

        print("\n\n[I] Iperparametro: {} - Tipo: {}".format(hyperparam['param_name'] , hyperparam['param_type'] ))


        #Scelta se Inserire o meno l'Iperparametro
        print("\n[Q] Scegli se inserire l'iperparametro o se lasciare il valore di default\n")
        hy_choices:List[str]                         = [ "Inserisci Iperparametro" , "Lascia il Valore di Default" ]
        n_choice:int                                 = 2
        hyper_param_choice_guide:str                 = guide_selection_build(hy_choices)

        hyperparam_choice:Union[ bool , Exception ]  = await bool_input(hyper_param_choice_guide)
        if ExceptionManager.lookForExceptions(hyperparam_choice):
            print ("\n\n[!] ERRORE, per inserire l'iperparametro {} bisogna digitare un numero compreso fra 1 e 2\n".format(hyperparam['param_name']))
            return "error"

        if hyperparam_choice == False:
            continue    


        # Caso IperParametro di Interi
        if hyperparam['param_type'] == "int":
            hyper_param_choice:Union[ int, Exception]  = await int_input("\n\n[Q] Inserisci il valore per l'iperparametro {}\n".format(hyperparam['param_name']))

            if ExceptionManager.lookForExceptions(hyper_param_choice):
                print ("\n\n[!] ERRORE, il valore dell'Iperparametro {} deve essere un numero intero\n".format(hyperparam['param_name']))
                return "error"

            hyperparam_record['hyper_param_value']      = hyper_param_choice


        # Caso IperParametro di Float
        if hyperparam['param_type'] == "float":
            hyper_param_choice:Union[ float, Exception]  = await float_input("\n\n[Q] Inserisci il valore per l'iperparametro {}\n".format(hyperparam['param_name']))
            
            if ExceptionManager.lookForExceptions(hyper_param_choice):
                print ("\n\n[!] ERRORE, il valore dell'Iperparametro {} deve essere un numero in virgola mobile\n".format(hyperparam['param_name']))
                return "error"

            hyperparam_record['hyper_param_value']      = str( hyper_param_choice )


        # Caso IperParametro di Stringa
        if hyperparam['param_type'] == "str":
            hy_choices:List[str]                         = hyperparam['options']
            n_choice:int                                 = len(hy_choices)
            hyper_param_choice_guide:str                 = guide_selection_build(hy_choices)

            print("\n\n[Q] Scegli il valore per l'iperparametro {} \n".format(hyperparam['param_name']))

            hyperparam_choice:Union[ int , Exception ]  = await selection_input( hyper_param_choice_guide , n_choice)
            if type(hyperparam_choice) == ValueError:
                print("\n\n[!] ERRORE, l'opzione scelta non è disponibile, scegliere un iperparametro digitando un numero compreso fra 1 e {} \n".format(n_choice))
                return "error"

            if type(hyperparam_choice) == TypeError:
                print("\n\n[!] ERRORE, per scegliere l'Iperparametro {} bisogna inserire un numero intero da tastiera ! \n".format(hyperparam['param_name']))
                return "error"

            
            hyperparam_record['hyper_param_value']      = hy_choices[hyperparam_choice-1]


        # Caso IperParametro di Booleano
        if hyperparam['param_type'] == "bool":
            hy_choices:List[str]                         = [ "SI" , "NO" ]
            n_choice:int                                 = 2
            hyper_param_choice_guide:str                 = guide_selection_build(hy_choices)

            print("\n\n[Q] Scegli il valore per l'iperparametro {} \n".format(hyperparam['param_name']))
            hyperparam_choice:Union[ bool , Exception ]  = await bool_input(hyper_param_choice_guide)

            if ExceptionManager.lookForExceptions(hyperparam_choice):
                print ("\n\n[!] ERRORE, il valore dell'Iperparametro {} deve essere un numero intero che codifica il valore booleano da inserire\n".format(hyperparam['param_name']))
                return "error"
            
            hyperparam_record['hyper_param_value']      = hyperparam_choice


        # Caso IperParametro di tipo List[str]
        if hyperparam['param_type'] == "List[str]":
            hyperparam_record['hyper_param_value']       = []

            while True:
                list_choice:str                          = await str_input("\n\n[Q] Inserisci un valore della lista appartenente all'Iperparametro {} \n\t-> inserisci -1 per stoppare l'inserimento \n".format(hyperparam['param_name']))


                if list_choice == "-1":
                    break
                else:
                    hyperparam_record['hyper_param_value'].append(list_choice)  
                    print("\n[I] Valore Inserito: {}\n".format(list_choice))


        # Caso IperParametro di tipo List[int]
        if hyperparam['param_type'] == "List[int]":
            hyperparam_record['hyper_param_value']       = []

            while True:
                list_choice:int                          = await int_input("\n\n[Q] Inserisci un valore della lista appartenente all'Iperparametro {} \n\t-> inserisci -1 per stoppare l'inserimento \n".format(hyperparam['param_name']))

                if ExceptionManager.lookForExceptions(list_choice):
                    print ("\n\n[!] ERRORE, il valore scelto per l'iperparametro {} deve essere un numero intero \n".format(hyperparam_record['hyper_param_name']))
                    return "error"

                if list_choice == -1:
                    break
                else:
                    hyperparam_record['hyper_param_value'].append(list_choice)
                    print("\n[I] Valore Inserito: {}\n".format(list_choice)) 


        # Caso IperParametro di tipo List[float]
        if hyperparam['param_type'] == "List[float]":
            hyperparam_record['hyper_param_value']       = []

            while True:
                list_choice:float                        = await float_input("\n\n[Q] Inserisci un valore della lista appartenente all'Iperparametro {} \n\t-> inserisci -1 per stoppare l'inserimento \n".format(hyperparam['param_name']))

                if ExceptionManager.lookForExceptions(list_choice):
                    print ("\n\n[!] ERRORE, il valore scelto per l'iperparametro {} deve essere un numero in virgola Mobile \n".format(hyperparam_record['hyper_param_name']))
                    return "error"

                if float(list_choice) == -1:
                    break
                else:
                    hyperparam_record['hyper_param_value'].append(list_choice)   
                    print("\n[I] Valore Inserito: {}\n".format(list_choice))

        if type(hyperparam_record['hyper_param_value']) == int  and type(hyperparam_record['hyper_param_value']) == -99999999: 
            continue

        pFillDict[pFillToken].append(hyperparam_record)


def guide_selection_build (pChoices:List[str]) -> str:
    """
    # **guide_selection_build**

    Questa funzione permette di costruire una stringa che mostra una lista di opzioni che l'utente può scegliere

    Args:\n
        pChoices                (List[str])     : lista di opzioni

    Returns:\n
        str
    """
    guide:str       = ""

    for idx,choice in enumerate(pChoices):
        guide += "\t{}) {}\n".format( idx+1 , choice)

    return guide