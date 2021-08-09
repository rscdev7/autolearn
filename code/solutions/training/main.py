"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 08/08/2021                       \n
@last-update            :  Sun 08/08/2021                       \n
"""

from fastapi                                import FastAPI
from lib.rest_api.rest_end_point            import router 

app:FastAPI         = FastAPI()
app.include_router(router)