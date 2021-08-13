"""
@author           	    :  rscalia                              \n
@build-date             :  Thu 12/08/2021                       \n
@last-update            :  Thu 12/08/2021                       \n

Questo componente serve per testare la classe LocalMLEngine
"""

from .lib.client_config.ClientConfigurator                      import ClientConfigurator
from .lib.local_ml_engine.LocalMLEngine                         import LocalMLEngine
from .lib.concrete_network_communicator.AsyncHTTPCommunicator   import AsyncHTTPCommunicator
from typing                                                     import Union
import pytest
from .lib.network_serializer.NetworkSerializer                  import NetworkSerializer
import asyncio


# Costruzione Record di Training
record:dict                                                 = {}
dataset:dict                                                = {}
dataset['dataset_name']                                     = "Height-Weight Dataset"
dataset['dataset_task']                                     = "Classification"
dataset['split_test']                                       = 0.03
dataset['split_seed']                                       = 5024

model:dict                                                  = {}
model['model_name']                                         = "LogisticRegressor"
model['model_task']                                         = "Classification"
model['model_hyperparams']                                  = [ { "hyper_param_name":"random_state" , "hyper_param_value":30 } ]

record["train_data"]                                        = { "dataset":dataset , "model":model }


WAIT_TIME:int                                               = 5


@pytest.mark.asyncio
async def test_remote_proxy():


    # [0] SetUp Sistema
    cfg:ClientConfigurator                                  = ClientConfigurator()
    outcome:Union[ None , Exception]                        = cfg.inspect()
    assert issubclass( type(outcome) , Exception  ) == False

    #[0.1] Start LocalMLEngine
    ml_engine:LocalMLEngine                                 = LocalMLEngine( cfg  )
    outcome:Union[ dict , Exception]                        = await ml_engine.start()
    assert issubclass( type(outcome) , Exception  ) == False


    # [1] Get Catalog
    outcome:Union[ dict , Exception]                        = await ml_engine.getCatalog()
    assert issubclass( type(outcome) , Exception  ) == False
    assert set( ['data_lake','models','metrics','learning'] ).difference( set( outcome.keys() ) ) == set( [] )

    print("\n\n[!] Outcome Get Catalog: {}".format(outcome.keys()))


    # [2] Train ML Model
    outcome:Union[ str , Exception , dict ]                 = await ml_engine.trainMLModel(record)
    assert issubclass( type(outcome) , Exception  ) == False
    assert type(outcome) == str
    print("[!] Outcome Training ML Model: {}".format(outcome))


    await asyncio.sleep(WAIT_TIME)


    # [3] View Sessions
    outcome:Union[ dict , Exception]                        = await ml_engine.viewSessionData()
    assert issubclass( type(outcome) , Exception  ) == False
    assert "experiments" in outcome.keys()
    assert type(outcome['experiments']) == list
    assert len( outcome['experiments'] ) >= 1 

    print ("[!] Outcome View Sessions: {}".format( outcome['experiments'][0].keys()) )


    # [4] Eval Model
    exp_id:int                                              = outcome['experiments'][-1]['timestamp']
    print ("[!] Target Model ID: {}".format(exp_id))
    assert type(exp_id) == int

    outcome:Union[ str , Exception , dict ]                 = await ml_engine.evaluateMLModel(exp_id)
    assert issubclass( type(outcome) , Exception  ) == False
    assert type(outcome) == str

    print("[!] Outcome Evaluate Model: {}".format(outcome))


    await asyncio.sleep(WAIT_TIME)

    
    # [5.1] Save Session
    outcome:Union[ str , Exception , dict ]                 = await ml_engine.saveSession(exp_id)
    assert issubclass( type(outcome) , Exception  ) == False
    assert type(outcome) == str 

    print ("[!] Outcome Salvataggio Sessione: {}".format(outcome))


    await asyncio.sleep(WAIT_TIME)


    # [5.2] Check deletion of old record on Session DB
    outcome:Union[ dict , Exception ]                       = await ml_engine.viewSessionData()
    assert issubclass( type(outcome) , Exception  ) == False
    assert "experiments" in outcome.keys()
    assert type(outcome['experiments']) == list
    assert len( outcome['experiments'] ) >= 1 

    search_old_sess:list                                    = list( filter ( lambda x: x['timestamp'] == exp_id , outcome['experiments']  ) )
    assert len(search_old_sess) == 0


    await asyncio.sleep(WAIT_TIME)


    # [3] View Experiments
    outcome:Union[ dict , Exception ]                       = await ml_engine.viewExperiments()
    assert issubclass( type(outcome) , Exception  ) == False
    assert "experiments" in outcome.keys()
    assert type(outcome['experiments']) == list
    assert len( outcome['experiments'] ) >= 1 

    target_exp:list                                         = list ( filter ( lambda x : x['timestamp'] ==  exp_id and 'eval_data' in x.keys() and x['eval_data'] != None , outcome['experiments'] )   )
    assert len(target_exp) == 1

    print ("[!] Outcome View Experiments: \n\t-> Chiavi Record: {} \n\t-> Timestamp: {} \n\t-> Eval: {} ".format(target_exp[0].keys() , target_exp[0]['timestamp'] , target_exp[0]['eval_data']) )


    # Stop MLEngine
    outcome:Union[ dict , Exception]                        = await ml_engine.stop()
    assert issubclass( type(outcome) , Exception  ) == False
    


