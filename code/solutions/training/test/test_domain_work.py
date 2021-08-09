"""
@author           	    :  rscalia                              \n
@build-date             :  Thu 03/07/2021                       \n
@last-update            :  Thu 03/07/2021                       \n

Questo componente serve per testare il Domain Work del Microservizio di Training
"""

from ..lib.data_validator.TrainRequestValidator     import TrainRequestValidator
from ..lib.network_serializer.NetworkSerializer     import NetworkSerializer
from pprint                                         import pprint
from typing                                         import Union , Tuple , Dict
from ..lib.http_engine.HTTPEngine                   import HTTPEngine


#Costanti
CATALOG_URL:str                                                     = "http://localhost:9200/catalog/api/get_catalog?pIdClient=client"


#[0] Istanziazione Serializzatore
serializer:NetworkSerializer                                        = NetworkSerializer()

# [1] Loading Catalog from disk
fd                                                                  = open("autolearn_catalog.json" , "rb")
output:bytes                                                        = fd.read()
catalog:dict                                                        = serializer.decodeJson(output)

# [2] Retrieving Catalog from Network
engine:HTTPEngine                                                   = HTTPEngine(60)
res:Union[ Dict[int,dict] , Exception, Tuple [Exception , int] ]    = engine.get(CATALOG_URL)


if issubclass (type(res),Exception) == False and type(res) == dict:
    print ("\n\n<<<< NETWORK CATALOG >>>>>>>> \n")
    catalog                                                         = res['payload']
else:
    print ("\n\n<<<< LOCAL CATALOG >>>>>>>> \n")


def test_data_validator_1():

    # Test Positivo - SVM
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "SVM"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"kernel" , "hyper_param_value":"linear" } ]

    record["train_data"]                                        = { "dataset":dataset , "model":model }


    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert outcome == True


def test_data_validator_9():

    # Test Positivo - RandomForest
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "RandomForest"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"max_depth" , "hyper_param_value": 2 } ]

    record["train_data"]                                        = { "dataset":dataset , "model":model }


    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert outcome == True


def test_data_validator_15():
    # Test Positivo - DecisionTree
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "DecisionTree"
    model['model_task']                                         = "Classification"
    model['model_hyperparam']                                                  = [ { "hyper_param_name":"n_estimator" , "hyper_param_value": 50 } ]

    record["train_data"]                                        = { "dataset":dataset , "model":model   }
    

    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert outcome == True


def test_data_validator_16():
    # Test Positivo - LogisticRegressor
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "LogisticRegressor"
    model['model_task']                                         = "Classification"

    record["train_data"]                                        = { "dataset":dataset , "model":model   }
    

    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert outcome == True


def test_data_validator_3():

    # Test Positivo con Learning 
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "SVM"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"kernel" , "hyper_param_value":"linear" } ]

    learning:dict                                               = {}
    learning['learning_hyperparams']                            = [ {"hyper_param_name":"regularization" , "hyper_param_value" : 1.5 }  ]
    record["train_data"]                                        = { "dataset":dataset , "model":model , "learning":learning  }
    

    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert outcome == True


def test_data_validator_2():

    # Test Negativo - errore nel Dataset Name
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "MINIST"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "SVM"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"kernel" , "hyper_param_value":"linear" } ]

    record["train_data"]                                        = { "dataset":dataset , "model":model }


    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert type(outcome) == tuple
    print (outcome[1])


def test_data_validator_7():
    # Test Negativo - Errore nel dataset task
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Regression"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "LogisticRegressor"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"random_state" , "hyper_param_value":1 } ]

    learning:dict                                               = {}
    learning['learning_hyperparams']                            = [ { "hyper_param_name":"max_iter" , "hyper_param_value": 2 } ]
    record["train_data"]                                        = { "dataset":dataset , "model":model , "learning":learning  }
    

    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert type(outcome) == tuple
    print(outcome[1])


def test_data_validator_8():
    # Test Negativo - Errore nello Split Seed
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 50.0
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "LogisticRegressor"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"random_state" , "hyper_param_value":1 } ]

    learning:dict                                               = {}
    learning['learning_hyperparams']                            = [ { "hyper_param_name":"max_iter" , "hyper_param_value": 2 } ]
    record["train_data"]                                        = { "dataset":dataset , "model":model , "learning":learning  }
    

    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert type(outcome) == tuple
    print(outcome[1])


def test_data_validator_10():
    # Test Negativo - Errore nel Model Name
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "DCGAN"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"random_state" , "hyper_param_value":1 } ]

    learning:dict                                               = {}
    learning['learning_hyperparams']                            = [ { "hyper_param_name":"max_iter" , "hyper_param_value": 2 } ]
    record["train_data"]                                        = { "dataset":dataset , "model":model , "learning":learning  }
    

    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert type(outcome) == tuple
    print(outcome[1])


def test_data_validator_11():
    # Test Negativo - Errore nel Model Task
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "Naive-Bayes"
    model['model_task']                                         = "Regression"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"priors" , "hyper_param_value":[0.5,0.8]} ]

    record["train_data"]                                        = { "dataset":dataset , "model":model   }
    

    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert type(outcome) == tuple
    print(outcome[1])


def test_data_validator_18():
    # Test Negativo - Errore nel Model Task
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "Naive-Bayes"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"priors" , "hyper_param_value":["ciao"]} ]

    record["train_data"]                                        = { "dataset":dataset , "model":model   }
    
    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert type(outcome) == tuple
    print(outcome[1])


def test_data_validator_19():
    # Test Negativo - Errore nel Model Task
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "Naive-Bayes"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"priors" , "hyper_param_value":[50.8,80.0]} ]

    record["train_data"]                                        = { "dataset":dataset , "model":model   }
    
    #Alterazione catalogo
    models:dict                                                 = catalog['models']
    naive_bayes:dict                                            = [ record for record in models if record['model_name'] == "Naive-Bayes" ][0]
    hyperparams:dict                                            = naive_bayes['model_hyperparams'][0]
    hyperparams['range_l']                                      = 0.0
    hyperparams['range_u']                                      = 1.0


    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert type(outcome) == tuple
    print(outcome[1])



def test_data_validator_20():
    # Test Negativo - Errore nel Model Task
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "Naive-Bayes"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"priors" , "hyper_param_value":[2.0,4]} ]

    record["train_data"]                                        = { "dataset":dataset , "model":model   }
    


    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert type(outcome) == tuple
    print(outcome[1])


def test_data_validator_21():
    # Test Negativo - Errore nel Model Task
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "Naive-Bayes"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"priors" , "hyper_param_value":[0.5 , 1.0, 0.2,  80.0 ]} ]

    record["train_data"]                                        = { "dataset":dataset , "model":model   }
    
    #Alterazione catalogo
    models:dict                                                 = catalog['models']
    naive_bayes:dict                                            = [ record for record in models if record['model_name'] == "Naive-Bayes" ][0]
    hyperparams:dict                                            = naive_bayes['model_hyperparams'][0]
    hyperparams['range_l']                                      = 0.0
    hyperparams['range_u']                                      = 1.0


    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert type(outcome) == tuple
    print(outcome[1])


def test_data_validator_4():
    # Test Negativo - Errore nei Model Hyperparams
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "LogisticRegressor"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"random_state" , "hyper_param_value":"None" } ]

    learning:dict                                               = {}
    learning['learning_hyperparams']                            = [ { "hyper_param_name":"max_iter" , "hyper_param_value": 2 } ]
    record["train_data"]                                        = { "dataset":dataset , "model":model , "learning":learning  }
    

    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert type(outcome) == tuple
    print(outcome[1])



def test_data_validator_5():
    # Test Negativo - Errore nei parametri di Learning (Loss)
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "LogisticRegressor"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"random_state" , "hyper_param_value":1 } ]

    learning:dict                                               = {}
    learning['learning_hyperparams']                            = [ { "hyper_param_name":"max_iter" , "hyper_param_value": 2 } ]
    learning['loss']                                            = "Hinge-Loss"
    record["train_data"]                                        = { "dataset":dataset , "model":model , "learning":learning  }
    

    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert type(outcome) == tuple
    print(outcome[1])


def test_data_validator_17():
    # Test Negativo - Errore nei parametri di Learning 
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "SVM"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"kernel" , "hyper_param_value": "test"} ]

    record["train_data"]                                        = { "dataset":dataset , "model":model }
    

    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert type(outcome) == tuple
    print(outcome[1])


def test_data_validator_6():
    # Test Negativo - Errore nei parametri di learnig (Learning Algorihtm)
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "LogisticRegressor"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"random_state" , "hyper_param_value":1 } ]

    learning:dict                                               = {}
    learning['learning_hyperparams']                            = [ { "hyper_param_name":"max_iter" , "hyper_param_value": 2 }   ]
    learning['learning_algorithm']                              = "SGD"
    record["train_data"]                                        = { "dataset":dataset , "model":model , "learning":learning  }
    

    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert type(outcome) == tuple
    print(outcome[1])


def test_data_validator_12():
    # Test Negativo - Errore nei Learning HyperParams
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "LogisticRegressor"
    model['model_task']                                         = "Classification"
    model['model_hyperparams']                                  = [ { "hyper_param_name":"random_state" , "hyper_param_value":1 } ]

    learning:dict                                               = {}
    learning['learning_hyperparams']                            = [ { "hyper_param_name":"max_iter" , "hyper_param_value": -50 } ]
    record["train_data"]                                        = { "dataset":dataset , "model":model , "learning":learning  }
    

    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert type(outcome) == tuple
    print(outcome[1])


def test_data_validator_13():
    # Test Negativo - Errore nei Learning HyperParams e assenza Model HyperParams
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "SVM"
    model['model_task']                                         = "Classification"

    learning:dict                                               = {}
    learning['learning_hyperparams']                            = [ { "hyper_param_name":"max_iter" , "hyper_param_value": -50 } ]
    record["train_data"]                                        = { "dataset":dataset , "model":model , "learning":learning  }
    

    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert type(outcome) == tuple
    print(outcome[1])


def test_data_validator_14():
    # Test Negativo - Errore nei Learning Hyperparams
    record:dict                                                 = {}
    dataset:dict                                                = {}
    dataset['dataset_name']                                     = "Iris-Fisher"
    dataset['dataset_task']                                     = "Classification"
    dataset['split_test']                                       = 0.03
    dataset['split_seed']                                       = 1234

    model:dict                                                  = {}
    model['model_name']                                         = "RandomForest"
    model['model_task']                                         = "Classification"

    learning:dict                                               = {}
    learning['learning_hyperparams']                            = [ { "hyper_param_name":"n_estimator" , "hyper_param_value": 50 } ]
    record["train_data"]                                        = { "dataset":dataset , "model":model , "learning":learning  }
    

    outcome:Union[ bool , Tuple[ bool , str ] , Exception ]     = TrainRequestValidator.checkRequest(record, catalog)
    assert type(outcome) == tuple
    print(outcome[1])











