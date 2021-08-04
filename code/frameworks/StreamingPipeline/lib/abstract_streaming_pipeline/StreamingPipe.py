"""
@author           	:  rscalia                                  \n
@build-date         :  Wed 04/08/2021                           \n
@last-update        :  Wed 04/08/2021                           \n

Questa classe implementa l'astrazione della StreamingPipe presente nel DP StreamingPipeline
"""

from abc            import ABC, ABCMeta, abstractmethod
from typing         import Union , Iterator, Generator


class StreamingPipe( ABC , metaclass=ABCMeta ):

    def __init__(self, pInputStream:Iterator = None  ) -> object:
        """
        Costruttore

        Args:\n
            pInputStream        (Iterator | DEF = None)        : eventuale stream di input alla Pipe
        """
        self._inputStream:Iterator                   = pInputStream


    def __iter__(self) -> Generator:
        """
        Metodo che restituisce l'oggetto necessario al prelievo dei dati dallo stream 

        Returns:\n
            Generator                                        : Generatore
        """
        return self.make()


    def __next__(self) -> object:
        """
        Questo metodo permette di elaborare il prossimo elemento presente nello stream di input

        Returns:\n
            object                                             : dato proveniente dallo stream elaborato dalla Pipe
        """
        return next ( self.make() )


    def has_next(self) -> bool:
        """
        Metodo che indica se è possibile prelevare ancora elementi dallo Stream

        Returns:\n
            bool                                             : VERO se è presente ancora un elemento da elaborare, FALSO altrimenti
        """
        return True

    
    def make(self) -> Generator:
        """
        Restituisce un generatore che permette di prelevare sequenzialmente i dati elaborati dalla pipe

        Returns:\n
            Generator                                   : generatore che permette di prelevare i dati dalla pipe

        Raises:\n   
            StopIteration                               : stop dello stream verso la pipe
            Exception                                   : eccezione derivata dal prelievo dei dati dallo stream oppure dalla filter oppure dalla map oppure dall'assenza dell'oggetto per accedere allo Stream
        """
        while self.has_next():

            try:
                if self._inputStream == None:
                    raise ValueError("[!] Data Stream is unavailable !")

                data:object                     = self.getFromStream()
                if self.filter(data):
                    computed_data:object        = self.map(data)
                    yield computed_data

            except StopIteration:
                return

    
    def getFromStream(self) -> object:
        """
        Questo metodo preleva un elemento dallo stream di dati in input alla Pipe

        Returns:\n
            object          : elemento prelevato dallo stream

        Raises:\n
            Exception       : errore nella get del dato dallo stream
        """
        return next(self._inputStream)


    def __or__(self, pNextPipe:object) -> object:
        """
        Permette di connettere più Task tra di loro attraverso l'operatore OR (" | ")

        Args:\n
            pNextPipe           (StreamingPipe)     : Prossimo task della Pipeline

        Returns:\n
            StreamingPipe                           : prossima Task da eseguire nella Pipeline con dato di input caricato

        Raises:\n   
            StopIteration                           : stop dello stream verso la pipe
            Exception                               : eccezione derivata dal prelievo dei dati dallo stream oppure dalla filter oppure dalla map oppure dall'assenza dell'oggetto per accedere allo Stream
        """
        pNextPipe._inputStream                           = self.make()
        return pNextPipe
        
        
    @abstractmethod
    def filter(self, pData:object) -> bool:
        """
        Filtra il dato attuale secondo un criterio opportuno
        
        Args:\n
            pData               (object)        : dato da filtrare

        Returns:\n
            bool                                : booleano in merito alla logica del filtro oppure eccezione

        Raises:\n
            Exception                           : eventuale eccezione accaduta durante il filtraggio
        """
        pass


    @abstractmethod
    def map(self, pData:object) -> object:
        """
        Elabora il dato in input alla pipe

        Args:\n
            pData               (object)        : dato da elaborare

        Returns:\n
            object                              : dato elaborato o eccezzione

        Raises:\n
            Exception                           : eventuale eccezione accaduta durante l'elaborazione
        """
        pass