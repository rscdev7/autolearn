"""
@author           	:  rscalia
@build-date         :  Fri 16/07/2021
@last-update        :  Fri 16/07/2021

Questo componente serve per testare ExceptionManager
"""

from ..lib.exception_manager.ExceptionManager  import ExceptionManager
from .logger.Logger                       import Logger



LOGGER_NAME:str         = "test_logger"


def wrong_fun():
    """
    funzione con eccezione
    """
    try:
        a = 8/0
        return a
    except ZeroDivisionError as zd:
        return zd


def test_e_mng():
    lg:Logger           = Logger(LOGGER_NAME,"../log")
    lg.start()
    
    res:float           = wrong_fun()
    fun_outcome:bool    = ExceptionManager.checkFunCall(res)
    assert fun_outcome == True
    lg.error(res)
    
