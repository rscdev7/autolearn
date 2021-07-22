"""
@author           	:  rscalia
@build-date         :  Sun 02/05/2021
@last_update        :  Thu 22/07/2021

Questo componente serve per testare la classe TimeStampConverter

"""
from ..lib.time_stamp_manager.TimeStampManager import TimeStampManager


def date_2_timestamp(pDay, pMonth, pYear) -> float:
    """
    Test metodo date2Timestamp
    """
    tp      = TimeStampManager()
    return tp.date2Timestamp(pDay, pMonth, pYear)


def timestamp_2_date(pTimeStamp:float) -> str:
    """
    Test metodo timestamp2Date
    """
    tp      = TimeStampManager()
    return tp.timestamp2Date(pTimeStamp)


def currentTimeStampInMS() -> int:
    """
    Test metodo currentTimeStampInMS
    """
    tp      = TimeStampManager()
    return tp.currentTimeStampInMS()


def test_launcher():
    """
    Test Launcher
    """
    assert date_2_timestamp(14,5,2020)      == 1589407200
    assert timestamp_2_date(1589407200)     == "14-05-2020 00:00"
    
    current_tm:int                          = currentTimeStampInMS()
    print("\n[!] Current Timestamo in ms: {}".format(current_tm))