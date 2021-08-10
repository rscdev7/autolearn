"""
@author           	:  rscalia                              \n
@build-date             :  Mon 10/08/2021                       \n
@last-update            :  Mon 10/08/2021                       \n

Questo componente serve per testare la classe HTTPCommunicator
"""

from .lib.concrete_network_communicator.AsyncHTTPCommunicator      import AsyncHTTPCommunicator
import pytest
import asyncio
from typing                                                        import List, Union
from pprint                                                        import pprint
from .lib.network_serializer.NetworkSerializer                     import NetworkSerializer
 

#Parametri Test
CONNECTION_PARAMS:dict              = { "timeout" : 10 }

catalog     = {     
                    "recipient_name"  : "catalog" ,
                    "base_address"    : "http://localhost:9200/catalog/api"  ,
                    "actions"         : [ ( "get_catalog" , "/get_catalog?pIdClient='client'" , "GET" , False  ) ] 
              }


training    = {
                    "recipient_name"  : "training" ,
                    "base_address"    : "http://localhost:9091/training/api"  ,
                    "actions"         : [ ( "training_req" , "/training_req" , "POST" , True  ) ]   
              }


evaluation = {
                    "recipient_name"  : "evaluation" ,
                    "base_address"    : "http://localhost:9094/evaluation/api"  ,
                    "actions"         : [ ( "eval_model" , "/eval_model" , "POST" , True  ) ]   
             }


session    = {
                    "recipient_name"  : "session" ,
                    "base_address"    : "http://localhost:9097/session/api"  ,
                    "actions"         : [ ( "view_sessions"     ,        "/view_sessions"       , "GET"       , False  ) ,
                                          ( "save_session"      ,       "/save_session"         , "POST"      , True  ) 
                                        ]   
             }


storage   = {
                    "recipient_name"  : "storage" ,
                    "base_address"    : "http://localhost:9099/storage/api"  ,
                    "actions"         : [ ( "view_experiments"     ,  "/view_experiments"     , "GET"       , False  ) ]   
             }

RECIPIENTS:List[dict]       = [ catalog , training , evaluation , session , storage ]
EVAL_MODEL_ID:int           = 1628620127000
ARCHIVE_RECORD:int          = 1628620127000


@pytest.mark.asyncio
async def test_get_catalog():

      communicator:AsyncHTTPCommunicator      = AsyncHTTPCommunicator()

      outcome:Union[ None , Exception]        = await communicator.setUp(RECIPIENTS, CONNECTION_PARAMS)
      assert issubclass ( type(outcome) , Exception ) == False 

      outcome:Union[ None , Exception]        = communicator.start()
      assert issubclass ( type(outcome) , Exception ) == False 


      catalog:Union[object , Exception ]      = await communicator.request( "catalog" , "get_catalog" )
      if issubclass ( type(catalog) , Exception ) == False:
            print( str(catalog) )
      else:
            pprint(catalog)


      outcome:Union[ None , Exception]        = await communicator.stop()
      assert issubclass ( type(outcome) , Exception ) == False 

      outcome:bool                            = communicator.isConnected()
      assert outcome == False


@pytest.mark.asyncio
async def test_training():

      communicator:AsyncHTTPCommunicator      = AsyncHTTPCommunicator()

      outcome:Union[ None , Exception]        = await communicator.setUp(RECIPIENTS, CONNECTION_PARAMS)
      assert issubclass ( type(outcome) , Exception ) == False 

      outcome:Union[ None , Exception]        = communicator.start()
      assert issubclass ( type(outcome) , Exception ) == False 


      # Costruzione Record di Training
      record:dict                                                 = {}
      dataset:dict                                                = {}
      dataset['dataset_name']                                     = "Iris-Fisher"
      dataset['dataset_task']                                     = "Classification"
      dataset['split_test']                                       = 0.03
      dataset['split_seed']                                       = 1234

      model:dict                                                  = {}
      model['model_name']                                         = "RandomForest"
      model['model_task']                                         = "Classification"
      model['model_hyperparams']                                  = [ { "hyper_param_name":"n_estimator" , "hyper_param_value":20 } ]

      record["train_data"]                                        = { "dataset":dataset , "model":model }


      outcome:Union[object , Exception ]                          = await communicator.request( "training" , "training_req" , record )
      if issubclass ( type(outcome) , Exception ) == False:
            print( str(outcome) )
      else:
            pprint(outcome)


      outcome:Union[ None , Exception]                            = await communicator.stop()
      assert issubclass ( type(outcome) , Exception ) == False 

      outcome:bool                                                = communicator.isConnected()
      assert outcome == False


@pytest.mark.asyncio
async def test_eval():

      communicator:AsyncHTTPCommunicator                          = AsyncHTTPCommunicator()

      outcome:Union[ None , Exception]                            = await communicator.setUp(RECIPIENTS, CONNECTION_PARAMS)
      assert issubclass ( type(outcome) , Exception ) == False 

      outcome:Union[ None , Exception]                            = communicator.start()
      assert issubclass ( type(outcome) , Exception ) == False 


      # Costruzione Record di Training
      serializer:NetworkSerializer                                = NetworkSerializer()
      outcome:Union[ None , Exception ]                           = serializer.readKeyFromFile()
      assert issubclass ( type(outcome) , Exception ) == False 

      crypt_id_sess:Union[ str, Exception ]                       = serializer.encryptField( str(EVAL_MODEL_ID) )
      assert issubclass( type( crypt_id_sess ) , Exception ) == False     

      request:dict                                                = {}
      request['payload']                                          = crypt_id_sess


      outcome:Union[object , Exception ]                          = await communicator.request( "evaluation" , "eval_model" , request )
      if issubclass ( type(outcome) , Exception ) == False:
            print( str(outcome) )
      else:
            pprint(outcome)


      outcome:Union[ None , Exception]                            = await communicator.stop()
      assert issubclass ( type(outcome) , Exception ) == False 

      outcome:bool                                                = communicator.isConnected()
      assert outcome == False


@pytest.mark.asyncio
async def test_view_sessions():

      communicator:AsyncHTTPCommunicator      = AsyncHTTPCommunicator()

      outcome:Union[ None , Exception]        = await communicator.setUp(RECIPIENTS, CONNECTION_PARAMS)
      assert issubclass ( type(outcome) , Exception ) == False 

      outcome:Union[ None , Exception]        = communicator.start()
      assert issubclass ( type(outcome) , Exception ) == False 

      

      outcome:Union[object , Exception ]      = await communicator.request( "session" , "view_sessions"  )
      if issubclass ( type(outcome) , Exception ) == False:
            print( str(outcome) )
      else:
            pprint(outcome)

      outcome:Union[ None , Exception]        = await communicator.stop()
      assert issubclass ( type(outcome) , Exception ) == False 

      outcome:bool                            = communicator.isConnected()
      assert outcome == False


@pytest.mark.asyncio
async def test_save_session():

      communicator:AsyncHTTPCommunicator        = AsyncHTTPCommunicator()

      outcome:Union[ None , Exception]          = await communicator.setUp(RECIPIENTS, CONNECTION_PARAMS)
      assert issubclass ( type(outcome) , Exception ) == False 

      outcome:Union[ None , Exception]          = communicator.start()
      assert issubclass ( type(outcome) , Exception ) == False 


      serializer:NetworkSerializer                = NetworkSerializer()
      outcome:Union[None , Exception]             = serializer.readKeyFromFile()
      assert issubclass( type(outcome) , Exception ) == False

      crypt_id:str                                = serializer.encryptField( str(ARCHIVE_RECORD) )
      assert issubclass( type(crypt_id) , Exception ) == False

      req:dict                                    = { "id_sess_cf":crypt_id }


      outcome:Union[object , Exception ]      = await communicator.request( "session" , "save_session" , req  )
      if issubclass ( type(outcome) , Exception ) == False:
            print( str(outcome) )
      else:
            pprint(outcome)


      outcome:Union[ None , Exception]        = await communicator.stop()
      assert issubclass ( type(outcome) , Exception ) == False 

      outcome:bool                            = communicator.isConnected()
      assert outcome == False


@pytest.mark.asyncio
async def test_view_exp():

      communicator:AsyncHTTPCommunicator      = AsyncHTTPCommunicator()

      outcome:Union[ None , Exception]        = await communicator.setUp(RECIPIENTS, CONNECTION_PARAMS)
      assert issubclass ( type(outcome) , Exception ) == False 

      outcome:Union[ None , Exception]        = communicator.start()
      assert issubclass ( type(outcome) , Exception ) == False 

      

      outcome:Union[object , Exception ]      = await communicator.request( "storage" , "view_experiments"  )
      if issubclass ( type(outcome) , Exception ) == False:
            print( str(outcome) )
      else:
            pprint(outcome)

      outcome:Union[ None , Exception]        = await communicator.stop()
      assert issubclass ( type(outcome) , Exception ) == False 

      outcome:bool                            = communicator.isConnected()
      assert outcome == False


