"""
@author           	:  rscalia
@build-date         :  Fri 16/07/2021
@last-update        :  Fri 23/07/2021

Questo componente serve per testare ExceptionManager
"""

from ..lib.exception_manager.ExceptionManager  import ExceptionManager


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
    res:float           = wrong_fun()
    fun_outcome:bool    = ExceptionManager.checkFunCall(res)
    assert fun_outcome == True

    print("[!] Exception Type: {}".format(res))
    
