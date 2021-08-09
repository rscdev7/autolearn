"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 07/08/2021                       \n
@last-update            :  Sat 07/08/2021                       \n

Questo modulo permette di costruire le pipeline di caricamento dei dataset.
"""

from ..abstract_streaming_pipeline.StreamingPipe        import StreamingPipe
from ..dataset_pipelines.PandasCSVDatasetLoader         import PandasCSVDatasetLoader
from ..dataset_pipelines.PandasDatasetSplit             import PandasDatasetSplit
from ..dataset_pipelines.StatsModelsDatasetLoader       import StatsModelsDatasetLoader

def build_height_weight_dataset_load_pipeline(pDataPath:str , pTestSplit:float , pSeed:int) -> StreamingPipe:
    """
    # **build_height_weight_dataset_load_pipeline**

    Questa funzione permette di costruire la pipeline di caricamento del dataset Height Weight.

    Args:\n
        pDataPath                   (str)       : path al file contente il dataset Height Weight
        pTestSplit                  (float)     : percentuale dei dati per il test-set
        pSeed                       (int)       : seed per gli algoritmi randomici            
    """
    loader:HeightWeightLoad     = PandasCSVDatasetLoader(pDataPath)
    splitter:HeightWeightSplit  = PandasDatasetSplit(pTestSplit , pSeed)
    load_pipeline:StreamingPipe = loader | splitter

    return load_pipeline


def build_iris_dataset_load_pipeline(pTestSplit:float , pSeed:int) -> StreamingPipe:
    """
    # **build_iris_dataset_load_pipeline**
    
    Questa funzione permette di costruire la pipeline di caricamento del dataset Iris.

    Args:\n
        pTestSplit                  (float)     : percentuale dei dati per il test-set
        pSeed                       (int)       : seed per gli algoritmi randomici            
    """
    loader:HeightWeightLoad     = StatsModelsDatasetLoader("iris")
    splitter:HeightWeightSplit  = PandasDatasetSplit(pTestSplit , pSeed)
    load_pipeline:StreamingPipe = loader | splitter

    return load_pipeline


        