"""
@author           	:  rscalia
@date               :  Sun 02/05/2021
@last_update  		:  Sun 02/05/2021

Questo componente serve per testare il Modulo TimeStampConverter

"""

import sys
sys.path.append('../lib')
from TimeStampConverter import *


def date_2_timestamp(pDay, pMonth, pYear) -> float:
    """
    Test metodo date2Timestamp
    """
    tp      = TimeStampConverter()
    return tp.date2Timestamp(pDay, pMonth, pYear)


def timestamp_2_date(pTimeStamp:float) -> str:
    """
    Test metodo timestamp2Date
    """
    tp      = TimeStampConverter()
    return tp.timestamp2Date(pTimeStamp)


def test_launcher():
    """
    Test Launcher
    """
    assert date_2_timestamp(14,5,2020) == 1589414400.0
    assert timestamp_2_date(1589414400.0) == "14-05-2020 00:00"