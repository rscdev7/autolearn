"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 25/07/2021                       \n
@last-update            :  Sun 25/07/2021                       \n

Questo componente implementa il design pattern Singleton
"""

from typing         import List,Dict


class Singleton(type):

    def __init__(self, *args:List[object], **kwargs:Dict[str,str]) -> object:
        """
        Costruttore

        Args:\n
            args        (List[object])                  : argomenti passati come parametro
            kwargs      (Dict[str,str])                 : argomenti passati come key-value
        """
        self._singleIstance:object = None
        super().__init__(*args, **kwargs)
 

    def __call__(cls:object, *args:List[object], **kwargs:Dict[str,str]) -> object:
        """
        Metodo di call

        Args:\n
            cls         (object)                        : costrutto Python che permette di modificare la classe anzichè l'istanza, tale campo conterrà la classe che vogliamo far diventare Singleton.
            args        (List[object])                  : argomenti passati come parametro
            kwargs      (Dict[str,str])                 : argomenti passati come key-value
        """
        #Se la classe è già istanziata, viene restituita l'istanza già creata
        if cls._singleIstance:
            return cls._singleIstance

        #Costruisco una Istanza della Classe passata e lancio il Suo costruttore
        single_obj:object       = cls.__new__(cls)
        single_obj.__init__(*args, **kwargs)

        #Archiviazione Istanza classe creata
        cls._singleIstance      = single_obj

        #Restituzione Istanza creata al chiamante
        return single_obj
        