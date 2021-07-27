"""
@author           	:  rscalia
@build-date         :  Sun 09/05/2021
@last-update        :  Sun 09/05/2021

Definizione Data Transfer Object del Catalogo

"""

from pydantic       import BaseModel, Field
from typing         import List,Optional,Dict
from .ParamSpec     import ParamSpec


class SeqComputationSpec (BaseModel):
    step:int                                        = Field(...,title="Posizione",description="Ordine della computazione all'itnerno di uno schema di Pre-Processing di un dataset")

    computation:str                                 = Field(...,title="Computazione",description="Tipo di Computazione")


class ModelReference (BaseModel):
    model_name:str                                  = Field(...,title="Nome Modello",description="Nome Modello")
    model_task:str                                  = Field(...,title="Task Modello",description="Task Modello")



class Dataset (BaseModel):
    dataset_name:str                                = Field(...,title="Nome Dataset",description="Nome del Dataset")

    dataset_task:str                                = Field(...,title="Task Dataset",description="Task associato al Dataset")

    dataset_description:str                         = Field(...,title="Descrizione Dataset",description="TDescrizione del Dataset")

    features:List[str]                              = Field(...,title="Features",description="Features del Dataset")

    label:List[str]                                 = Field(...,title="Etichetta",description="Etichetta del Dataset")

    n_record:int                                    = Field(...,title="Numero Record",description="Numero di sample del dataset")

    pre_processing:List[SeqComputationSpec]         =  Field(...,title="Pre-Processing Dataset",description="Specifica le computazioni necessarie prima di dare in input il dataset ad un algoritmo di Machine Learning")


class Model (BaseModel):
    model_name:str                                  = Field(...,title="Nome del Modello",description="Nome del Modello")

    model_task:str                                  = Field(...,title="Task",description="Task associato al Modello")

    model_hyperparams:Optional[List[ParamSpec]]     = Field(None,title="Iperparametri Modello",description="Iperparametri Modello")


class Metric (BaseModel):
    metric_task:str                                 = Field(...,title="Task",description="Task associato alla Metrica")
    metric_name:str                                 = Field(...,title="Nome della Metrica",description="Nome della Metric")


class LearningAsset (BaseModel):
    model_reference:ModelReference                  = Field(...,title="Riferimento al Modello",description="Riferimento al Modello a cui e' associato il learning asset")

    loss:Optional[str]                              = Field(None,title="Funzione di Costo del Learning Asset",description="Funzione di Costo del Learning Asset")

    learning_algorithm:Optional[str]                = Field(None,title="Funzione di Costo del Learning Asset",description="Funzione di Costo del Learning Asset")

    learning_hyperparams:List[ParamSpec]            = Field(...,title="Iperparametri dell'algoritmo di Machine Learning",description="Iperparametri dell'algoritmo di Machine Learning")



class Catalog (BaseModel):
    data_lake:List[Dataset]                         = Field(...,title="Data Lake",description="Contiene tutti i dataset disponibili a catalogo")

    models:List[Model]                              = Field(...,title="Models",description="Contiene tutti i modelli disponibili a catalogo")

    metrics:List[Metric]                            = Field(...,title="Metrics",description="Contiene la lista delle Metriche per valutare i modelli di Machine Learning")

    learning:List[LearningAsset]                    = Field(...,title="Learning",description="Contiene le impostazioni del training disponibili per i Modelli a Catalogo")