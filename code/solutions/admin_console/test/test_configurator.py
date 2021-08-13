"""
@author           	    :  rscalia                              \n
@build-date             :  Fri 13/08/2021                       \n
@last-update            :  Fri 13/08/2021                       \n

Questo componente serve per testare AdminConfigurator
"""

from ..lib.admin_config.AdminConfig import AdminConfigurator



def test_admin_config():

    cfg:AdminConfigurator               = AdminConfigurator()
    outcome:Union[ None , Exception ]   = cfg.inspect()

    assert issubclass( type(outcome) , Exception ) == False


    print ("<<<<<<<<<<<<<<<< CFG >>>>>>>>>>>>>>>\n")

    print ("-> Entity ID: {}".format(cfg.ENTITY_ID))
    print("-> Event Store Name: {}".format( cfg.EVENT_STORE_NAME ))
    print("-> Event Store Port: {}".format( cfg.EVENT_STORE_PORT ))
    print("-> Event Store Login Token: {}".format( cfg.EVENT_STORE_LOGIN_TOKEN ))
    print("-> Event Store Off-Set Setup: {}".format( cfg.OFF_SET_SETUP ))
    print("-> Event Store Wait Time: {}".format( cfg.WAIT_TIME ))
    print("-> Event Store Infinite Fetch: {}".format( cfg.INFINITE_FETCH ))