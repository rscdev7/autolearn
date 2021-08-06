"""
@author           	    :  rscalia                              \n
@build-date             :  Wed 03/08/2021                       \n
@last-update            :  Fri 06/08/2021                       \n

Questo componente serve per testare la classe StreamingPipeline.
"""

from ..lib.abstract_streaming_pipeline.GeneralStreamingPipe         import GeneralStreamingPipe
from typing                                                         import  Iterator


class Step_3 (GeneralStreamingPipe):


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
        return True if pData % 2 == 0 else False


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
        if pData < 40:
            return pData+1
        else:
            raise ValueError("Errore nella Map")