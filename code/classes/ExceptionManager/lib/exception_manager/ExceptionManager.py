"""
@author           	:  rscalia
@build-date         :  Fri 16/07/2021
@last-update        :  Fri 23/07/2021

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
        return True if issubclass(type(pResult), Exception) == True else False