"""
@author           	    :  rscalia                              \n
@build-date             :  Thu 12/08/2021                       \n
@last-update            :  Thu 12/08/2021                       \n

Questo componente serve per testare la classe ClientConfigurator

"""

from .lib.client_config.ClientConfigurator       import ClientConfigurator
from typing                                     import Union

def test_cfg():

    cfg:ClientConfigurator                  = ClientConfigurator()
    outcome:Union[ None , Exception]        = cfg.inspect()

    assert issubclass( type(outcome) , Exception  ) == False

    print ("\n\n<<<<<<<<<<<<<< AUTOLEARN_CFG >>>>>>>>>>>>>>>>>>>>")

    print ("\n_____Misc Config______")
    print("-> Http Connection Timeout in Seconds: {}".format(cfg.HTTP_REQ_TIME_OUT_IN_SEC))
    print("-> Catalog Caching Time in Days: {}".format(cfg.CATALOG_RETENTATION_TIME_IN_DAYS))

    print ("\n_____Catalog Service______")
    service:str         = "Catalog"
    print("-> {} Service Name: {}".format(service , cfg.CATALOG_SERVICE_NAME))
    print("-> {} Service Base Address: {}".format(service , cfg.CATALOG_BASE_ADDRESS))
    print("-> {} Service Actions: {}".format(service , cfg.CATALOG_ACTIONS))

    print ("\n_____Training Service______")
    service:str         = "Training"
    print("-> {} Service Name: {}".format(service , cfg.TRAINING_SERVICE_NAME))
    print("-> {} Service Base Address: {}".format(service , cfg.TRAINING_BASE_ADDRESS))
    print("-> {} Service Actions: {}".format(service , cfg.TRAINING_ACTIONS))

    print ("\n_____Evaluation Service______")
    service:str         = "Evaluation"
    print("-> {} Service Name: {}".format(service , cfg.EVALUATION_SERVICE_NAME))
    print("-> {} Service Base Address: {}".format(service , cfg.EVALUATION_BASE_ADDRESS))
    print("-> {} Service Actions: {}".format(service , cfg.EVALUATION_ACTIONS))

    print ("\n_____Session Service______")
    service:str         = "Session"
    print("-> {} Service Name: {}".format(service , cfg.SESSION_SERVICE_NAME))
    print("-> {} Service Base Address: {}".format(service , cfg.SESSION_BASE_ADDRESS))
    print("-> {} Service Actions: {}".format(service , cfg.SESSION_ACTIONS))


    print ("\n_____Storage Service______")
    service:str         = "Storage"
    print("-> {} Service Name: {}".format(service , cfg.STORAGE_SERVICE_NAME))
    print("-> {} Service Base Address: {}".format(service , cfg.STORAGE_BASE_ADDRESS))
    print("-> {} Service Actions: {}".format(service , cfg.STORAGE_ACTIONS))

    print ("\n\n_____Services List______\n")
    for service in cfg.SERVICES_LIST:
        print ("[{}]".format(service["recipient_name"].upper()))
        print ("\t-> Base Address: {}".format(service["base_address"]))
        print ("\t-> Actions: {}\n".format(service["actions"]))

    print ("\n<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>")