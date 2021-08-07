"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 07/08/2021                       \n
@last-update            :  Sat 07/08/2021                       \n

Questo componente serve per testare la classe HeightWeightDataset
"""

from ..lib.concrete_ml_engine.HeightWeightDataset           import HeightWeightDataset
from ..lib.concrete_ml_engine.IrisFisherDataset             import IrisFisher

from ..lib.dataset_pipelines.datasets_load_pipelines        import build_height_weight_dataset_load_pipeline
from ..lib.dataset_pipelines.datasets_load_pipelines        import build_iris_dataset_load_pipeline

from ..lib.abstract_streaming_pipeline.StreamingPipe        import StreamingPipe
from typing                                                 import Union


DATA_PATH:str           = "height_weight.csv"
TEST_SPLIT:float        = 0.10
SEED:int                = 1234
HEIGHT_WEIGHT_LEN:int   = 4231
IRIS_FISHER_LEN:int     = 150


def test_load_dataset():

    # [1] Costruzione Pipeline di Caricamento e Inizializzazione Oggetto Dataset
    load_pipeline:StreamingPipe                     = build_height_weight_dataset_load_pipeline(DATA_PATH,TEST_SPLIT, SEED)
    height_weight_dataset:HeightWeightDataset       = HeightWeightDataset()


    # [2] Caricamento Dataset in Memoria
    height_weight_dataset.setUp(load_pipeline)
    outcome:Union[ None , Exception]                = height_weight_dataset.load()
    assert issubclass( type(outcome) , Exception )  == False


    # [3] Test sulla buona riuscita del caricamento
    train_size:int                                  = height_weight_dataset._trainingSet.shape[0]
    val_size:int                                    = height_weight_dataset._validationSet.shape[0]
    test_size:int                                   = height_weight_dataset._testSet.shape[0]

    assert ( train_size + val_size + test_size )    == HEIGHT_WEIGHT_LEN
    assert test_size == 424
    assert val_size  == 191


def test_load_iris():

    # [1] Costruzione Pipeline di Caricamento e Inizializzazione Oggetto Dataset
    load_pipeline:StreamingPipe                     = build_iris_dataset_load_pipeline(TEST_SPLIT, SEED)
    iris_datase:IrisFisher                          = IrisFisher()


    # [2] Caricamento Dataset in Memoria
    iris_datase.setUp(load_pipeline)
    outcome:Union[ None , Exception]                = iris_datase.load()
    assert issubclass( type(outcome) , Exception )  == False

    
    # [3] Test sulla buona riuscita del caricamento
    train_size:int                                  = iris_datase._trainingSet.shape[0]
    val_size:int                                    = iris_datase._validationSet.shape[0]
    test_size:int                                   = iris_datase._testSet.shape[0]

    assert ( train_size + val_size + test_size )    == IRIS_FISHER_LEN
    assert test_size == 15
    assert val_size  == 7