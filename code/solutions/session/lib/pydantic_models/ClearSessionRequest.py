"""
@author           	:  rscalia              \n
@build-date         :  Sat 31/05/2021       \n
@last-update        :  Sat 31/05/2021       \n

Questa classe codifica una richiesta che permette di leggere uno specifico record di Sessione dal DB
"""

from pydantic   import BaseModel, Field
from typing     import List,Optional,Dict


class ClearSessionRequest (BaseModel):
    id_rec:int                      = Field(...,title="Id Sessione in Chiaro",description="Id Sessione in Chiaro, utilizzato solo per scambi interni fra microservizi")