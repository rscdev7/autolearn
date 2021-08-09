"""
@author           	    :  rscalia                              \n
@build-date             :  Mon 09/08/2021                       \n
@last-update            :  Mon 09/08/2021                       \n
"""

from fastapi                                import FastAPI
from lib.rest_api.rest_end_point            import router 

app:FastAPI         = FastAPI()
app.include_router(router)