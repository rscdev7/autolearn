"""
@author           	:  rscalia
@build-date         :  Fri 16/07/2021
@last-update        :  Fri 16/07/2021

Questo componente serve per gestire opportunamente il verificarsi delle eccezioni
"""


class ExceptionManager (object):

    @staticmethod
    def checkFunCall (pResult:object) -> bool:
        """
        Questo metodo permette di controllare se si sono verificate eccezioni a runtime.

        Args:
            pResult                 (object)    : risultato su cui bisogna verificare se è accaduta una eccezione

        Returns:
                                    (bool)      : VERO se non si sono verificate eccezion, FALSO altrimenti.
        """
        if ( issubclass(type(pResult), Exception) == True):
            ExceptionManager._taskSpecificManagement(pResult)

            return False
        else:
            return True


    @staticmethod
    def _taskSpecificManagement (pResult:object) -> None:
        """
        Questo metodo astratto permette di gestire in maniera specifica alcuni particolari tipi di eccezione che sono legate a classi specifiche di dominio.

        Args:
            pResult                 (object)    : risultato su cui bisogna verificare se è accaduta una eccezzione

        Raises;
            Exception : eccezzione generica, molto probabilmente riconducibile alla non esistenza del logger.
        """
        pass