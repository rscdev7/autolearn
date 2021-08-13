"""
@author           	    :  rscalia                              \n
@build-date             :  Fro 13/08/2021                       \n
@last-update            :  Fri 13/08/2021                       \n

Questo componente serve per testare le routine di input dell'applicativo autolearn
"""

from .lib.train_request_wizard.training_wizard   import training_wizard
from .lib.async_input.utils                      import int_input, str_input , float_input , bool_input , selection_input
from .lib.client_config.ClientConfigurator       import ClientConfigurator
from .lib.concrete_network_communicator.AsyncHTTPCommunicator   import AsyncHTTPCommunicator
from .lib.local_ml_engine.LocalMLEngine          import LocalMLEngine
import asyncio
from typing                                     import List,Union
import pytest
from pprint                                     import pprint

@pytest.mark.asyncio
async def test_training_wizard():

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


    train_req:Union [ dict , Exception ]                    = await training_wizard(outcome)
    print("\n")
    pprint(train_req,indent=3 , width=2 ,depth=2)


    outcome:Union[Union[str, Exception, dict]]              = await ml_engine.trainMLModel(train_req)
    assert issubclass( type(outcome) , Exception  ) == False
    assert type(outcome) == str

    print("\n")    
    if "[!]" in outcome:
        print (outcome.split("bad_request__")[1])
    else:
        print(outcome)



    #[2] Stop LocalMLEngine
    outcome:Union[ dict , Exception]                        = await ml_engine.stop()
    assert issubclass( type(outcome) , Exception  ) == False

