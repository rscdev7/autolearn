"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 07/08/2021                       \n
@last-update            :  Sun 07/08/2021                       \n

Questo componente rappresenta un wrapper ad un dataset che permette di caricarlo in memoria ed eventualmente applicargli un pre-processing. (es. split in train-val-test ecc...)
"""
from typing                                         import List, Union
from abc                                            import ABC, ABCMeta, abstractmethod
from ..abstract_streaming_pipeline.StreamingPipe    import StreamingPipe

class Dataset (ABC, metaclass=ABCMeta):

    __slots__ = ("_loadPipeline" , "_trainingSet" , "_validationSet" , "_testSet")
    @abstractmethod
    def setUp(self, pLoadPipeline:StreamingPipe) -> None:
        """
        Questo metodo permette di acquisire la pipeline di caricamento del dataset

        Args:\n
            pLoadPipeline           (StreamingPipe)     : pipeline di caricamento del dataset in memoria
        """
        pass

    @abstractmethod
    def load(self) -> Union [ None , Exception ]:
        """
        Questo metodo permette di caricare un dataset in memoria.

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                           : errore nell'esecuzione della pipeline di caricamento del dataset 
        """
        pass
        