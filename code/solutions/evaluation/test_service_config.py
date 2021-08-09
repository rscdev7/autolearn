"""
@author           	    :  rscalia                              \n
@build-date             :  Mon 09/08/2021                       \n
@last-update            :  Mon 09/08/2021                       \n

Questo componente serve per testare ServiceConfig
"""

from .lib.service_config.ServiceConfig      import ServiceConfig

def test_cfg():

    cfg:ServiceConfig                               = ServiceConfig()
    outcome:Union[None , Exception]                 = cfg.inspect()

    assert issubclass ( type( outcome ) , Exception ) == False

    print ("<<<<<<<<<<<<<<< CFG >>>>>>>>>>>>>>")

    print ("-> Entity ID: {}".format(cfg.ENTITY_ID))
    print ("-> Event Store name: {}".format(cfg.EVENT_STORE_NAME))
    print ("-> Event Store Port: {}".format(cfg.EVENT_STORE_PORT))
    print ("-> Broker Login Token: {}".format(cfg.BROKER_LOGIN_TOKEN))
    print ("-> Event Store Partition: {}".format(cfg.REST_EP_PARTITION))
    print ("-> Event Store Topic: {}".format(cfg.REST_EP_TOPIC))
    print ("-> Broker Queue: {}".format(cfg.QUEUE))
    print ("-> Height Weight Data Path: {}".format(cfg.HEIGHT_WEIGHT_DATA_PATH))
    print ("-> Query URL: {}".format(cfg.QUERY_RECORD_URL))


