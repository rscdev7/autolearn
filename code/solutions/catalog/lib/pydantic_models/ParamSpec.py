"""
@author           	:  rscalia              \n
@build-date         :  Sun 09/05/2021       \n
@last-update        :  Sun 09/05/2021       \n

Definizione PyDantic model rappresentante un Parametro di un algortimo di Machine Learning

"""

from pydantic   import BaseModel, Field
from typing     import List,Optional,Dict


class ParamSpec (BaseModel):
    param_name:str                      = Field(...,title="Nome Parametro",description="Nome Parametro")

    param_type:str                      = Field(...,title="Tipo parametro",description="Tipo Parametro")

    default:Optional[str]               = Field(None,title="Valore di Default del Parametro",description="Valore di Default del Parametro")

    range_l:Optional[str]               = Field(None,title="Lower bound parametro numerico",description="Lower bound parametro numerico")

    range_u:Optional[str]               = Field(None,title="Upper bound parametro numerico",description="Upper bound parametro numerico")

    options:Optional[List[str]]         = Field(None,title="Lista letterali per il parametro",description="Lista letterali per il parametro")