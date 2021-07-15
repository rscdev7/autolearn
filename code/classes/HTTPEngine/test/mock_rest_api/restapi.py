"""
@author           	:  rscalia
@build-date         :  Thu 15/07/2021
@last_update        :  Thu 15/07/2021

Questo modulo rappresente un mock per testare le chiamate HTTP della classe HTTPEngine
"""

from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

class Bin(BaseModel):
    data:str

#REST-API object build
app = FastAPI()


@app.get('/get_param/')
async def get_with_param(param:int):
	return param

@app.get('/get_clean/')
async def get_without_param():
	return {'res': 80}


@app.post("/post/")
async def post(it: Item):
    return it

@app.post("/post_bin/")
async def post_bin(it: Bin):
    return it
