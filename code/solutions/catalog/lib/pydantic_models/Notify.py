"""
@author           	:  rscalia              \n
@build-date         :  Wed 27/05/2021       \n
@last-update        :  Wed 27/05/2021       \n

Definizione PyDantic model che codifica un risultato negativo di una chiamata ad un'API REST.

"""

from pydantic   import BaseModel, Field
from typing     import List,Optional,Dict


class Notify (BaseModel):
    payload:str                      = Field(...,title="Comunicazione",description="Notifica Problema Esecuzione Chiamata ad API-REST")