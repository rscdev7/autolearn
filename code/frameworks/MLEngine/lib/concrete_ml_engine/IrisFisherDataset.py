"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 07/08/2021                       \n
@last-update            :  Sat 07/05/2021                       \n

Questo componente implementa un modulo che carica in memoria il dataset Iris e contestualmente lo suddivide in training, validation e test-set.
"""
from ..abstract_ml_engine.Dataset                       import Dataset
from ..abstract_streaming_pipeline.StreamingPipe        import StreamingPipe
from pandas.core.frame                                  import DataFrame
from typing                                             import Union

class IrisFisher (Dataset):

    def setUp(self, pLoadPipeline:StreamingPipe) -> None:
        """
        Questo metodo permette di acquisire la pipeline di caricamento del dataset

        Args:\n
            pLoadPipeline           (StreamingPipe)     : pipeline di caricamento del dataset in memoria
        """
        self._loadPipeline:StreamingPipe      = pLoadPipeline
        self._label:str                       = "Species"       


    def load(self) -> Union [ None , Exception ]:
        """
        Questo metodo permette di caricare un dataset in memoria.

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                           : errore nell'esecuzione della pipeline di caricamento del dataset 
        """
        try:
            train , val , test              = next ( self._loadPipeline )

            self._trainingSet:DataFrame     = train
            self._validationSet:DataFrame   = val
            self._testSet:DataFrame         = test
        except Exception as exp:
            return exp
        