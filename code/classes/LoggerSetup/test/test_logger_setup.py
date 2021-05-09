"""
@author           	:  rscalia
@version  		    :  1.0.0
@build-date         :  Sun 09/05/2021
@last_update        :  Sun 09/05/2021

Questo componente serve per testare la classe LoggerSetup

"""

import logging
from ..lib.LoggerSetup import *


NAME        = "test-logger"

def test_logger_setup () -> None:
    """
    Questa funzione permette di testare il componente LoggerSetup
    """

    starter = LoggerSetup()

    starter.setUp(NAME)

    lg      = logging.getLogger(NAME)

    lg.info("\nError 1")
    lg.info ("eeeeeeeeee")
    lg.info ("qq")

    lg.error("Error 2")