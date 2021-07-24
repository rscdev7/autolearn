"""
@author           	:  rscalia
@build-date         :  Mon 15/07/2021
@last_update        :  Fri 23/07/2021

Questo componente serve per testare la classe logger
"""

from ..lib.logger.Logger    import Logger
from typing                 import Union

LOG_PATH:str                      = "../log"


def test_logger():
    lg:Logger = Logger(pLogPath=LOG_PATH)
    lg.start()

    res:Union[None , Exception ] = lg.log("Test")
    assert issubclass( type(res) , Exception) == False

    res:Union[None , Exception ] = lg.log("Test 2")
    assert issubclass( type(res) , Exception) == False

    try:
        a:float = 5.0/0.0
    except ZeroDivisionError as zd:
        res:Union[None , Exception ] = lg.error(zd)
        assert issubclass( type(res) , Exception) == False