"""
@author           	:  rscalia                      \n
@build-date         :  Fri 16/07/2021               \n
@last-update        :  Sun 25/07/2021               \n

Questo componente serve per gestire opportunamente il verificarsi delle eccezioni
"""


class ExceptionManager (object):

    @staticmethod
    def lookForExceptions (pResult:object) -> bool:
        """
        Questo metodo permette di controllare se si sono verificate eccezioni a runtime.

        Args:
            pResult                 (object)    : risultato su cui bisogna verificare se è accaduta una eccezione

        Returns:
                                    (bool)      : VERO se si sono verificate eccezioni, FALSO altrimenti.
        """
        return True if issubclass(type(pResult), Exception) else False