"""
@author           	:  rscalia
@build-date         :  Mon 15/07/2021
@last_update        :  Mon 15/07/2021

Questo componente serve per testare la classe logger
"""

from ..lib.logger.Logger import Logger

LOG_PATH:str        = "../log"


def test_logger():
    lg:Logger = Logger(pLogPath=LOG_PATH)
    lg.start()

    lg.log("Test")
    lg.log("Test 2")