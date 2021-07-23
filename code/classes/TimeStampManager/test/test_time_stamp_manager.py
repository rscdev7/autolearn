"""
@author           	:  rscalia
@build-date         :  Sun 02/05/2021
@last_update        :  Fri 23/07/2021

Questo componente serve per testare la classe TimeStampConverter

"""
from ..lib.time_stamp_manager.TimeStampManager  import TimeStampManager
from typing                                     import Union


def date_2_timestamp(pDay, pMonth, pYear) -> Union[ int , Exception]:
    """
    Test metodo date2Timestamp
    """
    return TimeStampManager.date2Timestamp(pDay, pMonth, pYear)


def timestamp_2_date(pTimeStamp:int) -> str:
    """
    Test metodo timestamp2Date
    """
    return TimeStampManager.timestamp2Date(pTimeStamp)


def currentTimeStampInMS() -> int:
    """
    Test metodo currentTimeStampInMS
    """
    return TimeStampManager.currentTimeStampInMS()

def currentTimeStampInSec() -> int:
    """
    Test metodo currentTimeStampInMS
    """
    return TimeStampManager.currentTimeStampInSec()


def test_launcher():
    """
    Test Launcher
    """
    res:Union[int, Exception]                   = date_2_timestamp(14,5,2020)
    assert issubclass(type(res) , Exception)    == False    and         res == 1589407200
    assert timestamp_2_date(1589407200)         == "14-05-2020 00:00"
    
    current_tm:int                              = currentTimeStampInMS()
    print("\n[!] Current Timestamo in ms: {}".format(current_tm))

    current_tm:int                              = currentTimeStampInSec()
    print("\n[!] Current Timestamo in Sec: {}".format(current_tm))