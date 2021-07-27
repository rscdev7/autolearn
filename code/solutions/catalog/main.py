"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 25/07/2021                       \n
@last-update            :  Sun 25/07/2021                       \n

Questo componente inizializza l'applicazione FastAPI
"""

from fastapi import FastAPI
from lib.rest_api.catalog_rest_end_point import router 

app:FastAPI = FastAPI()
app.include_router(router)