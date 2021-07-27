"""
@author           	    :  rscalia                              \n
@build-date             :  Wed 27/07/2021                       \n
@last-update            :  Thu 27/07/2021                       \n

Questo componente serve per testare il Microservizio Catalog
"""

import sys
sys.path.append (".")

import pytest
from httpx              import AsyncClient, Response
import shutil
from main               import app


URL:str                    = "http://localhost:9200/catalog/api"

@pytest.mark.asyncio
async def test_api_positive():
    print ("\n<<<<<<<<<<< Test API Positivo >>>>>>>>>>>>")

    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response = await ac.get("/get_catalog?pIdClient=test_client")
        status_code:int   = response.status_code
        payload:dict      = response.json()

    assert status_code == 202
    assert set( [ "data_lake" , "models" , "metrics" , "learning" ] ).issubset( set( payload.keys() ) )


@pytest.mark.asyncio
async def test_api_negative():
    print ("\n<<<<<<<<<<< Test API Negativo >>>>>>>>>>>>")

    #Altero la posizione del file del catalogo in modo da simulare l'assenza di quest'ultimo
    shutil.move("./data/autolearn_catalog.json" , ".")

    async with AsyncClient(app=app, base_url=URL) as ac:
        response:Response = await ac.get("/get_catalog?pIdClient=test_client")
        status_code:int   = response.status_code
        payload:dict      = response.json()

    assert status_code == 503
    assert payload     == { "message" : "Unable to Retrieve Catalog" }

    #Rimetto a posto il file del catalogo
    shutil.move("./autolearn_catalog.json" , "./data/autolearn_catalog.json")

    