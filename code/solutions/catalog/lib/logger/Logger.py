"""
@author           	:  rscalia                          \n
@build-date         :  Mon 15/07/2021                   \n
@last-update        :  Fri 23/07/2021                   \n

Questo componente serve per fare logging in merito alle attività dei microservizi
"""

import logging
from logging                    import Logger,StreamHandler,FileHandler, Formatter,getLogger
from datetime                   import datetime
from os.path                    import join
from typing                     import Union

class Logger(object):

    def __init__(self, pName:str="logger", pLogPath:str="./log") -> object:
        """
        Costruttore \n

        Args:\n
            pName           (str)       : nome del logger
            pLogPath        (str)       : path dove è presente il file di log
        """
        self._name:str              = pName
        self._logPath:str           = pLogPath


    def start (self) -> None:
        """
        Questo metodo configura il logging dell'applicativo, sia su file che su stdout
        """

        #Creazione nome del file di log
        current_datetime:datetime           = datetime.now()
        log_file_name:str                   = self._name+current_datetime.strftime("__%d_%m_%Y__%H_%M_%S")+".log"
        logFilePath:str                     = join(self._logPath, log_file_name)

        #Costruzione Oggetto Logger
        self._logger:Logger                 = getLogger(self._name)


        #Creazione Handler per Logging su File e su Console
        console_handler:StreamHandler       = StreamHandler()
        file_handler:FileHandler            = FileHandler(logFilePath)

        #Impostazione Livello Priorità Logging su File e Console
        console_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        self._logger.setLevel(logging.INFO)


        #Impostazione Formattazione Log
        syle:Formatter                      = Formatter('| %(asctime)s | %(message)s',"DATE: %d-%m-%Y | TIME: %H:%M:%S")
        console_handler.setFormatter(syle)
        file_handler.setFormatter(syle)


        #Aggiunta Handler al logger
        self._logger.addHandler(console_handler)
        self._logger.addHandler(file_handler)


    def log (self, pMsg:str) -> Union [ None , Exception ]:
        """
        Questo metodo scrive una linea di log 

        Args:\n
            pMsg            (str)       : messaggio

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception   : eccezzione generica       
        """
        try:
            info_line:str = "INFO | "+pMsg
            self._logger.info(info_line)
        except Exception as exp:
            return exp

        
    def error (self, pMsg:Union[ str , Exception ] ) -> Union [ None , Exception ]:
        """
        Questo metodo segnala il verificarsi di un Errore all'interno del Log.

        Args:\n
            pMsg            ( Union[ str , Exception ] )         : messaggio d'errore

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                                            : eccezzione generica       
        """
        try:
            error_line:str = "ERROR | "+str(pMsg)
            self._logger.error(error_line)
        except Exception as exp:
            return exp
