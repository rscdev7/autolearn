"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 07/08/2021                       \n
@last-update            :  Sat 07/08/2021                       \n

Questo componente rappresenta il task di split di un dataset Pandas
"""
from ..abstract_streaming_pipeline.GeneralStreamingPipe         import GeneralStreamingPipe
from pandas.core.frame                                          import DataFrame
import pandas                                                   as pd
from sklearn.model_selection                                    import train_test_split
import numpy                                                    as np
from typing                                                     import Iterator


class PandasDatasetSplit (GeneralStreamingPipe):

    def __init__ (self, pTestSplit:float , pSeed:int , pValSplit:float = 0.05) -> object:
        """
        Costruttore

        Args:\n
            pTestSplit                (float)                       : percentuale dei dati per il test-set
            pSeed                     (int)                         : seed per gli algoritmi randomici
            pValSplit                 (float | DEF = 0.05)          : percentuale dei dati per il validation-set
        """
        self._valSplit:float                            = pValSplit
        self._testSplit:float                           = pTestSplit
        self._seed:int                                  = pSeed
        np.random.seed(self._seed)


    def make(self) -> Iterator:
        """
        Restituisce un iteratore che permette di prelevare sequenzialmente i dati elaborati dalla pipe

        Returns:\n
            Iterator                                    : iteratore che permette di prelevare i dati dalla pipe

        Raises:\n   
            StopIteration                               : stop dello stream verso la pipe
            Exception                                   : eccezione derivata dal prelievo dei dati dallo stream oppure dalla filter oppure dalla map oppure dall'assenza dell'oggetto per accedere allo Stream
        """
        while self.hasNext():

            try:
                if self._inputStream == None:
                    raise ValueError("[!] Data Stream is unavailable !")

                dataset:DataFrame               = self.getFromStream()
                train_val, test_set             = train_test_split(dataset,     test_size=self._testSplit)
                training_set , validation_set   = train_test_split(train_val,   test_size=self._valSplit)

                yield ( training_set , validation_set , test_set )

            except StopIteration:
                return


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
        