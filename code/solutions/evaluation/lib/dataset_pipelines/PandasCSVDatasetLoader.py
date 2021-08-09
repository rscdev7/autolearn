"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 07/08/2021                       \n
@last-update            :  Sat 07/08/2021                       \n

Questo componente rappresenta il task di caricamento da disco di un dataset in formato csv.
"""
from ..abstract_streaming_pipeline.GeneralStreamingPipe         import GeneralStreamingPipe
from pandas.core.frame                                          import DataFrame
import pandas                                                   as pd
from typing                                                     import Iterator

class PandasCSVDatasetLoader (GeneralStreamingPipe):

    def __init__ (self, pDataPath:str) -> object:
        """
        Costruttore

        Args:\n
            pDataPath               (str)       : path del file contente il dataset
        """
        self._dataPath:str                          = pDataPath


    def make(self) -> Iterator:
        """
        Restituisce un iteratore che permette di prelevare sequenzialmente i dati elaborati dalla pipe

        Returns:\n
            Iterator                                    : iteratore che permette di prelevare i dati dalla pipe

        Raises:\n   
            StopIteration                               : stop dello stream verso la pipe
            Exception                                   : eccezione derivata dal prelievo dei dati dallo stream oppure dalla filter oppure dalla map oppure dall'assenza dell'oggetto per accedere allo Stream
        """
        try:
            data:DataFrame = pd.read_csv(self._dataPath)

            yield data
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