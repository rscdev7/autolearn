"""
@author           	:  rscalia
@version  		    :  1.0.0
@build-date         :  Sun 09/05/2021
@last_update        :  Sun 09/05/2021

Questo componente serve per costruire un logger globale per un Processo Python

"""

import logging


class LoggerSetup (object):

    def setUp (self, pName:str) -> None:
        """
        Questa funzione costruisce un logger globale referenziabile da qualunque oggetto presente nel Processo Python "attuale"

        Args:
            pName       (str)                          : nome del logger

        """

        logger                  = logging.getLogger(pName)

        #Costruzione Handler
        info_handler           = logging.StreamHandler()
        info_handler.setLevel(logging.INFO)

        info_handler_format    = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        info_handler.setFormatter(info_handler_format)

        #Aggiunta Handler al logger
        logger.addHandler(info_handler)


        #Imposto il livello del Logger
        logger.setLevel(logging.INFO)
