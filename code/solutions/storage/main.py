"""
@author           	    :  rscalia                              \n
@build-date             :  Wed 27/07/2021                       \n
@last-update            :  Wed 28/07/2021                       \n

Modulo Main del microservizio Storage
"""

from fastapi                                import FastAPI
from lib.rest_api.rest_end_point            import router 

app:FastAPI         = FastAPI()
app.include_router(router)