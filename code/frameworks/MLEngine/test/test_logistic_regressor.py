"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 07/08/2021                       \n
@last-update            :  Sat 07/08/2021                       \n

Questo componente serve per testare il Modello LogisticRegressor
"""
from ..lib.concrete_ml_engine.HeightWeightDataset               import HeightWeightDataset
from ..lib.concrete_ml_engine.IrisFisherDataset                 import IrisFisher

from ..lib.dataset_pipelines.datasets_load_pipelines            import build_height_weight_dataset_load_pipeline
from ..lib.dataset_pipelines.datasets_load_pipelines            import build_iris_dataset_load_pipeline

from ..lib.concrete_ml_engine.LogisticRegressorPandasDataset    import LogisticRegressorPandasDataset

from ..lib.abstract_streaming_pipeline.StreamingPipe            import StreamingPipe

from typing                                                     import List 


DATA_PATH:str                               = "height_weight.csv"
SPLIT:float                                 = 0.10
SEED:int                                    = 1234

RANDOM_STATE:int                            = 5

IRIS_RECORD:List[float]                     = [ [0.5, 0.7, 0.5,0.8] ]
HW_RECORD:List[float]                       = [ [33.0,187.0,180.0] ]

def test_svm_iris():
    load_pipeline:StreamingPipe             = build_iris_dataset_load_pipeline(SPLIT , SEED)
    iris_dataset:IrisFisher                 = IrisFisher()
    iris_dataset.setUp(load_pipeline)

    # [1] Test caricamento dataset
    outcome:Union[ None , Exception]        = iris_dataset.load()
    assert issubclass( type(outcome) , Exception ) == False

    # [2] SetUp Model
    logit:LogisticRegressorPandasDataset    = LogisticRegressorPandasDataset()
    params:List[dict]                       = { "random_state" : RANDOM_STATE}
    outccome:Union[ None , Exception]       = logit.setUp(params)
    assert issubclass( type(outcome) , Exception ) == False

    # [3] Fitting Modello
    outcome:Union[ None , Exception]        = logit.fit(iris_dataset)
    assert issubclass( type(outcome) , Exception ) == False

    # [4] Inference Modello
    outcome:Union[ None , Exception]        = logit.inference( IRIS_RECORD )
    assert issubclass( type(outcome) , Exception ) == False
    print ("\n[!] Inferenza LogisticRegressor su Iris: {}".format(outcome))

    # [5] Eval Modello
    outcome:Union[ None , Exception]        = logit.evaluate(iris_dataset)
    assert issubclass( type(outcome) , Exception ) == False
    print ("\n[!] Evaluation LogisticRegressor su Iris: {}".format(outcome))


def test_svm_height_weight():
    load_pipeline:StreamingPipe             = build_height_weight_dataset_load_pipeline(DATA_PATH, SPLIT , SEED)
    hw_dataset:HeightWeightDataset          = HeightWeightDataset()
    hw_dataset.setUp(load_pipeline)

    # [1] Test caricamento dataset
    outcome:Union[ None , Exception]        = hw_dataset.load()
    assert issubclass( type(outcome) , Exception ) == False

    # [2] SetUp Model
    logit:LogisticRegressorPandasDataset    = LogisticRegressorPandasDataset()
    params:List[dict]                       = { "random_state" : RANDOM_STATE}
    outccome:Union[ None , Exception]       = logit.setUp(params)
    assert issubclass( type(outcome) , Exception ) == False

    # [3] Fitting Modello
    outcome:Union[ None , Exception]        = logit.fit(hw_dataset)
    assert issubclass( type(outcome) , Exception ) == False

    # [4] Inference Modello
    outcome:Union[ None , Exception]        = logit.inference( HW_RECORD )
    assert issubclass( type(outcome) , Exception ) == False
    print ("\n[!] Inferenza LogisticRegressor su HeightWeight: {}".format(outcome))

    # [5] Eval Modello
    outcome:Union[ None , Exception]        = logit.evaluate(hw_dataset)
    assert issubclass( type(outcome) , Exception ) == False
    print ("\n[!] Evaluation LogisticRegressor su HeightWeight: {}".format(outcome))